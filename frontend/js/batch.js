import { $, escapeHtml, statusClass, toast, iconSvg } from './ui.js';
import { apiGet, apiPost } from './api.js';

let items=[];
let activeProjectId=null;
let pollHandle=null;
export function setBatchProject(id){activeProjectId=id;}
function renderBatch(){
  $('#batch-count').textContent=`${items.length} ${items.length===1?'task':'tasks'}`;
  $('#batch-dot').classList.toggle('visible',items.length>0);
  $('#run-batch').disabled=!items.length;
  $('#batch-items').innerHTML=items.length?items.map((item,index)=>`<div class="batch-item"><span class="batch-index">${index+1}</span><div class="batch-copy"><strong>${escapeHtml(item.title)}</strong><small>${escapeHtml(item.module_key)} · ${item.dataset_id?'dataset linked':'manual parameters'}</small></div><button type="button" class="icon-button" data-remove-task="${index}" aria-label="Remove ${escapeHtml(item.title)} from batch" title="Remove task">${iconSvg('close',15)}</button></div>`).join(''):`<div class="empty-state compact"><div class="empty-icon">${iconSvg('branch',17)}</div><strong>Your batch is empty</strong><span>Configure a module and select “Add to batch”.</span><button class="btn btn-secondary btn-small" data-go="modules">Explore modules</button></div>`;
  document.querySelectorAll('[data-remove-task]').forEach(b=>b.addEventListener('click',()=>{items.splice(Number(b.dataset.removeTask),1);renderBatch();}));
  document.querySelectorAll('#batch-items [data-go="modules"]').forEach(b=>b.addEventListener('click',()=>document.querySelector('[data-page="modules"]').click()));
}
export function addBatchItem(item){items.push(item);renderBatch();toast(`${item.title} added to batch.`);}
export function initBatch(){
  renderBatch();
  $('#clear-batch').addEventListener('click',()=>{items=[];renderBatch();});
  $('#run-batch').addEventListener('click',async()=>{
    if(!items.length)return;
    $('#run-batch').disabled=true;$('#run-batch').textContent='Submitting…';
    try{
      const result=await apiPost('/api/jobs/batch',{tasks:items.map(x=>({...x,project_id:x.project_id||activeProjectId}))});
      toast(`${result.submitted} analysis job(s) submitted.`);items=[];renderBatch();await refreshJobs();
      if(pollHandle)clearInterval(pollHandle);
      pollHandle=setInterval(async()=>{try{const jobs=await refreshJobs();if(jobs.length&&jobs.every(j=>['SUCCEEDED','FAILED','CANCELLED'].includes(j.status))){clearInterval(pollHandle);pollHandle=null;toast('Batch processing completed.');document.dispatchEvent(new Event('ors:refresh-all'));}}catch(e){console.error(e)}},1800);
    }catch(err){toast(err.message,'error');}
    finally{$('#run-batch').disabled=!items.length;$('#run-batch').textContent='Run all analyses';}
  });
  $('#refresh-jobs').addEventListener('click',()=>refreshJobs());
}
export async function refreshJobs(){
  const data=await apiGet(`/api/jobs${activeProjectId?`?project_id=${activeProjectId}`:''}`);const jobs=data.jobs||[];
  $('#metric-active').textContent=jobs.filter(j=>['QUEUED','RUNNING'].includes(j.status)).length;
  $('#job-list').innerHTML=jobs.length?jobs.map(j=>`<div class="job-row"><div class="batch-index">${j.status==='SUCCEEDED'?iconSvg('check',15):j.status==='FAILED'?iconSvg('alert',15):iconSvg('clock',15)}</div><div class="job-copy"><strong>${escapeHtml(j.title)}</strong><small>${escapeHtml(j.module_key)} · ${new Date(j.created_at).toLocaleString()}</small>${j.status==='RUNNING'?`<div class="job-progress"><span style="width:${j.progress||10}%"></span></div>`:''}${j.error?`<small class="error-text">${escapeHtml(j.error)}</small>`:''}</div><span class="status-tag ${statusClass(j.status)}">${escapeHtml(j.status)}</span>${j.status==='SUCCEEDED'?`<button type="button" class="btn btn-secondary btn-small" data-open-analysis="${j.analysis_id}">View result</button>`:''}</div>`).join(''):`<div class="empty-state compact"><div class="empty-icon">${iconSvg('clock',17)}</div><strong>No jobs submitted</strong><span>Submitted analysis jobs will show here.</span></div>`;
  document.querySelectorAll('#job-list [data-open-analysis]').forEach(b=>b.addEventListener('click',()=>document.dispatchEvent(new CustomEvent('ors:open-analysis',{detail:{id:b.dataset.openAnalysis}}))));
  return jobs;
}
