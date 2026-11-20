# Hash of Weakness - Argon2 Challenge Solution

## Challenge Details
- **Name**: Hash of Weakness
- **Category**: Crypto
- **Points**: 450
- **Flag Format**: `Hack!tUp{...}`

## Hash Information
```
$argon2id$v=19$m=1024,t=2,p=1$AtVzx7UNpesvBaccM1kkdg$ZKvPZb3TZ4fXg5HzAUhamH6yp86UmJqy8AYRBYvMWis
```

### Parameters Analysis
- **Type**: argon2id (hybrid mode - combines argon2i and argon2d)
- **Version**: 19 (latest)
- **Memory**: 1024 KB ⚠️ **VERY WEAK** (default is 65536 KB = 64 MB)
- **Time**: 2 iterations ⚠️ **WEAK** (default is 3)
- **Parallelism**: 1 thread
- **Salt**: `AtVzx7UNpesvBaccM1kkdg` (base64)
- **Hash**: `ZKvPZb3TZ4fXg5HzAUhamH6yp86UmJqy8AYRBYvMWis` (base64)

## Why It's Weak

The challenge is called "Hash of Weakness" because the Argon2 parameters are intentionally weak:

1. **Memory Cost (m=1024)**: Only 1 MB instead of the recommended 64 MB
   - Makes it 64x faster to crack
   - Reduces memory-hardness protection

2. **Time Cost (t=2)**: Only 2 iterations instead of 3+
   - Makes it 33% faster to crack
   - Reduces computational cost

These weak parameters make the hash vulnerable to brute force attacks.

## Solution Approach

### Method 1: Hashcat (RECOMMENDED - Fastest)

Hashcat is a GPU-accelerated password cracker that's much faster than Python:

```bash
# Install hashcat (if not installed)
# Windows: Download from https://hashcat.net/hashcat/
# Linux: sudo apt install hashcat
# Mac: brew install hashcat

# Crack with rockyou.txt
hashcat -m 10900 -a 0 argon2_hash.txt rockyou.txt

# Or with a custom wordlist
hashcat -m 10900 -a 0 argon2_hash.txt wordlist.txt

# Brute force (4-6 characters, alphanumeric)
hashcat -m 10900 -a 3 argon2_hash.txt ?a?a?a?a
```

**Hashcat Mode**: `-m 10900` (Argon2)

### Method 2: John the Ripper

```bash
# Install john
# Linux: sudo apt install john
# Mac: brew install john

# Crack the hash
john --format=argon2 argon2_hash.txt --wordlist=rockyou.txt

# Show cracked password
john --show argon2_hash.txt
```

### Method 3: Python (Slow but works)

The provided Python scripts test common passwords:
- `argon2_hash_cracker.py` - Basic cracker
- `argon2_extended_crack.py` - Extended with brute force
- `argon2_smart_crack.py` - CTF-focused wordlist

```bash
python argon2_smart_crack.py
```

## Tested Wordlists

✅ Tested (No match):
- 86 CTF-specific passwords
- Top 1000 from rockyou.txt
- 3-character lowercase combinations (17,576 passwords)
- Partial 3-character alphanumeric (tested ~56,000)

## Next Steps

1. **Use Hashcat** with full rockyou.txt (14 million passwords)
2. **Brute force** 4-5 character passwords
3. **Try challenge-specific** wordlists related to:
   - "weakness"
   - "hash"
   - "argon2"
   - CTF/security terms

## Expected Flag Format

Once the password is found:
```
Hack!tUp{password_here}
```

## Files Created

- `argon2_hash.txt` - Hash file for hashcat/john
- `argon2_hash_cracker.py` - Basic Python cracker
- `argon2_extended_crack.py` - Extended Python cracker with brute force
- `argon2_smart_crack.py` - CTF-focused Python cracker
- `ARGON2_SOLUTION.md` - This file

## Performance Notes

- Python: ~500-700 passwords/second
- Hashcat (CPU): ~10,000-100,000 passwords/second
- Hashcat (GPU): ~1,000,000+ passwords/second

With weak parameters (m=1024, t=2), even a CPU can crack this relatively quickly with the right wordlist.

## Recommendation

**Use hashcat with rockyou.txt** - this is the fastest and most likely to succeed:

```bash
hashcat -m 10900 -a 0 argon2_hash.txt rockyou.txt --force
```

If rockyou.txt doesn't work, try brute forcing 4-5 character passwords:

```bash
# 4 characters, lowercase + digits
hashcat -m 10900 -a 3 argon2_hash.txt ?l?l?l?l
hashcat -m 10900 -a 3 argon2_hash.txt ?d?d?d?d
hashcat -m 10900 -a 3 argon2_hash.txt ?l?l?d?d

# 5 characters
hashcat -m 10900 -a 3 argon2_hash.txt ?l?l?l?l?l
```

Where:
- `?l` = lowercase letter (a-z)
- `?u` = uppercase letter (A-Z)
- `?d` = digit (0-9)
- `?a` = all printable ASCII
