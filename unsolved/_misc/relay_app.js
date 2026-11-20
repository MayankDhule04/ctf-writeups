/* Continuity — operator console (read-only).
 *
 * A single-page client over the relay's JSON API. It reads three endpoints —
 * /api/relay/status, /api/relay/events, /api/incidents — and derives every
 * view (captures, recovery jobs, incident activity, timelines) deterministically
 * from that data. It performs NO privileged actions: it never opens captures,
 * stores notes, or runs recovery previews. Those are operator-API actions,
 * documented in the handout and driven by operator tooling.
 *
 * No external resources are loaded (the instance has no egress).
 */
'use strict';

/* ----------------------------- data layer ------------------------------ */

const STATE = {
  status: null,
  events: [],
  incidents: null,
  derived: { captures: {}, notes: {}, recovery: [] },
  loading: true,
  error: null,
  lastUpdated: null,
  online: false,
};

async function getJSON(path) {
  const r = await fetch(path, { headers: { Accept: 'application/json' } });
  if (!r.ok && r.status >= 500) throw new Error(`${path} -> ${r.status}`);
  return r.json();
}

function derive(events) {
  const captures = {};
  const notes = {};
  const recovery = [];
  for (const e of events) {
    switch (e.type) {
      case 'CAPTURE_OPEN':
        captures[e.request_id] = {
          request_id: e.request_id, slot: e.slot, epoch: e.epoch,
          status: 'open', descriptor: 'pending',
          incident: e.incident || null, seq: e.seq, endSeq: null,
        };
        break;
      case 'CAPTURE_COMMIT':
        if (captures[e.request_id]) Object.assign(captures[e.request_id],
          { status: 'committed', descriptor: 'retired', endSeq: e.seq });
        break;
      case 'CAPTURE_INTERRUPT':
        if (captures[e.request_id]) Object.assign(captures[e.request_id],
          { status: 'interrupted', descriptor: 'retained', endSeq: e.seq });
        break;
      case 'NOTE_STORE':
        notes[e.note_id] = {
          note_id: e.note_id, slot: e.slot, epoch: e.epoch,
          bytes: e.bytes, trust: e.trust || 'untrusted', status: 'stored',
          seq: e.seq, endSeq: null,
        };
        break;
      case 'NOTE_DISCARD':
        if (notes[e.note_id]) Object.assign(notes[e.note_id],
          { status: 'discarded', endSeq: e.seq });
        break;
      case 'RECOVER_PREVIEW':
        recovery.push({
          request_id: e.request_id, descriptor_epoch: e.descriptor_epoch,
          slot: e.slot, occupant_epoch: e.occupant_epoch,
          occupant: e.occupant, seq: e.seq,
        });
        break;
      default: break;
    }
  }
  return { captures, notes, recovery };
}

function signature() {
  const s = STATE.status;
  const last = STATE.events.length ? STATE.events[STATE.events.length - 1].seq : 0;
  return [
    STATE.events.length, last, STATE.error ? 'E' : 'ok',
    s ? JSON.stringify(s.slots) : '-',
    s ? s.captures_open : '-', s ? s.notes_stored : '-',
    STATE.incidents ? 'i' : '-',
  ].join('|');
}

let lastSig = '';

async function fetchAll() {
  try {
    const [status, eventsResp, incidents] = await Promise.all([
      getJSON('/api/relay/status'),
      getJSON('/api/relay/events'),
      getJSON('/api/incidents').catch(() => null),
    ]);
    STATE.status = status;
    STATE.events = Array.isArray(eventsResp.events) ? eventsResp.events : [];
    STATE.incidents = incidents;
    STATE.derived = derive(STATE.events);
    STATE.error = null;
    STATE.online = true;
  } catch (err) {
    STATE.error = err.message || 'relay unreachable';
    STATE.online = false;
  } finally {
    STATE.loading = false;
    STATE.lastUpdated = new Date();
  }
}

