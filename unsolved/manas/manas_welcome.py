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
    return data.get('response', ''), data.get('session_id', sid)

# Get the FULL welcome message
resp, sid = chat('')
print('FULL WELCOME:')
print(resp)
print()
print('SID:', sid)

# Also try asking directly about what's "beyond" the koshas
time.sleep(2)
resp2, sid2 = chat('What lies beyond the five sheaths?')
print('\nBEYOND question (fresh session):')
print(resp2)
