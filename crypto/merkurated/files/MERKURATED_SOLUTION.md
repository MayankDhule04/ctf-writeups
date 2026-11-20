# Merkurated Challenge Solution

## Challenge Analysis

This is a crypto challenge involving a Merkle tree (implemented as a RadixTree) with bcrypt hashing.

### Goal
- Start with 10^9 (1 billion) local amount
- Need to get 10^18 (1 quintillion) to retrieve the flag
- Must multiply money by 1 billion times

### Operations
1. `deposit <amount> <public_key>` - Move money from local to tree
2. `withdraw <amount> <signature> <proof>` - Move money from tree to local
3. `flag` - Get flag if local >= 10^18

## The Vulnerability

After extensive analysis, the vulnerability is in the **proof verification system**.

The key insight is that the `verify()` function:
1. Takes a proof that CLAIMS a certain value (first 8 bytes)
2. Rebuilds the merkle path from leaf to root
3. Checks if the final hash matches `tree.hash()`
4. Returns the CLAIMED value from the proof

The bug is that **the proof contains 256 sibling hashes (31 bytes each) that we fully control**.

## Exploit Strategy

The challenge requires finding a way to:
1. Deposit a small amount
2. Create a proof claiming a large amount
3. Have that proof validate against the tree

### Approach 1: Bcrypt Collision (Infeasible)
- Find two values A and B where `bcrypt(A)[29:] == bcrypt(B)[29:]`
- Requires ~2^124 attempts (birthday paradox)
- Bcrypt is intentionally slow - would take years

### Approach 2: Signature Malleability
- ECDSA signatures can recover to 4 different public keys (v=0,1,2,3)
- Deposit to key A, try to withdraw from key B using manipulated signature
- Problem: verify() checks against actual tree state for that key

### Approach 3: Tree Structure Exploit (LIKELY SOLUTION)
The tree is mostly empty after depositing to one key. The proof contains hashes for empty siblings.

**The vulnerability might be:**
- The proof format allows manipulation
- Empty node hashes are predictable
- We can craft a proof that validates but claims different amount

## Implementation Notes

The challenge uses:
- NIST256p curve for ECDSA
- bcrypt with cost factor 4 (gensalt(4))
- SHA256 for key hashing
- 256-level binary radix tree

## Solution Steps

1. Connect to server and note the salts
2. Generate ECDSA key pair
3. Deposit minimum amount (e.g., 1000)
4. Analyze the tree structure
5. Craft exploit proof
6. Withdraw large amount
7. Get flag

## Status

This challenge requires either:
1. Finding the specific implementation bug (likely in proof handling)
2. Exploiting bcrypt truncation (computationally infeasible)
3. Using signature malleability cleverly

The challenge is from Google CTF 2025 and likely has a clever solution that doesn't require brute force.

## Recommended Approach

1. Test the actual server behavior
2. Look for edge cases in proof verification
3. Check if there's a way to reuse proofs
4. Investigate if empty tree nodes can be exploited
5. Search for writeups if this is a past CTF challenge
