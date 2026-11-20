#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests, re, json

base = 'https://gokul-hidden-makhan.vercel.app'

# First find all clue IDs and answers from JS
with open('chakra_bundle.js', encoding='utf-8') as f:
    js = f.read()

# Find verify-clue usage and clue IDs
idx = js.find('verify-clue')
print('[*] verify-clue context:')
print(js[max(0,idx-300):idx+500])
print('---')

# Find clueId references
clue_ids = re.findall(r'clueId["\s:=]+["\']([^"\']+)["\']', js)
print('[*] Clue IDs found:', clue_ids)

# Find the answer comparison logic
for kw in ['clue_1', 'clue_2', 'clue_3', 'clue1', 'clue2', 'clue3', 
           'vrindavan', 'makhan', 'bansuri', 'flute', 'butter',
           'answer', 'correct_answer', 'rightAnswer']:
    idx = js.lower().find(kw.lower())
    if idx != -1 and kw not in ['answer']:  # skip generic 'answer'
        print(f'\n[*] {kw!r} at {idx}:')
        print(js[max(0,idx-100):idx+200])

# Find the /api/ prefix usage
idx2 = js.find('api/')
print(f'\n[*] api/ context at {idx2}:')
print(js[max(0,idx2-200):idx2+300])
