# Intern Portal Challenge - Analysis Summary

## Challenge Info
- **Category**: Web
- **Points**: 854 (10splayaSec8)
- **Hint**: "The intern said they made a custom report application... but I don't think security was in mind." + "I hear something...."
- **URL**: http://23.179.17.92:5001
- **Flag Format**: `CIT{...}`

## Application Features
- User registration and login
- Create reports with title and content fields
- View own reports
- Reports stored with sequential IDs

## Vulnerabilities Found

### 1. Insecure Direct Object Reference (IDOR) ✓
- Can access any report by ID: `/report?id=X`
- Tested IDs 1-100, 1000, and recent IDs
- No flag found in accessible reports

### 2. Input Sanitization
- HTML content is escaped in reports
- XSS payloads are neutralized
- SSTI payloads ({{7*7}}) are escaped
- XXE payloads are escaped

### 3. Session Management
- Flask session cookie format: `{"user_id": XXXX}`
- Session is signed (cannot forge easily)

## Attack Vectors Tested

### ❌ Failed Attempts:
1. **SQL Injection in Login**: Payloads accepted but don't bypass authentication
2. **SQL Injection in Report ID**: No error messages or data leakage
3. **SSTI (Server-Side Template Injection)**: Content is escaped
4. **XXE (XML External Entity)**: Content is escaped
5. **LFI via iframe/object tags**: Content is escaped, no PDF generation found
6. **Path Traversal**: No file access
7. **Admin Panel Access**: `/admin`, `/admin/reports` return 404
8. **Source Code Access**: `/app.py`, `/.env`, `/flag.txt` return 404
9. **Directory Listing**: Not enabled
10. **Error-Based SQLi**: No verbose errors
11. **Time-Based SQLi**: No delays detected
12. **Boolean-Based SQLi**: No differential responses
13. **UNION-Based SQLi**: No data extraction
14. **Session Manipulation**: Cannot forge admin session
15. **HTTP Method Testing**: Only standard methods allowed
16. **Parameter Pollution**: No effect
17. **Special Report IDs**: 0, -1, negative numbers return nothing

## Observations

1. **"I hear something" hint**: Unusual phrasing - could indicate:
   - Audio steganography component
   - Listening/monitoring functionality
   - Webhook/callback feature
   - Network traffic analysis needed

2. **Report Content**: All tested payloads show escaped content
   - Suggests strong input sanitization
   - But hint says "security was not in mind"

3. **Missing Features**:
   - No PDF generation endpoint found
   - No file upload functionality
   - No export/download feature
   - No admin panel accessible

## Possible Next Steps

1. **Deeper IDOR Testing**:
   - Systematically check ALL report IDs (may take time)
   - Flag might be in a specific admin report

2. **Race Condition**:
   - Try concurrent requests
   - Check for timing-based vulnerabilities

3. **SSRF (Server-Side Request Forgery)**:
   - If there's a PDF generation feature we haven't found
   - Try to make server request external URLs

4. **Second-Order Injection**:
   - Create report with SQLi payload
   - See if it's executed when admin views it

5. **Blind SQLi with Binary Search**:
   - Extract flag character by character
   - Use boolean-based or time-based techniques

6. **Check for Hidden Endpoints**:
   - Fuzz for additional endpoints
   - `/api/`, `/v1/`, `/internal/`, etc.

7. **WebSocket/Real-time Features**:
   - "I hear something" might indicate WebSocket
   - Check for `/socket.io`, `/ws`, etc.

8. **JWT/Token Manipulation**:
   - If there are API endpoints with JWT auth

## Files Created
- `intern_portal_recon.py` - Initial reconnaissance
- `intern_portal_explore.py` - Feature exploration
- `intern_portal_login.py` - Login testing
- `intern_portal_dashboard_check.py` - Dashboard analysis
- `intern_portal_exploit.py` - PDF LFI testing
- `intern_portal_idor_test.py` - IDOR vulnerability testing
- `intern_portal_find_flag.py` - Systematic flag search
- `intern_portal_smart_search.py` - Targeted search
- `intern_portal_session_analysis.py` - Session cookie analysis
- `intern_portal_sqli_exploit.py` - SQL injection attempts
- `intern_portal_xxe_test.py` - XXE and SSTI testing
- `intern_portal_final_check.py` - Comprehensive checks
- `intern_portal_error_based.py` - Error-based SQLi
- `intern_portal_static_check.py` - Static file enumeration
- `intern_portal_special_ids.py` - Special ID testing
- `intern_portal_sqli_union.py` - UNION-based SQLi

## Recommendation
The challenge likely requires:
1. Finding a specific report ID with the flag (brute force all IDs)
2. Discovering a hidden endpoint or feature
3. Exploiting a subtle vulnerability we haven't identified yet
4. Understanding the "I hear something" hint more literally

The IDOR vulnerability is confirmed, so the flag is likely in a report we haven't accessed yet.
