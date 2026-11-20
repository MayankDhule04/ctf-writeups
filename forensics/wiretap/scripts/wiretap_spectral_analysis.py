#!/usr/bin/env python3
"""
Wiretap - Spectral Analysis and Better DTMF Detection
Try to extract ALL tones more accurately
"""

import wave
import numpy as np
from scipy import signal as scipy_signal

def detect_dtmf_advanced(audio_data, sample_rate):
    """
    Advanced DTMF detection using spectrogram
    """
    # DTMF frequencies
    low_freqs = [697, 770, 852, 941]
    high_freqs = [1209, 1336, 1477, 1633]
    
    dtmf_table = {
        (697, 1209): '1', (697, 1336): '2', (697, 1477): '3', (697, 1633): 'A',
        (770, 1209): '4', (770, 1336): '5', (770, 1477): '6', (770, 1633): 'B',
        (852, 1209): '7', (852, 1336): '8', (852, 1477): '9', (852, 1633): 'C',
        (941, 1209): '*', (941, 1336): '0', (941, 1477): '#', (941, 1633): 'D',
    }
    
    # Create spectrogram
    window_size = int(sample_rate * 0.05)  # 50ms
    hop_length = int(sample_rate * 0.01)   # 10ms
    
    f, t, Sxx = scipy_signal.spectrogram(audio_data, sample_rate, 
                                          nperseg=window_size, 
                                          noverlap=window_size-hop_length)
    
    detected_tones = []
    last_tone = None
    last_time = -1
    
    for time_idx in range(Sxx.shape[1]):
        spectrum = Sxx[:, time_idx]
        current_time = t[time_idx]
        
        # Find peaks in spectrum
        peaks = []
        for freq_list in [low_freqs, high_freqs]:
            max_mag = 0
            best_freq = None
            for target_freq in freq_list:
                # Find closest frequency bin
                freq_idx = np.argmin(np.abs(f - target_freq))
                mag = spectrum[freq_idx]
                if mag > max_mag:
                    max_mag = mag
                    best_freq = target_freq
            if max_mag > 1e-6:  # Threshold
                peaks.append((best_freq, max_mag))
        
        # Check if we have both low and high frequency
        if len(peaks) == 2:
            low_freq = min(peaks[0][0], peaks[1][0])
            high_freq = max(peaks[0][0], peaks[1][0])
            
            # Match to DTMF
            for (f_low, f_high), digit in dtmf_table.items():
                if abs(low_freq - f_low) < 50 and abs(high_freq - f_high) < 50:
                    if digit != last_tone and current_time - last_time > 0.1:
                        detected_tones.append((current_time, digit))
                        last_tone = digit
                        last_time = current_time
                    break
    
    return detected_tones

print("="*70)
print("WIRETAP - SPECTRAL ANALYSIS")
print("="*70)

# Read WAV
wav_file = "beep_beep_boop.wav"
with wave.open(wav_file, 'rb') as wav:
    sample_rate = wav.getframerate()
    n_frames = wav.getnframes()
    frames = wav.readframes(n_frames)

audio_data = np.frombuffer(frames, dtype=np.int16).astype(np.float64)

print(f"\nAnalyzing audio with scipy spectrogram...")

try:
    detections = detect_dtmf_advanced(audio_data, sample_rate)
    
    print(f"\nDetected {len(detections)} tones:\n")
    for time, tone in detections:
        print(f"  {time:7.2f}s: {tone}")
    
    sequence = ''.join([t[1] for t in detections])
    print(f"\n{'='*70}")
    print(f"SEQUENCE: {sequence}")
    print(f"{'='*70}")
    
    # Try different decodings
    print(f"\n[1] As ASCII (2-digit):")
    for i in range(0, len(sequence)-1, 2):
        try:
            code = int(sequence[i:i+2])
            if 32 <= code <= 126:
                print(f"  {sequence[i:i+2]} = {chr(code)}")
        except:
            pass
    
    print(f"\n[2] As Morse (7=., 8=-, *=sep):")
    if '*' in sequence:
        parts = sequence.split('*')
        morse_to_char = {
            '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
            '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
            '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
            '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
            '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
            '--..': 'Z'
        }
        
        decoded = []
        for part in parts:
            if part:
                morse = part.replace('7', '.').replace('8', '-')
                if morse in morse_to_char:
                    decoded.append(morse_to_char[morse])
                    print(f"  {part} -> {morse} -> {morse_to_char[morse]}")
        
        if decoded:
            result = ''.join(decoded)
            print(f"\n  Decoded: {result}")
            print(f"  Flag: CIT{{{result.lower()}}}")

except Exception as e:
    print(f"Error: {e}")
    print("\nFalling back to simpler method...")

print(f"\n{'='*70}")
