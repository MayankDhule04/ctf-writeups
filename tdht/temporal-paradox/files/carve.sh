#!/bin/bash
set -e
cd /data
IMG="gateway_snapshot.img"
echo "=== debugfs: list deltaforge dir ==="
debugfs -R "ls -l /var/lib/deltaforge" "$IMG" 2>/dev/null || true
debugfs -R "ls -l /var/cache/deltaforge" "$IMG" 2>/dev/null || true
echo "=== dump encoder_crash.fragment ==="
debugfs -R "dump /var/lib/deltaforge/encoder_crash.fragment /data/encoder_crash.fragment" "$IMG" 2>/dev/null || \
debugfs -R "dump /var/cache/deltaforge/encoder_crash.fragment /data/encoder_crash.fragment" "$IMG" 2>/dev/null || true
echo "=== find any encoder file ==="
debugfs -R "ls -l -d /var/lib/deltaforge" "$IMG" 2>/dev/null || true
ls -la /data/encoder_crash.fragment 2>/dev/null || echo "not dumped by path"