/* --------------------------- small helpers ----------------------------- */

function esc(v) {
  return String(v == null ? '' : v).replace(/[&<>"']/g, (c) => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
  ));
}
const $ = (sel, root = document) => root.querySelector(sel);
const activeIncidentId = () =>
  (STATE.incidents && STATE.incidents.active_incident) ||
  (STATE.status && STATE.status.incident) || null;

function captureBadge(c) {
  if (c.status === 'committed') return `<span class="badge ok plain">committed</span>`;
  if (c.status === 'interrupted') return `<span class="badge warn plain">interrupted</span>`;
  return `<span class="badge info plain">open</span>`;
}
function descriptorBadge(d) {
  if (d === 'retired') return `<span class="badge neutral plain">retired</span>`;
  if (d === 'retained') return `<span class="badge amber plain">retained</span>`;
  return `<span class="badge info plain">pending</span>`;
}
function occupantBadge(o) {
  if (o === 'free' || o == null) return `<span class="badge neutral plain">free</span>`;
  if (o === 'note') return `<span class="badge warn plain">note</span>`;
  return `<span class="badge info plain">capture</span>`;
}

const EVENT_META = {
  CAPTURE_OPEN:      { label: 'Capture opened', tone: 'info' },
  CAPTURE_COMMIT:    { label: 'Capture committed', tone: 'ok' },
  CAPTURE_INTERRUPT: { label: 'Capture interrupted', tone: 'warn' },
  NOTE_STORE:        { label: 'Note stored', tone: 'warn' },
  NOTE_DISCARD:      { label: 'Note discarded', tone: 'ok' },
  RECOVER_PREVIEW:   { label: 'Recovery preview', tone: 'danger' },
};

function eventDetail(e) {
  const skip = new Set(['seq', 'type']);
  return Object.entries(e)
    .filter(([k]) => !skip.has(k))
    .map(([k, v]) => `<b>${esc(k)}</b>=${esc(v)}`)
    .join('  ');
}

/* interrupted captures whose descriptor was retained and whose slot has since
 * been recycled to a higher epoch — the operational inconsistency an
 * investigator is asked to assess. Derived purely from recorded state. */
function staleHandles() {
  const out = [];
  const slots = STATE.status ? STATE.status.slots : [];
  for (const c of Object.values(STATE.derived.captures)) {
    if (c.status !== 'interrupted' || c.descriptor !== 'retained') continue;
    const slot = slots.find((s) => s.slot === c.slot);
    const recycled = slot ? slot.epoch > c.epoch : false;
    out.push({ ...c, currentEpoch: slot ? slot.epoch : null, recycled });
  }
  return out;
}

/* ------------------------------- views --------------------------------- */

function stateBlock() {
  if (STATE.loading) {
    return `<div class="loading">Loading relay state…</div>`;
  }
  if (STATE.error) {
    return `<div class="error-box">
      <div class="title">Relay unreachable</div>
      <div>The operator API did not respond (${esc(STATE.error)}). The console will
      keep retrying; use <em>Refresh</em> to retry now.</div></div>`;
  }
  return null;
}

