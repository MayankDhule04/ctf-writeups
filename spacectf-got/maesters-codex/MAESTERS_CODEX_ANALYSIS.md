# Maester's Codex - Analysis

## Challenge Description
- **Title:** Maester's Codex
- **Category:** Crypto
- **Flag Format:** `SpaceCTF{..}`
- **File:** cipher.txt

## Clues
1. **Three links in a chain:**
   - Stone (weathered and old)
   - Bronze (rings when struck)
   - Iron (cold black, Northern wind)

2. **Quote:** "Forge your chain link by link, novice. The maesters do not give up their codex to those who skip a single forge."

3. **Description:** "A page from the codex was smuggled out of the Citadel. It has been wrapped in three layers of protection. Strip them off, in the right order, to read what the maesters did not want you to see."

## What We Know

### Cipher Text
```
PIVx3Y<eJWZhC2OAaQ7Obz^WKd2S$3W@UM9a(N(cW?~>}XlY?<ZE<=aa%yOEAar?hdUhajaBgIEE+9!~b!2HEb#8TIVIX5^b#EYPXJ{a1W@c`6AarbGcpzeUVs~k9Aar?da3FMIYItEfAbM$fd1NdgY;S0FZf`6gWMpL^YHNCVE+A29W^*8KW^ZyJX>}lBcynlRbz&fPb!s4bcWoeWZhCiUZy;rEAb50hVr(uTS#xrFYD!N?du?xVX>VV1X?197UwUU>Z)Rd&YG`R;Yi)6QUwUV3dU|~
```

### Successful Decryptions

#### Layer 1: Base85 Decode
```
Nu tlz nnzip qhsucp yn Pfeynry ofb jhiakmqz rjhs tyrzv qpndu. Igudi unuca ciuo igh fffnu tldx bxbwip tynp tbjxa: zizyd, lohuno, dde jkzy. Qifs ofor iu axshqub vuj zwm pnzwho en xtsbl. YsrzjJOH{moqio_siuhj_zg_ofb_jhiakmqz_zglzz}
```

#### Layer 2: ROT13 on Base85 output
```
Ah gym aamvc dufhpc la Csrlael bso wuvnxzdm ewuf glemi dcaqh. Vthqv hahpn pvhb vtu sssah gyqk okojvc glac gowkn: mvmlq, ybuhab, qqr wxml. Dvsf bsbe vh nkfudho ihw mjz camjub ra kgfoy. LfemwWBU{zbdvb_fvhuw_mt_bso_wuvnxzdm_mtymm}
```

**Encrypted Flag:** `LfemwWBU{zbdvb_fvhuw_mt_bso_wuvnxzdm_mtymm}`
**Expected:** `SpaceCTF{...}`

### Layer 3: Unknown

The third layer needs to transform:
- `LfemwWBU` → `SpaceCTF`
- `zbdvb_fvhuw_mt_bso_wuvnxzdm_mtymm` → `?????_?????_??_???_????????_?????`

## Attempted Solutions

1. ✗ Vigenere cipher (tried 50+ keys)
2. ✗ Caesar cipher (all 25 shifts)
3. ✗ Double ROT13
4. ✗ Atbash
5. ✗ Base64 after Base85
6. ✗ Different orderings of Base85/ROT13/Vigenere
7. ✗ Brute force Vigenere keys length 1-3

## Character Analysis

```
L -> S: shift of 7 (or 19 backwards)
f -> p: shift of 10 (or 16 backwards)
e -> a: shift of 4 (or 22 backwards)
m -> c: shift of 10 (or 16 backwards)
w -> e: shift of 18 (or 8 backwards)
W -> C: shift of 20 (or 6 backwards)
B -> T: shift of 18 (or 8 backwards)
U -> F: shift of 15 (or 11 backwards)
```

The shifts are: 19, 16, 4, 10, 18, 20, 8, 15
This corresponds to Vigenere key: **TQEKSUIP**

But this key doesn't work when applied to the entire text!

## Next Steps

1. Maybe the key only applies to the flag portion?
2. Maybe there's a different cipher for the flag vs the message?
3. Maybe the order is completely different?
4. Check if there are any other Game of Thrones themed ciphers
