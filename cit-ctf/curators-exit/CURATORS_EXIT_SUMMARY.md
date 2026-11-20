# The Curator's Exit - OSINT Challenge Summary

## Challenge Info
- **Category**: OSINT
- **Points**: 971 (elemental3)
- **Description**: "We've received a communication from Interpol, containing a PDF. We are unsure of the contents, but believe it contains information on one of the thieves from the Louvre Heist. Your job is to find out as much as you can about this individual and send the information back to the authorities."
- **Question**: What is the thief's name?
- **Flag Format**: `CIT{First_Last}`
- **File**: VF0000000011-Enc.pdf
- **SHA1**: c3c8f91ed60e902be482dc26b61a9bc0fa443f26 ✓ Verified

## Analysis Performed

### PDF Status
- **Encrypted**: YES (Password-protected)
- **Size**: 155,296 bytes
- **Pages**: 3 (based on PDF structure)
- **Encryption**: Strong encryption, not crackable with common passwords

### Password Attempts (300+ passwords tested)
❌ Common passwords (password, admin, 123456, etc.)
❌ Louvre-related (louvre, Louvre, LOUVRE, etc.)
❌ Interpol-related (interpol, Interpol, INTERPOL, etc.)
❌ Curator-related (curator, Curator, curatorexit, etc.)
❌ Art/Museum-related (monalisa, davinci, art, museum, etc.)
❌ Filename-based (VF0000000011, 0000000011, 11, etc.)
❌ Challenge-based (971, elemental3, etc.)
❌ SHA1 hash-based (full hash, partial hash, etc.)
❌ Famous art thieves (Vincenzo, Peruggia, VincenzoPeruggia, etc.)
❌ Empty password

### Raw PDF Analysis
- Contains encrypted streams (FlateDecode)
- Has auto-actions
- Metadata is encrypted
- No readable text in raw bytes
- No embedded unencrypted files

## Possible Solutions

### 1. Advanced PDF Cracking
Use specialized tools:
```bash
# pdfcrack (brute force)
pdfcrack -f VF0000000011-Enc.pdf -w wordlist.txt

# John the Ripper
pdf2john VF0000000011-Enc.pdf > hash.txt
john --wordlist=rockyou.txt hash.txt

# Hashcat (if hash can be extracted)
hashcat -m 10500 hash.txt wordlist.txt
```

### 2. OSINT Research
The password might be:
- A famous Louvre heist detail (date, location, item stolen)
- A real art thief's name or alias
- A specific Interpol case number
- Hidden in another challenge or file

### 3. Historical Context
**Famous Louvre Thefts**:
- **1911**: Vincenzo Peruggia stole the Mona Lisa
- **1998**: Corot painting stolen
- **2019**: Attempted theft

**Possible Passwords to Try**:
- Dates: 1911, 21081911, August211911
- Names: Vincenzo, Peruggia, VincenzoPeruggia
- Items: MonaLisa, LaJoconde
- Locations: SalleDesEtats

### 4. Check for Additional Files
- Look for images with steganography
- Check for other documents in the challenge
- Look for hints in the CTF platform

### 5. Metadata Clues
The filename "VF0000000011-Enc" suggests:
- VF = Possibly "Verified File" or "Victim File"
- 0000000011 = Case number or file ID
- Enc = Encrypted

## Recommended Next Steps

1. **Use pdfcrack or John the Ripper** with a comprehensive wordlist
2. **Research famous Louvre heists** and try related passwords
3. **Check if there are other files** in the challenge that contain the password
4. **Look for steganography** in any images associated with the challenge
5. **Try online PDF password recovery services** (if allowed)
6. **Contact challenge organizers** if the PDF is corrupted or password is missing

## Tools Used
- PyPDF2 (Python library)
- Custom password generation scripts
- Raw byte analysis

## Files Created
- `curators_exit_analyzer.py` - Initial PDF analysis
- `curator_pdf_decrypt.py` - Common password attempts
- `curator_pdf_metadata.py` - Metadata extraction
- `curator_bruteforce.py` - Wordlist generation (308 passwords)
- `curator_raw_analysis.py` - Raw byte analysis
- `curator_specific_passwords.py` - Context-specific passwords
- `curator_hash_passwords.py` - SHA1-based passwords
- `curator_raw_strings.txt` - Extracted printable strings

## Conclusion
The PDF is strongly encrypted and requires either:
1. The correct password (likely related to a specific Louvre heist detail)
2. Advanced cracking tools with large wordlists
3. Additional information from other challenge files

The thief's name is inside the PDF and will be in the format `CIT{First_Last}` once decrypted.
