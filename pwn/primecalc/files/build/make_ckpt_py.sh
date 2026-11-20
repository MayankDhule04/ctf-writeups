#!/bin/sh
set -e
mkdir -p /out
rm -f /out/*.dmtcp /out/dmtcp_restart_script* 2>/dev/null || true
cp /work/mal.py /mal.py
dmtcp_launch --new-coordinator --coord-port 7779 --ckptdir /out --interval 0 python3 /mal.py &
sleep 4
dmtcp_command --coord-port 7779 --bcheckpoint
sleep 1
dmtcp_command --coord-port 7779 --quit 2>/dev/null || true
sleep 1
echo "=== ckpt files ==="
ls -la /out
