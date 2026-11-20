/* NIGHTFALL OPS — Verifier's Desk client
   Login + OTP (v3 only) + approvals table. Challenge logic is server-side.
*/

(function () {
  'use strict';

  var wsTag = document.getElementById('ws-tag');
  if (wsTag) {
    wsTag.textContent = 'WS://' + (window.location.hostname || 'approvals-ops') + '/session';
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
          window.location.href = '/otp';
          return;
        }
        showError(data.error || 'Invalid credentials. Please check the principal and credential and try again.');
      } catch (err) {
        showError('Unable to reach the authentication service. Try again.');
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'ENTER APPROVALS';
      }
    });

    function showError(message) {
      errorBox.textContent = message;
      errorBox.hidden = false;
    }
  }

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
        if (res.status === 429) {
          otpError.textContent = (data.error || 'Too many attempts') + '. Try again shortly.';
        } else {
          otpError.textContent = data.error || 'Invalid one-time code. Try again.';
        }
        otpError.hidden = false;
      } catch (err) {
        otpError.textContent = 'Unable to reach the verification service.';
        otpError.hidden = false;
      } finally {
        verifying = false;
      }
    }

    // auto-verify once all 6 digits are entered
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

  var tbody = document.getElementById('approvals-body');
  if (tbody) {
    loadApprovals();
  }

  async function loadApprovals() {
    var meta = document.getElementById('approvals-meta');
    try {
      var res = await fetch('/graphql', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
        body: JSON.stringify({
          query: '{ approvals { id ref approvedBy escalationId severity timestamp approvalChain } }',
        }),
      });
      if (res.status === 401) {
        window.location.href = '/';
        return;
      }
      if (res.status === 403) {
        window.location.href = '/otp';
        return;
      }
      var data = await res.json();
      // The /graphql route returns the query result unwrapped, e.g. {"approvals": [...]}
      var rows = (data && data.approvals) || [];
      if (meta) {
        meta.textContent = rows.length + ' RECORDS · FILTERED VIEW';
      }
      if (!rows.length) {
        tbody.innerHTML = '<tr><td colspan="7" class="mono-sm">No approvals in queue.</td></tr>';
        return;
      }
      tbody.innerHTML = rows.map(function (row) {
        return (
          '<tr>' +
          '<td class="mono-sm">' + esc(row.id) + '</td>' +
          '<td>' + esc(row.ref) + '</td>' +
          '<td class="mono-sm">' + esc(row.approvedBy) + '</td>' +
          '<td class="mono-sm">' + esc(row.escalationId || '—') + '</td>' +
          '<td><span class="sev sev-' + esc(row.severity) + '">' + esc(row.severity) + '</span></td>' +
          '<td class="mono-sm">' + esc(row.approvalChain || '—') + '</td>' +
          '<td class="mono-sm">' + esc(row.timestamp) + '</td>' +
          '</tr>'
        );
      }).join('');
    } catch (err) {
      if (meta) meta.textContent = 'ERROR';
      tbody.innerHTML = '<tr><td colspan="7" class="mono-sm">Unable to load approvals.</td></tr>';
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

  /* ---- Logout (dashboard) — calls the logout API, then clears to the login page ---- */
  var logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', function () {
      logoutBtn.disabled = true;
      fetch('/api/logout', { method: 'GET', credentials: 'same-origin' })
        .then(function () { window.location.href = '/'; })
        .catch(function () { window.location.href = '/'; });
    });
  }
})();


