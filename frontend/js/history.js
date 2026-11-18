import { $, $$, escapeHtml, statusClass, iconSvg } from './ui.js';
import { apiGet } from './api.js';

let activeProjectId=null;
export function setHistoryProject(id){activeProjectId=id;}
export async function refreshHistory(){
  const data=await apiGet(`/api/analyses?limit=300${activeProjectId?`&project_id=${activeProjectId}`:''}`);
  renderHistory(data.analyses||[]);
  const completed=(data.analyses||[]).filter(a=>a.status==='SUCCEEDED').length;
  $('#metric-completed').textContent=completed;
  $('#recent-activity').innerHTML=(data.analyses||[]).slice(0,4).length?(data.analyses||[]).slice(0,4).map(a=>`<div class="job-row"><div class="batch-index">${a.status==='SUCCEEDED'?iconSvg('check',15):iconSvg('alert',15)}</div><div class="job-copy"><strong>${escapeHtml(a.title)}</strong><small>${escapeHtml(a.module_key)} · ${new Date(a.created_at).toLocaleString()}</small></div><span class="status-tag ${statusClass(a.status)}">${escapeHtml(a.status)}</span></div>`).join(''):`<div class="empty-state compact"><div class="empty-icon">${iconSvg('clock',17)}</div><strong>No activity yet</strong><span>Your analysis history will appear here.</span></div>`;
  return data.analyses||[];
}
function renderHistory(items){
  const q=$('#history-search').value.toLowerCase().trim();const status=$('#history-status').value;
  const shown=items.filter(a=>(!status||a.status===status)&&(`${a.title} ${a.module_key} ${a.id}`).toLowerCase().includes(q));
  $('#history-table').innerHTML=shown.length?`<table class="data-table"><thead><tr><th>Analysis</th><th>Module</th><th>Date</th><th>Status</th><th>Actions</th></tr></thead><tbody>${shown.map(a=>`<tr><td><strong>${escapeHtml(a.title)}</strong><br><small>${escapeHtml(a.id.slice(0,8))}</small></td><td>${escapeHtml(a.module_key)}</td><td>${new Date(a.created_at).toLocaleString()}</td><td><span class="status-tag ${statusClass(a.status)}">${escapeHtml(a.status)}</span></td><td>${a.status==='SUCCEEDED'?`<button type="button" class="btn btn-secondary btn-small" data-history-open="${a.id}">View result</button>`:'—'}</td></tr>`).join('')}</tbody></table>`:`<div class="empty-state compact"><strong>No matching analyses</strong><span>Change the search or status filter.</span></div>`;
  $$('#history-table [data-history-open]').forEach(btn=>btn.addEventListener('click',()=>document.dispatchEvent(new CustomEvent('ors:open-analysis',{detail:{id:btn.dataset.historyOpen}}))));
}
export function initHistory(){
  $('#refresh-history').addEventListener('click',refreshHistory);
  $('#history-search').addEventListener('input',()=>refreshHistory());
  $('#history-status').addEventListener('change',()=>refreshHistory());
}
