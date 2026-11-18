import { $, escapeHtml, toast, iconSvg } from './ui.js';
import { apiGet, apiDelete, importDataset, inspectWorkbook } from './api.js';

let datasets=[];
let selectedFile=null;
let selectedSheet='';
let activeProjectId=null;
export function setActiveProject(id){activeProjectId=id;}
export function getDatasets(){return datasets;}
export async function refreshDatasets(){
  const data=await apiGet(`/api/datasets${activeProjectId?`?project_id=${activeProjectId}`:''}`);datasets=data.datasets||[];
  $('#dataset-count').textContent=`${datasets.length} ${datasets.length===1?'file':'files'}`;
  $('#metric-datasets').textContent=datasets.length;
  $('#binding-dataset').innerHTML=`<option value="">No dataset selected</option>${datasets.map(d=>`<option value="${d.id}">${escapeHtml(d.filename)} (${d.row_count})</option>`).join('')}`;
  $('#dataset-list').innerHTML=datasets.length?datasets.map(d=>`<div class="dataset-row"><div class="file-icon">${d.filename.toLowerCase().endsWith('.xlsx')?'XLS':'CSV'}</div><div class="dataset-info"><strong>${escapeHtml(d.filename)}</strong><small>${d.row_count.toLocaleString()} rows · ${d.columns.length} columns · ${escapeHtml(d.sheet_name||'CSV')}</small></div><div class="dataset-actions"><button class="btn btn-secondary btn-small" data-preview="${d.id}">Preview</button><button type="button" class="icon-button" data-delete="${d.id}" aria-label="Delete ${escapeHtml(d.filename)}" title="Delete dataset">${iconSvg('close',15)}</button></div></div>`).join(''):`<div class="empty-state compact"><div class="empty-icon">${iconSvg('file',17)}</div><strong>No datasets yet</strong><span>Upload a CSV or Excel file to get started.</span></div>`;
  document.querySelectorAll('[data-preview]').forEach(b=>b.addEventListener('click',()=>previewDataset(b.dataset.preview)));
  document.querySelectorAll('[data-delete]').forEach(b=>b.addEventListener('click',()=>removeDataset(b.dataset.delete)));
  document.dispatchEvent(new CustomEvent('ors:datasets-updated',{detail:{datasets}}));
}
export async function previewDataset(id){
  const ds=await apiGet(`/api/datasets/${id}`);
  $('#dataset-preview-panel').hidden=false;$('#preview-title').textContent=ds.filename;$('#preview-meta').textContent=`${ds.row_count} rows · ${ds.columns.length} columns`;
  const rows=ds.preview||[];
  $('#dataset-preview').innerHTML=`<table class="data-table"><thead><tr>${ds.columns.map(c=>`<th>${escapeHtml(c)}</th>`).join('')}</tr></thead><tbody>${rows.map(r=>`<tr>${ds.columns.map(c=>`<td>${escapeHtml(r[c]??'—')}</td>`).join('')}</tr>`).join('')}</tbody></table>`;
  $('#dataset-warnings').innerHTML='';$('#dataset-preview-panel').scrollIntoView({behavior:'smooth',block:'nearest'});
}
async function removeDataset(id){
  if(!confirm('Delete this saved dataset? Analyses already completed will remain in history.'))return;
  await apiDelete(`/api/datasets/${id}`);toast('Dataset deleted.');await refreshDatasets();
}
function setSelectedFile(file){
  selectedFile=file;selectedSheet='';$('#selected-file').textContent=file?`${file.name} · ${(file.size/1024/1024).toFixed(2)} MB`:'';
  $('#upload-button').disabled=!file;$('#sheet-row').hidden=true;$('#import-message').textContent='';
  if(file&&file.name.toLowerCase().endsWith('.xlsx')){
    inspectWorkbook(file).then(info=>{const sheets=info.sheets||[];$('#sheet-select').innerHTML=sheets.map(s=>`<option value="${escapeHtml(s)}">${escapeHtml(s)}</option>`).join('');selectedSheet=sheets[0]||'';$('#sheet-row').hidden=sheets.length<=1;}).catch(e=>{ $('#import-message').textContent=e.message;$('#import-message').className='import-message error'; });
  }
}
export function initDataCenter(){
  const input=$('#upload-file'),drop=$('#dropzone');
  input.addEventListener('change',()=>setSelectedFile(input.files[0]));
  ['dragenter','dragover'].forEach(type=>drop.addEventListener(type,e=>{e.preventDefault();drop.classList.add('dragover');}));
  ['dragleave','drop'].forEach(type=>drop.addEventListener(type,e=>{e.preventDefault();drop.classList.remove('dragover');}));
  drop.addEventListener('drop',e=>{const f=e.dataTransfer.files[0];if(f){input.files=e.dataTransfer.files;setSelectedFile(f);}});
  $('#sheet-select').addEventListener('change',e=>selectedSheet=e.target.value);
  $('#upload-button').addEventListener('click',async()=>{
    if(!selectedFile)return;
    $('#upload-button').disabled=true;$('#upload-button').textContent='Importing…';$('#import-message').textContent='Reading and validating the file…';$('#import-message').className='import-message';
    try{
      const result=await importDataset(selectedFile,activeProjectId,selectedSheet);
      $('#import-message').textContent=`Imported ${result.row_count.toLocaleString()} rows and ${result.columns.length} columns.`;$('#import-message').className='import-message success';
      $('#dataset-preview-panel').hidden=false;$('#preview-title').textContent=result.filename;$('#preview-meta').textContent=`${result.row_count} rows · ${result.columns.length} columns · ${result.sheet_name||'CSV'}`;
      $('#dataset-preview').innerHTML=`<table class="data-table"><thead><tr>${result.columns.map(c=>`<th>${escapeHtml(c)}</th>`).join('')}</tr></thead><tbody>${(result.preview||[]).map(r=>`<tr>${result.columns.map(c=>`<td>${escapeHtml(r[c]??'—')}</td>`).join('')}</tr>`).join('')}</tbody></table>`;
      $('#dataset-warnings').innerHTML=(result.warnings||[]).map(w=>`<span class="warning-item">${escapeHtml(w.column)}: ${escapeHtml(w.count)} ${escapeHtml(w.type.replaceAll('_',' '))}</span>`).join('');
      toast('Dataset imported successfully.');await refreshDatasets();input.value='';selectedFile=null;$('#selected-file').textContent='';$('#upload-button').textContent='Import dataset';
    }catch(err){$('#import-message').textContent=err.message;$('#import-message').className='import-message error';toast(err.message,'error');}
    finally{$('#upload-button').disabled=!selectedFile;$('#upload-button').textContent='Import dataset';}
  });
  $('#close-preview').addEventListener('click',()=>$('#dataset-preview-panel').hidden=true);
}
