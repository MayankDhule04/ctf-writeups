"""Compare vDSO between my Kali-built checkpoint and the pristine remote checkpoint."""
import paramiko
c = paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.137.128', 22, 'kali', 'Mayank_1601',
          look_for_keys=False, allow_agent=False, timeout=15)


def run(cmd, timeout=180):
    i, o, e = c.exec_command(cmd, timeout=timeout)
    return o.read().decode(errors='replace') + e.read().decode(errors='replace')


# my checkpoint (built on kali)
print('--- my ckpt (kali 6.16) vDSO analysis ---')
print(run(r'''cd ~/pwn_primecalc && python3 -c '
import gzip, re
d=gzip.decompress(open("out/ckpt_payload_11501224e1745734-40000-618bd89bb4.dmtcp","rb").read())
for m in re.finditer(rb"__vdso_[a-z_]+", d):
    print(hex(m.start()), m.group())
# search for LINUX notes  
print("--- LINUX notes ---")
for m in re.finditer(rb"LINUX\x00\x00\x00([\x00-\xff]{16})", d):
    off = m.start()
    ctx = d[max(0,off-16):off+32]
    print(hex(off), ctx.hex())
' '''))
c.close()
