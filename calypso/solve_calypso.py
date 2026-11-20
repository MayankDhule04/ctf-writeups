#!/usr/bin/env python3
"""
Extended Argon2 cracker with more comprehensive wordlists
"""

from argon2.low_level import hash_secret_raw, Type as ArgonType
import base64
import time
import itertools

# The hash to crack
target_hash = "$argon2id$v=19$m=1024,t=2,p=1$AtVzx7UNpesvBaccM1kkdg$ZKvPZb3TZ4fXg5HzAUhamH6yp86UmJqy8AYRBYvMWis"

parts = target_hash.split('$')
salt_b64 = parts[4]
hash_b64 = parts[5]

salt = base64.b64decode(salt_b64 + '==')
expected_hash = base64.b64decode(hash_b64 + '==')

print("=" * 70)
print("Extended Argon2 Hash Cracker")
print("=" * 70)

def try_password(password):
    """Try a password against the hash"""
    try:
        computed_hash = hash_secret_raw(
            secret=password.encode(),
            salt=salt,
            time_cost=2,
            memory_cost=1024,
            parallelism=1,
            hash_len=32,
            type=ArgonType.ID
        )
        return computed_hash == expected_hash
    except Exception as e:
        return False

start_time = time.time()
attempts = 0

# Extended wordlist with more variations
extended_wordlist = [
    # Basic
    "password", "123456", "12345678", "qwerty", "abc123", "password123",
    "admin", "root", "user", "test", "guest", "demo",
    
    # Challenge-specific
    "weakness", "weak", "hash", "argon2", "argon", "crypto", "ctf",
    "hackitup", "hack", "security", "authentication", "auth",
    
    # Common words
    "welcome", "hello", "world", "secret", "private", "secure",
    "login", "access", "system", "computer", "internet",
    
    # Simple patterns
    "pass", "pass123", "admin123", "root123", "test123",
    "password1", "password2", "password!", "password@",
    
    # Numbers
    "123", "1234", "12345", "123456", "1234567", "12345678",
    "000", "0000", "00000", "111", "1111", "11111",
    
    # Leet speak
    "p@ssw0rd", "p@ss", "adm1n", "r00t", "h@ck", "w3@k",
    
    # CTF common
    "flag", "ctf", "challenge", "solve", "crack", "brute",
    
    # Weakness-related
    "lowmemory", "weakparam", "weakparams", "1024", "m1024",
    "t2", "p1", "weak_hash", "weakhash", "hashweak",
    
    # Single words
    "a", "b", "c", "d", "e", "f", "g", "h", "i", "j",
    "1", "2", "3", "4", "5", "6", "7", "8", "9", "0",
    
    # Two letters
    "aa", "ab", "ac", "ad", "ae", "af", "ag", "ah", "ai", "aj",
    "ba", "bb", "bc", "bd", "be", "bf", "bg", "bh", "bi", "bj",
    
    # Common short words
    "cat", "dog", "god", "man", "boy", "girl", "sun", "moon",
    "star", "sky", "sea", "tree", "fire", "water", "earth",
    
    # Tech terms
    "linux", "windows", "mac", "unix", "shell", "bash", "cmd",
    "python", "java", "code", "debug", "error", "bug",
]

print(f"[*] Testing {len(extended_wordlist)} passwords from extended wordlist...")
print()

for password in extended_wordlist:
    attempts += 1
    if attempts % 10 == 0:
        elapsed = time.time() - start_time
        rate = attempts / elapsed if elapsed > 0 else 0
        print(f"  [{attempts}/{len(extended_wordlist)}] Testing: {password:20s} ({rate:.1f} p/s)", end='\r')
    
    if try_password(password):
        elapsed = time.time() - start_time
        print()
        print()
        print("=" * 70)
        print("SUCCESS! Password found!")
        print("=" * 70)
        print(f"Password: {password}")
        print(f"Attempts: {attempts}")
        print(f"Time: {elapsed:.2f} seconds")
        print()
        print(f"Flag: Hack!tUp{{{password}}}")
        print("=" * 70)
        exit(0)

print()
print()
print("[*] Testing 3-character lowercase combinations...")
print()

# Try 3-character lowercase combinations (26^3 = 17,576)
for combo in itertools.product('abcdefghijklmnopqrstuvwxyz', repeat=3):
    password = ''.join(combo)
    attempts += 1
    
    if attempts % 100 == 0:
        elapsed = time.time() - start_time
        rate = attempts / elapsed if elapsed > 0 else 0
        print(f"  Tested {attempts} passwords ({rate:.1f} p/s) - Current: {password}", end='\r')
    
    if try_password(password):
        elapsed = time.time() - start_time
        print()
        print()
        print("=" * 70)
        print("SUCCESS! Password found!")
        print("=" * 70)
        print(f"Password: {password}")
        print(f"Attempts: {attempts}")
        print(f"Time: {elapsed:.2f} seconds")
        print()
        print(f"Flag: Hack!tUp{{{password}}}")
        print("=" * 70)
        exit(0)

print()
print()
print("[*] Testing 3-character alphanumeric combinations...")
print()

# Try 3-character alphanumeric (36^3 = 46,656)
for combo in itertools.product('abcdefghijklmnopqrstuvwxyz0123456789', repeat=3):
    password = ''.join(combo)
    attempts += 1
    
    if attempts % 100 == 0:
        elapsed = time.time() - start_time
        rate = attempts / elapsed if elapsed > 0 else 0
        print(f"  Tested {attempts} passwords ({rate:.1f} p/s) - Current: {password}", end='\r')
    
    if try_password(password):
        elapsed = time.time() - start_time
        print()
        print()
        print("=" * 70)
        print("SUCCESS! Password found!")
        print("=" * 70)
        print(f"Password: {password}")
        print(f"Attempts: {attempts}")
        print(f"Time: {elapsed:.2f} seconds")
        print()
        print(f"Flag: Hack!tUp{{{password}}}")
        print("=" * 70)
        exit(0)

print()
print()
elapsed = time.time() - start_time
print(f"[-] Password not found after {attempts} attempts in {elapsed:.2f} seconds")
print()
print("[*] The password is likely longer or uses special characters")
print("[*] Recommend using hashcat with rockyou.txt:")
print("    hashcat -m 10900 -a 0 hash.txt rockyou.txt")
