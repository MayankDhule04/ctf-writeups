// NIGHTFALL Console — shared client script (login, sidebar, dashboard, audit portal, services)

async function whoami() {
  try {
    const res = await fetch("/api/v1/auth/whoami");
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

// ---- Login page ----
const loginForm = document.getElementById("login-form");
if (loginForm) {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const status = document.getElementById("login-status");
    status.textContent = "Signing in…";
    const res = await fetch("/api/v1/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: document.getElementById("username").value,
        password: document.getElementById("password").value,
      }),
    });
    if (res.ok) {
      window.location.href = "/dashboard.html";
    } else {
      // Deliberately only surfaces the generic error text. The response
      // body also carries a support_token for ticket correlation, but
      // that's not something the UI is supposed to show a user.
      const data = await res.json().catch(() => ({}));
      status.textContent = data.error || "Invalid credentials.";
    }
  });
}

// ---- Shared sidebar ----
// Rendered by JS instead of duplicated per-page so adding a page never
// means re-copy-pasting five sections of nav markup by hand.
const NAV_SECTIONS = [
  {
    heading: "INTELLIGENCE",
    items: [
      { key: "overview", label: "Overview", href: "/dashboard.html" },
      { key: "audit", label: "Audit Ledger", href: "/internal/audit-legacy/", locked: true },
      { key: "investigations", label: "Investigations", locked: true },
    ],
  },
  {
    heading: "MARKETPLACE",
    items: [
      { key: "marketplace-activity", label: "Marketplace Activity", locked: true },
      { key: "accounts", label: "Accounts", locked: true },
      { key: "orders", label: "Orders", locked: true },
      { key: "vendor-ops", label: "Vendor Operations", locked: true },
    ],
  },
  {
    heading: "INFRASTRUCTURE",
    items: [
      { key: "services", label: "Service Registry", href: "/services.html" },
      { key: "service-health", label: "Service Health", locked: true },
      { key: "system-events", label: "System Events", locked: true },
    ],
  },
  {
    heading: "COMMUNICATIONS",
    items: [
      { key: "messages", label: "Messages", locked: true },
      { key: "webhooks", label: "Webhooks", locked: true },
    ],
  },
  {
    heading: "FINANCIAL",
    items: [
      { key: "transactions", label: "Transactions", href: "/transactions.html" },
      { key: "settlement", label: "Settlement Activity", locked: true },
    ],
  },
  {
    heading: "REPORTING",
    items: [
      { key: "reports", label: "Reports", locked: true },
      { key: "exports", label: "Exports", restrictedMsg: "Export management requires export:manage." },
    ],
  },
  {
    heading: "SYSTEM",
    items: [
      { key: "api-clients", label: "API Clients", locked: true },
      { key: "configuration", label: "Configuration", locked: true },
      { key: "access-control", label: "Access Control", locked: true },
    ],
  },
];

// Small always-on-screen notice, reused by anything gated behind a scope
// the current session doesn't carry (nav items, the export button, ...).
function showToast(msg) {
  let toast = document.getElementById("toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "toast";
    document.body.appendChild(toast);
  }
  toast.textContent = msg;
  toast.classList.add("show");
  clearTimeout(showToast._t);
  showToast._t = setTimeout(() => toast.classList.remove("show"), 3000);
}

