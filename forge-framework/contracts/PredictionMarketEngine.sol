// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "./ForgeREP.sol";

contract PredictionMarketEngine {
    struct Market {
        string question;
        uint256 resolutionDate;
        uint8 marketType;
        uint256 finalPrice;
        bool resolved;
        address creator;
        uint256 totalYesStake;
        uint256 totalNoStake;
    }

    struct Position {
        uint256 yesStake;
        uint256 noStake;
    }

    ForgeREP public immutable rep;
    uint256 public marketCount;

    mapping(uint256 => Market) public markets;
    mapping(uint256 => mapping(address => Position)) public positions;
    mapping(uint256 => mapping(address => bool)) public payoutClaimed;

    event MarketCreated(uint256 indexed marketId, string question, address creator);
    event PositionTaken(uint256 indexed marketId, address indexed user, bool yes, uint256 stake);
    event MarketResolved(uint256 indexed marketId, uint256 finalPrice);
    event PayoutClaimed(uint256 indexed marketId, address indexed user, uint256 amount);

    constructor(address repAddress) {
        rep = ForgeREP(repAddress);
    }

    function createMarket(string calldata question, uint256 resolutionDate, uint8 marketType) external returns (uint256) {
        require(rep.getTier(msg.sender) >= 2, "tier too low");
        require(resolutionDate > block.timestamp, "invalid date");

        marketCount += 1;
        markets[marketCount] = Market(question, resolutionDate, marketType, 0, false, msg.sender, 0, 0);
        emit MarketCreated(marketCount, question, msg.sender);
        return marketCount;
    }

    function takePosition(uint256 marketId, bool yes) external payable {
        require(msg.value > 0, "stake=0");
        Market storage m = markets[marketId];
        require(m.creator != address(0), "market missing");
        require(block.timestamp < m.resolutionDate, "market closed");

        if (yes) {
            positions[marketId][msg.sender].yesStake += msg.value;
            m.totalYesStake += msg.value;
        } else {
            positions[marketId][msg.sender].noStake += msg.value;
            m.totalNoStake += msg.value;
        }

        emit PositionTaken(marketId, msg.sender, yes, msg.value);
    }


    function claimPayout(uint256 marketId) external {
        Market storage m = markets[marketId];
        require(m.resolved, "market unresolved");
        require(!payoutClaimed[marketId][msg.sender], "already claimed");

        Position storage position = positions[marketId][msg.sender];
        uint256 participantYes = position.yesStake;
        uint256 participantNo = position.noStake;
        require(participantYes > 0 || participantNo > 0, "no position");

        bool yesWins = m.finalPrice > 0;
        uint256 winningPool = yesWins ? m.totalYesStake : m.totalNoStake;
        uint256 losingPool = yesWins ? m.totalNoStake : m.totalYesStake;
        uint256 participantWinningStake = yesWins ? participantYes : participantNo;

        uint256 payout;
        if (winningPool == 0) {
            payout = participantYes + participantNo;
        } else {
            require(participantWinningStake > 0, "not winning side");
            payout = participantWinningStake + (losingPool * participantWinningStake) / winningPool;
        }

        payoutClaimed[marketId][msg.sender] = true;

        (bool sent, ) = payable(msg.sender).call{value: payout}("");
        require(sent, "payout failed");

        emit PayoutClaimed(marketId, msg.sender, payout);
    }

    function resolveMarket(uint256 marketId, uint256 finalPrice) external {
        Market storage m = markets[marketId];
        require(msg.sender == m.creator || rep.getTier(msg.sender) >= 3, "not allowed");
        require(block.timestamp >= m.resolutionDate, "too early");
        require(!m.resolved, "already resolved");

        m.finalPrice = finalPrice;
        m.resolved = true;

        emit MarketResolved(marketId, finalPrice);
    }
}
