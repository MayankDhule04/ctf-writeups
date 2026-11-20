"""Crypto solvers — XOR, Vigenere, Caesar, hashes, AES, encodings."""

import base64
import hashlib
import hmac
import itertools
import math
import re
import string
from typing import List, Dict, Optional

from .utils import (
    xor_single, xor_key, b64decode_safe, try_common_encodings,
    caesar_decrypt, rot13, ic, extract_printable_strings, is_printable
)
from .flag_detector import FlagDetector

_detector = FlagDetector()

# ---------------------------------------------------------------------------
# XOR
# ---------------------------------------------------------------------------

def xor_decrypt(data: bytes, key: bytes) -> bytes:
    """XOR data with cycling key."""
    return xor_key(data, key)


def xor_bruteforce(data: bytes, known_prefix: str = "CHAKRA{",
                   flag_regex: str = None) -> List[Dict]:
    """Brute-force all 256 single-byte XOR keys.

    Args:
        data: Bytes to decrypt
        known_prefix: Expected flag prefix to check for
        flag_regex: Optional override for flag detection

    Returns:
        List of {key, key_hex, result_text, flags_found}
    """
    detector = FlagDetector(extra_regex=flag_regex) if flag_regex else _detector
    results = []
    for k in range(256):
        decrypted = xor_single(data, k)
        try:
            text = decrypted.decode("utf-8", errors="replace")
        except Exception:
            text = decrypted.decode("latin-1", errors="replace")

        flags = detector.extract_all(text)
        prefix_match = known_prefix and text.startswith(known_prefix)

        if flags or prefix_match or is_printable(text, 0.85):
            results.append({
                "key":        k,
                "key_hex":    hex(k),
                "result_text": text[:200],
                "flags_found": flags,
                "printable":  is_printable(text, 0.85),
            })
    results.sort(key=lambda x: (-len(x["flags_found"]), -int(x["printable"])))
    return results


def xor_brute_multibyte(data: bytes, max_keylen: int = 16,
                         known_prefix: str = "CHAKRA{",
                         flag_regex: str = None) -> List[Dict]:
    """Brute-force multi-byte XOR keys using Index of Coincidence + Kasiski.

    Returns top candidates sorted by IC score.
    """
    detector = FlagDetector(extra_regex=flag_regex) if flag_regex else _detector
    results = []

    for keylen in range(1, max_keylen + 1):
        # Split into keylen columns
        columns = [data[i::keylen] for i in range(keylen)]
        key_bytes = []
        for col in columns:
            # For each column, pick byte that maximises English IC
            best_k, best_ic = 0, -1
            for k in range(256):
                decoded_col = xor_single(col, k)
                try:
                    col_text = decoded_col.decode("latin-1")
                except Exception:
                    continue
                score = ic(col_text)
                if score > best_ic:
                    best_ic = score
                    best_k = k
            key_bytes.append(best_k)

        key = bytes(key_bytes)
        decrypted = xor_key(data, key)
        try:
            text = decrypted.decode("utf-8", errors="replace")
        except Exception:
            text = decrypted.decode("latin-1", errors="replace")

        flags = detector.extract_all(text)
        if flags or (known_prefix and text.startswith(known_prefix)) or is_printable(text, 0.80):
            results.append({
                "keylen":     keylen,
                "key":        key.hex(),
                "key_bytes":  list(key),
                "result_text": text[:300],
                "flags_found": flags,
            })
            if flags:
                break  # found something good

    return results


# ---------------------------------------------------------------------------
# Base64 chain
# ---------------------------------------------------------------------------

def base64_chain_decode(s: str, max_depth: int = 10) -> List[str]:
    """Repeatedly base64-decode until no longer valid or max_depth reached.

    Returns list of all intermediate values (as strings).
    """
    results = [s]
    current = s.strip()
    for _ in range(max_depth):
        decoded = b64decode_safe(current)
        if not decoded:
            break
        try:
            text = decoded.decode("utf-8")
        except Exception:
            text = decoded.decode("latin-1", errors="replace")
        if text == current:
            break
        results.append(text)
        current = text.strip()
    return results


def decode_hex_chain(s: str) -> List[str]:
    """Try hex decode and optionally chained with base64."""
    results = []
    s = s.strip().replace(" ", "").replace("0x", "")
    try:
        decoded = bytes.fromhex(s)
        text = decoded.decode("utf-8", errors="replace")
        results.append(text)
        # Try further b64 chain
        chain = base64_chain_decode(text.strip())
        results.extend(chain[1:])
    except Exception:
        pass
    return results


def try_all_encodings(s: str) -> List[Dict]:
    """Wrapper around utils.try_common_encodings + flag detection."""
    results = try_common_encodings(s)
    for r in results:
        r["flags"] = _detector.extract_all(r.get("result", ""))
    return results


