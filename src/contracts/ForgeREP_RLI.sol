// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@chainlink/contracts/src/v0.8/ChainlinkClient.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

contract ForgeREP_RLI is ChainlinkClient, AccessControl {
    using Chainlink for Chainlink.Request;

    struct RLIEvaluation {
        uint256 taskId;
        uint256 automationRate;
        uint256 eloScore;
        uint256 economicValue;
        uint256 repEarned;
        uint256 timestamp;
        bool verified;
    }

    mapping(address => RLIEvaluation[]) public rliHistory;
    mapping(address => uint256) public rliAvgAutomation;
    mapping(address => uint256) public rliTasksCompleted;

    bytes32 public rliOracleJobId;
    uint256 public oracleFee;
    uint256 public rliEvaluationBudget;
    uint256 public rliEvaluationsUsed;

    event RLIEvaluationRequested(address indexed member, bytes32 indexed requestId, uint256 taskId);
    event RLIEvaluationRecorded(address indexed member, uint256 taskId, uint256 automationRate, uint256 eloScore, uint256 repEarned);

    constructor(address linkToken_, address oracle_, bytes32 jobId_, uint256 fee_, uint256 budget_) {
        setChainlinkToken(linkToken_);
        setChainlinkOracle(oracle_);
        rliOracleJobId = jobId_;
        oracleFee = fee_;
        rliEvaluationBudget = budget_;
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
    }

    function requestRLIEvaluation(address member, uint256 taskId, string calldata deliverableIPFSHash)
        external
        returns (bytes32 requestId)
    {
        require(rliEvaluationsUsed < rliEvaluationBudget, "Budget exhausted");

        Chainlink.Request memory req = buildChainlinkRequest(rliOracleJobId, address(this), this.fulfillRLIEvaluation.selector);
        req.add("member", _addressToString(member));
        req.addUint("taskId", taskId);
        req.add("deliverable", deliverableIPFSHash);

        requestId = sendChainlinkRequest(req, oracleFee);
        rliEvaluationsUsed++;
        emit RLIEvaluationRequested(member, requestId, taskId);
    }

    function fulfillRLIEvaluation(
        bytes32 requestId,
        address member,
        uint256 taskId,
        uint256 automationRate,
        uint256 eloScore,
        uint256 economicValue
    ) public recordChainlinkFulfillment(requestId) {
        uint256 repEarned = _calculateREPFromRLI(automationRate, eloScore, economicValue);

        rliHistory[member].push(RLIEvaluation(taskId, automationRate, eloScore, economicValue, repEarned, block.timestamp, true));
        rliTasksCompleted[member]++;
        _updateRollingAverage(member, automationRate);

        emit RLIEvaluationRecorded(member, taskId, automationRate, eloScore, repEarned);
    }

    function _calculateREPFromRLI(uint256 automationRate, uint256 eloScore, uint256 economicValue)
        internal
        pure
        returns (uint256)
    {
        uint256 baseREP = (automationRate * economicValue) / 100000;
        uint256 eloBonus = eloScore > 1000 ? (eloScore - 1000) / 10 : 0;
        return baseREP + eloBonus;
    }

    function _updateRollingAverage(address member, uint256 newRate) internal {
        uint256 count = rliTasksCompleted[member];
        if (count == 1) {
            rliAvgAutomation[member] = newRate;
        } else {
            rliAvgAutomation[member] = (rliAvgAutomation[member] * (count - 1) + newRate) / count;
        }
    }

    function _addressToString(address account) internal pure returns (string memory) {
        return toAsciiString(account);
    }

    function toAsciiString(address x) internal pure returns (string memory) {
        bytes memory s = new bytes(42);
        s[0] = "0";
        s[1] = "x";
        for (uint256 i = 0; i < 20; i++) {
            bytes1 b = bytes1(uint8(uint(uint160(x)) / (2 ** (8 * (19 - i)))));
            bytes1 hi = bytes1(uint8(b) / 16);
            bytes1 lo = bytes1(uint8(b) - 16 * uint8(hi));
            s[2 + i * 2] = char(hi);
            s[3 + i * 2] = char(lo);
        }
        return string(s);
    }

    function char(bytes1 b) internal pure returns (bytes1 c) {
        if (uint8(b) < 10) return bytes1(uint8(b) + 0x30);
        return bytes1(uint8(b) + 0x57);
    }
}
