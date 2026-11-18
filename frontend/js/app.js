import { initializeCloudAuth } from './auth.js';
import { $, $$, escapeHtml, toast } from './ui.js';
import { apiGet, apiPost, downloadExport } from './api.js';
import { setModules, initModuleBrowser, renderFeaturedModules, selectModule, getSelectedModule, readParams } from './modules.js';
import { initDataCenter, refreshDatasets, setActiveProject, getDatasets } from './data-center.js';
import { initBatch, setBatchProject, addBatchItem, refreshJobs } from './batch.js';
import { initHistory, setHistoryProject, refreshHistory } from './history.js';
import { showResult, closeResult, resultAnalysisId } from './results.js';

let activeProject=null;
let currentDataset=null;
let columnMap={};
let currentResult=null;
let projectDialogReturnFocus=null;

function navigate(page){
  $$('.page').forEach(p=>p.classList.toggle('active',p.id===`page-${page}`));
  $$('.nav-link[data-page]').forEach(b=>{const active=b.dataset.page===page;b.classList.toggle('active',active);if(active)b.setAttribute('aria-current','page');else b.removeAttribute('aria-current');});
  const label=({overview:'Overview',modules:'Analysis modules',data:'Data center',batch:'Batch processing',history:'Analysis history',settings:'Settings'})[page]||'Overview';
  $('#breadcrumb-current').textContent=label;$('#sidebar').classList.remove('open');$('#mobile-menu').setAttribute('aria-expanded','false');$('#main-content').focus({preventScroll:true});
  if(page==='data')refreshDatasets();if(page==='batch')refreshJobs();if(page==='history')refreshHistory();
}
async function initProject(){
  const data=await apiGet('/api/projects');
  activeProject=data.projects?.[0]||null;
  if(activeProject){$('#workspace-name').textContent=activeProject.name;setActiveProject(activeProject.id);setBatchProject(activeProject.id);setHistoryProject(activeProject.id);}
}
async function refreshOverview(){
  await Promise.all([refreshDatasets(),refreshHistory(),refreshJobs()]);
  $('#metric-modules').textContent='29';
}
function activeBindingData(){
  const datasetId=$('#binding-dataset').value;
  return {dataset_id:datasetId||null,column_map:{...columnMap}};
}
async function changeBindingDataset(id){
  currentDataset=null;columnMap={};$('#binding-summary').textContent='No dataset mapping applied.';
  if(!id){$('#binding-column').innerHTML='<option value="">Dataset column</option>';return;}
  try{
    currentDataset=await apiGet(`/api/datasets/${id}`);
    const numeric=currentDataset.columns.filter(c=>currentDataset.preview.some(row=>row[c]!==null&&row[c]!==''&&Number.isFinite(Number(row[c]))));
    $('#binding-column').innerHTML=`<option value="">Dataset column</option>${numeric.map(c=>`<option value="${escapeHtml(c)}">${escapeHtml(c)}</option>`).join('')}`;
    if(!numeric.length)$('#binding-summary').textContent='No numeric columns were detected in the first preview rows.';
  }catch(e){toast(e.message,'error');}
}
async function applyColumnMapping(){
  const target=$('#binding-target').value,column=$('#binding-column').value;
  if(!currentDataset||!target||!column){toast('Choose a dataset, a parameter, and a numeric column.','error');return;}
  columnMap[target]=column;
  $('#binding-summary').textContent=`Mapped parameter “${target}” to column “${column}” in ${currentDataset.filename}.`;
  toast('Dataset mapping applied.');
}
function currentTask(){
  const module=getSelectedModule();if(!module)throw new Error('Select an analysis module first.');
  const params=readParams();const binding=activeBindingData();
  return {module_key:module.key,title:module.name,params,project_id:activeProject?.id,dataset_id:binding.dataset_id,column_map:binding.column_map};
}

async function compareForecastMethods(){
  try{
    const task=currentTask();
    if(task.module_key!=='forecasting')throw new Error('Select the Forecasting module first.');
    let values=task.params.values || task.params.data;
    if(task.dataset_id && task.column_map.values){
      const column=await apiGet(`/api/datasets/${task.dataset_id}/columns/${encodeURIComponent(task.column_map.values)}`);
      values=column.values;
    }
    const params=task.params;
    const response=await apiPost('/api/forecast/compare',{
      values:values,
      methods:['naive','moving_average','weighted_moving_average','ses','linear_trend'],
      holdout:Math.min(Number(params.holdout||3),Math.max(1,values.length-2)),
      window:Number(params.window||3),alpha:Number(params.alpha||.3),weights:params.weights||[1,2,3]
    });
    currentResult={status:'COMPLETED',title:'Forecast method comparison',output:response};
    showResult(currentResult,'Forecast method comparison');
    toast(response.best_method?`Best forecasting method: ${response.best_method}`:'Comparison completed.');
  }catch(err){toast(err.message,'error');}
}

