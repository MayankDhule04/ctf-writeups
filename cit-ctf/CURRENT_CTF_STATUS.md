# Current CTF Challenge Status

## ✅ COMPLETED CHALLENGES

### 1. Baby Exponent (CIT CTF - Crypto)
- **Flag**: `CIT{sm4ll_3xp0n3nt_g0_brrr}`
- **Solution**: RSA with e=3, took cube root of ciphertext
- **File**: `baby_exponent_solver.py`

### 2. GlitchSkull (CSBC CTF - Web)
- **Flag**: `CSBC{Combine_layer_challenge_baby}`
- **Solution**: Found in JavaScript source code
- **Files**: `glitchskull_recon.py`, `glitchskull_solution.py`

---

## 🔄 IN-PROGRESS CHALLENGES

### 3. Cartographer's Secret (CIT CTF - OSINT) ⚠️ NEEDS MANUAL WORK
- **Status**: Requires manual map inspection
- **Prerequisite**: Follow the Flock = `CIT{State_Street_New_Haven_CT}`
- **Hint**: "Maybe I'm not looking closely enough"
- **Task**: Find name of menu item
- **Flag Format**: `CIT{name_of_item}` or `CIT{name-of-item}`

**Failed Attempts**:
- ❌ `CIT{Ninth_Square}`
- ❌ `CIT{Nine_Squares}`
- ❌ `CIT{West_Haven}`

**Next Steps**:
1. Open Google Maps
2. Search "State Street, New Haven, CT"
3. Zoom in CLOSELY
4. Look for visible landmarks, buildings, businesses
5. The "menu item" is something you can SEE on the map

**Top Candidates**:
- `CIT{New_Haven_Green}` - Famous park on State Street
- `CIT{The_Green}` - Short form
- `CIT{City_Hall}` - Major landmark on State Street
- `CIT{White_Clam_Pizza}` - Famous New Haven menu item
- `CIT{Chapel_Street}` - Intersects State Street

**Files**: `cartographers_secret_solver.py`, `cartographers_secret_final_solver.py`

---

### 4. Sign Up and Enjoy (CIT CTF - Web) ⚠️ NEEDS ADVANCED EXPLOITATION
- **URL**: http://23.179.17.92:5557
- **Status**: Vulnerabilities identified, exploitation incomplete
- **Flag Format**: `CIT{...}`

**Vulnerabilities Found**:
1. **Link Preview Tool** - Potential SSRF at `/tools/link-preview`
2. **Flask Session Cookie** - Uses signed cookie with unknown secret

**Tested (No Success)**:
- SQL Injection
- SSTI, XXE, LFI
- Common Flask secrets
- Direct admin role injection

**Next Steps**:
1. Set up webhook server for SSRF exfiltration
2. Brute force Flask secret with rockyou.txt
3. Find hidden results endpoint for link previews

**Files**: `SIGNUP_ENJOY_SUMMARY.md`, 15+ exploit scripts

---

### 5. Has it really been 2 years? (CIT CTF - OSINT) ⚠️ NEEDS RESEARCH
- **Status**: Image analysis incomplete
- **Image**: Sandwich with cucumber and cream cheese
- **Hint**: "Has it really been 2 years?" (suggests 2024 reference)
- **Task**: Find name of menu item
- **Flag Format**: `CIT{name_of_item}` or `CIT{name-of-item}`

**Next Steps**:
1. Research viral cucumber sandwiches from 2024
2. Check fast food limited-time items from 2024
3. Try: `CIT{Veggie_Delight}`, `CIT{Cucumber_Sandwich}`, `CIT{Cool_Cucumber}`

**Files**: `two_years_osint.py`, `two_years_solution_attempts.py`

---

### 6. Who Is He (TRZ CTF - Web) ⚠️ SERVER OFFLINE
- **URL**: http://23.179.17.69:1337 (NOT ACCESSIBLE)
- **Status**: Challenge server is down
- **Flag Format**: `TRZ{...}`

**Vulnerability**: Whois command injection
- Regex: `/^[a-z.-]+$/` (only lowercase, dots, hyphens)
- Command: `whois #{@domain}`
- Goal: Execute `/readflag "could you please give me the flag thank you so much"`

**Exploitation Strategy**:
1. Use `-h` option to redirect to malicious whois server
2. Exploit whois command options
3. Find Alpine whois package vulnerability

**Next Steps**:
1. Wait for challenge server to come online
2. Run `who_is_he_final_exploit.py`
3. Set up malicious whois server if needed

**Files**: `web_who-is-he/` folder, `who_is_he_final_exploit.py`, `WHO_IS_HE_SOLUTION.md`

---

### 7. Goober (CIT CTF - PWN) ⚠️ NEEDS CREDENTIALS
- **Target**: 23.179.17.69
- **Status**: Only SSH port open, needs credentials
- **Flag Format**: `CIT{...}`

**Next Steps**:
1. Get SSH credentials from CTF platform
2. Or download challenge binary

**Files**: `GOOBER_ANALYSIS.md`, `goober_recon.py`

---

## 📊 SUMMARY

### Completed: 2/7 (29%)
- ✅ Baby Exponent
- ✅ GlitchSkull

### Needs Manual Work: 2/7
- ⚠️ Cartographer's Secret (map inspection)
- ⚠️ Has it really been 2 years? (research)

### Needs Advanced Exploitation: 1/7
- ⚠️ Sign Up and Enjoy (SSRF/Flask secret)

### Blocked: 2/7
- 🚫 Who Is He (server offline)
- 🚫 Goober (needs credentials)

---

## 🎯 RECOMMENDED NEXT ACTIONS

### Immediate (Can do now):
1. **Cartographer's Secret**: Open Google Maps, zoom in on State Street, New Haven, CT
2. **Has it really been 2 years?**: Research 2024 viral cucumber sandwiches

### Requires Setup:
3. **Sign Up and Enjoy**: Set up webhook server or run Flask secret brute force
4. **Who Is He**: Wait for server to come online, then run exploit script

### Blocked:
5. **Goober**: Get credentials from CTF platform

---

## 📁 KEY FILES

### Solvers:
- `baby_exponent_solver.py` - ✅ Solved
- `glitchskull_solution.py` - ✅ Solved
- `cartographers_secret_final_solver.py` - 🔄 In progress
- `who_is_he_final_exploit.py` - 🔄 Ready to run when server is up

### Documentation:
- `SIGNUP_ENJOY_SUMMARY.md` - Complete analysis
- `WHO_IS_HE_SOLUTION.md` - Exploitation strategy
- `GOOBER_ANALYSIS.md` - Recon results

### Challenge Folders:
- `web_who-is-he/` - Complete challenge files
- `a-massive-problem/` - Another web challenge (not analyzed yet)

