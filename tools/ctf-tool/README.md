# CTF Tool

A unified, reusable CTF solver tool built from real challenge scripts. Covers crypto, web, forensics, steganography, and misc categories with auto-detection.

## Install

```bash
cd ctf-tool
pip install -e .
# Or just run directly:
python -m ctf_tool.cli --help
```

Install optional dependencies for full functionality:
```bash
pip install -r requirements.txt
```

---

## Quick Start

```bash
# Auto-detect and solve anything
ctf_tool auto challenge.png
ctf_tool auto http://target-ctf.com/

# Crypto
ctf_tool crypto xor challenge.bin --brute
ctf_tool crypto xor challenge.bin --key deadbeef
ctf_tool crypto b64 "SGVsbG8gV29ybGQ="
ctf_tool crypto hash 5f4dcc3b5aa765d61d8327deb882cf99 --wordlist rockyou.txt
ctf_tool crypto caesar "PURXEN{pnrfne}" 
ctf_tool crypto vigenere cipher.txt --keylen 10
ctf_tool crypto analyze mysterious.txt

# Web
ctf_tool web recon http://target.com
ctf_tool web dirbust http://target.com --wordlist wordlist.txt
ctf_tool web jwt decode eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoiYWRtaW4ifQ.xxx
ctf_tool web jwt crack eyJ...token... --wordlist rockyou.txt
ctf_tool web jwt forge '{"user":"admin","role":3}' --secret mysecret
ctf_tool web sqli "http://t.com/page?id=1" --param id
ctf_tool web ssti "http://t.com/render" --param template
ctf_tool web login-brute http://t.com/login --user admin --user-field user --pass-field pass

# Forensics
ctf_tool forensics strings binary.elf --min-len 6
ctf_tool forensics scan unknown_file.bin
ctf_tool forensics extract image_with_zip.png --output ./extracted/
ctf_tool forensics memory heart.dmp --xor-keys 0x42,0x13
ctf_tool forensics apk challenge.apk

# Steganography
ctf_tool stego image flag.png --all
ctf_tool stego image flag.png --lsb --channel RGB
ctf_tool stego audio transmission.wav --all
ctf_tool stego audio morse_signal.wav --morse
ctf_tool stego qr corrupted_qr.png

# Misc
ctf_tool misc morse "... --- ..." --decode
ctf_tool misc morse "SOS" --encode
ctf_tool misc bacon "AABBBAABAABABABBABABBABBBA"
ctf_tool misc graph graph.json
ctf_tool misc coords "Server at (10720, -2040)"
```

---

## Global Options

| Option | Description |
|--------|-------------|
| `--flag-regex PATTERN` | Custom regex for flag detection (overrides default patterns) |
| `--output FILE` | Save full JSON results to file |
| `--verbose` | Print progress messages |

---

## Auto Mode Logic

`ctf_tool auto <input>` detects input type and runs solvers in priority order:

| Input Type | Solvers Run |
|-----------|-------------|
| URL | check_headers → wellknown → dirbust → JWT cookie check |
| Image | metadata → QR decode → LSB (R/G/B/RGB) → stegsolve all → channel XOR |
| Audio | LSB → spectrogram → morse → raw strings |
| Memory dump | plain string scan → XOR brute (all 256 keys) |
| Archive/APK | extract contents → scan all files |
| Binary/Text | flag scan → XOR brute → base64 chain → encodings |

Stops early when a flag-format match is found.

---

## Module Reference

### `ctf_tool.crypto`
- `xor_bruteforce(data, known_prefix, flag_regex)` — all 256 single-byte keys
- `xor_brute_multibyte(data, max_keylen)` — IC-based multi-byte key recovery
- `xor_decrypt(data, key)` — decrypt with known key
- `base64_chain_decode(s, max_depth)` — repeated base64 decode
- `vigenere_brute(ciphertext, max_keylen)` — IC-based Vigenere key recovery
- `vigenere_decrypt(ciphertext, key)` — known key decrypt
- `caesar_brute(ciphertext)` — all 26 shifts
- `hash_identify(h)` — identify hash type from length
- `hash_crack_wordlist(hash, wordlist_path)` — dictionary attack
- `aes_decrypt(data, key, mode, iv)` — AES decryption
- `analyze_cipher(text)` — IC, entropy, cipher type guess

