#!/usr/bin/env python3
"""
Farcical Clones - Final comprehensive attempt
"""

cipher1 = [95, 181, 145, 39, 245, 91, 212, 232, 123, 220, 167, 69, 91, 208, 245, 164, 245, 145, 123, 94]
cipher2 = [62, 150, 94, 172, 83, 135, 96, 153, 2, 208, 96, 172]
flag_nums = [131, 91, 90, 53, 95, 218, 238, 211, 91, 4, 201, 182, 135, 245, 167, 74, 90, 145, 96, 238]

xor_result = bytes([cipher1[i] ^ flag_nums[i] for i in range(len(cipher1))])

print("="*70)
print("FARCICAL CLONES - FINAL ATTEMPT")
print("="*70)

# Try every possible 20-character phrase
# Focus on Star Wars and CTF themes

phrases = [
    # Star Wars quotes (20 chars exactly)
    "May the Force be wit",
    "may the force be wit",
    "May The Force Be Wit",
    "Use the Force, Luke!",
    "use the force, luke!",
    "I am your father!!!",
    "i am your father!!!",
    "The Force is strong!",
    "the force is strong!",
    "Do or do not, there ",
    "do or do not, there ",
    "Fear is the path to ",
    "fear is the path to ",
    "These are not the dr",
    "these are not the dr",
    "In a galaxy far, far",
    "in a galaxy far, far",
    "A long time ago in a",
    "a long time ago in a",
    "The dark side clouds",
    "the dark side clouds",
    "Always two there are",
    "always two there are",
    "Once you start down ",
    "once you start down ",
    "Wars not make one gr",
    "wars not make one gr",
    "Try not. Do or do no",
    "try not. do or do no",
    "You must unlearn wha",
    "you must unlearn wha",
    "Much to learn you st",
    "much to learn you st",
    "Size matters not. Lo",
    "size matters not. lo",
    "Judge me by my size,",
    "judge me by my size,",
    "Truly wonderful, the",
    "truly wonderful, the",
    # CTF/Bootstrap themed
    "Bootstrap the system",
    "bootstrap the system",
    "Farcical clones here",
    "farcical clones here",
    "Attack of the clones",
    "attack of the clones",
    "Clone wars beginning",
    "clone wars beginning",
    "The clones are ready",
    "the clones are ready",
    "Order sixty-six exec",
    "order sixty-six exec",
    "Jedi mind trick work",
    "jedi mind trick work",
    "Padawan training beg",
    "padawan training beg",
]

print("Testing phrases as Cipher1 plaintext...\n")

for phrase in phrases:
    if len(phrase) == 20:
        # Recover flag plaintext
        flag_plaintext = ''.join(chr(xor_result[i] ^ ord(phrase[i])) for i in range(20))
        
        # Check if it looks like a flag
        if flag_plaintext.startswith("CIT{") and flag_plaintext.endswith("}"):
            print(f"✓✓✓ FOUND COMPLETE FLAG!")
            print(f"  Cipher1: {phrase}")
            print(f"  Flag: {flag_plaintext}")
            print()
            break
        elif flag_plaintext.startswith("CIT{"):
            print(f"✓ Starts with CIT{{:")
            print(f"  Cipher1: {phrase}")
            print(f"  Flag: {flag_plaintext}")
            print()
        elif all(32 <= ord(c) < 127 for c in flag_plaintext):
            # All printable
            if "flag" in flag_plaintext.lower() or "clone" in flag_plaintext.lower():
                print(f"  Cipher1: {phrase}")
                print(f"  Flag: {flag_plaintext}")
                print()

print("="*70)
print("\nIf no match found, this might not be a simple two-time pad.")
print("The challenge might require a different approach or additional context.")
print("="*70)
