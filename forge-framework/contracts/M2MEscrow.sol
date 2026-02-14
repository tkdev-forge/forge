// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract M2MEscrow {
    event TradeExecuted(bytes32 indexed txHash, address indexed buyer, address indexed seller, string resource, uint256 amount, uint256 price);

    function executeTrade(address buyer, address seller, string calldata resource, uint256 amount, uint256 price)
        external
        payable
        returns (bytes32 txHash)
    {
        require(msg.sender == buyer, "caller must be buyer");
        require(msg.value == price, "wrong payment amount");
        require(seller != address(0), "invalid seller");

        (bool ok, ) = payable(seller).call{value: price}("");
        require(ok, "payment failed");

        txHash = keccak256(abi.encodePacked(block.chainid, buyer, seller, resource, amount, price, block.timestamp));
        emit TradeExecuted(txHash, buyer, seller, resource, amount, price);
    }
}
