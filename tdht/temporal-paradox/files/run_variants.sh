#!/bin/sh
chmod +x /data/usr/local/sbin/r9sampler
for f in /work/variants/*.cal; do
  printf '%s -> ' "$f"
  /data/usr/local/sbin/r9sampler "$f"
done
