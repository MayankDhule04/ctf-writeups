# OSINT — "Find the Ghost" Writeup

**Flag:** `IATCQ26{0-11c1-1e0}`

## Challenge

> A deleted repository isn't truly gone, if the history still echoes. Find the
> ghost, trace it to the real world, and listen for the address. The ghost was
> last seen as **dev-hex09**!

Flag template (revealed later in the chain): `IATCQ26{server_etag}`

## TL;DR

`dev-hex09` (GitHub) → a scrubbed issue in `config-vault` whose **edit history**
still holds the secret → recovered a base64 **IP address** + a burner social
handle **phantom.actual.98** → that handle's SoundCloud track *Operation
Daybreaker* reveals the flag template `IATCQ26{server_etag}` → the "address" is
`157.97.210.115`; its HTTP **ETag** header is the flag body.

---

## Step 1 — Find the ghost (GitHub)

`dev-hex09` exists on GitHub with a single repo, `config-vault`:

```
https://github.com/dev-hex09
https://github.com/dev-hex09/config-vault   (2 commits, 1 fork)
```

Commit author email leaks via the `.patch` trick:

```
GET https://github.com/dev-hex09/config-vault/commit/fe5fae3.patch
From: dev-hex09 <hphohokk@gmail.com>   (TZ +0530 → India)
```

The repo contains a decoy `index.html` ("SecureBank Demo", "Welcome, Amrit")
and a **closed issue #1**: *"Deployment Failure - Access Point locked"* whose
visible body is just `"Nevermind, fixed it"`.

## Step 2 — "History still echoes" (recover the scrubbed issue)

The issue body was edited to hide the payload. GitHub keeps every prior version
in `userContentEdits`, readable with any token via GraphQL:

```graphql
query {
  repository(owner:"dev-hex09", name:"config-vault") {
    issue(number:1) {
      userContentEdits(first:50){ nodes { editedAt diff editor{login} } }
    }
  }
}
```

Original (pre-scrub) body recovered:

> "Scrubbing the code. The target access point is locked down.
> **Address: MTU3Ljk3LjIxMC4xMTU=**. I am burning this account and going back to
> my **phantom.actual.98** handle to listen to my Night Run playlist."

Decode the address:

```python
base64.b64decode("MTU3Ljk3LjIxMC4xMTU=")  # -> 157.97.210.115
```

## Step 3 — Trace to the real world / "listen"

The burner handle `phantom.actual.98`:
- Instagram: profile exists.
- **SoundCloud**: `https://soundcloud.com/phantom-actual-98` — full name "dev hex",
  New Delhi, **one track: "Operation Daybreaker"**.

"Listen to my Night Run playlist" → listen to that track. It reveals the flag
template:

```
IATCQ26{server_etag}
```

`server_etag` is a placeholder — the real flag body is the **ETag of the server**
at the recovered address.

## Step 4 — Read the ETag ("the address")

```python
import requests
r = requests.get("http://157.97.210.115/", timeout=15)
print(r.headers["Server"])  # TruVision
print(r.headers["ETag"])    # "0-11c1-1e0"
```

Response headers:

```
Server: TruVision
ETag: "0-11c1-1e0"
Last-Modified: Wed, 16 Sep 2020 12:09:02 GMT
```

## Flag

Substitute the ETag into the template:

```
IATCQ26{0-11c1-1e0}
```

---

## Decoys / dead ends
- `flag{...}`-style decoys never applied; the event format is `IATCQ26{...}`.
- The SecureBank `index.html`, the IP alone, and the `phantom.actual.98` handle
  are all leads, not the answer — the answer is the live server's ETag.

## Notes
- Recovering an edited GitHub issue body requires a token (GraphQL
  `userContentEdits`); unauthenticated web endpoints for edit history 404.
- Keys/tokens used during solving should be revoked afterward.
