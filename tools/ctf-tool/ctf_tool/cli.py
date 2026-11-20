"""CTF Tool — Unified CLI entry point."""

import argparse
import json
import sys
import os

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    _HAS_COLOR = True
except ImportError:
    _HAS_COLOR = False
    class Fore:
        GREEN = YELLOW = RED = CYAN = MAGENTA = WHITE = RESET = ""
    class Style:
        BRIGHT = RESET_ALL = ""


def _ok(msg):    print(f"{Fore.GREEN}{Style.BRIGHT}[+]{Style.RESET_ALL} {msg}")
def _info(msg):  print(f"{Fore.CYAN}[*]{Style.RESET_ALL} {msg}")
def _warn(msg):  print(f"{Fore.YELLOW}[!]{Style.RESET_ALL} {msg}")
def _err(msg):   print(f"{Fore.RED}[-]{Style.RESET_ALL} {msg}")
def _flag(msg):  print(f"{Fore.GREEN}{Style.BRIGHT}[FLAG] {msg}{Style.RESET_ALL}")


def _print_results(results: dict, output_file: str = None):
    """Print structured results, highlight flags."""
    flags = results.get("flags_found") or results.get("flags") or []
    if flags:
        for f in flags:
            _flag(f)
    else:
        _warn("No flags found in output.")

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, default=str)
        _info(f"Full results saved to: {output_file}")


# ---------------------------------------------------------------------------
# Subcommand handlers
# ---------------------------------------------------------------------------

def cmd_auto(args):
    """Auto-detect and solve."""
    from .auto import auto_solve
    _info(f"Auto-solving: {args.input}")
    results = auto_solve(args.input, flag_regex=args.flag_regex, verbose=True)
    _info(f"Detected type: {results['detected_type']}")
    _info(f"Solvers tried: {', '.join(results['solvers_tried'])}")
    _print_results(results, args.output)


def cmd_triage(args):
    """Gather structured evidence for reasoning (does not solve)."""
    from .triage import triage
    _info(f"Triaging: {args.path}")
    report = triage(args.path, flag_regex=args.flag_regex)
    s = report["summary"]

    _info(f"Files: {s['file_count']}   Categories: {dict(s['categories'])}")
    for fl in s["flag_candidates"]:
        _flag(fl)
    for u in s["urls"]:
        _ok(f"url: {u}")
    for h in s["nc_hosts"]:
        _ok(f"service: {h}")

    print()
    for r in report["files"]:
        if "error" in r:
            continue
        line = (f"{r['file']}  [{r['category_hint']}]  "
                f"{r.get('size', 0)}B  ent={r.get('entropy')}  {r.get('type','')}")
        _info(line)
        if r.get("keywords"):
            print(f"      keywords: {', '.join(r['keywords'])}")
        if r.get("hashes"):
            print(f"      hashes:   {', '.join(r['hashes'])}")
        if r.get("b64_blobs"):
            print(f"      b64:      {r['b64_blobs']}")
        for fl in r.get("flag_candidates", []):
            _flag(fl)

    if args.output:
        import json as _json
        with open(args.output, "w", encoding="utf-8") as f:
            _json.dump(report, f, indent=2, default=str)
        _info(f"Full report saved to: {args.output}")


def cmd_flagfind(args):
    """Recursively hunt for flags across a directory or file."""
    from .flagfind import flagfind
    _info(f"Hunting for flags in: {args.path}")
    hits = flagfind(args.path, flag_regex=args.flag_regex,
                    deep_strings=not args.no_strings)
    if not hits:
        _warn("No flags found. Move to a category-specific solver (crypto/web/stego/forensics).")
    else:
        for h in hits:
            _flag(f"{h['value']}  [{h['encoding']}]  <- {h['file']}")
        _info(f"{len(hits)} unique candidate(s). Verify format before submitting.")
    if args.output:
        _print_results({"flags_found": [h["value"] for h in hits], "hits": hits},
                       args.output)


# ── CRYPTO ──────────────────────────────────────────────────────────────────

