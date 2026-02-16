// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@chainlink/contracts/src/v0.8/ChainlinkClient.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

contract ForgeREP_RLI is ChainlinkClient, AccessControl {
    using Chainlink for Chainlink.Request;

    bytes32 public constant EVALUATOR_ROLE = keccak256("EVALUATOR_ROLE");

    struct RLIEvaluation {
        string taskId;
        uint256 automationRate;
        uint256 eloScore;
        uint256 economicValue;
        uint256 repEarned;
        uint256 timestamp;
        string taskCategory;
        bool verified;
    }

    struct PendingRequest {
        address member;
        string taskId;
        string taskCategory;
        uint256 requestedAt;
        bool exists;
    }

    mapping(address => RLIEvaluation[]) public rliHistory;
    mapping(address => uint256) public rliAvgAutomation;
    mapping(address => uint256) public rliTasksCompleted;
    mapping(bytes32 => PendingRequest) public pendingRequests;

    bytes32 public chainlinkJobId;
    uint256 public chainlinkFee;
    uint256 public remainingEvaluations;
    bool public oraclePaused;

    uint256 public constant AUTOMATION_RATE_SCALE = 100000;
    uint256 public constant ELO_BASELINE = 1000;
    uint256 public constant ELO_BONUS_DIVISOR = 10;
    uint256 public constant MAX_REP_REWARD = 1_000_000;
    uint256 public constant ORACLE_TIMEOUT = 1 days;

    event RLIEvaluationRequested(bytes32 indexed requestId, address indexed member, string taskId);
    event RLIEvaluationRecorded(bytes32 indexed requestId, address indexed member, uint256 repEarned);
    event RLIEvaluationExpired(bytes32 indexed requestId, address indexed member);

    constructor(address linkToken_, address oracle_, bytes32 jobId_, uint256 fee_, uint256 budget_) {
        setChainlinkToken(linkToken_);
        setChainlinkOracle(oracle_);
        chainlinkJobId = jobId_;
        chainlinkFee = fee_;
        remainingEvaluations = budget_;
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(EVALUATOR_ROLE, msg.sender);
    }

    function requestRLIEvaluation(
        address member,
        string calldata taskId,
        string calldata taskCategory,
        string calldata deliverableIPFSHash
    )
        external
        onlyRole(EVALUATOR_ROLE)
        returns (bytes32 requestId)
    {
        require(!oraclePaused, "oracle paused");
        require(remainingEvaluations > 0, "no budget");

        Chainlink.Request memory req = buildChainlinkRequest(chainlinkJobId, address(this), this.fulfillRLIEvaluation.selector);
        req.add("member", _addressToString(member));
        req.add("taskId", taskId);
        req.add("taskCategory", taskCategory);
        req.add("deliverable", deliverableIPFSHash);

        requestId = sendChainlinkRequest(req, chainlinkFee);
        pendingRequests[requestId] = PendingRequest(member, taskId, taskCategory, block.timestamp, true);
        remainingEvaluations -= 1;

        emit RLIEvaluationRequested(requestId, member, taskId);
    }

    function fulfillRLIEvaluation(
        bytes32 requestId,
        uint256 automationRate,
        bool hasEloScore,
        uint256 eloScore,
        uint256 economicValue
    ) public recordChainlinkFulfillment(requestId) {
        PendingRequest memory pending = pendingRequests[requestId];
        require(pending.exists, "unknown request");

        uint256 repEarned = _calculateREPFromRLI(automationRate, hasEloScore, eloScore, economicValue);

        rliHistory[pending.member].push(
            RLIEvaluation(pending.taskId, automationRate, eloScore, economicValue, repEarned, block.timestamp, pending.taskCategory, true)
        );
        rliTasksCompleted[pending.member]++;
        _updateRollingAverage(pending.member, automationRate);
        delete pendingRequests[requestId];

        emit RLIEvaluationRecorded(requestId, pending.member, repEarned);
    }

    function _calculateREPFromRLI(uint256 automationRate, bool hasEloScore, uint256 eloScore, uint256 economicValue)
        internal
        pure
        returns (uint256)
    {
        if (economicValue == 0) {
            return 0;
        }

        uint256 cappedAutomationRate = automationRate > AUTOMATION_RATE_SCALE ? AUTOMATION_RATE_SCALE : automationRate;
        uint256 baseREP = (cappedAutomationRate * economicValue) / AUTOMATION_RATE_SCALE;

        uint256 normalizedEloScore = hasEloScore ? eloScore : ELO_BASELINE;
        uint256 eloBonus = normalizedEloScore > ELO_BASELINE ? (normalizedEloScore - ELO_BASELINE) / ELO_BONUS_DIVISOR : 0;

        uint256 reward = baseREP + eloBonus;
        return reward > MAX_REP_REWARD ? MAX_REP_REWARD : reward;
    }

    function cancelExpiredRequest(bytes32 requestId) external onlyRole(DEFAULT_ADMIN_ROLE) {
        PendingRequest memory pending = pendingRequests[requestId];
        require(pending.exists, "unknown request");
        require(block.timestamp >= pending.requestedAt + ORACLE_TIMEOUT, "request active");

        delete pendingRequests[requestId];
        remainingEvaluations += 1;

        emit RLIEvaluationExpired(requestId, pending.member);
    }

    function pauseOracle() external onlyRole(DEFAULT_ADMIN_ROLE) {
        oraclePaused = true;
    }

    function resumeOracle() external onlyRole(DEFAULT_ADMIN_ROLE) {
        oraclePaused = false;
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
