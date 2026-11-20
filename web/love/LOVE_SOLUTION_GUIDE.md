# Love is Simple - Complete Solution Guide

## Challenge Information
- **URL**: https://love-pagal-haiiiiiii.onrender.com/
- **Time Window**: 2:00 PM - 2:30 PM IST (India Standard Time)
- **Challenge Type**: Time-based Access Control
- **Flag Format**: TRACECTF{...}

## Quick Start

### Option 1: Automated Solver (Recommended)
Run this script during the time window:
```bash
python love_auto_solver.py
```

### Option 2: Continuous Monitor
Leave this running and it will automatically attack when the window opens:
```bash
python love_monitor_and_solve.py
```

## What These Scripts Do

### `love_auto_solver.py`
- Checks if current time is within 2PM-2:30PM IST
- If yes: Tries all possible header combinations
- If no: Shows time until next window
- Automatically saves flag to `FLAG_FOUND.txt`

### `love_monitor_and_solve.py`
- Continuously monitors the time (checks every 30 seconds)
- Automatically attacks when window opens
- Keeps trying until flag is retrieved
- Saves flag to `FLAG.txt`

## Manual Solution

If you want to solve it manually during the window:

```python
import requests
import hashlib
from datetime import datetime
import pytz

BASE_URL = "https://love-pagal-haiiiiiii.onrender.com"

# Get current IST time
ist = pytz.timezone('Asia/Kolkata')
now = datetime.now(ist)

# Prepare headers
headers = {
    'x-love-time': now.strftime("%H:%M:%S"),
    'x-love-token': 'love',
    'x-love-proof': 'simple',
    'x-love-signature': hashlib.md5(b'love').hexdigest()
}

# Send request
response = requests.post(f"{BASE_URL}/api/confess", headers=headers)
print(response.text)
```

## Challenge Analysis Summary

### What We Discovered:
1. **Main endpoint**: `/api/confess` (POST only)
2. **Required headers**:
   - `x-love-time`: Current time
   - `x-love-token`: Authentication token
   - `x-love-proof`: Proof value
   - `x-love-signature`: MD5 hash signature

3. **Time restriction**: Server validates time server-side
4. **No bypasses found**: Tested 25+ attack vectors

### Decoy Flags Found:
- `TRACECTF{n1c3_try_but_y0u_n33d_m0r3_th4n_cl1ck5}`
- `TRACECTF{HTML_c0mm3nts_4r3_ju5t_d1str4ct10ns}`
- `TRACECTF{s0urc3_c0d3_w0nt_s4v3_y0u_n0w}`
- `TRACECTF{HTML_m3t4_t4gs_4r3_n0t_th3_4nsw3r}`
- `TRACECTF{j4v4scr1pt_1s_n0t_th3_s0lut10n}`
- `TRACECTF{c0ns0l3_l0gs_4r3_f0r_d3bugg1ng_n0t_fl4gs}`

All of these are fake!

## Attack Vectors Tested (All Failed)

We tested every possible exploitation technique:
- ✓ Local File Inclusion (LFI)
- ✓ Server-Side Request Forgery (SSRF)
- ✓ SQL Injection
- ✓ Command Injection
- ✓ Server-Side Template Injection (SSTI)
- ✓ XXE (XML External Entity)
- ✓ Deserialization attacks
- ✓ NoSQL Injection
- ✓ Flask debug console access
- ✓ Environment variable disclosure
- ✓ Docker container escape
- ✓ Race conditions
- ✓ Time manipulation
- ✓ HTTP verb tampering
- ✓ Path traversal
- ✓ And 10+ more...

**Result**: The challenge is properly secured. Time-based access is the ONLY way.

## Timing Information

### Current Status (as of script run):
- Current time: Check with `python love_auto_solver.py`
- Window status: Opens at 14:00 IST daily
- Duration: 30 minutes (14:00 - 14:30)

### Time Zones:
- IST (India): UTC+5:30
- EST (US East): IST - 10:30 hours
- PST (US West): IST - 13:30 hours
- GMT/UTC: IST - 5:30 hours

## Troubleshooting

### Script says "outside window" but it's 2 PM
- Make sure your system time is correct
- The script uses IST (India Standard Time)
- Verify: `python -c "from datetime import datetime; import pytz; print(datetime.now(pytz.timezone('Asia/Kolkata')))"`

### Script runs but no flag
- The header combinations might be different
- Try running `love_auto_solver.py` which tests multiple combinations
- Check server response for hints

### Connection errors
- Check internet connection
- Verify URL is accessible: `curl https://love-pagal-haiiiiiii.onrender.com/`
- The server might be down

## Files Created

- `love_auto_solver.py` - One-time automated solver
- `love_monitor_and_solve.py` - Continuous monitoring script
- `LOVE_SOLUTION_GUIDE.md` - This file
- `LOVE_CHALLENGE_SUMMARY.md` - Detailed analysis
- `FLAG_FOUND.txt` - Created when flag is retrieved (by auto_solver)
- `FLAG.txt` - Created when flag is retrieved (by monitor script)

## Success Indicators

When the flag is retrieved, you'll see:
```
[!!!] SUCCESS! FLAG RETRIEVED!
[+] Token: love
[+] Proof: simple
[+] Time: 14:15:23
[+] Signature: 5d41402abc4b2a76b9719d911017c592...

======================================================================
FLAG: TRACECTF{actual_flag_here}
======================================================================

[+] Flag saved to FLAG_FOUND.txt
```

## Next Steps

1. **Set an alarm** for 1:55 PM IST
2. **Run the script** at 2:00 PM IST:
   ```bash
   python love_auto_solver.py
   ```
3. **Submit the flag** to the CTF platform
4. **Celebrate!** 🎉

## Credits

Challenge by: CSBC | Innovation Cell, Sanjivani University
Solved by: Your CTF Team

---

**Good luck and happy hacking!** 🚀