### `ctf_tool.web`
- `check_headers(url)` — security headers + flag scan
- `check_wellknown(base_url)` — common recon paths
- `dir_enum(base_url, wordlist)` — directory enumeration
- `jwt_decode(token)` — no-verify JWT decode
- `jwt_crack(token, wordlist_path)` — HMAC secret brute force
- `jwt_forge(payload, secret, algorithm)` — sign new JWT
- `jwt_none_attack(token)` — alg:none bypass
- `sqli_test(url, param, method)` — error-based SQLi detection
- `sqli_extract(url, param, query)` — UNION-based data extraction
- `ssti_test(url, param, method)` — SSTI detection (Jinja2/Twig/etc.)
- `login_brute(url, user_field, pass_field, username, wordlist)` — brute force login
- `patch_auth_bypass(url, payload)` — PATCH/PUT privilege escalation

### `ctf_tool.forensics`
- `extract_strings(file, min_len)` — printable string extraction
- `scan_for_flags(file, flag_regex)` — multi-encoding flag scan
- `file_info(file)` — type, size, entropy, strings
- `extract_embedded(file, output_dir)` — ZIP/PNG/ELF embedded extraction
- `memory_string_search(dump, pattern)` — pattern search in memory dump
- `memory_xor_scan(dump, xor_keys)` — XOR brute on memory dump
- `apk_extract(apk, output_dir)` — APK content extraction
- `check_archive(file)` — ZIP/TAR listing and scanning
- `analyze_binary(file)` — full binary analysis

### `ctf_tool.stego`
- `image_lsb_extract(image, channels, bit_planes)` — LSB extraction
- `image_channel_analysis(image)` — R/G/B/A analysis + XOR differences
- `image_bitplane_extract(image, bit, channel)` — specific bit plane
- `image_metadata(image)` — EXIF and embedded metadata
- `image_stegsolve(image)` — run all LSB variations
- `qr_decode_robust(image)` — QR decode with preprocessing
- `qr_repair_and_decode(image)` — attempt QR repair
- `audio_lsb(audio)` — audio sample LSB extraction
- `audio_spectrogram(audio, output_path)` — generate spectrogram
- `audio_morse(audio)` — detect and decode Morse from amplitude
- `morse_decode(morse)` — Morse string to text

### `ctf_tool.misc`
- `graph_walk(graph_data)` — BFS all paths, decode edge labels
- `graph_edge_labels_decode(graph_data)` — collect edge labels
- `automaton_simulate(states, transitions, inputs, accepting)` — DFA simulation
- `bacon_decode(text)` — Bacon cipher decode
- `binary_to_text(binary)` — binary string to ASCII
- `extract_coordinates(text)` — GPS/game coords from text
- `flag_from_parts(parts, separators)` — combine parts into flag candidates
- `brainfuck_run(code, input)` — Brainfuck interpreter
- `osint_username_search(username)` — check username on platforms

### `ctf_tool.flag_detector`
- `FlagDetector(patterns_file, extra_regex)` — configurable flag detector
- `scan_text(text)` — returns `[{name, value, start, end}]`
- `scan_bytes(data)` — scan binary data
- `is_flag(s)` — boolean check
- `extract_all(text)` — list of unique flag strings
- `scan_file(path)` — scan any file

---

## Adding a New Solver Module

1. Create `ctf_tool/my_category.py`
2. Write parameterized functions that return dicts/lists (no hardcoded paths)
3. Import and call from `cli.py` in the appropriate subcommand handler
4. Add flag detection using `FlagDetector` from `flag_detector.py`
5. Add tests in `tests/test_my_category.py`

```python
# ctf_tool/my_category.py
from .flag_detector import FlagDetector

def my_solver(input_data: str, option: str = "default") -> dict:
    """My new solver.
    
    Args:
        input_data: The input to process
        option: Some option
    
    Returns:
        {result, flags}
    """
    detector = FlagDetector()
    # ... solver logic ...
    result = "decoded_output"
    flags = detector.extract_all(result)
    return {"result": result, "flags": flags}
```

---

## Customising Flag Formats

Edit `flag_formats.json` to add new patterns:

```json
{
  "patterns": [
    {"name": "MyFormat", "regex": "MYCTF\\{[^}]+\\}", "priority": 2}
  ]
}
```

Or use `--flag-regex` on the command line:
```bash
ctf_tool auto file.bin --flag-regex "MYCTF\\{[^}]+\\}"
```

---

## Running Tests

```bash
cd ctf-tool
python tests/test_crypto.py
python tests/test_forensics.py
python tests/test_misc.py
```

---

## Dependencies

Core (auto-installed):
- `requests` — web requests
- `pycryptodome` — AES/DES crypto
- `Pillow` — image processing
- `numpy` — numerical arrays
- `colorama` — colored output
- `PyJWT` — JWT handling

Optional (for full functionality):
- `opencv-python` — QR code detection, image processing
- `scipy` — audio spectrogram
- `pyzbar` — robust QR decoding
- `zxing-cpp` — additional QR decoding
