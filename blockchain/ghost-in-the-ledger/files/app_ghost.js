/* NIGHTFALL OPS — Telemetry client
   Auth (login → /otp) + the capture console (archive, session log w/ live stream, processes,
   memory, vault export).
*/

(function () {
  'use strict';

  var state = { captureId: null, status: null, events: [], processes: [], memory: '', liveTimer: null, eventFilter: '', rendered: 0, shown: 0 };

  function esc(v) {
    if (v == null) return '';
    return String(v).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  function setStat(id, value) { var el = document.getElementById(id); if (el) el.textContent = value; }

  /* ================= Auth: login ================= */
  var form = document.getElementById('login-form');
  if (form) {
    var submitBtn = document.getElementById('login-submit');
    var errorBox = document.getElementById('login-error');
    form.addEventListener('submit', async function (event) {
      event.preventDefault();
      errorBox.hidden = true;
      var username = (document.getElementById('ops-username').value || '').trim();
      var password = document.getElementById('ops-password').value;
      submitBtn.disabled = true;
      submitBtn.textContent = 'AUTHENTICATING…';
      try {
        var res = await fetch('/api/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username: username, password: password }),
        });
        var data = await res.json().catch(function () { return {}; });
        if (res.ok && data.ok) { window.location.href = '/otp'; return; }   // stage 1 → TOTP
        errorBox.textContent = data.error || 'Invalid credentials. Check the principal and credential and try again.';
        errorBox.hidden = false;
      } catch (err) {
        errorBox.textContent = 'Unable to reach the telemetry service. Try again.';
        errorBox.hidden = false;
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'ENTER TELEMETRY';
      }
    });
  }

  /* ================= Auth: OTP ================= */
  var otpForm = document.getElementById('otp-form');
  if (otpForm) {
    var otpError = document.getElementById('otp-error');
    var otpCode = document.getElementById('otp-code');
    var verifying = false;
    async function doVerify(code) {
      if (verifying) return;
      verifying = true;
      otpError.hidden = true;
      try {
        var res = await fetch('/api/otp/verify', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ otp: code }),
        });
        var data = await res.json().catch(function () { return {}; });
        if (res.ok && data.ok) { window.location.href = '/dashboard'; return; }
        otpError.textContent = (res.status === 429
          ? (data.error || 'Too many attempts') + '. Try again shortly.'
          : (data.error || 'Invalid one-time code. Try again.'));
        otpError.hidden = false;
      } catch (err) {
        otpError.textContent = 'Unable to reach the verification service.';
        otpError.hidden = false;
      } finally {
        verifying = false;
      }
    }
    if (otpCode) {
      otpCode.addEventListener('input', function () {
        var value = (otpCode.value || '').trim();
        if (value.length === 6 && /^\d{6}$/.test(value)) doVerify(value);
      });
    }
    otpForm.addEventListener('submit', function (event) {
      event.preventDefault();
      doVerify((otpCode && otpCode.value || '').trim());
    });
  }

  /* ================= Logout ================= */
  var logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', function () {
      logoutBtn.disabled = true;
      fetch('/api/logout', { method: 'GET', credentials: 'same-origin' })
        .then(function () { window.location.href = '/'; })
        .catch(function () { window.location.href = '/'; });
    });
  }

  /* ================= Console chrome ================= */
  var wsTag = document.getElementById('ws-tag');
  if (wsTag) wsTag.textContent = 'WS://' + (window.location.hostname || 'telemetry-ops') + '/session';

  /* ================= Capture archive ================= */
  var capsBody = document.getElementById('captures-body');
  if (capsBody) loadCaptures();

  async function loadCaptures() {
    var meta = document.getElementById('captures-meta');
    try {
      var res = await fetch('/api/telemetry/captures', { credentials: 'same-origin' });
      if (res.status === 401) { window.location.href = '/'; return; }
      var rows = await res.json();
      if (!Array.isArray(rows)) throw new Error('bad response');
      if (meta) meta.textContent = rows.length + ' CAPTURES';
      setStat('stat-captures', rows.length);
      setStat('stat-running', rows.filter(function (c) { return c.status === 'RUNNING'; }).length);
      capsBody.innerHTML = rows.map(function (c) {
        var running = c.status === 'RUNNING';
        return '<tr>' +
          '<td class="mono-sm">' + esc(c.id) + '</td>' +
          '<td class="mono-sm">' + esc(c.host) + '</td>' +
          '<td class="mono-sm">' + esc(c.ts) + '</td>' +
          '<td class="mono-sm">' + esc(c.size) + '</td>' +
          '<td>' + (running
            ? '<span class="badge badge-running"><span class="live-dot"></span>RUNNING</span>'
            : '<span class="badge badge-idle">IDLE</span>') + '</td>' +
          '<td><button type="button" class="mini-button inspect-btn" data-capture="' + esc(c.id) + '">INSPECT</button></td>' +
          '</tr>';
      }).join('');
      capsBody.querySelectorAll('.inspect-btn').forEach(function (b) {
        b.addEventListener('click', function () { inspectCapture(b.getAttribute('data-capture')); });
      });
    } catch (err) {
      if (meta) meta.textContent = 'ERROR';
      capsBody.innerHTML = '<tr><td colspan="6" class="empty-state">Unable to load captures.</td></tr>';
    }
  }

  /* ================= Tabs ================= */
  function activateTab(name) {
    document.querySelectorAll('#capture-tabs .tab').forEach(function (t) {
      t.classList.toggle('active', t.getAttribute('data-tab') === name);
    });
    document.querySelectorAll('.tab-panel').forEach(function (p) {
      p.classList.toggle('active', p.getAttribute('data-panel') === name);
    });
  }
  document.querySelectorAll('#capture-tabs .tab').forEach(function (t) {
    t.addEventListener('click', function () { activateTab(t.getAttribute('data-tab')); });
  });

  /* ================= Live stream ================= */
  function stopLive() {
    if (state.liveTimer) { clearInterval(state.liveTimer); state.liveTimer = null; }
    var ind = document.getElementById('live-indicator');
    if (ind) ind.hidden = true;
  }

  function startLive() {
    var since = state.events.length;
    state.liveTimer = setInterval(async function () {
      if (!state.captureId) return;
      try {
        var res = await fetch('/api/telemetry/capture/' + encodeURIComponent(state.captureId) +
          '/events?since=' + since, { credentials: 'same-origin' });
        if (!res.ok) return;
        var data = await res.json();
        if (!Array.isArray(data.entries) || !data.entries.length) return;
        state.events = state.events.concat(data.entries);
        since = state.events.length;
        setStat('stat-events', state.events.length);
        appendEvents();          // append in the background — no scroll, no focus change
      } catch (err) { /* keep streaming */ }
    }, 3000);
  }

  /* ================= Capture workspace ================= */
  async function inspectCapture(cid) {
    stopLive();
    state.captureId = cid;
    state.status = null;
    state.events = [];
    state.processes = [];
    state.memory = '';
    state.eventFilter = '';
    var detail = document.getElementById('capture-detail');
    detail.hidden = false;
    document.getElementById('capture-title').textContent = cid;
    document.getElementById('capture-meta').innerHTML = '<span class="chip">loading…</span>';
    document.getElementById('event-filter').value = '';
    document.getElementById('proc-filter').value = '';
    document.getElementById('memory-view').textContent = 'Select a process on the PROCESSES tab to view its memory page.';
    document.getElementById('memory-view').classList.add('is-empty');
    document.getElementById('memory-title').textContent = 'No process selected';
    document.getElementById('memory-copy').disabled = true;
    activateTab('events');

    // detail / meta chips
    try {
      var metaRes = await fetch('/api/telemetry/capture/' + encodeURIComponent(cid), { credentials: 'same-origin' });
      var meta = await metaRes.json().catch(function () { return {}; });
      state.status = meta.status;
      document.getElementById('capture-meta').innerHTML =
        [['host', meta.host], ['recorded', meta.ts], ['size', meta.size], ['status', meta.status]]
          .filter(function (kv) { return kv[1]; })
          .map(function (kv) { return '<span class="chip">' + esc(kv[0]) + ': ' + esc(kv[1]) + '</span>'; }).join('');
    } catch (err) { document.getElementById('capture-meta').innerHTML = ''; }

    // events (static + any live so far)
    var evBox = document.getElementById('events');
    evBox.textContent = 'loading…';
    try {
      var evRes = await fetch('/api/telemetry/capture/' + encodeURIComponent(cid) + '/events?since=0', { credentials: 'same-origin' });
      var ev = await evRes.json();
      state.events = Array.isArray(ev.entries) ? ev.entries : [];
      setStat('stat-events', state.events.length);
      renderEvents();
    } catch (err) { state.events = []; evBox.textContent = 'unavailable'; }

    // live streaming only for the RUNNING capture
    if (state.status === 'RUNNING') {
      var ind = document.getElementById('live-indicator');
      if (ind) ind.hidden = false;
      startLive();
    }

    // processes
    try {
      var prRes = await fetch('/api/telemetry/capture/' + encodeURIComponent(cid) + '/processes', { credentials: 'same-origin' });
      var procs = await prRes.json();
      state.processes = Array.isArray(procs) ? procs : [];
      setStat('stat-processes', state.processes.length);
      renderProcesses('');
    } catch (err) { state.processes = []; renderProcesses(''); }
  }

  /* ---- session log ---- */
  function eventMatches(e, f) {
    if (!f) return true;
    return (e.process + ' ' + e.pid + ' ' + (e.session || '') + ' ' + e.action).toLowerCase().indexOf(f) >= 0;
  }
  function eventHtml(e) {
    var line = e.ts + '  pid=' + String(e.pid).padEnd(5) + ' ' + e.process + '  — ' + e.action +
      (e.principal ? '  [' + e.principal + ']' : '') + (e.session ? '  session=' + e.session : '');
    return '<div>' + esc(line) + '</div>';
  }
  function updateEventCount() {
    document.getElementById('events-count').textContent = state.shown + ' / ' + state.events.length + ' entries';
  }
  // full (re)render — only on inspect and when the filter changes
  function renderEvents() {
    var box = document.getElementById('events');
    var f = (state.eventFilter || '').toLowerCase();
    var rows = state.events.filter(function (e) { return eventMatches(e, f); });
    box.innerHTML = rows.length ? rows.map(eventHtml).join('')
      : '<div class="empty-state">No matching log entries.</div>';
    state.rendered = state.events.length;
    state.shown = rows.length;
    updateEventCount();
  }
  // background append — never scrolls, never steals focus
  function appendEvents() {
    var box = document.getElementById('events');
    if (state.rendered >= state.events.length) return;
    var f = (state.eventFilter || '').toLowerCase();
    var add = '', n = 0;
    for (var i = state.rendered; i < state.events.length; i++) {
      if (eventMatches(state.events[i], f)) { add += eventHtml(state.events[i]); n++; }
    }
    state.rendered = state.events.length;
    if (!add) return;
    var empty = box.querySelector('.empty-state');
    if (empty) empty.remove();
    box.insertAdjacentHTML('beforeend', add);
    state.shown += n;
    updateEventCount();
  }
  var eventFilter = document.getElementById('event-filter');
  if (eventFilter) eventFilter.addEventListener('input', function () {
    state.eventFilter = eventFilter.value;
    renderEvents();
  });

  /* ---- processes ---- */
  function renderProcesses(filter) {
    var box = document.getElementById('processes');
    var f = (filter || '').toLowerCase();
    var rows = state.processes.filter(function (p) {
      return !f || p.name.toLowerCase().indexOf(f) >= 0 || String(p.pid).indexOf(f) >= 0;
    });
    document.getElementById('procs-count').textContent = rows.length + ' / ' + state.processes.length + ' processes';
    if (!rows.length) { box.innerHTML = '<div class="empty-state">No matching processes.</div>'; return; }
    box.innerHTML = rows.map(function (p) {
      return '<div class="proc-row">' +
        '<span class="proc-name">' + esc(p.name) + '</span>' +
        '<span class="proc-pid">' + esc(p.pid) + '</span>' +
        '<button type="button" class="mini-button mem-btn" data-pid="' + esc(p.pid) + '">VIEW</button>' +
        '</div>';
    }).join('');
    box.querySelectorAll('.mem-btn').forEach(function (b) {
      b.addEventListener('click', function () { viewMemory(b.getAttribute('data-pid')); });
    });
  }
  var procFilter = document.getElementById('proc-filter');
  if (procFilter) procFilter.addEventListener('input', function () { renderProcesses(procFilter.value); });

  /* ---- memory ---- */
  async function viewMemory(pid) {
    if (!state.captureId) return;
    var view = document.getElementById('memory-view');
    var copyBtn = document.getElementById('memory-copy');
    document.getElementById('memory-title').textContent = 'pid ' + pid;
    view.classList.remove('is-empty');
    view.textContent = 'loading…';
    activateTab('memory');
    try {
      var res = await fetch('/api/telemetry/capture/' + encodeURIComponent(state.captureId) +
        '/process/' + encodeURIComponent(pid) + '/memory', { credentials: 'same-origin' });
      var text = await res.text();
      state.memory = res.ok ? text : (text || 'unavailable');
    } catch (err) { state.memory = 'unavailable'; }
    view.textContent = state.memory;
    copyBtn.disabled = !state.memory;
  }
  var copyBtn = document.getElementById('memory-copy');
  if (copyBtn) {
    copyBtn.addEventListener('click', function () {
      if (!state.memory) return;
      navigator.clipboard.writeText(state.memory).then(function () {
        copyBtn.textContent = 'COPIED';
        setTimeout(function () { copyBtn.textContent = 'COPY'; }, 1200);
      }).catch(function () {});
    });
  }

  /* ================= Vault export ================= */
  var eform = document.getElementById('export-form');
  if (eform) {
    var eresult = document.getElementById('export-result');
    eform.addEventListener('submit', async function (event) {
      event.preventDefault();
      var token = (document.getElementById('vault-token').value || '').trim();
      if (!token) return;
      try {
        var res = await fetch('/api/telemetry/vault/export', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ token: token }),
        });
        var data = await res.json().catch(function () { return {}; });
        if (data.correct) {
          eresult.style.background = '#eefaf3';
          eresult.style.color = '#0a6b38';
          eresult.innerHTML = 'EXPORT READY — ' + esc(data.filename) + ' (' + esc(data.records) +
            ' records, ' + esc(data.encoding) + ').<br>seal: ' + esc(data.seal) +
            '<br><a href="#" id="export-dl" style="color:inherit; text-decoration:underline">DOWNLOAD ' +
            esc(data.filename) + '</a>';
          eresult.hidden = false;
          var blob = new Blob([data.data], { type: 'text/plain' });
          var link = document.getElementById('export-dl');
          if (link) { link.href = URL.createObjectURL(blob); link.download = data.filename; }
        } else {
          eresult.style.background = '#fdeeee';
          eresult.style.color = '#a11';
          eresult.textContent = 'Access token not recognized.';
          eresult.hidden = false;
        }
      } catch (err) {
        eresult.style.background = '#fdeeee';
        eresult.style.color = '#a11';
        eresult.textContent = 'Unable to reach the telemetry service.';
        eresult.hidden = false;
      }
    });
  }
})();
