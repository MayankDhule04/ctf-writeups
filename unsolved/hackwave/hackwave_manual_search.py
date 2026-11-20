import re

# Read the JavaScript file
with open('hackwave_js_0.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

print("="*70)
print("MANUAL SEARCH FOR STAGE DATA")
print("="*70)

# Search for "Stage 1" through "Stage 8"
print("\n[*] Searching for 'Stage X' strings...")
for i in range(1, 9):
    # Find context around "Stage X"
    pattern = rf'.{{0,200}}Stage\s*{i}.{{0,200}}'
    matches = re.findall(pattern, js_content, re.IGNORECASE)
    if matches:
        print(f"\n--- Stage {i} ---")
        for match in matches[:3]:
            print(match.strip())

# Search for common CTF fragment patterns
print("\n" + "="*70)
print("[*] Searching for 4-character sequences in quotes...")
print("="*70)

# Find all 4-char strings
four_char = re.findall(r'["\']([A-Za-z0-9_]{4})["\']', js_content)
unique_four = list(set(four_char))

# Filter out common React/JS keywords
common_words = ['true', 'false', 'null', 'void', 'this', 'self', 'type', 'name', 'data', 'text', 'html', 'json', 'http', 'href', 'link', 'path', 'file', 'code', 'mode', 'size', 'time', 'date', 'user', 'pass', 'auth', 'role', 'page', 'view', 'form', 'post', 'load', 'save', 'open', 'close', 'show', 'hide', 'menu', 'list', 'item', 'main', 'body', 'head', 'meta', 'span', 'root', 'app']

filtered = [x for x in unique_four if x.lower() not in common_words and not x.isdigit()]

print(f"Found {len(filtered)} potential fragments (filtered):")
for i, frag in enumerate(sorted(filtered)[:50], 1):
    print(f"  {i:2d}. {frag}")

# Search for specific challenge-related keywords
print("\n" + "="*70)
print("[*] Searching for challenge keywords...")
print("="*70)

keywords = ['fragment', 'flag', 'HW{', 'stage', 'challenge', 'hint', 'clue', 'hidden', 'secret']
for keyword in keywords:
    count = js_content.lower().count(keyword.lower())
    print(f"  '{keyword}': {count} occurrences")

# Try to find the stages data structure
print("\n" + "="*70)
print("[*] Looking for stages data structure...")
print("="*70)

# Look for array with 8 elements
eight_elem_pattern = r'\[([^\]]{200,})\]'
matches = re.findall(eight_elem_pattern, js_content)
print(f"Found {len(matches)} arrays")

# Check if any contain stage-related info
for i, match in enumerate(matches):
    if 'stage' in match.lower() and len(match) > 500:
        print(f"\nArray {i} (contains 'stage'):")
        print(match[:500])
        break

# Search for the word "fragment" with context
print("\n" + "="*70)
print("[*] Context around 'fragment' keyword...")
print("="*70)

fragment_contexts = re.findall(r'.{50}fragment.{50}', js_content, re.IGNORECASE)
for i, ctx in enumerate(fragment_contexts[:15], 1):
    print(f"{i:2d}. ...{ctx}...")

print("\n" + "="*70)
print("SEARCH COMPLETE")
print("="*70)
