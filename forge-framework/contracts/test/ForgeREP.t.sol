// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Test.sol";
import "../ForgeREP.sol";

contract ForgeREPTest is Test {
    ForgeREP internal rep;
    address internal admin = address(this);
    address internal manager = address(0xABCD);
    address internal alice = address(0xA11CE);

    function setUp() public {
        rep = new ForgeREP();
        rep.grantRole(rep.REP_MANAGER_ROLE(), manager);
    }

    function testInitialTierConfig() public view {
        (uint256 minRep0,,,,,) = rep.tierConfigs(0);
        (uint256 minRep1,,,,,) = rep.tierConfigs(1);
        (uint256 minRep2,,,,,) = rep.tierConfigs(2);
        (uint256 minRep3,,,,,) = rep.tierConfigs(3);

        assertEq(minRep0, 0);
        assertEq(minRep1, 10);
        assertEq(minRep2, 100);
        assertEq(minRep3, 500);
    }

    function testMintAndTierProgression() public {
        vm.prank(manager);
        rep.mintREP(alice, 600);

        assertEq(rep.reputation(alice), 600);
        assertEq(rep.getTier(alice), 3);
        assertEq(rep.ownerOf(uint256(uint160(alice))), alice);
    }

    function testDecayCapMax50Percent() public {
        vm.startPrank(manager);
        rep.mintREP(alice, 1000);

        vm.warp(block.timestamp + (11 * rep.MONTH()));
        rep.updateREP(alice, 0);
        vm.stopPrank();

        assertEq(rep.reputation(alice), 500, "decay should cap at 50%");
    }

    function testUpdateRepWithBoostFromCommunityAverage() public {
        address bob = address(0xB0B);
        vm.startPrank(manager);
        rep.mintREP(alice, 100);
        rep.mintREP(bob, 100);

        vm.warp(block.timestamp + rep.MONTH());
        rep.updateREP(alice, 50);
        vm.stopPrank();

        // old 100 - 5 decay + (100*50/100) boost = 145
        assertEq(rep.reputation(alice), 145);
    }

    function testOnlyRoleCanMintAndUpdate() public {
        vm.expectRevert("missing role");
        rep.mintREP(alice, 10);

        vm.prank(manager);
        rep.mintREP(alice, 10);

        vm.expectRevert("missing role");
        rep.updateREP(alice, 1);
    }

    function testTierConfigEdgeCases() public {
        vm.prank(manager);
        rep.updateTierConfig(1, 11, "User+", true, true, false, false);
        assertEq(rep.getTier(alice), 0);

        vm.prank(manager);
        rep.mintREP(alice, 11);
        assertEq(rep.getTier(alice), 1);
    }

    function testTierConfigGuardrailsRevert() public {
        vm.prank(manager);
        vm.expectRevert("minREP < lower tier");
        rep.updateTierConfig(2, 5, "Bad", true, true, true, false);

        vm.prank(manager);
        vm.expectRevert("tier out of range");
        rep.updateTierConfig(4, 1000, "Bad", true, true, true, false);
    }

    function testSoulboundTransferBlocked() public {
        vm.prank(manager);
        rep.mintREP(alice, 10);

        vm.prank(alice);
        vm.expectRevert("Soulbound: non-transferable");
        rep.transferFrom(alice, address(0x9999), uint256(uint160(alice)));
    }
}