def cmd_crypto_xor(args):
    from .crypto import xor_bruteforce, xor_brute_multibyte, xor_decrypt
    with open(args.file, "rb") as f:
        data = f.read()

    if args.key:
        key = bytes.fromhex(args.key) if all(c in "0123456789abcdefABCDEF" for c in args.key) \
              else args.key.encode()
        result = xor_decrypt(data, key)
        text = result.decode("utf-8", errors="replace")
        print(text[:500])
        from .flag_detector import scan_text
        flags = [r["value"] for r in scan_text(text)]
        for f in flags:
            _flag(f)
    elif args.keylen and args.keylen > 1:
        results = xor_brute_multibyte(data, max_keylen=args.keylen,
                                       flag_regex=args.flag_regex)
        for r in results[:5]:
            _ok(f"keylen={r['keylen']} key={r['key']}: {r['result_text'][:100]}")
            for flag in r.get("flags_found", []):
                _flag(flag)
    else:
        results = xor_bruteforce(data, flag_regex=args.flag_regex)
        for r in results[:10]:
            _ok(f"key={r['key_hex']}: {r['result_text'][:80]}")
            for flag in r.get("flags_found", []):
                _flag(flag)


def cmd_crypto_b64(args):
    from .crypto import base64_chain_decode, try_all_encodings
    s = args.string_or_file
    if os.path.exists(s):
        with open(s, encoding="utf-8", errors="replace") as f:
            s = f.read().strip()

    chain = base64_chain_decode(s)
    for i, val in enumerate(chain):
        _info(f"Depth {i}: {val[:200]}")
        from .flag_detector import FlagDetector
        flags = FlagDetector().extract_all(val)
        for fl in flags:
            _flag(fl)

    if not args.chain_only:
        _info("Also trying other encodings:")
        for r in try_all_encodings(s):
            method = r.get("method")
            res = r.get("result", "")[:100]
            flags = r.get("flags", [])
            _ok(f"{method}: {res}")
            for fl in flags:
                _flag(fl)


def cmd_crypto_vigenere(args):
    from .crypto import vigenere_decrypt, vigenere_brute
    with open(args.file, encoding="utf-8", errors="replace") as f:
        text = f.read()

    if args.key:
        result = vigenere_decrypt(text, args.key)
        print(result[:500])
        from .flag_detector import FlagDetector
        for fl in FlagDetector().extract_all(result):
            _flag(fl)
    else:
        results = vigenere_brute(text, max_keylen=args.keylen or 20)
        for r in results[:5]:
            _ok(f"keylen={r['keylen']} key={r['key']} ic={r['ic_score']:.4f}")
            print(f"  {r['result'][:100]}")
            for fl in r.get("flags", []):
                _flag(fl)


def cmd_crypto_hash(args):
    from .crypto import hash_identify, hash_crack_wordlist, hash_crack_common
    h = args.hash_str
    algo = hash_identify(h)
    _info(f"Hash type: {algo}")

    result = hash_crack_common(h, algorithm=algo)
    if result:
        _flag(f"Cracked: {result}")
        return

    if args.wordlist:
        _info(f"Cracking against wordlist: {args.wordlist}")
        result = hash_crack_wordlist(h, args.wordlist, algorithm=algo)
        if result:
            _flag(f"Cracked: {result}")
        else:
            _warn("Not found in wordlist.")
    else:
        _warn("No wordlist provided. Use --wordlist <path>")


def cmd_crypto_caesar(args):
    from .crypto import caesar_brute
    results = caesar_brute(args.text)
    for r in results:
        line = f"shift={r['shift']:2d}: {r['result'][:80]}"
        if r["flags"]:
            _flag(f"shift={r['shift']}: {r['result'][:120]}")
        else:
            _info(line)


def cmd_crypto_analyze(args):
    from .crypto import analyze_cipher
    with open(args.file, encoding="utf-8", errors="replace") as f:
        text = f.read()
    result = analyze_cipher(text)
    for k, v in result.items():
        _info(f"  {k}: {v}")


# ── FORENSICS ───────────────────────────────────────────────────────────────

