#!/bin/bash
apt-get update -qq >/dev/null 2>&1
pkgs="ca-certificates curl wget git jq ripgrep xxd file less vim nano procps \
build-essential gcc g++ make pkg-config python3 python3-pip python3-dev ruby ruby-dev \
default-jre-headless libgmp-dev libmpfr-dev libmpc-dev libssl-dev libffi-dev \
nmap sqlmap netcat-openbsd dnsutils whois openssl binwalk foremost libimage-exiftool-perl \
steghide outguess sox imagemagick poppler-utils zbar-tools tesseract-ocr gdb binutils \
patchelf ltrace strace checksec p7zip-full zip unzip john hashid tshark tcpdump"
for p in $pkgs; do
  apt-get install -s --no-install-recommends "$p" >/dev/null 2>&1 || echo "MISSING: $p"
done
echo DONE
