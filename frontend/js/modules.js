import { $, $$, escapeHtml, pretty, iconSvg } from './ui.js';

const ICONS = {
  aggregate_planning:'optimize', assembly_line_balancing:'grid', assignment:'people', breakeven:'chart', capital_investment:'chart', decision_analysis:'branch', forecasting:'chart', game_theory:'network', goal_programming:'optimize', integer_programming:'optimize', inventory:'inventory', job_shop_scheduling:'grid', layout:'grid', learning_curves:'chart', linear_programming:'optimize', location:'network', lot_sizing:'inventory', markov_analysis:'network', mrp:'inventory', networks:'network', productivity:'chart', project_management:'branch', quality_control:'chart', reliability:'network', simulation:'branch', statistics:'chart', transportation:'truck', waiting_lines:'people', work_measurement:'chart'
};
let modules = [];
let selected = null;
let activeCategory = 'All';

export function setModules(items) { modules = items; }
export function getModules() { return modules; }
export function getSelectedModule() { return selected; }
export function getModuleIcon(key) { return iconSvg(ICONS[key] || 'grid', 17); }

function categories() { return ['All', ...new Set(modules.map(m => m.category))]; }
function renderCategories() {
  $('#category-tabs').innerHTML = categories().map(c => `<button type="button" class="category-tab ${c===activeCategory?'active':''}" data-category="${escapeHtml(c)}" aria-pressed="${c===activeCategory}">${escapeHtml(c)}</button>`).join('');
  $$('#category-tabs [data-category]').forEach(btn => btn.addEventListener('click', () => { activeCategory=btn.dataset.category; renderCategories(); renderList(); }));
}
function renderList() {
  const q=$('#module-search').value.trim().toLowerCase();
  const shown=modules.filter(m => (activeCategory==='All'||m.category===activeCategory) && `${m.name} ${m.description} ${m.key}`.toLowerCase().includes(q));
  $('#module-list').innerHTML=shown.map(m=>`<button type="button" class="module-item ${selected?.key===m.key?'active':''}" data-key="${m.key}" aria-pressed="${selected?.key===m.key}"><span class="module-icon">${getModuleIcon(m.key)}</span><span class="module-copy"><strong>${escapeHtml(m.name)}</strong><small>${escapeHtml(m.category)}</small></span><span class="module-chevron" aria-hidden="true">${iconSvg('chevron', 15)}</span></button>`).join('') || `<div class="empty-state compact"><strong>No modules found</strong><span>Try another search term.</span></div>`;
  $$('#module-list [data-key]').forEach(btn=>btn.addEventListener('click',()=>selectModule(btn.dataset.key)));
}
function renderParameterBindings() {
  const params=selected.default_params || {};
  const arrays=Object.entries(params).filter(([,v])=>Array.isArray(v) && v.every(x=>typeof x==='number'||x===null)).map(([k])=>k);
  $('#binding-target').innerHTML=`<option value="">Parameter to replace</option>${arrays.map(k=>`<option value="${escapeHtml(k)}">${escapeHtml(k)}</option>`).join('')}`;
  $('#binding-summary').textContent='No dataset mapping applied.';
}
export function selectModule(key) {
  selected=modules.find(m=>m.key===key) || modules[0];
  if(!selected)return;
  $('#module-config-empty').hidden=true;
  $('#module-config-content').hidden=false;
  $('#selected-module-icon').innerHTML=getModuleIcon(selected.key);
  $('#selected-module-category').textContent=selected.category;
  $('#selected-module-name').textContent=selected.name;
  $('#selected-module-description').textContent=selected.description;
  $('#selected-module-readiness').textContent=`Scope: ${selected.readiness}. Review the assumptions and limitations included with every result.`;
  $('#forecast-tools').hidden = selected.key !== 'forecasting';
  $('#params-editor').value=pretty(selected.default_params);
  renderParameterBindings();renderList();
}
export function readParams() {
  try { const obj=JSON.parse($('#params-editor').value); if(!obj||Array.isArray(obj)||typeof obj!=='object')throw new Error('Parameters must be a JSON object.'); return obj; }
  catch(err){ throw new Error(`Invalid parameter JSON: ${err.message}`); }
}
export function initModuleBrowser() {
  renderCategories();renderList();
  $('#module-search').addEventListener('input',renderList);
  $('#reset-params').addEventListener('click',()=>{if(selected)$('#params-editor').value=pretty(selected.default_params);renderParameterBindings();});
}
export function renderFeaturedModules() {
  const picks=['forecasting','linear_programming','inventory','transportation'];
  $('#featured-modules').innerHTML=picks.map(key=>{const m=modules.find(x=>x.key===key);return `<button type="button" class="featured-card" data-feature="${key}"><span class="featured-icon">${getModuleIcon(key)}</span><span><strong>${escapeHtml(m.name)}</strong><small>${escapeHtml(m.description.slice(0,70))}…</small></span></button>`}).join('');
  $$('#featured-modules [data-feature]').forEach(btn=>btn.addEventListener('click',()=>{selectModule(btn.dataset.feature);document.querySelector('[data-page="modules"]').click();}));
}
