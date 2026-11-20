"""Compare pristine (works) vs my Kali-built (fails) checkpoint header/metadata."""
import gzip, requests

pristine = gzip.decompress(open('snap_pristine.dmtcp','rb').read())
print(f'pristine: {len(pristine)} bytes')

# Grab my Kali-built checkpoint over SSH
import paramiko
c = paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.137.128', 22, 'kali', 'Mayank_1601',
          look_for_keys=False, allow_agent=False, timeout=15)
sftp = c.open_sftp()
# find the ckpt file
_, o, _ = c.exec_command('ls ~/pwn_primecalc/out/ckpt_payload_*.dmtcp | head -1')
path = o.read().decode().strip()
print(f'kali ckpt: {path}')
with sftp.open(path, 'rb') as f:
    kali = gzip.decompress(f.read())
print(f'kali: {len(kali)} bytes')
sftp.close(); c.close()

# Compare headers (DMTCP MAGIC + fields)
print('\n--- pristine head 512 bytes ---')
print(pristine[:512])
print('\n--- kali head 512 bytes ---')
print(kali[:512])

# Look for DMTCP magic and structure. DMTCP stores plaintext header,
# then process memory. Compare early metadata fields.
import re
for label,data in [('pristine',pristine),('kali',kali)]:
    print(f'\n=== {label} metadata search ===')
    for pat in [rb'DMTCP_[A-Z_]+', rb'uid=[0-9]+', rb'gid=[0-9]+', rb'compGroup=[^\n]+']:
        for m in re.finditer(pat, data[:100_000]):
            print(f'  @{m.start():x}: {m.group()!r}')
