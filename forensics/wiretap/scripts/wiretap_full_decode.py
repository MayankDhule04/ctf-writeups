#!/usr/bin/env python3
"""
Wiretap - Full DTMF Decode with T9 interpretation
"""

import wave
import numpy as np

def goertzel(samples, sample_rate, target_freq):
    n = len(samples)
    k = int(0.5 + (n * target_freq) / sample_rate)
    omega = (2.0 * np.pi * k) / n
    sine = np.sin(omega)
    cosine = np.cos(omega)
    coeff = 2.0 * cosine
    
    q0, q1, q2 = 0.0, 0.0, 0.0
    
    for sample in samples:
        q0 = coeff * q1 - q2 + sample
        q2 = q1
        q1 = q0
    
    magnitude = np.sqrt(q1**2 + q2**2 - q1*q2*coeff)
    return magnitude

def detect_dtmf_tone(samples, sample_rate):
    low_freqs = [697, 770, 852, 941]
    high_freqs = [1209, 1336, 1477, 1633]
    
    dtmf_table = [
        ['1', '2', '3', 'A'],
        ['4', '5', '6', 'B'],
        ['7', '8', '9', 'C'],
        ['*', '0', '#', 'D']
    ]
    
    low_mags = [goertzel(samples, sample_rate, f) for f in low_freqs]
    high_mags = [goertzel(samples, sample_rate, f) for f in high_freqs]
    
    low_idx = np.argmax(low_mags)
    high_idx = np.argmax(high_mags)
    
    threshold = 1000000
    if low_mags[low_idx] > threshold and high_mags[high_idx] > threshold:
        return dtmf_table[low_idx][high_idx]
    
    return None

def decode_t9(sequence):
    """
    Decode T9 multi-tap text
    * = space, # = next letter, pause = next letter
    """
    # T9 mapping
    t9_map = {
        '2': 'ABC', '3': 'DEF', '4': 'GHI', '5': 'JKL',
        '6': 'MNO', '7': 'PQRS', '8': 'TUV', '9': 'WXYZ',
        '0': ' ', '1': ''
    }
    
    result = []
    i = 0
    
    while i < len(sequence):
        char = sequence[i]
        
        if char == '*':
            result.append(' ')
            i += 1
        elif char == '#':
            i += 1  # Skip, it's a separator
        elif char in t9_map:
            # Count consecutive presses
            count = 1
            while i + count < len(sequence) and sequence[i + count] == char:
                count += 1
            
            # Get the letter
            letters = t9_map[char]
            if letters:
                letter_idx = (count - 1) % len(letters)
                result.append(letters[letter_idx])
            
            i += count
        else:
            i += 1
    
    return ''.join(result)

print("="*70)
print("WIRETAP - FULL DTMF DECODE")
print("="*70)

# Read WAV
wav_file = "beep_beep_boop.wav"
with wave.open(wav_file, 'rb') as wav:
    sample_rate = wav.getframerate()
    n_frames = wav.getnframes()
    frames = wav.readframes(n_frames)

audio_data = np.frombuffer(frames, dtype=np.int16).astype(np.float64)

# Detect all tones
chunk_size = int(sample_rate * 0.05)
hop_size = int(sample_rate * 0.02)

detected_sequence = []
last_tone = None
last_time = -1

print("\nProcessing audio (this may take a moment)...")

for i in range(0, len(audio_data) - chunk_size, hop_size):
    chunk = audio_data[i:i+chunk_size]
    tone = detect_dtmf_tone(chunk, sample_rate)
    
    current_time = i / sample_rate
    
    if tone and tone != last_tone:
        if current_time - last_time > 0.1:
            detected_sequence.append(tone)
            last_time = current_time
        last_tone = tone
    elif not tone:
        last_tone = None

sequence = ''.join(detected_sequence)
print(f"\nFull sequence ({len(sequence)} digits):")
print(f"{sequence}")

# Try to decode as T9
print(f"\n{'='*70}")
print("T9 DECODING ATTEMPTS:")
print(f"{'='*70}")

# Method 1: Treat * as space separator
print("\n[1] Using * as space:")
parts = sequence.split('*')
decoded_parts = []
for part in parts:
    if part:
        decoded = decode_t9(part)
        decoded_parts.append(decoded)
        print(f"  {part} -> {decoded}")

full_text = ' '.join(decoded_parts)
print(f"\nFull text: {full_text}")

# Check for flag
if 'CIT' in full_text.upper():
    print(f"\n✓✓ POSSIBLE FLAG FOUND!")
    # Format as flag
    flag_text = full_text.replace(' ', '_').lower()
    print(f"FLAG: CIT{{{flag_text}}}")

# Method 2: Try without spaces
print(f"\n[2] Continuous decode (no spaces):")
decoded_continuous = decode_t9(sequence.replace('*', ''))
print(f"  {decoded_continuous}")

print(f"\n{'='*70}")
