// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "./ForgeREP.sol";

interface IGroth16Verifier {
    function verifyProof(uint256[2] calldata a, uint256[2][2] calldata b, uint256[2] calldata c, uint256[3] calldata input)
        external
        view
        returns (bool);
}

contract ZKReputationVerifier {
    struct ZKProof {
        uint256[2] a;
        uint256[2][2] b;
        uint256[2] c;
        uint256[3] publicSignals; // repMin, tier, nullifier
    }

    ForgeREP public immutable rep;
    IGroth16Verifier public immutable verifier;
    mapping(bytes32 => bool) public usedNullifiers;

    event SessionCreated(bytes32 indexed sessionId, address indexed requester, uint256 repMin, uint256 tier, bytes32 nullifier);

    constructor(address repAddress, address verifierAddress) {
        rep = ForgeREP(repAddress);
        verifier = IGroth16Verifier(verifierAddress);
    }

    function verifyAndCreateSession(ZKProof calldata proof) external returns (bytes32 sessionId) {
        bytes32 nullifier = bytes32(proof.publicSignals[2]);
        require(!usedNullifiers[nullifier], "nullifier used");

        bool ok = verifier.verifyProof(proof.a, proof.b, proof.c, proof.publicSignals);
        require(ok, "invalid proof");

        usedNullifiers[nullifier] = true;
        sessionId = keccak256(abi.encodePacked(msg.sender, nullifier, block.timestamp));

        emit SessionCreated(sessionId, msg.sender, proof.publicSignals[0], proof.publicSignals[1], nullifier);
    }
}
