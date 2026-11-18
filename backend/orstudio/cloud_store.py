"""Tenant-aware persistence for the public ORS web application.

The desktop app keeps its isolated SQLite store in database.py. The web app uses
this module with PostgreSQL in production and SQLite only for tests/development.
Every project-scoped read/write requires a principal_id.
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Index, Integer,
                        JSON, MetaData, String, Table, Text, create_engine,
                        delete, insert, select, update, event)
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool

metadata = MetaData()
principals = Table(
    "ors_principals", metadata,
    Column("id", String(36), primary_key=True),
    Column("kind", String(12), nullable=False),  # USER | GUEST
    Column("email", String(320), unique=True, nullable=True),
    Column("password_hash", Text, nullable=True),
    Column("display_name", String(120), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("expires_at", DateTime(timezone=True), nullable=True),
    Column("is_active", Boolean, nullable=False, default=True),
)
sessions = Table(
    "ors_sessions", metadata,
    Column("token_hash", String(64), primary_key=True),
    Column("principal_id", String(36), ForeignKey("ors_principals.id", ondelete="CASCADE"), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("expires_at", DateTime(timezone=True), nullable=False),
)
projects = Table(
    "ors_projects", metadata,
    Column("id", String(36), primary_key=True),
    Column("owner_id", String(36), ForeignKey("ors_principals.id", ondelete="CASCADE"), nullable=False),
    Column("name", String(120), nullable=False),
    Column("description", String(1000), nullable=False, default=""),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)
datasets = Table(
    "ors_datasets", metadata,
    Column("id", String(36), primary_key=True),
    Column("project_id", String(36), ForeignKey("ors_projects.id", ondelete="CASCADE"), nullable=False),
    Column("filename", String(255), nullable=False),
    Column("sheet_name", String(255), nullable=True),
    Column("columns_json", JSON, nullable=False),
    Column("rows_json", JSON, nullable=False),
    Column("row_count", Integer, nullable=False),
    Column("storage_bytes", Integer, nullable=False, default=0),
    Column("created_at", DateTime(timezone=True), nullable=False),
)
analyses = Table(
    "ors_analyses", metadata,
    Column("id", String(36), primary_key=True),
    Column("project_id", String(36), ForeignKey("ors_projects.id", ondelete="CASCADE"), nullable=False),
    Column("module_key", String(80), nullable=False),
    Column("title", String(180), nullable=False),
    Column("status", String(20), nullable=False),
    Column("input_json", JSON, nullable=False),
    Column("output_json", JSON, nullable=True),
    Column("error", Text, nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("completed_at", DateTime(timezone=True), nullable=True),
)
jobs = Table(
    "ors_jobs", metadata,
    Column("id", String(36), primary_key=True),
    Column("analysis_id", String(36), ForeignKey("ors_analyses.id", ondelete="CASCADE"), nullable=False),
    Column("project_id", String(36), ForeignKey("ors_projects.id", ondelete="CASCADE"), nullable=False),
    Column("status", String(20), nullable=False),
    Column("progress", Integer, nullable=False, default=0),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("started_at", DateTime(timezone=True), nullable=True),
    Column("finished_at", DateTime(timezone=True), nullable=True),
    Column("error", Text, nullable=True),
)
Index("ix_ors_projects_owner_updated", projects.c.owner_id, projects.c.updated_at)
Index("ix_ors_datasets_project_created", datasets.c.project_id, datasets.c.created_at)
Index("ix_ors_analyses_project_created", analyses.c.project_id, analyses.c.created_at)
Index("ix_ors_jobs_project_created", jobs.c.project_id, jobs.c.created_at)

_engine: Engine | None = None


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def configure_database(url: str | None = None) -> Engine:
    """Configure engine; intended to be called once at application startup/tests."""
    global _engine
    if _engine is not None:
        _engine.dispose()
    database_url = url or os.getenv("DATABASE_URL", "sqlite:///./ors-web-dev.sqlite3")
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif database_url.startswith("postgresql://") and "+psycopg" not in database_url:
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    pool_class = StaticPool if database_url in {"sqlite://", "sqlite:///:memory:"} else None
    engine_options = {"pool_pre_ping": True, "future": True, "connect_args": connect_args}
    if pool_class: engine_options["poolclass"] = pool_class
    _engine = create_engine(database_url, **engine_options)
    if database_url.startswith("sqlite"):
        @event.listens_for(_engine, "connect")
        def _enable_sqlite_foreign_keys(dbapi_connection, _connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
    return _engine


def engine() -> Engine:
    global _engine
    if _engine is None:
        configure_database()
    assert _engine is not None
    return _engine


def init_db() -> None:
    metadata.create_all(engine())


def _dict(row) -> dict[str, Any] | None:
    return dict(row._mapping) if row is not None else None


def _iso(value):
    return value.isoformat() if value else None


def create_principal(kind: str, display_name: str, email: str | None = None,
                     password_hash: str | None = None, guest_hours: int = 24) -> dict:
    pid = str(uuid.uuid4()); now = utcnow()
    expires = now + timedelta(hours=guest_hours) if kind == "GUEST" else None
    values = {"id": pid, "kind": kind, "email": email, "password_hash": password_hash,
              "display_name": display_name, "created_at": now, "expires_at": expires, "is_active": True}
    with engine().begin() as conn:
        conn.execute(insert(principals).values(**values))
    return {**values, "created_at": _iso(now), "expires_at": _iso(expires), "password_hash": None}


def get_user_by_email(email: str) -> dict | None:
    with engine().connect() as conn:
        return _dict(conn.execute(select(principals).where(principals.c.email == email, principals.c.kind == "USER")).first())


def create_session(token_hash: str, principal_id: str, ttl_hours: int) -> None:
    now = utcnow()
    with engine().begin() as conn:
        conn.execute(insert(sessions).values(token_hash=token_hash, principal_id=principal_id,
                                             created_at=now, expires_at=now + timedelta(hours=ttl_hours)))


def get_principal_by_session(token_hash: str) -> dict | None:
    now = utcnow()
    query = select(principals).join(sessions, sessions.c.principal_id == principals.c.id).where(
        sessions.c.token_hash == token_hash, sessions.c.expires_at > now,
        principals.c.is_active.is_(True),
    )
    with engine().connect() as conn:
        return _dict(conn.execute(query).first())


def delete_session(token_hash: str) -> None:
    with engine().begin() as conn:
        conn.execute(delete(sessions).where(sessions.c.token_hash == token_hash))


def delete_expired_guests() -> int:
    now = utcnow()
    with engine().begin() as conn:
        ids = select(principals.c.id).where(principals.c.kind == "GUEST", principals.c.expires_at < now)
        conn.execute(delete(sessions).where(sessions.c.principal_id.in_(ids)))
        result = conn.execute(delete(principals).where(principals.c.kind == "GUEST", principals.c.expires_at < now))
        return result.rowcount or 0


def _owned_project(conn, project_id: str, owner_id: str):
    return conn.execute(select(projects).where(projects.c.id == project_id, projects.c.owner_id == owner_id)).first()


def create_project(owner_id: str, name: str, description: str = "") -> dict:
    pid = str(uuid.uuid4()); now = utcnow()
    values = {"id": pid, "owner_id": owner_id, "name": name, "description": description,
              "created_at": now, "updated_at": now}
    with engine().begin() as conn:
        conn.execute(insert(projects).values(**values))
    return {**values, "created_at": _iso(now), "updated_at": _iso(now)}


def ensure_default_project(owner_id: str) -> str:
    with engine().begin() as conn:
        row = conn.execute(select(projects.c.id).where(projects.c.owner_id == owner_id).order_by(projects.c.created_at).limit(1)).first()
        if row:
            return row[0]
        pid = str(uuid.uuid4()); now = utcnow()
        conn.execute(insert(projects).values(id=pid, owner_id=owner_id, name="My ORS Workspace",
                                             description="Personal workspace", created_at=now, updated_at=now))
        return pid


def list_projects(owner_id: str) -> list[dict]:
    with engine().connect() as conn:
        rows = conn.execute(select(projects).where(projects.c.owner_id == owner_id).order_by(projects.c.updated_at.desc())).all()
    return [{**dict(r._mapping), "created_at": _iso(r.created_at), "updated_at": _iso(r.updated_at)} for r in rows]


def get_project(project_id: str, owner_id: str) -> dict | None:
    with engine().connect() as conn:
        row = _owned_project(conn, project_id, owner_id)
    result = _dict(row)
    if result:
        result["created_at"] = _iso(result["created_at"]); result["updated_at"] = _iso(result["updated_at"])
    return result


def project_id_or_default(owner_id: str, project_id: str | None = None) -> str:
    if project_id:
        if not get_project(project_id, owner_id):
            raise ValueError("Project not found")
        return project_id
    return ensure_default_project(owner_id)


def dataset_storage_bytes(columns: list[str], rows: list[dict]) -> int:
    """Estimate persisted normalized dataset size, including JSON serialization overhead."""
    payload = json.dumps({"columns": columns, "rows": rows}, ensure_ascii=False,
                         separators=(",", ":"), allow_nan=False).encode("utf-8")
    return len(payload)


def sum_dataset_storage(owner_id: str) -> int:
    from sqlalchemy import func
    query = select(func.coalesce(func.sum(datasets.c.storage_bytes), 0)).select_from(
        datasets.join(projects, projects.c.id == datasets.c.project_id)
    ).where(projects.c.owner_id == owner_id)
    with engine().connect() as conn:
        return int(conn.execute(query).scalar_one())


def create_dataset(owner_id: str, project_id: str, filename: str, sheet_name: str | None,
                   columns: list[str], rows: list[dict]) -> dict:
    if not get_project(project_id, owner_id):
        raise ValueError("Project not found")
    did = str(uuid.uuid4()); now = utcnow()
    persisted_bytes = dataset_storage_bytes(columns, rows)
    with engine().begin() as conn:
        conn.execute(insert(datasets).values(id=did, project_id=project_id, filename=filename,
            sheet_name=sheet_name, columns_json=columns, rows_json=rows,
            row_count=len(rows), storage_bytes=persisted_bytes, created_at=now))
        conn.execute(update(projects).where(projects.c.id == project_id, projects.c.owner_id == owner_id).values(updated_at=now))
    return {"id": did, "project_id": project_id, "filename": filename, "sheet_name": sheet_name,
            "columns": columns, "row_count": len(rows), "storage_bytes": persisted_bytes, "created_at": _iso(now)}


def get_dataset(dataset_id: str, owner_id: str) -> dict | None:
    query = select(datasets).join(projects, projects.c.id == datasets.c.project_id).where(
        datasets.c.id == dataset_id, projects.c.owner_id == owner_id)
    with engine().connect() as conn:
        result = _dict(conn.execute(query).first())
    if result:
        result["columns"] = result.pop("columns_json")
        result["rows"] = result.pop("rows_json")
        result["created_at"] = _iso(result["created_at"])
    return result


def list_datasets(project_id: str, owner_id: str) -> list[dict]:
    query = select(datasets).join(projects, projects.c.id == datasets.c.project_id).where(
        datasets.c.project_id == project_id, projects.c.owner_id == owner_id).order_by(datasets.c.created_at.desc())
    with engine().connect() as conn:
        rows = conn.execute(query).all()
    return [{"id": r.id, "project_id": r.project_id, "filename": r.filename, "sheet_name": r.sheet_name,
             "columns": r.columns_json, "row_count": r.row_count, "storage_bytes": r.storage_bytes,
             "created_at": _iso(r.created_at)} for r in rows]


def delete_dataset(dataset_id: str, owner_id: str) -> bool:
    query = delete(datasets).where(datasets.c.id == dataset_id).where(datasets.c.project_id.in_(
        select(projects.c.id).where(projects.c.owner_id == owner_id)))
    with engine().begin() as conn:
        return (conn.execute(query).rowcount or 0) > 0


def create_analysis(owner_id: str, project_id: str, module_key: str, title: str, params: dict, status="QUEUED") -> str:
    if not get_project(project_id, owner_id):
        raise ValueError("Project not found")
    aid = str(uuid.uuid4()); now = utcnow()
    with engine().begin() as conn:
        conn.execute(insert(analyses).values(id=aid, project_id=project_id, module_key=module_key,
            title=title, status=status, input_json=params, created_at=now))
        conn.execute(update(projects).where(projects.c.id == project_id).values(updated_at=now))
    return aid


def create_batch_records(owner_id: str, items: list[dict]) -> list[dict]:
    created = []; now = utcnow()
    with engine().begin() as conn:
        for item in items:
            if not _owned_project(conn, item["project_id"], owner_id):
                raise ValueError("Project not found")
            aid, jid = str(uuid.uuid4()), str(uuid.uuid4())
            conn.execute(insert(analyses).values(id=aid, project_id=item["project_id"], module_key=item["module_key"],
                title=item["title"], status="QUEUED", input_json=item["stored_params"], created_at=now))
            conn.execute(insert(jobs).values(id=jid, analysis_id=aid, project_id=item["project_id"],
                status="QUEUED", progress=0, created_at=now))
            conn.execute(update(projects).where(projects.c.id == item["project_id"]).values(updated_at=now))
            created.append({"job_id": jid, "analysis_id": aid, "module_key": item["module_key"],
                            "title": item["title"], "status": "QUEUED", "project_id": item["project_id"]})
    return created


def get_analysis(analysis_id: str, owner_id: str) -> dict | None:
    query = select(analyses).join(projects, projects.c.id == analyses.c.project_id).where(
        analyses.c.id == analysis_id, projects.c.owner_id == owner_id)
    with engine().connect() as conn:
        result = _dict(conn.execute(query).first())
    if result:
        result["input"] = result.pop("input_json")
        result["output"] = result.pop("output_json")
        result["created_at"] = _iso(result["created_at"]); result["completed_at"] = _iso(result["completed_at"])
    return result


def update_analysis(analysis_id: str, owner_id: str, status: str, output=None, error=None) -> None:
    query = update(analyses).where(analyses.c.id == analysis_id).where(analyses.c.project_id.in_(
        select(projects.c.id).where(projects.c.owner_id == owner_id)))
    values = {"status": status, "output_json": output, "error": error,
              "completed_at": utcnow() if status in {"SUCCEEDED", "FAILED", "CANCELLED"} else None}
    with engine().begin() as conn:
        conn.execute(query.values(**values))


def list_analyses(project_id: str, owner_id: str, limit=100) -> list[dict]:
    query = select(analyses).join(projects, projects.c.id == analyses.c.project_id).where(
        analyses.c.project_id == project_id, projects.c.owner_id == owner_id).order_by(analyses.c.created_at.desc()).limit(limit)
    with engine().connect() as conn:
        rows = conn.execute(query).all()
    return [{"id": r.id, "project_id": r.project_id, "module_key": r.module_key, "title": r.title,
             "status": r.status, "input": r.input_json, "output": r.output_json, "error": r.error,
             "created_at": _iso(r.created_at), "completed_at": _iso(r.completed_at)} for r in rows]


def create_job(analysis_id: str, project_id: str, owner_id: str) -> str:
    if not get_project(project_id, owner_id):
        raise ValueError("Project not found")
    jid = str(uuid.uuid4()); now = utcnow()
    with engine().begin() as conn:
        conn.execute(insert(jobs).values(id=jid, analysis_id=analysis_id, project_id=project_id,
                                         status="QUEUED", progress=0, created_at=now))
    return jid


def update_job(job_id: str, owner_id: str, status: str, progress=None, error=None, started=False) -> None:
    query = update(jobs).where(jobs.c.id == job_id).where(jobs.c.project_id.in_(
        select(projects.c.id).where(projects.c.owner_id == owner_id)))
    with engine().begin() as conn:
        row = conn.execute(select(jobs.c.started_at).where(jobs.c.id == job_id).where(
            jobs.c.project_id.in_(select(projects.c.id).where(projects.c.owner_id == owner_id)))).first()
        if not row:
            return
        values = {"status": status, "error": error}
        if progress is not None: values["progress"] = progress
        if started and row.started_at is None: values["started_at"] = utcnow()
        if status in {"SUCCEEDED", "FAILED", "CANCELLED"}: values["finished_at"] = utcnow()
        conn.execute(query.values(**values))


def list_jobs(project_id: str, owner_id: str, limit=100) -> list[dict]:
    query = select(jobs, analyses.c.module_key, analyses.c.title, analyses.c.output_json).join(
        analyses, analyses.c.id == jobs.c.analysis_id).join(projects, projects.c.id == jobs.c.project_id).where(
        jobs.c.project_id == project_id, projects.c.owner_id == owner_id).order_by(jobs.c.created_at.desc()).limit(limit)
    with engine().connect() as conn:
        rows = conn.execute(query).all()
    return [{"id": r.id, "analysis_id": r.analysis_id, "project_id": r.project_id, "status": r.status,
             "progress": r.progress, "created_at": _iso(r.created_at), "started_at": _iso(r.started_at),
             "finished_at": _iso(r.finished_at), "error": r.error, "module_key": r.module_key,
             "title": r.title, "output": r.output_json} for r in rows]


def get_job(job_id: str, owner_id: str) -> dict | None:
    query = select(jobs, analyses.c.module_key, analyses.c.title, analyses.c.output_json).join(
        analyses, analyses.c.id == jobs.c.analysis_id).join(projects, projects.c.id == jobs.c.project_id).where(
        jobs.c.id == job_id, projects.c.owner_id == owner_id)
    with engine().connect() as conn:
        r = conn.execute(query).first()
    if not r: return None
    return {"id": r.id, "analysis_id": r.analysis_id, "project_id": r.project_id, "status": r.status,
            "progress": r.progress, "created_at": _iso(r.created_at), "started_at": _iso(r.started_at),
            "finished_at": _iso(r.finished_at), "error": r.error, "module_key": r.module_key,
            "title": r.title, "output": r.output_json}


def count_owned(table_name: str, owner_id: str) -> int:
    from sqlalchemy import func
    table = {"projects": projects, "datasets": datasets, "analyses": analyses, "jobs": jobs}[table_name]
    if table_name == "projects":
        query = select(func.count()).select_from(table).where(table.c.owner_id == owner_id)
    else:
        query = select(func.count()).select_from(table.join(projects, projects.c.id == table.c.project_id)).where(projects.c.owner_id == owner_id)
    with engine().connect() as conn:
        return int(conn.execute(query).scalar_one())
