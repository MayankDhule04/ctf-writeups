#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests, re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

base = 'https://gokul-hidden-makhan.vercel.app'

with open('chakra_bundle.js', encoding='utf-8') as f:
    js = f.read()

# Find Hd() - the session ID function
idx = js.find('function Hd(')
if idx == -1:
    idx = js.find('Hd=')
print(f'Hd() context: {js[max(0,idx-50):idx+300]}')

# The session ID is sent as x-session-id header - find what value it uses
# Look for sessionId, seeker-welcome-player
for kw in ['seeker-welcome', 'x-session-id', 'sessionId', 'session_id']:
    idx2 = js.find(kw)
    if idx2 != -1:
        print(f'\n{kw} context: {js[max(0,idx2-100):idx2+200]}')

# Find the actual answers - look for the answer validation on backend
# Or in the JS - the correct answers should be there
# Q1: Krishna's mother = Yashoda / Devaki
# Q2: Favorite food = Makhan / Butter
# Q3: Divine instrument = Flute / Bansuri

# Save all string literals to a file to search through
all_strings = re.findall(r'"([^"]{3,50})"', js)
with open('chakra_strings.txt', 'w', encoding='utf-8') as f:
    for s in set(all_strings):
        f.write(s + '\n')
print(f'\nSaved {len(set(all_strings))} unique strings to chakra_strings.txt')

# Now try the API with session ID from the state response
s = requests.Session()
headers = {
    'Content-Type': 'application/json',
    'Origin': base,
    'Referer': base + '/',
    'x-session-id': 'seeker-welcome-player'
}

# Q1: Krishna's mother
q1_answers = ['Yashoda', 'yashoda', 'YASHODA', 'Devaki', 'devaki', 'DEVAKI',
              'yashodha', 'Yashodha', 'mata yashoda', 'Mata Yashoda']
# Q2: Favorite food  
q2_answers = ['Makhan', 'makhan', 'MAKHAN', 'Butter', 'butter', 'makkhan', 'Makkhan',
              'dahi makhan', 'Dahi Makhan']
# Q3: Divine instrument
q3_answers = ['Flute', 'flute', 'Bansuri', 'bansuri', 'BANSURI', 'FLUTE',
              'Murali', 'murali', 'venu', 'Venu']

print('\n[*] Testing Q1 (Krishna mother) with step1...')
for ans in q1_answers:
    r = requests.post(f'{base}/api/verify-clue',
                     json={'clueId': 'step1', 'answer': ans},
                     headers=headers, timeout=10)
    result = r.json() if r.headers.get('content-type','').startswith('application/json') else {'raw': r.text}
    if result.get('success') or result.get('correct'):
        print(f'[+] Q1 CORRECT: {ans} -> {result}')
        break
    else:
        print(f'  step1/{ans}: {result}')

print('\n[*] Testing Q2 (favorite food) with step2...')
for ans in q2_answers:
    r = requests.post(f'{base}/api/verify-clue',
                     json={'clueId': 'step2', 'answer': ans},
                     headers=headers, timeout=10)
    result = r.json() if r.headers.get('content-type','').startswith('application/json') else {'raw': r.text}
    if result.get('success') or result.get('correct'):
        print(f'[+] Q2 CORRECT: {ans} -> {result}')
        break
    else:
        print(f'  step2/{ans}: {result}')

print('\n[*] Testing Q3 (instrument) with step3...')
for ans in q3_answers:
    r = requests.post(f'{base}/api/verify-clue',
                     json={'clueId': 'step3', 'answer': ans},
                     headers=headers, timeout=10)
    result = r.json() if r.headers.get('content-type','').startswith('application/json') else {'raw': r.text}
    if result.get('success') or result.get('correct'):
        print(f'[+] Q3 CORRECT: {ans} -> {result}')
        break
    else:
        print(f'  step3/{ans}: {result}')
