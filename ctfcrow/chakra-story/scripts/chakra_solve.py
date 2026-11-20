#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json

base = 'https://gokul-hidden-makhan.vercel.app'
s = requests.Session()
s.headers.update({'Content-Type': 'application/json', 'Origin': base, 'Referer': base + '/'})

# From JS: 3 questions
# Q1: ??? (loc1) - probably Vrindavan or Gokul
# Q2: What is Lord Krishna's favorite food? -> Makhan (butter)
# Q3: Which divine instrument does Lord Krishna play? -> Flute / Bansuri

# First check the /state endpoint
print('[*] Checking /state...')
r = s.get(base + '/state', timeout=10)
print(f'  Status: {r.status_code}, Body: {r.text[:300]}')

# Try /api/state too
r2 = s.get(base + '/api/state', timeout=10)
print(f'  /api/state: {r2.status_code}, Body: {r2.text[:300]}')

# Try to call /extract directly to get the flag
print('\n[*] Trying /extract directly...')
r3 = s.post(base + '/extract', json={}, timeout=10)
print(f'  Status: {r3.status_code}, Body: {r3.text[:500]}')

r4 = s.post(base + '/api/extract', json={}, timeout=10)
print(f'  /api/extract: {r4.status_code}, Body: {r4.text[:500]}')

# Try /break-handi with guessed keys
print('\n[*] Trying /break-handi...')
for key in ['makhan', 'MAKHAN', 'butter', 'flute', 'krishna', 'radha', 'vrindavan', 'gokul',
            'bansuri', 'Makhan', 'Flute', 'Bansuri', 'Krishna', 'Radha']:
    r = s.post(base + '/break-handi', json={'key': key}, timeout=10)
    if r.status_code == 200 and 'CHAKRA' in r.text:
        print(f'  KEY={key} -> FLAG: {r.text}')
        break
    elif r.status_code == 200 and len(r.text) > 10:
        print(f'  KEY={key} -> {r.text[:200]}')

# Try verify-clue with Q1 answers
print('\n[*] Verifying clues...')
# Q1: from JS - what is loc1/Q1? Let's guess it's about Gokul/Vrindavan
clue_answers = [
    ('clue1', 'Vrindavan'), ('clue1', 'vrindavan'), ('clue1', 'Gokul'), ('clue1', 'gokul'),
    ('clue1', 'Mathura'), ('clue1', 'mathura'), ('clue1', 'Govardhan'), ('clue1', 'govardhan'),
    ('makhan', 'Butter'), ('makhan', 'butter'), ('makhan', 'Makhan'), ('makhan', 'makhan'),
    ('temple', 'Flute'), ('temple', 'flute'), ('temple', 'Bansuri'), ('temple', 'bansuri'),
]
for clue_id, answer in clue_answers:
    r = s.post(base + '/verify-clue', json={'clueId': clue_id, 'answer': answer}, timeout=10)
    if r.status_code == 200:
        data = r.text
        if 'true' in data.lower() or 'correct' in data.lower() or 'success' in data.lower():
            print(f'  [+] clueId={clue_id} answer={answer} -> {data[:200]}')
        elif r.status_code != 404:
            print(f'  clueId={clue_id} answer={answer} -> {data[:100]}')