function viewDashboard() {
  const s = STATE.status;
  const d = STATE.derived;
  const captures = Object.values(d.captures);
  const stale = staleHandles();
  const freeSlots = s.slots.filter((x) => x.occupant === 'free').length;

  const attn = stale.length
    ? `<div class="banner">
        <span class="b-ico" aria-hidden="true">⚠</span>
        <span class="b-body"><b>Recovery integrity — attention.</b>
        ${stale.length} capture${stale.length > 1 ? 's were' : ' was'} interrupted with the
        recovery descriptor <b>retained</b>${stale.some((x) => x.recycled)
          ? `, and the affected work slot has since been <b>recycled</b> to a new occupant` : ''}.
        Interrupted recovery state is reconciled from the audit trail — review the affected
        captures and the recovery path below.</span></div>`
    : '';

  const recentEvents = STATE.events.slice(-8).reverse();

  return `
    <div class="page-head"><div class="page-head-row">
      <div>
        <h1>Operations overview</h1>
        <p class="lede">Live state of the Continuity Relay evidence buffer for the active
        incident, with recent operator activity reconciled from the audit trail.</p>
      </div>
    </div></div>

    ${attn}

    <div class="grid cols-4" style="margin-bottom:18px">
      <div class="stat accent"><div class="k">Active incident</div>
        <div class="v" style="font-size:19px">${esc(activeIncidentId() || '—')}</div>
        <div class="d">evidence custody open</div></div>
      <div class="stat"><div class="k">Work slots free</div>
        <div class="v">${freeSlots}<span class="faint" style="font-size:15px">/${s.slot_count}</span></div>
        <div class="d">reusable buffer pool</div></div>
      <div class="stat"><div class="k">Captures open</div>
        <div class="v">${s.captures_open}</div>
        <div class="d">${captures.length} recorded total</div></div>
      <div class="stat ${stale.length ? 'attn' : ''}"><div class="k">Retained descriptors</div>
        <div class="v">${stale.length}</div>
        <div class="d">interrupted, not retired</div></div>
    </div>

    <div class="grid cols-2">
      <div class="panel">
        <div class="panel-head"><h2>Work-slot pool</h2>
          <span class="sub">${s.notes_stored} note${s.notes_stored === 1 ? '' : 's'} stored</span></div>
        <div class="panel-body flush"><div class="tbl-wrap">
          <table class="tbl"><thead><tr><th>Slot</th><th>Epoch</th><th>Occupant</th></tr></thead><tbody>
          ${s.slots.map((x) => `<tr>
            <td class="mono">slot ${x.slot}</td>
            <td class="mono">${x.epoch}</td>
            <td>${occupantBadge(x.occupant)}</td></tr>`).join('')}
          </tbody></table></div></div>
      </div>

      <div class="panel">
        <div class="panel-head"><h2>Recent activity</h2>
          <a class="sub" href="#/events">View full timeline →</a></div>
        <div class="panel-body">
          ${recentEvents.length ? `<div class="timeline">
            ${recentEvents.map((e) => {
              const m = EVENT_META[e.type] || { label: e.type, tone: 'info' };
              return `<div class="tl-item ${m.tone}">
                <div class="tl-head"><span class="tl-type">${esc(m.label)}</span>
                <span class="tl-seq">#${esc(e.seq)}</span></div>
                <div class="tl-detail">${eventDetail(e)}</div></div>`;
            }).join('')}
          </div>` : `<div class="empty"><div class="hint">No activity recorded yet.</div></div>`}
        </div>
      </div>
    </div>`;
}

let incidentFilter = { q: '', state: 'all' };

