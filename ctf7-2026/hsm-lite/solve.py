#!/usr/bin/env python3
"""
HSM-lite / vault-signer Ed25519 key-substitution key-recovery exploit.

Vulnerability
=============
HSM-lite's /api/sign endpoint accepts an optional caller-supplied "public_key"
(A) that is spliced directly into the EdDSA hash H(R || A || M) used to
compute S, instead of HSM-lite recomputing A itself from its own secret key.
The server only checks that the supplied A decodes to a valid curve point,
never that A actually equals s*B for the secret scalar s it holds (the
"detached-pk sign API... skip the scalar multiplication" optimization
described in the service banner).

Critically, HSM-lite's nonce r is deterministic and derived ONLY from the
secret key and the message (RFC 8032 standard EdDSA: r = SHA512(prefix||M)),
NOT from A. That means signing the *same* message M twice with two different
caller-supplied public keys A1 != A2 yields two signatures that share the
same R = r*B, but different S:

    S1 = r + H(R||A1||M)*s  (mod L)
    S2 = r + H(R||A2||M)*s  (mod L)

This is two linear equations in two unknowns (r, s). Solving directly
recovers the real secret scalar s used by vault-signer -- a full private
key recovery, not just a one-off forgery. Once s is known, any message
(including the literal VAULT-RELEASE challenge text, which HSM-lite's
/api/sign refuses to sign by policy) can be signed locally and will verify
under vault-signer's real public key with a standard EdDSA verifier.

This matches the "signing core recently tuned for throughput" / "skip the
scalar multiplication" hints: the throughput optimization (caller supplies
A) is what breaks the nonce-independence assumption that keeps EdDSA safe.

Steps
=====
1. GET /api/keys -> real vault-signer public key A_real.
2. POST /api/sign twice with the SAME message, once with public_key=A_real
   (or omitted) and once with public_key=<attacker's own valid curve point>.
   Confirm R matches between the two signatures (same message -> same r).
3. Solve the 2x2 linear system mod L for s (and r), using
   h_i = SHA512(R || A_i || M) mod L as the hash scalar.
4. Verify s*B == A_real (pure python Ed25519 point multiplication) to
   confirm correct key recovery.
5. GET /api/vault/challenge for a fresh challenge/message.
6. Forge a valid signature locally: pick a fresh random r', compute
   R' = r'*B, h' = SHA512(R'||A_real||M) mod L, S' = r' + h'*s mod L.
7. POST /api/vault/release with {"challenge", "signature"} -> flag.
"""
import hashlib
import secrets

import requests
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.exceptions import InvalidSignature

BASE = "http://91.99.207.116:16311"

# --- Ed25519 curve constants / pure-python point math (RFC 8032) ---
P = 2**255 - 19
L = 2**252 + 27742317777372353535851937790883648493
D = -121665 * pow(121666, P - 2, P) % P
BX = 15112221349535400772501151409588531511454012693041857206046113283949847762202
BY = 46316835694926478169428394003475163141307993866256225615783033603165251855960
BASEPOINT = (BX % P, BY % P)


def inv(x):
    return pow(x, P - 2, P)


def point_add(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    x3 = (x1 * y2 + x2 * y1) * inv(1 + D * x1 * x2 * y1 * y2) % P
    y3 = (y1 * y2 + x1 * x2) * inv(1 - D * x1 * x2 * y1 * y2) % P
    return (x3, y3)


def point_mul(s, point):
    result = (0, 1)
    while s > 0:
        if s & 1:
            result = point_add(result, point)
        point = point_add(point, point)
        s >>= 1
    return result


def encode_point(point):
    x, y = point
    out = bytearray(y.to_bytes(32, "little"))
    out[31] = (out[31] & 0x7F) | ((x & 1) << 7)
    return bytes(out)


def h_scalar(r_bytes, a_bytes, msg):
    digest = hashlib.sha512(r_bytes + a_bytes + msg).digest()
    return int.from_bytes(digest, "little") % L


def forge_signature(msg_bytes, secret_scalar, pubkey_bytes):
    r = secrets.randbelow(L)
    big_r = encode_point(point_mul(r, BASEPOINT))
    h = h_scalar(big_r, pubkey_bytes, msg_bytes)
    big_s = (r + h * secret_scalar) % L
    return big_r + big_s.to_bytes(32, "little")


def main():
    keys = requests.get(BASE + "/api/keys").json()
    real_pk_hex = keys["keys"][0]["public_key"]
    real_pk = bytes.fromhex(real_pk_hex)
    print("[*] real vault-signer public key:", real_pk_hex)

    # Attacker-controlled second public key (any valid Ed25519 point works).
    attacker_sk = Ed25519PrivateKey.generate()
    attacker_pk = attacker_sk.public_key().public_bytes_raw()

    probe_msg = "key-recovery-probe"

    r1 = requests.post(
        BASE + "/api/sign",
        json={"key_id": "vault-signer", "message": probe_msg, "public_key": real_pk_hex},
    ).json()
    r2 = requests.post(
        BASE + "/api/sign",
        json={
            "key_id": "vault-signer",
            "message": probe_msg,
            "public_key": attacker_pk.hex(),
        },
    ).json()

    sig1 = bytes.fromhex(r1["signature"])
    sig2 = bytes.fromhex(r2["signature"])
    big_r1, s1_bytes = sig1[:32], sig1[32:]
    big_r2, s2_bytes = sig2[:32], sig2[32:]
    assert big_r1 == big_r2, "expected shared R (deterministic nonce independent of A)"

    msg_bytes = probe_msg.encode()
    s1 = int.from_bytes(s1_bytes, "little")
    s2 = int.from_bytes(s2_bytes, "little")
    h1 = h_scalar(big_r1, real_pk, msg_bytes)
    h2 = h_scalar(big_r2, attacker_pk, msg_bytes)

    dh = (h1 - h2) % L
    ds = (s1 - s2) % L
    secret_scalar = (ds * pow(dh, -1, L)) % L

    recovered_pub = encode_point(point_mul(secret_scalar, BASEPOINT))
    assert recovered_pub == real_pk, "recovered scalar does not match real public key!"
    print("[*] recovered secret scalar s:", secret_scalar)
    print("[+] confirmed: s*B == real vault-signer public key")

    challenge = requests.get(BASE + "/api/vault/challenge").json()
    vault_msg = bytes.fromhex(challenge["message_hex"])
    print("[*] fresh challenge message:", vault_msg)

    forged_sig = forge_signature(vault_msg, secret_scalar, real_pk)

    # Local sanity check with a standard verifier before submitting.
    Ed25519PublicKey.from_public_bytes(real_pk).verify(forged_sig, vault_msg)
    print("[+] forged signature verifies locally under the real public key")

    release = requests.post(
        BASE + "/api/vault/release",
        json={"challenge": challenge["challenge"], "signature": forged_sig.hex()},
    )
    print(release.status_code, release.text)


if __name__ == "__main__":
    main()
