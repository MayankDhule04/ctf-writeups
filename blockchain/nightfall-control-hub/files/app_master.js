/* NIGHTFALL — Management console client (bundle).
   Supplies the 3-stage sign-in (login → otp → role token) and the console views.
   NOTE: the admin "System Export" backup (GET /api/export) is a legacy unlinked
   function — kept server-side, never surfaced here. */

(function () {
  'use strict';

  var esc = function (v) {
    if (v == null) return '';
    return String(v).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  };

  /* ------------------------------------------------------------------
     Sign-in — stage 1: credential
     ------------------------------------------------------------------ */

  var loginForm = document.getElementById('login-form');
  if (loginForm) {
    var loginError = document.getElementById('login-error');
    loginForm.addEventListener('submit', async function (event) {
      event.preventDefault();
      loginError.hidden = true;
      var username = (document.getElementById('ops-username').value || '').trim();
      var password = document.getElementById('ops-password').value;
      try {
        var res = await fetch('/api/login', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username: username, password: password }),
        });
        var data = await res.json().catch(function () { return {}; });
        if (res.ok && data.stage === 1) { window.location.href = '/otp'; return; }
        loginError.textContent = data.error || 'Invalid credentials.';
        loginError.hidden = false;
      } catch (err) {
        loginError.textContent = 'Unable to reach the management platform.';
        loginError.hidden = false;
      }
    });
  }

  /* ------------------------------------------------------------------
     Sign-in — stage 2: one-time code
     ------------------------------------------------------------------ */

  var otpForm = document.getElementById('otp-form');
  if (otpForm) {
    var otpError = document.getElementById('otp-error');
    var otpCode = document.getElementById('otp-code');
    var otpBusy = false;

    async function verifyOtp(code) {
      if (otpBusy) return;
      otpBusy = true;
      otpError.hidden = true;
      try {
        var res = await fetch('/api/otp/verify', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ otp: code }),
        });
        var data = await res.json().catch(function () { return {}; });
        if (res.ok && data.stage === 2) { window.location.href = '/role'; return; }
        otpError.textContent = (res.status === 429
          ? (data.error || 'Too many attempts') + '. Try again shortly.'
          : (data.error || 'Invalid one-time code. Try again.'));
        otpError.hidden = false;
      } catch (err) {
        otpError.textContent = 'Unable to reach the verification service.';
        otpError.hidden = false;
      } finally { otpBusy = false; }
    }

    if (otpCode) {
      otpCode.addEventListener('input', function () {
        var value = (otpCode.value || '').trim();
        if (value.length === 6 && /^\d{6}$/.test(value)) verifyOtp(value);
      });
    }
    otpForm.addEventListener('submit', function (event) {
      event.preventDefault();
      verifyOtp((otpCode && otpCode.value || '').trim());
    });
  }

  /* ------------------------------------------------------------------
     Sign-in — stage 3: role token
     ------------------------------------------------------------------ */

  var roleForm = document.getElementById('role-form');
  if (roleForm) {
    var roleError = document.getElementById('role-error');
    roleForm.addEventListener('submit', async function (event) {
      event.preventDefault();
      roleError.hidden = true;
      var token = (document.getElementById('role-token').value || '').trim();
      try {
        var res = await fetch('/api/auth/role', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ role_token: token }),
        });
        var data = await res.json().catch(function () { return {}; });
        if (res.ok && data.stage === 3) { window.location.href = '/console'; return; }
        roleError.textContent = data.error || 'Invalid role token.';
        roleError.hidden = false;
      } catch (err) {
        roleError.textContent = 'Unable to reach the management platform.';
        roleError.hidden = false;
      }
    });
  }

  /* ------------------------------------------------------------------
     Console
     ------------------------------------------------------------------ */

  var logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', function () {
      logoutBtn.disabled = true;
      fetch('/api/logout', { method: 'GET', credentials: 'same-origin' })
        .then(function () { window.location.href = '/'; })
        .catch(function () { window.location.href = '/'; });
    });
  }

  function table(headers, rows) {
    var h = headers.map(function (x) { return '<th>' + esc(x) + '</th>'; }).join('');
    var r = rows.map(function (cols) {
      return '<tr>' + cols.map(function (c) { return '<td class="mono-sm">' + esc(c) + '</td>'; }).join('') + '</tr>';
    }).join('');
    return '<div class="table-scroll"><table class="data-table"><thead><tr>' + h + '</tr></thead><tbody>' +
      (r || '<tr><td colspan="' + headers.length + '" class="empty-state">none</td></tr>') +
      '</tbody></table></div>';
  }

  // Fleet "Health Probe" — ping an endpoint before dispatch (server-side fetch).
  function healthProbeBox() {
    return '<div class="probe-box">' +
      '<div class="section-kicker" style="color:hsl(var(--accent))">HEALTH PROBE</div>' +
      '<p class="panel-sub">Connectivity tester — fetches an HTTP(S) endpoint and returns status + response bytes.</p>' +
      '<div class="probe-inputs">' +
      '<input class="field-control" id="probe-target" placeholder="http://host:port/path" spellcheck="false" />' +
      '<input class="field-control" id="probe-token" placeholder="X-Bus-Token (optional)" spellcheck="false" />' +
      '<button class="blue-button" id="probe-run">PROBE</button>' +
      '</div>' +
      '<pre class="ops-feed" id="probe-out" style="white-space:pre-wrap; margin-top:.75rem"></pre>' +
      '</div>';
  }

  // Evidence verification — confirm the recovered reference, then follow the upstream link.
  function upstreamLinkBox() {
    return '<div class="probe-box mt-4">' +
      '<div class="section-kicker" style="color:hsl(var(--accent))">EVIDENCE VERIFICATION</div>' +
      '<p class="panel-sub">Confirm the evidence reference recovered from the internal control ' +
      'bus to re-establish the platform\u2019s upstream control link.</p>' +
      '<div class="probe-inputs">' +
      '<input class="field-control" id="evidence-ref" placeholder="recovered evidence reference" spellcheck="false" autocomplete="off" />' +
      '<button class="blue-button" id="evidence-run">VERIFY</button>' +
      '</div>' +
      '<pre class="ops-feed" id="upstream-out" style="white-space:pre-wrap; margin-top:.75rem"></pre>' +
      '</div>';
  }

  // Records — artifact export (fetch a stored record/artifact by name).
  function artifactExportBox(files) {
    var chips = files.map(function (f) { return '<span class="chip" data-file="' + esc(f) + '">' + esc(f) + '</span>'; }).join(' ');
    return '<div class="probe-box mt-4">' +
      '<div class="section-kicker" style="color:hsl(var(--accent))">ARTIFACT EXPORT</div>' +
      '<p class="panel-sub">Stream one stored record / config artifact by name.</p>' +
      '<div class="probe-inputs">' +
      '<input class="field-control" id="record-file" placeholder="record filename (or rel-path)" spellcheck="false" />' +
      '<button class="blue-button" id="record-run">EXPORT</button>' +
      '</div>' +
      '<div class="chip-row">' + chips + '</div>' +
      '<pre class="ops-feed" id="record-out" style="white-space:pre-wrap; margin-top:.75rem"></pre>' +
      '</div>';
  }

  function wireProbe() {
    var run = document.getElementById('probe-run');
    var target = document.getElementById('probe-target');
    var token = document.getElementById('probe-token');
    var out = document.getElementById('probe-out');
    if (!run || !target || !out) return;
    run.addEventListener('click', async function () {
      run.disabled = true;
      out.textContent = 'probing…';
      var headers = {};
      if (token && token.value.trim()) headers['X-Bus-Token'] = token.value.trim();
      try {
        var res = await fetch('/api/mgmt/probe', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ target: target.value.trim(), headers: headers }),
        });
        var d = await res.json();
        if (d.ok) {
          out.textContent = 'TARGET   ' + d.target + '\n' +
            'STATUS   ' + d.status + '\n' +
            'BODY     ' + (d.body || '(empty)');
        } else if (d.error) {
          out.textContent = 'ERROR    ' + d.error;
        } else {
          out.textContent = 'TARGET   ' + d.target + '\nSTATUS   ' + d.status + '\n' + (d.body || '');
        }
      } catch (err) {
        out.textContent = 'ERROR    request failed';
      } finally { run.disabled = false; }
    });
  }

  function wireUpstream() {
    var run = document.getElementById('evidence-run');
    var input = document.getElementById('evidence-ref');
    var out = document.getElementById('upstream-out');
    if (!run || !input || !out) return;

    function renderLink(u) {
      if (!u || u.link !== 'ESTABLISHED') {
        out.textContent = 'EVIDENCE REFERENCE ACCEPTED\nUPSTREAM LINK: establishing…';
        return true;                                    // keep polling
      }
      out.textContent = 'UPSTREAM LINK: ESTABLISHED\n' +
        'PRINCIPAL  ' + (u.principal || '—') + '\n' +
        'PORTAL     ' + (u.portal || '—') + '\n' +
        'URL        ' + (u.url || '—');
      return false;                                     // stop polling
    }

    async function poll(tries) {
      try {
        var res = await fetch('/api/mgmt/upstream', { credentials: 'same-origin' });
        var d = await res.json();
        if (res.ok && d.upstream && !renderLink(d.upstream)) return;
      } catch (err) { /* keep trying */ }
      if (tries > 0) setTimeout(function () { poll(tries - 1); }, 2000);
    }

    run.addEventListener('click', async function () {
      run.disabled = true;
      out.textContent = 'verifying evidence reference…';
      try {
        var res = await fetch('/api/mgmt/upstream', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ reference: input.value.trim() }),
        });
        var d = await res.json();
        if (res.ok && d.ok) {
          poll(10);                                     // start polling the link status
        } else {
          out.textContent = 'ERROR      ' + (d.error || 'reference not recognized');
          run.disabled = false;
        }
      } catch (err) {
        out.textContent = 'ERROR      request failed';
        run.disabled = false;
      }
    });
  }

  function wireRecordExport() {
    var run = document.getElementById('record-run');
    var file = document.getElementById('record-file');
    var out = document.getElementById('record-out');
    if (!run || !file || !out) return;
    var chips = document.querySelectorAll('.chip-row .chip');
    chips.forEach(function (chip) {
      chip.addEventListener('click', function () {
        file.value = chip.getAttribute('data-file') || '';
      });
    });
    run.addEventListener('click', async function () {
      run.disabled = true;
      out.textContent = 'fetching…';
      try {
        var res = await fetch('/api/mgmt/records/export?file=' + encodeURIComponent(file.value.trim()));
        var d = await res.json();
        if (d.ok) out.textContent = 'FILE ' + d.file + '\n' + (d.content || '(empty)');
        else out.textContent = d.error || 'unable to export record';
      } catch (err) {
        out.textContent = 'request failed';
      } finally { run.disabled = false; }
    });
  }

  var MODULES = {
    dashboard: async function (body) {
      var d = await fetch('/api/mgmt/overview').then(function (r) { return r.json(); });
      body.innerHTML =
        '<div class="stat-strip">' +
        card('OPERATORS', d.operators) + card('DIRECTIVES', d.directives) +
        card('FLEET NODES', d.fleet) + card('BUS ROUTES', d.bus_routes) +
        '</div>' +
        '<div class="mt-4 mono-sm" style="color:hsl(var(--muted-foreground)); line-height:1.9">' +
        'node_id&nbsp;: <span style="color:hsl(var(--accent))">' + esc(d.node_id) + '</span><br>' +
        'firmware : ' + esc(d.firmware) + '<br>seal : ' + esc(d.seal) + '</div>';
    },
    operators: async function (body) {
      var list = await fetch('/api/mgmt/operators').then(function (r) { return r.json(); });
      var rows = list.map(function (o) {
        return [o.username, o.type, o.role, o.bound_service || '—', o.status, o.handler];
      });
      body.innerHTML = table(['PRINCIPAL', 'TYPE', 'ROLE', 'SERVICE', 'STATUS', 'HANDLER'], rows);
      document.getElementById('scope-notice').hidden = false;
    },
    directives: async function (body) {
      var list = await fetch('/api/mgmt/directives').then(function (r) { return r.json(); });
      body.innerHTML = table(['ID', 'TARGET', 'ACTION', 'STATUS', 'ISSUER'],
        list.map(function (x) { return [x.id, x.target, x.action, x.status, x.issuer]; }));
    },
    fleet: async function (body) {
      var list = await fetch('/api/mgmt/fleet').then(function (r) { return r.json(); });
      body.innerHTML = table(['NODE', 'APP', 'STATUS', 'ENDPOINT', 'LAST PING'],
        list.map(function (x) { return [x.id, x.app, x.status, x.endpoint, x.last_ping]; })) +
        healthProbeBox();
      wireProbe();
    },
    bus: async function (body) {
      var list = await fetch('/api/mgmt/bus').then(function (r) { return r.json(); });
      body.innerHTML = table(['FROM', 'TO', 'ROUTE', 'TRANSPORT'],
        list.map(function (x) { return [x.from, x.to, x.route, x.transport]; }));
    },
    audit: async function (body) {
      var list = await fetch('/api/mgmt/audit').then(function (r) { return r.json(); });
      body.innerHTML = table(['TIMESTAMP', 'ACTOR', 'ACTION'],
        list.map(function (x) { return [x.ts, x.actor, x.action]; }));
    },
    records: async function (body) {
      var d = await fetch('/api/mgmt/records?scope=operator').then(function (r) { return r.json(); });
      var pre = JSON.stringify(d.records, null, 2);
      body.innerHTML =
        '<div class="section-kicker">OPERATIONAL RECORDS — SCOPE: ' + esc(d.scope) + '</div>' +
        '<pre class="ops-feed scroll" style="white-space:pre-wrap; margin-top:.75rem">' + esc(pre) + '</pre>' +
        '<div class="mt-4" style="border-top:1px solid hsl(var(--border)); padding-top:1rem">' +
        '<div class="section-kicker">RECORD ARTIFACTS</div>' +
        '<p class="panel-sub">Stored records/artifacts (the <em>evidence_signpost.json</em> artifact ' +
        'documents the evidence store on the internal control-bus agent — see the Bus module). ' +
        'Click a file chip, or type a filename/path, then EXPORT.</p>' +
        '</div>' +
        artifactExportBox(d.artifact_files || []) +
        upstreamLinkBox() +
        '<div class="mt-4" style="border-top:1px solid hsl(var(--border)); padding-top:1rem">' +
        '<div class="section-kicker">SYSTEM EXPORT</div>' +
        '<p class="panel-sub">Full operational archive export is an admin (master scope) function.</p>' +
        '<button class="blue-button" style="padding:.5rem 1rem; font-size:11px" disabled>System Export — requires master scope</button>' +
        '</div>';
      wireRecordExport();
      wireUpstream();
      document.getElementById('scope-notice').hidden = false;
    },
  };

  function card(label, value) {
    return '<div class="stat-card"><div class="stat-label">' + esc(label) + '</div>' +
      '<div class="stat-value">' + esc(value) + '</div></div>';
  }

  var titleMap = {
    dashboard: 'DASHBOARD', operators: 'OPERATOR REGISTRY', directives: 'DIRECTIVE QUEUE',
    fleet: 'FLEET / NODE HEALTH', bus: 'BUS TOPOLOGY', audit: 'AUDIT TRAIL',
    records: 'RECORDS &amp; SYSTEM EXPORT',
  };

  document.querySelectorAll('#console-nav a[data-module]').forEach(function (link) {
    link.addEventListener('click', function (event) {
      event.preventDefault();
      var mod = link.getAttribute('data-module');
      document.querySelectorAll('#console-nav a').forEach(function (a) { a.classList.remove('active'); });
      link.classList.add('active');
      var title = document.querySelector('#module-view .section-kicker');
      if (title) title.innerHTML = titleMap[mod] || 'MODULE';
      var body = document.getElementById('module-body');
      body.innerHTML = 'Loading…';
      document.getElementById('scope-notice').hidden = true;
      if (MODULES[mod]) MODULES[mod](body).catch(function () { body.innerHTML = 'Module unavailable.'; });
    });
  });

  if (document.getElementById('console-nav')) {
    document.querySelector('#console-nav a[data-module="dashboard"]').click();
  }
})();