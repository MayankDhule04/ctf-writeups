# between_the_lines.txt: round 3 findings

Result: no flag recovered. No mechanism tested produced a `ctf7{...}` string.

Scratch scripts are in `work/`. `work/load.py` is the shared loader. `work/brute3.py` is `refchal/brute2.py` with about 40 extra key strings.

## File re-verification (briefing items 1, 2, 4, 6)
- The file is 4408 bytes, identical to `f.bin`. It contains only printable ASCII plus 313 TAB and 83 LF characters. There are no bytes above 0x7E, no CR and no zero-width or other Unicode characters. The file ends with `\n`.
- Every row matches `^. \| \S+ +\| \S`. The K field is always 2 characters wide and the TERM field is always 11, matching the 11 dashes. Every row has exactly 2 pipes. There are no double spaces inside notes. Every row ends with exactly 8 tab/space characters. Column spacing therefore carries no data. The only double spaces in the file are in the header (`GLOSSARY  v5  (`).
- Line lengths range from 43 to 64 and depend only on term and note length.

## Whitespace payload (77 rows x 8 bits) is statistically uniform
- The 77 row bytes take 69 distinct values. Uniform random bytes would give about 66.6 distinct values, so this is what randomness looks like.
- The 77x8 bit matrix has full GF(2) rank 8, also after an affine shift. It is not a [8,4] Hamming or any other linear code.
- Linear-dependency test: own row bits + K bits + constant has rank 16 of 17, and the only dependency is K's always-zero bit 7. Own + next row has rank 17 of 17. Own + next + K bits of both rows has rank 31 of 33, again only K's constant bits. Three consecutive rows have rank 25 of 25. So no GF(2)-linear decode using the same/adjacent rows, any bit permutation, or K produces a constant high bit. That excludes ASCII output from every XOR, differential or bit-permutation scheme.
- Range test: ASCII plaintext minus an ASCII key, mod 256, can only give bytes in 0..94 or 162..255. The ciphertext has 17 to 21 bytes inside 95..161 under every mapping. So add/sub with any ASCII key (K or anything else) is also impossible.
- Longest run of rows with a 0 high bit is at most 7 under any mapping, so no contiguous ASCII-XOR-ASCII flag segment exists either.
- Conclusion: the whitespace is either noise or encrypted with a high-entropy keystream (hash, PRNG or cipher) whose key we have not found.

## New tests in this round (all negative)
- Raw deflate, zlib and gzip on ct, ct^K, ct-K, K-ct, ct^rev(K), each forward and reversed, for all 4 tab/space and MSB/LSB mappings.
- AEAD with tag verification: AES-GCM, AES-EAX and ChaCha20-Poly1305 with nonce lengths 8/12/16 and layouts nonce|ct|tag, nonce|tag|ct and tag|nonce|ct. Also NaCl SecretBox (24-byte nonce + 16-byte MAC + 37-byte message) and XChaCha20-Poly1305. Keys came from sha256, md5, sha1, blake2b, sha3, raw/padded bytes and PBKDF2 (1 to 100k iterations, 3 salts) of 17 K-derived and hint strings. No tag verified.
- Python `random.Random(seed)` for integer seeds 0..199999 (randbytes, randrange, getrandbits, randint) against the known prefix `ctf7{`.
- UUIDv5 keystreams (prompted by the `v5` in the header) over 4 namespaces, 10 names and 4 modes.
- Per-row keystream from row content: md5, sha1, sha256, sha512, blake2b, sha3, crc32, and HMAC keyed with K or K[5:], each over 10 row-text variants (full row, term, note, term+note, K-prefix and others), bytes 0..3 and -1, with xor/sub/rsub. I checked for `ctf` anywhere and for more than 52 printable bytes.
- Whitespace as a checksum of the row: equality with any byte of 11 hashes (including 3 CRC-8 polynomials) over 12 text variants. The best score was 5/77, which is chance level.
- Nonlinear per-row ops with K: multiply and its modular inverse, rotate by K or by the row index combined with XOR, mod 257, and ±i±K.
- Chaining modes (for the "holds state between calls" hint): prefix XOR, prefix sum, difference, CBC/CFB/OFB-like XOR and add/sub autokey with K or reversed K, forward and reversed.
- Row permutations i*s+o mod 77 for every stride s coprime to 77 and every offset o, in row-major and column-major order, 7/8-bit, both polarities and bit orders: no `ctf` anywhere.
- Linked-list and index views: byte mod 77 is not a permutation. Bytes as indices into K, the visible file, or the visible file without spaces gave nothing.
- One bit per row: bit (a*f+c) mod 8 for features f (row index, K, term/note/line length, word count, popcount); parity(ws & K), bit selected by K, ws > K. Nothing.
- SNOW-style "spaces before each tab" 3-bit groups, per row and concatenated. Runs reach 10 spaces, so the format does not fit.
- 7-bit packed stream (88 symbols) XOR, sub or rsub with K, reversed K and K[5:] cycled. Nothing.
- Per-phrase transforms (18 note base phrases x 32 rotate/reverse/invert transforms, plain and XOR K): no consistent group.
- Visible acrostics: characters 0..5, -1, -2 and -3 of term, note and row, plus the first letters of note words. All noise.
- Term '2' suffix as 77 bits, 5/6/7/8-bit groups at all offsets, both polarities and directions. Noise. The suffix is not a dedupe marker either: X2 often appears before X, for example bucket2 at row 9 and bucket at row 68.
- Keyed brute force (brute3.py: hash keystreams, RC4, ChaCha, Salsa, AES-CTR/OFB/CFB, Python random) with about 517 key strings. The new strings include `r34d_b3tw33n_th3_l1n3s`, `read between the lines`, `st0p_r34d1ng_th3_f1rst_c0lumn`, `CHANNEL GLOSSARY  v5`, `v5`, `techvisions`, `TVX` and `the key hides in plain sight`. No hit.

## Visible channels summarized
- There are 18 note base phrases with counts 2 to 8. Modifiers are 82 words from {aside 16, again 14, once 12, inline 11, twice 11, later 10, here 8}. Modifier counts per row are 0: 25, 1: 22, 2: 30. 39 of 77 terms carry the '2' suffix. Nothing decodes.

## Assessment / what is needed
The visible text looks randomly generated, and the K column is a self-declared decoy. The whitespace payload is uniformly random. Every key that can be derived from the file has failed, as has every structural decode. The most likely missing piece is information outside the file, such as the challenge description or a hint on the CTF platform (e.g. a key, a cipher name, or a "1 row per channel" explanation). Next steps:
1. Get the exact challenge description, any hints, and the attachment list from the platform (ctf-techvisions.com, through `./dl.sh`, which gets past Cloudflare). Check whether another file belongs with this one.
2. If the description names a key or passphrase, run it through `work/brute3.py`: add it to `base` and run from `/projects/sandbox/refchal`.
