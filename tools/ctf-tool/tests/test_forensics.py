"""Tests for forensics module."""
import sys, os, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ctf_tool.forensics import (
    extract_strings, scan_for_flags, file_info, memory_xor_scan,
)


def _write_temp(content: bytes, suffix=".bin"):
    tf = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tf.write(content)
    tf.close()
    return tf.name


def test_extract_strings():
    data = b"\x00\x01" + b"hello world" + b"\x00" + b"CHAKRA{flag_here}" + b"\xff"
    path = _write_temp(data)
    strings = extract_strings(path, min_len=4)
    assert "hello world" in strings
    assert "CHAKRA{flag_here}" in strings
    os.unlink(path)


def test_scan_for_flags_plain():
    data = b"junk CHAKRA{plain_flag} more junk"
    path = _write_temp(data)
    results = scan_for_flags(path)
    values = [r["value"] for r in results if "value" in r]
    assert "CHAKRA{plain_flag}" in values
    os.unlink(path)


def test_scan_for_flags_base64():
    import base64
    flag = "CHAKRA{b64_encoded}"
    encoded = base64.b64encode(flag.encode()).decode()
    data = f"prefix {encoded} suffix".encode()
    path = _write_temp(data)
    results = scan_for_flags(path)
    values = [r["value"] for r in results if "value" in r]
    assert flag in values, f"Expected {flag} in {values}"
    os.unlink(path)


def test_memory_xor_scan():
    key = 0x42
    flag = b"CHAKRA{xor_memory}"
    data = bytes(b ^ key for b in flag) + b"\x00" * 100
    path = _write_temp(data, suffix=".dmp")
    results = memory_xor_scan(path, xor_keys=[key])
    assert any(r.get("flag") == "CHAKRA{xor_memory}" for r in results)
    os.unlink(path)


def test_file_info():
    data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
    path = _write_temp(data, suffix=".png")
    info = file_info(path)
    assert info["type"] == "png"
    assert info["size"] > 0
    os.unlink(path)


if __name__ == "__main__":
    test_extract_strings()
    test_scan_for_flags_plain()
    test_scan_for_flags_base64()
    test_memory_xor_scan()
    test_file_info()
    print("All forensics tests passed!")
