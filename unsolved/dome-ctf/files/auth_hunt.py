import re
f = r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf\signalroom_app.js"
js = open(f, "r", encoding="utf-8", errors="replace").read()

terms = ["localStorage","sessionStorage","isAuthenticat","isAdmin","isMember",
         "passcode","passphrase","password","secret","token","unlock","gate",
         "vault","portal","members","/member","/portal","/vault","/signal",
         "/admin","/private","/dashboard","/enter","access","authoriz","Unauthor",
         "atob(","btoa(","===\"","Bearer","x-","apiKey","api_key","invite","role"]

for t in terms:
    idx = 0
    hits = 0
    while True:
        i = js.find(t, idx)
        if i < 0: break
        hits += 1
        if hits <= 3:
            seg = js[max(0,i-80):i+120]
            print(f"[{t}] ...{seg}...")
        idx = i + 1
    if hits:
        print(f"   ^ {t}: {hits} total\n")
