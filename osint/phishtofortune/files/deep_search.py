import os, re, base64, zipfile

base = r'c:\Users\mayan\OneDrive\Desktop\ctf\Phishtofortune\Phishtofortune\Phishtofortune'
xlsm = os.path.join(base, 'Phishtofortune.xlsm')

# 1) XLSM zip entries
print('=== XLSM zip entries ===')
with zipfile.ZipFile(xlsm) as z:
    for info in z.infolist():
        print(f'  {info.filename} size={info.file_size} compressed={info.compress_size}')
    for info in z.infolist():
        try:
            d = z.read(info.filename)
            for m in re.finditer(rb'(?i)flag\{[^}]*\}', d):
                print(f'  *** FLAG in {info.filename}: {m.group()}')
            for m in re.finditer(rb'[A-Za-z0-9+/]{20,}={0,2}', d):
                try:
                    dec = base64.b64decode(m.group())
                    if b'FLAG' in dec or b'flag' in dec:
                        print(f'  *** B64 in {info.filename}: {dec[:100]}')
                except: pass
        except: pass

# 2) Strings from printer settings
for fn in ['printerSettings1.bin', 'printerSettings2.bin']:
    fp = os.path.join(base, 'xl', 'printerSettings', fn)
    d = open(fp,'rb').read()
    strs = [m.group().decode('latin1') for m in re.finditer(rb'[ -~]{6,}', d)]
    if strs:
        print(f'\n=== strings in {fn} ===')
        for s in strs: print(f'  {s}')

# 3) GIF comment/app extensions
gifp = os.path.join(base, 'xl', 'media', 'image1.gif')
d = open(gifp,'rb').read()
print(f'\nGIF: {len(d)} bytes, header: {d[:6]}')
i = 0
while i < len(d):
    if d[i] == 0x21 and i+1 < len(d):
        ext_type = d[i+1]
        if ext_type == 0xFE:
            j = i+2; comment = b''
            while j < len(d) and d[j] != 0:
                blen = d[j]; j += 1; comment += d[j:j+blen]; j += blen
            print(f'GIF COMMENT at {i}: {comment}')
        elif ext_type == 0xFF:
            j = i+2; blen = d[j]; j += 1
            app = d[j:j+blen]; j += blen
            print(f'GIF APP ext at {i}: {app}')
    i += 1

# 4) Check ALL files for hex-encoded flag
for root, dirs, files in os.walk(base):
    for f in files:
        fp = os.path.join(root, f)
        d = open(fp, 'rb').read()
        # hex encoded FLAG{
        for m in re.finditer(rb'464c41477b', d):
            end = d.find(b'7d', m.start())
            if end > 0:
                hexflag = d[m.start():end+2].decode()
                print(f'HEX FLAG in {f}: {bytes.fromhex(hexflag)}')
        # check for ROT13 of FLAG{ = SYNT{
        for m in re.finditer(rb'SYNT\{[^}]*\}', d):
            import codecs
            print(f'ROT13 FLAG in {f}: {codecs.decode(m.group().decode(), "rot_13")}')
        for m in re.finditer(rb'synt\{[^}]*\}', d):
            import codecs
            print(f'ROT13 flag in {f}: {codecs.decode(m.group().decode(), "rot_13")}')

# 5) The xlsm raw bytes — search for any hidden streams
raw = open(xlsm, 'rb').read()
# After the zip end-of-central-directory, is there trailing data?
eocd = raw.rfind(b'PK\x05\x06')
if eocd > 0:
    # EOCD is 22 bytes + comment length
    comment_len = int.from_bytes(raw[eocd+20:eocd+22], 'little')
    end_of_zip = eocd + 22 + comment_len
    if end_of_zip < len(raw):
        trail = raw[end_of_zip:]
        print(f'\n=== trailing data after zip ({len(trail)} bytes) ===')
        print(trail[:200])
    else:
        print('\nNo trailing data after zip')
    if comment_len > 0:
        comment = raw[eocd+22:eocd+22+comment_len]
        print(f'ZIP comment: {comment}')
