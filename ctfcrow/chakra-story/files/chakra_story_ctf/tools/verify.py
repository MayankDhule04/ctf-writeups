#!/usr/bin/env python3
"""Offline answer checker for The Keeper's Four Pages."""

from __future__ import annotations

import hashlib
import re
import sys

EXPECTED_SHA256 = "f1c967c7f342d6cbed8e3a39f9a5a4ff4d747b9ba930e7ac87b94bcc7f4d268c"
FLAG_PATTERN = re.compile(r"^CHAKRA\{[^{}\r\n]+\}$")


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python3 tools/verify.py 'CHAKRA{...}'")
        return 2

    flag = sys.argv[1]
    if not FLAG_PATTERN.fullmatch(flag):
        print("FAIL: invalid flag format")
        return 1

    if hashlib.sha256(flag.encode()).hexdigest() != EXPECTED_SHA256:
        print("FAIL: wrong flag")
        return 1

    print("PASS: flag accepted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())