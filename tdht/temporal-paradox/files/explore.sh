#!/bin/sh
apt-get update -qq >/dev/null 2>&1
apt-get install -y -qq e2fsprogs >/dev/null 2>&1
IMG="/data/Temporal Paradox/gateway_snapshot.img"
# recursive-ish listing using rdump of whole tree to /out then find
mkdir -p /out
debugfs -R "rdump / /out" "$IMG" 2>/dev/null
echo "=== FILE TREE ==="
find /out -printf '%y %10s  %p\n' 2>/dev/null | sort -k3
echo "=== stat-like (mtime) for all files ==="
find /out -type f -printf '%TY-%Tm-%Td %TH:%TM  %s  %p\n' 2>/dev/null | sort
# copy extracted tree to mounted volume for host access
cp -r /out "/data/extracted" 2>/dev/null
echo "=== rollout.log ==="; cat "/out/var/log/deltaforge/rollout.log"
echo "=== triage_cache.txt ==="; cat "/out/home/operator/triage_cache.txt"
echo "=== .gdb_history ==="; cat "/out/home/operator/.gdb_history"
echo "=== lane_0.cal (hex) ==="; xxd "/out/var/lib/deltaforge/lane_0.cal" 2>/dev/null || od -An -tx1 "/out/var/lib/deltaforge/lane_0.cal"
echo "=== lane_1.cal (hex) ==="; xxd "/out/var/lib/deltaforge/lane_1.cal" 2>/dev/null || od -An -tx1 "/out/var/lib/deltaforge/lane_1.cal"
