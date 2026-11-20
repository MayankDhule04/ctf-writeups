import wave

filename = r"c:\Users\mayan\OneDrive\Desktop\ctf\new challeneg\GREEK.wav"

try:
    with wave.open(filename, 'rb') as w:
        frames = w.readframes(w.getnframes())
        import struct
        samples = struct.unpack(f"<{w.getnframes()}h", frames)
        
        bits = []
        for s in samples:
            bits.append(str(s & 1))
            
        bit_string = "".join(bits)
        
        for byte_order in ['big', 'little']:
            bytes_list = []
            for i in range(0, len(bit_string), 8):
                byte_str = bit_string[i:i+8]
                if len(byte_str) == 8:
                    if byte_order == 'little':
                        byte_str = byte_str[::-1]
                    bytes_list.append(chr(int(byte_str, 2)))
            
            ascii_text = "".join(b for b in bytes_list)
            
            # search for CTF, ctf, part, PART, flag, FLAG
            import re
            matches = re.finditer(r'.{0,10}(ctf|flag|part).{0,20}', ascii_text, re.IGNORECASE)
            print(f"--- MATCHES for {byte_order} ---")
            for m in matches:
                # filter to printable
                s = "".join(c if 32 <= ord(c) <= 126 else "." for c in m.group(0))
                print(s)
                
            # maybe the flag format is ctf{
            idx = ascii_text.lower().find("ctf{")
            if idx != -1:
                print("FOUND ctf{:", ascii_text[idx:idx+50])

except Exception as e:
    print(f"Error: {e}")
