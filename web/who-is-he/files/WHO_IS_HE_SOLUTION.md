# Who Is He - CTF Challenge Analysis

## Challenge Information
- **URL**: http://a68900d109aa.who-is-he.ctf.theromanxpl0.it
- **Flag Format**: TRX{...}
- **Type**: Web

## Analysis

### Source Code Review
The challenge provides source code for a Ruby Sinatra application (`app.rb`):
- Has a `/lookup` endpoint that takes a `domain` parameter
- Validates domain with regex: `/^[a-z.-]+$/`
- Executes: `whois #{@domain}` using `Open3.capture3`
- There's a `/readflag` SUID binary that requires specific argument

### Vulnerability
The regex `/^[a-z.-]+$/` in Ruby allows newlines by default (unlike other languages).
This enables command injection via newline character.

### Deployed Application
The deployed URL shows a SvelteKit CTF platform (frontend SPA), not the Ruby backend.
This suggests either:
1. The Ruby backend is on a different port/path
2. The challenge description/source is for a different instance
3. Need to access the actual challenge through the CTF platform

## Next Steps
Need to:
1. Access the actual CTF platform and find the "who-is-he" challenge
2. Get the correct instance URL for the Ruby backend
3. Or determine if the challenge is something else entirely

The mismatch between source code (Ruby/Sinatra) and deployed app (SvelteKit) suggests
we're looking at the wrong endpoint or need to navigate through the CTF platform first.
