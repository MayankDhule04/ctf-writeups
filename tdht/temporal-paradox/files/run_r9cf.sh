#!/bin/sh
chmod +x /data/usr/local/sbin/r9sampler
for f in /work/r9cf/rec*.bin; do
  printf '%s -> ' "$(basename $f)"
  /data/usr/local/sbin/r9sampler "$f"
done
