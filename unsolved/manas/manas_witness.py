#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests, re, time, sys
sys.stdout.reconfigure(encoding='utf-8')

base = 'https://manas-yantra-ctf1.onrender.com'

def chat(msg, sid=None, delay=4):
    payload = {'message': msg}
    if sid:
        payload['session_id'] = sid
    r = requests.post(base + '/chat', json=payload, timeout=30)
    data = r.json()
    resp = data.get('response', '')
    sid = data.get('session_id', sid)
    flags = re.findall(r'CHAKRA\{[^}]+\}', resp)
    if flags and 'N0TH1NG' not in str(flags):
        print(f'\n*** REAL FLAG: {flags} ***')
    time.sleep(delay)
    return resp, sid

# The KEY question from K5: "Something witnesses the bliss. What is that witness?"
# This is the actual question I need to answer!

print('[*] Answering the guardian\'s question about the witness...')
resp, sid = chat('')  # Get welcome
time.sleep(3)
print(f'Welcome (trimmed): {resp[:50]}')

# Navigate all 5 koshas
for k in ['Annamaya', 'Pranamaya', 'Manomaya', 'Vijnanamaya']:
    resp, sid = chat(k, sid, delay=4)
    print(f'{k}: {resp[:80]}')

# K5 - get the full question
resp, sid = chat('Anandamaya', sid, delay=4)
print(f'\nK5 FULL RESPONSE:')
print(resp)

# Now answer the question: "What is that witness?"
print('\n[*] Answering: What is the witness?')
witness_answers = [
    'The witness is Atman',
    'Atman is the witness',
    'The witness is Brahman',
    'The witness is pure consciousness',
    'The witness is the Self',
    'The witness is Turiya',
    'I am the witness - the eternal Atman',
    'Pure Awareness is the witness',
    'Consciousness (Chit) is the witness',
    'The witness is Sat-Chit-Ananda',
    'The Atman witnesses all. Atman is Brahman. Aham Brahmasmi.',
    'The witness is the pure Self, Atman, which is Brahman',
]

for answer in witness_answers:
    resp, sid = chat(answer, sid, delay=4)
    full_resp = resp
    print(f'\n[{answer[:50]}]')
    print(f'Response: {full_resp[:300]}')
    flags = re.findall(r'CHAKRA\{[^}]+\}', full_resp)
    if flags and 'N0TH1NG' not in str(flags):
        print(f'*** REAL FLAG: {flags} ***')
        break
    # Check if we got a new question to answer
    if '?' in full_resp and 'CHAKRA' not in full_resp and 'Patience' not in full_resp:
        print(f'  [NEW QUESTION DETECTED]')
