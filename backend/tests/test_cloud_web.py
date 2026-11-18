from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

from orstudio import cloud_store
from orstudio.web_api import app


@pytest.fixture()
def web_client(monkeypatch, tmp_path):
    monkeypatch.setenv("ORS_ENV", "development")
    monkeypatch.setenv("ORS_SESSION_SECRET", "test-session-secret-very-long")
    monkeypatch.delenv("REDIS_URL", raising=False)
    cloud_store.configure_database(f"sqlite:///{tmp_path / 'ors-cloud-tests.sqlite3'}")
    with TestClient(app, base_url="http://testserver") as client:
        yield client
    cloud_store.engine().dispose()


def post(client, path, **kwargs):
    headers = kwargs.pop("headers", {})
    headers.setdefault("origin", "http://testserver")
    return client.post(path, headers=headers, **kwargs)


def test_guest_can_enter_and_get_isolated_workspace(web_client):
    client = web_client
    unauthenticated = client.get("/api/projects")
    assert unauthenticated.status_code == 401

    guest = post(client, "/api/auth/guest", json={})
    assert guest.status_code == 200
    assert guest.json()["kind"] == "GUEST"
    assert client.cookies.get("ors_session")

    projects = client.get("/api/projects").json()["projects"]
    assert len(projects) == 1
    assert projects[0]["owner_id"]
    assert client.get("/api/auth/me").json()["authenticated"] is True


def test_account_register_login_and_password_policy(web_client):
    bad = post(web_client, "/api/auth/register", json={
        "email": "new@example.com", "password": "short", "display_name": "New User"
    })
    assert bad.status_code == 422  # Pydantic minimum length

    created = post(web_client, "/api/auth/register", json={
        "email": "analyst@example.com", "password": "a-very-long-password-123", "display_name": "Analyst"
    })
    assert created.status_code == 200
    assert created.json()["kind"] == "USER"
    assert created.json()["email"] == "analyst@example.com"

    duplicate = post(web_client, "/api/auth/register", json={
        "email": "analyst@example.com", "password": "a-very-long-password-123", "display_name": "Analyst"
    })
    assert duplicate.status_code == 409

    logout = post(web_client, "/api/auth/logout", json={})
    assert logout.status_code == 200
    assert web_client.get("/api/projects").status_code == 401

    login = post(web_client, "/api/auth/login", json={
        "email": "analyst@example.com", "password": "a-very-long-password-123"
    })
    assert login.status_code == 200
    assert web_client.get("/api/projects").status_code == 200


def test_guest_upgrade_keeps_existing_projects(web_client):
    post(web_client, "/api/auth/guest", json={})
    created = post(web_client, "/api/projects", json={"name": "My study", "description": "test"})
    assert created.status_code == 200
    before = {p["id"] for p in web_client.get("/api/projects").json()["projects"]}

    upgraded = post(web_client, "/api/auth/upgrade", json={
        "email": "keep@example.com", "password": "another-long-password-456", "display_name": "Guest Converted"
    })
    assert upgraded.status_code == 200
    assert upgraded.json()["kind"] == "USER"
    after = {p["id"] for p in web_client.get("/api/projects").json()["projects"]}
    assert before == after


def test_project_and_dataset_data_are_tenant_scoped(web_client):
    post(web_client, "/api/auth/guest", json={})
    project = post(web_client, "/api/projects", json={"name": "Private project", "description": ""}).json()
    upload = post(web_client, "/api/datasets/import", data={"project_id": project["id"]},
                  files={"file": ("demand.csv", b"period,demand\n1,12\n2,15\n3,18\n", "text/csv")})
    assert upload.status_code == 200, upload.text
    dataset_id = upload.json()["id"]

    # A second browser session shares the same application and database, but has
    # a different principal cookie. Do not start a second ASGI lifespan here.
    from fastapi.testclient import TestClient as Client
    from orstudio.cloud_security import new_session
    second_principal = cloud_store.create_principal("GUEST", "Second visitor", guest_hours=24)
    cloud_store.ensure_default_project(second_principal["id"])
    second = Client(app, base_url="http://testserver")
    second.cookies.set("ors_session", new_session(second_principal["id"], guest=True))
    assert second.get(f"/api/datasets/{dataset_id}").status_code == 404
    assert second.get(f"/api/datasets?project_id={project['id']}").status_code == 404
    assert second.delete(f"/api/datasets/{dataset_id}", headers={"origin": "http://testserver"}).status_code == 404

    assert web_client.get(f"/api/datasets/{dataset_id}").status_code == 200


def test_batch_analysis_uses_existing_solver_and_owner_scope(web_client):
    post(web_client, "/api/auth/guest", json={})
    project = web_client.get("/api/projects").json()["projects"][0]
    response = post(web_client, "/api/jobs/batch", json={"tasks": [{
        "module_key": "forecasting", "title": "Guest forecast", "project_id": project["id"],
        "params": {"method": "moving_average", "values": [10, 12, 13, 15, 18], "window": 3, "horizon": 1}
    }]})
    assert response.status_code == 200, response.text
    assert response.json()["submitted"] == 1
    job_id = response.json()["jobs"][0]["job_id"]
    # In-process test queue completes quickly, but allow a short bounded poll.
    import time
    job = None
    for _ in range(30):
        job = web_client.get(f"/api/jobs/{job_id}").json()
        if job["status"] in {"SUCCEEDED", "FAILED"}:
            break
        time.sleep(0.05)
    assert job["status"] == "SUCCEEDED", job
    analysis = web_client.get(f"/api/analyses/{job['analysis_id']}")
    assert analysis.status_code == 200
    assert analysis.json()["output"] is not None


