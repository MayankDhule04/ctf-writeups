# ctfbox — Docker CTF toolbox

A single image with the tools that actually speed up CTFs, so you (and Kiro) can run
real tooling against challenge files/targets without installing anything on Windows.

## Build
```powershell
docker build -t ctfbox:latest -f docker/Dockerfile.ctf docker
```

## Run
Your current folder is mounted at `/work` inside the container.
```powershell
# one-off tool run
.\docker\ctfbox.ps1 <tool> [args...]

# interactive shell
.\docker\ctfbox.ps1
```
Or directly:
```powershell
docker run --rm -it -v "${PWD}:/work" -w /work ctfbox:latest <tool> ...
```

## What's inside
- **Web/recon:** nmap, ffuf, gobuster, nuclei, httpx, sqlmap, whois, dnsutils, curl/wget
- **Crypto (python):** pwntools, pycryptodome, sympy, gmpy2, z3-solver, openssl, pyjwt
- **Rev:** radare2, gdb(+gef), binutils, ltrace/strace, patchelf, checksec, jadx (APK), default-jre
- **Pwn:** pwntools, gdb+gef, ropper, one_gadget, checksec, patchelf
- **Forensics:** binwalk, foremost, exiftool, tshark/tcpdump, p7zip, poppler-utils
- **Stego:** steghide, stegseek, zsteg, outguess, sox, imagemagick, zbar (QR), tesseract (OCR)
- **Hashes:** john, hashid, name-that-hash
- **Utils:** jq, ripgrep, xxd, git, python3/ruby

## Notes
- GPU crackers (hashcat) aren't included — Docker Desktop/WSL GPU passthrough is unreliable; use `john` for CPU cracking or crack on the host.
- For long interactive pwn/gdb sessions, start a persistent container:
  ```powershell
  docker run -d --name ctfbox-live -v "${PWD}:/work" -w /work ctfbox:latest sleep infinity
  docker exec -it ctfbox-live bash
  ```
- rockyou.txt in your workspace is reachable at `/work/rockyou.txt`.
