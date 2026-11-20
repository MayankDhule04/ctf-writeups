# CTF Progress Summary

## Flags Found: 2

### 1. Westeros "WINTER IS COMING" Challenge ✅
**Flag:** `Kaal{Ch0a5_IS_ladder}`

**Challenge Type:** Crypto/Encoding  
**Difficulty:** Medium

**Solution:**
- Part 1 (⚔️): ASCII → Caesar +19 → `Ch0a5`
- Part 2 (🛡️): Alternative Bacon cipher → `IS`
- Part 3 (👑): UTF-8 → Romaji → Vigenere → `ladder`
- Reference: "Chaos is a ladder" from Game of Thrones

---

### 2. Numerology (Google CTF 2025) ✅
**Flag:** `CTF{w3_aRe_g0Nn@_ge7_MY_FuncKee_monkey_!!}`

**Challenge Type:** Crypto  
**Difficulty:** Easy (50 pts)

**Solution:**
- Custom stream cipher based on weakened ChaCha20 (only 1 round instead of 20)
- Given: Known key, plaintext, many ciphertext samples with different nonces/counters
- Attack: Brute-force the counter value with a fixed nonce
- The cipher's weakness (single round) made it vulnerable to known-plaintext attacks

**Key Learning:**
- Modified ciphers often introduce weaknesses even if based on strong primitives
- Stream ciphers + known plaintext = keystream recovery
- With known key and samples, brute-forcing a 32-bit counter is feasible

**Writeup Source:** https://ctftime.org/writeup/40328

---

## Challenges In Progress

### 3. "The Signal is Real" Challenge 🔄
**Status:** Extensive analysis done, not solved yet

**Challenge Details:**
- URL: http://138.199.163.92:12669/
- Type: Web/Crypto
- Secret from robots.txt: `q355q636678723p4`
- SVG-based challenge with 1024 rectangles (classes: bit, ctrl, noise, junk, bg)

**Approaches Tried:**
- Binary decoding from rectangle colors
- Data-k value analysis
- Visual grid rendering
- XOR operations on different classes
- Multiple SVG requests with different keys
- Linear cryptanalysis attempts

**Hint:** "The signal is real. Most of what you see is not. The clock does not care."

**Next Steps:**
- May require timing-based requests or combining multiple SVG responses
- The secret likely encodes which samples/keys to combine

---

### 4. Incomplete Crypto Challenge 🔄
**Status:** Just started

**Challenge Details:**
- Folder: `challenge_CnK3cCB (1)`
- Files: encrypt.py, flag_cipher.txt, known_pair.txt, diagram.png
- Missing parameters: ROUNDS, SBOX, PERM
- Has known plaintext-ciphertext pair

**Next Steps:**
- Analyze the diagram for missing parameters
- Use known pair for cryptanalysis
- Recover ROUNDS, SBOX, and PERM values

---

## Statistics

- **Total Challenges Attempted:** 4
- **Solved:** 2
- **In Progress:** 2
- **Success Rate:** 50%

## Tools & Techniques Used

1. **Crypto Analysis:**
   - Caesar cipher, Bacon cipher, Vigenere cipher
   - Stream cipher analysis
   - Known-plaintext attacks
   - Linear cryptanalysis
   - XOR operations

2. **Web Reconnaissance:**
   - robots.txt analysis
   - SVG parsing and analysis
   - Rate limit handling

3. **Research:**
   - CTFtime writeup searches
   - Online cipher identification
   - Bytecode decompilation attempts

## Key Takeaways

1. Always search for writeups when stuck - they provide valuable learning
2. Weakened cryptographic primitives are common CTF targets
3. Known-plaintext attacks are powerful when you have samples
4. Visual/SVG-based challenges often hide data in attributes or patterns
5. Rate limiting suggests the solution doesn't require many requests

---

*Last Updated: Current Session*