# ---------------------------------------------------------------------------
# Classical ciphers
# ---------------------------------------------------------------------------

def caesar_brute(ciphertext: str) -> List[Dict]:
    """Try all 26 Caesar cipher shifts. Returns {shift, result, flags}."""
    results = []
    for shift in range(26):
        text = caesar_decrypt(ciphertext, shift)
        flags = _detector.extract_all(text)
        results.append({"shift": shift, "result": text, "flags": flags})
    return results


def vigenere_decrypt(ciphertext: str, key: str) -> str:
    """Decrypt Vigenere cipher with known key."""
    key = key.upper()
    result = []
    ki = 0
    for c in ciphertext:
        if c.isalpha():
            shift = ord(key[ki % len(key)]) - ord("A")
            if c.isupper():
                result.append(chr((ord(c) - ord("A") - shift) % 26 + ord("A")))
            else:
                result.append(chr((ord(c) - ord("a") - shift) % 26 + ord("a")))
            ki += 1
        else:
            result.append(c)
    return "".join(result)


def vigenere_brute(ciphertext: str, max_keylen: int = 20,
                   flag_regex: str = None) -> List[Dict]:
    """Brute-force Vigenere key length via IC, then each column.

    Returns candidates sorted by IC score.
    """
    detector = FlagDetector(extra_regex=flag_regex) if flag_regex else _detector
    alpha_only = "".join(c for c in ciphertext.upper() if c.isalpha())
    if len(alpha_only) < 20:
        return []

    # Score each key length
    kl_scores = []
    for kl in range(1, min(max_keylen + 1, len(alpha_only) // 2)):
        columns = [alpha_only[i::kl] for i in range(kl)]
        avg_ic = sum(ic(col) for col in columns) / kl
        kl_scores.append((kl, avg_ic))
    kl_scores.sort(key=lambda x: -x[1])

    results = []
    for kl, score in kl_scores[:5]:
        columns = [alpha_only[i::kl] for i in range(kl)]
        key_chars = []
        for col in columns:
            best_k, best_score = "A", -1
            for k in range(26):
                shifted = "".join(chr((ord(c) - k) % 26 + ord("A")) for c in col)
                s = ic(shifted)
                if s > best_score:
                    best_score = s
                    best_k = chr(k + ord("A"))
            key_chars.append(best_k)
        key = "".join(key_chars)
        decrypted = vigenere_decrypt(ciphertext, key)
        flags = detector.extract_all(decrypted)
        results.append({
            "keylen": kl,
            "key":    key,
            "ic_score": score,
            "result": decrypted[:200],
            "flags":  flags,
        })
        if flags:
            break

    return results


# ---------------------------------------------------------------------------
# Substitution cipher
# ---------------------------------------------------------------------------

_ENGLISH_FREQ = "ETAOINSHRDLCUMWFGYPBVKJXQZ"


def substitution_crack(ciphertext: str, flag_regex: str = None) -> List[Dict]:
    """Simple frequency-analysis substitution crack (returns best guess)."""
    detector = FlagDetector(extra_regex=flag_regex) if flag_regex else _detector
    alpha = "".join(c.upper() for c in ciphertext if c.isalpha())
    if not alpha:
        return []

    freq = {}
    for c in alpha:
        freq[c] = freq.get(c, 0) + 1
    sorted_cipher = sorted(freq, key=freq.get, reverse=True)

    mapping = {}
    for i, c in enumerate(sorted_cipher):
        if i < len(_ENGLISH_FREQ):
            mapping[c] = _ENGLISH_FREQ[i]

    result = []
    for c in ciphertext:
        if c.upper() in mapping:
            sub = mapping[c.upper()]
            result.append(sub if c.isupper() else sub.lower())
        else:
            result.append(c)
    text = "".join(result)
    flags = detector.extract_all(text)
    return [{"method": "frequency_analysis", "result": text, "flags": flags}]


def analyze_cipher(text: str) -> Dict:
    """Analyze ciphertext: IC, bigrams, entropy, guess cipher type."""
    alpha = "".join(c.upper() for c in text if c.isalpha())
    ic_val = ic(alpha) if alpha else 0.0

    # Entropy
    freq = {}
    for c in text:
        freq[c] = freq.get(c, 0) + 1
    total = len(text)
    entropy = 0.0
    if total > 0:
        for cnt in freq.values():
            p = cnt / total
            if p > 0:
                entropy -= p * math.log2(p)

    # Guess
    guess = "unknown"
    if ic_val > 0.065:
        guess = "monoalphabetic_or_plain"
    elif ic_val > 0.045:
        guess = "vigenere_short_key"
    elif ic_val > 0.038:
        guess = "vigenere_long_key"
    else:
        guess = "transposition_or_random"

    # Check if looks like hex
    if re.fullmatch(r"[0-9a-fA-F\s]+", text.strip()):
        guess = "hex_encoded"
    # Check if looks like base64
    if re.fullmatch(r"[A-Za-z0-9+/=\n]+", text.strip()):
        guess = "base64_encoded"

    return {
        "length":   len(text),
        "ic":       round(ic_val, 4),
        "entropy":  round(entropy, 4),
        "guess":    guess,
        "unique_chars": len(freq),
    }


# ---------------------------------------------------------------------------
# Hash cracking
# ---------------------------------------------------------------------------

_HASH_LENGTHS = {
    32:  ["md5"],
    40:  ["sha1"],
    56:  ["sha224"],
    64:  ["sha256"],
    96:  ["sha384"],
    128: ["sha512"],
}


def hash_identify(h: str) -> str:
    """Identify hash type by length."""
    h = h.strip()
    if not re.fullmatch(r"[0-9a-fA-F]+", h):
        if h.startswith("$2"):
            return "bcrypt"
        if h.startswith("$argon2"):
            return "argon2"
        return "unknown"
    types = _HASH_LENGTHS.get(len(h), ["unknown"])
    return types[0]


def _hash_one(s: str, algo: str) -> str:
    try:
        h = hashlib.new(algo)
        h.update(s.encode("utf-8"))
        return h.hexdigest()
    except Exception:
        return ""


def hash_crack_wordlist(hash_str: str, wordlist_path: str,
                         algorithm: str = "auto") -> Optional[str]:
    """Crack a hash against a wordlist file.

    Args:
        hash_str: The hash to crack
        wordlist_path: Path to wordlist file
        algorithm: Hash algorithm or 'auto' to detect

    Returns:
        The cracked plaintext or None
    """
    hash_str = hash_str.strip().lower()
    algo = algorithm
    if algo == "auto":
        algo = hash_identify(hash_str)
    if algo == "unknown":
        algos_to_try = ["md5", "sha1", "sha256", "sha512"]
    else:
        algos_to_try = [algo]

    try:
        with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                word = line.rstrip("\n")
                for a in algos_to_try:
                    if _hash_one(word, a) == hash_str:
                        return word
                    # Try common transforms
                    for transform in [word.lower(), word.upper(),
                                      word.capitalize(), word + "!", word + "1"]:
                        if _hash_one(transform, a) == hash_str:
                            return transform
    except FileNotFoundError:
        pass
    return None


def hash_crack_common(hash_str: str, algorithm: str = "auto") -> Optional[str]:
    """Try a built-in list of common passwords."""
    common = [
        "password", "123456", "admin", "letmein", "qwerty", "abc123",
        "password1", "welcome", "monkey", "dragon", "master", "123456789",
        "1234567890", "sunshine", "princess", "shadow", "superman",
        "michael", "baseball", "football", "iloveyou", "trustno1",
        "secret", "pass", "test", "root", "toor", "flag", "ctf",
    ]
    hash_str = hash_str.strip().lower()
    algo = algorithm if algorithm != "auto" else hash_identify(hash_str)
    if algo == "unknown":
        algos = ["md5", "sha1", "sha256"]
    else:
        algos = [algo]
    for word in common:
        for a in algos:
            if _hash_one(word, a) == hash_str:
                return word
    return None


# ---------------------------------------------------------------------------
# AES
# ---------------------------------------------------------------------------

def aes_decrypt(ciphertext: bytes, key: bytes, mode: str = "ECB",
                iv: bytes = None) -> Optional[bytes]:
    """AES decrypt. Requires pycryptodome.

    Args:
        ciphertext: Encrypted bytes
        key: AES key (16/24/32 bytes)
        mode: 'ECB', 'CBC', 'CTR', 'CFB'
        iv: IV for CBC/CFB (16 bytes)

    Returns:
        Decrypted bytes or None on error
    """
    try:
        from Crypto.Cipher import AES
        from Crypto.Util.Padding import unpad
        mode_map = {
            "ECB": AES.MODE_ECB,
            "CBC": AES.MODE_CBC,
            "CTR": AES.MODE_CTR,
            "CFB": AES.MODE_CFB,
        }
        m = mode_map.get(mode.upper(), AES.MODE_ECB)
        if m == AES.MODE_ECB:
            cipher = AES.new(key, m)
        else:
            cipher = AES.new(key, m, iv or b"\x00" * 16)
        raw = cipher.decrypt(ciphertext)
        # Try unpadding
        try:
            return unpad(raw, 16)
        except Exception:
            return raw
    except ImportError:
        return None
    except Exception:
        return None
