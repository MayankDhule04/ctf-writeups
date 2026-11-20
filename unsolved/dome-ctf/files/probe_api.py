import urllib.request, urllib.error, ssl

base = "https://www.signalroom.in"
eps = ["/api/quiz","/api/contact","/api/enquiry","/api/ebook","/api/careers",
       "/api/admin","/api/private","/api/submissions","/api/leads","/api/messages",
       "/api/login","/api/auth","/api/members","/api/posts","/api/threads",
       "/api/users","/api/signal","/api/health","/api/status","/api/config",
       "/api","/api/contact?id=1","/api/admin/login"]

ctx = ssl.create_default_context()
for e in eps:
    url = base + e
    for method in ("GET",):
        req = urllib.request.Request(url, method=method, headers={"User-Agent":"Mozilla/5.0"})
        try:
            r = urllib.request.urlopen(req, timeout=15, context=ctx)
            body = r.read(200).decode("utf-8","replace").replace("\n"," ")
            print(f"{method} {e:28} {r.status}  {dict(r.headers).get('Content-Type','')}  {body[:100]}")
        except urllib.error.HTTPError as ex:
            body = ex.read(200).decode("utf-8","replace").replace("\n"," ")
            print(f"{method} {e:28} {ex.code}  {ex.headers.get('Content-Type','')}  {body[:100]}")
        except Exception as ex:
            print(f"{method} {e:28} ERR {ex}")
