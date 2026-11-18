const BASE = '';

async function parseResponse(response) {
  const type = response.headers.get('content-type') || '';
  const body = type.includes('application/json') ? await response.json() : await response.text();
  if (!response.ok) {
    const message = body?.detail || body?.message || body || `Request failed (${response.status})`;
    throw new Error(typeof message === 'string' ? message : JSON.stringify(message));
  }
  return body;
}

export async function apiGet(path) {
  return parseResponse(await fetch(`${BASE}${path}`));
}
export async function apiPost(path, payload) {
  return parseResponse(await fetch(`${BASE}${path}`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
  }));
}
export async function apiDelete(path) {
  return parseResponse(await fetch(`${BASE}${path}`, { method: 'DELETE' }));
}
export async function importDataset(file, projectId, sheetName) {
  const form = new FormData();
  form.append('file', file);
  if (projectId) form.append('project_id', projectId);
  if (sheetName) form.append('sheet_name', sheetName);
  return parseResponse(await fetch('/api/datasets/import', { method: 'POST', body: form }));
}
export async function inspectWorkbook(file) {
  const form = new FormData(); form.append('file', file);
  return parseResponse(await fetch('/api/datasets/inspect', { method: 'POST', body: form }));
}
export async function downloadExport(analysisId, format) {
  const response = await fetch(`/api/analyses/${analysisId}/export?format=${format}`);
  if (!response.ok) return parseResponse(response);
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a'); a.href = url; a.download = `ors-analysis.${format}`; a.click();
  URL.revokeObjectURL(url);
}
