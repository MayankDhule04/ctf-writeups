import urllib.request, ssl, os
ctx = ssl.create_default_context()
d = r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf"
imgs = {
 "masto_avatar.png":"https://files.mastodon.social/accounts/avatars/117/386/728/458/611/438/original/8d41518ae1448b7f.png",
 "masto_header.png":"https://files.mastodon.social/accounts/headers/117/386/728/458/611/438/original/4ed7be3fc54afa5a.png",
}
for fn,url in imgs.items():
    req=urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
    data=urllib.request.urlopen(req,timeout=30,context=ctx).read()
    open(os.path.join(d,fn),"wb").write(data)
    # quick strings scan for urls/text
    import re
    txt=data.decode("latin1","replace")
    hits=sorted(set(re.findall(r'(?:https?://|www\.)[^\s"\'<>)]{4,100}|[A-Za-z0-9_.-]+\{[^}]{3,60}\}|signalroom[^\s]*|[a-z0-9-]+\.(?:in|com|net|onion|xyz|app|link)\b', txt, re.I)))
    print(fn, len(data), "bytes; string hits:", hits[:20])
