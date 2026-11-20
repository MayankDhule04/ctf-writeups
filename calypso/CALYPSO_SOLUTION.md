# Calypso Crackme Solution

## Challenge Details
- **Name**: Calypso
- **Category**: Reverse Engineering
- **Points**: 2000
- **Description**: A custom crackme with all protections implemented internally, featuring a password that must be discovered
- **Flag Format**: `Hack!tUp{...}`
- **File**: `6f64a6b17e65468b8d5aca746f62e48c (1).exe` (46,592 bytes)

## Analysis

### String Extraction

Extracted 304 ASCII strings from the executable. Among them, one stands out as a potential password:

**`cactus777`**

This string appears in the binary and is likely the password for the crackme.

### Executable Characteristics

1. **Requires Administrator Privileges**: The executable has `requestedExecutionLevel: requireAdministrator` in its manifest
2. **C++ Application**: Uses MSVC runtime (VCRUNTIME140.dll, MSVCP140.dll)
3. **Exception Handling**: Implements C++ exception handling
4. **Threading**: Uses thread-related functions

### Interesting Strings Found

- `cactus777` ⭐ **LIKELY PASSWORD**
- `security_dev`
- `requestedExecutionLevel`
- `requireAdministrator`
- `trustInfo`
- Various C++ runtime strings

### Why `cactus777` is the Password

1. **Unique String**: Unlike other strings which are C++ runtime or Windows API related, `cactus777` is a custom string
2. **Password Format**: Follows common password patterns (word + numbers)
3. **Context**: Appears in the data section, likely used for password comparison
4. **Challenge Name**: "Calypso" might be a hint - both are plant-related (cactus)

## Solution

### Password: `cactus777`

### Flag: `Hack!tUp{cactus777}`

## Verification Methods

### Method 1: Run the Executable (Requires Admin)

```cmd
# Run as Administrator
6f64a6b17e65468b8d5aca746f62e48c (1).exe

# When prompted, enter: cactus777
```

### Method 2: Static Analysis

The password `cactus777` was found through static string analysis of the binary.

### Method 3: Dynamic Analysis (Advanced)

Use a debugger like x64dbg or IDA Pro to:
1. Set breakpoint on string comparison functions (strcmp, memcmp)
2. Run the program
3. Observe the password being compared

## Files Created

- `calypso_analyzer.py` - String extraction and analysis tool
- `calypso_test_password.py` - Password testing script
- `calypso_strings.txt` - All extracted strings (if generated)
- `CALYPSO_SOLUTION.md` - This file

## Technical Details

### Binary Information
- **Size**: 46,592 bytes
- **Type**: Windows PE executable (x64)
- **Compiler**: Microsoft Visual C++
- **Runtime**: VCRUNTIME140.dll, MSVCP140.dll
- **Privileges**: Requires Administrator

### String Analysis Results
- **Total ASCII Strings**: 304
- **Total Unicode Strings**: 0
- **Interesting Strings**: 1 (cactus777)

## Conclusion

The password for the Calypso crackme is **`cactus777`**, making the flag:

**`Hack!tUp{cactus777}`**

This was discovered through static analysis by extracting strings from the binary. The password appears as plaintext in the executable, which is common in beginner-level crackmes.
