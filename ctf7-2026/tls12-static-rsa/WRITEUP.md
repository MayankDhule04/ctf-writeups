# portal-dmz.pcap — TLS 1.2 "harmless" static-RSA decrypt

## Flag

```
ctf7{n0_f0rw4rd_s3cr3cy_st4t1c_rs4_r3gr3t}
```

## Summary

The ops team's claim that "TLS 1.2 can't hurt anyone" is wrong for two independent
reasons that compound here:

1. Several sessions to `portal.kestrel-freight.example` (10.60.1.20:443) negotiate
   **static RSA key exchange** cipher suites (`TLS_RSA_WITH_AES_256_CBC_SHA` =
   `0x0035`, `TLS_RSA_WITH_AES_128_CBC_SHA` = `0x002f`,
   `TLS_RSA_WITH_AES_128_GCM_SHA256` = `0x009c`) instead of an ephemeral
   (EC)DHE suite. Static RSA key exchange has **no forward secrecy** — the
   pre-master secret (PMS) is simply RSA-encrypted to the server's public key,
   so anyone who later obtains the server's RSA private key can decrypt the
   entire recorded session, even offline, after the fact.
2. The capture itself contains a **plaintext HTTP leak of that exact RSA
   private key**. The same DMZ tap shows an external host (`203.0.113.241`,
   `curl/8.5.0`) directory-brute-forcing the portal over plain HTTP (port 80)
   with `gobuster`, discovering an open `Index of /backup/` listing, and
   downloading `nginx-etc-20261104.tar.gz` — a full backup of
   `/etc/nginx` including `ssl/portal.kestrel-freight.example.key`
   (password-protected PKCS#8, decryptable with a passphrase from the
   accompanying `ssl/global.pass` file) and the matching certificate.

So the "harmless" TLS capture is only harmless if the private key stays
secret — and the same tap shows the key walking out the door in cleartext.

## Stream / session identification

Across the 30-minute capture there are ~50 TCP flows to/from 10.60.1.20:

- Most external "client" sessions from addresses like `198.51.100.x`,
  `203.0.113.x`, `100.x.x.x` negotiate `TLS_ECDHE_RSA_WITH_AES_*_GCM_SHA*`
  (`0xc02f` / `0xc030`) — forward-secret, **not** decryptable even with the
  server's RSA key, and consistent with ordinary/scanner web traffic.
- A cluster of internal loopback-style connections from `10.60.1.2` negotiate
  `0x009c` (static-RSA AES-GCM) but turn out to be lightweight internal
  healthchecks with garbage/placeholder application data (MAC/tag
  verification fails even after correctly decrypting the PMS) — a decoy to
  chase for anyone pattern-matching "static RSA = juicy."
- Three flows to `10.60.40.14/16/25` use `0x002f` (static-RSA AES-128-CBC-SHA)
  but are zero-length/empty application data streams — infrastructure noise,
  not the settlement traffic.
- **Five flows to `192.0.2.45`** use `0x0035` (static-RSA AES-256-CBC-SHA) and
  carry real HTTP application data: `POST /api/v1/settlement/batch` followed
  by `GET /api/v1/settlement/remittance-advice/RA-xxxxxx`, all authenticated
  with HTTP Basic auth as **`nbk-settle`** (the bank partner's settlement
  agent, `User-Agent: Java/1.8.0_92`). These are the real target.

Four of the five `nbk-settle` remittance-advice responses contain mundane
freight/logistics-sounding memo decoys ("Partner hub depot invoice pickup.",
"Pallet forecast batch exception shipment.", etc.) planted to look plausible
to a quick skim. The fifth — advice `RA-057157`, batch `SB-78784453`, TCP
session `10.60.1.20:443 <-> 192.0.2.45:33184` (wire IP in the capture:
`192.0.2.45:45059` at `t0=1793874335.88`, i.e. ~10:25 into the capture) —
returns the actual flag as its `memo` field.

## Key recovery and decryption method

