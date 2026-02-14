// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "./ForgeREP.sol";

contract ForgeDAO {
    struct Proposal {
        string description;
        uint256 votesFor;
        uint256 votesAgainst;
        bool executed;
        uint256 minTier;
        uint256 createdAt;
        uint256 deadline;
    }

    ForgeREP public immutable rep;
    uint256 public constant PROPOSAL_REP_THRESHOLD = 100;

    Proposal[] public proposals;
    mapping(uint256 => mapping(address => bool)) public hasVoted;

    event ProposalCreated(uint256 indexed proposalId, string description, uint256 minTier, uint256 deadline);
    event Voted(uint256 indexed proposalId, address indexed voter, bool support, uint256 weight);
    event ProposalExecuted(uint256 indexed proposalId);

    constructor(address repAddress) {
        rep = ForgeREP(repAddress);
    }

    function createProposal(string calldata description, uint256 minTier, uint256 duration) external returns (uint256 id) {
        uint8 tier = rep.getTier(msg.sender);
        uint256 r = rep.reputation(msg.sender);
        require(tier >= 2 || r >= PROPOSAL_REP_THRESHOLD, "not eligible");
        require(duration >= 1 days, "duration too short");

        proposals.push(
            Proposal({
                description: description,
                votesFor: 0,
                votesAgainst: 0,
                executed: false,
                minTier: minTier,
                createdAt: block.timestamp,
                deadline: block.timestamp + duration
            })
        );

        id = proposals.length - 1;
        emit ProposalCreated(id, description, minTier, block.timestamp + duration);
    }

    function vote(uint256 proposalId, bool support) external {
        Proposal storage p = proposals[proposalId];
        require(block.timestamp < p.deadline, "vote ended");
        require(!hasVoted[proposalId][msg.sender], "already voted");
        require(rep.getTier(msg.sender) >= p.minTier, "tier too low");

        uint256 weight = rep.reputation(msg.sender);
        require(weight > 0, "no REP");

        hasVoted[proposalId][msg.sender] = true;
        if (support) p.votesFor += weight;
        else p.votesAgainst += weight;

        emit Voted(proposalId, msg.sender, support, weight);
    }

    function executeProposal(uint256 proposalId) external {
        Proposal storage p = proposals[proposalId];
        require(!p.executed, "already executed");
        require(block.timestamp >= p.deadline, "vote active");
        require(p.votesFor > p.votesAgainst, "proposal rejected");

        p.executed = true;
        emit ProposalExecuted(proposalId);
    }
}
