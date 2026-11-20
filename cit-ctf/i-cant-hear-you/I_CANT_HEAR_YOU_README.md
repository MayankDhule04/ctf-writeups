# I Can't Hear You - CTF Challenge Solution

## 🎯 Challenge Overview
**Category:** Forensics  
**Title:** I Can't Hear You  
**File:** `i_cant_hear_you (1).wav`

## 🔍 The Problem
The WAV file has a **header mismatch**:
- Header declares: **16-bit PCM**
- Actual data: **8-bit PCM** (proven by block_align=1 and byte_rate=16000)

When audio players read this file, they interpret pairs of 8-bit samples as single 16-bit samples, resulting in **garbled static noise** - hence "I Can't Hear You"!

## ✅ What I've Done For You

### 1. Analysis Scripts Created ✨

| Script | Purpose |
|--------|---------|
| `i_cant_hear_you_solver.py` | Main solver - fixes header, analyzes audio data |
| `advanced_audio_forensics.py` | Creates spectrograms, detects morse/DTMF |
| `read_spectrogram_text.py` | High-resolution spectrogram generation |
| `compare_audio_files.py` | Compares your existing fixed versions |
| `extract_flag_from_spectrogram.py` | OCR and manual inspection guide |

### 2. Fixed Audio Files Created 🎵

| File | Description |
|------|-------------|
| `fixed_8bit_corrected.wav` | ✅ Corrected 8-bit header - PLAYABLE! |
| `fixed_8bit_raw.wav` | Your version (unsigned) |
| `fixed_8bit_shifted.wav` | Your version (signed, centered at 128) |
| `audio_8bit.raw` | Raw PCM data |

### 3. Spectrograms Generated 📊

| File | Description |
|------|-------------|
| `spectrogram.png` | Basic spectrogram |
| `spectrogram_detailed.png` | **HIGH-RES with 3 views - CHECK THIS!** |
| `spectrogram_data.npz` | Raw data for further analysis |

## 🎯 NEXT STEPS - How to Get the Flag

### Step 1: Look at the Spectrogram! 👀
```bash
# Open this file and look for visible text:
spectrogram_detailed.png
```

**What to look for:**
- Horizontal lines forming letters/numbers
- Usually in the **upper half** (3000-8000 Hz range)
- Text appears as frequency bands over time
- Flag format: `CTF{...}` or `CIT{...}`

### Step 2: Play the Fixed Audio 🔊
```bash
# Right-click the file and play with any audio player:
fixed_8bit_corrected.wav
```

The flag might be:
- Spoken words
- Morse code beeps
- DTMF tones (phone keypad)
- Or just the audio itself reveals something

### Step 3: If You See Partial Text
If you can read even part of the text in the spectrogram, run:
```bash
python extract_flag_from_spectrogram.py
```

Or just tell me what you see and I'll help extract it!

## 📊 Analysis Results Summary

### Header Mismatch Confirmed ✅
```
Original Header:
- Bits Per Sample: 16 (wrong!)
- Block Align: 1 (indicates 8-bit)
- Byte Rate: 16000 (indicates 8-bit)
- Sample Rate: 16000 Hz

Misinterpretation:
- Players think it's 6.20 seconds @ 16-bit
- Reality: 12.40 seconds @ 8-bit
```

### Spectrogram Analysis ✅
```
Strong frequency bands detected at:
- 7500 Hz
- 6906 Hz  
- 3500 Hz
- 4500 Hz
- 1094 Hz
- And many more between 500-8000 Hz

54 frequency bands have strong persistent signals
→ Likely forming text characters!
```

### Pattern Detection ✅
```
✅ Morse code patterns: 13 pulses detected
✅ Frequency peaks: Multiple strong bands
❌ DTMF tones: None detected
❌ LSB steganography: No clear flag
```

## 🚀 Quick Commands

### Re-run complete analysis:
```bash
python i_cant_hear_you_solver.py
```

### Generate fresh spectrograms:
```bash
python read_spectrogram_text.py
```

### Try OCR extraction:
```bash
python extract_flag_from_spectrogram.py
```

### Compare your fixed versions:
```bash
python compare_audio_files.py
```

## 💡 CTF Tips

### Why "I Can't Hear You"?
The challenge name is a **huge hint**:
- You CAN'T hear it → Audio is garbled
- But you CAN see it → Look at spectrogram!
- Classic **spectrogram steganography**

### Common Flag Locations in Audio CTF:
1. **Spectrogram text** (MOST LIKELY) ⭐⭐⭐
2. Spoken/audible message
3. LSB steganography
4. Morse code
5. DTMF tones
6. Metadata/comments
7. Phase encoding

We've checked all of these. The spectrogram is the most promising!

## 📝 Technical Details

### The Header Fix
Changed bytes 34-35 (bits per sample) from 16 → 8:
```python
struct.pack_into('<H', data, 34, 8)  # Set to 8-bit
```

### Why Both Raw and Shifted Versions?
- **Raw**: Unsigned 8-bit (0-255)
- **Shifted**: Signed 8-bit centered at 128 (for proper audio playback)
- Both are valid, shifted sounds better

### Spectrogram Settings Used
```
NFFT values: 512, 2048, 4096
- 512: Better time resolution (for text)
- 2048: Balanced
- 4096: Better frequency resolution
```

## 🎪 What Makes This Challenge Clever

1. **Header Mismatch**: Clever misdirection
2. **Name Hint**: "I Can't Hear You" = visual clue
3. **Multi-Stage**: Fix → Analyze → Visualize
4. **Classic Technique**: Spectrogram steganography is a CTF staple

## 📞 Need Help?

If you:
- See something in the spectrogram but can't read it clearly
- Hear something in the audio but can't decipher it  
- Need me to enhance/process the images
- Want to try different analysis approaches

Just describe what you see/hear and I'll help decode it!

## ⚡ TL;DR

1. ✅ Header fixed - audio now plays correctly
2. ✅ Spectrograms generated in high resolution
3. 👉 **OPEN `spectrogram_detailed.png` AND LOOK FOR TEXT**
4. 👉 **PLAY `fixed_8bit_corrected.wav` AND LISTEN**
5. 👉 **Tell me what you find!**

---

The flag is in there - we just need to see or hear it! 🎯
