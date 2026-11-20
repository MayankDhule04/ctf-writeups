#!/bin/bash
pip install --quiet stego-lsb 2>/dev/null
echo "=== stegolsb WavSteg n=1..8 ==="
for N in 1 2 3 4 5 6 8; do
  stegolsb wavsteg -r -i /work/noise.wav -o /work/wsout_$N.bin -n $N -b 200 2>/dev/null
  if [ -f /work/wsout_$N.bin ]; then
    echo "--- n=$N ---"
    strings -n 6 /work/wsout_$N.bin | head -3
    python3 -c "d=open('/work/wsout_$N.bin','rb').read(); print('head',d[:32])"
  fi
done
echo "=== done ==="
