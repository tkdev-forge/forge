// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract L3RollupManager {
    struct Rollup {
        string project;
        address owner;
        address sequencer;
        uint256 createdAt;
        bool active;
    }

    struct SequencerStake {
        uint256 amount;
        bool active;
    }

    uint256 public rollupCount;
    mapping(uint256 => Rollup) public rollups;
    mapping(address => SequencerStake) public sequencerStakes;

    event RollupDeployed(uint256 indexed rollupId, string project, address owner);
    event SequencerStaked(address indexed sequencer, uint256 amount);

    function deployRollup(string calldata project, address sequencer) external returns (uint256) {
        require(sequencer != address(0), "invalid sequencer");
        rollupCount += 1;

        rollups[rollupCount] = Rollup({
            project: project,
            owner: msg.sender,
            sequencer: sequencer,
            createdAt: block.timestamp,
            active: true
        });

        emit RollupDeployed(rollupCount, project, msg.sender);
        return rollupCount;
    }

    function stakeAsSequencer() external payable {
        require(msg.value > 0, "stake=0");
        sequencerStakes[msg.sender].amount += msg.value;
        sequencerStakes[msg.sender].active = true;
        emit SequencerStaked(msg.sender, msg.value);
    }
}
