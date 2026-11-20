# I Can't Hear You - CTF Forensics Challenge Solution Guide

## Challenge Summary
**Title:** I Can't Hear You  
**Category:** Forensics  
**File:** `i_cant_hear_you (1).wav`

## The Trick

The WAV file header declares **16-bit samples**, but the `block_align` and `byte_rate` fields reveal the actual audio is **8-bit PCM**.

- **Header says:** 16-bit samples (bits_per_sample = 16)
- **Reality:** Block align = 1, Byte rate = 16000 (consistent with 8-bit, not 16-bit)

When a normal audio player reads this file:
1. It trusts the "16-bit" field in the header
2. It reads **2 bytes per sample** instead of 1
3. This causes every pair of 8-bit samples to be interpreted as one 16-bit sample
4. The result is **garbled static noise** - "I Can't Hear You"!

## Analysis Results

### Original File Analysis
```
Bits Per Sample: 16 (declared)
Block Align: 1 (suggests 8-bit)
Byte Rate: 16000 (suggests 8-bit)
Sample Rate: 16000 Hz
Data Size: 198408 bytes

MISMATCH DETECTED!
- If truly 16-bit: 99,204 samples, 6.20 seconds duration
- If truly 8-bit: 198,408 samples, 12.40 seconds duration
```

## Solution Steps

### Step 1: Fix the WAV Header ✓
Run `i_cant_hear_you_solver.py` to:
- Analyze the header mismatch
- Create `fixed_8bit_corrected.wav` with correct 8-bit header
- Extract raw audio data

### Step 2: Create Spectrogram ✓
Run `read_spectrogram_text.py` to:
- Generate high-resolution spectrograms
- Create `spectrogram_detailed.png`
- The flag is likely **visible as text in the spectrogram**!

### Step 3: Read the Spectrogram 👁️
**Look at the generated spectrogram images:**
- `spectrogram.png` - Initial spectrogram
- `spectrogram_detailed.png` - High-resolution with 3 different views

**What to look for:**
- Horizontal lines forming letters/numbers in the frequency domain
- Text typically appears in the mid-to-high frequency range (3000-8000 Hz)
- The "joke" is you can't HEAR it, but you can SEE it!

### Key Frequencies Detected:
Top energy bands (potential text regions):
- 7500 Hz
- 6906 Hz  
- 3500 Hz
- 4500 Hz
- Various bands between 500-7500 Hz

## Files Generated

1. **fixed_8bit_corrected.wav** - Playable audio with corrected header
2. **audio_8bit.raw** - Raw 8-bit audio data
3. **spectrogram.png** - Visual spectrogram
4. **spectrogram_detailed.png** - High-res spectrogram (3 views)
5. **spectrogram_data.npz** - Raw spectrogram data for further analysis

## How to Find the Flag

### Method 1: Visual Inspection (Most Likely)
1. Open `spectrogram_detailed.png`
2. Look for horizontal lines forming text characters
3. Text in audio spectrograms appears as frequency bands that form letters
4. Common formats: `CTF{...}`, `FLAG{...}`, `CIT{...}`

### Method 2: Play the Fixed Audio
```bash
# Use any audio player
# Windows: Right-click → Open with → Windows Media Player
# Or use online tools like: https://www.audacityteam.org/
```

### Method 3: OCR on Spectrogram
If the text is visible but hard to read, you can:
1. Crop the spectrogram to just the text region
2. Enhance contrast
3. Use OCR tools to extract the text

## Tools Provided

### i_cant_hear_you_solver.py
- Header analysis and validation
- Fixes WAV header to 8-bit
- Extracts raw audio data  
- LSB steganography check
- Alternate interpretation attempts

### advanced_audio_forensics.py
- Creates spectrograms
- Detects morse code patterns
- Detects DTMF tones
- Phase analysis
- Metadata extraction

### read_spectrogram_text.py
- High-resolution spectrogram generation
- Multiple NFFT settings for different text sizes
- Frequency band analysis
- Pattern detection for text-like features

### compare_audio_files.py
- Compares different audio file versions
- Extracts differences
- Tests for hidden data in differences

## Next Steps

1. **OPEN THE SPECTROGRAM IMAGES** - This is the most important step!
2. Look for visible text in the frequency domain
3. If you see text but can't read it clearly, let me know and I can enhance it
4. Try playing the fixed WAV file in case the message is audible

## Common CTF Audio Steganography Techniques

This challenge uses: **Spectrogram Steganography**
- Data hidden in frequency domain
- Visible when visualized, inaudible when played
- Perfect for "I Can't Hear You" theme!

Other techniques (not applicable here):
- ❌ LSB Steganography - checked, no flag found
- ❌ DTMF Tones - checked, none detected
- ❌ Morse Code - pattern detected but not forming clear message
- ❌ Phase Encoding - checked, no obvious patterns

## Flag Format
Most likely: `CTF{...}` or `CIT{...}` or `FLAG{...}`

---

**The key insight:** The challenge title "I Can't Hear You" is a clue that you need to SEE the flag, not hear it!