function viewIncidents() {
  const reg = STATE.incidents ? STATE.incidents.incidents : [];
  const q = incidentFilter.q.trim().toLowerCase();
  const rows = reg.filter((i) => {
    if (incidentFilter.state !== 'all' && i.state !== incidentFilter.state) return false;
    if (!q) return true;
    return (`${i.id} ${i.title} ${i.disposition} ${i.summary}`).toLowerCase().includes(q);
  });

  const stateBtn = (val, label) =>
    `<button data-filter-state="${val}" class="${incidentFilter.state === val ? 'on' : ''}">${label}</button>`;

  return `
    <div class="page-head">
      <h1>Incident register</h1>
      <p class="lede">Incidents known to the relay. Select an incident to review its custody
      disposition and the relay activity recorded against it.</p>
    </div>

    <div class="toolbar">
      <div class="field search"><input id="inc-q" type="search" placeholder="Search incidents…"
        value="${esc(incidentFilter.q)}" autocomplete="off"></div>
      <div class="seg">${stateBtn('all', 'All')}${stateBtn('active', 'Active')}${stateBtn('closed', 'Closed')}</div>
      <span class="spacer"></span>
      <span class="result-count">${rows.length} of ${reg.length}</span>
    </div>

    <div class="panel"><div class="panel-body flush">
      ${rows.length ? `<div class="tbl-wrap"><table class="tbl">
        <thead><tr><th>Incident</th><th>Title</th><th>State</th><th>Custody</th><th>Severity</th><th>Updated</th></tr></thead>
        <tbody>
        ${rows.map((i) => `<tr class="clickable" data-nav="#/incidents/${encodeURIComponent(i.id)}">
          <td class="mono">${esc(i.id)}</td>
          <td>${esc(i.title)}<span class="sub">${esc(i.owner)}</span></td>
          <td>${i.state === 'active' ? '<span class="badge info">active</span>' : '<span class="badge neutral">closed</span>'}</td>
          <td>${i.disposition === 'sealed' ? '<span class="badge amber">sealed</span>' : '<span class="badge ok">cleared</span>'}</td>
          <td><span class="badge ${i.severity === 'high' ? 'danger' : 'neutral'} plain">${esc(i.severity)}</span></td>
          <td class="mono">${esc(i.updated)}</td></tr>`).join('')}
        </tbody></table></div>`
      : `<div class="empty"><div class="empty-ico">◎</div>
          <div class="title">No matching incidents</div>
          <div class="hint">No incident matches the current search and filter.</div></div>`}
    </div></div>`;
}

function viewIncidentDetail(id) {
  const reg = STATE.incidents ? STATE.incidents.incidents : [];
  const inc = reg.find((i) => i.id === id);
  if (!inc) {
    return `<a class="back-link" href="#/incidents">← Incidents</a>
      <div class="empty"><div class="empty-ico">◌</div>
      <div class="title">Incident not found</div>
      <div class="hint">No incident <span class="tag">${esc(id)}</span> is registered on this relay.</div></div>`;
  }

  const isActive = inc.id === activeIncidentId();
  const caps = isActive ? Object.values(STATE.derived.captures) : [];
  const recov = isActive ? STATE.derived.recovery : [];
  const stale = isActive ? staleHandles() : [];

  const capsTable = caps.length ? `<div class="tbl-wrap"><table class="tbl">
      <thead><tr><th>Request</th><th>Slot</th><th>Epoch</th><th>Status</th><th>Descriptor</th></tr></thead>
      <tbody>${caps.map((c) => `<tr>
        <td class="mono">${esc(c.request_id)}</td>
        <td class="mono">slot ${esc(c.slot)}</td>
        <td class="mono">${esc(c.epoch)}</td>
        <td>${captureBadge(c)}</td>
        <td>${descriptorBadge(c.descriptor)}</td></tr>`).join('')}</tbody></table></div>`
    : `<div class="empty"><div class="hint">No evidence captures recorded against this incident.</div></div>`;

  return `
    <a class="back-link" href="#/incidents">← Incidents</a>
    <div class="page-head"><div class="page-head-row">
      <div>
        <h1>${esc(inc.id)} <span class="faint" style="font-weight:500">·</span>
          ${inc.disposition === 'sealed' ? '<span class="badge amber">sealed</span>' : '<span class="badge ok">cleared</span>'}</h1>
        <p class="lede">${esc(inc.title)}</p>
      </div>
    </div></div>

    ${stale.length ? `<div class="banner"><span class="b-ico">⚠</span>
      <span class="b-body"><b>Recovery state inconsistency recorded.</b> An interrupted capture
      retained its recovery descriptor while its work slot was recycled. The custody seal for this
      incident is retained — review the recovery path integrity below.</span></div>` : ''}

    <div class="grid cols-2">
      <div class="panel"><div class="panel-head"><h2>Case record</h2></div>
        <div class="panel-body"><dl class="kv">
          <dt>State</dt><dd>${inc.state === 'active' ? '<span class="badge info">active</span>' : '<span class="badge neutral">closed</span>'}</dd>
          <dt>Disposition</dt><dd>${esc(inc.disposition)}</dd>
          <dt>Custody</dt><dd>${esc(inc.custody)}</dd>
          <dt>Filed artifact</dt><dd><span class="tag">${esc(inc.artifact)}</span></dd>
          <dt>Severity</dt><dd>${esc(inc.severity)}</dd>
          <dt>Owner</dt><dd>${esc(inc.owner)}</dd>
          <dt>Opened</dt><dd class="mono">${esc(inc.opened)}</dd>
          <dt>Updated</dt><dd class="mono">${esc(inc.updated)}</dd>
        </dl></div></div>

      <div class="panel"><div class="panel-head"><h2>Summary</h2></div>
        <div class="panel-body"><p style="margin:0;color:var(--ink-2)">${esc(inc.summary)}</p>
        ${isActive ? `<hr class="div">
          <div class="grid cols-3">
            <div><div class="k faint" style="font-size:11px;text-transform:uppercase;letter-spacing:.7px">Captures</div>
              <div class="mono" style="font-size:19px;margin-top:4px">${caps.length}</div></div>
            <div><div class="k faint" style="font-size:11px;text-transform:uppercase;letter-spacing:.7px">Recovery jobs</div>
              <div class="mono" style="font-size:19px;margin-top:4px">${recov.length}</div></div>
            <div><div class="k faint" style="font-size:11px;text-transform:uppercase;letter-spacing:.7px">Retained desc.</div>
              <div class="mono" style="font-size:19px;margin-top:4px;color:var(--amber-2)">${stale.length}</div></div>
          </div>` : ''}
        </div></div>
    </div>

    <div class="panel"><div class="panel-head"><h2>Evidence captures</h2>
      <a class="sub" href="#/captures">All captures →</a></div>
      <div class="panel-body flush">${capsTable}</div></div>`;
}

