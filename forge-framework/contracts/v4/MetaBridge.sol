// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract MetaBridge {
    address public owner;
    mapping(address => uint256) public metaREP;
    mapping(bytes32 => bool) public verifiedProofs;
    mapping(bytes32 => bool) public consumedProofs;

    event ProofVerified(bytes32 indexed proofHash, address indexed verifier);
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

    event REPBridged(address indexed member, uint256 amount, string sourceChain, bytes32 proofHash);

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "only owner");
        _;
    }

    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "invalid owner");
        emit OwnershipTransferred(owner, newOwner);
        owner = newOwner;
    }

    function verifyProof(bytes32 proofHash) external onlyOwner {
        require(proofHash != bytes32(0), "invalid proof");
        verifiedProofs[proofHash] = true;
        emit ProofVerified(proofHash, msg.sender);
    }

    function bridgeREP(address member, uint256 amount, string calldata sourceChain, bytes32 merkleProof) external {
        require(member != address(0), "invalid member");
        require(amount > 0, "amount=0");
        require(verifiedProofs[merkleProof], "unverified proof");
        require(!consumedProofs[merkleProof], "proof already used");

        consumedProofs[merkleProof] = true;

        metaREP[member] += amount;
        emit REPBridged(member, amount, sourceChain, merkleProof);
    }
}
