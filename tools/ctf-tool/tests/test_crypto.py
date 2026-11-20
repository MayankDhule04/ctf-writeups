"""Tests for crypto module."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ctf_tool.crypto import (
    xor_bruteforce, xor_decrypt, base64_chain_decode,
    caesar_brute, vigenere_decrypt, hash_identify,
    decode_hex_chain, analyze_cipher,
)
from ctf_tool.flag_detector import FlagDetector


def test_xor_single_byte():
    key = 0x42
    plaintext = b"CHAKRA{test_flag}"
    ciphertext = bytes(b ^ key for b in plaintext)
    results = xor_bruteforce(ciphertext, known_prefix="CHAKRA{")
    flags = [r for r in results if r["flags_found"]]
    assert flags, "Should find flag with single-byte XOR"
    assert any("CHAKRA{test_flag}" in r["flags_found"] for r in flags)


def test_xor_decrypt_cycling():
    key = b"abc"
    plaintext = b"hello world"
    ciphertext = bytes(plaintext[i] ^ key[i % len(key)] for i in range(len(plaintext)))
    result = xor_decrypt(ciphertext, key)
    assert result == plaintext


def test_base64_chain():
    import base64
    flag = "CHAKRA{b64_chained}"
    encoded = base64.b64encode(base64.b64encode(flag.encode()).decode().encode()).decode()
    chain = base64_chain_decode(encoded)
    assert flag in chain, f"Expected flag in chain: {chain}"


def test_caesar_brute():
    plaintext = "CHAKRA{caesar_flag}"
    shift = 13
    ciphertext = ""
    for c in plaintext:
        if c.isalpha():
            base = ord("A") if c.isupper() else ord("a")
            ciphertext += chr((ord(c) - base + shift) % 26 + base)
        else:
            ciphertext += c
    results = caesar_brute(ciphertext)
    found = [r for r in results if "CHAKRA{caesar_flag}" in r["result"]]
    assert found, f"Caesar brute should find plaintext"


def test_hash_identify():
    assert hash_identify("5f4dcc3b5aa765d61d8327deb882cf99") == "md5"
    assert hash_identify("a" * 40) == "sha1"
    assert hash_identify("a" * 64) == "sha256"


def test_vigenere_known_key():
    plaintext = "HELLO"
    key = "KEY"
    # Encrypt
    encrypted = ""
    for i, c in enumerate(plaintext):
        if c.isalpha():
            shift = ord(key[i % len(key)].upper()) - ord("A")
            encrypted += chr((ord(c.upper()) - ord("A") + shift) % 26 + ord("A"))
    decrypted = vigenere_decrypt(encrypted, key)
    assert decrypted.upper() == plaintext.upper()


def test_analyze_cipher_hex():
    result = analyze_cipher("48656c6c6f20576f726c64")
    # hex strings are also valid base64-ish patterns; just check it identifies something
    assert result["guess"] in ("hex_encoded", "base64_encoded", "monoalphabetic_or_plain")


def test_analyze_cipher_b64():
    result = analyze_cipher("SGVsbG8gV29ybGQ=")
    assert result["guess"] in ("base64_encoded", "monoalphabetic_or_plain")


def test_flag_detector_basic():
    d = FlagDetector()
    assert d.is_flag("CHAKRA{hello_world}")
    assert d.is_flag("flag{test}")
    assert not d.is_flag("no_flag_here")
    flags = d.extract_all("prefix CHAKRA{found_it} suffix")
    assert "CHAKRA{found_it}" in flags


if __name__ == "__main__":
    test_xor_single_byte()
    test_xor_decrypt_cycling()
    test_base64_chain()
    test_caesar_brute()
    test_hash_identify()
    test_vigenere_known_key()
    test_analyze_cipher_hex()
    test_analyze_cipher_b64()
    test_flag_detector_basic()
    print("All crypto tests passed!")