def cmd_forensics_strings(args):
    from .forensics import extract_strings
    strings = extract_strings(args.file, min_len=args.min_len or 4,
                              flag_regex=args.flag_regex)
    for s in strings:
        from .flag_detector import FlagDetector
        if FlagDetector().is_flag(s):
            _flag(s)
        else:
            print(s)
    _info(f"Total strings: {len(strings)}")


def cmd_forensics_scan(args):
    from .forensics import scan_for_flags
    results = scan_for_flags(args.file, flag_regex=args.flag_regex)
    if not results:
        _warn("No flags found.")
    for r in results:
        if "error" in r:
            _err(r["error"])
        else:
            _flag(f"[{r.get('encoding','?')}] offset={r.get('offset',0):#x}: {r.get('value','')}")


def cmd_forensics_extract(args):
    from .forensics import extract_embedded
    files = extract_embedded(args.file, output_dir=args.output)
    if files:
        for f in files:
            _ok(f"Extracted: {f}")
    else:
        _warn("No embedded files found.")


def cmd_forensics_memory(args):
    from .forensics import memory_xor_scan, scan_for_flags
    _info("Scanning plaintext...")
    plain = scan_for_flags(args.dump)
    for r in plain:
        if "value" in r:
            _flag(r["value"])

    keys = None
    if args.xor_keys:
        keys = [int(k, 0) for k in args.xor_keys.split(",")]
    _info("XOR scanning...")
    results = memory_xor_scan(args.dump, xor_keys=keys)
    for r in results:
        _flag(f"key={r.get('key_hex')}: {r.get('flag','')}")


def cmd_forensics_apk(args):
    from .forensics import apk_extract
    result = apk_extract(args.apk_file, output_dir=args.output)
    _info(f"Files in APK: {len(result['files'])}")
    for flag in result.get("flags", []):
        _flag(flag)
    if result.get("error"):
        _err(result["error"])


# ── WEB ─────────────────────────────────────────────────────────────────────

def cmd_web_recon(args):
    from .web import check_headers, check_wellknown
    _info(f"Recon: {args.url}")
    h = check_headers(args.url)
    _info(f"Status: {h.get('status')}")
    for k, v in h.get("interesting", {}).items():
        _info(f"  {k}: {v}")
    for f in h.get("flags", []):
        _flag(f)
    _info("Checking well-known paths...")
    wk = check_wellknown(args.url)
    for path, data in wk.items():
        _ok(f"{path} [{data.get('status')}] size={data.get('size')}")
        for f in data.get("flags", []):
            _flag(f)


def cmd_web_dirbust(args):
    from .web import dir_enum
    wordlist = None
    if args.wordlist:
        with open(args.wordlist, encoding="utf-8", errors="ignore") as f:
            wordlist = [l.strip() for l in f if l.strip()]
    results = dir_enum(args.url, wordlist=wordlist)
    for r in results:
        _ok(f"[{r['status']}] {r['url']} ({r['size']} bytes)")
        for f in r.get("flags", []):
            _flag(f)


def cmd_web_jwt_decode(args):
    from .web import jwt_decode
    result = jwt_decode(args.token)
    if "error" in result:
        _err(result["error"])
    else:
        _info(f"Header:  {json.dumps(result['header'])}")
        _info(f"Payload: {json.dumps(result['payload'])}")


def cmd_web_jwt_crack(args):
    from .web import jwt_crack
    _info("Cracking JWT secret...")
    result = jwt_crack(args.token, wordlist_path=args.wordlist)
    if result is not None:
        _flag(f"Secret found: {result!r}")
    else:
        _warn("Secret not found.")


def cmd_web_jwt_forge(args):
    from .web import jwt_forge
    payload = json.loads(args.payload_json)
    token = jwt_forge(payload, args.secret, algorithm=args.algo or "HS256")
    _ok(f"Forged JWT:\n{token}")


def cmd_web_sqli(args):
    from .web import sqli_test
    result = sqli_test(args.url, args.param, method=args.method or "GET")
    if result["vulnerable"]:
        _flag(f"SQLi FOUND! error_based={result['error_based']}")
        for ev in result.get("evidence", []):
            _info(f"  payload={ev.get('payload')} evidence={ev}")
    else:
        _warn("No SQLi detected.")


