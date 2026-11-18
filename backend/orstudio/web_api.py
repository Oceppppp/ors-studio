from __future__ import annotations

import hashlib
import json
import logging
import math
import os
import re
import time
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import numpy as np
from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import cloud_store
from .api import AnalysisRequest, BatchRequest, ForecastCompareRequest, ProjectCreate, clean_json, _set_path, _stored_params, compare_forecasts
from .cloud_security import (COOKIE_NAME, clear_session_cookie, current_principal_optional,
                             hash_password, new_session, require_principal,
                             set_session_cookie, token_hash, verify_password)
from .registry import MODULES, MODULE_MAP, run_module
from .services.import_service import read_tabular_file, inspect_tabular_file
from .services import export_service

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("ors.web")
VERSION = "0.4.0"
IS_PRODUCTION = os.getenv("ORS_ENV", "development").lower() == "production"
COOKIE_SECURE = os.getenv("ORS_COOKIE_SECURE", "true" if IS_PRODUCTION else "false").lower() == "true"
MAX_UPLOAD_USER = 20 * 1024 * 1024
MAX_UPLOAD_GUEST = 5 * 1024 * 1024
MAX_DATASET_STORAGE_USER = 250 * 1024 * 1024
MAX_DATASET_STORAGE_GUEST = 15 * 1024 * 1024

_pool: ThreadPoolExecutor | None = None
_auth_events: dict[str, deque[float]] = defaultdict(deque)


class RegisterRequest(BaseModel):
    email: str = Field(min_length=5, max_length=320)
    password: str = Field(min_length=12, max_length=128)
    display_name: str = Field(min_length=1, max_length=120)


class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=320)
    password: str = Field(min_length=1, max_length=128)


class UpgradeRequest(RegisterRequest):
    pass


def _rate_limit(request: Request, bucket: str, maximum: int, seconds: int) -> None:
    identity = request.client.host if request.client else "unknown"
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        try:
            from redis import Redis
            client = Redis.from_url(redis_url, socket_connect_timeout=2, socket_timeout=2)
            key = f"ors:ratelimit:{bucket}:{identity}"
            count = client.incr(key)
            if count == 1:
                client.expire(key, seconds)
            if count > maximum:
                raise HTTPException(429, "Too many attempts. Please wait and try again.")
            return
        except HTTPException:
            raise
        except Exception:
            logger.exception("Shared rate limiter unavailable")
            if IS_PRODUCTION:
                raise HTTPException(503, "Security rate limiter unavailable. Please retry shortly.")
    key = f"{bucket}:{identity}"
    now = time.monotonic(); events = _auth_events[key]
    while events and events[0] < now - seconds:
        events.popleft()
    if len(events) >= maximum:
        raise HTTPException(429, "Too many attempts. Please wait and try again.")
    events.append(now)


def _check_origin(request: Request) -> None:
    """Same-origin mutation guard; cookies are HttpOnly + SameSite=Lax."""
    origin = request.headers.get("origin")
    if not origin:
        if request.headers.get("sec-fetch-site", "same-origin") == "cross-site":
            raise HTTPException(403, "Cross-site requests are not allowed")
        return
    try:
        origin_parts = urlsplit(origin)
        origin_host = origin_parts.netloc.lower()
        request_host = request.headers.get("host", "").lower()
        request_scheme = request.url.scheme.lower()
        configured = {x.strip().lower() for x in os.getenv("ORS_ALLOWED_ORIGINS", "").split(",") if x.strip()}
        same_origin = origin_parts.scheme.lower() == request_scheme and origin_host == request_host
        if origin.rstrip("/") in configured or same_origin:
            return
    except ValueError:
        pass
    raise HTTPException(403, "Cross-origin changes are not allowed")


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _pool
    if IS_PRODUCTION and not os.getenv("DATABASE_URL", "").startswith(("postgres://", "postgresql://", "postgresql+psycopg://")):
        raise RuntimeError("Production requires DATABASE_URL pointing to PostgreSQL")
    if IS_PRODUCTION and not os.getenv("REDIS_URL"):
        raise RuntimeError("Production requires REDIS_URL for the persistent background job queue")
    if IS_PRODUCTION and not os.getenv("ORS_SESSION_SECRET"):
        raise RuntimeError("Production requires ORS_SESSION_SECRET")
    cloud_store.init_db()
    _pool = None if IS_PRODUCTION else ThreadPoolExecutor(
        max_workers=max(2, min(4, os.cpu_count() or 2)), thread_name_prefix="ors-web-dev"
    )
    try:
        yield
    finally:
        if _pool:
            _pool.shutdown(wait=False, cancel_futures=True)
            _pool = None
        cloud_store.engine().dispose()


