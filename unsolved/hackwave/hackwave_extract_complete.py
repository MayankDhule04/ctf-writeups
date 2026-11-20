import re
import json

# Read the JavaScript file
with open('hackwave_js_0.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

print("="*70)
print("EXTRACTING COMPLETE STAGE INFORMATION")
print("="*70)

# Search for the stages array - it should have id, title, category, description, etc.
# Pattern: {id:1,title:`...`,category:`...`,description:`...`,...}

# Find all stage objects
stage_pattern = r'\{id:(\d+),title:`([^`]+)`,category:`([^`]+)`,description:`([^`]+)`[^}]*endpoint:`([^`]*)`[^}]*answerHint:`([^`]+)`'

matches = re.findall(stage_pattern, js_content)

if matches:
    print(f"\n[+] Found {len(matches)} stages!\n")
    
    stages = []
    for match in matches:
        stage_id, title, category, description, endpoint, answer_hint = match
        stage = {
            'id': int(stage_id),
            'title': title,
            'category': category,
            'description': description,
            'endpoint': endpoint,
            'answer_hint': answer_hint
        }
        stages.append(stage)
        
        print(f"--- STAGE {stage_id} ---")
        print(f"Title: {title}")
        print(f"Category: {category}")
        print(f"Description: {description}")
        print(f"Endpoint: {endpoint}")
        print(f"Answer Hint: {answer_hint}")
        print()
    
    # Save to JSON
    with open('hackwave_stages.json', 'w') as f:
        json.dump(stages, f, indent=2)
    
    print(f"[+] Saved {len(stages)} stages to hackwave_stages.json")
else:
    print("[-] No stages found with that pattern")
    
    # Try alternative pattern
    print("\n[*] Trying alternative extraction...")
    
    # Look for objects with id and title
    alt_pattern = r'\{id:(\d+)[^}]{50,500}\}'
    matches = re.findall(alt_pattern, js_content)
    print(f"Found {len(matches)} objects with id field")
    
    # Print some context
    for i in range(1, 9):
        context = re.search(rf'id:{i}[^}}]{{100,600}}', js_content)
        if context:
            print(f"\n--- Stage {i} context ---")
            print(context.group(0))

print("\n" + "="*70)
print("EXTRACTION COMPLETE")
print("="*70)
