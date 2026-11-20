"""Hunt for the PyASCIIObject header before each occurrence of key path strings
in the pristine snapshot. A PyASCIIObject has (on 64-bit):
  ob_refcnt (8), ob_type (8), length (8), hash (8), state (4), pad (4)
= 40 bytes header, then string bytes follow.

Find the length field (little-endian int64 with value == strlen)."""
import gzip, struct

d = gzip.decompress(open('snap_pristine.dmtcp','rb').read())

def find_pyuni(text):
    offs = []
    L = len(text)
    i = 0
    while True:
        j = d.find(text, i)
        if j < 0: break
        # Check 40 bytes before for a PyASCIIObject header pattern.
        if j >= 40:
            length = struct.unpack_from('<q', d, j - 40 + 16)[0]
            hash_ = struct.unpack_from('<q', d, j - 40 + 24)[0]
            state = struct.unpack_from('<I', d, j - 40 + 32)[0]
            ob_type = struct.unpack_from('<Q', d, j - 40 + 8)[0]
            ob_refcnt = struct.unpack_from('<q', d, j - 40)[0]
            hit = length == L and (state & 0xff) != 0  # rough sanity
            offs.append((j, length, hash_, hex(state), hex(ob_type), ob_refcnt, hit))
        i = j + 1
    return offs

for t in [b'/app/data/output/latest.txt', b'/app/data/runtime/active-config.json',
          b'initial_search_value', b'search_method', b'prime', b'mersenne']:
    print(f'\n=== {t!r} (len={len(t)}) ===')
    hits = find_pyuni(t)
    for j, ln, h, st, ty, rc, ok in hits[:6]:
        marker = '*' if ok else ' '
        print(f'  {marker} @{j:x} len={ln} hash={h:x} state={st} type={ty} refcnt={rc}')
