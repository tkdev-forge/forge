// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract MetaBridge {
    mapping(address => uint256) public metaREP;

    event REPBridged(address indexed member, uint256 amount, string sourceChain, bytes32 proofHash);

    function bridgeREP(address member, uint256 amount, string calldata sourceChain, bytes32 merkleProof) external {
        require(member != address(0), "invalid member");
        require(amount > 0, "amount=0");

        metaREP[member] += amount;
        emit REPBridged(member, amount, sourceChain, merkleProof);
    }
}
