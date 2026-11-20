import urllib.request, urllib.error, ssl

base = "https://www.signalroom.in"
eps = ["/api/render","/api/export","/api/document","/api/documents","/api/pdf",
       "/api/generate","/api/share","/api/shared","/api/artifact","/api/artifacts",
       "/api/cache","/api/9f34f9","/api/export/9f34f9","/api/render/9173",
       "/render","/export","/share","/document","/documents","/private/render",
       "/api/view","/api/download","/api/file","/api/files","/api/report","/api/reports",
       "/api/worker","/api/jobs","/api/job"]
ctx = ssl.create_default_context()
for e in eps:
    url = base + e
    req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
    try:
        r = urllib.request.urlopen(req, timeout=15, context=ctx)
        body = r.read(160).decode("utf-8","replace").replace("\n"," ")
        print(f"{e:26} {r.status} {r.headers.get('Content-Type','')[:30]:30} {body[:80]}")
    except urllib.error.HTTPError as ex:
        body = ex.read(160).decode("utf-8","replace").replace("\n"," ")
        print(f"{e:26} {ex.code} {ex.headers.get('Content-Type','')[:30]:30} {body[:80]}")
    except Exception as ex:
        print(f"{e:26} ERR {ex}")
