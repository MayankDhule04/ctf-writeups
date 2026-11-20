/* NIGHTFALL OPS — Escrow Ledger client */

(function () {
  'use strict';

  var wsTag = document.getElementById('ws-tag');
  if (wsTag) {
    wsTag.textContent = 'WS://' + (window.location.hostname || 'escrow-ops') + '/session';
  }

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

        if (res.ok && data.ok) {
          window.location.href = '/otp';   // stage 1 done — TOTP next
          return;
        }
        showError(data.error || 'Invalid credentials.');
      } catch (err) {
        showError('Unable to reach the authentication service.');
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'ENTER ESCROW';
      }
    });

    function showError(message) {
      errorBox.textContent = message;
      errorBox.hidden = false;
    }
  }

  /* ---- OTP page — auto-verifies once all 6 digits are entered ---- */
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
        if (res.ok && data.ok) {
          window.location.href = '/dashboard';
          return;
        }
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

  /* ---- Logout (dashboard) — clears the session ---- */
  var logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', function () {
      logoutBtn.disabled = true;
      fetch('/api/logout', { method: 'GET', credentials: 'same-origin' })
        .then(function () { window.location.href = '/'; })
        .catch(function () { window.location.href = '/'; });
    });
  }

  var tbody = document.getElementById('periods-body');
  if (tbody) {
    loadPeriods();
  }

  async function loadPeriods() {
    var meta = document.getElementById('periods-meta');
    try {
      var res = await fetch('/api/escrow/periods', { credentials: 'same-origin' });
      if (res.status === 401) {
        window.location.href = '/';
        return;
      }
      var rows = await res.json();
      if (!Array.isArray(rows)) throw new Error('bad response');
      if (meta) meta.textContent = rows.length + ' PERIODS';
      if (!rows.length) {
        tbody.innerHTML = '<tr><td colspan="6" class="mono-sm">No periods.</td></tr>';
        return;
      }
      tbody.innerHTML = rows.map(function (row) {
        var disabled = row.status === 'RELEASED' ? ' disabled' : '';
        return (
          '<tr data-period="' + esc(row.period_id) + '">' +
          '<td class="mono-sm">' + esc(row.period_id) + '</td>' +
          '<td class="mono-sm">' + esc(row.escrow_token) + '</td>' +
          '<td class="mono-sm">' + esc(row.manifest_id) + ' <a href="/api/escrow/periods' + esc(row.manifest_url) +
          '" target="_blank" rel="noopener" class="nav-link" style="font-size:10px">manifest ↗</a></td>' +
          '<td>' + esc(row.amount) + '</td>' +
          '<td class="mono-sm">' + esc(row.status) + '</td>' +
          '<td><button type="button" class="blue-button release-btn"' + disabled +
          ' data-period="' + esc(row.period_id) + '">Release escrow</button></td>' +
          '</tr>'
        );
      }).join('');

      tbody.querySelectorAll('.release-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
          if (btn.disabled) return;
          var tr = btn.closest('tr');
          var periodId = tr.getAttribute('data-period');
          openReleasePrompt(periodId, btn);
        });
      });
    } catch (err) {
      if (meta) meta.textContent = 'ERROR';
      tbody.innerHTML = '<tr><td colspan="5" class="mono-sm">Unable to load periods.</td></tr>';
    }
  }

  async function releasePeriod(periodId, settlementCode, btn) {
    var panel = document.getElementById('release-panel');
    var output = document.getElementById('release-output');
    btn.disabled = true;
    try {
      var res = await fetch('/api/escrow/release', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
        body: JSON.stringify({ period: periodId, settlement_code: settlementCode }),
      });
      var data = await res.json().catch(function () { return {}; });
      panel.hidden = false;
      if (res.ok) {
        output.textContent = JSON.stringify(data, null, 2);
        await loadPeriods();
      } else {
        output.textContent = data.error || 'Release failed.';
        btn.disabled = false;
      }
    } catch (err) {
      panel.hidden = false;
      output.textContent = 'Unable to reach the release service.';
      btn.disabled = false;
    }
  }

  function esc(value) {
    if (value == null) return '';
    return String(value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  /* ------------------------------------------------------------------ *
   * ESCROW RELEASE — settlement-code prompt (styled modal)
   * ------------------------------------------------------------------ */
  var releasePrompt = document.getElementById('release-prompt');
  var pendingRelease = null;

  function openReleasePrompt(periodId, btn) {
    if (!releasePrompt) {
      // fallback (markup missing) — legacy browser prompt
      var code = window.prompt('Settlement code for ' + periodId + ' (64-character hex fingerprint):', '');
      if (code != null) releasePeriod(periodId, code.trim(), btn);
      return;
    }
    pendingRelease = { periodId: periodId, btn: btn };
    var period = document.getElementById('prompt-period');
    var field = document.getElementById('prompt-code');
    var errorBox = document.getElementById('prompt-error');
    if (period) period.textContent = 'PERIOD: ' + periodId;
    if (field) { field.value = ''; }
    if (errorBox) errorBox.hidden = true;
    releasePrompt.hidden = false;
    if (field) field.focus();
  }

  function closeReleasePrompt() {
    pendingRelease = null;
    if (releasePrompt) releasePrompt.hidden = true;
  }

  if (releasePrompt) {
    var cancelBtn = document.getElementById('prompt-cancel');
    if (cancelBtn) cancelBtn.addEventListener('click', closeReleasePrompt);

    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && !releasePrompt.hidden) closeReleasePrompt();
    });

    var promptForm = document.getElementById('release-prompt-form');
    if (promptForm) {
      promptForm.addEventListener('submit', function (event) {
        event.preventDefault();
        if (!pendingRelease) return;
        var field = document.getElementById('prompt-code');
        var errorBox = document.getElementById('prompt-error');
        var code = (field && field.value || '').trim();
        if (!/^[0-9a-f]{64}$/i.test(code)) {
          if (errorBox) {
            errorBox.textContent = 'Settlement code must be a 64-character hexadecimal fingerprint.';
            errorBox.hidden = false;
          }
          if (field) field.focus();
          return;
        }
        var pr = pendingRelease;
        closeReleasePrompt();
        releasePeriod(pr.periodId, code, pr.btn);
      });
    }
  }
})();

