#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests, re, time, sys
sys.stdout.reconfigure(encoding='utf-8')

base = 'https://manas-yantra-ctf1.onrender.com'

def chat(msg, sid=None):
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
    return resp, sid

def koshas(sid=None):
    for k in ['Annamaya', 'Pranamaya', 'Manomaya', 'Vijnanamaya', 'Anandamaya']:
        _, sid = chat(k, sid)
        time.sleep(1)
    return sid

# The 4 Mahavakyas (great sayings) of the Upanishads:
# 1. Prajnanam Brahma (Aitareya Upanishad) - Consciousness is Brahman
# 2. Aham Brahmasmi (Brihadaranyaka Upanishad) - I am Brahman  
# 3. Tat tvam asi (Chandogya Upanishad) - That thou art
# 4. Ayam Atma Brahma (Mandukya Upanishad) - This Self is Brahman

# Maybe the trigger is ONE of these 4 Mahavakyas said after completing all 5 koshas
print('[*] Testing Mahavakyas after all 5 koshas...')
for mahavakya in [
    'Prajnanam Brahma',
    'Aham Brahmasmi',
    'Tat tvam asi',
    'Ayam Atma Brahma',
    'Prajnanam Brahma. Aham Brahmasmi. Tat tvam asi. Ayam Atma Brahma.',
    # Also try the specific realization statement
    'I have realized: Aham Brahmasmi',
    'I declare: Prajnanam Brahma',
    'The Mahavakya: Tat tvam asi',
    'Ayam Atma Brahma - This Self is Brahman',
]:
    sid = koshas()
    resp, sid = chat(mahavakya, sid)
    print(f'[{mahavakya[:40]}]: {resp[:200]}')
    time.sleep(2)

# The challenge says "walk the path of self-realization"
# In Vedanta, self-realization (Atma-jnana/Brahma-jnana) is achieved through:
# Shravana (hearing), Manana (reflection), Nididhyasana (meditation)

print('\n[*] Testing Shravana/Manana/Nididhyasana path...')
sid2 = koshas()
for step in [
    'I have performed Shravana - I have heard the teachings of the five koshas',
    'I have performed Manana - I have reflected on what I heard',
    'I have performed Nididhyasana - I have meditated on the truth',
    'Through Shravana, Manana, and Nididhyasana, I have achieved self-realization',
]:
    resp2, sid2 = chat(step, sid2)
    print(f'{step[:50]}: {resp2[:200]}')
    time.sleep(2)
