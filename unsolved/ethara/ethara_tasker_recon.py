#!/usr/bin/env python3
"""
Ethara Tasker - Web Application Testing
https://task.ethara.ai/tasker
"""

import requests
from bs4 import BeautifulSoup
import re

URL = "https://task.ethara.ai/tasker"

print("[*] Ethara Tasker - Reconnaissance")
print(f"[*] Target: {URL}")
print()

# Fetch the page
print("[*] Fetching page...")
try:
    resp = requests.get(URL, timeout=10)
    print(f"[+] Status: {resp.status_code}")
    print(f"[+] Content-Length: {len(resp.text)}")
    print()
except Exception as e:
    print(f"[-] Error: {e}")
    exit(1)

# Check for flags
print("[*] Searching for flags...")
flags = re.findall(r'(CIT|FLAG|flag|CTF)\{[^}]+\}', resp.text, re.IGNORECASE)
if flags:
    print(f"[+] FOUND FLAGS: {flags}")
else:
    print("[-] No obvious flags found")

print()

# Parse HTML
soup = BeautifulSoup(resp.text, 'html.parser')

# Page title
title = soup.find('title')
if title:
    print(f"[*] Page Title: {title.get_text()}")

# Check for forms
print("\n[*] Forms found:")
forms = soup.find_all('form')
for i, form in enumerate(forms, 1):
    print(f"\n  Form {i}:")
    print(f"    Action: {form.get('action')}")
    print(f"    Method: {form.get('method')}")
    print(f"    Fields:")
    for input_field in form.find_all(['input', 'textarea', 'select']):
        print(f"      - {input_field.get('name')}: {input_field.get('type')}")

# Check for JavaScript files
print("\n[*] JavaScript files:")
for script in soup.find_all('script'):
    src = script.get('src')
    if src:
        print(f"    {src}")

# Check for API endpoints in JavaScript
print("\n[*] Looking for API endpoints in JavaScript...")
for script in soup.find_all('script'):
    if script.string:
        # Look for API URLs
        api_matches = re.findall(r'["\']/(api|endpoint|task|submit)[^"\']*["\']', script.string)
        if api_matches:
            print(f"    Found: {api_matches}")

# Check for comments
print("\n[*] HTML Comments:")
comments = soup.find_all(string=lambda text: isinstance(text, str) and '<!--' in str(text))
for comment in comments[:5]:
    print(f"    {comment[:200]}")

# Check response headers
print("\n[*] Response Headers:")
for header, value in resp.headers.items():
    print(f"    {header}: {value}")

# Print visible text
print("\n[*] Visible text on page:")
text = soup.get_text()
print(text[:1000])

print("\n" + "="*80)
print("[*] Full HTML (first 5000 chars):")
print("="*80)
print(resp.text[:5000])
