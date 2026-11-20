import urllib.request, urllib.error, ssl, json, time

BASE="https://iuqrarlmvuydxhiygkro.supabase.co"
ANON="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml1cXJhcmxtdnV5ZHhoaXlna3JvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAzODI2NzUsImV4cCI6MjA4NTk1ODY3NX0.DCWPItRMC2aekqWjFoTGoROzzmR_q2uy2NjJK-nAxLg"
ctx=ssl.create_default_context()
def req(method, path, body=None):
    r=urllib.request.Request(f"{BASE}{path}", data=(json.dumps(body).encode() if body is not None else None), method=method,
        headers={"apikey":ANON,"Authorization":f"Bearer {ANON}","Content-Type":"application/json","Accept":"application/json"})
    try:
        resp=urllib.request.urlopen(r,timeout=25,context=ctx); return resp.status, resp.read().decode("utf-8","replace")
    except urllib.error.HTTPError as e: return e.code, e.read().decode("utf-8","replace")
    except Exception as e: return "ERR", str(e)

EMAIL="daniele@thesignalroom.org"
print("1) request OTP for", EMAIL)
s,o=req("POST","/functions/v1/custom-otp",{"email":EMAIL}); print("   custom-otp ->", s, o[:300])

time.sleep(1)
print("2) read otp_codes (anon):")
s,o=req("GET","/rest/v1/otp_codes?select=*&order=created_at.desc"); print("   otp_codes ->", s, o[:1500])
