#!/bin/bash
echo "=== binaries (which) ==="
for t in nmap ffuf gobuster nuclei httpx sqlmap r2 radare2 gdb objdump checksec patchelf \
         binwalk foremost exiftool steghide stegseek zsteg outguess sox convert zbarimg \
         tesseract john hashid nth jadx one_gadget tshark 7z jq rg xxd; do
  p=$(command -v "$t" 2>/dev/null)
  printf "  %-12s %s\n" "$t" "${p:-MISSING}"
done
echo "=== python libs ==="
python3 - <<'PY'
mods=["pwn","Crypto","sympy","gmpy2","z3","ropper","PIL","numpy","scipy","jwt","requests","bs4"]
for m in mods:
    try:
        __import__(m); print("  ok   ", m)
    except Exception as e:
        print("  FAIL ", m, e)
PY
echo "=== versions ==="
r2 -v 2>/dev/null | head -1
ffuf -V 2>/dev/null | head -1
python3 -c "import pwn; print('pwntools', pwn.__version__)"