app = FastAPI(title="ORS Studio Public Web API", version=VERSION,
              description="Multi-user web edition of Operations Research Studio", lifespan=lifespan)


@app.middleware("http")
async def web_security_headers(request: Request, call_next):
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        try:
            _check_origin(request)
        except HTTPException as exc:
            return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    if COOKIE_SECURE:
        response.headers.setdefault("Strict-Transport-Security", "max-age=31536000")
    response.headers.setdefault("Cache-Control", "no-store" if request.url.path.startswith("/api/") else "no-cache")
    response.headers.setdefault("Content-Security-Policy",
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; img-src 'self' data: blob:; connect-src 'self'; "
        "object-src 'none'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'")
    return response


def _principal_payload(principal: dict | None):
    if not principal:
        return {"cloud_mode": True, "authenticated": False}
    return {"cloud_mode": True, "authenticated": True, "id": principal["id"],
            "kind": principal["kind"], "email": principal.get("email"),
            "display_name": principal["display_name"], "expires_at": principal.get("expires_at")}


def _issue_response(principal: dict, token: str, guest: bool = False):
    response = JSONResponse(_principal_payload(principal))
    response.set_cookie(COOKIE_NAME, token, max_age=(24 if guest else 24 * 14) * 3600,
                        httponly=True, secure=COOKIE_SECURE, samesite="lax", path="/")
    return response


def _require_owner_project(owner_id: str, project_id: str | None) -> str:
    try:
        return cloud_store.project_id_or_default(owner_id, project_id)
    except ValueError:
        raise HTTPException(404, "Project not found")


def _prepare_cloud_task(req: AnalysisRequest, owner_id: str):
    params = json.loads(json.dumps(req.params))
    if req.column_map and not req.dataset_id:
        raise ValueError("A dataset must be selected before applying column mappings")
    source = None; project_id = req.project_id
    if req.dataset_id:
        ds = cloud_store.get_dataset(req.dataset_id, owner_id)
        if not ds:
            raise ValueError("Dataset not found")
        if project_id and ds["project_id"] != project_id:
            raise ValueError("Dataset does not belong to the selected project")
        project_id = project_id or ds["project_id"]
        for param_path, column in req.column_map.items():
            if column not in ds["columns"]:
                raise ValueError(f"Column '{column}' not found in dataset")
            raw_values = [row.get(column) for row in ds["rows"]]
            if any(v is None or (isinstance(v, str) and not v.strip()) for v in raw_values):
                raise ValueError(f"Mapped column '{column}' contains blank values")
            try:
                values = [float(v) for v in raw_values]
            except (ValueError, TypeError) as exc:
                raise ValueError(f"Mapped column '{column}' must contain numeric values") from exc
            if not np.isfinite(values).all():
                raise ValueError(f"Mapped column '{column}' contains non-finite numbers")
            _set_path(params, param_path, values)
        source = {"dataset_id": ds["id"], "filename": ds["filename"], "sheet_name": ds["sheet_name"],
                  "column_map": dict(req.column_map), "row_count": ds["row_count"]}
    project_id = _require_owner_project(owner_id, project_id)
    return project_id, params, source


def _dispatch_job(job_id: str, analysis_id: str, owner_id: str, module_key: str, params: dict):
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        from redis import Redis
        from rq import Queue
        queue = Queue("ors-analysis", connection=Redis.from_url(redis_url), default_timeout=900)
        queue.enqueue("orstudio.cloud_jobs.process_job", job_id, analysis_id, owner_id, module_key, params,
                      job_id=job_id, result_ttl=3600, failure_ttl=86400)
        return "redis"
    if IS_PRODUCTION or _pool is None:
        raise HTTPException(503, "Background analysis queue is unavailable")
    from .cloud_jobs import process_job
    _pool.submit(process_job, job_id, analysis_id, owner_id, module_key, params)
    return "in-process-development"


