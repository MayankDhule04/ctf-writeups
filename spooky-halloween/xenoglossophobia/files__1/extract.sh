#!/bin/bash
cd /data/xeno_out
passes=("supermercado" "supermarket" "Supermarket" "Supermarket Simulator" "supermarket_simulator" "supermarketsimulator" "SupermarketSimulator" "mercado" "grocery" "store" "Supermercado")
for p in "${passes[@]}"; do
  rm -f out.bin
  if steghide extract -sf file0.jpg -p "$p" -xf out.bin -f >/dev/null 2>&1; then
    echo "=== SUCCESS passphrase: [$p] ==="
    echo "--- size: $(wc -c < out.bin) ---"
    cat out.bin
    echo
    exit 0
  else
    echo "fail: [$p]"
  fi
done
echo "no passphrase worked"
