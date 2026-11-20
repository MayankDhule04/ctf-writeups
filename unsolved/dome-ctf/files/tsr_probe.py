import urllib.request, urllib.error, ssl, re

base="https://thesignalroom.org"
ctx=ssl.create_default_context()
paths=[
 "/robots.txt","/sitemap.xml","/favicon.png",
 "/login","/signin","/sign-in","/members","/member","/dashboard","/feed",
 "/chapters","/chapter","/admin","/profile","/app","/community","/posts",
 "/directory","/salon","/lounge","/join","/apply","/request-access","/gate","/me",
 "/api","/api/health","/api/me","/api/user","/api/users","/api/posts","/api/members",
 "/api/login","/api/auth","/api/session","/api/chapters","/api/leads","/api/config",
 "/~api","/~api/analytics","/rest/v1/","/auth/v1/health","/.env","/config.json",
]
def g(p, method="GET"):
    url=base+p
    req=urllib.request.Request(url, method=method, headers={"User-Agent":"Mozilla/5.0","Accept":"application/json,*/*"})
    try:
        r=urllib.request.urlopen(req,timeout=12,context=ctx)
        b=r.read(300).decode("utf-8","replace").replace("\n"," ")
        return r.status, r.headers.get("Content-Type",""), b
    except urllib.error.HTTPError as e:
        b=e.read(300).decode("utf-8","replace").replace("\n"," ")
        return e.code, e.headers.get("Content-Type",""), b
    except Exception as e:
        return "ERR", "", str(e)[:60]

for p in paths:
    s,ct,b=g(p)
    tag = "JSON" if "json" in ct else ("HTML" if "html" in ct else ct[:20])
    print(f"{p:22} {s} {tag:14} {b[:90]}")