def cmd_web_ssti(args):
    from .web import ssti_test
    result = ssti_test(args.url, args.param, method=args.method or "GET")
    if result["vulnerable"]:
        _flag(f"SSTI FOUND! engine={result['engine']}")
        for ev in result.get("evidence", []):
            _info(f"  payload={ev.get('payload')}")
    else:
        _warn("No SSTI detected.")


def cmd_web_login_brute(args):
    from .web import login_brute
    wordlist = []
    if args.wordlist:
        with open(args.wordlist, encoding="utf-8", errors="ignore") as f:
            wordlist = [l.strip() for l in f if l.strip()]
    else:
        wordlist = ["password", "admin", "123456", "test", "letmein", "flag"]

    result = login_brute(args.url, args.user_field, args.pass_field,
                          args.user, wordlist)
    if result:
        _flag(f"Password found: {result!r}")
    else:
        _warn("Password not found.")


# ── STEGO ───────────────────────────────────────────────────────────────────

def cmd_stego_image(args):
    from .stego import image_lsb_extract, image_stegsolve, image_metadata, image_channel_analysis
    _info(f"Analysing image: {args.image}")

    meta = image_metadata(args.image)
    for f in meta.get("flags", []):
        _flag(f)

    if args.lsb or args.all:
        ch = args.channel or "RGB"
        data = image_lsb_extract(args.image, channels=ch)
        text = data.decode("utf-8", errors="replace")
        print(text[:200])
        from .flag_detector import FlagDetector
        for fl in FlagDetector().extract_all(text):
            _flag(fl)

    if args.all:
        _info("Running all stegsolve variations...")
        for v in image_stegsolve(args.image):
            if v.get("flags"):
                for fl in v["flags"]:
                    _flag(f"ch={v['channel']} bit={v['bit']}: {fl}")

        _info("Channel analysis...")
        chan = image_channel_analysis(args.image)
        for fl in chan.get("flags", []):
            _flag(fl)


def cmd_stego_audio(args):
    from .stego import audio_lsb, audio_spectrogram, audio_morse
    _info(f"Analysing audio: {args.audio}")

    if args.lsb or args.all:
        data = audio_lsb(args.audio)
        text = data.decode("utf-8", errors="replace")
        print(text[:200])
        from .flag_detector import FlagDetector
        for fl in FlagDetector().extract_all(text):
            _flag(fl)

    if args.spectrogram or args.all:
        spec_path = args.audio + "_spec.png"
        spec = audio_spectrogram(args.audio, output_path=spec_path)
        _info(f"Spectrogram saved: {spec.get('output')}")

    if args.morse or args.all:
        decoded = audio_morse(args.audio)
        _info(f"Morse decoded: {decoded}")
        from .flag_detector import FlagDetector
        for fl in FlagDetector().extract_all(decoded):
            _flag(fl)


def cmd_stego_qr(args):
    from .stego import qr_decode_robust, qr_repair_and_decode
    _info(f"Decoding QR: {args.image}")
    result = qr_decode_robust(args.image)
    if result:
        _ok(f"Decoded: {result}")
        from .flag_detector import FlagDetector
        for fl in FlagDetector().extract_all(result):
            _flag(fl)
    else:
        _info("Trying repair...")
        result = qr_repair_and_decode(args.image)
        if result:
            _ok(f"Repaired & decoded: {result}")
        else:
            _warn("QR decode failed.")


# ── MISC ────────────────────────────────────────────────────────────────────

def cmd_misc_morse(args):
    from .stego import morse_decode
    from .misc import brainfuck_run
    if args.decode:
        print(morse_decode(args.text))
    else:
        # Encode
        _MORSE_ENC = {v: k for k, v in {
            ".-":"A","-...":"B","-.-.":"C","-..":"D",".":"E",
            "..-.":"F","--.":"G","....":"H","..":"I",".---":"J",
            "-.-":"K",".-..":"L","--":"M","-.":"N","---":"O",
            ".--.":"P","--.-":"Q",".-.":"R","...":"S","-":"T",
            "..-":"U","...-":"V",".--":"W","-..-":"X","-.--":"Y",
            "--..":"Z","-----":"0",".----":"1","..---":"2",
            "...--":"3","....-":"4",".....":"5","-....":"6",
            "--...":"7","---..":"8","----.":"9",
        }.items()}
        encoded = " ".join(_MORSE_ENC.get(c.upper(), "?") for c in args.text)
        print(encoded)


