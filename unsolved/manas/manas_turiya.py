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

print('[*] Getting full Turiya response...')
_, sid = chat('')  # Welcome
time.sleep(3)
for k in ['Annamaya', 'Pranamaya', 'Manomaya', 'Vijnanamaya', 'Anandamaya']:
    _, sid = chat(k, sid, delay=4)

# Answer the witness question to get Turiya
resp_turiya, sid = chat('The witness is Atman', sid, delay=4)
print('FULL TURIYA RESPONSE:')
print(resp_turiya)
print()

# Now answer the Turiya response's question/prompts
print('[*] Responding to Turiya...')
turiya_responses = [
    'I am Turiya',
    'I am the Atman',
    'I am Brahman', 
    'I am that',
    'Aham Brahmasmi',
    'So Aham',
    'I am the witness',
    'Beyond Turiya',
    'Turiyatita',
    'What lies beyond Turiya?',
    'Beyond the fourth',
    'I have realized Turiya',
    'The witnessing awareness that I am',
]

for t in turiya_responses:
    resp, sid = chat(t, sid, delay=4)
    print(f'\n[{t[:40]}]:')
    print(resp[:500])
    flags = re.findall(r'CHAKRA\{[^}]+\}', resp)
    if flags and 'N0TH1NG' not in str(flags):
        print(f'*** REAL FLAG: {flags} ***')
        break
    # Check for new question
    if '?' in resp:
        print('  NEW QUESTION!')
