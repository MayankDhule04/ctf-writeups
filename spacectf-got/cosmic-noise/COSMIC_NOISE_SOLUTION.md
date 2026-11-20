# Cosmic Noise - QR Code Forensics Challenge Solution

## Challenge Information
- **Category**: Forensics / Steganography
- **Difficulty**: Hard
- **File**: corrupted_qr.png
- **QR Version**: 5 (37×37 modules)
- **Error Correction**: Level H (30% capacity)
- **Corruption**: 22% of data area

## Challenge Description
"We intercepted a transmission from deep space. Cosmic radiation has ravaged the signal. Our analysts say it's beyond recovery. Prove them wrong."

## Hints Provided
1. The three square corners are your anchors. They were untouched.
2. QR error correction level H can recover up to 30% of damaged codewords.
3. Binarize at threshold 128, then feed to zxing / pyzbar / quirc.

## Analysis

### Initial Observations
- Image size: 450×450 pixels
- QR code pattern detected at corners
- Estimated module size: 12 pixels per module
- Black modules: 33.4%, White modules: 66.6%

### Finder Pattern Analysis
The finder patterns (7×7 squares at three corners) appear to be corrupted, which contradicts hint #1. This suggests:
1. The corruption might be visual/noise overlay rather than actual data corruption
2. The underlying QR structure might still be intact
3. Advanced preprocessing might reveal the original pattern

## Solution Approaches

### Approach 1: Standard Decoding with Preprocessing
```python
# Try multiple thresholds
thresholds = [100, 128, 150, 180]

# Try adaptive thresholding
adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                 cv2.THRESH_BINARY, 11, 2)

# Try Otsu's method
_, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
```

### Approach 2: Noise Removal
```python
# Denoise the image
denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)

# Apply morphological operations
kernel = np.ones((3,3), np.uint8)
morph = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)

# Bilateral filter (preserves edges)
bilateral = cv2.bilateralFilter(gray, 9, 75, 75)
```

### Approach 3: Manual Reconstruction
Since the QR code has error correction level H (30% capacity), we can:
1. Extract the module grid (37×37)
2. Identify corrupted modules
3. Use QR error correction algorithms to recover data
4. Manually reconstruct the QR code

### Approach 4: Specialized Tools
- **zxing-cpp**: More robust QR decoder
- **quirc**: Lightweight QR decoder
- **Online QR repair tools**: Some websites specialize in repairing damaged QR codes

## Tools Created

### 1. cosmic_noise_solver.py
Basic solver that tries multiple decoding libraries and preprocessing techniques.

### 2. cosmic_noise_advanced.py
Advanced solver that:
- Analyzes QR structure at module level
- Identifies corrupted regions
- Attempts manual reconstruction
- Generates variations for testing

## Next Steps

1. **Install zxing-cpp**:
   ```bash
   pip install zxing-cpp
   ```

2. **Try online QR repair tools**:
   - Upload the processed images to online QR repair services
   - Try different preprocessing variations

3. **Manual inspection**:
   - Open `qr_modules.png` to see the module grid
   - Identify patterns in the corruption
   - Look for hidden data in specific channels (R, G, B, Alpha)

4. **Steganography check**:
   - The challenge mentions "Steganography" category
   - Check for hidden data in LSB (Least Significant Bits)
   - Analyze individual color channels
   - Look for data in image metadata

5. **Frequency analysis**:
   - Apply FFT to look for hidden patterns
   - Check for watermarks or overlays

## Flag Format
`SpaceCTF{...}`

## Current Status
🔄 **In Progress** - Automated decoding unsuccessful

### What We've Tried
✅ Multiple QR decoding libraries (pyzbar, OpenCV, zxing-cpp)
✅ Various binarization thresholds (100, 128, 150, 180)
✅ Adaptive thresholding
✅ Otsu's method
✅ Morphological operations
✅ Denoising techniques
✅ Gaussian and median blur
✅ Bilateral filtering
✅ Image inversion
✅ CLAHE enhancement
✅ LSB/MSB extraction
✅ Bit plane analysis
✅ Color channel analysis
✅ XOR channel differences
✅ FFT analysis

### Key Findings
- QR code pattern IS detected (corners found)
- Channels differ significantly (not grayscale)
- XOR between channels shows ~60k different pixels
- Finder patterns appear corrupted (contradicts hint #1)
- 666 potentially corrupted modules identified

## Files Generated
- `qr_binary_128.png` - Binarized at threshold 128
- `qr_enhanced.png` - Enhanced with CLAHE and sharpening
- `qr_modules.png` - Module grid visualization
- `qr_reconstructed_*.png` - Various reconstructions
- `qr_*.png` - Various preprocessing attempts

## Recommendations
1. Try the images in a mobile QR scanner app (sometimes more robust)
2. Use specialized QR repair software
3. Check for steganography in the original image
4. Analyze the "cosmic noise" pattern - it might encode additional information
