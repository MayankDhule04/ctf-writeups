# Sign Up and Enjoy - Challenge Summary

## Challenge Info
- **Name**: Sign Up and Enjoy
- **Category**: Web
- **Points**: 930 (10splayaSec2)
- **Hint**: "I'm confused, what does this application do exactly?"
- **URL**: http://23.179.17.92:5557
- **Flag Format**: `CIT{...}`

## Application Features
- User registration and login system
- Workspace dashboard
- **Link Preview Tool** at `/tools/link-preview`
- Session-based authentication using Flask signed cookies

## Vulnerabilities Identified

### 1. Link Preview Tool (Potential SSRF)
- **Endpoint**: `/tools/link-preview`
- **Parameter**: `target_url`
- **Behavior**: Accepts URLs and processes them asynchronously
- **Status**: Shows "Currently Processing..." then JavaScript changes to "Error occurred" after 10 seconds
- **Issue**: No results endpoint found, unclear where preview results are stored

### 2. Session Cookie Structure
- **Format**: Flask signed cookie (itsdangerous)
- **Content**: `{"role":"standard","uid":"u_XXXXXXXX","username":"USERNAME"}`
- **Signature**: Uses unknown secret key
- **Tested**: Common secrets (secret, dev, debug, etc.) - none worked
- **Role**: Always "standard" even when trying to inject "admin" during registration

## Attack Vectors Tested

### ✅ Tested (No Success)
1. **SQL Injection** - Login and registration forms
2. **SSTI** - Template injection attempts
3. **XXE** - XML external entity
4. **LFI** - Local file inclusion
5. **Path Traversal** - Directory traversal
6. **SSRF** - Server-side request forgery (file://, http://localhost, etc.)
7. **Parameter Pollution** - Multiple role parameters
8. **Session Forgery** - Tried common Flask secret keys
9. **Direct Role Injection** - Adding role=admin to registration
10. **IDOR** - Insecure direct object references
11. **Hidden Endpoints** - Checked /api, /internal, /admin/flag, etc.
12. **Static Files** - Checked /static/flag.txt, etc.
13. **HTML Comments** - No hidden flags in comments

### 🔄 Partially Tested
1. **SSRF with Async Processing** - Submitted requests but couldn't find results endpoint
2. **Session Secret Brute Force** - Only tried ~20 common secrets

## Observations

1. **Async Processing**: The link preview tool processes requests asynchronously
   - Shows "Currently Processing..." message
   - JavaScript updates to error after 10 seconds
   - No visible results endpoint

2. **Session Cookie**: 
   - Role is always "standard"
   - Cannot inject "admin" role during registration
   - Secret key is not a common value

3. **Hint Analysis**: "I'm confused, what does this application do exactly?"
   - Could mean the application's purpose is confusing
   - Could be about understanding async processing
   - Could be a red herring

## Possible Solutions

### 1. SSRF with Webhook
- The link preview might fetch URLs and store results somewhere
- Could need to use a webhook/callback URL to exfiltrate data
- Example: Submit URL to attacker-controlled server, app fetches it and leaks flag in request

### 2. Session Secret Brute Force
- Need to brute force Flask secret key more comprehensively
- Could use wordlists like rockyou.txt
- Once found, forge admin session

### 3. Hidden Results Endpoint
- Preview results might be stored at an endpoint we haven't found
- Could be user-specific: `/preview/{uid}` or `/results/{request_id}`
- Might need to enumerate IDs

### 4. Race Condition
- Async processing might have race condition
- Could exploit timing between request submission and processing

### 5. Client-Side Vulnerability
- JavaScript might have vulnerability
- Could be XSS or prototype pollution

## Next Steps

1. **Set up webhook server** to test SSRF exfiltration:
   ```python
   # Use ngrok or similar to get public URL
   # Submit http://YOUR_SERVER/webhook as target_url
   # Check if app makes request and what it sends
   ```

2. **Brute force Flask secret** more comprehensively:
   ```python
   # Use larger wordlist
   # Try challenge-specific words: signup, enjoy, campaign, city, etc.
   ```

3. **Enumerate preview request IDs**:
   ```python
   # Try /preview/1, /preview/2, etc.
   # Try /results/UUID patterns
   ```

4. **Check response headers** for hidden information

5. **Analyze JavaScript** in detail for client-side vulns

## Files Created
- `signup_enjoy_recon.py` - Initial reconnaissance
- `signup_enjoy_explore.py` - Deep exploration
- `signup_enjoy_attack.py` - SQL injection and auth bypass attempts
- `signup_enjoy_session_forge.py` - Session cookie forgery attempts
- `signup_enjoy_link_preview.py` - Link preview tool testing
- `signup_enjoy_ssrf_detailed.py` - Detailed SSRF testing
- `signup_enjoy_async_test.py` - Async processing tests
- `signup_enjoy_comprehensive.py` - Comprehensive attack script
- `signup_enjoy_final_ssrf.py` - Final SSRF payload testing
- `signup_enjoy_check_error.py` - Error message analysis
- `signup_enjoy_find_results.py` - Results endpoint enumeration
- `signup_enjoy_static_files.py` - Static file checking

## Recommendation

The most likely solution is **SSRF with webhook exfiltration** or **Flask secret key brute force**. The async processing suggests the app is fetching URLs in the background, and we need to either:
1. Find where results are stored
2. Use a webhook to receive the fetched content
3. Forge an admin session to access privileged endpoints