@app.get("/api/health")
def health(response: Response):
    redis_url = os.getenv("REDIS_URL")
    queue_mode = "redis" if redis_url else "in-process-development"
    try:
        with cloud_store.engine().connect() as conn:
            conn.exec_driver_sql("SELECT 1")
        db_status = "ok"
    except Exception:
        logger.exception("Cloud health database check failed")
        db_status = "error"

    queue_status = "development-pool" if not redis_url else "ok"
    if redis_url:
        try:
            from redis import Redis
            Redis.from_url(redis_url, socket_connect_timeout=1.5, socket_timeout=1.5).ping()
        except Exception:
            logger.exception("Cloud health Redis check failed")
            queue_status = "error"
    if redis_url:
        try:
            worker_count = max(1, min(16, int(os.getenv("ORS_QUEUE_WORKERS", "2"))))
        except ValueError:
            worker_count = 1
    else:
        worker_count = _pool._max_workers if _pool else 0
    overall = "ok" if db_status == "ok" and queue_status != "error" else "degraded"
    response.status_code = 200 if overall == "ok" else 503
    return {"status": overall, "name": "ORS Studio", "version": VERSION,
            "mode": "public-web", "database": db_status, "queue": queue_mode,
            "queue_health": queue_status, "worker_count": worker_count,
            "module_count": len(MODULES)}


@app.get("/api/auth/me")
def auth_me(principal=Depends(current_principal_optional)):
    return _principal_payload(principal)


@app.post("/api/auth/guest")
def continue_as_guest(request: Request, principal=Depends(current_principal_optional)):
    _rate_limit(request, "guest", 8, 3600)
    if principal:
        return _principal_payload(principal)
    cloud_store.delete_expired_guests()
    guest = cloud_store.create_principal("GUEST", "Guest workspace", guest_hours=24)
    cloud_store.ensure_default_project(guest["id"])
    token = new_session(guest["id"], guest=True)
    return _issue_response(guest, token, guest=True)


@app.post("/api/auth/register")
def register(payload: RegisterRequest, request: Request):
    _rate_limit(request, "register", 6, 3600)
    email = payload.email.strip().lower()
    if not payload.display_name.strip():
        raise HTTPException(400, "Display name cannot be blank")
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        raise HTTPException(400, "Enter a valid email address")
    if len(payload.password) < 12 or not any(c.isalpha() for c in payload.password) or not any(c.isdigit() for c in payload.password):
        raise HTTPException(400, "Password must contain at least 12 characters, including letters and numbers")
    if cloud_store.get_user_by_email(email):
        raise HTTPException(409, "An account with this email already exists")
    try:
        user = cloud_store.create_principal("USER", payload.display_name.strip(), email=email,
                                            password_hash=hash_password(payload.password))
    except Exception as exc:
        logger.exception("Account registration failed")
        raise HTTPException(409, "Could not create account. The email may already be registered.") from exc
    cloud_store.ensure_default_project(user["id"])
    return _issue_response(user, new_session(user["id"]))


@app.post("/api/auth/login")
def login(payload: LoginRequest, request: Request):
    _rate_limit(request, "login", 10, 900)
    user = cloud_store.get_user_by_email(payload.email.strip().lower())
    if not user or not user.get("password_hash") or not verify_password(user["password_hash"], payload.password):
        raise HTTPException(401, "Email or password is incorrect")
    token = new_session(user["id"])
    return _issue_response(user, token)


@app.post("/api/auth/upgrade")
def upgrade_guest(payload: UpgradeRequest, request: Request, principal=Depends(require_principal)):
    """Convert a guest identity to a permanent account without losing its workspace."""
    if principal["kind"] != "GUEST":
        raise HTTPException(409, "This session already belongs to a registered account")
    _rate_limit(request, "upgrade", 5, 3600)
    email = payload.email.strip().lower()
    if not payload.display_name.strip():
        raise HTTPException(400, "Display name cannot be blank")
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        raise HTTPException(400, "Enter a valid email address")
    if cloud_store.get_user_by_email(email):
        raise HTTPException(409, "An account with this email already exists")
    from sqlalchemy import update as sql_update
    with cloud_store.engine().begin() as conn:
        conn.execute(sql_update(cloud_store.principals).where(cloud_store.principals.c.id == principal["id"]).values(
            kind="USER", email=email, password_hash=hash_password(payload.password),
            display_name=payload.display_name.strip(), expires_at=None))
    old_token = request.cookies.get(COOKIE_NAME)
    if old_token:
        cloud_store.delete_session(token_hash(old_token))
    updated = {**principal, "kind": "USER", "email": email, "display_name": payload.display_name.strip(), "expires_at": None}
    response = JSONResponse(_principal_payload(updated))
    response.set_cookie(COOKIE_NAME, new_session(principal["id"]), max_age=14 * 24 * 3600,
                        httponly=True, secure=COOKIE_SECURE, samesite="lax", path="/")
    return response


