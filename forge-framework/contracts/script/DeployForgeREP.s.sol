// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Script.sol";
import "../ForgeREP.sol";

contract DeployForgeREP is Script {
    function run() external returns (ForgeREP deployed) {
        uint256 privateKey = vm.envUint("DEPLOYER_PRIVATE_KEY");
        vm.startBroadcast(privateKey);
        deployed = new ForgeREP();
        vm.stopBroadcast();
    }
}
