# Star Wars Force Challenge Analysis

## Challenge Input
```
May the Force be with you, young padawan.
095 181 145 039 245 091 212 232 123 220 167 069 091 208 245 164 245 145 123 094, 062 150 094 172 083 135 096 153 002 208 096 172. 201 005 019 {131 091 090 053 095 218 238 211 091 004 201 182 135 245 167 074 090 145 096 238}
```

## Analysis

### Key Findings:
1. **Numbers contain 8 and 9** - NOT octal despite the hint
2. **55 decimal numbers** in range 2-245
3. **Flag section** has 20 numbers: `[131, 91, 90, 53, 95, 218, 238, 211, 91, 4, 201, 182, 135, 245, 167, 74, 90, 145, 96, 238]`

### Attempted Approaches:

#### 1. Direct ASCII Conversion
- ❌ Numbers too high (max 245, many > 126)
- Result: Mostly non-printable characters

#### 2. XOR with Single Byte
- ❌ No single-byte XOR key produces readable text
- Tested all 256 possible keys

#### 3. XOR with Star Wars Keywords
- ❌ Tested: FORCE, YODA, JEDI, STAR, WARS, LUKE, VADER, PADAWAN
- None produced readable output

#### 4. Modulo Transformations
- ⚠️ `(n % 94) + 32` gives ~75% readable: `!wSGY{8L=@ie{4YfYS=`
- ⚠️ `(n % 100) + 32` gives 80% readable but still garbled

#### 5. Reverse Engineering
- 🔍 Assuming flag starts with "password" + 7-byte XOR key gives 85% readable
- Key pattern: `[243, 58, 41, 70, 40, 181, 156, 183]`
- Partial decode: `passwor a-..2iTps.H[`

### Current Status: 🔄 IN PROGRESS

The challenge likely uses:
- Multi-byte XOR cipher
- Possibly repeating key
- Key length might be 7-8 bytes

### Next Steps:
1. Try exhaustive multi-byte XOR with key lengths 2-10
2. Analyze the structure (commas, periods, braces) for clues
3. Consider that "May the Force be with you" might be the key itself
4. Try Caesar cipher or other classical ciphers on the numbers
5. Check if numbers represent coordinates or indices

### Files Created:
- `starwars_force_solver.py` - Initial octal attempt
- `starwars_advanced_solver.py` - Multiple strategies
- `starwars_decimal_solver.py` - Decimal interpretation
- `starwars_xor_force.py` - XOR with Star Wars keys
- `starwars_final_solver.py` - Comprehensive approaches
- `starwars_solution.py` - Modulo transformations
- `starwars_reverse_engineer.py` - Known plaintext attack

### Possible Flag Formats:
- `CTF{...}`
- `CIT{...}`
- `FLAG{...}`
- Or custom format based on challenge source