@app.post("/api/auth/logout")
def logout(request: Request):
    token = request.cookies.get(COOKIE_NAME)
    if token:
        cloud_store.delete_session(token_hash(token))
    response = JSONResponse({"logged_out": True})
    clear_session_cookie(response, COOKIE_SECURE)
    return response


@app.get("/api/modules")
def get_modules():
    return {"count": len(MODULES), "modules": MODULES}


@app.get("/api/projects")
def get_projects(principal=Depends(require_principal)):
    cloud_store.ensure_default_project(principal["id"])
    return {"projects": cloud_store.list_projects(principal["id"])}


@app.post("/api/projects")
def post_project(payload: ProjectCreate, principal=Depends(require_principal)):
    limit = 2 if principal["kind"] == "GUEST" else 50
    if cloud_store.count_owned("projects", principal["id"]) >= limit:
        raise HTTPException(403, "Workspace project limit reached. Create an account to unlock more projects." if principal["kind"] == "GUEST" else "Project quota reached")
    return cloud_store.create_project(principal["id"], payload.name.strip(), payload.description.strip())


@app.get("/api/datasets")
def get_datasets(project_id: str | None = None, principal=Depends(require_principal)):
    pid = _require_owner_project(principal["id"], project_id)
    return {"datasets": cloud_store.list_datasets(pid, principal["id"])}


@app.post("/api/datasets/inspect")
async def inspect_dataset(request: Request, file: UploadFile = File(...), principal=Depends(require_principal)):
    _rate_limit(request, "inspect-upload", 30, 3600)
    limit = MAX_UPLOAD_GUEST if principal["kind"] == "GUEST" else MAX_UPLOAD_USER
    content = await file.read(limit + 1)
    if len(content) > limit:
        raise HTTPException(413, f"Upload limit is {limit // (1024 * 1024)} MB for this session")
    try:
        return inspect_tabular_file(file.filename or "uploaded.csv", content)
    except ValueError as exc:
        raise HTTPException(400, str(exc))


@app.post("/api/datasets/import")
async def import_dataset(request: Request, file: UploadFile = File(...), project_id: str | None = Form(default=None),
                         sheet_name: str | None = Form(default=None), principal=Depends(require_principal)):
    _rate_limit(request, "import-upload", 20, 3600)
    limit = MAX_UPLOAD_GUEST if principal["kind"] == "GUEST" else MAX_UPLOAD_USER
    if principal["kind"] == "GUEST" and cloud_store.count_owned("datasets", principal["id"]) >= 3:
        raise HTTPException(403, "Guest dataset limit reached. Create an account to save more datasets.")
    if principal["kind"] == "USER" and cloud_store.count_owned("datasets", principal["id"]) >= 100:
        raise HTTPException(403, "Dataset quota reached")
    content = await file.read(limit + 1)
    if len(content) > limit:
        raise HTTPException(413, f"Upload limit is {limit // (1024 * 1024)} MB for this session")
    try:
        pid = _require_owner_project(principal["id"], project_id)
        parsed = read_tabular_file(file.filename or "uploaded.csv", content, sheet_name)
        if principal["kind"] == "GUEST" and parsed["row_count"] > 10000:
            raise HTTPException(413, "Guest sessions are limited to 10,000 rows per dataset")
        estimated_storage = cloud_store.dataset_storage_bytes(parsed["columns"], parsed["rows"])
        storage_limit = MAX_DATASET_STORAGE_GUEST if principal["kind"] == "GUEST" else MAX_DATASET_STORAGE_USER
        if cloud_store.sum_dataset_storage(principal["id"]) + estimated_storage > storage_limit:
            raise HTTPException(413, f"Dataset storage limit reached ({storage_limit // (1024 * 1024)} MiB). Delete unused datasets or reduce the upload size.")
        ds = cloud_store.create_dataset(principal["id"], pid, file.filename or "uploaded file",
                                        parsed["sheet_name"], parsed["columns"], parsed["rows"])
        return {**ds, "preview": parsed["preview"], "sheets": parsed.get("sheets"), "warnings": parsed["warnings"]}
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    except Exception as exc:
        logger.exception("Cloud dataset import failed")
        raise HTTPException(400, f"Could not import file: {exc}")


