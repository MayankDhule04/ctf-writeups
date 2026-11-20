"""Forensics solvers — strings, binary analysis, memory dumps, APK, archives."""

import os
import re
import struct
import zipfile
import tarfile
from typing import Dict, List, Optional

from .utils import file_magic, file_entropy, extract_printable_strings, xor_single, xor_key
from .flag_detector import FlagDetector

_detector = FlagDetector()


# ---------------------------------------------------------------------------
# String extraction
# ---------------------------------------------------------------------------

def extract_strings(file_path: str, min_len: int = 4,
                    flag_regex: str = None) -> List[str]:
    """Extract printable ASCII strings from any binary file.

    Args:
        file_path: Path to binary/text file
        min_len: Minimum string length to return
        flag_regex: Optional additional flag regex

    Returns:
        List of printable strings
    """
    detector = FlagDetector(extra_regex=flag_regex) if flag_regex else _detector
    try:
        with open(file_path, "rb") as f:
            data = f.read()
    except Exception as e:
        return [f"ERROR: {e}"]
    return extract_printable_strings(data, min_len=min_len)


def scan_for_flags(file_path: str, flag_regex: str = None) -> List[Dict]:
    """Scan a file for flag patterns including encoded variants.

    Returns list of {offset, value, encoding}
    """
    detector = FlagDetector(extra_regex=flag_regex) if flag_regex else _detector
    results = []
    try:
        with open(file_path, "rb") as f:
            data = f.read()
    except Exception as e:
        return [{"error": str(e)}]

    text = data.decode("utf-8", errors="replace")

    # Plain scan
    for match in detector.scan_text(text):
        results.append({"offset": match["start"], "value": match["value"], "encoding": "plain"})

    # Hex decode then scan
    hex_clean = re.sub(r"[^0-9a-fA-F]", "", text)
    if len(hex_clean) >= 8:
        try:
            hex_decoded = bytes.fromhex(hex_clean).decode("utf-8", errors="replace")
            for m in detector.scan_text(hex_decoded):
                results.append({"offset": -1, "value": m["value"], "encoding": "hex"})
        except Exception:
            pass

    # Base64 scan
    import base64
    b64_pattern = re.compile(r"[A-Za-z0-9+/]{20,}={0,2}")
    for m in b64_pattern.finditer(text):
        try:
            dec = base64.b64decode(m.group(0) + "==").decode("utf-8", errors="replace")
            for fm in detector.scan_text(dec):
                results.append({"offset": m.start(), "value": fm["value"], "encoding": "base64"})
        except Exception:
            pass

    # Deduplicate
    seen = set()
    unique = []
    for r in results:
        key = r.get("value", "")
        if key not in seen:
            seen.add(key)
            unique.append(r)
    return unique


# ---------------------------------------------------------------------------
# File info
# ---------------------------------------------------------------------------

def file_info(file_path: str) -> Dict:
    """Get comprehensive file information.

    Returns dict with type, magic, size, entropy, strings sample.
    """
    if not os.path.exists(file_path):
        return {"error": "file not found"}

    size = os.path.getsize(file_path)
    ftype = file_magic(file_path)
    entropy = file_entropy(file_path)

    with open(file_path, "rb") as f:
        header = f.read(32)

    strings = extract_strings(file_path, min_len=6)[:20]
    flags = _detector.extract_all("\n".join(strings))

    return {
        "path":         file_path,
        "type":         ftype,
        "size":         size,
        "entropy":      round(entropy, 3),
        "header_hex":   header.hex(),
        "strings_sample": strings[:10],
        "flags":        flags,
    }


# ---------------------------------------------------------------------------
# Embedded file extraction
# ---------------------------------------------------------------------------

def extract_embedded(file_path: str, output_dir: str = None) -> List[str]:
    """Extract embedded files (ZIP inside PNG, files appended to ELF, etc.).

    Returns list of extracted file paths.
    """
    extracted = []
    out = output_dir or os.path.dirname(file_path) or "."

    with open(file_path, "rb") as f:
        data = f.read()

    # ZIP detection
    zip_sig = b"PK\x03\x04"
    offset = 0
    while True:
        idx = data.find(zip_sig, offset)
        if idx == -1:
            break
        out_path = os.path.join(out, f"embedded_{idx}.zip")
        with open(out_path, "wb") as f:
            f.write(data[idx:])
        try:
            with zipfile.ZipFile(out_path) as zf:
                zf.extractall(os.path.join(out, f"zip_{idx}"))
                extracted.append(out_path)
        except Exception:
            os.remove(out_path)
        offset = idx + 4

    # PNG inside binary
    png_sig = b"\x89PNG"
    offset = 0
    count = 0
    while True:
        idx = data.find(png_sig, offset)
        if idx == -1 or idx == 0:
            offset = idx + 1 if idx != -1 else len(data)
            if idx == -1:
                break
            continue
        out_path = os.path.join(out, f"embedded_img_{count}.png")
        with open(out_path, "wb") as f:
            f.write(data[idx:])
        extracted.append(out_path)
        count += 1
        offset = idx + 4

    return extracted


# ---------------------------------------------------------------------------
# Memory dump analysis
# ---------------------------------------------------------------------------

def memory_string_search(dump_path: str, pattern: str,
                          context_bytes: int = 64) -> List[Dict]:
    """Search memory dump for a string pattern.

    Returns list of {offset, offset_hex, match, context}
    """
    results = []
    try:
        with open(dump_path, "rb") as f:
            data = f.read()
    except Exception as e:
        return [{"error": str(e)}]

    encoded = pattern.encode("utf-8")
    offset = 0
    while True:
        idx = data.find(encoded, offset)
        if idx == -1:
            break
        ctx_start = max(0, idx - context_bytes)
        ctx_end = min(len(data), idx + len(encoded) + context_bytes)
        ctx = data[ctx_start:ctx_end].decode("utf-8", errors="replace")
        results.append({
            "offset":     idx,
            "offset_hex": hex(idx),
            "match":      pattern,
            "context":    ctx,
        })
        offset = idx + 1
    return results


