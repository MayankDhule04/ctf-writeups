import re
import json

# Read the JavaScript file
with open('hackwave_js_0.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

print("="*70)
print("EXTRACTING STAGE INFORMATION")
print("="*70)

# Look for stage definitions
# Common patterns in React apps
patterns = [
    r'stage[s]?\s*[:=]\s*\[([^\]]+)\]',
    r'stages\s*=\s*\{([^}]+)\}',
    r'const\s+stages\s*=\s*([^;]+);',
    r'fragment[s]?\s*[:=]\s*\[([^\]]+)\]',
    r'STAGE_\d+["\']?\s*[:=]\s*["\']([^"\']+)["\']',
]

for pattern in patterns:
    matches = re.findall(pattern, js_content, re.IGNORECASE | re.DOTALL)
    if matches:
        print(f"\nPattern: {pattern}")
        for match in matches[:5]:
            print(f"  {match[:200]}")

# Look for numbered stages
print("\n" + "="*70)
print("SEARCHING FOR STAGE NUMBERS")
print("="*70)

for i in range(1, 9):
    # Look for Stage 1, Stage 2, etc.
    stage_pattern = rf'[Ss]tage\s*{i}[^a-zA-Z0-9]{{1,50}}([a-zA-Z0-9_]{{4}})'
    matches = re.findall(stage_pattern, js_content)
    if matches:
        print(f"Stage {i}: {matches}")
    
    # Look for stage: 1, stage: 2, etc.
    stage_obj_pattern = rf'stage["\']?\s*:\s*{i}[^}}]{{0,200}}'
    matches = re.findall(stage_obj_pattern, js_content, re.IGNORECASE)
    if matches:
        print(f"Stage {i} object: {matches[0][:150]}")

# Look for the actual fragment values
print("\n" + "="*70)
print("SEARCHING FOR FRAGMENT VALUES")
print("="*70)

# Look for objects with fragment property
fragment_pattern = r'\{[^}]*fragment["\']?\s*:\s*["\']([A-Za-z0-9_]{4})["\'][^}]*\}'
matches = re.findall(fragment_pattern, js_content, re.IGNORECASE)
if matches:
    print(f"Found {len(matches)} fragment values:")
    for i, match in enumerate(set(matches), 1):
        print(f"  {i}. {match}")

# Look for hint patterns
print("\n" + "="*70)
print("SEARCHING FOR HINTS")
print("="*70)

hint_pattern = r'hint["\']?\s*:\s*["\']([^"\']{20,150})["\']'
matches = re.findall(hint_pattern, js_content, re.IGNORECASE)
if matches:
    print(f"Found {len(matches)} hints:")
    for i, match in enumerate(matches[:10], 1):
        print(f"  {i}. {match}")

# Look for description patterns
desc_pattern = r'description["\']?\s*:\s*["\']([^"\']{30,200})["\']'
matches = re.findall(desc_pattern, js_content, re.IGNORECASE)
if matches:
    print(f"\nFound {len(matches)} descriptions:")
    for i, match in enumerate(matches[:10], 1):
        print(f"  {i}. {match[:100]}")

# Try to find the stages array more specifically
print("\n" + "="*70)
print("LOOKING FOR STAGES ARRAY")
print("="*70)

# Look for array of objects with stage info
array_pattern = r'\[\s*\{[^]]{500,3000}\}\s*\]'
matches = re.findall(array_pattern, js_content)
print(f"Found {len(matches)} potential arrays")

# Try to extract a specific section that looks like stage definitions
stage_section = re.search(r'(const\s+\w+\s*=\s*\[\s*\{[^]]{1000,5000}stage[^]]{1000,5000}\]\s*)', js_content, re.IGNORECASE)
if stage_section:
    print("\nFound potential stages section:")
    print(stage_section.group(1)[:500])

print("\n" + "="*70)
print("COMPLETE - Check output above for stage information")
print("="*70)
