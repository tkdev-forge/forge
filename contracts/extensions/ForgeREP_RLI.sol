// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.8/ChainlinkClient.sol";

/**
 * @title ForgeREP_RLI
 * @notice Extension for ForgeREP with RLI (Remote Labor Index) evaluation integration
 * @dev Integrates with RLI evaluation platform via Chainlink oracles for objective performance metrics
 */
contract ForgeREP_RLI is Ownable, ChainlinkClient {
    using Chainlink for Chainlink.Request;
    
    // ========== STRUCTS ==========
    
    struct RLIEvaluation {
        uint256 taskId;
        uint256 automationRate;      // 0-10000 basis points (0-100%)
        uint256 eloScore;
        uint256 economicValue;       // USD cents
        uint256 repEarned;
        uint256 timestamp;
        string taskCategory;
        bool verified;
    }
    
    struct TierQualification {
        uint256 requiredAutomationRate;  // Basis points
        uint256 requiredTaskCount;
        uint256 minEloScore;
        bool rliCheckRequired;
    }
    
    // ========== STATE VARIABLES ==========
    
    mapping(address => RLIEvaluation[]) public rliHistory;
    mapping(address => uint256) public rliAvgAutomation;  // Rolling average
    mapping(address => uint256) public rliTasksCompleted;
    mapping(address => bool) public rliTierQualified;
    
    // Tier-specific RLI requirements
    mapping(uint8 => TierQualification) public tierRequirements;
    
    // Chainlink Oracle config
    bytes32 public rliOracleJobId;
    uint256 public oracleFee;
    
    // Treasury allocation for RLI evaluations
    uint256 public rliEvaluationBudget;
    uint256 public rliEvaluationsUsed;
    
    // ========== EVENTS ==========
    
    event RLIEvaluationRequested(
        address indexed member,
        bytes32 indexed requestId,
        uint256 taskId
    );
    
    event RLIEvaluationRecorded(
        address indexed member,
        uint256 taskId,
        uint256 automationRate,
        uint256 eloScore,
        uint256 repEarned
    );
    
    event TierQualificationUpdated(
        address indexed member,
        uint8 tier,
        bool qualified
    );
    
    // ========== CONSTRUCTOR ==========
    
    constructor(
        address _linkToken,
        address _oracle,
        bytes32 _jobId
    ) Ownable(msg.sender) {
        setChainlinkToken(_linkToken);
        setChainlinkOracle(_oracle);
        rliOracleJobId = _jobId;
        oracleFee = 0.1 * 10**18; // 0.1 LINK
        
        // Initialize tier requirements
        _initializeTierRequirements();
        
        // Set initial budget: 100 evaluations @ $2.34 = $234
        rliEvaluationBudget = 100;
    }
    
    function _initializeTierRequirements() internal {
        // Tier 1 -> Tier 2: Basic qualification
        tierRequirements[2] = TierQualification({
            requiredAutomationRate: 5000,  // 50%
            requiredTaskCount: 3,
            minEloScore: 800,
            rliCheckRequired: true
        });
        
        // Tier 2 -> Tier 3: Advanced qualification
        tierRequirements[3] = TierQualification({
            requiredAutomationRate: 7000,  // 70%
            requiredTaskCount: 5,
            minEloScore: 1000,  // Human baseline
            rliCheckRequired: true
        });
    }
    
    // ========== RLI EVALUATION FLOW ==========
    
    function requestRLIEvaluation(
        address member,
        uint256 taskId,
        string calldata taskCategory,
        string calldata deliverableIPFSHash
    ) external onlyOwner returns (bytes32 requestId) {
        require(rliEvaluationsUsed < rliEvaluationBudget, "Budget exhausted");
        
        // Create Chainlink request
        Chainlink.Request memory req = buildChainlinkRequest(
            rliOracleJobId,
            address(this),
            this.fulfillRLIEvaluation.selector
        );
        
        // Set request parameters
        req.add("member", _addressToString(member));
        req.addUint("taskId", taskId);
        req.add("category", taskCategory);
        req.add("deliverable", deliverableIPFSHash);
        
        // Send request
        requestId = sendChainlinkRequest(req, oracleFee);
        rliEvaluationsUsed++;
        
        emit RLIEvaluationRequested(member, requestId, taskId);
        
        return requestId;
    }
    
    function fulfillRLIEvaluation(
        bytes32 _requestId,
        address member,
        uint256 taskId,
        uint256 automationRate,
        uint256 eloScore,
        uint256 economicValue,
        string calldata taskCategory
    ) public recordChainlinkFulfillment(_requestId) {
        // Calculate REP earned
        uint256 repEarned = _calculateREPFromRLI(
            automationRate,
            eloScore,
            economicValue
        );
        
        // Store evaluation
        rliHistory[member].push(RLIEvaluation({
            taskId: taskId,
            automationRate: automationRate,
            eloScore: eloScore,
            economicValue: economicValue,
            repEarned: repEarned,
            timestamp: block.timestamp,
            taskCategory: taskCategory,
            verified: true
        }));
        
        // Update stats
        rliTasksCompleted[member]++;
        _updateRollingAverage(member, automationRate);
        
        // Check tier qualification
        _checkTierQualification(member);
        
        emit RLIEvaluationRecorded(
            member,
            taskId,
            automationRate,
            eloScore,
            repEarned
        );
    }
    
    function _calculateREPFromRLI(
        uint256 automationRate,
        uint256 eloScore,
        uint256 economicValue
    ) internal pure returns (uint256) {
        // Base REP: (AutomationRate × EconomicValue × 0.1) / 100
        uint256 baseREP = (automationRate * economicValue) / 100000;
        
        // Elo bonus for exceeding human baseline (1000)
        uint256 eloBonus = 0;
        if (eloScore > 1000) {
            eloBonus = (eloScore - 1000) / 10;
        }
        
        return baseREP + eloBonus;
    }
    
    function _updateRollingAverage(
        address member,
        uint256 newAutomationRate
    ) internal {
        uint256 currentAvg = rliAvgAutomation[member];
        uint256 taskCount = rliTasksCompleted[member];
        
        if (taskCount == 1) {
            rliAvgAutomation[member] = newAutomationRate;
        } else {
            rliAvgAutomation[member] = 
                (currentAvg * (taskCount - 1) + newAutomationRate) / taskCount;
        }
    }
    
    function _checkTierQualification(address member) internal {
        // Get current tier from main REP contract (would need interface)
        // For now, check against all tier requirements
        
        for (uint8 tier = 2; tier <= 3; tier++) {
            TierQualification memory req = tierRequirements[tier];
            
            if (!req.rliCheckRequired) continue;
            
            bool qualified = (
                rliTasksCompleted[member] >= req.requiredTaskCount &&
                rliAvgAutomation[member] >= req.requiredAutomationRate &&
                _getMaxEloScore(member) >= req.minEloScore
            );
            
            if (qualified && !rliTierQualified[member]) {
                rliTierQualified[member] = true;
                emit TierQualificationUpdated(member, tier, true);
            }
        }
    }
    
    function _getMaxEloScore(address member) internal view returns (uint256) {
        RLIEvaluation[] memory history = rliHistory[member];
        uint256 maxElo = 0;
        
        for (uint256 i = 0; i < history.length; i++) {
            if (history[i].eloScore > maxElo) {
                maxElo = history[i].eloScore;
            }
        }
        
        return maxElo;
    }
    
    // ========== VIEW FUNCTIONS ==========
    
    function canUpgradeToTier(
        address member,
        uint8 targetTier
    ) public view returns (bool, string memory reason) {
        TierQualification memory req = tierRequirements[targetTier];
        
        if (!req.rliCheckRequired) {
            return (true, "No RLI check required");
        }
        
        if (rliTasksCompleted[member] < req.requiredTaskCount) {
            return (false, "Insufficient RLI tasks completed");
        }
        
        if (rliAvgAutomation[member] < req.requiredAutomationRate) {
            return (false, "Automation rate too low");
        }
        
        if (_getMaxEloScore(member) < req.minEloScore) {
            return (false, "Elo score too low");
        }
        
        return (true, "Qualified");
    }
    
    function getRLIStats(address member) external view returns (
        uint256 tasksCompleted,
        uint256 avgAutomation,
        uint256 maxElo,
        bool tierQualified
    ) {
        return (
            rliTasksCompleted[member],
            rliAvgAutomation[member],
            _getMaxEloScore(member),
            rliTierQualified[member]
        );
    }
    
    // ========== ADMIN FUNCTIONS ==========
    
    function updateTierRequirements(
        uint8 tier,
        uint256 automationRate,
        uint256 taskCount,
        uint256 minElo
    ) external onlyOwner {
        tierRequirements[tier] = TierQualification({
            requiredAutomationRate: automationRate,
            requiredTaskCount: taskCount,
            minEloScore: minElo,
            rliCheckRequired: true
        });
    }
    
    function addRLIBudget(uint256 additionalEvaluations) external onlyOwner {
        rliEvaluationBudget += additionalEvaluations;
    }
    
    function updateOracleConfig(
        address _oracle,
        bytes32 _jobId,
        uint256 _fee
    ) external onlyOwner {
        setChainlinkOracle(_oracle);
        rliOracleJobId = _jobId;
        oracleFee = _fee;
    }
    
    // ========== UTILITIES ==========
    
    function _addressToString(address _addr) internal pure returns (string memory) {
        bytes32 value = bytes32(uint256(uint160(_addr)));
        bytes memory alphabet = "0123456789abcdef";
        bytes memory str = new bytes(42);
        str[0] = '0';
        str[1] = 'x';
        for (uint256 i = 0; i < 20; i++) {
            str[2+i*2] = alphabet[uint8(value[i + 12] >> 4)];
            str[3+i*2] = alphabet[uint8(value[i + 12] & 0x0f)];
        }
        return string(str);
    }
}
