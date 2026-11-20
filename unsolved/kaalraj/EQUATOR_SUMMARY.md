# Equator Navigation System - CTF Challenge Summary

## Challenge Information
- **URL**: http://138.199.163.92:12973/
- **Name**: Equator Navigation System
- **Description**: Geohashing puzzle with security bypass
- **Flag Format**: `Kaal{...}`
- **Author**: M33T SH@H

## Flags Found (All Decoys)

1. **Kaal{html_c0mm3nts_ar3_n0t_s3cur3}**
   - Location: HTML comment in main page
   - Line: `<!-- Debug Flag: Kaal{html_c0mm3nts_ar3_n0t_s3cur3} -->`

2. **Kaal{r0b0ts_d0nt_k33p_s3cr3ts}**
   - Location: robots.txt
   - Line: `# Test Flag: Kaal{r0b0ts_d0nt_k33p_s3cr3ts}`

3. **Kaal{r0b0ts_txt_l3d_m3_h3r3}**
   - Location: /flag.txt
   - Content: Marked as decoy

## Challenge Structure

### Accessible Endpoints
- `/` - Main page with challenge info
- `/robots.txt` - Contains disallowed paths
- `/flag.txt` - Decoy flag
- `/backup.bin` - Dynamic SHA384 hash (changes each request)
- `/login` - Login form (GET/POST)

### Protected Endpoints (Require JWT)
- `/admin` - Returns 401 "Authentication required"
- `/api/v3/geohash-debug-2025` - Returns 401 "Authentication required"

## Key Information from Page

### Null Island
- Coordinates: 0°N, 0°E
- Location: Gulf of Guinea, Atlantic Ocean
- Geohash: u000 sector
- Graticule: Grid Reference 0,0

### Security Info
- Authentication: JWT Token Required
- API Version: v3.0
- Encryption: AES-256-CBC
- Access Control: Role-Based (ADMIN)

### Hints from Page
- "Not all authentication mechanisms are secure"
- "Legacy systems may contain vulnerabilities"
- "Hidden endpoints often reveal critical information"
- "The center of the world holds secrets"
- "Geospatial coordinates can be the key to everything"

## Attack Vectors Tested (All Failed)

### 1. JWT Attacks
- ✗ Weak secrets (tried 30+ common passwords)
- ✗ None algorithm bypass
- ✗ Algorithm confusion
- ✗ Different payload structures

### 2. Login Attacks
- ✗ SQL Injection (10+ payloads)
- ✗ NoSQL Injection
- ✗ LDAP Injection
- ✗ Command Injection
- ✗ Default credentials
- ✗ Common passwords

### 3. File/Directory Attacks
- ✗ Directory traversal
- ✗ .git exposure
- ✗ Backup file variations
- ✗ Source code exposure
- ✗ Config file exposure

### 4. Other Attacks
- ✗ Parameter pollution
- ✗ X-Forwarded headers
- ✗ IDOR
- ✗ Debug endpoints
- ✗ API endpoint enumeration

## Observations

1. **backup.bin is dynamic**
   - 48 bytes (SHA384 length)
   - Changes with each request
   - Not the JWT secret

2. **Login form exists**
   - Says "Default credentials have been disabled"
   - Accepts JSON POST
   - Returns 401 for all attempts

3. **JWT is required**
   - Both protected endpoints need valid JWT
   - Secret is unknown
   - Standard weak secrets don't work

4. **Geohashing theme**
   - Challenge mentions geohashing
   - Null Island (0,0) is significant
   - Geohash u000 mentioned

## Possible Solutions (Not Yet Found)

1. **Hidden JWT Secret**
   - May be in another file we haven't found
   - Could be derived from geohash/coordinates
   - Might be in page source (encoded)

2. **Credential Bruteforce**
   - Need correct username/password
   - Could be geohash-related
   - Might be coordinates-based

3. **JWT Vulnerability**
   - Algorithm confusion with public key
   - JWT secret in another endpoint
   - Weak secret we haven't tried

4. **Hidden Endpoint**
   - Another API endpoint that gives token
   - Debug endpoint with flag
   - Alternative authentication method

## Next Steps

1. Try more JWT secrets based on:
   - Geohash calculations
   - Coordinate transformations
   - Author name variations

2. Check for:
   - More hidden files
   - JavaScript in page source
   - Encoded data in HTML

3. Try:
   - Longer wordlists for JWT
   - Geohash-based credentials
   - Coordinate-based passwords

## Files Created
- `equator_solver.py` - Initial reconnaissance
- `equator_advanced.py` - Advanced analysis
- `equator_final_attack.py` - Comprehensive attack
- `equator_crack_sha384.py` - Hash cracking attempt
- `equator_smart_attack.py` - CTF-specific attacks
- `login_attack.py` - Login form attacks
- `check_for_jwt.py` - JWT token search
- `final_recon.py` - Final reconnaissance

## Status
**INCOMPLETE** - Real flag not yet found. All 3 flags found are marked as decoys.
