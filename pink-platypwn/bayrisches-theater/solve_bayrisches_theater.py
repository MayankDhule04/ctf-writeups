import ctypes
from ctypes import wintypes, c_void_p, c_size_t

CF_UNICODETEXT = 13
u32 = ctypes.windll.user32
k32 = ctypes.windll.kernel32

u32.OpenClipboard.argtypes = [wintypes.HWND]
u32.OpenClipboard.restype = wintypes.BOOL
u32.GetClipboardData.argtypes = [wintypes.UINT]
u32.GetClipboardData.restype = wintypes.HANDLE
k32.GlobalLock.argtypes = [wintypes.HGLOBAL]
k32.GlobalLock.restype = c_void_p
k32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]

if not u32.OpenClipboard(None):
    print("could not open clipboard"); raise SystemExit
try:
    h = u32.GetClipboardData(CF_UNICODETEXT)
    if not h:
        print("no unicode text on clipboard - copy the emoji first"); raise SystemExit
    p = k32.GlobalLock(h)
    s = ctypes.wstring_at(p)
    k32.GlobalUnlock(h)
finally:
    u32.CloseClipboard()

open('theater_clip.txt','w',encoding='utf-8').write(s)
print("chars:", len(s))
hidden=[ord(c) for c in s if (0xFE00<=ord(c)<=0xFE0F) or (0xE0100<=ord(c)<=0xE01EF)]
print("variation-selector chars:", len(hidden))

out=bytearray()
for c in s:
    o=ord(c)
    if 0xFE00<=o<=0xFE0F:     out.append(o-0xFE00)
    elif 0xE0100<=o<=0xE01EF: out.append(o-0xE0100+16)
print("hidden byte count:", len(out))
if out:
    print("DECODED:", out.decode('utf-8','replace'))
else:
    extra=[hex(ord(c)) for c in s if c not in ('\U0001F7E6','\u2B1C','\n','\r')]
    print("no VS bytes; other codepoints:", extra[:60])