function viewCaptures() {
  const caps = Object.values(STATE.derived.captures).sort((a, b) => b.seq - a.seq);
  return `
    <div class="page-head">
      <h1>Evidence captures</h1>
      <p class="lede">Every evidence capture the relay recorded, with its work slot, generation
      epoch, outcome, and recovery-descriptor disposition. A committed capture retires its
      descriptor; an interrupted capture retains it.</p>
    </div>

    <div class="panel"><div class="panel-body flush">
      ${caps.length ? `<div class="tbl-wrap"><table class="tbl">
        <thead><tr><th>Request</th><th>Slot</th><th>Epoch</th><th>Outcome</th><th>Descriptor</th><th>Incident</th></tr></thead>
        <tbody>${caps.map((c) => `<tr>
          <td class="mono">${esc(c.request_id)}</td>
          <td class="mono">slot ${esc(c.slot)}</td>
          <td class="mono">${esc(c.epoch)}</td>
          <td>${captureBadge(c)}</td>
          <td>${descriptorBadge(c.descriptor)}</td>
          <td class="mono">${esc(c.incident || activeIncidentId() || '—')}</td></tr>`).join('')}
        </tbody></table></div>`
      : `<div class="empty"><div class="empty-ico">▤</div>
          <div class="title">No captures recorded</div>
          <div class="hint">Evidence captures opened through the operator API will appear here.</div></div>`}
    </div></div>`;
}

