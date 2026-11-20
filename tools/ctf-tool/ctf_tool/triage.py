"""triage — gather structured evidence about challenge files for reasoning.

This is the hybrid enabler. It does NOT try to solve anything. It produces a
compact, information-dense report that a human (or an LLM assistant) reads to
decide *which specific* attack applies. Everything here is deterministic:
file type, size, entropy, magic bytes, notable strings (urls / hosts / keys /
hashes / encoded blobs), and any plaintext flag candidates.

High entropy (~7.5+) hints encrypted/compressed data. Low entropy + long
base64/hex blobs hint an encoding challenge. Source files (.py/.js/.php/.rb)
hint the mechanism is in the code, so read it, don't brute-force.
"""

import os
import re
from typing import Dict, List, Optional

from .utils import file_magic, file_entropy, extract_printable_strings
from .flag_detector import FlagDetector

_SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", ".idea"}
_MAX_BYTES = 50 * 1024 * 1024

# Extension -> likely challenge category. Only a hint; the assistant decides.
_CATEGORY_HINTS = {
    ".py": "code/rev", ".js": "web/code", ".php": "web", ".rb": "web/code",
    ".html": "web", ".jsp": "web", ".java": "rev", ".class": "rev",
    ".apk": "rev/mobile", ".dex": "rev/mobile", ".so": "rev/pwn",
    ".exe": "rev/pwn", ".elf": "rev/pwn", ".bin": "rev/pwn/crypto",
    ".png": "stego", ".jpg": "stego", ".jpeg": "stego", ".bmp": "stego",
    ".gif": "stego", ".svg": "stego/misc",
    ".wav": "stego/audio", ".mp3": "stego/audio", ".flac": "stego/audio",
    ".pcap": "forensics/network", ".pcapng": "forensics/network",
    ".dmp": "forensics/memory", ".raw": "forensics/memory", ".mem": "forensics/memory",
    ".zip": "archive", ".tar": "archive", ".gz": "archive", ".7z": "archive",
    ".enc": "crypto", ".cipher": "crypto", ".key": "crypto", ".pem": "crypto",
    ".json": "misc/web", ".txt": "misc/crypto",
}

_URL_RE   = re.compile(r"https?://[^\s\"'<>]+")
_HOST_RE  = re.compile(r"\b(?:nc|ncat|connect)\s+([\w.\-]+)\s+(\d{2,5})\b")
_HASH_RE  = re.compile(r"\b[a-fA-F0-9]{32,128}\b")
_B64_RE   = re.compile(r"\b[A-Za-z0-9+/]{24,}={0,2}\b")
_KEYWORD_RE = re.compile(r"(?i)\b(password|secret|token|api[_-]?key|private[_-]?key|BEGIN [A-Z ]*PRIVATE KEY|admin|flag)\b")


def _analyze_file(path: str, detector: FlagDetector) -> Dict:
    """Build an evidence dict for a single file."""
    info: Dict = {"file": path}
    try:
        size = os.path.getsize(path)
    except OSError:
        return {"file": path, "error": "unreadable"}
    info["size"] = size
    ext = os.path.splitext(path)[1].lower()
    info["category_hint"] = _CATEGORY_HINTS.get(ext, "unknown")

    try:
        info["type"] = file_magic(path)
    except Exception:
        info["type"] = "?"
    try:
        info["entropy"] = round(file_entropy(path), 2)
    except Exception:
        info["entropy"] = None

    # String-based evidence (skip if huge)
    strings: List[str] = []
    if size <= _MAX_BYTES:
        try:
            with open(path, "rb") as f:
                data = f.read()
            strings = extract_printable_strings(data, min_len=4)
        except Exception:
            data = b""
    else:
        data = b""

    joined = "\n".join(strings)
    info["flag_candidates"] = detector.extract_all(joined)
    info["urls"]     = sorted(set(_URL_RE.findall(joined)))[:10]
    info["nc_hosts"] = [f"{h}:{p}" for h, p in _HOST_RE.findall(joined)][:5]
    info["hashes"]   = sorted(set(_HASH_RE.findall(joined)))[:5]
    info["keywords"] = sorted(set(m.lower() for m in _KEYWORD_RE.findall(joined)))
    # Long encoded blobs are worth a human look
    b64 = sorted(set(_B64_RE.findall(joined)), key=len, reverse=True)
    info["b64_blobs"] = [b[:60] + ("…" if len(b) > 60 else "") for b in b64[:3]]
    return info


def triage(root: str, flag_regex: Optional[str] = None) -> Dict:
    """Walk `root` and produce a structured evidence report.

    Returns a dict with a per-file list and a rolled-up summary. Nothing here
    is a "solution" — it's raw material for deciding the next move.
    """
    detector = FlagDetector(extra_regex=flag_regex) if flag_regex else FlagDetector()

    files: List[str] = []
    if os.path.isfile(root):
        files = [root]
    else:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
            for name in filenames:
                files.append(os.path.join(dirpath, name))

    reports = [_analyze_file(f, detector) for f in files]

    # Roll-up summary the assistant can skim first.
    categories: Dict[str, int] = {}
    all_flags, all_urls, all_hosts = [], [], []
    for r in reports:
        categories[r.get("category_hint", "unknown")] = \
            categories.get(r.get("category_hint", "unknown"), 0) + 1
        all_flags.extend(r.get("flag_candidates", []))
        all_urls.extend(r.get("urls", []))
        all_hosts.extend(r.get("nc_hosts", []))

    summary = {
        "file_count": len(reports),
        "categories": categories,
        "flag_candidates": sorted(set(all_flags)),
        "urls": sorted(set(all_urls)),
        "nc_hosts": sorted(set(all_hosts)),
    }
    return {"summary": summary, "files": reports}
