"""Tests for ctf_tool.stego module."""

import pytest
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ctf_tool.stego import (
    image_lsb_extract,
    image_channel_analysis,
    image_bitplane_extract,
    image_metadata,
    svg_analyze,
    audio_lsb,
    audio_morse,
)
from ctf_tool.misc import morse_decode, morse_encode


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_test_png(path: str, width: int = 32, height: int = 32, lsb_message: bytes = b""):
    """Create a simple PNG image, optionally hiding a message in LSBs."""
    try:
        from PIL import Image
        import numpy as np
    except ImportError:
        pytest.skip("PIL/numpy not available")

    img_array = np.zeros((height, width, 3), dtype=np.uint8)
    # Fill with a gradient
    for y in range(height):
        for x in range(width):
            img_array[y, x] = [x * 8, y * 8, (x + y) * 4]

    if lsb_message:
        bits = []
        for byte in lsb_message:
            for i in range(7, -1, -1):
                bits.append((byte >> i) & 1)

        flat = img_array.reshape(-1, 3)
        for i, bit in enumerate(bits[:len(flat)]):
            flat[i, 0] = (flat[i, 0] & 0xFE) | bit
        img_array = flat.reshape(height, width, 3)

    img = Image.fromarray(img_array, mode="RGB")
    img.save(path)


def make_test_wav(path: str, message: bytes = b""):
    """Create a simple WAV file with optional LSB message."""
    try:
        import numpy as np
        import scipy.io.wavfile as wavfile
    except ImportError:
        pytest.skip("numpy/scipy not available")

    rate = 44100
    duration = 1.0  # 1 second
    samples = int(rate * duration)
    data = (np.sin(2 * np.pi * 440 * np.arange(samples) / rate) * 16000).astype(np.int16)

    if message:
        bits = []
        for byte in message:
            for i in range(7, -1, -1):
                bits.append((byte >> i) & 1)
        for i, bit in enumerate(bits[:len(data)]):
            data[i] = (data[i] & ~1) | bit

    wavfile.write(path, rate, data)


# ---------------------------------------------------------------------------
# Image LSB extraction
# ---------------------------------------------------------------------------

class TestImageLsbExtract:
    def test_extracts_hidden_message(self):
        try:
            from PIL import Image
            import numpy as np
        except ImportError:
            pytest.skip("PIL not available")

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            path = f.name

        message = b"CTF{lsb_test}"
        make_test_png(path, lsb_message=message)
        try:
            extracted = image_lsb_extract(path, channels="R")
            # The extracted bytes should begin with our message
            assert extracted[:len(message)] == message
        finally:
            os.remove(path)

    def test_returns_bytes(self):
        try:
            from PIL import Image
        except ImportError:
            pytest.skip("PIL not available")

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            path = f.name
        make_test_png(path)
        try:
            result = image_lsb_extract(path)
            assert isinstance(result, bytes)
        finally:
            os.remove(path)

    def test_different_channels(self):
        try:
            from PIL import Image
        except ImportError:
            pytest.skip("PIL not available")

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            path = f.name
        make_test_png(path)
        try:
            rgb = image_lsb_extract(path, channels="RGB")
            r_only = image_lsb_extract(path, channels="R")
            # RGB should be larger (3x channels)
            assert len(rgb) > len(r_only)
        finally:
            os.remove(path)


# ---------------------------------------------------------------------------
# Image channel analysis
# ---------------------------------------------------------------------------

class TestImageChannelAnalysis:
    def test_returns_dict_with_channels(self):
        try:
            from PIL import Image
        except ImportError:
            pytest.skip("PIL not available")

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            path = f.name
        make_test_png(path)
        try:
            result = image_channel_analysis(path)
            assert "channels" in result
            assert "R" in result["channels"]
            assert "G" in result["channels"]
            assert "B" in result["channels"]
        finally:
            os.remove(path)

    def test_missing_file(self):
        result = image_channel_analysis("/nonexistent/image.png")
        assert "error" in result

    def test_has_xor_results(self):
        try:
            from PIL import Image
        except ImportError:
            pytest.skip("PIL not available")

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            path = f.name
        make_test_png(path)
        try:
            result = image_channel_analysis(path)
            assert "xor_results" in result
        finally:
            os.remove(path)


