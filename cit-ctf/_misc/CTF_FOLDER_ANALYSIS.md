# CTF Folder Analysis - Complete Overview

## Summary
This folder contains work on **multiple CTF challenges** across different categories. Based on the files, you're working on at least 6-7 distinct challenges.

---

## 🎯 Active Challenges

### 1. **Memory Dump Challenge** (CURRENT FOCUS)
**Status:** 🔴 In Progress  
**Challenge:** Extract flag from memory.dmp that has been reversed and XOR'd

**Files:**
- `memory.dmp` - The memory dump file
- `memory_dump_analyzer.py` - Original analyzer
- `memory_flag_solver.py` - New comprehensive solver (just created)
- `memory_bruteforce.py` - Brute force approach
- `reversed_flag_search.py` - Search for reversed patterns
- `smart_xor_search.py` - Smart XOR key detection
- `exhaustive_xor.py` - Exhaustive XOR testing

**Challenge Details:**
- Flag is reversed (byte-level, either full or in fixed-size words)
- Then XOR'd with a short repeating byte mask
- Format likely: `ctf7{...}` or `flag{...}`

**Next Steps:**
1. Run `memory_flag_solver.py` on memory.dmp
2. Try different word sizes for reversal (1, 2, 4, 8 bytes)
3. Test XOR keys 1-4 bytes long

---

### 2. **KageGate JWT Challenge**
**Status:** 🟡 Partially Solved (Need to crack JWT secret)  
**Challenge:** OAuth/JWT timing attack with `nbf` claim set 365 days in future

**Files:**
- `KAGEGATE_SUMMARY.md` - Complete analysis
- `kagegate_*.py` - Multiple attack scripts
- `jwt_cracker.py` - JWT secret cracker
- `forge_jwt_proper.py` - JWT forging tool
- `jwt_token.txt` - The JWT to crack
- `kagegate_wordlist.txt` - Custom wordlist
- `rockyou.txt` - Common password list

**Key Finding:**
- JWT has `nbf` (not before) claim set to Jan 17, 2027 (365 days in future)
- Need to crack HS256 secret to forge valid token
- Token: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

**Next Steps:**
1. Use hashcat: `hashcat -m 16500 -a 0 jwt_token.txt rockyou.txt`
2. Try Japanese/ninja themed passwords
3. Once cracked, forge JWT without `nbf` claim

---

### 3. **SSTV Audio Challenge**
**Status:** 🟡 In Progress  
**Challenge:** Decode SSTV (Slow Scan Television) signal from audio file

**Files:**
- `clean (1).wav` - Audio file with SSTV signal
- `reversed_audio.wav` - Reversed version
- `sstv_decoder.py` - Main decoder
- `sstv_flag_decoder.py` - Flag-specific decoder
- `advanced_sstv_decoder.py` - Advanced decoder
- Multiple `sstv_*.png` - Decoded images
- `spectrogram*.png` - Frequency analysis images
- `audio_analyzer.py`, `frequency_analyzer.py` - Analysis tools

**Key Findings:**
- Dominant frequencies: 1551.77 Hz and 1905.13 Hz
- Close to SSTV sync (1900 Hz) and black level (1500 Hz)
- Binary FSK encoding detected

**Next Steps:**
1. Decode as Robot36 or Martin M1 SSTV mode
2. Try binary FSK decoding
3. Check decoded images for flag

---

### 4. **Hash Collision Challenge**
**Status:** 🟡 In Progress  
**Challenge:** Find hash collisions for custom hash function

**Files:**
- `hash_collision_finder.py`
- `hash_collision_tools.py` (empty)
- `hex_collision_finder.py`
- `collision_attack.py`
- `collision_solver.py`
- `smart_collision.py`
- `pow_solver_and_collision_finder.py`

**Challenge Type:** Proof of Work or hash collision finding

---

### 5. **OSINT Challenge**
**Status:** 🟡 In Progress  
**Challenge:** Find password for sebastien.taupiac@orange.fr

**Files:**
- `osint_search_guide.txt` - Detailed guide
- `osint_search.py` - Search automation
- `check_leak.py` - Leak checker

**Target:** sebastien.taupiac@orange.fr  
**Context:** Music streaming service leak (Deezer 2019)  
**Flag Format:** `ctf7{password}`