function viewRecovery() {
  const recov = STATE.derived.recovery.slice().sort((a, b) => b.seq - a.seq);
  return `
    <div class="page-head">
      <h1>Recovery jobs</h1>
      <p class="lede">Recovery previews reconstructed from the audit trail. Each row shows the
      epoch the descriptor was bound to versus the epoch of the slot occupant at preview time —
      an epoch mismatch indicates the slot was recycled after the descriptor was issued.</p>
    </div>

    <div class="panel"><div class="panel-body flush">
      ${recov.length ? `<div class="tbl-wrap"><table class="tbl">
        <thead><tr><th>Request</th><th>Slot</th><th>Descriptor epoch</th><th>Occupant epoch</th><th>Occupant</th><th>Match</th></tr></thead>
        <tbody>${recov.map((r) => {
          const mismatch = r.descriptor_epoch !== r.occupant_epoch;
          return `<tr>
            <td class="mono">${esc(r.request_id)}</td>
            <td class="mono">slot ${esc(r.slot)}</td>
            <td class="mono">${esc(r.descriptor_epoch)}</td>
            <td class="mono">${esc(r.occupant_epoch)}</td>
            <td>${occupantBadge(r.occupant)}</td>
            <td>${mismatch ? '<span class="badge amber plain">recycled slot</span>'
                           : '<span class="badge ok plain">matched</span>'}</td></tr>`;
        }).join('')}</tbody></table></div>`
      : `<div class="empty"><div class="empty-ico">↻</div>
          <div class="title">No recovery jobs yet</div>
          <div class="hint">Recovery previews run through the operator API will be reconciled here
          from the audit trail.</div></div>`}
    </div></div>`;
}

let eventFilter = { q: '', type: 'all' };

function viewEvents() {
  const types = ['all', ...Object.keys(EVENT_META)];
  const q = eventFilter.q.trim().toLowerCase();
  const all = STATE.events.slice().reverse().filter((e) => {
    if (eventFilter.type !== 'all' && e.type !== eventFilter.type) return false;
    if (!q) return true;
    return JSON.stringify(e).toLowerCase().includes(q);
  });

  return `
    <div class="page-head">
      <h1>Event timeline</h1>
      <p class="lede">The relay audit trail — the primary source of truth for what the relay did
      and in what order. Most recent first.</p>
    </div>

    <div class="toolbar">
      <div class="field search"><input id="evt-q" type="search" placeholder="Search events…"
        value="${esc(eventFilter.q)}" autocomplete="off"></div>
      <div class="field"><select id="evt-type">
        ${types.map((t) => `<option value="${t}" ${eventFilter.type === t ? 'selected' : ''}>${
          t === 'all' ? 'All event types' : esc((EVENT_META[t] && EVENT_META[t].label) || t)}</option>`).join('')}
      </select></div>
      <span class="spacer"></span>
      <span class="result-count">${all.length} event${all.length === 1 ? '' : 's'}</span>
    </div>

    <div class="panel"><div class="panel-body">
      ${all.length ? `<div class="timeline">
        ${all.map((e) => {
          const m = EVENT_META[e.type] || { label: e.type, tone: 'info' };
          return `<div class="tl-item ${m.tone}">
            <div class="tl-head"><span class="tl-type">${esc(m.label)}</span>
              <span class="tag">${esc(e.type)}</span>
              <span class="tl-seq">#${esc(e.seq)}</span></div>
            <div class="tl-detail">${eventDetail(e)}</div></div>`;
        }).join('')}
      </div>` : `<div class="empty"><div class="empty-ico">≣</div>
        <div class="title">No matching events</div>
        <div class="hint">No audit event matches the current search and filter.</div></div>`}
    </div></div>`;
}

