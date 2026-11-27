import socket, ssl, sys, time
sys.path.insert(0, '/projects/sandbox/.agents/tasks/task-snmp-fab-edge03')
from snmp_min import build_get_request, decode_message

HOST = 'l-1d1390b81f3b4637-16326.cf959180.tb7.in'
PORT = 443

COMMUNITIES = ['public', 'private', 'read', 'readonly', 'ro', 'monitor',
               'guest', 'snmp', 'community', 'fabric', 'san', 'cisco',
               'brocade', 'switch', 'public1', 'read-only', 'view']


def connect():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    s = socket.create_connection((HOST, PORT), timeout=10)
    ss = ctx.wrap_socket(s)
    ss.settimeout(2.5)
    return ss


def try_community(community, version):
    ss = connect()
    pkt = build_get_request(community, ['1.3.6.1.2.1.1.1.0'], request_id=1, version=version)
    ss.sendall(pkt)
    try:
        data = ss.recv(4096)
    except socket.timeout:
        data = None
    ss.close()
    return data


for ver, vname in [(0, 'v1'), (1, 'v2c')]:
    for c in COMMUNITIES:
        d = try_community(c, ver)
        status = 'NO RESP' if not d else f'RESP {len(d)}B: {d.hex()[:80]}'
        print(f'{vname:4} community={c!r:15} -> {status}')
        time.sleep(0.05)
