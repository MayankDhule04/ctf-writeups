---
name: blockchain-attack-checklist
description: Walk a systematic checklist of named smart contract vulnerability classes (reentrancy, flashloan/oracle manipulation, access control, upgradeability bugs) before writing custom exploit contracts. Use when facing a CTF blockchain/Web3/Solidity challenge, especially ones involving DeFi primitives like lending pools, DEXs, vaults, or governance.
---

## Why checklist-first

Nearly all CTF blockchain challenges are an instance of a named vulnerability
class from the DeFi/smart-contract security literature (see Damn Vulnerable
DeFi — damnvulnerabledefi.xyz — for the canonical, hands-on reference set of
these exact patterns: Unstoppable, Naive Receiver, Truster, Side Entrance,
The Rewarder, Selfie, Compromised, Puppet/Puppet V2/V3, Free Rider, Backdoor,
Climber, Wallet Mining, ABI Smuggling, Shards, Curvy Puppet, Withdrawal).
Read the contract source fully first, then walk this list.

## Step 0 — always do first

1. Read every contract's source completely, including inherited/imported
   contracts and interfaces — do not skip library code, the bug is
   frequently in a helper function, not the headline contract.
2. Identify what action gives you the win condition (drain a pool to zero,
   become owner/admin, mint tokens, pass a governance vote) — work backward
   from there to find the state-changing function that reaches it.
3. Note which functions are `external`/`public` and callable by anyone,
   versus `internal`/`private` and only reachable through other logic.

## Checklist, in rough order of frequency in CTFs

1. **Reentrancy (classic)**: a function sends value/calls out to an external
   address BEFORE updating its own internal accounting state. Exploit via a
   malicious contract whose fallback/receive function re-enters the
   vulnerable function before the first call completes.
2. **Reentrancy (cross-function)**: the reentrant call doesn't re-enter the
   *same* function, but a *different* function that shares the same
   not-yet-updated state variable.
3. **Reentrancy (read-only)**: a view function returns a value that's
   momentarily inconsistent mid-transaction (e.g. during a callback), and
   another protocol/contract reads that view function and makes a decision
   based on the stale/manipulated value — no state is actually corrupted,
   but a reader is tricked.
4. **Access control**: `tx.origin` used instead of `msg.sender` for
   authorization (bypassable via a malicious intermediate contract); missing
   `onlyOwner`/role checks on a sensitive function; a constructor-only
   initialization function left callable post-deployment (common in
   upgradeable/proxy patterns — "unprotected initializer").
5. **Price/oracle manipulation**: a lending/DEX contract reads price from a
   single on-chain source (e.g. a spot AMM pool) that can be manipulated
   within the same transaction using a flashloan, then exploited before the
   price reverts.
6. **Flashloan-enabled attacks generally**: even without oracle
   manipulation, a flashloan can supply enough capital in one transaction to
   pass a balance/collateral threshold check that assumes an attacker
   couldn't otherwise afford the position.
7. **Unchecked external call return values**: a `call()`/`send()` whose
   return value isn't checked can silently fail, leaving internal state
   inconsistent with reality (e.g. marking a withdrawal "complete" even
   though the transfer failed).
8. **Integer edge cases**: in modern Solidity (0.8+) overflow/underflow
   reverts by default, so check instead for `unchecked {}` blocks that
   deliberately disable this protection, or truncation issues from unsafe
   downcasting (`uint256` to `uint128`/`uint8`).
9. **Upgradeability / proxy storage collisions**: in a proxy pattern
   (transparent/UUPS), check that the proxy's and implementation's storage
   layouts actually align — a mismatched slot layout can let you overwrite
   an unrelated variable (e.g. overwrite `owner` by writing to what you
   think is a different field).
10. **ABI smuggling / selector confusion**: a function dispatch or low-level
    `call` constructs its call data in a way that can be manipulated to
    invoke a different function than intended, or pass arguments that get
    reinterpreted due to encoding ambiguity.
11. **Governance manipulation**: flashloan-borrowed tokens used to pass a
    governance vote within a single transaction/block, then repaid
    immediately after the vote's effect is locked in.
12. **ERC-721/1155 callback reentrancy**: `safeTransferFrom`/`onERC721Received`
    hooks invoke attacker-controlled code mid-transfer — treat these exactly
    like a classic reentrancy vector.
13. **Signature replay/malleability**: a signature-based authorization scheme
    that doesn't include a nonce/chain ID, or doesn't reject malleable
    (s, 27/28 vs s, 28/27) ECDSA signature variants, allowing a captured
    signature to be reused.

## Tooling

- **Foundry** (`forge`/`cast`) for compiling, testing, and interacting with
  contracts, including writing a PoC exploit contract and running it against
  a forked/local chain before touching the live challenge RPC.
- **web3.py** (Python) or **ethers.js** (Node) if a live RPC endpoint is
  reachable and the exploit is simpler to script than to write as a
  Solidity PoC contract.
- Always test any exploit contract against a local fork (`anvil`) before
  sending it to the live challenge RPC — a failed on-chain transaction can
  cost you gas/attempts you don't get back.
