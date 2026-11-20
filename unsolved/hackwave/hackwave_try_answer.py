import requests
import json
import sys

backend_url = "https://hackwave-ctf-backend.onrender.com/api"

if len(sys.argv) < 2:
    print("Usage: python hackwave_try_answer.py <answer>")
    sys.exit(1)

answer = sys.argv[1]

print(f"[*] Trying answer: {answer}")

session = requests.Session()

# Initialize
r = session.get(f"{backend_url}/init")
session_token = r.headers.get('x-session-token')

# Submit
headers = {
    'Content-Type': 'application/json',
    'x-session-token': session_token
}

payload = {
    'stage': 1,
    'answer': answer
}

r = session.post(f"{backend_url}/verify", headers=headers, json=payload)

print(f"Status: {r.status_code}")
print(f"Response: {r.text}")

if r.status_code == 200:
    data = r.json()
    if data.get('verified'):
        print("\n[+] SUCCESS! Correct answer!")
    else:
        print("\n[-] Incorrect")