1. Pulled the plaintext HTTP backup `nginx-etc-20261104.tar.gz` out of the
   `203.0.113.241 -> 10.60.1.20:80` stream (strip the HTTP response header,
   gunzip the body, `tar` extract).
2. The archive's `etc/nginx/ssl/README` documents two keys: the currently
   deployed key/cert (renewed Oct 2026) and a retained previous key/cert
   (2025), both PKCS#8-encrypted, with candidate passphrases listed in
   `etc/nginx/ssl/global.pass`.
3. Loaded both encrypted keys with `cryptography`'s
   `serialization.load_pem_private_key`, trying each passphrase; confirmed
   which key matches which certificate by comparing RSA modulus (`n`) between
   decrypted private key and each `.crt` file's public key. The **current**
   key (`Bollard-Lighthouse-2026-66!`) is the one actually presented in the
   capture's `Certificate` handshake messages (not the retired 2025 key).
4. For each static-RSA TLS flow, parsed the TCP-reassembled byte stream as
   raw TLS records (pure `struct`-style slicing, no tshark/pyshark needed):
   extracted `ClientHello.random`, `ServerHello.random` +
   `ServerHello.cipher_suite`, and the `ClientKeyExchange` encrypted
   pre-master secret.
5. RSA-PKCS1v15-decrypted the encrypted PMS with the recovered private key
   (`cryptography`'s `key.decrypt(enc_pms, padding.PKCS1v15())`), validating
   the result as a well-formed 48-byte PMS with TLS version bytes `03 03`.
6. Implemented the TLS 1.2 PRF (`HMAC-SHA256`-based, per RFC 5246 §5) in pure
   Python (`hmac`/`hashlib`) to derive `master_secret` from the PMS and both
   randoms, then derived the `key_block` (MAC keys + encryption keys + IVs
   for CBC suites, or GCM fixed-IV, for AEAD suites) via the same PRF with
   label `"key expansion"`.
7. Decrypted each `ApplicationData` (TLS record type 23) record: for
   `0x0035`/`0x002f` (CBC+HMAC-SHA1) — AES-CBC decrypt with the derived IV
   embedded in the record, strip PKCS#7 padding, strip and validate the
   trailing SHA1 MAC; for `0x009c` (AES-128-GCM) — split the 8-byte explicit
   nonce from the ciphertext/tag, build the per-record AAD from the TLS
   sequence number/content-type/version/length, and `AES.MODE_GCM` decrypt +
   verify the tag.
8. Only the five `192.0.2.45` (`0x0035`) sessions decrypted to coherent,
   MAC-valid JSON/HTTP content; the `10.60.1.2` (`0x009c`) and `10.60.40.x`
   (`0x002f`) static-RSA flows failed MAC/padding checks or were empty,
   confirming they are decoy/noise traffic rather than the real settlement
   channel.

## Flag source record (decrypted)

```
HTTP/1.1 200 OK
Server: nginx
Date: Thu, 05 Nov 2026 10:15:27 GMT
Content-Type: application/json
Content-Length: 158
Connection: keep-alive

{"advice":"RA-057157","batch":"SB-78784453","amount":114125.47,"currency":"EUR","value_date":"2026-11-06","memo":"ctf7{n0_f0rw4rd_s3cr3cy_st4t1c_rs4_r3gr3t}"}
```

- Cipher suite: `TLS_RSA_WITH_AES_256_CBC_SHA` (`0x0035`) — static RSA key
  exchange, no forward secrecy.
- Key source: RSA private key recovered from the plaintext-HTTP-leaked
  `/backup/nginx-etc-20261104.tar.gz` nginx config backup
  (`etc/nginx/ssl/portal.kestrel-freight.example.key`, passphrase
  `Bollard-Lighthouse-2026-66!` from the bundled `global.pass`).
- Stream location: TCP flow `10.60.1.20:443 <-> 192.0.2.45:33184`
  (`nbk-settle` Basic-auth credential `5e6165430da3c13ac5`), remittance
  advice `RA-057157` / settlement batch `SB-78784453`, at capture time
  `2026-11-05 10:15:27 GMT`.
