"""Steganography solvers — image LSB, audio analysis, QR codes, spectrogram."""

import os
import struct
from typing import Dict, List, Optional, Tuple

from .flag_detector import FlagDetector
from .utils import extract_printable_strings

_detector = FlagDetector()

# ---------------------------------------------------------------------------
# Image steganography
# ---------------------------------------------------------------------------

def image_lsb_extract(image_path: str, channels: str = "RGB",
                       bit_planes: List[int] = None,
                       order: str = "row") -> bytes:
    """Extract LSB data from image channels.

    Args:
        image_path: Path to image file
        channels: Channel string like 'R', 'G', 'B', 'RGB', 'RGBA'
        bit_planes: List of bit plane indices to extract (default [0])
        order: Pixel traversal order ('row' or 'col')

    Returns:
        Extracted bytes
    """
    try:
        from PIL import Image
        import numpy as np
    except ImportError:
        return b"ERROR: Pillow/numpy not installed"

    if bit_planes is None:
        bit_planes = [0]

    try:
        img = Image.open(image_path).convert("RGBA")
        arr = np.array(img)
    except Exception as e:
        return f"ERROR: {e}".encode()

    channel_map = {"R": 0, "G": 1, "B": 2, "A": 3}
    bits = []

    if order == "row":
        pixels = arr.reshape(-1, arr.shape[-1])
    else:
        pixels = arr.T.reshape(-1, arr.shape[-1])

    for pixel in pixels:
        for ch in channels.upper():
            ci = channel_map.get(ch)
            if ci is None or ci >= pixel.shape[0]:
                continue
            val = int(pixel[ci])
            for bit in bit_planes:
                bits.append((val >> bit) & 1)

    # Pack bits into bytes
    result = bytearray()
    for i in range(0, len(bits) - 7, 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | bits[i + j]
        result.append(byte)
    return bytes(result)


def image_channel_analysis(image_path: str) -> Dict:
    """Analyze R/G/B/A channels separately and XOR between them.

    Returns dict with stats and flags found.
    """
    try:
        from PIL import Image
        import numpy as np
    except ImportError:
        return {"error": "Pillow/numpy not installed"}

    try:
        img = Image.open(image_path).convert("RGBA")
        arr = np.array(img)
    except Exception as e:
        return {"error": str(e)}

    r, g, b, a = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], arr[:, :, 3]
    result = {
        "size":       img.size,
        "mode":       img.mode,
        "channels":   {},
        "xor":        {},
        "flags":      [],
    }

    channels = {"R": r, "G": g, "B": b, "A": a}
    for name, ch in channels.items():
        unique = len(np.unique(ch))
        result["channels"][name] = {
            "min": int(ch.min()), "max": int(ch.max()),
            "mean": round(float(ch.mean()), 2), "unique": unique,
        }
        # Extract LSB of this channel and look for text
        lsb_bytes = bytes((int(px) & 1 for row in ch for px in row))
        text = _bits_to_text(lsb_bytes)
        flags = _detector.extract_all(text)
        if flags:
            result["flags"].extend(flags)

    # XOR channels
    for c1, c2 in [("R", "G"), ("R", "B"), ("G", "B")]:
        xored = np.bitwise_xor(channels[c1], channels[c2])
        unique = int(len(np.unique(xored)))
        result["xor"][f"{c1}^{c2}"] = {"unique": unique}
        # Check for patterns
        if unique < 10:
            result["xor"][f"{c1}^{c2}"]["suspicious"] = True

    return result


