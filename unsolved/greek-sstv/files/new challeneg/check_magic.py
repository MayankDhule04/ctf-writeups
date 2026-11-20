import magic

m = magic.Magic(mime=True)
mime_type = m.from_file(r"c:\Users\mayan\OneDrive\Desktop\ctf\new challeneg\lsb.bin")
print(f"MIME type of LSB data: {mime_type}")

desc = magic.from_file(r"c:\Users\mayan\OneDrive\Desktop\ctf\new challeneg\lsb.bin")
print(f"Description: {desc}")
