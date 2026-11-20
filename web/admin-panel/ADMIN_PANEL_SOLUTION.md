# Admin Panel CTF - Solution

## Challenge URL
https://admin-panel-ctf.onrender.com

## Solution Steps

### 1. Initial Reconnaissance
- Found login and registration pages
- Discovered robots.txt pointing to `/secret-backup.zip`
- Found JavaScript file `/static/app.min.js` revealing:
  - Proof-of-Work (PoW) challenge required for registration
  - JWT-based authentication
  - Login returns a token

### 2. Finding the Backup File
- robots.txt mentioned `/secret-backup.zip` but it returned 404
- Found the actual file at `/static/secret-backup.zip`
- Downloaded and extracted the backup

### 3. Backup Contents
The backup contained three files:

**config_old.txt:**
```
admin_user=admin
admin_pass=p@ssw0rd123
```

**notes.txt:**
```
moved flag storage to environment - do not commit credentials to repo again
```

**flag.txt:**
(Empty - flag moved to environment variables)

### 4. Admin Access
- Used credentials from backup: `admin:p@ssw0rd123`
- Successfully logged in as admin
- Received JWT token with `"role":"admin"`
- Accessed `/admin` endpoint

### 5. Admin Panel Content
The admin panel shows:
- User list (admin, john_doe, jane_smith)
- System status
- A fake flag: `flag{not_the_real_one_nice_try}`

### 6. Finding the Real Flag
According to notes.txt, the flag was "moved to environment". This suggests:
- The real flag is stored in an environment variable
- Need to find a way to read environment variables
- Possible methods:
  - SSTI (Server-Side Template Injection)
  - Debug endpoints
  - Error pages revealing environment
  - Source code access

## Current Status
✅ Found admin credentials
✅ Logged in as admin
✅ Accessed admin panel
❌ Real flag not yet found (stored in environment)

## Next Steps to Try
1. Test for SSTI in display_name field during registration
2. Try to trigger Flask debug mode or error pages
3. Look for endpoints that expose environment variables
4. Check if there's a way to execute commands or read files
5. Analyze the application framework for known vulnerabilities

## Key Files Created
- `admin_panel_recon.py` - Initial reconnaissance
- `admin_panel_explore.py` - Detailed exploration
- `admin_panel_find_backup.py` - Found backup at `/static/secret-backup.zip`
- `admin_panel_get_flag.py` - Login as admin
- `admin_panel_find_real_flag.py` - Search for real flag
- `admin_panel_deep_analysis.py` - HTML analysis
- `admin_panel_trigger_error.py` - Error page testing

## Admin Credentials
```
Username: admin
Password: p@ssw0rd123
```

## JWT Token Structure
```json
{
  "user": "admin",
  "role": "admin",
  "exp": <timestamp>
}
```

## Notes
- The challenge uses Proof-of-Work to prevent automated registration
- JWT secret is strong (not in common wordlists)
- Parameters in URLs trigger WAF (403 Forbidden)
- The real flag is likely in an environment variable that needs to be extracted