function openProjectDialog(){
  const modal=$('#project-modal');
  if(modal.hidden)projectDialogReturnFocus=document.activeElement;
  modal.hidden=false;
  $('#project-name').value='';
  $('#project-name').focus({preventScroll:true});
}
function closeProjectDialog(){
  const modal=$('#project-modal');
  if(modal.hidden)return;
  modal.hidden=true;
  if(projectDialogReturnFocus?.isConnected)projectDialogReturnFocus.focus({preventScroll:true});
  projectDialogReturnFocus=null;
}
function handleProjectDialogKeys(event){
  const modal=$('#project-modal');
  if(modal.hidden)return;
  if(event.key==='Escape'){event.preventDefault();closeProjectDialog();return;}
  if(event.key!=='Tab')return;
  const items=[...modal.querySelectorAll('input:not([disabled]),button:not([disabled])')].filter(node=>!node.closest('[hidden]'));
  if(!items.length){event.preventDefault();return;}
  const first=items[0],last=items[items.length-1];
  if(event.shiftKey&&(document.activeElement===first||!modal.contains(document.activeElement))){event.preventDefault();last.focus();}
  else if(!event.shiftKey&&(document.activeElement===last||!modal.contains(document.activeElement))){event.preventDefault();first.focus();}
}
async function createProject(name){
  if(!name?.trim()){$('#project-name').focus();return;}
  const submit=$('#create-project-button');
  submit.disabled=true;submit.textContent='Creating…';
  try{
    const project=await apiPost('/api/projects',{name:name.trim(),description:''});
    activeProject=project;$('#workspace-name').textContent=project.name;
    setActiveProject(project.id);setBatchProject(project.id);setHistoryProject(project.id);
    closeProjectDialog();await refreshOverview();toast(`Project “${project.name}” created.`);
  }catch(err){toast(err.message,'error');}
  finally{submit.disabled=false;submit.textContent='Create project';}
}

async function runAnalysis(){
  try{
    const task=currentTask();$('#run-analysis').disabled=true;$('#run-analysis').textContent='Calculating…';
    const result=await apiPost('/api/analyses/run',task);currentResult=result;
    showResult(result,getSelectedModule()?.name);await Promise.all([refreshOverview(),refreshHistory()]);toast('Analysis completed.');
  }catch(err){toast(err.message,'error');}
  finally{$('#run-analysis').disabled=false;$('#run-analysis').innerHTML='Run analysis <span class="button-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg></span>';}
}
function addToBatch(){try{addBatchItem(currentTask());}catch(err){toast(err.message,'error');}}
async function openAnalysis(id){
  try{const analysis=await apiGet(`/api/analyses/${id}`);currentResult=analysis;showResult(analysis,analysis.title);}catch(e){toast(e.message,'error');}
}
function attachEvents(){
  $$('[data-page]').forEach(btn=>btn.addEventListener('click',()=>navigate(btn.dataset.page)));
  $$('[data-go]').forEach(btn=>btn.addEventListener('click',()=>navigate(btn.dataset.go)));
  $('#mobile-menu').addEventListener('click',()=>{const opened=$('#sidebar').classList.toggle('open');$('#mobile-menu').setAttribute('aria-expanded',String(opened));$('#mobile-menu').setAttribute('aria-label',opened?'Close navigation':'Open navigation');});
  $('#quick-import').addEventListener('click',()=>navigate('data'));$('#welcome-upload').addEventListener('click',()=>navigate('data'));
  $('#quick-analysis').addEventListener('click',()=>{navigate('modules');if(getSelectedModule())return;selectModule('forecasting');});
  $('#welcome-module').addEventListener('click',()=>navigate('modules'));
  $('#binding-dataset').addEventListener('change',e=>changeBindingDataset(e.target.value));
  $('#apply-binding').addEventListener('click',applyColumnMapping);
  $('#run-analysis').addEventListener('click',runAnalysis);$('#add-to-batch').addEventListener('click',addToBatch);
  $('#compare-forecast').addEventListener('click',compareForecastMethods);
  $('#workspace-switcher').addEventListener('click',openProjectDialog);
  $('#project-form').addEventListener('submit',event=>{event.preventDefault();createProject($('#project-name').value);});
  $('#cancel-project').addEventListener('click',closeProjectDialog);
  $('#project-modal').addEventListener('click',event=>{if(event.target===$('#project-modal'))closeProjectDialog();});
  $('#project-modal').addEventListener('keydown',handleProjectDialogKeys);
  $('#result-done').addEventListener('click',closeResult);$('#close-result').addEventListener('click',closeResult);
  $('#result-modal').addEventListener('click',e=>{if(e.target===$('#result-modal'))closeResult();});
  $$('[data-export]').forEach(btn=>btn.addEventListener('click',async()=>{const id=resultAnalysisId();if(!id){toast('No saved analysis is available for export.','error');return;}try{await downloadExport(id,btn.dataset.export);toast(`${btn.dataset.export.toUpperCase()} export ready.`);}catch(e){toast(e.message,'error');}}));
  document.addEventListener('ors:datasets-updated',()=>{if($('#binding-dataset').value)changeBindingDataset($('#binding-dataset').value);});
  document.addEventListener('ors:open-analysis',e=>openAnalysis(e.detail.id));
  document.addEventListener('ors:refresh-all',()=>refreshOverview());
  $('#metric-modules').textContent='29';
}

async function bootstrap(){
  const cloudSession = await initializeCloudAuth();
  if (cloudSession === "waiting") return;
  attachEvents();
  try{
    const health=await apiGet('/api/health');$('#worker-setting').textContent=health.worker_count;$('#engine-status').innerHTML=health.mode==='public-web'?'<span class="status-led"></span> Cloud engine connected':'<span class="status-led"></span> Local engine connected';
    const catalog=await apiGet('/api/modules');setModules(catalog.modules);$('#module-count').textContent=catalog.count;
    initModuleBrowser();renderFeaturedModules();initDataCenter();initBatch();initHistory();
    await initProject();await refreshOverview();selectModule('forecasting');
    $('#storage-path').textContent=health.mode==='public-web'?'Stored in your private cloud workspace.':'Stored locally in the current operating system user profile.';
  }catch(err){$('#engine-status').innerHTML='<span class="status-led status-led-error"></span> Engine connection failed';toast(`Could not connect to the ORS engine: ${err.message}`,'error');}
}
bootstrap();