function viewDiagnostics() {
  const recov = STATE.derived.recovery.slice().sort((a, b) => b.seq - a.seq);
  return `
    <div class="page-head">
      <h1>Diagnostics</h1>
      <p class="lede">The relay's recovery preview exposes a restricted, read-only diagnostic
      surface over an in-universe virtual map. It is a closed simulation: it launches no operating-system
      commands, spawns no subprocesses, and touches no real filesystem or network.</p>
    </div>

    <div class="banner info"><span class="b-ico">ℹ</span>
      <span class="b-body">Diagnostic previews are <b>initiated through the operator API</b>
      (recovery preview), not from this console. This page documents the diagnostic surface and
      surfaces the recorded outcomes of recovery jobs.</span></div>

    <div class="grid cols-2">
      <div class="panel"><div class="panel-head"><h2>Restricted interpreter</h2>
        <span class="sub">read-only</span></div>
        <div class="panel-body">
          <p class="muted" style="margin-top:0">Recovered maintenance material in the documented
          <span class="tag">relay-maint/1</span> format is evaluated by a virtual interpreter with a
          fixed verb allowlist. Paths resolve only within the closed map.</p>
          <div class="verb-list">
            <span class="verb"><b>help</b></span>
            <span class="verb"><b>whoami</b></span>
            <span class="verb"><b>pwd</b></span>
            <span class="verb"><b>ls</b> [path]</span>
            <span class="verb"><b>cat</b> &lt;path&gt;</span>
          </div>
          <hr class="div">
          <div class="codeblock">#!relay-maint/1
help
ls /</div>
        </div></div>

      <div class="panel"><div class="panel-head"><h2>Safety envelope</h2></div>
        <div class="panel-body"><ul class="notice-list">
          <li>No OS command execution, shell, or subprocess.</li>
          <li>No real filesystem access — resolution is a pure in-memory map walk.</li>
          <li>No network or external-target capability.</li>
          <li>Verbs outside the allowlist are rejected; traversal is collapsed within the map only.</li>
          <li>Output is bounded (command count, line length, path depth).</li>
        </ul></div></div>
    </div>

    <div class="panel"><div class="panel-head"><h2>Recorded recovery outcomes</h2>
      <a class="sub" href="#/recovery">Recovery jobs →</a></div>
      <div class="panel-body flush">
        ${recov.length ? `<div class="tbl-wrap"><table class="tbl">
          <thead><tr><th>Request</th><th>Slot</th><th>Descriptor epoch</th><th>Occupant epoch</th><th>Occupant</th></tr></thead>
          <tbody>${recov.map((r) => `<tr>
            <td class="mono">${esc(r.request_id)}</td>
            <td class="mono">slot ${esc(r.slot)}</td>
            <td class="mono">${esc(r.descriptor_epoch)}</td>
            <td class="mono">${esc(r.occupant_epoch)}</td>
            <td>${occupantBadge(r.occupant)}</td></tr>`).join('')}
          </tbody></table></div>`
        : `<div class="empty"><div class="hint">No recovery previews have been recorded on this relay.</div></div>`}
      </div></div>`;
}

/* ------------------------------ router --------------------------------- */

const ROUTES = {
  dashboard:   { crumbs: ['Operations', 'Overview'], render: viewDashboard },
  incidents:   { crumbs: ['Operations', 'Incidents'], render: viewIncidents },
  captures:    { crumbs: ['Relay', 'Evidence captures'], render: viewCaptures },
  recovery:    { crumbs: ['Relay', 'Recovery jobs'], render: viewRecovery },
  events:      { crumbs: ['Relay', 'Event timeline'], render: viewEvents },
  diagnostics: { crumbs: ['Tools', 'Diagnostics'], render: viewDiagnostics },
};

