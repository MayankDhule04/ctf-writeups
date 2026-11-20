# CIT CTF Challenge Status (New Haven University)

## Completed Challenges ✅

### Challenge: Temporary Destruction (Web)
- **Status**: SOLVED ✅
- **Points**: 794 (10splayaSec11)
- **Hint**: "I hear something...."
- **URL**: http://23.179.17.92:5558
- **Flag**: `CIT{55T1_R3m0t3_C0d3_3x3cut1on}`

#### Vulnerability:
- Server-Side Template Injection (SSTI) in Flask/Jinja2
- Application uses `render_template_string()` on user input
- Filter blocks `__word__` patterns but can be bypassed

#### Solution:
- Bypass filter using string concatenation: `'__cla'+'ss__'`
- Exploit chain: `{{ lipsum['__glo'+'bals__']['__bu'+'iltins__']['open']('/tmp/flag.txt').read() }}`
- Flag located at `/tmp/flag.txt`

#### Files Created:
- `temporary_destruction_exploit.py` - Initial SSTI testing
- `temporary_destruction_rce.py` - Full RCE exploit

### Challenge: Intern Portal (Web)
- **Status**: IN PROGRESS 🔄
- **Points**: 854 (10splayaSec8)
- **Hint**: "The intern said they made a custom report application... but I don't think security was in mind." + "I hear something...."
- **URL**: http://23.179.17.92:5001

#### Vulnerabilities Found:
- **IDOR (Insecure Direct Object Reference)**: Can access any report via `/report?id=X`
- Input is sanitized (HTML escaped, no XSS/SSTI/XXE)
- SQL injection in login doesn't bypass authentication

#### Analysis:
- Tested 100+ attack vectors including SQLi, SSTI, XXE, LFI, path traversal
- Flag likely in a specific report ID accessible via IDOR
- Need to brute force report IDs systematically

#### Next Steps:
- Run `intern_portal_brute_force_ids.py` to search all report IDs
- Investigate "I hear something" hint (audio/webhook/monitoring?)
- Check for hidden endpoints or features

#### Files Created:
- 20+ analysis and exploit scripts
- `INTERN_PORTAL_SUMMARY.md` - Complete analysis
- `intern_portal_brute_force_ids.py` - ID enumeration script

### Challenge 1: Brainfuck Decoder
- **Status**: SOLVED ✅
- **Input**: Brainfuck code
- **Output**: `Wh@t_in_th3_w0rld_i$_th1s_l@ngu@g3`
- **Flag**: `CIT{Wh@t_in_th3_w0rld_i$_th1s_l@ngu@g3}`

### Challenge 2: Layers (Base64)
- **Status**: SOLVED ✅
- **Input**: Multi-layer Base64 encoded string
- **Decoded Result**: `b9486c74c779db5194d6508bebbee72b` (MD5 hash)
- **SHA1 Verification**: `6ca8b4ae8d7317b27f564bc962a20b3e6fb49c72` ✅ MATCH
- **Flag Format**: `CIT{b9486c74c779db5194d6508bebbee72b}`

## In Progress Challenges 🔄

### Challenge: Dog Barking (Misc)
- **Status**: IN PROGRESS 🔄 - AWAITING MANUAL INSPECTION
- **Points**: 900 (ronnie8)
- **Hint**: "dogs were trying to tell me something"
- **File**: dog.wav
- **Flag Format**: `CIT{example_flag}`

#### Analysis Complete:
- Audio is NOT actual dog barking - it's synthesized tones around 495Hz
- Zero crossing rate (0.0656) indicates tone-based encoding
- LSB steganography: ❌ Checked all 16 bit positions - no flag
- Bark timing analysis: ❌ No meaningful binary/Morse patterns
- **Spectrogram analysis**: ✓ MOST LIKELY SOLUTION

#### Generated Files:
**Spectrogram Images** (check these for visible text):
- `dog_spectrogram.png` - Full spectrum view
- `dog_spectrogram_high_freq.png` - High frequencies (4-8kHz)
- `dog_binary_0.5.png`, `dog_binary_0.6.png` - Binary thresholded
- `dog_text_4000_6000_t8.png` - Ultra high contrast (4-6kHz)
- `dog_text_6000_8000_t8.png` - Ultra high contrast (6-8kHz)
- `dog_text_inverted_t5.png`, `dog_text_inverted_t6.png` - Inverted versions

**Analysis Scripts**:
- `dog_barking_analyzer.py`, `dog_comprehensive_analyzer.py`
- `dog_timing_analyzer.py`, `dog_visual_analysis.py`
- `dog_spectrogram.py`, `dog_spectrogram_ocr.py`
- `dog_all_bits.py`, `dog_sstv_check.py`
- `dog_extract_text_region.py`
- `DOG_BARKING_ANALYSIS.md` - Full analysis summary

#### Next Steps:
1. **IMMEDIATE**: Open the PNG files and look for text manually
2. Recommended files to check first:
   - `dog_text_4000_6000_t8.png` (optimized for text)
   - `dog_text_inverted_t5.png` (white on black)
   - `dog_spectrogram.png` (full view)
3. If no text visible, use Audacity:
   - File > Open > dog.wav
   - Track dropdown > Spectrogram
   - Look for text in 4-8kHz range