function renderSidebar(activeKey) {
  const mount = document.getElementById("sidebar-mount");
  if (!mount) return;

  const itemHtml = (item) => {
    // The current page is always reachable regardless of its normal locked
    // state — you're only on it because you already cleared its gate. Every
    // other page still shows the item's real (locked) state, so discovery
    // via robots.txt stays the only path in from elsewhere.
    const isActive = item.key === activeKey;
    const locked = item.locked && !isActive;
    const cls = ["nav-item"];
    if (isActive) cls.push("active");
    if (locked) cls.push("locked");
    const lock = locked ? '<span class="lock" aria-label="Restricted">🔒</span>' : "";
    const title = locked ? ' title="Requires elevated privileges"' : "";
    const restricted = item.restrictedMsg ? ` data-restricted-msg="${item.restrictedMsg}"` : "";
    const href = locked || item.restrictedMsg ? "#" : item.href;
    return `<a class="${cls.join(" ")}" href="${href}"${title}${restricted}>${item.label}${lock}</a>`;
  };

  const sections = NAV_SECTIONS.map((section) => {
    const heading = section.heading ? `<div class="nav-heading">${section.heading}</div>` : "";
    return `<div class="nav-section">${heading}${section.items.map(itemHtml).join("")}</div>`;
  }).join("");

  mount.innerHTML = `
    <div class="logo">
      <div class="mark-icon">N</div>
      <div>
        <div class="mark">NIGHTFALL</div>
        <div class="sub">The Console</div>
      </div>
    </div>
    ${sections}
    <div class="nav-section nav-footer">
      <div class="nav-heading">SYSTEM</div>
      <a class="nav-item locked" href="#" title="Requires elevated privileges">Documentation<span class="lock" aria-label="Restricted">🔒</span></a>
      <a class="nav-item locked" href="#" title="Requires elevated privileges">About<span class="lock" aria-label="Restricted">🔒</span></a>
    </div>
  `;

  mount.querySelectorAll("[data-restricted-msg]").forEach((el) => {
    el.addEventListener("click", (e) => {
      e.preventDefault();
      showToast(el.dataset.restrictedMsg);
    });
  });
}
// esbuild wraps this whole bundle in a non-module IIFE, so top-level
// declarations don't leak to `window` — every page's trailing <script>
// (`renderSidebar("audit")` etc.) needs this to actually reach the function.
window.renderSidebar = renderSidebar;

// ---- Account label (any authenticated page) ----
// Cosmetic only — the JWT's real authorization claim is `scope`, checked
// server-side; this just picks a friendlier display string for `role`.
const ROLE_LABELS = { analyst: "Audit Reader", admin: "Administrator", anonymous: "Guest" };
const accountLabel = document.getElementById("account-label");
if (accountLabel) {
  whoami().then((info) => {
    if (!info) {
      window.location.href = "/";
      return;
    }
    accountLabel.textContent = info.role;
    const avatar = document.getElementById("avatar");
    if (avatar) avatar.textContent = info.role.slice(0, 2).toUpperCase();
    const roleLabel = document.getElementById("account-role-label");
    if (roleLabel) roleLabel.textContent = ROLE_LABELS[info.role] || info.role;
    const scopeEl = document.getElementById("account-scope");
    if (scopeEl) scopeEl.textContent = info.scope || "";
  });
}

// ---- Audit portal: stat cards + activity chart ----
function renderStats(rows) {
  const el = (id) => document.getElementById(id);
  if (!el("stat-total")) return;
  el("stat-total").textContent = rows.length;
  el("stat-admin").textContent = rows.filter((r) => (r.result || "").toLowerCase() === "failure").length;
  el("stat-failed").textContent = rows.filter((r) => (r.severity || "") === "ERROR" || (r.severity || "") === "WARN").length;
  el("stat-actors").textContent = new Set(rows.map((r) => r.actor_id)).size;
}

// Smooth cubic-bezier interpolation through a point series — cheap way to
// get a "wavy" area/line chart with plain inline SVG, no charting library.
function smoothPath(points) {
  if (points.length < 2) return "";
  let d = `M ${points[0].x} ${points[0].y}`;
  for (let i = 1; i < points.length; i++) {
    const prev = points[i - 1], curr = points[i];
    const midX = (prev.x + curr.x) / 2;
    d += ` C ${midX} ${prev.y}, ${midX} ${curr.y}, ${curr.x} ${curr.y}`;
  }
  return d;
}

