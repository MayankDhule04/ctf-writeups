"""
Minimal hand-rolled SNMP v1/v2c BER/ASN.1 encoder+decoder.
Built for tunneling raw SNMP packet bytes over a TCP/TLS stream
(the lab proxies each written buffer as one UDP datagram payload).
"""
import struct

# ---------- BER primitives ----------

def enc_len(n):
    if n < 0x80:
        return bytes([n])
    out = b''
    while n:
        out = bytes([n & 0xff]) + out
        n >>= 8
    return bytes([0x80 | len(out)]) + out

def enc_tlv(tag, value):
    return bytes([tag]) + enc_len(len(value)) + value

def enc_int(n, tag=0x02):
    if n == 0:
        b = b'\x00'
    else:
        neg = n < 0
        nb = n if not neg else (~n)
        out = b''
        while nb:
            out = bytes([nb & 0xff]) + out
            nb >>= 8
        if not out:
            out = b'\x00'
        if neg:
            out = bytes([~x & 0xff for x in out])
            # two's complement adjust
            carry = 1
            out = bytearray(out)
            for i in range(len(out) - 1, -1, -1):
                v = out[i] + carry
                out[i] = v & 0xff
                carry = v >> 8
                if carry == 0:
                    break
            out = bytes(out)
            if out[0] & 0x80 == 0:
                out = b'\xff' + out
        else:
            if out[0] & 0x80:
                out = b'\x00' + out
        b = out
    return enc_tlv(tag, b)

def enc_octetstring(s):
    if isinstance(s, str):
        s = s.encode()
    return enc_tlv(0x04, s)

def enc_null():
    return enc_tlv(0x05, b'')

def enc_oid(oid_str):
    parts = [int(x) for x in oid_str.strip('.').split('.')]
    first = parts[0] * 40 + parts[1]
    body = [first]
    for p in parts[2:]:
        body.append(p)
    out = b''
    for v in body:
        if v == 0:
            out += b'\x00'
            continue
        chunk = []
        while v:
            chunk.insert(0, v & 0x7f)
            v >>= 7
        for i in range(len(chunk) - 1):
            chunk[i] |= 0x80
        out += bytes(chunk)
    return enc_tlv(0x06, out)

def enc_seq(*parts):
    return enc_tlv(0x30, b''.join(parts))

def enc_seq_tag(tag, *parts):
    return enc_tlv(tag, b''.join(parts))

# ---------- BER decode ----------

class Reader:
    def __init__(self, data):
        self.data = data
        self.pos = 0

    def read_byte(self):
        b = self.data[self.pos]
        self.pos += 1
        return b

    def read_len(self):
        b = self.read_byte()
        if b < 0x80:
            return b
        n = b & 0x7f
        val = 0
        for _ in range(n):
            val = (val << 8) | self.read_byte()
        return val

    def read_tlv(self):
        tag = self.read_byte()
        length = self.read_len()
        value = self.data[self.pos:self.pos + length]
        self.pos += length
        return tag, value


def dec_int(value):
    n = 0
    neg = value[0] & 0x80
    for b in value:
        n = (n << 8) | b
    if neg:
        n -= (1 << (8 * len(value)))
    return n


def dec_oid(value):
    if not value:
        return ''
    first = value[0]
    parts = [first // 40, first % 40]
    i = 1
    cur = 0
    while i < len(value):
        b = value[i]
        cur = (cur << 7) | (b & 0x7f)
        if not (b & 0x80):
            parts.append(cur)
            cur = 0
        i += 1
    return '.'.join(str(p) for p in parts)


def parse_varbind_list(data):
    """data is the content of the varbind-list SEQUENCE."""
    r = Reader(data)
    results = []
    while r.pos < len(data):
        tag, vb = r.read_tlv()
        assert tag == 0x30
        vr = Reader(vb)
        otag, oval = vr.read_tlv()
        oid = dec_oid(oval)
        vtag, vval = vr.read_tlv()
        results.append((oid, vtag, vval))
    return results


def decode_message(data):
    """Returns dict: version, community, pdu_type, request_id, error_status,
    error_index, varbinds=[(oid, tag, value, decoded)]"""
    r = Reader(data)
    tag, body = r.read_tlv()
    assert tag == 0x30, f"expected SEQUENCE got {tag:#x}"
    br = Reader(body)
    t, v = br.read_tlv()
    version = dec_int(v)
    t, v = br.read_tlv()
    community = v.decode(errors='replace')
    t, pdu_body = br.read_tlv()
    pdu_type = t
    pr = Reader(pdu_body)
    t, v = pr.read_tlv()
    request_id = dec_int(v)
    t, v = pr.read_tlv()
    error_status = dec_int(v)
    t, v = pr.read_tlv()
    error_index = dec_int(v)
    t, vbdata = pr.read_tlv()
    assert t == 0x30
    raw_vbs = parse_varbind_list(vbdata)
    varbinds = []
    for oid, vtag, vval in raw_vbs:
        decoded = None
        if vtag == 0x04:
            decoded = vval
        elif vtag in (0x02, 0x41, 0x43, 0x42):  # int, counter, timeticks, gauge
            decoded = dec_int(vval)
        elif vtag == 0x05:
            decoded = None
        elif vtag == 0x06:
            decoded = dec_oid(vval)
        else:
            decoded = vval
        varbinds.append((oid, vtag, vval, decoded))
    return {
        'version': version,
        'community': community,
        'pdu_type': pdu_type,
        'request_id': request_id,
        'error_status': error_status,
        'error_index': error_index,
        'varbinds': varbinds,
    }


# ---------- PDU builders ----------

GET_REQUEST = 0xa0
GETNEXT_REQUEST = 0xa1
GET_RESPONSE = 0xa2
SET_REQUEST = 0xa3
GETBULK_REQUEST = 0xa5  # v2c only


def build_get_request(community, oids, request_id=1, version=0, pdu_tag=GET_REQUEST,
                       error_status=0, error_index=0):
    varbinds = b''
    for oid in oids:
        vb = enc_seq(enc_oid(oid), enc_null())
        varbinds += vb
    vb_list = enc_seq(varbinds)  # wrap all varbinds list; note enc_seq joins already-encoded TLVs
    pdu = enc_seq_tag(
        pdu_tag,
        enc_int(request_id),
        enc_int(error_status),
        enc_int(error_index),
        vb_list,
    )
    msg = enc_seq(
        enc_int(version),
        enc_octetstring(community),
        pdu,
    )
    return msg


def build_getbulk_request(community, oids, request_id=1, non_repeaters=0, max_repetitions=10):
    varbinds = b''
    for oid in oids:
        varbinds += enc_seq(enc_oid(oid), enc_null())
    vb_list = enc_seq(varbinds)
    pdu = enc_seq_tag(
        GETBULK_REQUEST,
        enc_int(request_id),
        enc_int(non_repeaters),
        enc_int(max_repetitions),
        vb_list,
    )
    msg = enc_seq(
        enc_int(1),  # v2c
        enc_octetstring(community),
        pdu,
    )
    return msg
