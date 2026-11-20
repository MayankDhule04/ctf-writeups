#!/usr/bin/env python3
"""
The Shield of Achilles - Audio Steganography Solver
Challenge: Listen to the forge, uncover layers, reveal what's hidden
"""

import numpy as np
from scipy.io import wavfile
import matplotlib.pyplot as plt

def analyze_forge():
    """Analyze the_forge.wav for hidden data"""
    
    print("="*60)
    print("The Shield of Achilles - Audio Analysis")
    print("="*60)
    
    # Read audio file
    sample_rate, data = wavfile.read('the_forge.wav')
    
    if len(data.shape) > 1:
        data = data[:, 0]  # Convert to mono
    
    print(f"\n[*] Sample rate: {sample_rate} Hz")
    print(f"[*] Duration: {len(data) / sample_rate:.2f} seconds")
    print(f"[*] Total samples: {len(data)}")
    
    # Analyze frequency content
    print("\n[*] Analyzing frequency spectrum...")
    fft = np.fft.fft(data)
    freqs = np.fft.fftfreq(len(fft), 1/sample_rate)
    magnitude = np.abs(fft)
    
    # Find dominant frequencies
    positive_freqs = freqs[:len(freqs)//2]
    positive_mag = magnitude[:len(magnitude)//2]
    
    # Get top 10 frequencies
    top_indices = np.argsort(positive_mag)[-10:][::-1]
    print("\n[*] Top 10 frequencies:")
    for idx in top_indices:
        freq = positive_freqs[idx]
        mag = positive_mag[idx]
        if freq > 0:
            print(f"  {freq:.2f} Hz (magnitude: {mag:.0f})")
    
    # Check for spectrogram patterns
    print("\n[*] Creating spectrogram...")
    plt.figure(figsize=(15, 8))
    
    plt.subplot(3, 1, 1)
    plt.plot(np.linspace(0, len(data)/sample_rate, len(data)), data)
    plt.title('Waveform')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    
    plt.subplot(3, 1, 2)
    plt.specgram(data, Fs=sample_rate, cmap='viridis')
    plt.title('Spectrogram')
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')
    plt.colorbar(label='Intensity (dB)')
    
    plt.subplot(3, 1, 3)
    plt.magnitude_spectrum(data, Fs=sample_rate)
    plt.title('Frequency Spectrum')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude')
    
    plt.tight_layout()
    plt.savefig('forge_analysis.png', dpi=300)
    print("[+] Saved spectrogram to forge_analysis.png")
    
    # Look for LSB in audio
    print("\n[*] Checking for LSB steganography...")
    lsb_bits = [sample & 1 for sample in data]
    
    # Convert bits to bytes
    bytes_data = []
    for i in range(0, len(lsb_bits) - 7, 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | lsb_bits[i + j]
        bytes_data.append(byte)
    
    lsb_data = bytes(bytes_data)
    
    # Look for flag pattern
    import re
    text = lsb_data.decode('utf-8', errors='ignore')
    
    flag_patterns = [
        r'BPCTF\{[^\}]+\}',
        r'bpctf\{[^\}]+\}',
        r'flag\{[^\}]+\}',
    ]
    
    for pattern in flag_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            print(f"\n[+] FOUND FLAG IN LSB: {matches[0]}")
            return matches[0]
    
    # Check for Morse code patterns
    print("\n[*] Checking for Morse code...")
    # Analyze amplitude changes
    threshold = np.mean(np.abs(data))
    binary_signal = (np.abs(data) > threshold).astype(int)
    
    # Look for patterns
    changes = np.diff(binary_signal)
    print(f"[*] Signal changes: {np.sum(np.abs(changes))}")
    
    # Try DTMF tones
    print("\n[*] Checking for DTMF tones...")
    dtmf_freqs = {
        (697, 1209): '1', (697, 1336): '2', (697, 1477): '3',
        (770, 1209): '4', (770, 1336): '5', (770, 1477): '6',
        (852, 1209): '7', (852, 1336): '8', (852, 1477): '9',
        (941, 1209): '*', (941, 1336): '0', (941, 1477): '#',
    }
    
    # Analyze in windows
    window_size = int(sample_rate * 0.05)  # 50ms windows
    for i in range(0, len(data) - window_size, window_size):
        window = data[i:i + window_size]
        window_fft = np.fft.fft(window)
        window_freqs = np.fft.fftfreq(len(window_fft), 1/sample_rate)
        window_mag = np.abs(window_fft)
        
        # Find peaks
        peaks = []
        for freq_pair, digit in dtmf_freqs.items():
            f1, f2 = freq_pair
            idx1 = np.argmin(np.abs(window_freqs - f1))
            idx2 = np.argmin(np.abs(window_freqs - f2))
            
            if window_mag[idx1] > np.mean(window_mag) * 5 and window_mag[idx2] > np.mean(window_mag) * 5:
                peaks.append(digit)
        
        if peaks:
            print(f"  Time {i/sample_rate:.2f}s: {peaks}")
    
    print("\n[*] Check forge_analysis.png for visual patterns")
    print("[*] The flag might be visible in the spectrogram!")

if __name__ == "__main__":
    analyze_forge()
