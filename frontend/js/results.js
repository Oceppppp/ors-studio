import { $, escapeHtml, formatValue, flattenScalars } from './ui.js';

let currentAnalysisId = null;
let returnFocusTo = null;

function modalFocusables() {
  return [...$('#result-modal').querySelectorAll(
    'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
  )].filter(node => !node.hidden && !node.closest('[hidden]') && node.getAttribute('aria-hidden') !== 'true');
}

function handleModalKeys(event) {
  const modal = $('#result-modal');
  if (!modal || modal.hidden) return;
  if (event.key === 'Escape') {
    event.preventDefault();
    closeResult();
    return;
  }
  if (event.key !== 'Tab') return;
  const items = modalFocusables();
  if (!items.length) {
    event.preventDefault();
    return;
  }
  const first = items[0], last = items[items.length - 1];
  if (event.shiftKey && (document.activeElement === first || !modal.contains(document.activeElement))) {
    event.preventDefault();
    last.focus();
  } else if (!event.shiftKey && (document.activeElement === last || !modal.contains(document.activeElement))) {
    event.preventDefault();
    first.focus();
  }
}

document.addEventListener('keydown', handleModalKeys);

function renderTable(rows, maxRows = 50) {
  if (!Array.isArray(rows) || !rows.length) return '';
  const objects = rows.map((r, i) => (r && typeof r === 'object' && !Array.isArray(r)) ? r : { value: r });
  const keys = [...new Set(objects.flatMap(r => Object.keys(r)))];
  return `<div class="table-wrap result-table"><table class="data-table"><thead><tr>${keys.map(k => `<th>${escapeHtml(k)}</th>`).join('')}</tr></thead><tbody>${objects.slice(0,maxRows).map(row => `<tr>${keys.map(k => `<td>${escapeHtml(formatValue(row[k]))}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
}
const CHART_COLORS = ['#2463eb', '#16865b', '#bb750b', '#8057c8', '#d05252'];
const X_AXIS_KEYS = new Set(['period', 'index', 'iteration', 'step', 'station', 'operation', 'sequence']);

function chartSeriesFromRows(rows) {
  const fields = new Map();
  rows.forEach((row, index) => {
    if (!row || typeof row !== 'object' || Array.isArray(row)) return;
    for (const [key, value] of Object.entries(row)) {
      if (X_AXIS_KEYS.has(key.toLowerCase())) continue;
      if (typeof value === 'number' && Number.isFinite(value)) {
        if (!fields.has(key)) fields.set(key, Array(rows.length).fill(null));
        fields.get(key)[index] = value;
      } else if (value && typeof value === 'object' && !Array.isArray(value)) {
        for (const [nestedKey, nestedValue] of Object.entries(value)) {
          if (typeof nestedValue !== 'number' || !Number.isFinite(nestedValue)) continue;
          const name = `${key}.${nestedKey}`;
          if (!fields.has(name)) fields.set(name, Array(rows.length).fill(null));
          fields.get(name)[index] = nestedValue;
        }
      }
    }
  });
  return [...fields.entries()]
    .map(([name, values]) => ({ name, values }))
    .filter(series => series.values.filter(Number.isFinite).length >= 2)
    .slice(0, 5);
}

function collectCharts(value, path = 'Result', groups = [], depth = 0) {
  if (depth > 5 || groups.length >= 8 || value == null) return groups;
  if (Array.isArray(value)) {
    if (value.length < 2) return groups;
    if (value.every(item => item === null || (typeof item === 'number' && Number.isFinite(item)))) {
      if (value.filter(Number.isFinite).length >= 2) groups.push({ title: path, series: [{ name: path, values: value }] });
    } else if (value.every(item => item && typeof item === 'object' && !Array.isArray(item))) {
      const series = chartSeriesFromRows(value);
      if (series.length) groups.push({ title: path, series });
      // Include numeric members nested in rows (e.g. holdout metrics) without
      // duplicating every nested object into a separate chart.
    }
    return groups;
  }
  if (typeof value === 'object') {
    for (const [key, child] of Object.entries(value)) {
      if (key === 'assumptions') continue;
      collectCharts(child, `${path}.${key}`, groups, depth + 1);
      if (groups.length >= 8) break;
    }
  }
  return groups;
}

function sampled(values, maxPoints = 140) {
  if (values.length <= maxPoints) return values;
  const step = (values.length - 1) / (maxPoints - 1);
  return Array.from({ length: maxPoints }, (_, index) => values[Math.round(index * step)]);
}

function renderChart(group) {
  const series = group.series.map(item => ({ ...item, values: sampled(item.values) }));
  const count = Math.max(...series.map(item => item.values.length));
  const allValues = series.flatMap(item => item.values).filter(Number.isFinite);
  if (count < 2 || allValues.length < 2) return '';
  let min = Math.min(...allValues), max = Math.max(...allValues);
  if (min === max) { const pad = Math.max(Math.abs(min) * .08, 1); min -= pad; max += pad; }
  const width = 720, height = 230, left = 52, right = 18, top = 14, bottom = 28;
  const plotWidth = width - left - right, plotHeight = height - top - bottom;
  const y = value => top + ((max - value) / (max - min)) * plotHeight;
  const x = index => left + (count <= 1 ? 0 : index / (count - 1)) * plotWidth;
  const grid = Array.from({ length: 5 }, (_, index) => {
    const value = max - ((max - min) * index / 4);
    const yPos = top + (plotHeight * index / 4);
    return `<line x1="${left}" y1="${yPos}" x2="${width-right}" y2="${yPos}" stroke="#e8edf3" stroke-width="1"/><text x="${left-9}" y="${yPos+3}" text-anchor="end" fill="#8997a8" font-size="10">${escapeHtml(formatValue(value))}</text>`;
  }).join('');
  const lines = series.map((item, index) => {
    let segment = [], paths = [];
    item.values.forEach((value, pointIndex) => {
      if (typeof value === 'number' && Number.isFinite(value)) segment.push([x(pointIndex), y(value)]);
      else if (segment.length) { paths.push(segment); segment = []; }
    });
    if (segment.length) paths.push(segment);
    const color = CHART_COLORS[index % CHART_COLORS.length];
    const pathMarkup = paths.map(points => `<path d="${points.map((point, pointIndex) => `${pointIndex ? 'L' : 'M'}${point[0].toFixed(2)},${point[1].toFixed(2)}`).join(' ')}" fill="none" stroke="${color}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>`).join('');
    const pointMarkup = item.values.map((value, pointIndex) => typeof value === 'number' && Number.isFinite(value) ? `<circle cx="${x(pointIndex)}" cy="${y(value)}" r="2.8" fill="${color}"/>` : '').join('');
    return pathMarkup + pointMarkup;
  }).join('');
  const legend = series.map((item, index) => `<span class="chart-legend-item"><i style="background:${CHART_COLORS[index % CHART_COLORS.length]}"></i>${escapeHtml(item.name)}</span>`).join('');
  return `<article class="result-chart-card"><div class="result-chart-title">${escapeHtml(group.title.replaceAll('_', ' '))}</div><div class="result-chart-scroll"><svg class="result-chart" viewBox="0 0 ${width} ${height}" role="img" aria-label="Line chart for ${escapeHtml(group.title)}">${grid}<line x1="${left}" y1="${top}" x2="${left}" y2="${height-bottom}" stroke="#cbd5e1"/><line x1="${left}" y1="${height-bottom}" x2="${width-right}" y2="${height-bottom}" stroke="#cbd5e1"/>${lines}</svg></div><div class="chart-legend">${legend}</div><div class="chart-axis-note">X axis: observation / period index · Y axis: value</div></article>`;
}

