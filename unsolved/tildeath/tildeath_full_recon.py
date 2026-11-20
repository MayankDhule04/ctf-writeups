#!/usr/bin/env python3
import requests, re, json

base = 'http://54.210.184.191:8081'
s = requests.Session()

# Get full raw main page
r = s.get(base + '/', timeout=15)
html = r.text

# Print the full main page, specifically looking for submission UI
# Find sections about submitting / mourners
idx = html.find('mourner')
if idx != -1:
    print('mourner section:', html[max(0,idx-200):idx+500])
print()

# Also look for "eulogy" section
idx2 = html.find('ulogy')  
if idx2 != -1:
    print('eulogy section:', html[max(0,idx2-200):idx2+500])
print()

# Look for "leave" section  
idx3 = html.find('leave')
if idx3 != -1:
    print('leave section:', html[max(0,idx3-200):idx3+500])

# Also try a wider word search
for word in ['POST', 'submit', 'send', 'write', 'add', 'post']:
    idx = html.lower().find(word)
    if idx != -1:
        context = html[max(0,idx-50):idx+100]
        if '<' in context or '/' in context:
            print(f'Found {word!r}: {context!r}')

# Now try ALL possible paths with fuzzing
print('\n[*] Fuzzing all paths...')
words = ['mourn', 'eulogy', 'eulogies', 'farewell', 'farewell-add', 
         'remember', 'tribute', 'candle', 'leave', 'write', 'post',
         'grief', 'memorial/add', 'memorial/submit', 'memorial/new',
         'chapel', 'priest/write', 'priest/eulogy', 'priest/farewell',
         'new', 'create', 'upload']

for word in words:
    for method in ['GET', 'POST']:
        try:
            if method == 'GET':
                r2 = s.get(f'{base}/{word}', timeout=5)
            else:
                r2 = s.post(f'{base}/{word}', json={'msg': 'test'}, timeout=5)
            if r2.status_code not in [404, 405]:
                print(f'  {method} /{word}: {r2.status_code} -> {r2.text[:100]}')
        except:
            pass