def _bits_to_text(bits_bytes: bytes) -> str:
    """Convert a bytes sequence of 0/1 values to text."""
    text_bytes = bytearray()
    for i in range(0, len(bits_bytes) - 7, 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | (bits_bytes[i + j] & 1)
        text_bytes.append(byte)
    return text_bytes.decode("utf-8", errors="replace")


def image_bitplane_extract(image_path: str, bit: int = 0,
                            channel: int = 0) -> bytes:
    """Extract a specific bit plane from image.

    Args:
        image_path: Path to image
        bit: Bit index (0=LSB, 7=MSB)
        channel: Channel index (0=R, 1=G, 2=B, 3=A)

    Returns:
        Bit plane as bytes (1 byte per bit)
    """
    try:
        from PIL import Image
        import numpy as np
        img = Image.open(image_path).convert("RGBA")
        arr = np.array(img)
        ch = arr[:, :, channel]
        plane = ((ch >> bit) & 1).flatten()
        return bytes(int(b) for b in plane)
    except ImportError:
        return b"ERROR: Pillow not installed"
    except Exception as e:
        return f"ERROR: {e}".encode()


def image_metadata(image_path: str) -> Dict:
    """Extract EXIF, comments, and other metadata from image."""
    result = {"exif": {}, "info": {}, "flags": []}
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS
        img = Image.open(image_path)
        result["info"] = dict(img.info)
        if hasattr(img, "_getexif") and img._getexif():
            for tag_id, value in img._getexif().items():
                tag = TAGS.get(tag_id, str(tag_id))
                result["exif"][tag] = str(value)[:200]
        # Scan all metadata for flags
        all_text = str(result["exif"]) + str(result["info"])
        result["flags"] = _detector.extract_all(all_text)
    except ImportError:
        result["error"] = "Pillow not installed"
    except Exception as e:
        result["error"] = str(e)
    return result


def image_stegsolve(image_path: str) -> List[Dict]:
    """Run multiple stego transformations and return interesting ones."""
    results = []
    channels = "RGBA"
    for ch in ["R", "G", "B", "A", "RGB", "RG", "GB", "RB"]:
        for bit in [0, 1, 2, 7]:
            data = image_lsb_extract(image_path, channels=ch, bit_planes=[bit])
            if data.startswith(b"ERROR"):
                continue
            text = data.decode("utf-8", errors="replace")
            flags = _detector.extract_all(text)
            if flags or any(s for s in extract_printable_strings(data, 8)):
                results.append({
                    "channel":  ch,
                    "bit":      bit,
                    "flags":    flags,
                    "preview":  text[:100],
                })
    return results


# ---------------------------------------------------------------------------
# QR codes
# ---------------------------------------------------------------------------

def qr_decode_robust(image_path: str) -> Optional[str]:
    """Decode QR code with multiple preprocessing attempts.

    Tries pyzbar and zxing-cpp with various thresholds.
    Returns decoded text or None.
    """
    try:
        import cv2
        import numpy as np
    except ImportError:
        return _qr_pil_only(image_path)

    img = cv2.imread(image_path)
    if img is None:
        return None

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    attempts = [
        ("original", img),
        ("gray_128", cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)[1]),
        ("otsu", cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]),
        ("adaptive", cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                            cv2.THRESH_BINARY, 11, 2)),
        ("inverted", cv2.bitwise_not(gray)),
    ]

    for name, proc in attempts:
        # Try pyzbar
        result = _try_pyzbar(proc)
        if result:
            return result
        # Try OpenCV built-in
        try:
            detector = cv2.QRCodeDetector()
            data, _, _ = detector.detectAndDecode(proc)
            if data:
                return data
        except Exception:
            pass
        # Try zxing-cpp
        result = _try_zxing(proc)
        if result:
            return result

    return None


def _try_pyzbar(img) -> Optional[str]:
    try:
        from pyzbar.pyzbar import decode
        from PIL import Image
        import numpy as np
        if isinstance(img, np.ndarray):
            pil_img = Image.fromarray(img)
        else:
            pil_img = img
        decoded = decode(pil_img)
        if decoded:
            return decoded[0].data.decode("utf-8", errors="replace")
    except Exception:
        pass
    return None


def _try_zxing(img) -> Optional[str]:
    try:
        import zxingcpp
        results = zxingcpp.read_barcodes(img)
        if results:
            return results[0].text
    except Exception:
        pass
    return None


def _qr_pil_only(image_path: str) -> Optional[str]:
    """Fallback QR decode using only PIL."""
    try:
        from PIL import Image
        img = Image.open(image_path)
        result = _try_pyzbar(img)
        return result
    except Exception:
        return None


def qr_repair_and_decode(image_path: str) -> Optional[str]:
    """Try to repair and decode a corrupted QR code."""
    try:
        import cv2
        import numpy as np
    except ImportError:
        return qr_decode_robust(image_path)

    img = cv2.imread(image_path)
    if img is None:
        return None

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    repairs = [
        cv2.GaussianBlur(gray, (3, 3), 0),
        cv2.medianBlur(gray, 3),
        cv2.bilateralFilter(gray, 9, 75, 75),
        cv2.morphologyEx(gray, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8)),
    ]
    for repaired in repairs:
        _, binary = cv2.threshold(repaired, 128, 255, cv2.THRESH_BINARY)
        result = _try_pyzbar(binary) or _try_zxing(binary)
        if result:
            return result

    return None


# ---------------------------------------------------------------------------
# Audio steganography
# ---------------------------------------------------------------------------