function charts(output) {
  const groups = collectCharts(output);
  if (!groups.length) return '';
  return `<section class="result-section"><h3>Charts & data patterns</h3><div class="result-chart-grid">${groups.map(renderChart).join('')}</div></section>`;
}

function kpis(output) {
  const prefer = ['objective','total_cost','NPV','EOQ','project_duration','system_reliability','mean','EVPI','break_even_units','max_flow'];
  const scalars = flattenScalars(output).filter(x => typeof x.value === 'number' && Number.isFinite(x.value));
  const selected = prefer.map(key => scalars.find(x => x.key === key || x.key.endsWith(`.${key}`))).filter(Boolean);
  const items = (selected.length ? selected : scalars.slice(0,3)).slice(0,3);
  if (!items.length) return '';
  return `<div class="result-kpis">${items.map(x => `<div class="result-kpi"><small>${escapeHtml(x.key.replaceAll('_',' '))}</small><strong>${escapeHtml(formatValue(x.value))}</strong></div>`).join('')}</div>`;
}
function sections(output) {
  const parts = [];
  if (Array.isArray(output.assumptions)) {
    parts.push(`<section class="result-section"><h3>Model assumptions & limitations</h3><ul class="assumption-list">${output.assumptions.map(x => `<li>${escapeHtml(x)}</li>`).join('')}</ul></section>`);
  }
  for (const [key, value] of Object.entries(output)) {
    if (key === 'assumptions') continue;
    if (Array.isArray(value) && value.length && (typeof value[0] === 'object' || Array.isArray(value[0]))) {
      parts.push(`<section class="result-section"><h3>${escapeHtml(key.replaceAll('_',' '))}</h3>${renderTable(value)}</section>`);
    }
  }
  parts.push(`<section class="result-section"><h3>Complete result (JSON)</h3><pre class="result-json">${escapeHtml(JSON.stringify(output,null,2))}</pre></section>`);
  return parts.join('');
}

export function showResult(analysis, moduleName) {
  const output = analysis.output || {};
  currentAnalysisId = analysis.analysis_id || analysis.id || null;
  $('#result-title').textContent = moduleName || analysis.title || 'Analysis result';
  $('#result-subtitle').textContent = `${analysis.status || 'SUCCEEDED'}${currentAnalysisId ? ` · Analysis ID: ${currentAnalysisId.slice(0,8)}` : ' · Comparison preview'}`;
  $('.export-actions').hidden = !currentAnalysisId;
  const best = output.best_method ? `<div class="readiness-note" style="margin-bottom:13px"><strong>Best method: ${escapeHtml(output.best_method.toUpperCase())}</strong><br><span style="font-size:8px;color:#7d8da2">${escapeHtml(output.selection_rule || 'Selected by holdout MAD.')}</span></div>` : '';
  $('#result-content').innerHTML = best + kpis(output) + charts(output) + sections(output);
  const modal = $('#result-modal');
  if (modal.hidden) returnFocusTo = document.activeElement;
  modal.hidden = false;
  $('#close-result').focus({ preventScroll: true });
}
export function closeResult() {
  const modal = $('#result-modal');
  if (!modal || modal.hidden) return;
  modal.hidden = true;
  if (returnFocusTo?.isConnected && typeof returnFocusTo.focus === 'function') {
    returnFocusTo.focus({ preventScroll: true });
  }
  returnFocusTo = null;
}
export function resultAnalysisId() { return currentAnalysisId; }
