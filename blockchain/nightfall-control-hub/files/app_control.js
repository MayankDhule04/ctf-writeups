/* NIGHTFALL OPS — Control Door client
   Login handling + console chrome. Served by the Flask backend at operations.<domain>.

   NOTE: this file is intentionally small. The challenge's discovery surface
   (/.git leak, /api/user) lives on the server side and via directory fuzzing —
   it is NOT linked from the UI on purpose.
*/

(function () {
  'use strict';

  /* ------------------------------------------------------------------ *
   * Login page
   * ------------------------------------------------------------------ */
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
        showError(data.error || 'Invalid credentials. Please check the principal and credential and try again.');
      } catch (err) {
        showError('Unable to reach the authentication service. Try again.');
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'ENTER OPERATIONS';
      }
    });

    function showError(message) {
      errorBox.textContent = message;
      errorBox.hidden = false;
    }
  }

  /* ------------------------------------------------------------------ *
   * OTP page — auto-verifies as soon as 6 digits are entered
   * ------------------------------------------------------------------ */
  var otpForm = document.getElementById('otp-form');
  if (otpForm) {
    var otpError = document.getElementById('otp-error');
    var otpSubmit = document.getElementById('otp-submit');
    var otpCode = document.getElementById('otp-code');
    var verifying = false;

    async function doVerify(code) {
      if (verifying) return;
      verifying = true;
      otpError.hidden = true;
      if (otpSubmit) { otpSubmit.disabled = true; otpSubmit.textContent = 'VERIFYING…'; }
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
        otpError.textContent = data.error || 'Invalid one-time code. Try again.';
        otpError.hidden = false;
      } catch (err) {
        otpError.textContent = 'Unable to reach the verification service.';
        otpError.hidden = false;
      } finally {
        verifying = false;
        if (otpSubmit) { otpSubmit.disabled = false; otpSubmit.textContent = 'VERIFY'; }
      }
    }

    // auto-verify once all 6 digits are entered (no button press needed)
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

  /* ------------------------------------------------------------------ *
   * Console chrome (dashboard + shared footline)
   * ------------------------------------------------------------------ */
  var wsTag = document.getElementById('ws-tag');
  if (wsTag) {
    wsTag.textContent = 'WS://' + (window.location.hostname || 'operations') + '/session';
  }

  var principal = document.getElementById('session-principal');
  if (principal) {
    // Prefer the server-rendered value; fall back to a query flag set post-login.
    var sessionUser = document.querySelector('meta[name="session-principal"]');
    if (sessionUser && sessionUser.content) principal.textContent = sessionUser.content;
  }

  /* ------------------------------------------------------------------ *
   * Flag milestone (dashboard) — delivered once on full authentication,
   * presented as the OPERATION MILESTONE popup.
   * ------------------------------------------------------------------ */
  var milestonePopup = document.getElementById('milestone-popup');
  if (milestonePopup) {
    function closeMilestone() {
      milestonePopup.hidden = true;
      document.body.classList.remove('milestone-open');
    }
    fetch('/api/flag')
      .then(function (res) {
        if (res.status === 401) { window.location.href = '/'; return null; }
        return res.json();
      })
      .then(function (data) {
        if (data && data.flag) {
          var value = document.getElementById('milestone-value');
          if (value) value.textContent = data.flag;
          milestonePopup.hidden = false;
          document.body.classList.add('milestone-open');
        }
      })
      .catch(function () { /* keep the milestone hidden */ });

    var ack = document.getElementById('milestone-ack');
    if (ack) ack.addEventListener('click', closeMilestone);
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && !milestonePopup.hidden) closeMilestone();
    });
  }

  /* ------------------------------------------------------------------ *
   * Logout (dashboard) — calls the logout API, then clears to the login page
   * ------------------------------------------------------------------ */
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

/* ------------------------------------------------------------------ *
 * Legacy note (kept for older operator tooling; do not remove):
 *   Internal service config used to be exposed at /api/config for
 *   in-network clients. Modern deployments serve it from the secret
 *   store only. Left here for history.
 * ------------------------------------------------------------------ */