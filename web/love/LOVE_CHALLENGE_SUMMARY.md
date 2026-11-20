# Love is Simple - CTF Challenge Summary

## Challenge Information
- **URL**: https://love-pagal-haiiiiiii.onrender.com/
- **Time Window**: 2PM - 2:30PM IST (14:00-14:30 IST)
- **Challenge Type**: Web + Time-based Access Control
- **Flag Format**: TRACECTF{...}

## Key Findings

### 1. Main Page Analysis
- Contains multiple decoy flags in HTML comments and JavaScript
- Meta keywords hint at: `love,time,moment,heart,2pm,IST,confess`
- HTML comment reveals API endpoint: `/api/confess`
- Required headers for `/api/confess`:
  - `x-love-time`
  - `x-love-token`
  - `x-love-proof`
  - `x-love-signature`

### 2. API Endpoints Discovered

#### `/robots.txt`
```
User-agent: *
Disallow: /api/secret
Disallow: /api/admin
Disallow: /api/flag
Disallow: /api/confess
Allow: /api/hint
```

#### `/api/hint`
Returns: `{"hint":"Look deeper into the source of time."}`

#### `/api/flag`
Returns base32-encoded data split by `||` delimiters (125 parts)
- Each part decodes to 15 characters containing `::` delimiters
- The decoded data appears to be obfuscated/encrypted

#### `/api/confess` (POST)
- Returns `{"error":"Access denied."}` when accessed outside time window
- Requires POST method (GET returns 405 Method Not Allowed)
- Likely returns the real flag during 2PM-2:30PM IST window

### 3. Decoy Flags Found
- `TRACECTF{n1c3_try_but_y0u_n33d_m0r3_th4n_cl1ck5}` (onclick alert)
- `TRACECTF{HTML_c0mm3nts_4r3_ju5t_d1str4ct10ns}` (hidden div)
- `TRACECTF{s0urc3_c0d3_w0nt_s4v3_y0u_n0w}` (HTML comment)
- `TRACECTF{HTML_m3t4_t4gs_4r3_n0t_th3_4nsw3r}` (meta description)
- `TRACECTF{j4v4scr1pt_1s_n0t_th3_s0lut10n}` (JavaScript comment)
- `TRACECTF{c0ns0l3_l0gs_4r3_f0r_d3bugg1ng_n0t_fl4gs}` (console.log)

## Solution Strategy

### To Get the Real Flag:

1. **Wait for the time window** (2PM-2:30PM IST)

2. **Send POST request to `/api/confess`** with correct headers:
```python
import requests
import hashlib
from datetime import datetime
import pytz

BASE_URL = "https://love-pagal-haiiiiiii.onrender.com"

# Get current IST time
ist = pytz.timezone('Asia/Kolkata')
now_ist = datetime.now(ist)

headers = {
    'x-love-time': now_ist.strftime("%H:%M:%S"),  # or "14:00:00"
    'x-love-token': 'love',  # or try: 'simple', 'pagal', '2pm'
    'x-love-proof': 'simple',  # or try: 'love', 'true'
    'x-love-signature': hashlib.md5(b'love').hexdigest()
}

response = requests.post(f"{BASE_URL}/api/confess", headers=headers)
print(response.text)
```

3. **Possible header values to try**:
   - `x-love-time`: Current IST time, "14:00:00", "14:15:00", etc.
   - `x-love-token`: "love", "simple", "pagal", "2pm", MD5/SHA256 hashes
   - `x-love-proof`: "love", "simple", "true", "1"
   - `x-love-signature`: MD5 or SHA256 hash of various combinations

## Current Status
- **Time**: Outside the 2PM-2:30PM IST window (currently 9:30PM IST)
- **Access**: `/api/confess` returns "Access denied"
- **Next Step**: Access the challenge during the specified time window

## Notes
- The hint "Look deeper into the source of time" confirms time-based access
- The challenge explicitly states "The 2PM window is OPEN until 2:30"
- All decoy flags are intentionally misleading
- The real flag is protected by time-based access control

## Files Created
- `love_challenge_solver.py` - Initial reconnaissance
- `love_decode_and_confess.py` - Flag decoding attempts
- `love_final_attack.py` - POST method testing
- `love_extract_real_flag.py` - Pattern extraction
- `love_smart_decode.py` - Column/diagonal analysis
- `love_extract_around_delimiter.py` - Delimiter analysis
- `love_complete_solution.py` - Complete analysis

## Recommendation
**Access the challenge between 2PM-2:30PM IST tomorrow and run the POST request to `/api/confess` with the correct headers to retrieve the real flag.**
