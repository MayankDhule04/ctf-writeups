#!/bin/sh
chmod +x /data/usr/local/sbin/r9sampler
for f in /work/variants2/*.cal; do
  printf '%s -> ' "$f"
  /data/usr/local/sbin/r9sampler "$f"
done
