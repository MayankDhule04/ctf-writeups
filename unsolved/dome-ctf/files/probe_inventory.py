import urllib.request, urllib.error, ssl, socket

ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
hosts=["inventory.domectf.in","api.domectf.in","archive.domectf.in","inventory-api.domectf.in",
       "data.domectf.in","vault.domectf.in","internal.domectf.in","gateway.domectf.in",
       "thesignalroom.org"]
paths=["/api/v3/inventory","/"]
for h in hosts:
    try: socket.gethostbyname(h)
    except Exception as e:
        print(f"{h:30} NO-DNS"); continue
    for p in paths:
        url=f"https://{h}{p}"
        try:
            r=urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=10,context=ctx)
            print(f"{h:30}{p:22} {r.status} {r.headers.get('Content-Type','')[:30]}")
        except urllib.error.HTTPError as e:
            print(f"{h:30}{p:22} {e.code} {e.headers.get('Content-Type','')[:30]}")
        except Exception as e:
            print(f"{h:30}{p:22} ERR {str(e)[:40]}")