function renderActivityChart(rows) {
  const svg = document.getElementById("activity-chart");
  if (!svg) return;
  const now = Date.now();
  const BUCKETS = 12; // 2h buckets over the last 24h
  const ok = new Array(BUCKETS).fill(0);
  const fail = new Array(BUCKETS).fill(0);
  rows.forEach((r) => {
    const ageHours = (now - new Date(r.ts).getTime()) / 3_600_000;
    if (ageHours < 0 || ageHours >= 24) return;
    const idx = BUCKETS - 1 - Math.floor(ageHours / 2);
    ((r.result || "").toLowerCase() === "failure" ? fail : ok)[idx]++;
  });

  const w = 640, h = 130, pad = 8;
  const max = Math.max(1, ...ok, ...fail);
  const toPoints = (series) =>
    series.map((v, i) => ({
      x: (i / (BUCKETS - 1)) * (w - pad * 2) + pad,
      y: h - pad - (v / max) * (h - pad * 2),
    }));
  const okPts = toPoints(ok);
  const failPts = toPoints(fail);
  const okLine = smoothPath(okPts);
  const failLine = smoothPath(failPts);
  const okArea = `${okLine} L ${okPts[okPts.length - 1].x} ${h} L ${okPts[0].x} ${h} Z`;

  svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
  svg.innerHTML = `
    <defs>
      <linearGradient id="waveFill" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="var(--accent)" stop-opacity="0.35" />
        <stop offset="100%" stop-color="var(--accent)" stop-opacity="0" />
      </linearGradient>
    </defs>
    <path d="${okArea}" fill="url(#waveFill)" stroke="none" />
    <path d="${okLine}" fill="none" stroke="var(--accent)" stroke-width="2.5" />
    <path d="${failLine}" fill="none" stroke="var(--accent2)" stroke-width="2" stroke-opacity="0.85" />
  `;
}

// ---- Severity breakdown donut ----
function renderSeverityDonut(rows) {
  const svg = document.getElementById("severity-donut");
  const legend = document.getElementById("severity-legend");
  const centerPct = document.getElementById("donut-pct");
  const centerLbl = document.getElementById("donut-lbl");
  if (!svg) return;

  const segments = [
    { key: "CRITICAL", label: "Critical", color: "var(--critical)" },
    { key: "ERROR", label: "Error", color: "var(--danger)" },
    { key: "WARN", label: "Warning", color: "var(--warn)" },
    { key: "INFO", label: "Info", color: "var(--accent)" },
  ];
  const total = rows.length || 1;
  const counts = { CRITICAL: 0, ERROR: 0, WARN: 0, INFO: 0 };
  rows.forEach((r) => {
    counts[r.severity] = (counts[r.severity] || 0) + 1;
  });

  const r = 45, cx = 60, cy = 60, circumference = 2 * Math.PI * r;
  let offset = 0;
  const circles = segments
    .map((seg) => {
      const count = counts[seg.key] || 0;
      const len = (count / total) * circumference;
      const circle = `<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="${seg.color}" stroke-width="14" stroke-dasharray="${len} ${circumference - len}" stroke-dashoffset="${-offset}" transform="rotate(-90 ${cx} ${cy})" />`;
      offset += len;
      return circle;
    })
    .join("");
  svg.setAttribute("viewBox", "0 0 120 120");
  svg.innerHTML = circles;

  const dominant = segments.reduce((a, b) => ((counts[b.key] || 0) > (counts[a.key] || 0) ? b : a));
  const pct = Math.round(((counts[dominant.key] || 0) / total) * 100);
  if (centerPct) centerPct.textContent = `${pct}%`;
  if (centerLbl) centerLbl.textContent = dominant.label;

  if (legend) {
    legend.innerHTML = segments
      .map((seg) => {
        const p = Math.round(((counts[seg.key] || 0) / total) * 100);
        return `<div class="row"><span class="name"><span class="sw" style="background:${seg.color}"></span>${seg.label}</span><span class="pct">${p}%</span></div>`;
      })
      .join("");
  }
}

// ---- Event details drawer ----
function pseudoId(seed, len) {
  let h = 0;
  for (let i = 0; i < seed.length; i++) h = (h * 31 + seed.charCodeAt(i)) >>> 0;
  return h.toString(16).padStart(len, "0").slice(0, len);
}

