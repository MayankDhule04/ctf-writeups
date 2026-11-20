#!/bin/sh
apt-get update -qq >/dev/null 2>&1
apt-get install -y -qq binutils >/dev/null 2>&1
B=/data/extracted/usr/local/sbin/r9sampler
echo "=== SECTIONS ==="
objdump -h "$B" 2>/dev/null | grep -E 'text|data|rodata'
echo "=== SYMBOLS ==="
objdump -t "$B" 2>/dev/null | grep -iE 'FUNC|OBJECT' | head -60
echo "=== DISASM (.text) ==="
objdump -d -M intel "$B" 2>/dev/null
echo "=== RODATA ==="
objdump -s -j .rodata "$B" 2>/dev/null
echo "=== DATA ==="
objdump -s -j .data "$B" 2>/dev/null
