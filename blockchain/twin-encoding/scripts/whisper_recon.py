#!/usr/bin/env python3
"""Whisper recon phase 2: read /docs and /clients (full), map token scheme."""
import requests, urllib3
urllib3.disable_warnings()
B="https://whisper-3cfe1275e06a.chall.hiddeninvestigations.net"
s=requests.Session(); s.verify=False; s.headers.update({"User-Agent":"Mozilla/5.0"})
for p in ["/","/docs","/clients"]:
    r=s.get(B+p, timeout=20)
    print(f"\n================= GET {p} [{r.status_code}] =================")
    print(r.text)
