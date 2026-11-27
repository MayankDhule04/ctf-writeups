import socket, ssl

HOST='l-1d1390b81f3b4637-16326.cf959180.tb7.in'
PORT=443

def connect():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    s = socket.create_connection((HOST, PORT), timeout=10)
    ss = ctx.wrap_socket(s)
    ss.settimeout(6)
    return ss

def req(path, method='GET', extra_headers='', body=b''):
    ss = connect()
    r = f'{method} {path} HTTP/1.1\r\nHost: {HOST}\r\n{extra_headers}Connection: close\r\n'
    if body:
        r += f'Content-Length: {len(body)}\r\n'
    r += '\r\n'
    ss.sendall(r.encode() + body)
    data = b''
    try:
        while True:
            chunk = ss.recv(4096)
            if not chunk: break
            data += chunk
    except socket.timeout:
        pass
    ss.close()
    return data

for path in ['/', '/snmp', '/api', '/ws', '/socket', '/udp', '/connect', '/tunnel', '/bridge', '/health', '/status']:
    d = req(path)
    print(path, '->', d.split(b'\r\n')[0] if d else b'NO DATA')