function parseHash() {
  const h = (location.hash || '#/dashboard').replace(/^#\/?/, '');
  const parts = h.split('/').filter(Boolean);
  return { name: parts[0] || 'dashboard', param: parts[1] ? decodeURIComponent(parts[1]) : null };
}

function setCrumbs(list) {
  $('#crumbs').innerHTML = list.map((c, i) =>
    `<span class="crumb ${i < list.length - 1 ? 'faded' : ''}">${esc(c)}</span>`).join('');
}

function setActiveNav(name) {
  document.querySelectorAll('.nav-item').forEach((a) =>
    a.classList.toggle('active', a.dataset.route === name));
}

function render() {
  const view = $('#view');
  const blocker = stateBlock();
  const { name, param } = parseHash();

  // Incident detail is a sub-route of incidents.
  if (name === 'incidents' && param) {
    setActiveNav('incidents');
    setCrumbs(['Operations', 'Incidents', param]);
    view.innerHTML = blocker || viewIncidentDetail(param);
  } else {
    const route = ROUTES[name] || ROUTES.dashboard;
    setActiveNav(ROUTES[name] ? name : 'dashboard');
    setCrumbs(route.crumbs);
    view.innerHTML = blocker || route.render();
  }

  bindViewEvents();
  closeNav();
}

function bindViewEvents() {
  // Row / element navigation (CSP-safe: no inline handlers).
  document.querySelectorAll('[data-nav]').forEach((el) => {
    el.addEventListener('click', () => { location.hash = el.dataset.nav; });
  });

  const incQ = $('#inc-q');
  if (incQ) {
    incQ.addEventListener('input', (e) => { incidentFilter.q = e.target.value; render(); restoreFocus('#inc-q'); });
    document.querySelectorAll('[data-filter-state]').forEach((b) =>
      b.addEventListener('click', () => { incidentFilter.state = b.dataset.filterState; render(); }));
  }
  const evtQ = $('#evt-q');
  if (evtQ) {
    evtQ.addEventListener('input', (e) => { eventFilter.q = e.target.value; render(); restoreFocus('#evt-q'); });
    const sel = $('#evt-type');
    if (sel) sel.addEventListener('change', (e) => { eventFilter.type = e.target.value; render(); });
  }
}

function restoreFocus(sel) {
  // Re-rendering replaces the input; restore caret to keep typing fluid.
  const el = $(sel);
  if (el) { const v = el.value; el.focus(); el.setSelectionRange(v.length, v.length); }
}

/* --------------------------- chrome / shell ---------------------------- */

function updateChrome() {
  const online = STATE.online && !STATE.error;
  $('#svc-dot').className = 'dot ' + (STATE.loading ? '' : (online ? 'ok' : 'down'));
  if (STATE.status) {
    $('#svc-name').textContent = STATE.status.service || 'continuity-relay';
    $('#svc-ver').textContent = 'v' + (STATE.status.version || '—');
  }
  $('#ctx-incident-v').textContent = activeIncidentId() || '—';

  const rs = $('#refresh-state');
  if (STATE.loading) { rs.textContent = 'connecting…'; rs.className = 'refresh-state'; }
  else if (online) { rs.textContent = 'live'; rs.className = 'refresh-state live'; }
  else { rs.textContent = 'offline'; rs.className = 'refresh-state err'; }

  if (STATE.lastUpdated) {
    const t = STATE.lastUpdated.toLocaleTimeString([], { hour12: false });
    $('#foot-updated').textContent = online ? `updated ${t}` : `last contact ${t}`;
  }
}

function openNav() { $('#app').classList.add('nav-open'); $('#scrim').hidden = false; }
function closeNav() { $('#app').classList.remove('nav-open'); $('#scrim').hidden = true; }

/* ------------------------------ lifecycle ------------------------------ */

async function refresh(force) {
  await fetchAll();
  updateChrome();
  const sig = signature();
  // Avoid clobbering an input the user is typing in unless forced; defer the
  // re-render (don't record the signature) so a change lands on a later tick.
  const focused = document.activeElement;
  const typing = focused && (focused.id === 'inc-q' || focused.id === 'evt-q');
  const changed = sig !== lastSig;
  if (force || (changed && !typing)) { lastSig = sig; render(); }
}

function init() {
  $('#menu-btn').addEventListener('click', openNav);
  $('#scrim').addEventListener('click', closeNav);
  $('#refresh-btn').addEventListener('click', () => refresh(true));
  window.addEventListener('hashchange', render);

  refresh(true);
  setInterval(() => refresh(false), 5000);
}

init();