**Recommended Sources:**
1. Intelligence X (intelx.io)
2. Dehashed (paid)
3. LeakCheck (paid)
4. Have I Been Pwned (confirmation only)

---

### 6. **SAML/OAuth Challenge**
**Status:** 🟡 In Progress  
**Challenge:** SAML authentication bypass or exploitation

**Files:**
- `saml_attack.py`
- `saml_exploit.py`
- `saml_flow.py`
- `get_flag.py`

---

### 7. **SQL Injection Challenge**
**Status:** 🟡 In Progress  
**Challenge:** SQL injection to extract secrets

**Files:**
- `sqli_attack.py`
- `sqli_extract_secret.py`

---

### 8. **Web Security Assessment**
**Status:** ✅ Completed  
**Target:** https://csbc.sanjivaniuniversity.com/

**Files:**
- `SECURITY_REPORT.md` - Complete report
- `security-check.js`
- `crash-test.js`
- `special-char-test.js`
- `server.js` - Test server

**Key Findings:**
- DoS vulnerability: `//` in URL crashes server
- Missing security headers
- Exposed .git directory
- No rate limiting

---

### 9. **Image Steganography Challenge**
**Status:** 🟡 In Progress  
**Challenge:** Extract hidden data from images

**Files:**
- `decode_images.py`
- `decode_network_images.py`
- `extract_images.py`
- `image_text_extractor.py`
- `comprehensive_decode.py`
- `lsb_*.bin` - LSB extracted data
- `extracted_BMP_image.bin`

---

### 10. **Broken Compass Challenge**
**Status:** 🟡 In Progress  
**Challenge:** Unknown (likely crypto or puzzle)

**Files:**
- `broken_compass_solver.py`

---

## 📊 Challenge Status Summary

| Challenge | Status | Priority | Completion |
|-----------|--------|----------|------------|
| Memory Dump | 🔴 Active | HIGH | 30% |
| KageGate JWT | 🟡 Blocked | HIGH | 70% |
| SSTV Audio | 🟡 Active | MEDIUM | 50% |
| Hash Collision | 🟡 Active | MEDIUM | 40% |
| OSINT | 🟡 Active | LOW | 20% |
| SAML/OAuth | 🟡 Active | MEDIUM | 30% |
| SQL Injection | 🟡 Active | MEDIUM | 40% |
| Web Security | ✅ Done | - | 100% |
| Steganography | 🟡 Active | LOW | 30% |
| Broken Compass | 🟡 Active | LOW | 10% |

---

## 🎯 Recommended Next Actions

### Immediate (Today):
1. **Memory Dump:** Run the new `memory_flag_solver.py` script
2. **KageGate:** Start hashcat on JWT token with rockyou.txt
3. **SSTV:** Try Robot36 decoder on audio file

### Short Term (This Week):
1. Complete OSINT search on Intelligence X
2. Finish hash collision solver
3. Test SAML exploits

### Tools Needed:
- `hashcat` - For JWT cracking
- `qsstv` or `RX-SSTV` - For SSTV decoding
- Intelligence X account - For OSINT
- Hex editor - For manual memory analysis

---

## 💡 Quick Wins

These challenges are closest to completion:

1. **KageGate JWT** - Just need to crack the secret (70% done)
2. **SSTV Audio** - Have all tools, just need right decoder (50% done)
3. **Memory Dump** - New comprehensive solver ready to run (30% done)

---

## 📁 File Organization

**Solvers:** 40+ Python scripts  
**Data Files:** memory.dmp, audio files, images  
**Documentation:** 3 markdown files  
**Wordlists:** rockyou.txt, kagegate_wordlist.txt  
**Output:** Multiple PNG images, bin files, analysis outputs

---

## 🔧 Tools & Libraries Used

- **Python:** Main scripting language
- **numpy, scipy:** Audio/signal processing
- **matplotlib:** Visualization
- **hashcat:** Password cracking
- **Node.js:** Web security testing
- **Various CTF tools:** JWT tools, SSTV decoders, etc.

---

**Last Updated:** Based on current folder state  
**Total Challenges:** 10  
**Completed:** 1  
**In Progress:** 9
