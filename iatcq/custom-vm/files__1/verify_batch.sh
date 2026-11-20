#!/bin/sh
chmod +x /w/hyperstate4
for k in "IATCQ{____________________H:Y:v}" "IATCQ{DarkCoverVMreverse00AZwYO}" "IATCQ{AAAAAAAAAAAAAAAAAAAA:25HJ}" "IATCQ{AAAAAAAAAAAAAAAAAAAAAAAA}" "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"; do
  printf '%s => ' "$k"
  /w/hyperstate4 "$k"
done
