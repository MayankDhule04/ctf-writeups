# Corvane ci-runner-02 exfil (Networking, 150 pts, Easy)

**Flag:** `ctf7{p1ng_p4yl04ds_c4rry_m0r3_th4n_t1m3st4mps}`

## How the passphrase left

The channel was ICMP tunneling: the data rode inside ping (echo request) payloads.

1. At t=1762851886.9, ci-runner-02 (10.13.37.52) resolved `edge-telemetry.cdn-metrics.net`, which returned A `203.0.113.66`. That was the only non-routine DNS name the runner looked up.
2. Over the next ~35 s it sent 42 ICMP echo requests (56-byte payload, the normal `ping` size) to 203.0.113.66. The remote host echoed them back, so to the firewall it looked like an ordinary ping.
3. Normal pings in this capture carry the timeval followed by the incrementing pattern `\x10\x11...`. These pings kept the 16-byte timeval and replaced the rest with:
   - bytes 16-17: chunk index (big-endian, 0..36)
   - bytes 18-19: `0x0025` = 37 total chunks
   - bytes 20-55: 36 bytes of data (the last chunk is 21 bytes)
   - 5 chunks were retransmitted (identical duplicates), so 42 packets carry 37 chunks.
4. Reassembling the chunks gives 1317 bytes of high-entropy data. XOR against the gzip magic `1f 8b` gives key `0xe3` for both bytes. Single-byte XOR with 0xe3 produces a gzip stream whose original filename is `.env.production`.
5. Decompressing gives `/opt/actions-runner/.env.production`, which contains
   `RELEASE_SIGNING_PASSPHRASE=ctf7{p1ng_p4yl04ds_c4rry_m0r3_th4n_t1m3st4mps}`.

I ruled out the other allowed protocols. The runner's NTP packets are standard 48-byte client requests sent every 64 s. Its DNS queries are all to ordinary hostnames (debian, github, ghcr, pypi). Its TLS ClientHellos go to normal CDN IPs.

## Files
- `solve.py`: reproducible extraction (scapy)
- `blob.bin`: reassembled XORed data; `payload.gz`: after XOR; `payload.bin`: the decompressed .env
