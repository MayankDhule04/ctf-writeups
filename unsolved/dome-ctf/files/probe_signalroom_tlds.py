import urllib.request, urllib.error, ssl, re, socket

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

names = []
for base in ["signalroom","thesignalroom","signal-room","the-signal-room","signalrooms","sigroom","signalroomctf","signal_room"]:
    for tld in [".in",".com",".net",".org",".xyz",".app",".site",".live",".space",".online",".club",".dev",".io",".me",".co",".sh",".link",".fun",".cc"]:
        names.append(base+tld)

def probe(host):
    try:
        socket.gethostbyname(host)
    except Exception:
        return None  # no DNS
    for scheme in ("https://","http://"):
        url = scheme+host+"/"
        try:
            req=urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
            r=urllib.request.urlopen(req,timeout=10,context=ctx)
            body=r.read(4000).decode("utf-8","replace")
            title=re.search(r'<title[^>]*>(.*?)</title>', body, re.I|re.S)
            title=title.group(1).strip()[:70] if title else ""
            login = bool(re.search(r'type=["\']password|login|sign in|signin|log in|authenticate', body, re.I))
            return (url, r.status, title, login, len(body))
        except urllib.error.HTTPError as ex:
            return (url, ex.code, "(httperror)", False, 0)
        except Exception as ex:
            continue
    return (host, "DNS-only/again", "", False, 0)

for h in names:
    res = probe(h)
    if res:
        print(f"{h:28} -> {res}")
