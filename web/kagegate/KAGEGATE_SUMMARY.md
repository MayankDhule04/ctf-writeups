# KageGate Challenge Summary

## Challenge Description
- Platform that "records names quietly, stores scrolls in shadow"
- "Your identity already exists" - no registration needed
- "Seals of time and honor" - timing-based restrictions
- "Some gates open early. Some seals are shared when they should not be"

## What I Found

### OAuth Flow
1. Visit `/consent` - shows KageGate consent page
2. Click "Allow" - GET `/callback`
3. Receives JWT in `auth` cookie

### JWT Analysis
```
Header: {"alg": "HS256", "typ": "JWT"}

Payload:
{
  "sub": "8765108499",
  "email": "john@mail.com",
  "username": "clan_shimazu",
  "scope": "username email",
  "iat": 1768645068,      # Issued at: Jan 17, 2026
  "nbf": 1800181068,      # Not before: Jan 17, 2027 (365 days later!)
  "exp": 1800181248,      # Expires: 3 minutes after nbf
  "iss": "kagegate",
  "aud": "dojo-web"
}
```

### The Vulnerability
The JWT has a `nbf` (not before) claim set to **365 days in the future**!
- This is the "seal of time" mentioned in the challenge
- The token won't be valid until 2027
- Need to either:
  1. Remove the `nbf` claim and re-sign with the correct secret
  2. Crack the HS256 secret to forge a valid token

### What I Tried
- ✗ alg=none attack - rejected
- ✗ Weak secrets (50+ attempts): secret, password, kagegate, shadow, ninja, samurai, dojo, etc.
- ✗ JWT-derived secrets: all payload/header values
- ✗ Time-related secrets: 31536000, 365, timestamps
- ✗ Direct login bypass
- ✗ Different endpoints

### Next Steps to Solve

**Option 1: Brute Force with Proper Tools**
```bash
# Using hashcat (mode 16500 for JWT HS256)
hashcat -m 16500 -a 0 jwt_token.txt rockyou.txt

# Using jwt_tool
python3 jwt_tool.py <JWT> -C -d /path/to/wordlist.txt
```

**Option 2: The Secret Might Be**
- A common password from rockyou.txt
- Related to Japanese/ninja theme I haven't tried
- A phrase from the challenge description
- Something obvious I'm missing

**Option 3: Different Approach**
- Maybe there's a `/admin` or `/api` endpoint that leaks the secret
- Maybe the secret is in a JavaScript file or API response
- Maybe there's a race condition or timing attack

## JWT Token for Cracking
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4NzY1MTA4NDk5IiwiZW1haWwiOiJqb2huQG1haWwuY29tIiwidXNlcm5hbWUiOiJjbGFuX3NoaW1henUiLCJzY29wZSI6InVzZXJuYW1lIGVtYWlsIiwiaWF0IjoxNzY4NjQ1MDY4LCJuYmYiOjE4MDAxODEwNjgsImV4cCI6MTgwMDE4MTI0OCwiaXNzIjoia2FnZWdhdGUiLCJhdWQiOiJkb2pvLXdlYiJ9.kbbbCV8KySucjmkPQdChbhsiWfzYhhRzXUtw-iPR7v4
```

## Recommended Action
Use `hashcat` or `john` with a comprehensive wordlist (rockyou.txt) to crack the HS256 secret.
Once cracked, forge a new JWT without the `nbf` claim and access `/flag`.
