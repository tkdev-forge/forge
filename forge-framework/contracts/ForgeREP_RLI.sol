// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@chainlink/contracts/src/v0.8/ChainlinkClient.sol";
import "@chainlink/contracts/src/v0.8/interfaces/LinkTokenInterface.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "./ForgeREP.sol";

contract ForgeREP_RLI is ForgeREP, ChainlinkClient, AccessControl, ReentrancyGuard {
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

    struct TierQualification {
        uint256 requiredAutomationRate;
        uint256 requiredTaskCount;
        uint256 minEloScore;
        bool rliCheckRequired;
    }

    struct PendingRequest {
        address member;
        string taskId;
        string taskCategory;
        bool exists;
    }

    mapping(address => RLIEvaluation[]) private rliHistory;
    mapping(address => uint256) public rliAvgAutomation;
    mapping(address => uint256) public rliTasksCompleted;
    mapping(address => bool) public rliTierQualified;
    mapping(uint8 => TierQualification) public tierRequirements;
    mapping(bytes32 => PendingRequest) public pendingRequests;

    address public chainlinkOracle;
    bytes32 public chainlinkJobId;
    uint256 public chainlinkFee;
    uint256 public remainingEvaluations;
    bool public oraclePaused;

    event RLIEvaluationRequested(bytes32 indexed requestId, address indexed member, string taskId);
    event RLIEvaluationFulfilled(bytes32 indexed requestId, address indexed member, uint256 repEarned);

    constructor(address linkToken, address oracle, bytes32 jobId, uint256 fee, uint256 budget)
        ForgeREP()
    {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(EVALUATOR_ROLE, msg.sender);

        setChainlinkToken(linkToken);
        chainlinkOracle = oracle;
        chainlinkJobId = jobId;
        chainlinkFee = fee;
        remainingEvaluations = budget;

        tierRequirements[1] = TierQualification(30, 1, 900, false);
        tierRequirements[2] = TierQualification(60, 5, 1100, true);
        tierRequirements[3] = TierQualification(75, 15, 1250, true);
    }

    function requestRLIEvaluation(
        address member,
        string calldata taskId,
        string calldata taskCategory,
        string calldata deliverableIPFSHash
    ) external onlyRole(EVALUATOR_ROLE) returns (bytes32 requestId) {
        require(!oraclePaused, "oracle paused");
        require(remainingEvaluations > 0, "no budget");

        Chainlink.Request memory req = buildChainlinkRequest(chainlinkJobId, address(this), this.fulfillRLIEvaluation.selector);
        req.add("taskId", taskId);
        req.add("taskCategory", taskCategory);
        req.add("member", _toAsciiString(member));
        req.add("ipfsHash", deliverableIPFSHash);

        requestId = sendChainlinkRequestTo(chainlinkOracle, req, chainlinkFee);
        pendingRequests[requestId] = PendingRequest(member, taskId, taskCategory, true);
        remainingEvaluations -= 1;

        emit RLIEvaluationRequested(requestId, member, taskId);
    }

    function fulfillRLIEvaluation(
        bytes32 requestId,
        uint256 automationRate,
        uint256 eloScore,
        uint256 economicValue
    ) external recordChainlinkFulfillment(requestId) nonReentrant {
        PendingRequest memory pending = pendingRequests[requestId];
        require(pending.exists, "unknown request");

        uint256 baseREP = (automationRate * economicValue) / 100000;
        uint256 eloBonus = eloScore > 1000 ? (eloScore - 1000) / 10 : 0;
        uint256 total = baseREP + eloBonus;

        bool isNewMember = reputation[pending.member] == 0;
        reputation[pending.member] += total;
        lastUpdate[pending.member] = block.timestamp;

        RLIEvaluation memory eval = RLIEvaluation({
            taskId: pending.taskId,
            automationRate: automationRate,
            eloScore: eloScore,
            economicValue: economicValue,
            repEarned: total,
            timestamp: block.timestamp,
            taskCategory: pending.taskCategory,
            verified: true
        });
        rliHistory[pending.member].push(eval);

        uint256 completed = rliTasksCompleted[pending.member] + 1;
        rliTasksCompleted[pending.member] = completed;
        rliAvgAutomation[pending.member] =
            ((rliAvgAutomation[pending.member] * (completed - 1)) + automationRate) /
            completed;

        _checkTierQualification(pending.member, getTier(pending.member));
        _updateCommunityAvg(int256(total), isNewMember);
        delete pendingRequests[requestId];

        emit RLIEvaluationFulfilled(requestId, pending.member, total);
    }

    function _checkTierQualification(address member, uint8 tier) internal {
        TierQualification memory req = tierRequirements[tier];
        if (!req.rliCheckRequired) {
            rliTierQualified[member] = true;
            return;
        }

        RLIEvaluation[] memory history = rliHistory[member];
        uint256 lastElo = history.length > 0 ? history[history.length - 1].eloScore : 0;

        rliTierQualified[member] =
            rliAvgAutomation[member] >= req.requiredAutomationRate &&
            rliTasksCompleted[member] >= req.requiredTaskCount &&
            lastElo >= req.minEloScore;
    }

    function canUpgradeToTier(address member, uint8 targetTier) external view returns (bool) {
        TierQualification memory req = tierRequirements[targetTier];
        if (!req.rliCheckRequired) return true;

        RLIEvaluation[] memory history = rliHistory[member];
        uint256 lastElo = history.length > 0 ? history[history.length - 1].eloScore : 0;

        return
            rliAvgAutomation[member] >= req.requiredAutomationRate &&
            rliTasksCompleted[member] >= req.requiredTaskCount &&
            lastElo >= req.minEloScore;
    }

    function getRLIStats(address member) external view returns (uint256 avgAutomation, uint256 taskCount, bool qualified) {
        return (rliAvgAutomation[member], rliTasksCompleted[member], rliTierQualified[member]);
    }

    function getRLIHistory(address member) external view returns (RLIEvaluation[] memory) {
        return rliHistory[member];
    }

    function updateTierRequirements(uint8 tier, uint256 automationRate, uint256 taskCount, uint256 minElo)
        external
        onlyRole(DEFAULT_ADMIN_ROLE)
    {
        tierRequirements[tier] = TierQualification(automationRate, taskCount, minElo, true);
    }

    function addRLIBudget(uint256 additionalEvaluations) external onlyRole(DEFAULT_ADMIN_ROLE) {
        remainingEvaluations += additionalEvaluations;
    }

    function pauseOracle() external onlyRole(DEFAULT_ADMIN_ROLE) {
        oraclePaused = true;
    }

    function resumeOracle() external onlyRole(DEFAULT_ADMIN_ROLE) {
        oraclePaused = false;
    }

    function updateOracleConfig(address oracle, bytes32 jobId, uint256 fee) external onlyRole(DEFAULT_ADMIN_ROLE) {
        chainlinkOracle = oracle;
        chainlinkJobId = jobId;
        chainlinkFee = fee;
    }

    function withdrawLink(address to, uint256 amount) external onlyRole(DEFAULT_ADMIN_ROLE) {
        LinkTokenInterface link = LinkTokenInterface(chainlinkTokenAddress());
        require(link.transfer(to, amount), "LINK transfer failed");
    }

    function _toAsciiString(address x) private pure returns (string memory) {
        bytes memory s = new bytes(40);
        for (uint256 i = 0; i < 20; i++) {
            bytes1 b = bytes1(uint8(uint(uint160(x)) / (2 ** (8 * (19 - i)))));
            bytes1 hi = bytes1(uint8(b) / 16);
            bytes1 lo = bytes1(uint8(b) - 16 * uint8(hi));
            s[2 * i] = _char(hi);
            s[2 * i + 1] = _char(lo);
        }
        return string(s);
    }

    function _char(bytes1 b) private pure returns (bytes1 c) {
        if (uint8(b) < 10) return bytes1(uint8(b) + 0x30);
        return bytes1(uint8(b) + 0x57);
    }
}
