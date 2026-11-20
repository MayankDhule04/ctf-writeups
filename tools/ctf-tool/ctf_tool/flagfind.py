"""flagfind — recursively hunt for flags across a directory or single file.

This is the "first thing to run when challenge files drop" command. It walks a
path, and for every reasonably-sized file it:
  * scans raw bytes for flag patterns (plain / hex / base64 via forensics.scan_for_flags)
  * pulls printable strings out of binaries and scans those too

It deliberately does NOT try to "solve" anything (no XOR/caesar/vigenere brute
loops). Those belong to the deliberate subcommands once you know the category.
Keeping this fast and honest means a hit here is a real hit, not noise.
"""

import os
from typing import Dict, List, Optional

from .forensics import scan_for_flags, extract_strings
from .flag_detector import FlagDetector

# Skip huge files by default; CTF flags rarely hide in multi-hundred-MB blobs
# and scanning them stalls the whole hunt.
_DEFAULT_MAX_BYTES = 50 * 1024 * 1024

# Directories that are never challenge content.
_SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", ".idea"}


def _iter_files(root: str, max_bytes: int):
    """Yield file paths under root, skipping junk dirs and oversized files."""
    if os.path.isfile(root):
        yield root
        return
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        for name in filenames:
            fp = os.path.join(dirpath, name)
            try:
                if os.path.getsize(fp) <= max_bytes:
                    yield fp
            except OSError:
                continue


def flagfind(root: str,
             flag_regex: Optional[str] = None,
             max_bytes: int = _DEFAULT_MAX_BYTES,
             deep_strings: bool = True) -> List[Dict]:
    """Recursively scan `root` for flags.

    Args:
        root:        Directory or file to scan.
        flag_regex:  Optional custom flag pattern (e.g. r"myctf\\{[^}]+\\}").
        max_bytes:   Skip files larger than this.
        deep_strings: Also run a strings-pass over each file and scan the output.

    Returns:
        List of hit dicts: {file, value, encoding, offset}. Deduplicated on
        (file, value).
    """
    detector = FlagDetector(extra_regex=flag_regex) if flag_regex else FlagDetector()
    hits: List[Dict] = []
    seen = set()

    def _add(file_path, value, encoding, offset):
        key = (file_path, value)
        if key not in seen:
            seen.add(key)
            hits.append({"file": file_path, "value": value,
                         "encoding": encoding, "offset": offset})

    for fp in _iter_files(root, max_bytes):
        # 1) raw / hex / base64 scan
        try:
            for r in scan_for_flags(fp, flag_regex=flag_regex):
                if "error" in r:
                    continue
                _add(fp, r["value"], r.get("encoding", "plain"), r.get("offset", -1))
        except Exception:
            pass

        # 2) strings pass (catches flags embedded in binaries)
        if deep_strings:
            try:
                for s in extract_strings(fp, min_len=4):
                    for m in detector.scan_text(s):
                        _add(fp, m["value"], "strings", -1)
            except Exception:
                pass

    # Rank: prefer named-format hits over the noisy generic/hex catch-alls.
    def _rank(h):
        enc = h["encoding"]
        val = h["value"]
        looks_named = "{" in val and "}" in val
        return (0 if looks_named else 1, 0 if enc == "plain" else 1)

    hits.sort(key=_rank)
    return hits
