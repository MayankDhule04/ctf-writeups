#!/usr/bin/env python3
"""
Hit Your Limit - Web Challenge
URL: http://23.179.17.92:5559
Hint: "Don't go above your limit" - likely rate limiting or integer overflow
"""

import requests
import re

url = "http://23.179.17.92:5559"

print("="*70)
print("HIT YOUR LIMIT - RECONNAISSANCE")
print("="*70)
print(f"URL: {url}")

# Initial request
print("\n[*] Making initial request...")
try:
    r = requests.get(url, timeout=10)
    print(f"    Status: {r.status_code}")
    print(f"    Headers:")
    for key, value in r.headers.items():
        print(f"      {key}: {value}")
    
    print(f"\n[*] Response body:")
    print(r.text[:1000])
    
    # Look for flag
    if 'CIT{' in r.text:
        flags = re.findall(r'CIT\{[^}]+\}', r.text)
        print(f"\n[!!!] FLAG FOUND: {flags}")
    
    # Check for forms
    if '<form' in r.text.lower():
        print("\n[*] Form detected in page")
        forms = re.findall(r'<form[^>]*>.*?</form>', r.text, re.DOTALL | re.IGNORECASE)
        for i, form in enumerate(forms):
            print(f"\n    Form {i+1}:")
            print(f"    {form[:200]}")
    
    # Check for input fields
    inputs = re.findall(r'<input[^>]*>', r.text, re.IGNORECASE)
    if inputs:
        print(f"\n[*] Input fields found: {len(inputs)}")
        for inp in inputs[:5]:
            print(f"    {inp}")
    
    # Check for JavaScript
    if '<script' in r.text.lower():
        print("\n[*] JavaScript detected")
        scripts = re.findall(r'<script[^>]*>(.*?)</script>', r.text, re.DOTALL | re.IGNORECASE)
        for i, script in enumerate(scripts[:3]):
            if script.strip():
                print(f"\n    Script {i+1}:")
                print(f"    {script[:300]}")
    
    # Check for comments
    comments = re.findall(r'<!--(.*?)-->', r.text, re.DOTALL)
    if comments:
        print(f"\n[*] HTML comments found:")
        for comment in comments:
            print(f"    {comment.strip()}")
    
except Exception as e:
    print(f"[!] Error: {e}")

# Check common endpoints
print("\n[*] Checking common endpoints...")
endpoints = [
    '/flag', '/admin', '/api', '/robots.txt', '/.git', 
    '/source', '/debug', '/test', '/config'
]

for endpoint in endpoints:
    try:
        r = requests.get(url + endpoint, timeout=5)
        if r.status_code != 404:
            print(f"    {endpoint}: {r.status_code}")
            if 'CIT{' in r.text:
                print(f"      [!!!] FLAG FOUND!")
    except:
        pass

print("\n" + "="*70)
