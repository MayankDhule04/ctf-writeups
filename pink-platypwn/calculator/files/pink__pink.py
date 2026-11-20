import lib_pink as pinkctf
e = pinkctf.get("alphabet")
c = "62 22 28 12 31 0 43 3 25 5 35 5 3 20 48 26 24 10 5 26 60 46 29 60 35 48 5 20 5 59 60 46 25 10 5 46 50 5 48 57 5 50 10 59 5 23 35 24 23 43 24 35 25 46 60 61"
if c == "":
    c = input("Ciphertext: ")
f = ""
for n in c.split():
    f += e[int(n)]
print(f)