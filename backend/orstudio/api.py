from __future__ import annotations

import json
import logging
import math
import os
from concurrent.futures import ThreadPoolExecutor, Future
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
from typing import Any

import numpy as np
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import database
from .registry import MODULES, MODULE_MAP, run_module
from .services.import_service import read_tabular_file, inspect_tabular_file
from .services import export_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger=logging.getLogger("ors")
WORKER_COUNT=max(2,min(4,os.cpu_count() or 2))
POOL:ThreadPoolExecutor|None=None
FUTURES:dict[str,Future]={}


@asynccontextmanager
async def lifespan(app: FastAPI):
    global POOL
    database.init_db()
    POOL=ThreadPoolExecutor(max_workers=WORKER_COUNT,thread_name_prefix="ors-worker")
    try:
        yield
    finally:
        if POOL is not None:
            POOL.shutdown(wait=False,cancel_futures=True)
            POOL=None
        FUTURES.clear()

app=FastAPI(title="Operations Research Studio API",version="0.4.0",description="Local-first operations research and quantitative analysis platform",lifespan=lifespan)


@app.middleware("http")
async def protect_local_mutations(request: Request, call_next):
    """Reject cross-origin mutations to the unauthenticated loopback API."""
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        origin = request.headers.get("origin")
        if origin:
            try:
                origin_parts = urlsplit(origin)
                request_host = urlsplit(f"//{request.headers.get('host', '')}")
                allowed_hosts = {"127.0.0.1", "localhost"}
                valid_origin = (
                    origin_parts.scheme == request.url.scheme
                    and origin_parts.hostname in allowed_hosts
                    and request_host.hostname in allowed_hosts
                    and origin_parts.hostname == request_host.hostname
                    and origin_parts.port == request.url.port
                )
            except ValueError:
                valid_origin = False
            if not valid_origin:
                return JSONResponse(status_code=403, content={"detail": "Cross-origin changes are not allowed by the local ORS service"})
    return await call_next(request)


class ProjectCreate(BaseModel):
    name: str=Field(min_length=1,max_length=120)
    description: str=Field(default="",max_length=1000)

class AnalysisRequest(BaseModel):
    module_key: str
    params: dict[str,Any]
    project_id: str|None=None
    dataset_id: str|None=None
    column_map: dict[str,str]=Field(default_factory=dict)
    title: str|None=None

class BatchRequest(BaseModel):
    tasks: list[AnalysisRequest]=Field(min_length=1,max_length=40)

class ForecastCompareRequest(BaseModel):
    values: list[float]=Field(min_length=5)
    methods: list[str]=Field(default_factory=lambda:["naive","moving_average","weighted_moving_average","ses","linear_trend"])
    holdout: int=Field(default=3,ge=1,le=30)
    window: int=Field(default=3,ge=1,le=50)
    alpha: float=Field(default=.3,gt=0,le=1)
    weights: list[float]=Field(default_factory=lambda:[1,2,3])


def clean_json(value):
    if isinstance(value,dict): return {str(k):clean_json(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)): return [clean_json(v) for v in value]
    if isinstance(value,(np.integer,)): return int(value)
    if isinstance(value,(np.floating,)): return float(value) if np.isfinite(value) else None
    if isinstance(value,(np.bool_,)): return bool(value)
    if isinstance(value,float) and not math.isfinite(value): return None
    if isinstance(value,(str,int,float,bool)) or value is None: return value
    return str(value)


def _set_path(target:dict,path:str,value):
    parts=path.split(".");cur=target
    for part in parts[:-1]:
        if part not in cur or not isinstance(cur[part],dict):cur[part]={}
        cur=cur[part]
    cur[parts[-1]]=value


