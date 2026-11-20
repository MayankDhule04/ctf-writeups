#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests, sys, time
sys.stdout.reconfigure(encoding='utf-8')

base = 'https://gokul-hidden-makhan.vercel.app'

# Use a fresh unique session ID
import random, string
session_id = 'gokul_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=7))
print(f'[*] Using session: {session_id}')

headers = {
    'Content-Type': 'application/json',
    'Origin': base,
    'Referer': base + '/',
    'x-session-id': session_id
}

def api(endpoint, method='GET', data=None):
    if method == 'GET':
        r = requests.get(f'{base}/api{endpoint}', headers=headers, timeout=10)
    else:
        r = requests.post(f'{base}/api{endpoint}', json=data, headers=headers, timeout=10)
    return r.json()

# Step 1: Yashoda
print('[*] Step 1: Yashoda')
r = api('/verify-clue', 'POST', {'clueId': 'step1', 'answer': 'Yashoda'})
print(f'  -> {r.get("message")} | step1={r.get("state",{}).get("cluesCompleted",{}).get("step1")}')

# Step 2: Makhan
print('[*] Step 2: Makhan')
r = api('/verify-clue', 'POST', {'clueId': 'step2', 'answer': 'Makhan'})
print(f'  -> {r.get("message")} | step2={r.get("state",{}).get("cluesCompleted",{}).get("step2")}')

# Step 3: try all flute variants
print('[*] Step 3: brute forcing...')
q3_answers = ['Flute', 'flute', 'FLUTE', 'Bansuri', 'bansuri', 'BANSURI',
              'Murali', 'murali', 'Venu', 'venu', 'Basuri', 'basuri',
              'flute', 'Bansi', 'bansi', 'Pipa', 'pipa']

for ans in q3_answers:
    # Check if we need to redo steps 1&2
    state = api('/state')
    completed = state.get('state', {}).get('cluesCompleted', {})
    
    if not completed.get('step1'):
        print('  [re-doing step1]')
        api('/verify-clue', 'POST', {'clueId': 'step1', 'answer': 'Yashoda'})
    if not completed.get('step2'):
        print('  [re-doing step2]')
        api('/verify-clue', 'POST', {'clueId': 'step2', 'answer': 'Makhan'})
    
    r = api('/verify-clue', 'POST', {'clueId': 'step3', 'answer': ans})
    msg = r.get('message', '')
    print(f'  step3/{ans}: {msg}')
    
    if r.get('success') and r.get('state', {}).get('cluesCompleted', {}).get('step3'):
        print(f'[+] Q3 CORRECT: {ans}')
        print(f'    State: {r.get("state")}')
        
        # Now break the handi
        print('\n[*] Breaking Handi...')
        # Find key - likely combination of answers
        for key in [f'Yashoda_Makhan_{ans}', f'yashoda_makhan_{ans.lower()}',
                    'Yashoda+Makhan+'+ans, ans, 'makhan', 'Makhan',
                    'YashodaMakhan'+ans, f'{ans}_makhan_yashoda']:
            handi_r = api('/break-handi', 'POST', {'key': key})
            print(f'  key={key}: {handi_r}')
            if handi_r.get('success') or 'CHAKRA' in str(handi_r):
                print(f'[+] HANDI BROKEN! {handi_r}')
                # Extract flag
                flag_r = api('/extract', 'POST', {})
                print(f'[+] FLAG: {flag_r}')
                break
        break
    elif 'Complete' in msg or 'reset' in msg.lower():
        # Session got reset, redo
        continue

# Try breaking handi anyway
print('\n[*] Trying extract regardless...')
r_ext = api('/extract', 'POST', {})
print(f'Extract: {r_ext}')

# Try break-handi with all guesses
state = api('/state')
print(f'Final state: {state}')
