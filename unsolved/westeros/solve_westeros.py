#!/usr/bin/env python3
"""
Seven Kingdoms - Correct Solution
Following the exact steps from the guide
"""

print("[*] Seven Kingdoms Crypto - Step by Step")
print("=" * 70)

# Part 1: ⚔️ - ASCII Decimal + Leet Speak
print("\n[PART 1: ⚔️]")
part1 = [74, 111, 48, 104, 53]
print(f"Input: {part1}")

# Step 1: Convert to ASCII
part1_ascii = ''.join([chr(x) for x in part1])
print(f"Step 1 - ASCII: {part1_ascii}")

# Step 2: Check for leet speak
# The guide says: "If digits appear inside the word, check for leet substitutions"
# Jo0h5 -> J + o + 0 + h + 5
# 0 = o, 5 = s
# So: Jo0h5 -> Joohs? Or is it meant to be read as "Johs" -> "Josh"?
# Actually, looking at GoT: could be "Jon" + something?
# Let me try: J + o + 0(o) + h + 5(s) = "Joohs"
# But that's not a GoT word... 
# Wait - what if it's: 74=J, 111=o, 48=0, 104=h, 53=5
# And we need to interpret 0 and 5 as letters: 0=o, 5=s
# Result: J-o-o-h-s = "Joohs"
# But in GoT context, maybe it's meant to be "Jon" + "s" = "Jons"?
# Or the leet is: 0->o, 5->s giving us "Joohs"

# Let me try another interpretation:
# What if the numbers themselves need different conversion?
# 74, 111, 48, 104, 53
# Maybe 48 and 53 are meant to be converted differently?

# Actually, let me check if these could spell "Jon" or "Joffrey"
# J=74, o=111, n=110... so 48 is not 'n'
# Let me just follow the guide: convert to ASCII, then leet
part1_leet = part1_ascii.replace('0', 'o').replace('5', 's').replace('3', 'e').replace('1', 'i').replace('4', 'a').replace('7', 't')
print(f"Step 2 - Leet decoded: {part1_leet}")

# Part 2: 🛡️ - Bacon Cipher
print("\n[PART 2: 🛡️]")
part2 = [97, 98, 97, 97, 97, 32, 98, 97, 97, 97, 98]
print(f"Input: {part2}")

# Step 1: ASCII
part2_ascii = ''.join([chr(x) for x in part2])
print(f"Step 1 - ASCII: {repr(part2_ascii)}")

# Step 2: Remove space (32)
part2_clean = part2_ascii.replace(' ', '')
print(f"Step 2 - Remove space: {repr(part2_clean)}")

# Step 3: Group into 5s
groups = [part2_clean[i:i+5] for i in range(0, len(part2_clean), 5)]
print(f"Step 3 - Groups of 5: {groups}")

# Step 4 & 5: Bacon decode
bacon = {
    'aaaaa': 'a', 'aaaab': 'b', 'aaaba': 'c', 'aaabb': 'd', 'aabaa': 'e',
    'aabab': 'f', 'aabba': 'g', 'aabbb': 'h', 'abaaa': 'i', 'abaab': 'j',
    'ababa': 'k', 'ababb': 'l', 'abbaa': 'm', 'abbab': 'n', 'abbba': 'o',
    'abbbb': 'p', 'baaaa': 'q', 'baaab': 'r', 'baaba': 's', 'baabb': 't',
    'babaa': 'u', 'babab': 'v', 'babba': 'w', 'babbb': 'x', 'bbaaa': 'y',
    'bbaab': 'z'
}

part2_decoded = ''
for g in groups:
    if len(g) == 5:
        letter = bacon.get(g, '?')
        part2_decoded += letter
        print(f"  {g} -> {letter}")

print(f"Step 5 - Bacon decoded: {part2_decoded}")

# Part 3: 👑 - Caesar Cipher
print("\n[PART 3: 👑]")
part3 = [105, 108, 98, 99, 102, 118]
print(f"Input: {part3}")

# Step 1: ASCII
part3_ascii = ''.join([chr(x) for x in part3])
print(f"Step 1 - ASCII: {part3_ascii}")

# Step 2 & 3: Caesar brute force
print(f"Step 2 & 3 - Caesar brute force:")

# Check against common English words
common_words = ['winter', 'coming', 'stark', 'dragon', 'throne', 'sword', 'crown', 
                'honor', 'fire', 'blood', 'iron', 'gold', 'king', 'queen', 'north',
                'south', 'wall', 'night', 'watch', 'ghost', 'wolf', 'snow', 'dead',
                'white', 'black', 'red', 'green', 'blue', 'house', 'lord', 'lady']

part3_decoded = None
for shift in range(26):
    decoded = ''
    for char in part3_ascii:
        if char.isalpha():
            if char.islower():
                decoded += chr((ord(char) - ord('a') + shift) % 26 + ord('a'))
            else:
                decoded += chr((ord(char) - ord('A') + shift) % 26 + ord('A'))
    
    is_word = decoded in common_words
    marker = " *** MATCH ***" if is_word else ""
    print(f"  Shift {shift:2d}: {decoded}{marker}")
    
    if is_word and not part3_decoded:
        part3_decoded = decoded

if not part3_decoded:
    print("\n[!] No common word found. Trying ROT13 (shift 13):")
    part3_decoded = ''
    for char in part3_ascii:
        if char.isalpha():
            part3_decoded += chr((ord(char) - ord('a') + 13) % 26 + ord('a'))
    print(f"  ROT13: {part3_decoded}")

# Final Flag
print("\n" + "=" * 70)
print("[FINAL FLAG]")
print(f"Part 1: {part1_leet}")
print(f"Part 2: {part2_decoded}")
print(f"Part 3: {part3_decoded if part3_decoded else part3_ascii}")

flag = f"Kaal{{{part1_leet}_{part2_decoded}_{part3_decoded if part3_decoded else part3_ascii}}}"
print(f"\nFLAG: {flag}")
print("=" * 70)
