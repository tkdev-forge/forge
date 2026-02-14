// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract ForgeREP is ERC721, Ownable, AccessControl {
    struct TierConfig {
        uint256 minREP;
        string label;
        bool canSpawnAgents;
        bool canVote;
        bool canPropose;
        bool hasEmergencyAccess;
    }

    bytes32 public constant REP_MANAGER_ROLE = keccak256("REP_MANAGER_ROLE");

    mapping(address => uint256) public reputation;
    mapping(address => uint256) public lastUpdate;
    mapping(uint8 => TierConfig) public tierConfigs;

    uint256 public communityAvg;
    uint256 public memberCount;
    uint256 public totalRepTracked;

    uint256 public constant DECAYRATE = 5;
    uint256 public constant DECAY_CAP_PERCENT = 50;
    uint256 public constant ALPHA = 100;
    uint256 public constant MONTH = 30 days;

    event REPUpdated(address indexed member, uint256 oldREP, uint256 newREP, uint256 activityScore);
    event REPMinted(address indexed member, uint256 amount, uint256 totalREP);
    event TierConfigUpdated(uint8 indexed tier, uint256 minREP, string label);

    constructor() ERC721("Forge Reputation", "FREP") Ownable(msg.sender) {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(REP_MANAGER_ROLE, msg.sender);

        tierConfigs[0] = TierConfig(0, "Guest", false, false, false, false);
        tierConfigs[1] = TierConfig(10, "User", true, true, false, false);
        tierConfigs[2] = TierConfig(100, "Steward", true, true, true, false);
        tierConfigs[3] = TierConfig(500, "Root", true, true, true, true);
    }

    modifier onlyRepManager() {
        require(hasRole(REP_MANAGER_ROLE, msg.sender), "missing role");
        _;
    }

    function _updateCommunityAvg(int256 repDelta, bool isNewMember) internal {
        if (isNewMember) {
            memberCount += 1;
        }

        if (repDelta > 0) {
            totalRepTracked += uint256(repDelta);
        } else if (repDelta < 0) {
            uint256 absDelta = uint256(-repDelta);
            totalRepTracked = absDelta > totalRepTracked ? 0 : totalRepTracked - absDelta;
        }

        communityAvg = memberCount == 0 ? 0 : totalRepTracked / memberCount;
    }

    function mintREP(address member, uint256 amount) external onlyRepManager {
        require(member != address(0), "invalid member");
        require(amount > 0, "amount=0");

        bool isNewMember = reputation[member] == 0;
        uint256 tokenId = uint256(uint160(member));

        if (_ownerOf(tokenId) == address(0)) {
            _safeMint(member, tokenId);
        }

        reputation[member] += amount;
        lastUpdate[member] = block.timestamp;
        _updateCommunityAvg(int256(amount), isNewMember);

        emit REPMinted(member, amount, reputation[member]);
    }

    function updateREP(address member, uint256 activityScore) external onlyRepManager {
        require(member != address(0), "invalid member");
        uint256 oldRep = reputation[member];
        uint256 monthsElapsed = lastUpdate[member] == 0 ? 0 : (block.timestamp - lastUpdate[member]) / MONTH;
        uint256 rawDecay = (oldRep * DECAYRATE * monthsElapsed) / 100;
        uint256 maxDecay = (oldRep * DECAY_CAP_PERCENT) / 100;
        uint256 decay = rawDecay > maxDecay ? maxDecay : rawDecay;
        uint256 boost = communityAvg > 0 ? (ALPHA * activityScore) / communityAvg : 0;

        uint256 newRep = decay >= oldRep ? 0 : oldRep - decay;
        newRep += boost;

        reputation[member] = newRep;
        lastUpdate[member] = block.timestamp;

        int256 delta = int256(newRep) - int256(oldRep);
        _updateCommunityAvg(delta, oldRep == 0 && newRep > 0);

        emit REPUpdated(member, oldRep, newRep, activityScore);
    }

    function getTier(address member) public view returns (uint8) {
        uint256 rep = reputation[member];
        for (uint8 tier = 3; tier > 0; tier--) {
            if (rep >= tierConfigs[tier].minREP) {
                return tier;
            }
        }
        return 0;
    }

    function updateTierConfig(
        uint8 tier,
        uint256 minREP,
        string calldata label,
        bool canSpawnAgents,
        bool canVote,
        bool canPropose,
        bool hasEmergencyAccess
    ) external onlyRepManager {
        require(tier <= 3, "tier out of range");
        if (tier > 0) {
            require(minREP >= tierConfigs[tier - 1].minREP, "minREP < lower tier");
        }
        if (tier < 3) {
            require(minREP <= tierConfigs[tier + 1].minREP, "minREP > higher tier");
        }

        tierConfigs[tier] = TierConfig({
            minREP: minREP,
            label: label,
            canSpawnAgents: canSpawnAgents,
            canVote: canVote,
            canPropose: canPropose,
            hasEmergencyAccess: hasEmergencyAccess
        });

        emit TierConfigUpdated(tier, minREP, label);
    }

    function _update(address to, uint256 tokenId, address auth) internal override returns (address) {
        address from = _ownerOf(tokenId);
        require(from == address(0) || to == address(0), "Soulbound: non-transferable");
        return super._update(to, tokenId, auth);
    }

    function supportsInterface(bytes4 interfaceId) public view override(ERC721, AccessControl) returns (bool) {
        return super.supportsInterface(interfaceId);
    }
}
