# CTF7 (2026) — Solve Index

Challenges from the CTF7 platform event (flag format `ctf7{...}`), solved across a
single long session. Each folder holds the writeup/findings and, where applicable,
the working solver/exploit script.

## Solved

| Folder | Category | Flag |
|---|---|---|
| `lift-station-rtu/` | Networking / ICS (Modbus) | `ctf7{h4nd_m0d3_m41nt_k3y_dump_th3_pl4nt_31796b36}` |
| `line-break-news/` | Web | `ctf7{a_bare_line_feed_fixed_the_editors_session_b201f495}` |
| `san-fabric-switch/` | Networking (SNMP) | solved interactively by the user; flag not captured in session transcript |
| `the-house-vm/` | Reversing (custom VM) | `ctf7{h4nd_r0ll3d_vm_s3lf_d3crypt1ng_d4t4_d3p3nd3nt_0ps_r3v3rs3d}` |
| `orca2-leaked-docx/` | Forensics (docx tracked changes) | `ctf7{tr4ck3d_ch4ng3s_r3m3mb3r_wh4t_y0u_d3l3t3d}` |
| `pyxis-sandbox/` | Pwn (integer-truncation overflow) | `ctf7{pyx1s_1nt_0v3rfl0w_d1sp4tch_h1j4ck}` |
| `hsm-lite/` | Crypto (Ed25519 key substitution) | `ctf7{one_nonce_two_pubkeys_zero_secrets}` |
| `cloudgate-oidc/` | Cloud / IAM (path-normalization bypass) | `ctf7{01dc_14m_sub_cl41m_w1ldc4rd_pwn}` |
| `blockhouse-jwt/` | Crypto (JWT `kid` path traversal) | `ctf7{kid_traversal_to_a_null_hmac_key}` |
| `helmflux-ssti/` | DevSecOps (Helm `tpl` SSTI) | `ctf7{h3lm_tpl_f1l3s_g3t_sst1_3xf1ltr4t10n}` |
| `palette-tar-symlink/` | Misc (tar symlink extraction) | `ctf7{a_link_planted_early_steers_every_write_after}` |
| `ping-exfiltration/` | Networking (ICMP tunneling, pcap forensics) | `ctf7{p1ng_p4yl04ds_c4rry_m0r3_th4n_t1m3st4mps}` |
| `tls12-static-rsa/` | Networking (TLS 1.2 static-RSA decrypt, pcap forensics) | `ctf7{n0_f0rw4rd_s3cr3cy_st4t1c_rs4_r3gr3t}` |
| `northwind-graphql-mfa/` | Web (GraphQL aliasing rate-limit bypass) | `ctf7{one_request_a_thousand_guesses}` |
| `harborlight-unicode/` | Web (casefold/NFKC ordering bug) | `ctf7{casefold_then_nfkc_is_not_idempotent}` |
| `cosigngate-key-confusion/` | DevSecOps (JWT alg confusion) | `ctf7{c0s1gn_4tt3st4t10n_k3y_c0nfu510n_f0rg3ry}` |

## Blocked / unsolved (kept for reference)

| Folder | Category | Status |
|---|---|---|
| `kustomize-lfi-blocked/` | DevSecOps | `/api/v1/sync` confirmed a static facade; real vector never found |
| `kubeadmission-blocked/` | DevSecOps | Real admission-bypass bugs confirmed (case-sensitivity, type-confusion, scope gaps); flag-trigger mechanism never found |
| `envoymesh-blocked/` | DevSecOps (mTLS/SPIFFE), 500pts Hard | `/mesh/api/v1/forward` confirmed a complete facade; likely needs raw TLS-layer interaction, not HTTP |
| `meter-flutter-seal/` | Reversing (Flutter/Dart AOT) | Full static RE done (flag prefix, integrity check, navigation model); per-launch dynamic flag requires live app execution — got the app running headlessly in-sandbox but the recalled navigation path gives DRIFT not MATCH; needs the exact original tap sequence |
| `heapnotes-pwn-blocked/` | Pwn (heap, glibc 2.35), 500pts Hard | Full House-of-Einherjar chain independently reproduced live (off-by-one null overflow → backward consolidation → safe-linked heap leak → tcache-poisoned overlap) per 3 purchased hints; missing only the admin control block's heap offset (no binary available) |
| `between-the-lines-stego-blocked/` | Steganography, 700pts Expert | First-column decoy confirmed; trailing-whitespace channel confirmed present but statistically indistinguishable from random bytes under every tested cipher/key; likely needs a hint or second file not yet obtained |

## Common techniques seen this event

- Decoy flags everywhere: static `ctf7{...}`-shaped strings sitting in page info boxes,
  `robots.txt`-disclosed "crawler trap" files, and self-describing strings
  (`..._not_the_flag...`, `..._wont_help_you...`) are a deliberate, recurring pattern.
  Always verify a flag is produced by the challenge's own described mechanism.
- Several challenges explicitly claim a defense is solid ("protected against header
  injection", "Secure Sandboxed Mode", "signing key never leaves memory", "path-traversal
  bug has been fixed") — in every single case this session, the claim was narrowly true
  and the actual bug was an adjacent gap, not a direct contradiction of the claim.
- A shared platform-level HTTP 451 "acknowledgement gate" appears on many challenges on
  host `91.99.207.116`, requesting `POST /api/acknowledge` (empty body, unconditional 200,
  sets `ctf_ack=human-participant` cookie) before the real challenge page is reachable.
