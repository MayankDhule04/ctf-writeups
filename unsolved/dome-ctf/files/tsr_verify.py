import re
js = open(r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf\tsr_fresh.js","r",encoding="utf-8",errors="replace").read()

for kw in ["verify-otp","admin-add-user"]:
    print(f"\n########## {kw} ##########")
    for m in re.finditer(re.escape(kw), js):
        i=m.start()
        print(js[max(0,i-600):i+900])
        print("--------")