// Role label + UID are per-ACTOR, not per-event — seeded from actor_id
// alone (not event_id:actor_id) so the same actor reads identically across
// every row in the table, instead of a different pseudo-UID each time.
// Kage specifically needs a stable, narratively-meaningful UID (she's a
// monitored Marketplace Administrator in this story, not the operator).
const ACTOR_INFO = {
  Kage: { role: "Marketplace Administrator", uid: "UID-101" },
  "admin-k.osei": { role: "Platform Administrator" },
  analyst: { role: "Audit Reader" },
};
function actorInfo(actorId) {
  const known = ACTOR_INFO[actorId];
  const isService = actorId.startsWith("svc-") || actorId === "system_cron" || actorId === "waf_service";
  return {
    role: (known && known.role) || (isService ? "Service Account" : "Unknown"),
    uid: (known && known.uid) || `UID-${1000 + (parseInt(pseudoId(actorId, 4), 16) % 9000)}`,
  };
}

function openEventDrawer(row) {
  const drawer = document.getElementById("event-drawer");
  if (!drawer) return;
  const seed = `${row.event_id}:${row.actor_id}`;
  const { role, uid } = actorInfo(row.actor_id);
  document.getElementById("drawer-title").textContent = row.event_type;
  document.getElementById("drawer-body").innerHTML = `
    <div class="drawer-field"><span>Event ID</span><code>EVT-${pseudoId(seed, 8).toUpperCase()}</code></div>
    <div class="drawer-field"><span>Timestamp</span><code>${row.ts}</code></div>
    <div class="drawer-field"><span>Actor</span><code>${row.actor_id}</code></div>
    <div class="drawer-field"><span>Actor UID</span><code>${uid}</code></div>
    <div class="drawer-field"><span>Role</span><code>${role}</code></div>
    <div class="drawer-field"><span>Action</span><code>${row.event_type}</code></div>
    <div class="drawer-field"><span>Resource</span><code>${row.resource || "Audit"}</code></div>
    <div class="drawer-field"><span>Service</span><code>${row.service || "audit-service"}</code></div>
    <div class="drawer-field"><span>Source IP</span><code>10.${parseInt(pseudoId(seed + "a", 2), 16)}.${parseInt(pseudoId(seed + "b", 2), 16)}.${parseInt(pseudoId(seed + "c", 2), 16)}</code></div>
    <div class="drawer-field"><span>Environment</span><code>prod-us-east</code></div>
    <div class="drawer-field"><span>Result</span><code>${row.result || "Success"}</code></div>
    <div class="drawer-field"><span>Metadata</span><pre>{
  "resource": "${row.resource || "Audit"}",
  "service": "${row.service || "audit-service"}"
}</pre></div>
  `;
  drawer.classList.add("open");
}

const drawerClose = document.getElementById("drawer-close");
if (drawerClose) {
  drawerClose.addEventListener("click", () => {
    document.getElementById("event-drawer").classList.remove("open");
  });
}

// High-level data-source category for the Source column — derived
// client-side from event_type rather than stored, since it's purely a
// display grouping (PRD §16) and doesn't gate or inform any vulnerability.
function deriveSource(eventType) {
  const t = eventType || "";
  if (t.startsWith("Authentication") || t.startsWith("Session")) return "Authentication";
  if (t.startsWith("Webhook")) return "Webhook";
  if (t.startsWith("Finance")) return "Transaction";
  if (t.startsWith("Database") || t.startsWith("Cron")) return "Database";
  if (t.startsWith("Config") || t.startsWith("Role") || t.startsWith("Audit")) return "Administration";
  if (t.startsWith("WAF") || t.startsWith("ServiceHealth") || t.startsWith("RateLimit") || t.startsWith("Service.Token") || t.startsWith("Export")) return "Infrastructure";
  return "Marketplace";
}

