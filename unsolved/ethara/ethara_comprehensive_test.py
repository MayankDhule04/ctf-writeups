#!/usr/bin/env python3
"""
Ethara Tasker - Comprehensive Security Testing
"""

import requests
import json

BASE_URL = "https://task.ethara.ai"

print("[*] Ethara Tasker - Comprehensive Security Test")
print(f"[*] Base URL: {BASE_URL}")
print()

# Test 1: Check for exposed API endpoints
print("[*] Testing API endpoints...")
endpoints = [
    "/api/auth/login",
    "/api/auth/register",
    "/api/auth/forgot-password",
    "/api/tasks",
    "/api/flags",
    "/api/users",
    "/api/projects",
    "/api/admin",
    "/api/me",
]

for endpoint in endpoints:
    try:
        resp = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
        print(f"  {endpoint}: {resp.status_code}")
        if resp.status_code == 200:
            print(f"    Content: {resp.text[:200]}")
    except Exception as e:
        print(f"  {endpoint}: Error - {e}")

# Test 2: Try to register
print("\n[*] Testing registration...")
try:
    resp = requests.post(f"{BASE_URL}/api/auth/register", json={
        "email": "test@test.com",
        "password": "Test123!",
        "name": "Test User"
    }, timeout=5)
    print(f"  Status: {resp.status_code}")
    print(f"  Response: {resp.text[:500]}")
except Exception as e:
    print(f"  Error: {e}")

# Test 3: Check for flags endpoint
print("\n[*] Testing flags endpoint...")
try:
    resp = requests.get(f"{BASE_URL}/api/flags", timeout=5)
    print(f"  Status: {resp.status_code}")
    if resp.status_code == 200:
        print(f"  Response: {resp.text}")
except Exception as e:
    print(f"  Error: {e}")

# Test 4: Check robots.txt
print("\n[*] Checking robots.txt...")
try:
    resp = requests.get(f"{BASE_URL}/robots.txt", timeout=5)
    print(f"  Status: {resp.status_code}")
    if resp.status_code == 200:
        print(f"  Content:\n{resp.text}")
except Exception as e:
    print(f"  Error: {e}")

# Test 5: Check for common files
print("\n[*] Checking common files...")
common_files = [
    "/.env",
    "/.git/config",
    "/config.json",
    "/package.json",
    "/.well-known/security.txt",
]

for file in common_files:
    try:
        resp = requests.get(f"{BASE_URL}{file}", timeout=5)
        if resp.status_code == 200:
            print(f"  {file}: FOUND")
            print(f"    Content: {resp.text[:200]}")
    except:
        pass

print("\n[*] Testing complete!")