def audio_lsb(audio_path: str, n_bits: int = 1) -> bytes:
    """Extract LSB(s) from audio samples.

    Args:
        audio_path: Path to WAV file
        n_bits: Number of LSBs to extract per sample

    Returns:
        Extracted bits as bytes
    """
    try:
        import wave
        import numpy as np
        with wave.open(audio_path, "rb") as wf:
            n_frames = wf.getnframes()
            sampwidth = wf.getsampwidth()
            raw = wf.readframes(n_frames)

        if sampwidth == 1:
            samples = np.frombuffer(raw, dtype=np.uint8)
        elif sampwidth == 2:
            samples = np.frombuffer(raw, dtype=np.int16)
        else:
            return b""

        bits = []
        for s in samples:
            for b in range(n_bits):
                bits.append(int(s >> b & 1))

        result = bytearray()
        for i in range(0, len(bits) - 7, 8):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | bits[i + j]
            result.append(byte)
        return bytes(result)
    except ImportError:
        return b"ERROR: numpy not installed"
    except Exception as e:
        return f"ERROR: {e}".encode()


def audio_morse(audio_path: str, threshold: float = None) -> str:
    """Detect and decode Morse code from audio amplitude envelope.

    Returns decoded text string.
    """
    try:
        import wave
        import numpy as np
    except ImportError:
        return "ERROR: numpy not installed"

    try:
        with wave.open(audio_path, "rb") as wf:
            raw = wf.readframes(wf.getnframes())
            framerate = wf.getframerate()
            sampwidth = wf.getsampwidth()

        if sampwidth == 2:
            samples = np.frombuffer(raw, dtype=np.int16).astype(float)
        else:
            samples = np.frombuffer(raw, dtype=np.uint8).astype(float) - 128

        # Compute amplitude envelope
        window = framerate // 50
        envelope = np.array([
            np.abs(samples[i:i + window]).mean()
            for i in range(0, len(samples), window)
        ])

        if threshold is None:
            threshold = envelope.max() * 0.3

        signal = (envelope > threshold).astype(int)

        # Convert signal to Morse
        morse = ""
        prev = 0
        count = 0
        for val in list(signal) + [0]:
            if val == prev:
                count += 1
            else:
                if prev == 1:
                    morse += "." if count <= 2 else "-"
                else:
                    if count <= 2:
                        morse += ""
                    elif count <= 5:
                        morse += " "
                    else:
                        morse += " / "
                prev = val
                count = 1

        return morse_decode(morse)
    except Exception as e:
        return f"ERROR: {e}"


def audio_spectrogram(audio_path: str, output_path: str = None) -> Dict:
    """Generate spectrogram and look for hidden text/patterns.

    Returns dict with spectrogram path and any detected flags.
    """
    result = {"output": None, "flags": []}
    try:
        import numpy as np
        from scipy import signal as scipy_signal
        from scipy.io import wavfile
    except ImportError:
        result["error"] = "scipy/numpy not installed"
        return result

    try:
        rate, data = wavfile.read(audio_path)
        if data.ndim > 1:
            data = data[:, 0]
        data = data.astype(float)

        f, t, Sxx = scipy_signal.spectrogram(data, rate, nperseg=256)

        if output_path:
            try:
                import matplotlib
                matplotlib.use("Agg")
                import matplotlib.pyplot as plt
                plt.figure(figsize=(12, 6))
                plt.pcolormesh(t, f, 10 * np.log10(Sxx + 1e-10), cmap="inferno")
                plt.ylabel("Frequency [Hz]")
                plt.xlabel("Time [sec]")
                plt.colorbar(label="dB")
                plt.savefig(output_path, dpi=100, bbox_inches="tight")
                plt.close()
                result["output"] = output_path
            except Exception as e:
                result["plot_error"] = str(e)

        result["sample_rate"] = int(rate)
        result["duration"] = round(len(data) / rate, 2)
        result["freq_range"] = [float(f.min()), float(f.max())]
    except Exception as e:
        result["error"] = str(e)

    return result


# ---------------------------------------------------------------------------
# Morse code
# ---------------------------------------------------------------------------

_MORSE_TABLE = {
    ".-": "A", "-...": "B", "-.-.": "C", "-..": "D", ".": "E",
    "..-.": "F", "--.": "G", "....": "H", "..": "I", ".---": "J",
    "-.-": "K", ".-..": "L", "--": "M", "-.": "N", "---": "O",
    ".--.": "P", "--.-": "Q", ".-.": "R", "...": "S", "-": "T",
    "..-": "U", "...-": "V", ".--": "W", "-..-": "X", "-.--": "Y",
    "--..": "Z", "-----": "0", ".----": "1", "..---": "2",
    "...--": "3", "....-": "4", ".....": "5", "-....": "6",
    "--...": "7", "---..": "8", "----.": "9",
    ".-.-.-": ".", "--..--": ",", "..--..": "?",
}


def morse_decode(morse: str) -> str:
    """Decode Morse code string. Supports / as word separator."""
    result = []
    for word in morse.strip().split(" / "):
        letters = []
        for code in word.strip().split():
            letters.append(_MORSE_TABLE.get(code, "?"))
        result.append("".join(letters))
    return " ".join(result)
