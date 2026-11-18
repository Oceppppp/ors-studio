const $ = (selector) => document.querySelector(selector);

async function request(path, payload) {
  const response = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'same-origin',
    body: JSON.stringify(payload)
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.detail || `Request failed (${response.status})`);
  return body;
}

function showError(message) {
  const el = $('#auth-error');
  el.textContent = message;
  el.hidden = false;
}

function setBusy(form, busy) {
  form.querySelectorAll('button[type="submit"]').forEach(button => {
    button.disabled = busy;
    if (busy) button.dataset.originalText = button.textContent;
    button.textContent = busy ? 'Please wait…' : (button.dataset.originalText || button.textContent);
  });
}

function activateTab(tab) {
  const login = tab === 'login';
  $('#auth-tab-login').classList.toggle('active', login);
  $('#auth-tab-register').classList.toggle('active', !login);
  $('#auth-tab-login').setAttribute('aria-selected', String(login));
  $('#auth-tab-register').setAttribute('aria-selected', String(!login));
  $('#auth-login-panel').hidden = !login;
  $('#auth-register-panel').hidden = login;
  $('#auth-upgrade-panel').hidden = true;
  $('#auth-error').hidden = true;
  (login ? $('#auth-login-email') : $('#auth-register-name')).focus();
}

function updateChrome(user) {
  const guest = user.kind === 'GUEST';
  $('#profile-mark').textContent = (user.display_name || 'U').trim().charAt(0).toUpperCase();
  $('#profile-label').textContent = guest ? 'Guest session' : (user.display_name || user.email || 'Account');
  $('#profile-chip').setAttribute('aria-label', guest ? 'Temporary guest workspace' : `Signed in as ${user.email}`);
  $('#auth-upgrade-open').hidden = !guest;
  $('#auth-signout').hidden = guest;
  document.querySelectorAll('.local-card strong').forEach(el => { el.textContent = 'Private workspace'; });
  document.querySelectorAll('.local-card small').forEach(el => { el.textContent = guest ? 'Temporary guest data · 24 hours' : 'Only you can access your projects'; });
  const footer = document.querySelector('.sidebar-footer');
  if (footer) footer.innerHTML = '<span class="status-led"></span> Cloud workspace <b>v0.4.0</b>';
  const uploadCopy = document.querySelector('#page-data .import-panel .panel-header p');
  if (uploadCopy) uploadCopy.textContent = 'Upload and process files in your private ORS workspace.';
  const uploadLimits = document.querySelector('#page-data .page-heading .info-pill');
  if (uploadLimits) uploadLimits.textContent = guest ? '5 MiB per file · 15 MiB total storage' : '20 MiB per file · 250 MiB total storage';
  const dropzoneHelp = document.querySelector('#dropzone small');
  if (dropzoneHelp) dropzoneHelp.textContent = guest
    ? 'CSV and XLSX · 5 MiB per file · 15 MiB temporary workspace storage'
    : 'CSV and XLSX · 20 MiB per file · 250 MiB private workspace storage';
  const settingsHeading = document.querySelector('#page-settings .page-subtitle');
  if (settingsHeading) settingsHeading.textContent = 'Cloud workspace, account and storage information.';
  const projectDescription = document.querySelector('#project-dialog-description');
  if (projectDescription) projectDescription.textContent = 'Start a separate private workspace for a new analysis.';
  const projectNote = document.querySelector('.project-dialog-note');
  if (projectNote) projectNote.lastChild.textContent = ' Only your account can access these projects.';
  document.querySelectorAll('.run-hint').forEach(el => { el.innerHTML = '<span class="status-led"></span> Secure cloud analysis'; });
  const mainSettings = document.querySelector('#page-settings .settings-panel');
  if (mainSettings) {
    const rows = mainSettings.querySelectorAll('.settings-row');
    if (rows[1]) { rows[1].querySelector('p').textContent = 'Public web · analysis runs on the ORS cloud service'; rows[1].querySelector('.settings-value, .status-tag').textContent = 'CLOUD'; }
    if (rows[2]) { rows[2].querySelector('p').textContent = guest ? 'Temporary cloud workspace · 15 MiB normalized dataset quota' : 'Private PostgreSQL workspace · 250 MiB normalized dataset quota'; rows[2].querySelector('.settings-value').textContent = 'POSTGRESQL'; }
  }
}

async function establish(path, payload = {}) {
  await request(path, payload);
  window.location.reload();
}

function bindGate() {
  $('#auth-tab-login').addEventListener('click', () => activateTab('login'));
  $('#auth-tab-register').addEventListener('click', () => activateTab('register'));
  $('#auth-guest').addEventListener('click', async () => {
    const button = $('#auth-guest'); button.disabled = true; button.textContent = 'Opening guest workspace…';
    try { await establish('/api/auth/guest'); } catch (error) { showError(error.message); button.disabled = false; button.textContent = 'Continue as guest'; }
  });
  $('#auth-login-panel').addEventListener('submit', async (event) => {
    event.preventDefault(); const form = event.currentTarget; setBusy(form, true);
    try { await establish('/api/auth/login', { email: $('#auth-login-email').value, password: $('#auth-login-password').value }); }
    catch (error) { showError(error.message); setBusy(form, false); }
  });
  $('#auth-register-panel').addEventListener('submit', async (event) => {
    event.preventDefault(); const form = event.currentTarget; setBusy(form, true);
    try { await establish('/api/auth/register', { display_name: $('#auth-register-name').value, email: $('#auth-register-email').value, password: $('#auth-register-password').value }); }
    catch (error) { showError(error.message); setBusy(form, false); }
  });
  $('#auth-upgrade-open').addEventListener('click', () => {
    $('#auth-gate').hidden = false;
    $('#auth-login-panel').hidden = true; $('#auth-register-panel').hidden = true;
    $('#auth-upgrade-panel').hidden = false; $('#auth-title').textContent = 'Keep your work between visits.';
    $('#auth-upgrade-name').focus();
  });
  $('#auth-upgrade-form').addEventListener('submit', async (event) => {
    event.preventDefault(); const form = event.currentTarget; setBusy(form, true);
    try { await establish('/api/auth/upgrade', { display_name: $('#auth-upgrade-name').value, email: $('#auth-upgrade-email').value, password: $('#auth-upgrade-password').value }); }
    catch (error) { showError(error.message); setBusy(form, false); }
  });
  $('#auth-signout').addEventListener('click', async () => {
    try { await request('/api/auth/logout', {}); window.location.reload(); }
    catch (error) { showError(error.message); }
  });
}

export async function initializeCloudAuth() {
  let response;
  try {
    response = await fetch('/api/auth/me', { credentials: 'same-origin', cache: 'no-store' });
  } catch { return null; }
  if (response.status === 404) return null; // desktop/local API does not expose cloud auth
  if (!response.ok) throw new Error('Could not read the cloud account session.');
  const user = await response.json();
  if (!user.cloud_mode) return null;
  if (user.authenticated) {
    updateChrome(user);
    bindGate();
    return user;
  }
  $('#auth-gate').hidden = false;
  bindGate();
  $('#auth-login-email').focus();
  return 'waiting';
}
