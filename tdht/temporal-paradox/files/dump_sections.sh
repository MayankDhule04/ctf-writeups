#!/bin/sh
apt-get update -qq >/dev/null 2>&1
apt-get install -y -qq binutils >/dev/null 2>&1
B=/data/usr/local/sbin/r9sampler
echo "=====RODATA====="
objdump -s -j .rodata "$B"
echo "=====DATA.REL.RO====="
objdump -s -j .data.rel.ro "$B"
echo "=====DATA====="
objdump -s -j .data "$B"
echo "=====FULL DISASM====="
objdump -d -M intel "$B"