# ---------------------------------------------------------------------------
# Image bitplane extraction
# ---------------------------------------------------------------------------

class TestImageBitplaneExtract:
    def test_returns_bytes(self):
        try:
            from PIL import Image
        except ImportError:
            pytest.skip("PIL not available")

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            path = f.name
        make_test_png(path)
        try:
            result = image_bitplane_extract(path, bit=0, channel=0)
            assert isinstance(result, bytes)
        finally:
            os.remove(path)

    def test_msb_different_from_lsb(self):
        try:
            from PIL import Image
        except ImportError:
            pytest.skip("PIL not available")

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            path = f.name
        make_test_png(path)
        try:
            lsb = image_bitplane_extract(path, bit=0, channel=0)
            msb = image_bitplane_extract(path, bit=7, channel=0)
            assert lsb != msb
        finally:
            os.remove(path)


# ---------------------------------------------------------------------------
# Image metadata
# ---------------------------------------------------------------------------

class TestImageMetadata:
    def test_returns_format_info(self):
        try:
            from PIL import Image
        except ImportError:
            pytest.skip("PIL not available")

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            path = f.name
        make_test_png(path)
        try:
            meta = image_metadata(path)
            assert "format" in meta
            assert "size" in meta
            assert "flags_found" in meta
        finally:
            os.remove(path)

    def test_nonexistent_returns_error(self):
        result = image_metadata("/nonexistent/image.png")
        assert "error" in result


# ---------------------------------------------------------------------------
# SVG analysis
# ---------------------------------------------------------------------------

class TestSvgAnalyze:
    def _write_svg(self, content: str) -> str:
        fd, path = tempfile.mkstemp(suffix=".svg")
        with os.fdopen(fd, "w") as f:
            f.write(content)
        return path

    def test_finds_flag_in_svg_text(self):
        svg = """<svg><text>flag{svg_flag}</text></svg>"""
        path = self._write_svg(svg)
        try:
            result = svg_analyze(path)
            assert "flag{svg_flag}" in result.get("flags_found", [])
        finally:
            os.remove(path)

    def test_extracts_opacity_values(self):
        svg = """<svg>
            <rect opacity="0.1"/>
            <rect opacity="0.2"/>
            <rect opacity="0.3"/>
        </svg>"""
        path = self._write_svg(svg)
        try:
            result = svg_analyze(path)
            assert len(result.get("opacity_values", [])) == 3
        finally:
            os.remove(path)

    def test_missing_file_returns_error(self):
        result = svg_analyze("/nonexistent/file.svg")
        assert "error" in result


# ---------------------------------------------------------------------------
# Audio LSB
# ---------------------------------------------------------------------------

class TestAudioLsb:
    def test_extracts_hidden_bytes(self):
        try:
            import numpy as np
            import scipy.io.wavfile
        except ImportError:
            pytest.skip("numpy/scipy not available")

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            path = f.name
        message = b"flag{audio_lsb}"
        make_test_wav(path, message=message)
        try:
            extracted = audio_lsb(path)
            assert extracted[:len(message)] == message
        finally:
            os.remove(path)

    def test_returns_bytes(self):
        try:
            import numpy as np
            import scipy.io.wavfile
        except ImportError:
            pytest.skip("numpy/scipy not available")

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            path = f.name
        make_test_wav(path)
        try:
            result = audio_lsb(path)
            assert isinstance(result, bytes)
        finally:
            os.remove(path)


# ---------------------------------------------------------------------------
# Morse (misc module, related to stego)
# ---------------------------------------------------------------------------

class TestMorse:
    def test_encode_decode_roundtrip(self):
        text = "HELLO"
        encoded = morse_encode(text)
        decoded = morse_decode(encoded)
        assert decoded == text

    def test_decode_known(self):
        morse = "... --- ..."
        result = morse_decode(morse)
        assert result == "SOS"

    def test_encode_hello(self):
        result = morse_encode("A")
        assert result == ".-"

    def test_decode_with_slash_word_sep(self):
        morse = ".... . .-.. .-.. --- / .-- --- .-. .-.. -.."
        result = morse_decode(morse)
        assert result == "HELLO WORLD"