def memory_xor_scan(dump_path: str, xor_keys: List[int] = None,
                    flag_regex: str = None,
                    chunk_size: int = 4096) -> List[Dict]:
    """Scan memory dump with XOR keys, look for flag patterns.

    Args:
        dump_path: Path to memory dump
        xor_keys: List of single-byte keys to try (default: all 256)
        flag_regex: Optional override flag pattern
        chunk_size: Process dump in chunks of this size

    Returns:
        List of {key, offset, flags}
    """
    detector = FlagDetector(extra_regex=flag_regex) if flag_regex else _detector
    if xor_keys is None:
        xor_keys = list(range(1, 256))

    results = []
    try:
        with open(dump_path, "rb") as f:
            data = f.read()
    except Exception as e:
        return [{"error": str(e)}]

    for key in xor_keys:
        decrypted = xor_single(data, key)
        text = decrypted.decode("utf-8", errors="replace")
        flags = detector.extract_all(text)
        if flags:
            # Find offsets
            for flag in flags:
                try:
                    raw_flag = bytes(ord(c) ^ key for c in flag)
                    idx = data.find(raw_flag)
                except Exception:
                    idx = -1
                results.append({
                    "key":     key,
                    "key_hex": hex(key),
                    "flag":    flag,
                    "offset":  idx,
                })
    return results


def memory_bruteforce_flags(dump_path: str, flag_prefix: str = "CHAKRA{",
                             max_keys: int = 256) -> List[Dict]:
    """Bruteforce XOR keys on memory dump looking for flag prefix."""
    results = []
    try:
        with open(dump_path, "rb") as f:
            data = f.read()
    except Exception as e:
        return [{"error": str(e)}]

    for key in range(1, max_keys):
        decrypted = xor_single(data, key)
        text = decrypted.decode("utf-8", errors="replace")
        if flag_prefix in text or _detector.is_flag(text[:1000]):
            flags = _detector.extract_all(text)
            results.append({
                "key":        key,
                "key_hex":    hex(key),
                "flags":      flags,
                "has_prefix": flag_prefix in text,
            })
    return results


# ---------------------------------------------------------------------------
# APK analysis
# ---------------------------------------------------------------------------

def apk_extract(apk_path: str, output_dir: str = None) -> Dict:
    """Extract APK contents and find interesting strings.

    Returns dict with files, strings, assets, flags.
    """
    result = {
        "files":    [],
        "strings":  [],
        "assets":   [],
        "flags":    [],
        "error":    None,
    }
    out = output_dir or apk_path + "_extracted"
    try:
        with zipfile.ZipFile(apk_path, "r") as zf:
            zf.extractall(out)
            result["files"] = zf.namelist()
            for name in zf.namelist():
                if "asset" in name.lower() or name.endswith((".txt", ".json", ".xml")):
                    result["assets"].append(name)
                try:
                    content = zf.read(name).decode("utf-8", errors="replace")
                    strings = extract_printable_strings(content.encode(), min_len=6)
                    flags = _detector.extract_all(content)
                    if flags:
                        result["flags"].extend(flags)
                    result["strings"].extend(strings[:5])
                except Exception:
                    pass
    except Exception as e:
        result["error"] = str(e)
    result["flags"] = list(set(result["flags"]))
    return result


# ---------------------------------------------------------------------------
# Archive analysis
# ---------------------------------------------------------------------------

def check_archive(file_path: str) -> Dict:
    """Try to open file as ZIP/TAR, list and optionally extract contents."""
    result = {"type": None, "files": [], "error": None, "flags": []}

    # Try ZIP
    try:
        with zipfile.ZipFile(file_path, "r") as zf:
            result["type"] = "zip"
            for info in zf.infolist():
                result["files"].append({
                    "name":     info.filename,
                    "size":     info.file_size,
                    "compress": info.compress_size,
                })
                try:
                    content = zf.read(info.filename).decode("utf-8", errors="replace")
                    flags = _detector.extract_all(content)
                    result["flags"].extend(flags)
                except Exception:
                    pass
            return result
    except Exception:
        pass

    # Try TAR
    try:
        with tarfile.open(file_path, "r:*") as tf:
            result["type"] = "tar"
            for member in tf.getmembers():
                result["files"].append({"name": member.name, "size": member.size})
                if member.isfile():
                    try:
                        f = tf.extractfile(member)
                        if f:
                            content = f.read().decode("utf-8", errors="replace")
                            flags = _detector.extract_all(content)
                            result["flags"].extend(flags)
                    except Exception:
                        pass
            return result
    except Exception:
        pass

    result["error"] = "not a recognized archive format"
    return result


# ---------------------------------------------------------------------------
# Binary analysis
# ---------------------------------------------------------------------------

def analyze_binary(file_path: str) -> Dict:
    """Full binary analysis: type, strings, entropy, embedded files, flags."""
    info = file_info(file_path)
    strings = extract_strings(file_path, min_len=4)
    flags = _detector.extract_all("\n".join(strings))
    flags.extend(info.get("flags", []))

    # Check for embedded archives
    embedded = []
    try:
        embedded = extract_embedded(file_path)
    except Exception:
        pass

    return {
        **info,
        "all_strings_count": len(strings),
        "interesting_strings": [s for s in strings if len(s) > 10][:20],
        "flags":              list(set(flags)),
        "embedded_files":     embedded,
    }