def _prepare_task(req:AnalysisRequest):
    params=json.loads(json.dumps(req.params))
    if req.column_map and not req.dataset_id:
        raise ValueError("A dataset must be selected before applying column mappings")
    source=None
    project_id=req.project_id
    if req.dataset_id:
        ds=database.get_dataset(req.dataset_id)
        if not ds: raise ValueError("Dataset not found")
        if project_id and ds["project_id"]!=project_id:
            raise ValueError("Dataset does not belong to the selected project")
        project_id=project_id or ds["project_id"]
        for param_path,column in req.column_map.items():
            if column not in ds["columns"]: raise ValueError(f"Column '{column}' not found in dataset")
            raw_values=[row.get(column) for row in ds["rows"]]
            if any(v is None or (isinstance(v,str) and not v.strip()) for v in raw_values):
                raise ValueError(f"Mapped column '{column}' contains blank values; clean the dataset or choose another column")
            try: values=[float(v) for v in raw_values]
            except (ValueError,TypeError) as exc: raise ValueError(f"Mapped column '{column}' must contain numeric values") from exc
            _set_path(params,param_path,values)
        source={"dataset_id":ds["id"],"filename":ds["filename"],"sheet_name":ds["sheet_name"],
                "column_map":dict(req.column_map),"row_count":ds["row_count"]}
    project_id=database.project_id_or_default(project_id)
    return project_id,params,source


def _stored_params(params,source):
    stored=dict(params)
    if source:
        stored["_ors_source"]={**source,"mapping_applied_at":datetime.now(timezone.utc).isoformat()}
    return stored


def _run_worker(job_id,analysis_id,module_key,params):
    database.update_job(job_id,"RUNNING",progress=10,started=True)
    database.update_analysis(analysis_id,"RUNNING")
    try:
        solver_params={key:value for key,value in params.items() if key!="_ors_source"}
        result=clean_json(run_module(module_key,solver_params))
        database.update_analysis(analysis_id,"SUCCEEDED",output=result)
        database.update_job(job_id,"SUCCEEDED",progress=100)
        logger.info("Analysis %s completed (%s)",analysis_id,module_key)
    except Exception as exc:
        logger.exception("Analysis %s failed",analysis_id)
        message=str(exc) or exc.__class__.__name__
        database.update_analysis(analysis_id,"FAILED",error=message)
        database.update_job(job_id,"FAILED",progress=100,error=message)



@app.get("/api/health")
def health():
    return {"status":"ok","name":"Operations Research Studio","version":"0.4.0","worker_count":WORKER_COUNT}

@app.get("/api/modules")
def get_modules():
    return {"count":len(MODULES),"modules":MODULES}

@app.get("/api/projects")
def get_projects():
    return {"projects":database.list_projects()}

@app.post("/api/projects")
def post_project(payload:ProjectCreate):
    try:return database.create_project(payload.name.strip(),payload.description.strip())
    except Exception as exc: raise HTTPException(400,str(exc))

@app.get("/api/datasets")
def get_datasets(project_id:str|None=None):
    try:pid=database.project_id_or_default(project_id)
    except ValueError as exc:raise HTTPException(404,str(exc))
    return {"datasets":database.list_datasets(pid)}

@app.post("/api/datasets/inspect")
async def inspect_dataset(file:UploadFile=File(...)):
    content=await file.read(20*1024*1024+1)
    try:
        return inspect_tabular_file(file.filename or "uploaded.csv",content)
    except ValueError as exc:
        raise HTTPException(400,str(exc))
    except Exception as exc:
        logger.exception("Dataset inspection failed")
        raise HTTPException(400,f"Could not inspect file: {exc}")

@app.post("/api/datasets/import")
async def import_dataset(file:UploadFile=File(...),project_id:str|None=Form(default=None),sheet_name:str|None=Form(default=None)):
    try:
        pid=database.project_id_or_default(project_id)
        content=await file.read(20*1024*1024+1)
        parsed=read_tabular_file(file.filename or "uploaded.csv",content,sheet_name)
        ds=database.create_dataset(pid,file.filename or "uploaded file",parsed["sheet_name"],parsed["columns"],parsed["rows"])
        return {**ds,"preview":parsed["preview"],"sheets":parsed.get("sheets"),"warnings":parsed["warnings"]}
    except ValueError as exc:raise HTTPException(400,str(exc))
    except Exception as exc:
        logger.exception("Dataset import failed")
        raise HTTPException(400,f"Could not import dataset: {exc}")

@app.get("/api/datasets/{dataset_id}")
def dataset_detail(dataset_id:str):
    ds=database.get_dataset(dataset_id)
    if not ds:raise HTTPException(404,"Dataset not found")
    ds["preview"]=ds["rows"][:50];ds.pop("rows",None)
    return ds