def cmd_misc_bacon(args):
    from .misc import bacon_decode
    result = bacon_decode(args.text)
    _ok(f"Bacon decoded: {result}")
    from .flag_detector import FlagDetector
    for fl in FlagDetector().extract_all(result):
        _flag(fl)


def cmd_misc_graph(args):
    import json
    from .misc import graph_walk, graph_edge_labels_decode
    with open(args.json_file, encoding="utf-8") as f:
        graph = json.load(f)
    _info("Walking graph paths...")
    results = graph_walk(graph, flag_regex=args.flag_regex)
    for r in results[:20]:
        _info(f"Path: {' -> '.join(r['path'][:8])}")
        _info(f"  Labels: {r['label_string'][:80]}")
        for fl in r.get("flags", []):
            _flag(fl)
    if not results:
        _warn("No flag-matching paths found.")
        labels = graph_edge_labels_decode(graph)
        _info(f"Edge labels: {labels[:20]}")


def cmd_misc_coords(args):
    from .misc import extract_coordinates
    text = args.text_or_file
    if os.path.exists(text):
        with open(text, encoding="utf-8", errors="replace") as f:
            text = f.read()
    coords = extract_coordinates(text)
    if coords:
        for c in coords:
            _ok(f"[{c['type']}] {c['raw']} -> {c['parsed']}")
    else:
        _warn("No coordinates found.")


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="ctf_tool",
        description="CTF Tool — Unified solver for crypto/web/forensics/stego/misc",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ctf_tool auto challenge.png
  ctf_tool auto http://target.com/
  ctf_tool crypto xor challenge.bin --brute
  ctf_tool crypto b64 "SGVsbG8gV29ybGQ="
  ctf_tool crypto hash 5f4dcc3b5aa765d61d8327deb882cf99 --wordlist rockyou.txt
  ctf_tool forensics scan dump.bin
  ctf_tool forensics memory dump.dmp
  ctf_tool web recon http://target.com
  ctf_tool web jwt decode eyJ...
  ctf_tool web sqli "http://t.com/login?id=1" --param id
  ctf_tool stego image flag.png --all
  ctf_tool stego qr qrcode.png
  ctf_tool misc morse "... --- ..."  --decode
  ctf_tool misc graph graph.json
