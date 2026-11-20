# SpaceCTF - Challenge Summary

## Solved Challenges

### 1. Maester's Codex ✅
**Category:** Crypto  
**FLAG:** `SpaceCTF{three_links_of_the_maesters_chain}`

**Solution:**
- Layer 1 (Stone): Base85 decode
- Layer 2 (Bronze): ROT13
- Layer 3 (Iron): Vigenere cipher with long key `TQEKSUIPGUMRXUNUKEYOILKKURVEVMUKMYEZ`
- The Vigenere key was deduced by knowing the flag should start with "SpaceCTF{" and contain readable English

### 2. Take the Black ✅
**Category:** Misc/Network  
**Connection:** `nc labs.cyberspacevr.in 30967`  
**FLAG:** `SpaceCTF{the_watch_holds_the_line_5YRB2A}`

**Solution:**
1. Connected to Castle Black service
2. Explored paths: `/`, `/robots.txt`, `/steward/oaths`
3. Found hidden path `/etc/lordcommander` in robots.txt
4. Decoded Base64 oaths which revealed: "The path you seek is the lord commander's name reversed"
5. Lord Commander: Jeor Mormont
6. Reversed with underscore: `tnomrom_roej`
7. Accessed `/tnomrom_roej` to get the flag

**Bonus:** The flag message mentions "THE_WATCH_HOLDS_THE_LINE" as a password for the Iron Bank (possibly another challenge).

## In Progress

### 3. The Faceless Verifier ⏳
**Category:** Crypto/Web  
**Connection:** `nc labs.cyberspacevr.in 30182`  
**Status:** Partially solved

**What we know:**
- JWT challenge with RS256 algorithm
- Server message: "The flag is reserved for those who walk under the names of Jaqen H'ghar or the many-faced"
- Need to forge a JWT with name "Jaqen H'ghar" or "the many-faced"
- Classic JWT algorithm confusion attack (RS256 -> HS256) expected
- Public key obtained from server

**Attempted:**
- ✗ Algorithm confusion with public key as HMAC secret (all formats)
- ✗ "none" algorithm attack
- ✗ Simple secrets for HS256
- ✗ Various key formats (PEM, DER, Base64)

**Next steps:**
- May need to find the actual HMAC secret used by the server
- Could try RSA key factorization (unlikely with 2048-bit key)
- May need to exploit a different vulnerability in the JWT implementation
- Consider if "counter-signed" means something specific

## Tools Created
- `maesters_codex_solver.py` - Multi-layer crypto solver
- `take_the_black_navigate.py` - Path navigation tool
- `faceless_verifier_explorer.py` - JWT service explorer
- Various JWT attack scripts

## Notes
- All challenges have Game of Thrones themes
- Flag format: `SpaceCTF{...}`
- Challenges are well-designed with good hints in descriptions
