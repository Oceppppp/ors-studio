export const $ = (selector, root = document) => root.querySelector(selector);
export const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

export function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}
export function pretty(value) { return JSON.stringify(value, null, 2); }
export function formatValue(value) {
  if (value === null || value === undefined) return '—';
  if (typeof value === 'number') return Number.isInteger(value) ? value.toLocaleString() : value.toLocaleString(undefined, { maximumFractionDigits: 4 });
  if (typeof value === 'boolean') return value ? 'Yes' : 'No';
  if (Array.isArray(value)) return `${value.length} items`;
  if (typeof value === 'object') return 'Object';
  return String(value);
}
export function toast(message, kind = 'success') {
  const stack = $('#toast-stack'); const item = document.createElement('div');
  item.className = `toast ${kind === 'error' ? 'error' : ''}`; item.textContent = message;
  stack.append(item); setTimeout(() => item.remove(), 3600);
}
export function statusClass(status) {
  if (status === 'SUCCEEDED') return 'success';
  if (status === 'FAILED' || status === 'CANCELLED') return 'failed';
  if (status === 'RUNNING') return 'running';
  return 'queued';
}
export function flattenScalars(value, prefix = '', out = []) {
  if (Array.isArray(value)) return out;
  if (value && typeof value === 'object') {
    Object.entries(value).forEach(([key, val]) => flattenScalars(val, prefix ? `${prefix}.${key}` : key, out));
  } else if (prefix) out.push({ key: prefix, value });
  return out;
}


const ICON_PATHS = {
  chart: '<path d="M4 19V5M4 19h16"/><path d="m7 15 3-4 3 2 4-6"/><path d="M17 7h1v1"/>',
  optimize: '<path d="M4 5h16M4 12h16M4 19h16"/><circle cx="9" cy="5" r="2"/><circle cx="15" cy="12" r="2"/><circle cx="7" cy="19" r="2"/>',
  inventory: '<path d="m12 3 8 4.5v9L12 21l-8-4.5v-9L12 3Z"/><path d="m4.5 7.5 7.5 4 7.5-4M12 12v9M8 5l8 4.5"/>',
  truck: '<path d="M3 6h11v11H3zM14 10h4l3 3v4h-7z"/><circle cx="7.5" cy="18" r="1.5"/><circle cx="17.5" cy="18" r="1.5"/>',
  network: '<circle cx="5" cy="12" r="2"/><circle cx="19" cy="5" r="2"/><circle cx="19" cy="19" r="2"/><path d="m7 11 10-5M7 13l10 5"/>',
  people: '<path d="M16 20v-1.5a3.5 3.5 0 0 0-3.5-3.5h-5A3.5 3.5 0 0 0 4 18.5V20"/><circle cx="10" cy="7" r="3"/><path d="M16 4.2a3 3 0 0 1 0 5.6M17 15h1a3 3 0 0 1 3 3v2"/>',
  branch: '<path d="M6 4v5a4 4 0 0 0 4 4h4a4 4 0 0 1 4 4v3"/><circle cx="6" cy="4" r="2"/><circle cx="18" cy="20" r="2"/><circle cx="18" cy="4" r="2"/><path d="M18 6v2a4 4 0 0 1-4 4"/>',
  grid: '<rect x="3.5" y="3.5" width="7" height="7" rx="1"/><rect x="13.5" y="3.5" width="7" height="7" rx="1"/><rect x="3.5" y="13.5" width="7" height="7" rx="1"/><rect x="13.5" y="13.5" width="7" height="7" rx="1"/>',
  upload: '<path d="M12 16V4m0 0L7.5 8.5M12 4l4.5 4.5"/><path d="M4.5 15.5v4h15v-4"/>',
  database: '<ellipse cx="12" cy="5" rx="8" ry="2.5"/><path d="M4 5v6c0 1.4 3.6 2.5 8 2.5s8-1.1 8-2.5V5M4 11v6c0 1.4 3.6 2.5 8 2.5s8-1.1 8-2.5v-6"/>',
  clock: '<circle cx="12" cy="12" r="8.5"/><path d="M12 7v5l3.5 2"/>',
  file: '<path d="M6 3.5h8l4 4V20.5H6z"/><path d="M14 3.5v4h4M9 12h6M9 16h6"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  arrow: '<path d="M5 12h14M13 6l6 6-6 6"/>',
  chevron: '<path d="m9 18 6-6-6-6"/>',
  search: '<circle cx="10.8" cy="10.8" r="6.8"/><path d="m16 16 4.5 4.5"/>',
  refresh: '<path d="M20 7v5h-5"/><path d="M19 12a7.5 7.5 0 1 1-2-5.1L20 12"/>',
  check: '<path d="m5 12 4.2 4.2L19 6.5"/>',
  alert: '<path d="M12 3.5 21 20H3L12 3.5Z"/><path d="M12 9v4.5M12 17h.01"/>',
  close: '<path d="m6 6 12 12M18 6 6 18"/>',
  settings: '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1-1.8 1.8-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.5v.2h-2.6v-.2a1.7 1.7 0 0 0-1-1.5 1.7 1.7 0 0 0-1.9.3l-.1.1-1.8-1.8.1-.1A1.7 1.7 0 0 0 8 15a1.7 1.7 0 0 0-1.5-1H6.3v-2.6h.2a1.7 1.7 0 0 0 1.5-1 1.7 1.7 0 0 0-.3-1.9l-.1-.1 1.8-1.8.1.1a1.7 1.7 0 0 0 1.9.3 1.7 1.7 0 0 0 1-1.5v-.2H15v.2a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.9-.3l.1-.1 1.8 1.8-.1.1a1.7 1.7 0 0 0-.3 1.9 1.7 1.7 0 0 0 1.5 1h.2V14h-.2a1.7 1.7 0 0 0-1.5 1Z"/>',
};
export function iconSvg(name = 'grid', size = 18) {
  const path = ICON_PATHS[name] || ICON_PATHS.grid;
  return `<svg viewBox="0 0 24 24" width="${size}" height="${size}" aria-hidden="true" focusable="false">${path}</svg>`;
}
