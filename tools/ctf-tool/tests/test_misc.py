"""Tests for misc module."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ctf_tool.misc import (
    bacon_decode, binary_to_text, brainfuck_run,
    extract_coordinates, flag_from_parts,
)
from ctf_tool.stego import morse_decode


def test_bacon_decode():
    # HELLO in Bacon: H=AABBB E=AABAA L=ABABB L=ABABB O=ABBBA
    bacon = "AABBB AABAA ABABB ABABB ABBBA"
    result = bacon_decode(bacon.replace(" ", ""))
    assert result == "HELLO", f"Got: {result}"


def test_binary_to_text():
    # 'A' = 01000001
    result = binary_to_text("01000001 01000010 01000011")
    assert result == "ABC", f"Got: {result}"


def test_morse_decode():
    # SOS
    morse = "... --- ..."
    result = morse_decode(morse)
    assert result == "SOS", f"Got: {result}"


def test_morse_word_sep():
    morse = ".... . .-.. .-.. --- / .-- --- .-. .-.. -.."
    result = morse_decode(morse)
    assert "HELLO" in result and "WORLD" in result


def test_brainfuck():
    # Hello World! in brainfuck (simple version)
    code = "++++++++++[>+++++++>++++++++++>+++>+<<<<-]>++.>+.+++++++..+++.>++.<<+++++++++++++++.>.+++.------.--------.>+.>."
    result = brainfuck_run(code)
    assert "Hello World!" in result, f"Got: {result!r}"


def test_extract_coordinates_2d():
    text = "The portal is at (1340, -255)"
    coords = extract_coordinates(text)
    assert any(c["type"] == "2d_tuple" for c in coords)
    found = [c for c in coords if c["type"] == "2d_tuple"]
    assert found[0]["parsed"]["x"] == 1340


def test_flag_from_parts():
    parts = ["CHAKRA{", "hello", "_world", "}"]
    results = flag_from_parts(parts, separators=[""])
    assert "CHAKRA{hello_world}" in results or any("CHAKRA" in r for r in results)


if __name__ == "__main__":
    test_bacon_decode()
    test_binary_to_text()
    test_morse_decode()
    test_morse_word_sep()
    test_brainfuck()
    test_extract_coordinates_2d()
    test_flag_from_parts()
    print("All misc tests passed!")