@app.get("/api/datasets/{dataset_id}/columns/{column_name}")
def dataset_column(dataset_id:str,column_name:str):
    ds=database.get_dataset(dataset_id)
    if not ds: raise HTTPException(404,"Dataset not found")
    if column_name not in ds["columns"]: raise HTTPException(404,"Column not found")
    return {"dataset_id":dataset_id,"column":column_name,"values":[row.get(column_name) for row in ds["rows"]]}

@app.delete("/api/datasets/{dataset_id}")
def dataset_delete(dataset_id:str):
    if not database.delete_dataset(dataset_id):raise HTTPException(404,"Dataset not found")
    return {"deleted":True}

@app.post("/api/analyses/run")
def run_sync(req:AnalysisRequest):
    if req.module_key not in MODULE_MAP:raise HTTPException(404,"Unknown module")
    try:
        pid,params,source=_prepare_task(req)
        result=clean_json(run_module(req.module_key,params))
        title=req.title or MODULE_MAP[req.module_key]["name"]
        stored=_stored_params(params,source)
        aid=database.create_analysis(pid,req.module_key,title,stored,"SUCCEEDED")
        database.update_analysis(aid,"SUCCEEDED",output=result)
        return {"analysis_id":aid,"status":"SUCCEEDED","module_key":req.module_key,"title":title,"input":stored,"output":result}
    except ValueError as exc:raise HTTPException(400,str(exc))
    except KeyError as exc:raise HTTPException(400,f"Missing required parameter: {exc}")
    except Exception as exc:
        logger.exception("Synchronous analysis failed")
        raise HTTPException(400,str(exc))

@app.post("/api/jobs/batch")
def submit_batch(req:BatchRequest):
    prepared=[]
    try:
        # Validate every dataset mapping/project before writing or submitting any job.
        for task in req.tasks:
            if task.module_key not in MODULE_MAP:
                raise HTTPException(404,f"Unknown module: {task.module_key}")
            pid,params,source=_prepare_task(task)
            title=task.title or MODULE_MAP[task.module_key]["name"]
            prepared.append({"project_id":pid,"module_key":task.module_key,"title":title,
                             "solver_params":params,"stored_params":_stored_params(params,source)})
    except HTTPException:
        raise
    except ValueError as exc:raise HTTPException(400,str(exc))
    except KeyError as exc:raise HTTPException(400,f"Missing required parameter: {exc}")

    if POOL is None:
        raise HTTPException(503,"Analysis worker pool is not ready")
    records=database.create_batch_records(prepared)
    created=[]
    for index,record in enumerate(records):
        future=POOL.submit(_run_worker,record["job_id"],record["analysis_id"],
                            record["module_key"],prepared[index]["stored_params"])
        FUTURES[record["job_id"]]=future
        future.add_done_callback(lambda _future, job_id=record["job_id"]: FUTURES.pop(job_id,None))
        created.append({key:record[key] for key in ("job_id","analysis_id","module_key","title","status")})
    return {"submitted":len(created),"jobs":created,"parallel_workers":POOL._max_workers}

@app.get("/api/jobs")
def get_jobs(project_id:str|None=None):
    try:pid=database.project_id_or_default(project_id)
    except ValueError as exc:raise HTTPException(404,str(exc))
    return {"jobs":database.list_jobs(pid)}

@app.get("/api/jobs/{job_id}")
def job_detail(job_id:str):
    job=database.get_job(job_id)
    if not job:raise HTTPException(404,"Job not found")
    return job

@app.post("/api/jobs/{job_id}/cancel")
def cancel_job(job_id:str):
    job=database.get_job(job_id)
    if not job:raise HTTPException(404,"Job not found")
    if job["status"]!="QUEUED":raise HTTPException(409,"Only queued jobs can be cancelled")
    future=FUTURES.get(job_id)
    if future and future.cancel():
        database.update_job(job_id,"CANCELLED",progress=0)
        database.update_analysis(job["analysis_id"],"CANCELLED",error="Cancelled by user")
        return {"cancelled":True}
    raise HTTPException(409,"Job has already started")

@app.get("/api/analyses")
def get_analyses(project_id:str|None=None,limit:int=100):
    try:pid=database.project_id_or_default(project_id)
    except ValueError as exc:raise HTTPException(404,str(exc))
    return {"analyses":database.list_analyses(pid,max(1,min(limit,500)))}

