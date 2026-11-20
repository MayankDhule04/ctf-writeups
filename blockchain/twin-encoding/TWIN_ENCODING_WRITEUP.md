# CTF Writeup: Twin Encoding (DOME CTF 2026 — Operation Nightfall)

- **Challenge Name**: Twin Encoding
- **Event**: DOME CTF 2026 — Operation Nightfall
- **Category**: Cryptography / Web Forensics
- **Flag Format**: `dome.ctf{...}`
- **Flag**: `dome.ctf{whispers:tLiQN499qb3mUWYY1AElkHf}`

---

## 1. Challenge Overview

In a dark-web forum post by user `arcadeghost` (described as a "signed final broadcast"), two mystery ciphertext strings were discovered alongside a cryptic riddle.

### The Ciphertexts
- **String A ("the only current address")** — 105 characters:
  ```text
  5ec6a81xr14i50w1m31e51pv58l5ow6j65bn5ki1gk6nd5ws5jp53g6536lu69v64m1dx6ci67o6i31rd58h5ck1ei59551q5wu5gv5sf
  ```
- **String B ("the recovery verification token")** — 45 characters:
  ```text
  14p4wn54k1dy1b71tt1n751s1kf67950y56c65q6ag680
  ```

### The Riddle
> *"thread recovery seal; the twin encoding mirrors itself; what it names, the light will not reach."*

---

## 2. Reconnaissance & Structural Analysis

1. **Length Factorization:**
   - $\text{len}(A) = 105 = 3 \times 35$
   - $\text{len}(B) = 45 = 3 \times 15$
   - Both strings divide cleanly into 3-character blocks.

2. **Character Set:**
   - Both strings consist solely of Base-36 characters `[0-9a-z]`.
   - Every block starts with a small digit (`1, 4, 5, 6`).

3. **Deconstructing the Riddle:**
   - *"thread recovery seal"*: Contextual hint pointing to String B (a path/token used to recover forum thread data).
   - *"the twin encoding mirrors itself"*:
     - **Twin**: Pairs of input characters (bigrams).
     - **Mirrors itself / Encoding**: A bijective bigram mapping where 2 ASCII characters map to 3 Base-36 characters.
   - *"what it names, the light will not reach"*: Refers to the dark web — specifically a **Tor v3 `.onion` hidden service address**.

---

## 3. Cryptanalysis & The "Twin" Mechanism

A 3-character Base-36 string can represent values up to $36^3 - 1 = 46655$.
Standard printable ASCII encompasses 96 characters (from space `0x20` / 32 to `~` `0x7E` / 126, or inclusive to 127).

Pairs of printable characters (bigrams) produce:
$$96 \times 96 = 9216 \text{ states}$$

Because $9216 \le 46656$, any character pair $(c_1, c_2)$ fits within a 3-character Base-36 representation:

### Encoding
$$\text{value} = (c_1 - 32) \times 96 + (c_2 - 32)$$
Convert $\text{value}$ to Base-36 and zero-pad to 3 characters.

### Decoding
For each 3-character chunk $S$:
$$\text{value} = \text{int}(S, 36)$$
$$c_1 = \text{chr}\left(32 + \lfloor \text{value} / 96 \rfloor\right)$$
$$c_2 = \text{chr}\left(32 + (\text{value} \pmod{96})\right)$$

### Why the First Digit is in $\{1, 4, 5, 6\}$
In Base-36, the first digit is $\lfloor \text{value} / 36^2 \rfloor = \lfloor \text{value} / 1296 \rfloor$.
- For standard URL characters (`h`, `t`, `p`, `/`, letters, digits):
  - ASCII ranges $47 \dots 122$ produce $(c_1 - 32) \in [15, 90]$.
  - Multiplying by 96 yields values between $1440$ and $8640$.
  - Dividing by 1296 gives quotients in $\{1, 2, 3, 4, 5, 6\}$, which clusters heavily into `1`, `4`, `5`, and `6`.

---

## 4. Decoding the Ciphertexts

Applying the decoder to both strings:

### String A:
- 35 triplets $\to$ 70 characters:
  ```text
  http://2cp5k2m73felpx2gsk23dyioljudlrwy2tcrf2eubstwk7ifah42zfyd.onion/
  ```
- **Validation**:
  - Format: Standard HTTP Tor Hidden Service URL.
  - Length: `2cp5k2m73felpx2gsk23dyioljudlrwy2tcrf2eubstwk7ifah42zfyd` is exactly 56 Base-32 characters (Tor v3 ed25519 public key + checksum + version `0x03`).
  - Matches the Tor v3 SHA3-256 checksum rule.

### String B:
- 15 triplets $\to$ 30 characters:
  ```text
  /9b7e42f1c8a63d05/secrets.txt 
  ```
- Stripping trailing pad space gives the recovery endpoint:
  ```text
  /9b7e42f1c8a63d05/secrets.txt
  ```

---

## 5. Exploitation & Flag Retrieval

Combining the path with the target web portal infrastructure (`https://lantern.hackthe.website`):

```bash
curl -s "https://lantern.hackthe.website/9b7e42f1c8a63d05/secrets.txt"
```

### Server Response:
```text
dome.ctf{whispers:tLiQN499qb3mUWYY1AElkHf}
```

---

## 6. Complete Solve Script (`solve_twin.py`)

```python
#!/usr/bin/env python3
import requests

def decode_twin(ciphertext: str) -> str:
    """Decodes bigram Base-36 encoded strings."""
    assert len(ciphertext) % 3 == 0, "Ciphertext length must be a multiple of 3"
    groups = [ciphertext[i:i+3] for i in range(0, len(ciphertext), 3)]
    out = []
    for g in groups:
        val = int(g, 36)
        c1 = chr(32 + (val // 96))
        c2 = chr(32 + (val % 96))
        out.extend([c1, c2])
    return "".join(out)

string_a = "5ec6a81xr14i50w1m31e51pv58l5ow6j65bn5ki1gk6nd5ws5jp53g6536lu69v64m1dx6ci67o6i31rd58h5ck1ei59551q5wu5gv5sf"
string_b = "14p4wn54k1dy1b71tt1n751s1kf67950y56c65q6ag680"

address = decode_twin(string_a)
token_path = decode_twin(string_b).strip()

print(f"[+] Decoded Address   : {address}")
print(f"[+] Decoded Token Path: {token_path}")

target_url = f"https://lantern.hackthe.website{token_path}"
print(f"[+] Fetching flag from {target_url} ...")

try:
    resp = requests.get(target_url, timeout=10)
    print(f"[+] Response Status: {resp.status_code}")
    print(f"[+] Flag:\n{resp.text.strip()}")
except Exception as e:
    print(f"[-] Request failed: {e}")
```
