#!/usr/bin/env python3
"""Orphaned Context recon phase 3 — read the three API endpoints + save full app.js.
Endpoints: /api/relay/status, /api/relay/events, /api/incidents.
Events drive everything (CAPTURE_*, NOTE_STORE, NOTE_DISCARD, slots, epochs)."""
import json
import requests, urllib3
urllib3.disable_warnings()
B="https://orphaned-context-c18229f45f48.chall.hiddeninvestigations.net"
s=requests.Session(); s.verify=False
s.headers.update({"User-Agent":"Mozilla/5.0","Accept":"application/json"})

# save full app.js for careful reading
js=s.get(B+"/app.js", timeout=25).text
open("relay_app.js","w",encoding="utf-8").write(js)
print(f"[*] saved app.js ({len(js)}B)")

for ep in ["/api/relay/status","/api/relay/events","/api/incidents"]:
    r=s.get(B+ep, timeout=20)
    print(f"\n===== {ep} [{r.status_code}] =====")
    try:
        j=r.json()
        print(json.dumps(j, indent=2)[:4000])
        if ep.endswith("/events") and isinstance(j, (list,dict)):
            evs = j if isinstance(j,list) else j.get("events",[])
            print(f"\n[events total: {len(evs)}]")
            types={}
            for e in evs: types[e.get("type")]=types.get(e.get("type"),0)+1
            print("event types:", types)
    except Exception as e:
        print("(not json)", r.text[:500])
