#!/bin/sh
set -e
mkdir -p /out
rm -f /out/*.dmtcp 2>/dev/null || true
dmtcp_launch --new-coordinator --coord-port 7779 --ckptdir /out --interval 0 /payload &
sleep 3
dmtcp_command --coord-port 7779 --bcheckpoint
sleep 1
dmtcp_command --coord-port 7779 --quit || true
sleep 1
echo "=== ckpt files ==="
ls -la /out
