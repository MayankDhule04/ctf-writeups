"""Shared utilities for CTF Tool."""

import base64
import binascii
import os
import re
import struct
import string
from typing import List, Optional

# ---------------------------------------------------------------------------
# File type detection
# ---------------------------------------------------------------------------

_MAGIC = {
    b"\x89PNG":         "png",
    b"\xff\xd8\xff":    "jpeg",
    b"GIF8":            "gif",
    b"BM":              "bmp",
    b"RIFF":            "wav",   # may also be AVI/WEBP
    b"ID3":             "mp3",
    b"\xff\xfb":        "mp3",
    b"fLaC":            "flac",
    b"OggS":            "ogg",
    b"\x1f\x8b":        "gzip",
    b"PK\x03\x04":      "zip",
    b"PK\x05\x06":      "zip",
    b"7z\xbc\xaf":      "7z",
    b"Rar!":            "rar",
    b"%PDF":            "pdf",
    b"\x7fELF":         "elf",
    b"MZ":              "pe",
    b"dex\n":           "dex",
    b"\xca\xfe\xba\xbe": "class",
    b"<svg":            "svg",
    b"<?xml":           "xml",
    b"<!DOCTYPE":       "html",
    b"<html":           "html",
}


def file_magic(path: str) -> str:
    """Detect file type from magic bytes. Returns type string like 'png', 'elf', etc."""
    try:
        with open(path, "rb") as f:
            header = f.read(16)
    except Exception:
        return "unknown"

    for magic, ftype in _MAGIC.items():
        if header[:len(magic)] == magic:
            return ftype

    # Check extension fallback
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    return ext or "unknown"


def file_entropy(path: str, block_size: int = 65536) -> float:
    """Compute Shannon entropy of a file (0.0 = uniform, 8.0 = fully random)."""
    import math
    counts = [0] * 256
    total = 0
    try:
        with open(path, "rb") as f:
            while True:
                block = f.read(block_size)
                if not block:
                    break
                for b in block:
                    counts[b] += 1
                    total += 1
    except Exception:
        return 0.0
    if total == 0:
        return 0.0
    entropy = 0.0
    for c in counts:
        if c > 0:
            p = c / total
            entropy -= p * math.log2(p)
    return entropy


# ---------------------------------------------------------------------------
# Encoding / decoding helpers
# ---------------------------------------------------------------------------

def to_hex(data: bytes) -> str:
    """Convert bytes to hex string."""
    return data.hex()


def from_hex(s: str) -> Optional[bytes]:
    """Convert hex string to bytes. Returns None on error."""
    s = s.strip().replace(" ", "").replace("0x", "")
    try:
        return bytes.fromhex(s)
    except Exception:
        return None


def b64decode_safe(s: str) -> Optional[bytes]:
    """Base64 decode with padding fix. Returns None on failure."""
    s = s.strip()
    # Add padding
    padding = 4 - len(s) % 4
    if padding != 4:
        s += "=" * padding
    for variant in [s, s.replace("-", "+").replace("_", "/")]:
        try:
            return base64.b64decode(variant)
        except Exception:
            continue
    return None


def b64encode_safe(data: bytes) -> str:
    """URL-safe Base64 encode."""
    return base64.b64encode(data).decode()


def try_common_encodings(s: str) -> List[dict]:
    """Try multiple decode strategies. Returns list of {method, result}."""
    results = []

    # Base64
    decoded = b64decode_safe(s)
    if decoded:
        try:
            results.append({"method": "base64", "result": decoded.decode("utf-8")})
        except Exception:
            results.append({"method": "base64", "result": decoded.hex()})

    # Hex
    if re.fullmatch(r"[0-9a-fA-F\s]+", s.strip()):
        h = from_hex(s)
        if h:
            try:
                results.append({"method": "hex", "result": h.decode("utf-8")})
            except Exception:
                pass

    # Base32
    try:
        padded = s.strip().upper()
        padding = 8 - len(padded) % 8
        if padding != 8:
            padded += "=" * padding
        decoded32 = base64.b32decode(padded)
        results.append({"method": "base32", "result": decoded32.decode("utf-8", errors="replace")})
    except Exception:
        pass

    # ROT13
    results.append({"method": "rot13", "result": rot13(s)})

    # URL decode
    try:
        from urllib.parse import unquote
        results.append({"method": "url_decode", "result": unquote(s)})
    except Exception:
        pass

    return results


# ---------------------------------------------------------------------------
# Classic cipher helpers
# ---------------------------------------------------------------------------

def rot13(s: str) -> str:
    """Apply ROT-13 to a string."""
    result = []
    for c in s:
        if "a" <= c <= "z":
            result.append(chr((ord(c) - ord("a") + 13) % 26 + ord("a")))
        elif "A" <= c <= "Z":
            result.append(chr((ord(c) - ord("A") + 13) % 26 + ord("A")))
        else:
            result.append(c)
    return "".join(result)


def caesar_decrypt(s: str, shift: int) -> str:
    """Decrypt Caesar cipher with given shift."""
    result = []
    for c in s:
        if "a" <= c <= "z":
            result.append(chr((ord(c) - ord("a") - shift) % 26 + ord("a")))
        elif "A" <= c <= "Z":
            result.append(chr((ord(c) - ord("A") - shift) % 26 + ord("A")))
        else:
            result.append(c)
    return "".join(result)


# ---------------------------------------------------------------------------
# XOR helpers
# ---------------------------------------------------------------------------

def xor_bytes(a: bytes, b: bytes) -> bytes:
    """XOR two byte sequences (truncated to shorter)."""
    return bytes(x ^ y for x, y in zip(a, b))


def xor_single(data: bytes, key: int) -> bytes:
    """XOR every byte with a single byte key."""
    return bytes(b ^ key for b in data)


def xor_key(data: bytes, key: bytes) -> bytes:
    """XOR data with cycling key."""
    if not key:
        return data
    return bytes(data[i] ^ key[i % len(key)] for i in range(len(data)))


# ---------------------------------------------------------------------------
# String extraction
# ---------------------------------------------------------------------------

def extract_printable_strings(data: bytes, min_len: int = 4) -> List[str]:
    """Extract runs of printable ASCII bytes of at least min_len."""
    results = []
    current = []
    for b in data:
        if 0x20 <= b < 0x7f:
            current.append(chr(b))
        else:
            if len(current) >= min_len:
                results.append("".join(current))
            current = []
    if len(current) >= min_len:
        results.append("".join(current))
    return results


def is_printable(s: str, threshold: float = 0.9) -> bool:
    """Return True if >= threshold fraction of characters are printable ASCII."""
    if not s:
        return False
    printable_count = sum(1 for c in s if c in string.printable)
    return printable_count / len(s) >= threshold


# ---------------------------------------------------------------------------
# Misc
# ---------------------------------------------------------------------------

def ic(text: str) -> float:
    """Index of Coincidence for a string (only alphabetic chars)."""
    text = text.upper()
    alpha = [c for c in text if c.isalpha()]
    n = len(alpha)
    if n < 2:
        return 0.0
    freq = {}
    for c in alpha:
        freq[c] = freq.get(c, 0) + 1
    return sum(f * (f - 1) for f in freq.values()) / (n * (n - 1))


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