def test_cloud_health_and_module_catalog(web_client):
    health = web_client.get("/api/health").json()
    assert health["mode"] == "public-web"
    assert health["database"] == "ok"
    assert web_client.get("/api/modules").json()["count"] == 29


def test_cross_origin_mutation_is_rejected(web_client):
    response = post(web_client, "/api/auth/guest", json={}, headers={"origin": "https://attacker.invalid"})
    assert response.status_code == 403


def test_batch_dispatch_failure_marks_undispatched_records_failed(web_client, monkeypatch):
    post(web_client, "/api/auth/guest", json={})
    from orstudio import web_api
    calls = []

    def fake_dispatch(job_id, analysis_id, owner_id, module_key, params):
        calls.append(job_id)
        if len(calls) == 2:
            raise RuntimeError("simulated queue outage")
        web_client.app  # keep the fixture referenced while the first item is treated as dispatched

    monkeypatch.setattr(web_api, "_dispatch_job", fake_dispatch)
    tasks = [{
        "module_key": "breakeven",
        "params": {"fixed_cost": 100, "variable_cost_per_unit": 5, "selling_price_per_unit": 10}
    } for _ in range(3)]
    response = post(web_client, "/api/jobs/batch", json={"tasks": tasks})
    assert response.status_code == 503
    # The only successfully dispatched item is left for its worker; every later item is terminal.
    jobs = web_client.get("/api/jobs").json()["jobs"]
    assert len(jobs) == 3
    status_by_id = {job["id"]: job["status"] for job in jobs}
    assert status_by_id[calls[0]] == "QUEUED"
    assert all(status_by_id[job_id] == "FAILED" for job_id in status_by_id if job_id != calls[0])


def test_cloud_health_includes_worker_capacity(web_client):
    response = web_client.get("/api/health")
    assert response.status_code == 200
    health = response.json()
    assert health["status"] == "ok"
    assert health["queue_health"] == "development-pool"
    assert health["worker_count"] >= 2


def test_guest_dataset_storage_quota_is_enforced(web_client, monkeypatch):
    post(web_client, "/api/auth/guest", json={})
    from orstudio import web_api, cloud_store
    monkeypatch.setattr(web_api, "MAX_DATASET_STORAGE_GUEST", 1)
    response = post(web_client, "/api/datasets/import",
                    files={"file": ("demand.csv", b"period,demand\n1,10\n2,20\n", "text/csv")})
    assert response.status_code == 413
    assert cloud_store.count_owned("datasets", web_client.get("/api/auth/me").json()["id"]) == 0


def test_web_mounts_frontend_and_auth_assets(web_client):
    page = web_client.get("/")
    assert page.status_code == 200
    assert 'id="auth-gate"' in page.text
    assert web_client.get("/js/auth.js").status_code == 200
    assert web_client.get("/css/ors-console.css").status_code == 200


def test_cross_scheme_origin_is_rejected(web_client):
    # The test client is HTTP; HTTPS Origin with the same host is not same-origin.
    response = post(web_client, "/api/auth/guest", json={}, headers={"origin": "https://testserver"})
    assert response.status_code == 403


def test_second_principal_cannot_read_other_users_analysis_or_job(web_client):
    post(web_client, "/api/auth/guest", json={})
    project = web_client.get("/api/projects").json()["projects"][0]
    analysis = post(web_client, "/api/analyses/run", json={
        "module_key": "breakeven", "project_id": project["id"],
        "params": {"fixed_cost": 100, "variable_cost_per_unit": 5, "selling_price_per_unit": 10}
    })
    assert analysis.status_code == 200, analysis.text
    batch = post(web_client, "/api/jobs/batch", json={"tasks": [{
        "module_key": "breakeven", "project_id": project["id"],
        "params": {"fixed_cost": 100, "variable_cost_per_unit": 5, "selling_price_per_unit": 10}
    }]})
    assert batch.status_code == 200, batch.text
    analysis_id = analysis.json()["analysis_id"]
    job_id = batch.json()["jobs"][0]["job_id"]

    from fastapi.testclient import TestClient as Client
    from orstudio.cloud_security import new_session
    second_principal = cloud_store.create_principal("GUEST", "Another guest", guest_hours=24)
    cloud_store.ensure_default_project(second_principal["id"])
    second = Client(app, base_url="http://testserver")
    second.cookies.set("ors_session", new_session(second_principal["id"], guest=True))
    assert second.get(f"/api/analyses/{analysis_id}").status_code == 404
    assert second.get(f"/api/jobs/{job_id}").status_code == 404
    assert second.get(f"/api/analyses/{analysis_id}/export?format=csv").status_code == 404
