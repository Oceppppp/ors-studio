from __future__ import annotations

import logging

from . import cloud_store
from .api import clean_json
from .registry import run_module

logger = logging.getLogger("ors.cloud.worker")


def process_job(job_id: str, analysis_id: str, owner_id: str, module_key: str, params: dict) -> None:
    """RQ worker entry point; only IDs and JSON-serializable data cross the queue."""
    cloud_store.update_job(job_id, owner_id, "RUNNING", progress=10, started=True)
    cloud_store.update_analysis(analysis_id, owner_id, "RUNNING")
    try:
        solver_params = {k: v for k, v in params.items() if k != "_ors_source"}
        result = clean_json(run_module(module_key, solver_params))
        cloud_store.update_analysis(analysis_id, owner_id, "SUCCEEDED", output=result)
        cloud_store.update_job(job_id, owner_id, "SUCCEEDED", progress=100)
        logger.info("Cloud analysis %s completed: %s", analysis_id, module_key)
    except Exception as exc:  # keep the worker alive and persist a useful failure state
        logger.exception("Cloud analysis %s failed", analysis_id)
        message = str(exc) or exc.__class__.__name__
        cloud_store.update_analysis(analysis_id, owner_id, "FAILED", error=message)
        cloud_store.update_job(job_id, owner_id, "FAILED", progress=100, error=message)
