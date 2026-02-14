// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract ForgePolicy {
    uint256 public constant MIN_DECAY = 1;
    uint256 public constant MAX_DECAY = 10;
    uint256 public constant MIN_BOOSTER = 50;
    uint256 public constant MAX_BOOSTER = 200;

    uint256 public decayRate = 5;
    uint256 public activityBooster = 100;
    uint256 public communityAvgWindowDays = 30;

    address public dao;

    event PolicyUpdated(string key, uint256 value);

    modifier onlyDAO() {
        require(msg.sender == dao, "only DAO");
        _;
    }

    constructor(address daoAddress) {
        dao = daoAddress;
    }

    function updateDecayRate(uint256 newRate) external onlyDAO {
        require(newRate >= MIN_DECAY && newRate <= MAX_DECAY, "out of range");
        decayRate = newRate;
        emit PolicyUpdated("decayRate", newRate);
    }

    function updateBooster(uint256 newBooster) external onlyDAO {
        require(newBooster >= MIN_BOOSTER && newBooster <= MAX_BOOSTER, "out of range");
        activityBooster = newBooster;
        emit PolicyUpdated("activityBooster", newBooster);
    }

    function updateCommunityAvgWindow(uint256 days_) external onlyDAO {
        require(days_ > 0 && days_ <= 365, "invalid window");
        communityAvgWindowDays = days_;
        emit PolicyUpdated("communityAvgWindowDays", days_);
    }
}
