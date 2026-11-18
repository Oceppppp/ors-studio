import os
import time
from fastapi.testclient import TestClient


def test_api_import_run_batch_and_exports(tmp_path, monkeypatch):
    monkeypatch.setenv("ORS_DATA_DIR", str(tmp_path))
    from orstudio.api import app
    with TestClient(app) as client:
        health = client.get('/api/health').json()
        assert health['status'] == 'ok'
        assert health['version'] == '0.4.0'
        assert client.get('/api/modules').json()['count'] == 29

        imported = client.post('/api/datasets/import', files={'file': ('demand.csv', b'Period,Demand\nJan,10\nFeb,12\nMar,14\nApr,16\n', 'text/csv')})
        assert imported.status_code == 200, imported.text
        dataset_id = imported.json()['id']

        analysis = client.post('/api/analyses/run', json={
            'module_key': 'forecasting',
            'params': {'method':'moving_average','values':[1,2,3,4], 'window':2, 'horizon':1},
            'dataset_id': dataset_id,
            'column_map': {'values':'Demand'}
        })
        assert analysis.status_code == 200, analysis.text
        assert analysis.json()['output']['forecast'] == [15.0]
        analysis_id = analysis.json()['analysis_id']
        saved_analysis = client.get(f'/api/analyses/{analysis_id}').json()
        assert saved_analysis['input']['_ors_source']['dataset_id'] == dataset_id
        assert saved_analysis['input']['_ors_source']['column_map'] == {'values': 'Demand'}

        for fmt in ['xlsx','csv','pdf']:
            response = client.get(f'/api/analyses/{analysis_id}/export?format={fmt}')
            assert response.status_code == 200, response.text[:500]
            assert len(response.content) > 100

        batch = client.post('/api/jobs/batch', json={'tasks':[
            {'module_key':'breakeven','params':{'fixed_cost':100,'variable_cost_per_unit':5,'selling_price_per_unit':10}},
            {'module_key':'inventory','params':{'model':'eoq','annual_demand':1000,'ordering_cost':20,'holding_cost':2}}
        ]})
        assert batch.status_code == 200, batch.text
        job_ids = [x['job_id'] for x in batch.json()['jobs']]
        for _ in range(40):
            statuses=[client.get(f'/api/jobs/{jid}').json()['status'] for jid in job_ids]
            if all(x in {'SUCCEEDED','FAILED','CANCELLED'} for x in statuses): break
            time.sleep(.05)
        assert statuses == ['SUCCEEDED','SUCCEEDED']

        compare = client.post('/api/forecast/compare',json={'values':[10,12,14,16,18,20,22], 'holdout':2, 'window':2})
        assert compare.status_code == 200, compare.text
        assert compare.json()['best_method'] is not None


def test_api_serves_frontend_and_inspects_workbook(tmp_path, monkeypatch):
    from io import BytesIO
    from openpyxl import Workbook
    monkeypatch.setenv("ORS_DATA_DIR", str(tmp_path))
    from orstudio.api import app
    wb=Workbook();ws=wb.active;ws.title='Plan';ws.append(['Period','Demand']);ws.append(['P1',10]);wb.create_sheet('Costs')
    buf=BytesIO();wb.save(buf)
    with TestClient(app) as client:
        page=client.get('/')
        assert page.status_code==200 and 'Operations Research Studio' in page.text
        js=client.get('/js/app.js')
        assert js.status_code==200 and 'bootstrap' in js.text
        inspected=client.post('/api/datasets/inspect',files={'file':('plan.xlsx',buf.getvalue(),'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')})
        assert inspected.status_code==200, inspected.text
        assert inspected.json()['sheets']==['Plan','Costs']


def test_batch_rejects_invalid_mapping_without_creating_partial_jobs(tmp_path, monkeypatch):
    monkeypatch.setenv("ORS_DATA_DIR", str(tmp_path))
    from orstudio.api import app
    with TestClient(app) as client:
        imported = client.post('/api/datasets/import', files={
            'file': ('demand.csv', b'Period,Demand\nJan,10\nFeb,12\n', 'text/csv')
        })
        assert imported.status_code == 200
        dataset_id = imported.json()['id']
        before = client.get('/api/jobs').json()['jobs']
        response = client.post('/api/jobs/batch', json={'tasks': [
            {'module_key': 'breakeven', 'params': {'fixed_cost':100,'variable_cost_per_unit':5,'selling_price_per_unit':10}},
            {'module_key': 'forecasting', 'params': {'method':'moving_average','values':[],'window':2,'horizon':1},
             'dataset_id': dataset_id, 'column_map': {'values':'MissingColumn'}}
        ]})
        assert response.status_code == 400
        after = client.get('/api/jobs').json()['jobs']
        assert len(after) == len(before)


def test_api_lifespan_can_restart_worker_pool(tmp_path, monkeypatch):
    monkeypatch.setenv("ORS_DATA_DIR", str(tmp_path))
    from orstudio.api import app
    for _ in range(2):
        with TestClient(app) as client:
            response=client.post('/api/jobs/batch',json={'tasks':[
                {'module_key':'breakeven','params':{'fixed_cost':100,'variable_cost_per_unit':5,'selling_price_per_unit':10}}
            ]})
            assert response.status_code==200, response.text
            job_id=response.json()['jobs'][0]['job_id']
            for _attempt in range(40):
                job=client.get(f'/api/jobs/{job_id}').json()
                if job['status'] in {'SUCCEEDED','FAILED','CANCELLED'}: break
                time.sleep(.05)
            assert job['status']=='SUCCEEDED'


def test_local_api_rejects_cross_origin_mutations(tmp_path, monkeypatch):
    monkeypatch.setenv("ORS_DATA_DIR", str(tmp_path))
    from orstudio.api import app

    with TestClient(app, base_url="http://127.0.0.1") as client:
        blocked = client.post(
            "/api/projects",
            json={"name": "External project", "description": ""},
            headers={"Origin": "https://example.com"},
        )
        assert blocked.status_code == 403
        assert "Cross-origin" in blocked.json()["detail"]

        allowed = client.post(
            "/api/projects",
            json={"name": "Local project", "description": ""},
            headers={"Origin": "http://127.0.0.1"},
        )
        assert allowed.status_code == 200