@app.get("/api/datasets/{dataset_id}")
def dataset_detail(dataset_id: str, principal=Depends(require_principal)):
    ds = cloud_store.get_dataset(dataset_id, principal["id"])
    if not ds:
        raise HTTPException(404, "Dataset not found")
    ds["preview"] = ds["rows"][:50]; ds.pop("rows", None)
    return ds


@app.get("/api/datasets/{dataset_id}/columns/{column_name}")
def dataset_column(dataset_id: str, column_name: str, principal=Depends(require_principal)):
    ds = cloud_store.get_dataset(dataset_id, principal["id"])
    if not ds:
        raise HTTPException(404, "Dataset not found")
    if column_name not in ds["columns"]:
        raise HTTPException(404, "Column not found")
    return {"dataset_id": dataset_id, "column": column_name, "values": [row.get(column_name) for row in ds["rows"]]}


@app.delete("/api/datasets/{dataset_id}")
def dataset_delete(dataset_id: str, principal=Depends(require_principal)):
    if not cloud_store.delete_dataset(dataset_id, principal["id"]):
        raise HTTPException(404, "Dataset not found")
    return {"deleted": True}


@app.post("/api/analyses/run")
def run_sync(req: AnalysisRequest, request: Request, principal=Depends(require_principal)):
    _rate_limit(request, "single-analysis", 30, 60)
    if req.module_key not in MODULE_MAP:
        raise HTTPException(404, "Unknown module")
    max_analyses = 10 if principal["kind"] == "GUEST" else 5000
    if cloud_store.count_owned("analyses", principal["id"]) >= max_analyses:
        raise HTTPException(403, "Analysis quota reached. Create an account to continue." if principal["kind"] == "GUEST" else "Analysis quota reached")
    try:
        pid, params, source = _prepare_cloud_task(req, principal["id"])
        result = clean_json(run_module(req.module_key, {k: v for k, v in params.items() if k != "_ors_source"}))
        title = req.title or MODULE_MAP[req.module_key]["name"]
        stored = _stored_params(params, source)
        aid = cloud_store.create_analysis(principal["id"], pid, req.module_key, title, stored, "SUCCEEDED")
        cloud_store.update_analysis(aid, principal["id"], "SUCCEEDED", output=result)
        return {"analysis_id": aid, "status": "SUCCEEDED", "module_key": req.module_key,
                "title": title, "input": stored, "output": result}
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    except KeyError as exc:
        raise HTTPException(400, f"Missing required parameter: {exc}")
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Cloud synchronous analysis failed")
        raise HTTPException(400, str(exc))


@app.post("/api/jobs/batch")
def submit_batch(req: BatchRequest, request: Request, principal=Depends(require_principal)):
    _rate_limit(request, "batch-submit", 10, 60)
    guest_limit = 5 if principal["kind"] == "GUEST" else 40
    if len(req.tasks) > guest_limit:
        raise HTTPException(403, f"Guest batch limit is {guest_limit} tasks. Create an account for larger batches.")
    if cloud_store.count_owned("jobs", principal["id"]) + len(req.tasks) > (10 if principal["kind"] == "GUEST" else 1000):
        raise HTTPException(403, "Analysis quota reached for this account")
    prepared = []
    try:
        for task in req.tasks:
            if task.module_key not in MODULE_MAP:
                raise HTTPException(404, f"Unknown module: {task.module_key}")
            pid, params, source = _prepare_cloud_task(task, principal["id"])
            title = task.title or MODULE_MAP[task.module_key]["name"]
            prepared.append({"project_id": pid, "module_key": task.module_key, "title": title,
                             "stored_params": _stored_params(params, source)})
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    except KeyError as exc:
        raise HTTPException(400, f"Missing required parameter: {exc}")
    records = cloud_store.create_batch_records(principal["id"], prepared)
    dispatched: set[str] = set()
    try:
        for index, record in enumerate(records):
            _dispatch_job(record["job_id"], record["analysis_id"], principal["id"],
                          record["module_key"], prepared[index]["stored_params"])
            dispatched.add(record["job_id"])
        return {"submitted": len(records), "jobs": [{k: r[k] for k in ("job_id", "analysis_id", "module_key", "title", "status")} for r in records],
                "parallel_workers": "managed queue" if os.getenv("REDIS_URL") else 2}
    except Exception as exc:
        # Records are committed before dispatch. Never leave undispatched records looking queued.
        for record in records:
            if record["job_id"] not in dispatched:
                message = "Queue dispatch failed; please submit this analysis again."
                cloud_store.update_job(record["job_id"], principal["id"], "FAILED", progress=100, error=message)
                cloud_store.update_analysis(record["analysis_id"], principal["id"], "FAILED", error=message)
        if isinstance(exc, HTTPException):
            raise
        logger.exception("Could not dispatch batch")
        raise HTTPException(503, "Could not submit all analysis jobs. Successfully dispatched jobs will continue; failed jobs can be resubmitted.") from exc


