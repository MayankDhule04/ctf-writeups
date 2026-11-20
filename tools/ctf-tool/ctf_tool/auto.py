"""Auto-detect input type and run appropriate solvers."""

import os
import re
from typing import Dict, List, Optional

from .utils import file_magic, extract_printable_strings
from .flag_detector import FlagDetector

_detector = FlagDetector()

# ---------------------------------------------------------------------------
# Type detection
# ---------------------------------------------------------------------------

def detect_type(path_or_url: str) -> Dict:
    """Detect whether input is URL, image, audio, binary, text, archive or APK.

    Returns:
        {type, subtype, extension, magic, confidence}
    """
    result = {
        "input":      path_or_url,
        "type":       "unknown",
        "subtype":    None,
        "extension":  None,
        "magic":      None,
        "confidence": "low",
    }

    # URL detection
    if path_or_url.startswith(("http://", "https://", "ftp://")):
        result["type"] = "url"
        result["confidence"] = "high"
        return result

    if not os.path.exists(path_or_url):
        result["type"] = "string"
        return result

    ext = os.path.splitext(path_or_url)[1].lower()
    result["extension"] = ext
    magic = file_magic(path_or_url)
    result["magic"] = magic

    # Image types
    if magic in ("png", "jpeg", "gif", "bmp") or ext in (".png", ".jpg", ".jpeg", ".gif", ".bmp"):
        result["type"] = "image"
        result["subtype"] = magic
        result["confidence"] = "high"
    # Audio types
    elif magic in ("wav", "mp3", "flac", "ogg") or ext in (".wav", ".mp3", ".flac", ".ogg"):
        result["type"] = "audio"
        result["subtype"] = magic
        result["confidence"] = "high"
    # Archive types
    elif magic in ("zip", "gzip", "rar", "7z") or ext in (".zip", ".tar", ".gz", ".rar", ".7z"):
        result["type"] = "archive"
        result["subtype"] = magic
        result["confidence"] = "high"
    # APK (Android)
    elif ext == ".apk" or (magic == "zip" and ext == ".apk"):
        result["type"] = "apk"
        result["confidence"] = "high"
    # ELF binary
    elif magic == "elf" or ext in (".elf", ".so"):
        result["type"] = "binary"
        result["subtype"] = "elf"
        result["confidence"] = "high"
    # PE binary
    elif magic == "pe" or ext in (".exe", ".dll"):
        result["type"] = "binary"
        result["subtype"] = "pe"
        result["confidence"] = "high"
    # Memory dump
    elif ext in (".dmp", ".dump", ".mem"):
        result["type"] = "memory_dump"
        result["confidence"] = "high"
    # PDF
    elif magic == "pdf" or ext == ".pdf":
        result["type"] = "document"
        result["subtype"] = "pdf"
        result["confidence"] = "high"
    # Text/data files
    elif ext in (".txt", ".md", ".json", ".xml", ".html", ".py", ".js", ".csv"):
        result["type"] = "text"
        result["subtype"] = ext.lstrip(".")
        result["confidence"] = "high"
    else:
        # Read a sample to guess
        try:
            with open(path_or_url, "rb") as f:
                sample = f.read(512)
            printable_ratio = sum(1 for b in sample if 0x20 <= b < 0x7f) / max(len(sample), 1)
            if printable_ratio > 0.8:
                result["type"] = "text"
                result["confidence"] = "medium"
            else:
                result["type"] = "binary"
                result["confidence"] = "medium"
        except Exception:
            pass

    return result


# ---------------------------------------------------------------------------
# Auto solver
# ---------------------------------------------------------------------------