// ---------------------------------------------------------------------------
// Legacy "settlement bundle reader" (kept for the old operator console). The
// per-period settlement manifests are sealed: each bundle is XOR-encrypted with
// key = sha256(period_id + manifest_id). The console opens them client-side.
// ---------------------------------------------------------------------------
function hexToBytes(hex) {
  var bytes = [];
  for (var i = 0; i < hex.length; i += 2) bytes.push(parseInt(hex.substr(i, 2), 16));
  return bytes;
}

function bytesToUtf8(bytes) {
  return decodeURIComponent(escape(String.fromCharCode.apply(null, bytes)));
}

function readSettlementBundle(periodId, manifestId, hexBlob) {
  var keyHex = CryptoJS.SHA256(periodId + manifestId).toString(CryptoJS.enc.Hex);
  var key = hexToBytes(keyHex);
  var data = hexToBytes(hexBlob);
  var out = new Array(data.length);
  for (var i = 0; i < data.length; i++) out[i] = data[i] ^ key[i % key.length];
  return JSON.parse(bytesToUtf8(out));
}

// Legacy "staff release" helper (kept for compatibility, unused by the UI). The
// release code is the SHA-256 fingerprint of the period id, its escrow reference,
// and the release salt — see the dev generator docs under /api/escrow/dev/secrets.
function computeSettlementCode(periodId, escrowToken, releaseSalt) {
  return CryptoJS.SHA256(periodId + escrowToken + releaseSalt).toString(CryptoJS.enc.Hex);
}