// ---- Audit portal: recent events table ----
async function loadRecent() {
  const body = document.getElementById("recent-body");
  if (!body) return;
  try {
    const res = await fetch("/api/v1/audit/recent");
    if (res.status === 401) {
      body.innerHTML = `<tr><td colspan="8">Access denied for this account.</td></tr>`;
      renderStats([]);
      return;
    }
    const rows = await res.json();
    const list = Array.isArray(rows) ? rows : [];
    body.innerHTML = list
      .map((r, i) => {
        const failed = (r.result || "").toLowerCase() === "failure";
        const status = `<span class="status-pill ${failed ? "fail" : "ok"}"><span class="sw"></span>${r.result || "—"}</span>`;
        return (
          `<tr data-idx="${i}" class="event-row"><td>${status}</td><td>${new Date(r.ts).toLocaleTimeString()}</td>` +
          `<td><span class="sev sev-${(r.severity || "INFO").toLowerCase()}">${r.severity || "INFO"}</span></td>` +
          `<td>${deriveSource(r.event_type)}</td>` +
          `<td>${r.actor_id}</td><td>${r.event_type}</td><td>${r.resource || "—"}</td>` +
          `<td>${r.service || "—"}</td></tr>`
        );
      })
      .join("");
    body.querySelectorAll("tr.event-row").forEach((tr) => {
      tr.addEventListener("click", () => openEventDrawer(list[Number(tr.dataset.idx)]));
    });
    renderStats(list);
    renderActivityChart(list);
    renderSeverityDonut(list);
  } catch {
    body.innerHTML = `<tr><td colspan="8">Unable to load recent events.</td></tr>`;
  }
}

// ---- Audit portal / legacy interface: search ----
async function runSearch(q) {
  const status = document.getElementById("search-status");
  status.textContent = "Submitting…";
  const res = await fetch(`/api/v1/audit/search?filter=${encodeURIComponent(q)}`);
  if (res.status === 401) {
    status.textContent = "Access denied for this account.";
    return;
  }
  const data = await res.json();
  status.textContent = data.message || "Query submitted.";
}

const searchForm = document.getElementById("search-form");
if (searchForm) {
  searchForm.addEventListener("submit", (e) => {
    e.preventDefault();
    runSearch(document.getElementById("filter-input").value);
  });
}
if (document.getElementById("recent-body")) {
  loadRecent();
}

// ---- Audit portal: Advanced Search toggle (decorative — same search underneath) ----
const advancedToggle = document.getElementById("advanced-toggle");
if (advancedToggle) {
  advancedToggle.addEventListener("click", () => {
    document.getElementById("advanced-panel").classList.toggle("open");
  });
}
const advancedRun = document.getElementById("advanced-run");
if (advancedRun) {
  advancedRun.addEventListener("click", (e) => {
    e.preventDefault();
    runSearch(document.getElementById("filter-input").value);
  });
}

// ---- Audit portal: Saved Searches (static list, clicking pre-fills + runs) ----
document.querySelectorAll(".saved-search-row").forEach((row) => {
  row.addEventListener("click", () => {
    const q = row.dataset.query || "";
    const input = document.getElementById("filter-input");
    if (input) input.value = q;
    runSearch(q);
  });
});

// ---- Audit portal: Export Results dropdown (scope-gated message only) ----
const exportResultsBtn = document.getElementById("export-results-btn");
if (exportResultsBtn) {
  exportResultsBtn.addEventListener("click", async () => {
    const status = document.getElementById("export-results-status");
    const info = await whoami();
    const scopes = (info && info.scope) || "";
    if (scopes.split(" ").includes("audit:export")) {
      status.textContent = "Export queued.";
    } else {
      status.textContent = "Export requires: audit:export";
    }
  });
}

// V2 feature — internal PDF worker webhook, disabled until GA
const exportBtn = document.getElementById("export-pdf-btn");
if (exportBtn) {
  exportBtn.addEventListener("click", () => {
    fetch("/api/internal/export-job", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Nightfall-Hub-Signature": computeSig(payload) },
      body: JSON.stringify({ job_metadata: btoa(JSON.stringify({ report: "full-audit" })) }),
    });
  });
}

