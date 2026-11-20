#!/bin/sh
chmod +x /data/usr/local/sbin/r9sampler
for f in /work/probe/*.cal; do
  printf '%s -> ' "$(basename $f)"
  /data/usr/local/sbin/r9sampler "$f"
done
