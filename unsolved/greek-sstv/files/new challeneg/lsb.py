import wave

filename = r"c:\Users\mayan\OneDrive\Desktop\ctf\new challeneg\GREEK.wav"

try:
    with wave.open(filename, 'rb') as w:
        frames = w.readframes(w.getnframes())
        # 16-bit audio, little endian
        # LSB of each 16-bit sample
        import struct
        samples = struct.unpack(f"<{w.getnframes()}h", frames)
        
        bits = []
        for s in samples:
            bits.append(str(s & 1))
            
        bit_string = "".join(bits)
        
        # Convert bits to bytes
        # Try both MSB first and LSB first per byte
        for byte_order in ['big', 'little']:
            bytes_list = []
            for i in range(0, len(bit_string), 8):
                byte_str = bit_string[i:i+8]
                if len(byte_str) == 8:
                    if byte_order == 'little':
                        byte_str = byte_str[::-1]
                    bytes_list.append(chr(int(byte_str, 2)))
            
            ascii_text = "".join(b for b in bytes_list if 32 <= ord(b) <= 126)
            print(f"--- Decoded ASCII (order: {byte_order}) ---")
            if "flag" in ascii_text.lower() or "ctf" in ascii_text.lower() or "part" in ascii_text.lower():
                import re
                matches = re.finditer(r'.{0,20}(flag|ctf|part).{0,20}', ascii_text, re.IGNORECASE)
                for m in matches:
                    print(m.group(0))
            else:
                print("No obvious flag keywords found, printing first 200 printable chars:")
                print(ascii_text[:200])

except Exception as e:
    print(f"Error: {e}")