def auto_solve(input_path: str, flag_regex: str = None,
               verbose: bool = False) -> Dict:
    """Auto-detect input type and run the most relevant solvers.

    Stops early if a flag is found. Returns comprehensive results.

    Args:
        input_path: File path or URL
        flag_regex: Optional custom flag pattern
        verbose: Print progress messages

    Returns:
        {type, solvers_tried, flags_found, results}
    """
    detector = FlagDetector(extra_regex=flag_regex) if flag_regex else _detector
    info = detect_type(input_path)
    itype = info["type"]

    output = {
        "input":         input_path,
        "detected_type": itype,
        "detection":     info,
        "solvers_tried": [],
        "flags_found":   [],
        "results":       {},
    }

    def _log(msg):
        if verbose:
            print(f"[auto] {msg}")

    def _add_flags(solver_name: str, flags: List[str]):
        output["solvers_tried"].append(solver_name)
        if flags:
            output["flags_found"].extend(flags)
            output["flags_found"] = list(dict.fromkeys(output["flags_found"]))
            _log(f"  *** FLAGS FOUND by {solver_name}: {flags}")
            return True
        return False

    # ------------------------------------------------------------------ URL
    if itype == "url":
        from .web import check_headers, check_wellknown, dir_enum
        _log("Running web recon...")

        result = check_headers(input_path)
        output["results"]["headers"] = result
        if _add_flags("check_headers", result.get("flags", [])):
            return output

        wk = check_wellknown(input_path)
        output["results"]["wellknown"] = wk
        for path, data in wk.items():
            if _add_flags(f"wellknown:{path}", data.get("flags", [])):
                return output

        dirs = dir_enum(input_path)
        output["results"]["dirbust"] = dirs
        for d in dirs:
            if _add_flags(f"dirbust:{d['url']}", d.get("flags", [])):
                return output

        # Check for JWT in cookies
        cookies = result.get("cookies", {})
        for k, v in cookies.items():
            if v.count(".") == 2:
                from .web import jwt_decode
                decoded = jwt_decode(v)
                flags = detector.extract_all(str(decoded))
                _add_flags(f"jwt_cookie:{k}", flags)

        return output

    # --------------------------------------------------------------- IMAGE
    if itype == "image":
        _log("Running image stego analysis...")

        # 1. Metadata
        from .stego import image_metadata
        meta = image_metadata(input_path)
        output["results"]["metadata"] = meta
        if _add_flags("image_metadata", meta.get("flags", [])):
            return output

        # 2. QR decode
        from .stego import qr_decode_robust
        qr_result = qr_decode_robust(input_path)
        if qr_result:
            flags = detector.extract_all(qr_result)
            output["results"]["qr"] = qr_result
            _add_flags("qr_decode", flags)
            if flags:
                return output

        # 3. LSB extraction
        from .stego import image_lsb_extract, image_stegsolve
        for ch in ["R", "G", "B", "RGB"]:
            data = image_lsb_extract(input_path, channels=ch)
            if not data.startswith(b"ERROR"):
                text = data.decode("utf-8", errors="replace")
                flags = detector.extract_all(text)
                output["results"][f"lsb_{ch}"] = text[:200]
                if _add_flags(f"image_lsb_{ch}", flags):
                    return output

        # 4. Stegsolve all variations
        variations = image_stegsolve(input_path)
        output["results"]["stegsolve"] = variations
        for v in variations:
            if _add_flags(f"stegsolve_{v['channel']}_{v['bit']}", v.get("flags", [])):
                return output

        # 5. Channel analysis
        from .stego import image_channel_analysis
        chan = image_channel_analysis(input_path)
        output["results"]["channel_analysis"] = chan
        _add_flags("channel_analysis", chan.get("flags", []))

        return output

    # --------------------------------------------------------------- AUDIO
    if itype == "audio":
        _log("Running audio stego analysis...")

        from .stego import audio_lsb, audio_spectrogram, audio_morse

        # 1. LSB
        data = audio_lsb(input_path)
        if not data.startswith(b"ERROR"):
            text = data.decode("utf-8", errors="replace")
            flags = detector.extract_all(text)
            output["results"]["audio_lsb"] = text[:200]
            if _add_flags("audio_lsb", flags):
                return output

        # 2. Spectrogram
        spec_path = input_path + "_spectrogram.png"
        spec = audio_spectrogram(input_path, output_path=spec_path)
        output["results"]["spectrogram"] = spec
        _add_flags("spectrogram", spec.get("flags", []))

        # 3. Morse
        morse_text = audio_morse(input_path)
        output["results"]["morse"] = morse_text
        flags = detector.extract_all(morse_text)
        _add_flags("audio_morse", flags)

        # 4. Strings in raw audio
        from .forensics import extract_strings
        strings = extract_strings(input_path, min_len=6)
        flags = detector.extract_all("\n".join(strings))
        _add_flags("audio_strings", flags)

        return output

    # --------------------------------------------------------------- MEMORY
    if itype == "memory_dump":
        _log("Running memory dump analysis...")

        from .forensics import memory_string_search, memory_xor_scan

        # 1. Scan for flags in plaintext
        from .forensics import scan_for_flags
        flags_found = scan_for_flags(input_path, flag_regex=flag_regex)
        output["results"]["plain_flags"] = flags_found
        all_flags = [r["value"] for r in flags_found if "value" in r]
        if _add_flags("memory_plain_scan", all_flags):
            return output

        # 2. XOR brute force
        xor_results = memory_xor_scan(input_path, flag_regex=flag_regex)
        output["results"]["xor_scan"] = xor_results
        for r in xor_results:
            if _add_flags(f"memory_xor_key_{r.get('key')}", [r.get("flag", "")]):
                return output

        return output

    # --------------------------------------------------------------- ARCHIVE
    if itype == "archive":
        _log("Analysing archive...")

        from .forensics import check_archive
        arch = check_archive(input_path)
        output["results"]["archive"] = arch
        _add_flags("archive_contents", arch.get("flags", []))
        return output

    # --------------------------------------------------------------- APK
    if itype == "apk":
        _log("Analysing APK...")

        from .forensics import apk_extract
        apk = apk_extract(input_path)
        output["results"]["apk"] = apk
        _add_flags("apk_strings", apk.get("flags", []))
        return output

    # --------------------------------------------------------------- BINARY / TEXT
    if itype in ("binary", "text", "unknown"):
        _log(f"Running generic analysis on {itype}...")

        # 1. Scan for flags directly
        from .forensics import scan_for_flags, extract_strings
        flags_found = scan_for_flags(input_path, flag_regex=flag_regex)
        output["results"]["flag_scan"] = flags_found
        all_flags = [r["value"] for r in flags_found if "value" in r]
        if _add_flags("flag_scan", all_flags):
            return output

        # 2. XOR brute force
        from .crypto import xor_bruteforce
        try:
            with open(input_path, "rb") as f:
                data = f.read()
            xor_results = xor_bruteforce(data, flag_regex=flag_regex)
            output["results"]["xor_brute"] = xor_results[:5]
            for r in xor_results:
                if _add_flags(f"xor_key_{r['key']}", r.get("flags_found", [])):
                    return output
        except Exception:
            pass

        # 3. Try common encodings if text
        if itype == "text":
            try:
                with open(input_path, encoding="utf-8", errors="replace") as f:
                    content = f.read()
                from .crypto import try_all_encodings, base64_chain_decode
                enc_results = try_all_encodings(content.strip())
                for er in enc_results:
                    flags = detector.extract_all(er.get("result", ""))
                    _add_flags(f"encoding_{er['method']}", flags)

                chain = base64_chain_decode(content.strip())
                for step in chain:
                    flags = detector.extract_all(step)
                    if _add_flags("b64_chain", flags):
                        return output
            except Exception:
                pass

        return output

    # ----------------------------------------------------------- STRING INPUT
    if itype == "string":
        _log("Treating as string input...")

        s = input_path
        from .crypto import try_all_encodings, base64_chain_decode, caesar_brute

        # Direct check
        flags = detector.extract_all(s)
        _add_flags("direct", flags)

        # Encodings
        for er in try_all_encodings(s):
            flags = detector.extract_all(er.get("result", ""))
            _add_flags(f"encoding_{er['method']}", flags)

        # b64 chain
        for step in base64_chain_decode(s):
            flags = detector.extract_all(step)
            _add_flags("b64_chain", flags)

        # Caesar
        for r in caesar_brute(s):
            if r["flags"]:
                _add_flags(f"caesar_{r['shift']}", r["flags"])

        return output

    return output
