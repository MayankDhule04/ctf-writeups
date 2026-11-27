import socket, ssl, sys
sys.path.insert(0, '/projects/sandbox/.agents/tasks/task-snmp-fab-edge03')
from snmp_min import build_get_request, decode_message

HOST = 'l-1d1390b81f3b4637-16326.cf959180.tb7.in'
PORT = 443


def connect():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    s = socket.create_connection((HOST, PORT), timeout=10)
    ss = ctx.wrap_socket(s)
    ss.settimeout(5)
    return ss


def send_recv(ss, pkt):
    ss.sendall(pkt)
    try:
        data = ss.recv(4096)
    except socket.timeout:
        return None
    return data


if __name__ == '__main__':
    ss = connect()
    # sysDescr.0
    pkt = build_get_request('public', ['1.3.6.1.2.1.1.1.0'], request_id=1, version=0)
    print('sent', pkt.hex())
    resp = send_recv(ss, pkt)
    print('resp raw:', resp)
    if resp:
        try:
            msg = decode_message(resp)
            print(msg)
        except Exception as e:
            print('decode error', e)
