// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Test.sol";
import "../ForgeREP_RLI.sol";

contract LinkTokenMock {
    function transferAndCall(address, uint256, bytes calldata) external pure returns (bool) {
        return true;
    }
}

contract ForgeREPRLITest is Test {
    ForgeREP_RLI internal repRli;
    LinkTokenMock internal link;

    address internal admin = address(this);
    address internal evaluator = address(0xEVA1);
    address internal oracle = address(0x0B0B);
    address internal member = address(0xA11CE);

    function setUp() public {
        link = new LinkTokenMock();
        repRli = new ForgeREP_RLI(address(link), oracle, bytes32("job-1"), 0.1 ether, 3);
        repRli.grantRole(repRli.EVALUATOR_ROLE(), evaluator);
    }

    function testOnlyEvaluatorCanRequest() public {
        vm.expectRevert();
        repRli.requestRLIEvaluation(member, "task-1", "ops", "QmHash");
    }

    function testFormulaUsesIntegerMathAndRoundingDown() public {
        vm.prank(evaluator);
        bytes32 reqId = repRli.requestRLIEvaluation(member, "task-1", "ops", "QmHash");

        vm.prank(oracle);
        repRli.fulfillRLIEvaluation(reqId, 33333, true, 1137, 999);

        // base = floor(33333 * 999 / 100000) = 332
        // elo bonus = floor((1137 - 1000) / 10) = 13
        // total = 345
        assertEq(repRli.reputation(member), 345);

        ForgeREP_RLI.RLIEvaluation[] memory history = repRli.getRLIHistory(member);
        assertEq(history.length, 1);
        assertEq(history[0].repEarned, 345);
    }

    function testMissingEloScoreUsesBaseline() public {
        vm.prank(evaluator);
        bytes32 reqId = repRli.requestRLIEvaluation(member, "task-2", "ops", "QmHash");

        vm.prank(oracle);
        repRli.fulfillRLIEvaluation(reqId, 50000, false, 0, 1000);

        assertEq(repRli.reputation(member), 500);
    }

    function testZeroEconomicValueYieldsZeroReward() public {
        vm.prank(evaluator);
        bytes32 reqId = repRli.requestRLIEvaluation(member, "task-3", "ops", "QmHash");

        vm.prank(oracle);
        repRli.fulfillRLIEvaluation(reqId, 100000, true, 1800, 0);

        assertEq(repRli.reputation(member), 0);
    }

    function testAutomationRateIsCappedAtScale() public {
        vm.prank(evaluator);
        bytes32 reqId = repRli.requestRLIEvaluation(member, "task-4", "ops", "QmHash");

        vm.prank(oracle);
        repRli.fulfillRLIEvaluation(reqId, 150000, true, 1000, 200);

        assertEq(repRli.reputation(member), 200);
    }

    function testRewardIsCapped() public {
        vm.prank(evaluator);
        bytes32 reqId = repRli.requestRLIEvaluation(member, "task-5", "ops", "QmHash");

        vm.prank(oracle);
        repRli.fulfillRLIEvaluation(reqId, 100000, true, 5000, 2_500_000);

        assertEq(repRli.reputation(member), repRli.MAX_REP_REWARD());
    }

    function testCancelExpiredRequestRefundsBudget() public {
        vm.prank(evaluator);
        bytes32 reqId = repRli.requestRLIEvaluation(member, "task-6", "ops", "QmHash");

        assertEq(repRli.remainingEvaluations(), 2);

        vm.warp(block.timestamp + repRli.ORACLE_TIMEOUT() + 1);
        repRli.cancelExpiredRequest(reqId);

        assertEq(repRli.remainingEvaluations(), 3);
        (,,,, bool exists) = repRli.pendingRequests(reqId);
        assertFalse(exists);
    }

    function testCannotCancelBeforeTimeout() public {
        vm.prank(evaluator);
        bytes32 reqId = repRli.requestRLIEvaluation(member, "task-7", "ops", "QmHash");

        vm.expectRevert("request active");
        repRli.cancelExpiredRequest(reqId);
    }
}