""")

    p.add_argument("--flag-regex", metavar="PATTERN",
                   help="Custom regex for flag detection")
    p.add_argument("--output", "-o", metavar="FILE",
                   help="Save full results to JSON file")
    p.add_argument("--verbose", "-v", action="store_true")

    sub = p.add_subparsers(dest="command", required=True)

    # auto
    auto_p = sub.add_parser("auto", help="Auto-detect and solve")
    auto_p.add_argument("input", help="File path or URL")

    # flagfind
    ff_p = sub.add_parser("flagfind", help="Recursively hunt flags in a dir/file")
    ff_p.add_argument("path", help="Directory or file to scan")
    ff_p.add_argument("--no-strings", action="store_true",
                      help="Skip the strings pass (faster, plain/hex/b64 only)")

    # triage
    tr_p = sub.add_parser("triage", help="Gather structured evidence (for reasoning, not solving)")
    tr_p.add_argument("path", help="Directory or file to analyze")

    # crypto
    crypto_p = sub.add_parser("crypto", help="Cryptography solvers")
    crypto_sub = crypto_p.add_subparsers(dest="crypto_cmd", required=True)

    xor_p = crypto_sub.add_parser("xor", help="XOR decrypt/brute")
    xor_p.add_argument("file", help="Input file")
    xor_p.add_argument("--key", help="Hex or ASCII key")
    xor_p.add_argument("--brute", action="store_true", help="Brute-force single byte")
    xor_p.add_argument("--keylen", type=int, help="Max key length for multi-byte brute")

    b64_p = crypto_sub.add_parser("b64", help="Base64 chain decode")
    b64_p.add_argument("string_or_file", help="Base64 string or file path")
    b64_p.add_argument("--chain-only", action="store_true")

    vig_p = crypto_sub.add_parser("vigenere", help="Vigenere decrypt/brute")
    vig_p.add_argument("file")
    vig_p.add_argument("--key")
    vig_p.add_argument("--keylen", type=int)

    hash_p = crypto_sub.add_parser("hash", help="Hash identification and cracking")
    hash_p.add_argument("hash_str", metavar="HASH")
    hash_p.add_argument("--wordlist")
    hash_p.add_argument("--algo", default="auto")

    cae_p = crypto_sub.add_parser("caesar", help="Caesar brute force")
    cae_p.add_argument("text")

    ana_p = crypto_sub.add_parser("analyze", help="Analyze cipher type")
    ana_p.add_argument("file")

    # forensics
    for_p = sub.add_parser("forensics", help="Forensics solvers")
    for_sub = for_p.add_subparsers(dest="for_cmd", required=True)

    str_p = for_sub.add_parser("strings", help="Extract strings")
    str_p.add_argument("file")
    str_p.add_argument("--min-len", type=int, default=4)

    sc_p = for_sub.add_parser("scan", help="Scan for flags")
    sc_p.add_argument("file")

    ex_p = for_sub.add_parser("extract", help="Extract embedded files")
    ex_p.add_argument("file")
    ex_p.add_argument("--output", metavar="DIR")

    mem_p = for_sub.add_parser("memory", help="Memory dump analysis")
    mem_p.add_argument("dump")
    mem_p.add_argument("--xor-keys", metavar="K1,K2,...")

    apk_p = for_sub.add_parser("apk", help="APK analysis")
    apk_p.add_argument("apk_file")
    apk_p.add_argument("--output", metavar="DIR")

    # web
    web_p = sub.add_parser("web", help="Web attack solvers")
    web_sub = web_p.add_subparsers(dest="web_cmd", required=True)

    recon_p = web_sub.add_parser("recon", help="Web recon")
    recon_p.add_argument("url")

    dir_p = web_sub.add_parser("dirbust", help="Directory enumeration")
    dir_p.add_argument("url")
    dir_p.add_argument("--wordlist")

    jwt_p = web_sub.add_parser("jwt", help="JWT operations")
    jwt_sub = jwt_p.add_subparsers(dest="jwt_cmd", required=True)
    jwt_dec = jwt_sub.add_parser("decode")
    jwt_dec.add_argument("token")
    jwt_crack_p = jwt_sub.add_parser("crack")
    jwt_crack_p.add_argument("token")
    jwt_crack_p.add_argument("--wordlist")
    jwt_forge_p = jwt_sub.add_parser("forge")
    jwt_forge_p.add_argument("payload_json")
    jwt_forge_p.add_argument("--secret", required=True)
    jwt_forge_p.add_argument("--algo", default="HS256")

    sqli_p = web_sub.add_parser("sqli", help="SQL injection test")
    sqli_p.add_argument("url")
    sqli_p.add_argument("--param", required=True)
    sqli_p.add_argument("--method", default="GET")

    ssti_p = web_sub.add_parser("ssti", help="SSTI test")
    ssti_p.add_argument("url")
    ssti_p.add_argument("--param", required=True)
    ssti_p.add_argument("--method", default="GET")

    lb_p = web_sub.add_parser("login-brute", help="Login brute force")
    lb_p.add_argument("url")
    lb_p.add_argument("--user", required=True)
    lb_p.add_argument("--user-field", required=True)
    lb_p.add_argument("--pass-field", required=True)
    lb_p.add_argument("--wordlist")

    # stego
    stego_p = sub.add_parser("stego", help="Steganography solvers")
    stego_sub = stego_p.add_subparsers(dest="stego_cmd", required=True)

    img_p = stego_sub.add_parser("image", help="Image stego")
    img_p.add_argument("image")
    img_p.add_argument("--channel", default="RGB")
    img_p.add_argument("--lsb", action="store_true")
    img_p.add_argument("--all", action="store_true")

    aud_p = stego_sub.add_parser("audio", help="Audio stego")
    aud_p.add_argument("audio")
    aud_p.add_argument("--spectrogram", action="store_true")
    aud_p.add_argument("--lsb", action="store_true")
    aud_p.add_argument("--morse", action="store_true")
    aud_p.add_argument("--all", action="store_true")

    qr_p = stego_sub.add_parser("qr", help="QR code decode/repair")
    qr_p.add_argument("image")

    # misc
    misc_p = sub.add_parser("misc", help="Misc solvers")
    misc_sub = misc_p.add_subparsers(dest="misc_cmd", required=True)

    morse_p = misc_sub.add_parser("morse", help="Morse code encode/decode")
    morse_p.add_argument("text")
    morse_p.add_argument("--decode", action="store_true")
    morse_p.add_argument("--encode", action="store_true")

    bacon_pr = misc_sub.add_parser("bacon", help="Bacon cipher decode")
    bacon_pr.add_argument("text")

    graph_pr = misc_sub.add_parser("graph", help="Graph traversal")
    graph_pr.add_argument("json_file")

    coord_p = misc_sub.add_parser("coords", help="Extract coordinates")
    coord_p.add_argument("text_or_file")

    return p


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

_DISPATCH = {
    "auto":              cmd_auto,
    "flagfind":          cmd_flagfind,
    "triage":            cmd_triage,
    # crypto
    ("crypto", "xor"):        cmd_crypto_xor,
    ("crypto", "b64"):        cmd_crypto_b64,
    ("crypto", "vigenere"):   cmd_crypto_vigenere,
    ("crypto", "hash"):       cmd_crypto_hash,
    ("crypto", "caesar"):     cmd_crypto_caesar,
    ("crypto", "analyze"):    cmd_crypto_analyze,
    # forensics
    ("forensics", "strings"): cmd_forensics_strings,
    ("forensics", "scan"):    cmd_forensics_scan,
    ("forensics", "extract"): cmd_forensics_extract,
    ("forensics", "memory"):  cmd_forensics_memory,
    ("forensics", "apk"):     cmd_forensics_apk,
    # web
    ("web", "recon"):         cmd_web_recon,
    ("web", "dirbust"):       cmd_web_dirbust,
    ("web", "jwt", "decode"): cmd_web_jwt_decode,
    ("web", "jwt", "crack"):  cmd_web_jwt_crack,
    ("web", "jwt", "forge"):  cmd_web_jwt_forge,
    ("web", "sqli"):          cmd_web_sqli,
    ("web", "ssti"):          cmd_web_ssti,
    ("web", "login-brute"):   cmd_web_login_brute,
    # stego
    ("stego", "image"):       cmd_stego_image,
    ("stego", "audio"):       cmd_stego_audio,
    ("stego", "qr"):          cmd_stego_qr,
    # misc
    ("misc", "morse"):        cmd_misc_morse,
    ("misc", "bacon"):        cmd_misc_bacon,
    ("misc", "graph"):        cmd_misc_graph,
    ("misc", "coords"):       cmd_misc_coords,
}


def main():
    parser = build_parser()
    args = parser.parse_args()

    # Propagate global options down to subcommand args
    if not hasattr(args, "flag_regex"):
        args.flag_regex = None
    if not hasattr(args, "output"):
        args.output = None

    cmd = args.command
    if cmd == "auto":
        cmd_auto(args)
        return
    if cmd == "flagfind":
        cmd_flagfind(args)
        return
    if cmd == "triage":
        cmd_triage(args)
        return

    sub2 = getattr(args, f"{cmd}_cmd", None)
    sub3_map = {"web": "jwt_cmd", "stego": None, "misc": None}

    if cmd == "web" and sub2 == "jwt":
        jwt_cmd = getattr(args, "jwt_cmd", None)
        fn = _DISPATCH.get(("web", "jwt", jwt_cmd))
    else:
        fn = _DISPATCH.get((cmd, sub2))

    if fn:
        fn(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