// V2 feature — generic artifact retrieval, not wired to any live control
// (no "artifact-download-btn" element exists in the current HTML, same
// disabled-until-GA pattern as exportBtn above). Reveals the download
// API's shape (/api/v1/artifacts/{ref}/download) to anyone reading this
// file, but never a real `ref` — those live only in export-worker's own
// .manifest, reachable only after Stage 2's RCE.
async function downloadArtifact(ref) {
  const response = await fetch(`/api/v1/artifacts/${encodeURIComponent(ref)}/download`);
  if (!response.ok) {
    throw new Error("Artifact unavailable");
  }
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "";
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}
const artifactDownloadBtn = document.getElementById("artifact-download-btn");
if (artifactDownloadBtn) {
  artifactDownloadBtn.addEventListener("click", () => downloadArtifact(artifactDownloadBtn.dataset.ref));
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

// Reuses the event-drawer's field-row look (console.css .drawer-field) so
// a transaction reads the same as an audit event, not a raw JSON dump.
function renderTxFields(row) {
  const fields = [
    ["Transaction ID", row.transaction_id], ["Type", row.type], ["Status", row.status],
    ["Amount (BTC)", row.amount_btc], ["From", row.from_wallet], ["To", row.to_wallet],
    ["Operator UID", row.operator_uid], ["Memo", row.memo], ["BTC TXID", row.btc_txid],
    ["Block Height", row.block_height], ["Confirmations", row.confirmations],
    ["Created", row.created_at], ["Audit Note", row.audit_note],
  ].filter(([, v]) => v !== null && v !== undefined);
  return fields
    .map(([label, value]) => `<div class="drawer-field"><span>${label}</span><code>${escapeHtml(value)}</code></div>`)
    .join("");
}

function renderTxBanner(msg) {
  return `<div class="banner">${escapeHtml(msg)}</div>`;
}

// Transactions lookup (/transactions.html). Server-side gated on
// finance:audit (or finance:read/admin) — see app.py get_transaction().
// No ownership check on which transaction_id a given session may name —
// that's the deliberate BOLA (DEVELOPER_ADDENDUM.md §6).
const txLookupBtn = document.getElementById("tx-lookup-btn");
if (txLookupBtn) {
  txLookupBtn.addEventListener("click", async () => {
    const id = document.getElementById("tx-lookup-input").value;
    const status = document.getElementById("tx-lookup-status");
    status.innerHTML = "";
    // {"view": {"summary": true}} is the only view this client ever sends
    // — see app.py's TransactionView/get_transaction() for why sending
    // more keys in that object matters.
    const res = await fetch(`/api/v1/transactions/${encodeURIComponent(id)}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ view: { summary: true } }),
    });
    if (res.status === 401) {
      // Echo the server's own RFC 6750 challenge rather than hardcoding a
      // scope name here — this is the only place that string should live.
      const auth = res.headers.get("WWW-Authenticate") || "";
      const scope = auth.match(/scope="([^"]+)"/);
      status.innerHTML = renderTxBanner(scope ? `Requires: ${scope[1]}` : "Unauthorized");
      return;
    }
    const data = await res.json();
    status.innerHTML = res.ok ? renderTxFields(data) : renderTxBanner(data.error || "Request failed");
  });
}

// ---- Services page ----
const exportServiceToggle = document.getElementById("export-service-toggle");
if (exportServiceToggle) {
  exportServiceToggle.addEventListener("click", () => {
    document.getElementById("export-service-card").classList.toggle("open");
  });
}

// Live registry data from GET /api/v1/services — deliberately filtered
// server-side to visibility='public', so the internal research-agent row
// never appears here no matter what this code does (see app.py's services()).
async function loadServices() {
  const mount = document.getElementById("service-list");
  if (!mount) return;
  try {
    const res = await fetch("/api/v1/services");
    if (!res.ok) return;
    const rows = await res.json();
    mount.innerHTML = rows
      .map(
        (s) => `
      <div class="service-card">
        <h3>${s.service_name}</h3>
        <div class="service-status"><span class="dot"></span>${s.status === "active" ? "Healthy" : s.status}</div>
        <div class="service-meta">Type: ${s.integration_type}</div>
        ${s.notes ? `<div class="service-meta">${s.notes}</div>` : ""}
      </div>`
      )
      .join("");
  } catch {
    // Registry is decorative noise beyond the two pinned cards above — a
    // failed fetch just leaves this section empty, nothing else depends on it.
  }
}
loadServices();