4. Alternative: Try SSTV decoder (if it's an image, not text)
   - Online: https://sstv-decoder.com/
   - Windows: RX-SSTV, MMSSTV

### Challenge 17: Rotor Rooter (Crypto)
- **Status**: IN PROGRESS 🔄
- **Ciphertext**: `KLEGCKRGGONTBNBVPIIZVWXQQEZYAXXWQMGIZDNEWWUTOVZRWOMZKGWNKWZBQXOGZSTVCGUFL`
- **Hint**: "Spin it till it drains"
- **Points**: 892 (elemental3)
- **Flag Format**: `CIT{underscore_between_each_word}`

#### Analysis:
- Cipher type: Enigma M3 machine
- Successfully decoded with configuration: Rotors III-II-I, Reflector B, Position AAA
- Decoded message: `WECANONLYSEEASHORTDNCJPNPZNBCABZGDDRTBETEZVMCKHTDASURDXYSDGKSFWWAACEBJVSP`
- First part is readable: "WE CAN ONLY SEE A SHORT D..."
- After "SHORT", the text becomes garbled (may be intentional or incorrect settings)

#### Possible Flags to Try:
1. `CIT{we_can_only_see_a_short_distance_ahead}` (most likely)
2. `CIT{we_can_only_see_a_short_drain}` (based on hint)
3. `CIT{we_can_only_see_a_short_distance}`
4. Full decoded (unlikely): `CIT{wecanonlyseeashortdncjpnpznbcabzgddrtbetezvmckhtdasurdxysdgksfwwaacebjvsp}`

#### Files Created:
- `rotor_rooter_solver.py` - Initial attempts
- `rotor_enigma_full.py` - Enigma implementation
- `rotor_comprehensive.py` - Multiple cipher types
- `rotor_enigma_brute.py` - Enigma configuration brute force
- `rotor_decode_full.py` - Full message decode
- `rotor_position_brute.py` - Position brute force
- `rotor_extract_message.py` - Message analysis
- `rotor_alternative_approach.py` - Alternative cipher attempts

### Challenge 11: Call Me Maybe (Crypto)
- **Status**: IN PROGRESS 🔄
- **Hash**: `$2b$10$Ni0U3D5ibg1NY6G/k8CDHuXG7m/WNZzuV/9PDPnRzgKs4wUjaTwGO`
- **Type**: Bcrypt (cost factor 10)
- **Hint**: "Call me, maybe? No… wrong decade."
- **Points**: 900 (elemental2)

#### Analysis:
- Song "Call Me Maybe" by Carly Rae Jepsen (2012, 2010s decade)
- "Wrong decade" suggests password from different decade
- Tested 500+ passwords including:
  - Phone songs: 8675309 (Jenny), Blondie's "Call Me"
  - Decade references: 80s, 90s, 00s, wrongdecade
  - Common passwords from rockyou top 200
  - 900 number patterns (1-900 premium services)
  - CTF patterns: flag, admin, password variations

#### Next Steps:
1. **Use hashcat with rockyou.txt** (REQUIRED):
   ```
   hashcat -m 3200 -a 0 call_me_maybe_hash.txt rockyou.txt
   ```
2. **Or use john the ripper**:
   ```
   john --format=bcrypt call_me_maybe_hash.txt --wordlist=rockyou.txt
   ```
3. **Online services** (if allowed):
   - https://crackstation.net/
   - https://hashes.com/en/decrypt/hash

#### Files Created:
- `call_me_maybe_crack.py` - Initial cracker
- `call_me_maybe_extended.py` - Extended wordlist
- `call_me_maybe_targeted.py` - Targeted phone songs
- `call_me_maybe_ultimate.py` - Rockyou top + CTF patterns
- `call_me_900_patterns.py` - 900 number patterns
- `call_me_maybe_hash.txt` - Hash file for hashcat

### Challenge 3: MD5 Hash Cracking
- **Status**: IN PROGRESS 🔄
- **Hash**: `b9486c74c779db5194d6508bebbee72b`
- **Hint**: "Ronnie is a sick individual who orders a hot dog bun with only pickles on it and savors it"

#### Attempts Made:
1. ✅ Tested 100+ common passwords
2. ✅ Tested variations of "ronnie", "pickles", "hotdog", "bun"
3. ✅ Tested 2-word and 3-word combinations
4. ✅ Tested numeric suffixes (0-999)
5. ✅ Tested leet speak variations
6. ✅ Tested CIT/CTF related words
7. ❌ Online API lookups (returned HTML, not results)

#### Next Steps:
1. **Manual Online Lookup** (RECOMMENDED):
   - https://crackstation.net/
   - https://md5decrypt.net/
   - https://hashes.com/en/decrypt/hash
   - https://md5hashing.net/hash/md5/b9486c74c779db5194d6508bebbee72b

2. **Alternative Approaches**:
   - Use hashcat with rockyou.txt wordlist
   - Try more extensive wordlists (SecLists, etc.)
   - The password might not be related to the Discord hint
   - Could be a random string or reference we haven't tried

3. **Possible Password Types**:
   - A name or username
   - A phrase from the Discord message
   - A random string unrelated to the hint
   - A reference to something specific in the CTF context

### Challenge 4: Discord Challenge
- **Status**: NOT STARTED
- **Clue**: Same as Challenge 3 hint
- **Possible Connection**: May be related to the MD5 hash or a separate OSINT challenge

## Files Created:
- `cit_challenge_solver.py` - Brainfuck decoder
- `cit_layers_solver.py` - Base64 layers decoder
- `crack_md5.py` - Initial MD5 cracker
- `cit_md5_comprehensive_crack.py` - Extended MD5 cracker
- `cit_md5_online_lookup.py` - Online lookup attempts

## Flag Format:
- All flags use format: `CIT{string}`
- The answer from decoding does NOT include the wrapper
- You must add `CIT{}` to the final answer

## Notes:
- The MD5 hash `b9486c74c779db5194d6508bebbee72b` is the result from the Layers challenge
- It needs to be cracked to get the plaintext password
- The Discord hint about "Ronnie" and "pickles" may or may not be directly related
- Manual lookup on online databases is the most reliable next step
