# Dog Barking Challenge - Analysis Summary

## Challenge Info
- **Category**: Misc
- **Points**: 900
- **Hint**: "dogs were trying to tell me something"
- **File**: dog.wav
- **Flag Format**: `CIT{example_flag}`

## Audio Properties
- **Duration**: 77.80 seconds
- **Sample Rate**: 16000 Hz
- **Channels**: 1 (mono)
- **Bit Depth**: 16-bit
- **Samples**: 1,244,819

## Analysis Performed

### 1. LSB Steganography ❌
- Checked all 16 bit positions (bit 0 through bit 15)
- Tried standard LSB, reverse bit order, 2-bit LSB, MSB
- Tried different byte alignment offsets (0-7)
- **Result**: No readable text or flag found

### 2. Bark Timing Analysis ❌
- Detected 138 bark-like peaks using envelope detection
- Analyzed gaps between barks for binary/Morse encoding
- Tried multiple threshold percentiles (25th, 33rd, 50th, 66th, 75th)
- **Result**: Decoded text was mostly garbage, no flag

### 3. Frequency Analysis ✓ PROMISING
- **Dominant Frequencies**: 487-503 Hz (very specific!)
- **Zero Crossing Rate**: 0.0656 (LOW - suggests tones, not noise)
- **Top frequency**: 495 Hz with magnitude 21,989,315
- This is NOT typical dog barking - it's tone-based encoding!

### 4. Spectrogram Analysis ✓ LIKELY SOLUTION
- Generated multiple spectrogram images:
  - `dog_spectrogram.png` - Full spectrum (0-8kHz)
  - `dog_spectrogram_high_freq.png` - High frequencies (4-8kHz)
  - `dog_binary_0.4.png`, `dog_binary_0.5.png`, `dog_binary_0.6.png` - Binary thresholded
  - `dog_binary_flipped.png` - Flipped version
- Text in spectrograms is usually visible in 4-8kHz range
- **Action Required**: Manual inspection of PNG files

### 5. SSTV Check ✓ POSSIBLE
- SSTV (Slow Scan Television) transmits images via audio
- Typical SSTV frequencies: 1200Hz, 1500Hz, 1900Hz, 2300Hz
- Our audio has some energy at these frequencies
- **Action Required**: Try SSTV decoder

## Recommendations

### Option 1: Manual Spectrogram Inspection (RECOMMENDED)
1. Open the generated PNG files in an image viewer
2. Look for text written horizontally in the frequency domain
3. Text is usually in the 4-8kHz range
4. May need to adjust contrast/brightness

### Option 2: Use Audacity (BEST FOR VISUALIZATION)
```bash
# Install Audacity if not already installed
# Open dog.wav in Audacity
# Click on track name dropdown > Spectrogram
# Or: Analyze > Plot Spectrum
# Look for text patterns in the visualization
```

### Option 3: SSTV Decoder
If the spectrogram shows an image rather than text:
- **Windows**: Use RX-SSTV or MMSSTV
- **Linux**: Use QSSTV
- **Online**: https://sstv-decoder.com/
- Upload dog.wav and try different SSTV modes

### Option 4: Advanced Tools
```bash
# Install sox for audio analysis
sox dog.wav -n spectrogram -o spectrogram_sox.png

# Or use online spectrogram viewers
# https://academo.org/demos/spectrum-analyzer/
```

## Files Created
- `dog_barking_analyzer.py` - Initial LSB and bark detection
- `dog_comprehensive_analyzer.py` - Multiple LSB extraction methods
- `dog_timing_analyzer.py` - Bark timing and gap analysis
- `dog_visual_analysis.py` - Envelope and peak detection
- `dog_spectrogram.py` - Spectrogram generation
- `dog_spectrogram_ocr.py` - Binary spectrogram images
- `dog_all_bits.py` - All bit position extraction
- `dog_sstv_check.py` - SSTV signature detection

## Next Steps
1. **IMMEDIATE**: Open `dog_spectrogram.png` and look for text
2. If no text visible, try `dog_binary_0.5.png` (better contrast)
3. If still nothing, use Audacity for better visualization
4. If it's an image, use SSTV decoder
5. The flag will be in format `CIT{...}`

## Notes
- The audio is NOT actual dog barking - it's synthesized tones
- The dominant frequency around 495Hz suggests intentional encoding
- The hint "dogs were trying to tell me something" strongly suggests visual/spectrogram analysis
- This is a classic spectrogram steganography challenge