@app.get("/api/jobs")
def get_jobs(project_id: str | None = None, principal=Depends(require_principal)):
    pid = _require_owner_project(principal["id"], project_id)
    return {"jobs": cloud_store.list_jobs(pid, principal["id"])}


@app.get("/api/jobs/{job_id}")
def job_detail(job_id: str, principal=Depends(require_principal)):
    job = cloud_store.get_job(job_id, principal["id"])
    if not job:
        raise HTTPException(404, "Job not found")
    return job


@app.post("/api/jobs/{job_id}/cancel")
def cancel_job(job_id: str, principal=Depends(require_principal)):
    job = cloud_store.get_job(job_id, principal["id"])
    if not job:
        raise HTTPException(404, "Job not found")
    if job["status"] != "QUEUED":
        raise HTTPException(409, "Only queued jobs can be cancelled")
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        from redis import Redis
        from rq.job import Job
        try:
            rq_job = Job.fetch(job_id, connection=Redis.from_url(redis_url))
            rq_job.cancel()
        except Exception:
            raise HTTPException(409, "Job has already started")
    cloud_store.update_job(job_id, principal["id"], "CANCELLED", progress=0, error="Cancelled by user")
    cloud_store.update_analysis(job["analysis_id"], principal["id"], "CANCELLED", error="Cancelled by user")
    return {"cancelled": True}


@app.get("/api/analyses")
def get_analyses(project_id: str | None = None, limit: int = 100, principal=Depends(require_principal)):
    pid = _require_owner_project(principal["id"], project_id)
    return {"analyses": cloud_store.list_analyses(pid, principal["id"], max(1, min(limit, 500)))}


@app.get("/api/analyses/{analysis_id}")
def analysis_detail(analysis_id: str, principal=Depends(require_principal)):
    data = cloud_store.get_analysis(analysis_id, principal["id"])
    if not data:
        raise HTTPException(404, "Analysis not found")
    return data


@app.post("/api/forecast/compare")
def compare_forecast_cloud(req: ForecastCompareRequest, principal=Depends(require_principal)):
    return compare_forecasts(req)


@app.get("/api/analyses/{analysis_id}/export")
def export_analysis(analysis_id: str, format: str = "xlsx", principal=Depends(require_principal)):
    analysis = cloud_store.get_analysis(analysis_id, principal["id"])
    if not analysis:
        raise HTTPException(404, "Analysis not found")
    if analysis["status"] != "SUCCEEDED":
        raise HTTPException(409, "Only successful analyses can be exported")
    try:
        if format == "xlsx":
            content = export_service.build_excel(analysis); media = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"; ext = "xlsx"
        elif format == "csv":
            content = export_service.build_csv(analysis); media = "text/csv; charset=utf-8"; ext = "csv"
        elif format == "pdf":
            content = export_service.build_pdf(analysis); media = "application/pdf"; ext = "pdf"
        else:
            raise HTTPException(400, "format must be xlsx, csv, or pdf")
        filename = f"ors-{analysis['module_key']}-{analysis_id[:8]}.{ext}"
        return Response(content, media_type=media, headers={"Content-Disposition": f'attachment; filename="{filename}"'})
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Cloud export failed")
        raise HTTPException(500, f"Export failed: {exc}")


ROOT = Path(os.environ.get("ORS_APP_ROOT", Path(__file__).resolve().parents[2]))
FRONTEND = ROOT / "frontend"
if FRONTEND.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND), html=True), name="frontend")
