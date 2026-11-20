import re
js = open(r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf\tsr_fresh.js","r",encoding="utf-8",errors="replace").read()

# every supabase query chain context
for kw in ['from("chapter_content")','from("chapters")','from("chapter_access")','from("whitelisted_emails")','from("user_roles")','storage','chapter-files','getPublicUrl','createSignedUrl','download(']:
    for m in re.finditer(re.escape(kw), js):
        i=m.start()
        seg = js[max(0,i-120):i+260].replace("\n"," ")
        print(f"[{kw}] ...{seg}...")
        break  # first occurrence each
print("\n==== all .from( / .eq( chains near chapter_content ====")
for m in re.finditer(r'chapter_content', js):
    i=m.start(); print(js[max(0,i-60):i+200].replace("\n"," ")); print("--")
