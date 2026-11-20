#!/usr/bin/env python3
"""
Final Siren's Song Solver
Comprehensive approach combining all analysis methods
"""

import numpy as np
import matplotlib.pyplot as plt
import scipy.io.wavfile as wav
import librosa
from PIL import Image
import binascii
import cv2

class FinalSirensDecoder:
    def __init__(self):
        self.sample_rate, self.audio_data = wav.read('new challeneg/sirens_song_secure.wav')
        self.greek_alphabet = {
            'Α': 1, 'Β': 2, 'Γ': 3, 'Δ': 4, 'Ε': 5, 'Ζ': 6, 'Η': 7, 'Θ': 8, 'Ι': 9, 'Κ': 10,
            'Λ': 11, 'Μ': 12, 'Ν': 13, 'Ξ': 14, 'Ο': 15, 'Π': 16, 'Ρ': 17, 'Σ': 18, 'Τ': 19, 'Υ': 20,
            'Φ': 21, 'Χ': 22, 'Ψ': 23, 'Ω': 24
        }
        
        # Key findings from previous analysis
        self.greek_pattern = [19, 16, 18, 20, 20, 19, 11, 12, 14]  # Τ Π Σ Υ Υ Τ Λ Μ Ξ
        self.key_frequencies = [1000, 1500]  # Κ and Ο frequencies
        
    def analyze_greek_cipher_key(self):
        """Analyze the Greek cipher key image"""
        print("=== ANALYZING GREEK CIPHER KEY ===")
        
        try:
            # Load the Greek cipher key image
            img = cv2.imread('new challeneg/greek_cipher_key.png')
            if img is not None:
                print("[+] Greek cipher key image loaded successfully")
                
                # Convert to grayscale for text extraction
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                
                # Apply threshold to make text more visible
                _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
                
                # Save processed image
                cv2.imwrite('greek_cipher_processed.png', thresh)
                print("[+] Processed cipher key saved as 'greek_cipher_processed.png'")
                
                # Try to extract text patterns
                self.extract_cipher_patterns(thresh)
                
            else:
                print("[!] Could not load Greek cipher key image")
                
        except Exception as e:
            print(f"[!] Error analyzing cipher key: {e}")
    
    def extract_cipher_patterns(self, img):
        """Extract patterns from the cipher key image"""
        print("[*] Extracting cipher patterns...")
        
        # Look for specific patterns in the image
        height, width = img.shape
        
        # Divide image into regions and analyze
        regions = []
        for i in range(0, height, height//4):
            for j in range(0, width, width//4):
                region = img[i:i+height//4, j:j+width//4]
                avg_intensity = np.mean(region)
                regions.append(avg_intensity)
        
        print(f"[*] Image regions average intensities: {[f'{r:.1f}' for r in regions]}")
        
        # Convert intensities to binary pattern
        threshold = np.mean(regions)
        binary_pattern = [1 if r > threshold else 0 for r in regions]
        print(f"[*] Binary pattern from image: {''.join(map(str, binary_pattern))}")
    
    def decode_with_cipher_key(self):
        """Use the Greek pattern as a cipher key"""
        print("\n=== DECODING WITH CIPHER KEY ===")
        
        # The Greek pattern: [19, 16, 18, 20, 20, 19, 11, 12, 14]
        # Try using this as a Vigenère cipher key
        
        # Extract text from LSB of audio
        bits = []
        for sample in self.audio_data:
            bits.append(sample & 1)
        
        # Convert bits to text
        text_candidates = []
        for start_offset in range(0, min(1000, len(bits)), 8):
            try:
                text = ''
                for i in range(start_offset, min(start_offset + 200, len(bits) - 7), 8):
                    byte_val = 0
                    for j in range(8):
                        if i + j < len(bits):
                            byte_val |= (bits[i + j] << (7 - j))
                    if 32 <= byte_val <= 126:
                        text += chr(byte_val)
                    else:
                        break
                
                if len(text) > 10:
                    text_candidates.append((start_offset, text))
                    
            except:
                continue
        
        print(f"[*] Found {len(text_candidates)} text candidates from LSB")
        
        # Apply Greek cipher to each candidate
        for offset, candidate in text_candidates[:5]:  # Check first 5 candidates
            decoded = self.apply_greek_cipher(candidate)
            print(f"[*] Offset {offset}: Original: {candidate[:50]}...")
            print(f"[*] Offset {offset}: Decoded:  {decoded[:50]}...")
            
            if 'TRACEBACK' in decoded:
                print(f"[!] FLAG FOUND: {decoded}")
                return decoded
    
    def apply_greek_cipher(self, text):
        """Apply Greek pattern as Vigenère cipher"""
        result = ''
        key_pos = 0
        
        for char in text:
            if char.isalpha():
                # Get the shift value from Greek pattern
                shift = self.greek_pattern[key_pos % len(self.greek_pattern)]
                
                # Apply Caesar shift
                if char.isupper():
                    result += chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
                else:
                    result += chr((ord(char) - ord('a') - shift) % 26 + ord('a'))
                
                key_pos += 1
            else:
                result += char
        
        return result
    
    def frequency_domain_decode(self):
        """Advanced frequency domain analysis"""
        print("\n=== FREQUENCY DOMAIN DECODING ===")
        
        # Focus on the two key frequencies: 1000Hz (Κ) and 1500Hz (Ο)
        fft_data = np.fft.fft(self.audio_data.astype(float))
        freqs = np.fft.fftfreq(len(fft_data), 1/self.sample_rate)
        
        # Extract phase information at key frequencies
        for freq in self.key_frequencies:
            idx = np.argmin(np.abs(freqs - freq))
            phase = np.angle(fft_data[idx])
            magnitude = np.abs(fft_data[idx])
            
            print(f"[*] {freq}Hz: Phase={phase:.4f}, Magnitude={magnitude:.2f}")
            
            # Convert phase to potential data
            # Phase might encode information
            phase_normalized = (phase + np.pi) / (2 * np.pi)  # Normalize to 0-1
            phase_bits = int(phase_normalized * 255)  # Convert to 8-bit value
            
            print(f"[*] {freq}Hz phase as 8-bit: {phase_bits} (0x{phase_bits:02x}) ('{chr(phase_bits) if 32 <= phase_bits <= 126 else '?'}')")
    
    def spectrogram_text_extraction(self):
        """Extract text from spectrogram using OCR-like approach"""
        print("\n=== SPECTROGRAM TEXT EXTRACTION ===")
        
        # Generate high-resolution spectrogram
        D = librosa.amplitude_to_db(np.abs(librosa.stft(self.audio_data.astype(float), n_fft=8192)), ref=np.max)
        
        # Focus on text-likely frequency ranges (300-3000 Hz)
        freq_bins = librosa.fft_frequencies(sr=self.sample_rate, n_fft=8192)
        text_freq_start = np.argmin(np.abs(freq_bins - 300))
        text_freq_end = np.argmin(np.abs(freq_bins - 3000))
        
        text_region = D[text_freq_start:text_freq_end, :]
        
        # Enhance contrast
        text_region_enhanced = np.clip((text_region - np.min(text_region)) / (np.max(text_region) - np.min(text_region)) * 255, 0, 255).astype(np.uint8)
        
        # Save as image for manual inspection
        plt.figure(figsize=(20, 8))
        plt.imshow(text_region_enhanced, aspect='auto', origin='lower', cmap='hot')
        plt.title('Spectrogram Text Region (300-3000 Hz)')
        plt.savefig('sirens_text_region.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("[+] Text region saved as 'sirens_text_region.png'")
        
        # Try to find patterns that look like text
        self.find_text_patterns(text_region_enhanced)
    
    def find_text_patterns(self, img):
        """Find text-like patterns in the spectrogram"""
        print("[*] Searching for text patterns...")
        
        # Look for horizontal lines (letters)
        horizontal_kernel = np.ones((1, 10), np.uint8)
        horizontal_lines = cv2.morphologyEx(img, cv2.MORPH_OPEN, horizontal_kernel)
        
        # Look for vertical patterns
        vertical_kernel = np.ones((10, 1), np.uint8)
        vertical_lines = cv2.morphologyEx(img, cv2.MORPH_OPEN, vertical_kernel)
        
        # Combine patterns
        combined = cv2.addWeighted(horizontal_lines, 0.5, vertical_lines, 0.5, 0)
        
        # Save pattern analysis
        cv2.imwrite('sirens_text_patterns.png', combined)
        print("[+] Text patterns saved as 'sirens_text_patterns.png'")
        
        # Look for specific letter-like shapes
        self.detect_letter_shapes(combined)
    
    def detect_letter_shapes(self, img):
        """Detect letter-like shapes in the processed image"""
        print("[*] Detecting letter shapes...")
        
        # Find contours
        contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Analyze contours for letter-like properties
        letter_candidates = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if 50 < area < 5000:  # Filter by reasonable letter size
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h
                if 0.2 < aspect_ratio < 3.0:  # Reasonable aspect ratio for letters
                    letter_candidates.append((x, y, w, h, area))
        
        print(f"[*] Found {len(letter_candidates)} potential letter shapes")
        
        # Sort by x position (reading order)
        letter_candidates.sort(key=lambda x: x[0])
        
        # Extract regions for each potential letter
        for i, (x, y, w, h, area) in enumerate(letter_candidates[:20]):  # First 20
            letter_region = img[y:y+h, x:x+w]
            cv2.imwrite(f'sirens_letter_{i:02d}.png', letter_region)
        
        if letter_candidates:
            print(f"[+] Extracted {min(20, len(letter_candidates))} letter regions")
    
    def solve(self):
        """Main solving function"""
        print("="*60)
        print("FINAL SIREN'S SONG SOLVER")
        print("="*60)
        
        # Analyze the Greek cipher key
        self.analyze_greek_cipher_key()
        
        # Try decoding with cipher key
        result = self.decode_with_cipher_key()
        if result:
            return result
        
        # Advanced frequency analysis
        self.frequency_domain_decode()
        
        # Spectrogram text extraction
        self.spectrogram_text_extraction()
        
        print("\n" + "="*60)
        print("FINAL ANALYSIS COMPLETE")
        print("="*60)
        print("[*] Check all generated images for visual clues")
        print("[*] The flag might be hidden in the spectrogram text region")
        print("[*] Look for TRACEBACK{...} pattern in extracted letter shapes")

def main():
    decoder = FinalSirensDecoder()
    decoder.solve()

if __name__ == "__main__":
    main()