#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests, re, json, sys

# Fix encoding
sys.stdout.reconfigure(encoding='utf-8')

base = 'https://gokul-hidden-makhan.vercel.app'
s = requests.Session()
s.headers.update({'Content-Type': 'application/json', 'Origin': base, 'Referer': base + '/'})

with open('chakra_bundle.js', encoding='utf-8') as f:
    js = f.read()

# Find the API base path
idx = js.find('/api/')
print(f'API path context: {js[max(0,idx-100):idx+200]}')

# Find all strings after verify-clue, break-handi, extract endpoints
# The clue IDs - find them around the verify-clue call
# From earlier: Oo(e,t) posts to /verify-clue with {clueId:e, answer:t}
# Find where Oo() is called with actual IDs
calls = re.findall(r'Oo\(["\']([^"\']+)["\']', js)
print(f'\nOo() calls with string arg: {calls}')

# Find the actual question/answer data  
# Look for the loc1, loc2, loc3 values
locs = re.findall(r'loc[123]["\s:=]+["\']([^"\']+)["\']', js)
print(f'\nloc1/2/3 values: {locs}')

# Find break-handi key construction
idx2 = js.find('break-handi')
segment = js[max(0,idx2-500):idx2+300]
# Save to file to avoid encoding issues
with open('chakra_segment.txt', 'w', encoding='utf-8') as f:
    f.write(segment)
print('\nSaved break-handi segment to chakra_segment.txt')

# Find extract-flag / flag reveal
idx3 = js.find('extract')
segment3 = js[max(0,idx3-200):idx3+500]
with open('chakra_extract.txt', 'w', encoding='utf-8') as f:
    f.write(segment3)
print('Saved extract segment to chakra_extract.txt')

# Now try the API endpoints with session
# First get a fresh session state
print('\n[*] Getting state...')
r = s.get(f'{base}/api/state', timeout=10)
print(f'State: {r.text}')

# Try verify-clue with ALL possible IDs and answers
# From game: Q1=vrindavan/gokul, Q2=makhan/butter, Q3=flute/bansuri
print('\n[*] Brute-forcing clue answers...')

q1_answers = ['vrindavan', 'Vrindavan', 'VRINDAVAN', 'gokul', 'Gokul', 'GOKUL',
              'mathura', 'Mathura', 'govardhan', 'Govardhan', 'dwarka', 'Dwarka']
q2_answers = ['makhan', 'Makhan', 'MAKHAN', 'butter', 'Butter', 'BUTTER', 
              'dahi', 'Dahi', 'milk', 'Milk', 'mishri', 'Mishri']
q3_answers = ['flute', 'Flute', 'FLUTE', 'bansuri', 'Bansuri', 'BANSURI',
              'murali', 'Murali', 'MURALI', 'venu', 'Venu']

clue_ids_to_try = ['clue1', 'clue2', 'clue3', 'vrindavan', 'makhan', 'temple',
                   'gokul_1', 'makhan_1', 'temple_1', 'q1', 'q2', 'q3',
                   'stage1', 'stage2', 'stage3', 'step1', 'step2', 'step3']

# Try each combo
found_clues = {}
for clue_id in clue_ids_to_try:
    for answer in q1_answers + q2_answers + q3_answers:
        r = s.post(f'{base}/api/verify-clue', 
                   json={'clueId': clue_id, 'answer': answer}, timeout=10)
        if r.status_code == 200:
            data = r.json() if r.headers.get('content-type','').startswith('application/json') else {}
            if data.get('success') or data.get('correct') or 'true' in r.text.lower()[:50]:
                print(f'[+] CORRECT! clueId={clue_id} answer={answer} -> {r.text[:200]}')
                found_clues[clue_id] = answer
                break
        elif r.status_code not in [404, 400]:
            print(f'  clueId={clue_id} -> {r.status_code}: {r.text[:100]}')
            break

print(f'\nFound clues: {found_clues}')
