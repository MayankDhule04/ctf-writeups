#!/usr/bin/env python3
"""
Dog Barking - Extract and enhance text region from spectrogram
"""

import wave
import numpy as np
from scipy import signal
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

wav_file = "dog.wav"

print("="*70)
print("DOG BARKING - TEXT REGION EXTRACTION")
print("="*70)

# Read WAV file
with wave.open(wav_file, 'rb') as wav:
    frames = wav.readframes(wav.getnframes())
    sample_rate = wav.getframerate()

audio_data = np.frombuffer(frames, dtype=np.int16)

# Generate very high resolution spectrogram
print(f"\n[1] Generating ultra-high resolution spectrogram...")
frequencies, times, Sxx = signal.spectrogram(
    audio_data,
    fs=sample_rate,
    window='hann',
    nperseg=4096,  # Very high resolution
    noverlap=3584
)

# Convert to dB
Sxx_db = 10 * np.log10(Sxx + 1e-10)

# Focus on typical text frequency range (5-7kHz is common)
freq_ranges = [
    (4000, 6000),
    (5000, 7000),
    (6000, 8000),
    (3000, 5000)
]

for freq_min, freq_max in freq_ranges:
    print(f"\n[2] Processing {freq_min}-{freq_max}Hz range...")
    
    freq_min_idx = np.argmin(np.abs(frequencies - freq_min))
    freq_max_idx = np.argmin(np.abs(frequencies - freq_max))
    
    text_region = Sxx_db[freq_min_idx:freq_max_idx, :]
    
    # Normalize
    text_norm = (text_region - text_region.min()) / (text_region.max() - text_region.min())
    
    # Create high contrast binary image
    # Try multiple thresholds
    for threshold in [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]:
        binary = (text_norm > threshold).astype(float)
        
        # Save as black and white image
        plt.figure(figsize=(30, 4))
        plt.imshow(binary, aspect='auto', cmap='gray_r', origin='lower', interpolation='nearest')
        plt.axis('off')
        plt.tight_layout(pad=0)
        
        filename = f'dog_text_{freq_min}_{freq_max}_t{int(threshold*10)}.png'
        plt.savefig(filename, dpi=200, bbox_inches='tight', pad_inches=0, facecolor='white')
        plt.close()
        
        # Count white pixels
        white_pixels = np.sum(binary)
        total_pixels = binary.size
        white_pct = (white_pixels / total_pixels) * 100
        
        if 1 < white_pct < 30:  # Reasonable amount of content
            print(f"  Saved: {filename} ({white_pct:.1f}% white)")

print(f"\n[3] Created high-contrast images")
print(f"  Look for files: dog_text_*.png")
print(f"  These are optimized for text visibility")

# Also create an inverted version (white on black)
print(f"\n[4] Creating inverted versions...")
freq_min, freq_max = 5000, 7000
freq_min_idx = np.argmin(np.abs(frequencies - freq_min))
freq_max_idx = np.argmin(np.abs(frequencies - freq_max))
text_region = Sxx_db[freq_min_idx:freq_max_idx, :]
text_norm = (text_region - text_region.min()) / (text_region.max() - text_region.min())

for threshold in [0.5, 0.6]:
    binary = (text_norm > threshold).astype(float)
    
    # White on black
    plt.figure(figsize=(30, 4))
    plt.imshow(binary, aspect='auto', cmap='gray', origin='lower', interpolation='nearest')
    plt.axis('off')
    plt.tight_layout(pad=0)
    
    filename = f'dog_text_inverted_t{int(threshold*10)}.png'
    plt.savefig(filename, dpi=200, bbox_inches='tight', pad_inches=0, facecolor='black')
    plt.close()
    print(f"  Saved: {filename}")

print(f"\n{'='*70}")
print(f"NEXT: Open the dog_text_*.png files and look for readable text")
print(f"The flag should be visible as text in one of these images")
print(f"{'='*70}")
