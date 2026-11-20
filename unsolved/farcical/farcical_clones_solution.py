#!/usr/bin/env python3
"""
Farcical Clones - Final Solution
Two-time pad attack: Cipher1 and Flag encrypted with same OTP
"""

cipher1 = [95, 181, 145, 39, 245, 91, 212, 232, 123, 220, 167, 69, 91, 208, 245, 164, 245, 145, 123, 94]
flag_nums = [131, 91, 90, 53, 95, 218, 238, 211, 91, 4, 201, 182, 135, 245, 167, 74, 90, 145, 96, 238]

# XOR them to get plaintext1 XOR plaintext2
xor_result = [cipher1[i] ^ flag_nums[i] for i in range(len(cipher1))]

print("="*70)
print("FARCICAL CLONES - TWO-TIME PAD SOLUTION")
print("="*70)
print("Cipher1 XOR Flag = Plaintext1 XOR Plaintext2")
print(f"XOR result: {' '.join(f'{b:02x}' for b in xor_result)}")
print()

# We know flag format is CIT{...}
# Let's try different cribs for cipher1

# Star Wars quotes that are 20 characters:
cribs_cipher1 = [
    "May the Force be wit",  # 20 chars
    "May the force be wit",
    "The Force is strong",
    "Use the Force, Luke!",
    "I am your father!!!",
    "These are not the dr",  # "These are not the droids"
    "Do or do not, there ",  # "Do or do not, there is no try"
    "Fear is the path to ",  # "Fear is the path to the dark side"
    "In a galaxy far, fa",  # "In a galaxy far, far away"
    "A long time ago in a",
    "The dark side clouds",
    "Much to learn you st",  # "Much to learn you still have"
    "Size matters not. Lo",  # Yoda quote
    "Judge me by my size,",
    "Truly wonderful, the",  # "Truly wonderful, the mind of a child is"
    "Always two there are",  # Yoda about Sith
    "Once you start down ",  # "Once you start down the dark path"
    "Wars not make one gr",  # "Wars not make one great"
    "You must unlearn wha",  # "You must unlearn what you have learned"
    "Try not. Do or do no",  # "Try not. Do or do not"
]

print("[1] Trying Star Wars quotes as Cipher1 plaintext:")
for crib in cribs_cipher1:
    if len(crib) == 20:
        # Recover flag plaintext
        flag_plaintext = ''.join(chr(xor_result[i] ^ ord(crib[i])) for i in range(len(crib)))
        
        # Check if it starts with "CIT{"
        if flag_plaintext.startswith("CIT{"):
            print(f"\n✓✓ FOUND IT!")
            print(f"  Cipher1 plaintext: {crib}")
            print(f"  Flag plaintext: {flag_plaintext}")
            print(f"\n  FLAG: {flag_plaintext}")
            break
        
        # Check if it's mostly printable
        printable_count = sum(1 for c in flag_plaintext if 32 <= ord(c) < 127)
        if printable_count >= 18:
            print(f"\n  Cipher1: {crib}")
            print(f"  Flag: {flag_plaintext} (printable: {printable_count}/20)")

# If not found, try reverse - assume flag and recover cipher1
print("\n[2] Trying flag patterns:")
flag_patterns = [
    "CIT{attack_of_clone}",  # 20 chars
    "CIT{clone_wars_rule}",
    "CIT{may_the_force_b}",
    "CIT{farcical_clones}",
    "CIT{order_sixty_six}",
    "CIT{jedi_mind_trick}",
    "CIT{use_the_force_l}",
    "CIT{dark_side_power}",
]

for flag_pattern in flag_patterns:
    if len(flag_pattern) == 20:
        # Recover cipher1 plaintext
        cipher1_plaintext = ''.join(chr(xor_result[i] ^ ord(flag_pattern[i])) for i in range(len(flag_pattern)))
        
        # Check if it's readable
        printable_count = sum(1 for c in cipher1_plaintext if 32 <= ord(c) < 127)
        if printable_count >= 18:
            print(f"\n  Flag: {flag_pattern}")
            print(f"  Cipher1: {cipher1_plaintext} (printable: {printable_count}/20)")

print("\n" + "="*70)
