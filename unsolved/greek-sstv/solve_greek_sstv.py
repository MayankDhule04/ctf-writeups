#!/usr/bin/env python3
"""
GREEK.wav Steganography Solver
Comprehensive analysis for flag extraction
"""

import numpy as np
import matplotlib.pyplot as plt
import scipy.io.wavfile as wav
import librosa
import librosa.display
import cv2
from scipy import signal

class GreekWavSolver:
    def __init__(self):
        self.sample_rate, self.audio_data = wav.read('new challeneg/GREEK.wav')
        print(f"[*] Loaded GREEK.wav: {len(self.audio_data)} samples at {self.sample_rate} Hz")
        print(f"[*] Duration: {len(self.audio_data) / self.sample_rate:.2f} seconds")
        
        if len(self.audio_data.shape) > 1:
            print(f"[*] Channels: {self.audio_data.shape[1]} (stereo)")
            self.is_stereo = True
        else:
            print("[*] Channels: 1 (mono)")
            self.is_stereo = False
    
    def analyze_spectrogram(self):
        """Create detailed spectrogram analysis"""
        print("\n=== SPECTROGRAM ANALYSIS ===")
        
        # Convert to mono if stereo
        if self.is_stereo:
            audio_mono = np.mean(self.audio_data, axis=1)
        else:
            audio_mono = self.audio_data
        
        # High-resolution spectrogram
        D = librosa.amplitude_to_db(np.abs(librosa.stft(audio_mono.astype(float), n_fft=4096)), ref=np.max)
        
        # Create multiple views
        plt.figure(figsize=(20, 10))
        librosa.display.specshow(D, sr=self.sample_rate, x_axis='time', y_axis='hz', cmap='hot')
        plt.colorbar(format='%+2.0f dB')
        plt.title('GREEK.wav Spectrogram')
        plt.ylim(0, 8000)
        plt.tight_layout()
        plt.savefig('greek_spectrogram.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("[+] Spectrogram saved as 'greek_spectrogram.png'")
        
        # Look for text in spectrogram
        self.extract_spectrogram_text(D)
    
    def extract_spectrogram_text(self, D):
        """Extract text from spectrogram"""
        print("[*] Extracting text from spectrogram...")
        
        # Focus on text-likely frequencies (300-3000 Hz)
        freq_bins = librosa.fft_frequencies(sr=self.sample_rate, n_fft=4096)
        text_start = np.argmin(np.abs(freq_bins - 300))
        text_end = np.argmin(np.abs(freq_bins - 3000))
        
        text_region = D[text_start:text_end, :]
        
        # Enhance for text visibility
        text_enhanced = np.clip((text_region - np.min(text_region)) / 
                               (np.max(text_region) - np.min(text_region)) * 255, 0, 255).astype(np.uint8)
        
        cv2.imwrite('greek_text_region.png', text_enhanced)
        print("[+] Text region saved as 'greek_text_region.png'")
    
    def analyze_lsb(self):
        """LSB steganography analysis"""
        print("\n=== LSB ANALYSIS ===")
        
        # Convert to int16 if needed
        if self.audio_data.dtype == np.int16:
            audio_int = self.audio_data
        else:
            audio_int = (self.audio_data * 32767).astype(np.int16)
        
        # Flatten if stereo
        if self.is_stereo:
            audio_int = audio_int.flatten()
        
        # Try different LSB extraction methods
        for num_bits in [1, 2, 3, 4]:
            print(f"[*] Extracting {num_bits}-bit LSB...")
            
            # Extract bits
            mask = (1 << num_bits) - 1
            extracted_bits = [sample & mask for sample in audio_int]
            
            # Convert to text
            text = self.bits_to_text(extracted_bits, num_bits)
            if text and len(text) > 10:
                print(f"[+] {num_bits}-bit LSB: {text[:100]}...")
                
                if 'TRACEBACK' in text or 'FLAG' in text:
                    print(f"[!] FLAG FOUND in {num_bits}-bit LSB: {text}")
                    return text
    
    def bits_to_text(self, bits, bits_per_sample):
        """Convert bits to text"""
        # Try different interpretations
        for bits_per_char in [8, 7]:
            text_chars = []
            bit_buffer = []
            
            for bit_val in bits:
                # Convert bit_val to binary and add to buffer
                for i in range(bits_per_sample):
                    bit_buffer.append((bit_val >> i) & 1)
                
                # When we have enough bits, convert to character
                while len(bit_buffer) >= bits_per_char:
                    char_bits = bit_buffer[:bits_per_char]
                    bit_buffer = bit_buffer[bits_per_char:]
                    
                    char_val = 0
                    for i, bit in enumerate(char_bits):
                        char_val |= (bit << i)
                    
                    if 32 <= char_val <= 126:
                        text_chars.append(chr(char_val))
                    elif char_val == 0:
                        break
            
            text = ''.join(text_chars)
            if len(text) > 10:
                return text
        
        return None
    
    def analyze_stereo_channels(self):
        """Analyze stereo channels separately"""
        if not self.is_stereo:
            print("\n[*] Audio is mono, skipping stereo analysis")
            return
        
        print("\n=== STEREO CHANNEL ANALYSIS ===")
        
        left = self.audio_data[:, 0]
        right = self.audio_data[:, 1]
        
        # Analyze each channel's LSB
        for channel_name, channel_data in [('Left', left), ('Right', right)]:
            print(f"[*] Analyzing {channel_name} channel LSB...")
            
            bits = [sample & 1 for sample in channel_data.astype(np.int16)]
            
            # Convert to text
            text_chars = []
            for i in range(0, len(bits) - 7, 8):
                byte_val = 0
                for j in range(8):
                    byte_val |= (bits[i + j] << (7 - j))
                
                if 32 <= byte_val <= 126:
                    text_chars.append(chr(byte_val))
                elif byte_val == 0:
                    break
            
            text = ''.join(text_chars)
            if len(text) > 10:
                print(f"[+] {channel_name}: {text[:100]}...")
                
                if 'TRACEBACK' in text:
                    print(f"[!] FLAG FOUND in {channel_name} channel: {text}")
                    return text
        
        # Analyze channel difference
        print("[*] Analyzing channel difference...")
        diff = left - right
        diff_bits = [sample & 1 for sample in diff.astype(np.int16)]
        
        text_chars = []
        for i in range(0, len(diff_bits) - 7, 8):
            byte_val = 0
            for j in range(8):
                byte_val |= (diff_bits[i + j] << (7 - j))
            
            if 32 <= byte_val <= 126:
                text_chars.append(chr(byte_val))
            elif byte_val == 0:
                break
        
        text = ''.join(text_chars)
        if len(text) > 10:
            print(f"[+] Channel difference: {text[:100]}...")
            
            if 'TRACEBACK' in text:
                print(f"[!] FLAG FOUND in channel difference: {text}")
                return text
    
    def analyze_frequency_domain(self):
        """Frequency domain analysis"""
        print("\n=== FREQUENCY DOMAIN ANALYSIS ===")
        
        # Convert to mono
        if self.is_stereo:
            audio_mono = np.mean(self.audio_data, axis=1)
        else:
            audio_mono = self.audio_data
        
        # FFT
        fft_data = np.fft.fft(audio_mono.astype(float))
        freqs = np.fft.fftfreq(len(fft_data), 1/self.sample_rate)
        magnitudes = np.abs(fft_data)
        
        # Find strongest frequencies
        positive_freqs = freqs[:len(freqs)//2]
        positive_mags = magnitudes[:len(magnitudes)//2]
        
        # Get top 20 frequencies
        top_indices = np.argsort(positive_mags)[-20:][::-1]
        
        print("[*] Top 20 frequency components:")
        for idx in top_indices:
            freq = positive_freqs[idx]
            mag = positive_mags[idx]
            print(f"    {freq:.1f} Hz: {mag:.2e}")
    
    def analyze_amplitude_envelope(self):
        """Amplitude envelope analysis"""
        print("\n=== AMPLITUDE ENVELOPE ANALYSIS ===")
        
        # Convert to mono
        if self.is_stereo:
            audio_mono = np.mean(self.audio_data, axis=1)
        else:
            audio_mono = self.audio_data
        
        # Calculate envelope
        envelope = np.abs(signal.hilbert(audio_mono.astype(float)))
        
        # Try different downsampling rates
        for factor in [100, 500, 1000]:
            envelope_ds = envelope[::factor]
            
            # Binary threshold
            threshold = np.mean(envelope_ds)
            binary = (envelope_ds > threshold).astype(int)
            
            # Convert to text
            text = self.binary_to_text(binary)
            if text and len(text) > 10:
                print(f"[+] Envelope (factor {factor}): {text[:100]}...")
                
                if 'TRACEBACK' in text:
                    print(f"[!] FLAG FOUND in envelope: {text}")
                    return text
    
    def binary_to_text(self, binary_data):
        """Convert binary to text"""
        if len(binary_data) < 8:
            return None
        
        text_chars = []
        for i in range(0, len(binary_data) - 7, 8):
            byte_val = 0
            for j in range(8):
                byte_val |= (binary_data[i + j] << (7 - j))
            
            if 32 <= byte_val <= 126:
                text_chars.append(chr(byte_val))
            elif byte_val == 0:
                break
        
        return ''.join(text_chars) if len(text_chars) > 5 else None
    
    def solve(self):
        """Main solving function"""
        print("="*60)
        print("GREEK.WAV STEGANOGRAPHY SOLVER")
        print("="*60)
        
        # Try all analysis methods
        self.analyze_spectrogram()
        result = self.analyze_lsb()
        if result:
            return result
        
        result = self.analyze_stereo_channels()
        if result:
            return result
        
        self.analyze_frequency_domain()
        
        result = self.analyze_amplitude_envelope()
        if result:
            return result
        
        print("\n[*] No flag found in automated analysis")
        print("[*] Check generated spectrogram images for visual clues")

def main():
    solver = GreekWavSolver()
    result = solver.solve()
    
    if result:
        print(f"\n[!] FINAL FLAG: {result}")

if __name__ == "__main__":
    main()