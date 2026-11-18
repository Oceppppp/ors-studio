from __future__ import annotations
import json
import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def data_dir() -> Path:
    location=Path(os.environ.get("ORS_DATA_DIR", Path.home()/".ors-studio"))
    location.mkdir(parents=True,exist_ok=True)
    return location


def db_path() -> Path:
    return data_dir()/"ors.sqlite3"


def connect() -> sqlite3.Connection:
    conn=sqlite3.connect(db_path(),timeout=30,check_same_thread=False)
    conn.row_factory=sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

@contextmanager
def db_session():
    conn=connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    with db_session() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY, name TEXT NOT NULL, description TEXT DEFAULT '',
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS datasets (
            id TEXT PRIMARY KEY, project_id TEXT NOT NULL, filename TEXT NOT NULL,
            sheet_name TEXT, columns_json TEXT NOT NULL, rows_json TEXT NOT NULL,
            row_count INTEGER NOT NULL, created_at TEXT NOT NULL,
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS analyses (
            id TEXT PRIMARY KEY, project_id TEXT NOT NULL, module_key TEXT NOT NULL,
            title TEXT NOT NULL, status TEXT NOT NULL, input_json TEXT NOT NULL,
            output_json TEXT, error TEXT, created_at TEXT NOT NULL, completed_at TEXT,
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY, analysis_id TEXT NOT NULL, project_id TEXT NOT NULL,
            status TEXT NOT NULL, progress INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL, started_at TEXT, finished_at TEXT, error TEXT,
            FOREIGN KEY(analysis_id) REFERENCES analyses(id) ON DELETE CASCADE,
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_datasets_project ON datasets(project_id, created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_analyses_project ON analyses(project_id, created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_jobs_project ON jobs(project_id, created_at DESC);
        """)
        row=conn.execute("SELECT id FROM projects ORDER BY created_at LIMIT 1").fetchone()
        if not row:
            stamp=now_iso();pid=str(uuid.uuid4())
            conn.execute("INSERT INTO projects(id,name,description,created_at,updated_at) VALUES(?,?,?,?,?)",(pid,"My ORS Project","Default local workspace",stamp,stamp))


def create_project(name: str, description: str = "") -> dict:
    pid=str(uuid.uuid4());stamp=now_iso()
    with db_session() as conn:
        conn.execute("INSERT INTO projects(id,name,description,created_at,updated_at) VALUES(?,?,?,?,?)",(pid,name,description,stamp,stamp))
    return {"id":pid,"name":name,"description":description,"created_at":stamp,"updated_at":stamp}


def list_projects() -> list[dict]:
    with db_session() as conn:
        return [dict(x) for x in conn.execute("SELECT * FROM projects ORDER BY updated_at DESC")]


def get_project(project_id: str) -> dict | None:
    with db_session() as conn:
        row=conn.execute("SELECT * FROM projects WHERE id=?",(project_id,)).fetchone()
        return dict(row) if row else None


def project_id_or_default(project_id: str | None = None) -> str:
    with db_session() as conn:
        if project_id:
            row=conn.execute("SELECT id FROM projects WHERE id=?",(project_id,)).fetchone()
            if not row: raise ValueError("Project not found")
            return project_id
        row=conn.execute("SELECT id FROM projects ORDER BY created_at LIMIT 1").fetchone()
        if not row: raise RuntimeError("Default project has not been initialized")
        return row["id"]


def create_dataset(project_id, filename, sheet_name, columns, rows):
    did=str(uuid.uuid4());stamp=now_iso()
    with db_session() as conn:
        conn.execute("INSERT INTO datasets(id,project_id,filename,sheet_name,columns_json,rows_json,row_count,created_at) VALUES(?,?,?,?,?,?,?,?)",(did,project_id,filename,sheet_name,json.dumps(columns,ensure_ascii=False),json.dumps(rows,ensure_ascii=False,allow_nan=False),len(rows),stamp))
        conn.execute("UPDATE projects SET updated_at=? WHERE id=?",(stamp,project_id))
    return {"id":did,"project_id":project_id,"filename":filename,"sheet_name":sheet_name,"columns":columns,"row_count":len(rows),"created_at":stamp}


def get_dataset(dataset_id: str) -> dict | None:
    with db_session() as conn:
        row=conn.execute("SELECT * FROM datasets WHERE id=?",(dataset_id,)).fetchone()
    if not row:return None
    result=dict(row);result["columns"]=json.loads(result.pop("columns_json"));result["rows"]=json.loads(result.pop("rows_json"));return result


def list_datasets(project_id: str) -> list[dict]:
    with db_session() as conn:
        rows=conn.execute("SELECT id,project_id,filename,sheet_name,row_count,created_at,columns_json FROM datasets WHERE project_id=? ORDER BY created_at DESC",(project_id,)).fetchall()
    return [{**{k:r[k] for k in r.keys() if k!="columns_json"},"columns":json.loads(r["columns_json"])} for r in rows]


def delete_dataset(dataset_id: str) -> bool:
    with db_session() as conn:
        cur=conn.execute("DELETE FROM datasets WHERE id=?",(dataset_id,))
        return cur.rowcount>0


def create_analysis(project_id,module_key,title,params,status="QUEUED"):
    aid=str(uuid.uuid4());stamp=now_iso()
    with db_session() as conn:
        conn.execute("INSERT INTO analyses(id,project_id,module_key,title,status,input_json,created_at) VALUES(?,?,?,?,?,?,?)",(aid,project_id,module_key,title,status,json.dumps(params,ensure_ascii=False,allow_nan=False),stamp))
        conn.execute("UPDATE projects SET updated_at=? WHERE id=?",(stamp,project_id))
    return aid


def update_analysis(analysis_id,status,output=None,error=None):
    with db_session() as conn:
        conn.execute("UPDATE analyses SET status=?,output_json=?,error=?,completed_at=? WHERE id=?",(status,json.dumps(output,ensure_ascii=False,allow_nan=False) if output is not None else None,error,now_iso() if status in {"SUCCEEDED","FAILED","CANCELLED"} else None,analysis_id))


def get_analysis(analysis_id):
    with db_session() as conn:
        row=conn.execute("SELECT * FROM analyses WHERE id=?",(analysis_id,)).fetchone()
    if not row:return None
    x=dict(row);x["input"]=json.loads(x.pop("input_json"));x["output"]=json.loads(x.pop("output_json")) if x.get("output_json") else None;return x


def list_analyses(project_id,limit=100):
    with db_session() as conn:
        rows=conn.execute("SELECT * FROM analyses WHERE project_id=? ORDER BY created_at DESC LIMIT ?",(project_id,limit)).fetchall()
    out=[]
    for row in rows:
        x=dict(row);x["input"]=json.loads(x.pop("input_json"));x["output"]=json.loads(x.pop("output_json")) if x.get("output_json") else None;out.append(x)
    return out


def create_job(analysis_id,project_id):
    jid=str(uuid.uuid4());stamp=now_iso()
    with db_session() as conn:
        conn.execute("INSERT INTO jobs(id,analysis_id,project_id,status,progress,created_at) VALUES(?,?,?,?,?,?)",(jid,analysis_id,project_id,"QUEUED",0,stamp))
    return jid


def create_batch_records(items):
    """Create all analysis and queued-job rows in one SQLite transaction."""
    created=[]
    with db_session() as conn:
        for item in items:
            aid=str(uuid.uuid4());jid=str(uuid.uuid4());stamp=now_iso()
            conn.execute(
                "INSERT INTO analyses(id,project_id,module_key,title,status,input_json,created_at) VALUES(?,?,?,?,?,?,?)",
                (aid,item["project_id"],item["module_key"],item["title"],"QUEUED",
                 json.dumps(item["stored_params"],ensure_ascii=False,allow_nan=False),stamp)
            )
            conn.execute(
                "INSERT INTO jobs(id,analysis_id,project_id,status,progress,created_at) VALUES(?,?,?,?,?,?)",
                (jid,aid,item["project_id"],"QUEUED",0,stamp)
            )
            conn.execute("UPDATE projects SET updated_at=? WHERE id=?",(stamp,item["project_id"]))
            created.append({"job_id":jid,"analysis_id":aid,"module_key":item["module_key"],
                            "title":item["title"],"status":"QUEUED",
                            "project_id":item["project_id"]})
    return created


def update_job(job_id,status,progress=None,error=None,started=False):
    with db_session() as conn:
        row=conn.execute("SELECT started_at FROM jobs WHERE id=?",(job_id,)).fetchone()
        if not row:return
        started_at=now_iso() if started and not row["started_at"] else row["started_at"]
        finished=now_iso() if status in {"SUCCEEDED","FAILED","CANCELLED"} else None
        if progress is None: conn.execute("UPDATE jobs SET status=?,started_at=?,finished_at=?,error=? WHERE id=?",(status,started_at,finished,error,job_id))
        else: conn.execute("UPDATE jobs SET status=?,progress=?,started_at=?,finished_at=?,error=? WHERE id=?",(status,progress,started_at,finished,error,job_id))


def list_jobs(project_id,limit=100):
    with db_session() as conn:
        rows=conn.execute("SELECT j.*,a.module_key,a.title,a.output_json FROM jobs j JOIN analyses a ON a.id=j.analysis_id WHERE j.project_id=? ORDER BY j.created_at DESC LIMIT ?",(project_id,limit)).fetchall()
    out=[]
    for r in rows:
        d=dict(r);d["output"]=json.loads(d.pop("output_json")) if d.get("output_json") else None;out.append(d)
    return out


def get_job(job_id):
    with db_session() as conn:
        r=conn.execute("SELECT j.*,a.module_key,a.title,a.output_json FROM jobs j JOIN analyses a ON a.id=j.analysis_id WHERE j.id=?",(job_id,)).fetchone()
    if not r:return None
    d=dict(r);d["output"]=json.loads(d.pop("output_json")) if d.get("output_json") else None;return d