@app.get("/api/analyses/{analysis_id}")
def analysis_detail(analysis_id:str):
    data=database.get_analysis(analysis_id)
    if not data:raise HTTPException(404,"Analysis not found")
    return data

@app.post("/api/forecast/compare")
def compare_forecasts(req:ForecastCompareRequest):
    from .modules import forecasting
    values=[float(x) for x in req.values];h=req.holdout
    if not np.isfinite(values).all():
        raise HTTPException(400,"forecast values must all be finite numbers")
    if not req.methods:
        raise HTTPException(400,"select at least one forecasting method")
    if h>=len(values)-1:raise HTTPException(400,"holdout must be smaller than number of observations minus one")
    allowed={"naive","moving_average","weighted_moving_average","ses","linear_trend"}
    methods=[m.lower() for m in req.methods]
    invalid=[m for m in methods if m not in allowed]
    if invalid:raise HTTPException(400,f"Unsupported method(s): {', '.join(invalid)}")
    results=[]
    for method in methods:
        actual=[];pred=[]
        for index in range(len(values)-h,len(values)):
            train=values[:index]
            try:
                if method=="naive":r=forecasting.naive(train,1)
                elif method=="moving_average":r=forecasting.moving_average(train,min(req.window,len(train)-1),1)
                elif method=="weighted_moving_average":
                    w=req.weights[-min(len(req.weights),len(train)):]
                    r=forecasting.weighted_moving_average(train,w,1)
                elif method=="ses":r=forecasting.simple_exponential_smoothing(train,req.alpha,1)
                else:r=forecasting.linear_trend(train,1)
                pred.append(float(r["forecast"][0]));actual.append(values[index])
            except ValueError as exc:
                pred=[];actual=[];break
        if pred:
            metrics=forecasting._metrics(actual,pred)
            full=forecasting.run({"method":method,"values":values,"horizon":1,"window":req.window,"alpha":req.alpha,"weights":req.weights})
            results.append({"method":method,"metrics":metrics,"holdout_actual":actual,"holdout_forecast":pred,"next_period_forecast":full["forecast"][0]})
        else:results.append({"method":method,"metrics":None,"error":"Insufficient history for selected method/parameters"})
    valid=[r for r in results if r.get("metrics")]
    best=min(valid,key=lambda r:(r["metrics"]["MAD"],r["metrics"]["MSE"])) if valid else None
    return {"holdout_periods":h,"results":results,"best_method":best["method"] if best else None,"selection_rule":"Lowest holdout MAD; MSE breaks ties.","assumptions":["Rolling-origin one-step holdout evaluation; the final holdout points are predicted sequentially from prior actuals.","Methods are ranked only when each has valid predictions for every holdout point."]}

@app.get("/api/analyses/{analysis_id}/export")
def export_analysis(analysis_id:str,format:str="xlsx"):
    analysis=database.get_analysis(analysis_id)
    if not analysis:raise HTTPException(404,"Analysis not found")
    if analysis["status"]!="SUCCEEDED":raise HTTPException(409,"Only successful analyses can be exported")
    try:
        if format=="xlsx":content=export_service.build_excel(analysis);media="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet";ext="xlsx"
        elif format=="csv":content=export_service.build_csv(analysis);media="text/csv; charset=utf-8";ext="csv"
        elif format=="pdf":content=export_service.build_pdf(analysis);media="application/pdf";ext="pdf"
        else:raise HTTPException(400,"format must be xlsx, csv, or pdf")
        filename=f"ors-{analysis['module_key']}-{analysis_id[:8]}.{ext}"
        return Response(content,media_type=media,headers={"Content-Disposition":f'attachment; filename="{filename}"'})
    except HTTPException:raise
    except Exception as exc:
        logger.exception("Export failed")
        raise HTTPException(500,f"Export failed: {exc}")

# Static frontend is served by FastAPI so the app runs from one local origin.
ROOT=Path(os.environ.get("ORS_APP_ROOT", Path(__file__).resolve().parents[2]))
FRONTEND=ROOT/"frontend"
if FRONTEND.exists():
    app.mount("/",StaticFiles(directory=str(FRONTEND),html=True),name="frontend")
