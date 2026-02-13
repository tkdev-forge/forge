// Hardhat deployment script for ForgeREP_RLI contract
// Usage: npx hardhat run scripts/deploy-rli-extension.js --network optimism-sepolia

const hre = require("hardhat");
const fs = require('fs');
const path = require('path');

async function main() {
  console.log("\n=== Deploying ForgeREP_RLI Extension ===");
  
  // Get deployer account
  const [deployer] = await ethers.getSigners();
  console.log("Deploying with account:", deployer.address);
  console.log("Account balance:", (await deployer.getBalance()).toString());
  
  // Configuration
  const config = {
    linkToken: process.env.LINK_TOKEN || "0x779877A7B0D9E8603169DdbD7836e478b4624789", // Sepolia LINK
    chainlinkOracle: process.env.CHAINLINK_ORACLE || "0x0000000000000000000000000000000000000000",
    jobId: process.env.CHAINLINK_JOB_ID || ethers.utils.formatBytes32String("rli-eval-001")
  };
  
  console.log("\nConfiguration:");
  console.log("  LINK Token:", config.linkToken);
  console.log("  Oracle:", config.chainlinkOracle);
  console.log("  Job ID:", config.jobId);
  
  // Deploy ForgeREP_RLI
  console.log("\nDeploying ForgeREP_RLI...");
  const ForgeREP_RLI = await ethers.getContractFactory("ForgeREP_RLI");
  const rliContract = await ForgeREP_RLI.deploy(
    config.linkToken,
    config.chainlinkOracle,
    config.jobId
  );
  
  await rliContract.deployed();
  console.log("✅ ForgeREP_RLI deployed to:", rliContract.address);
  
  // Save deployment info
  const deploymentInfo = {
    network: hre.network.name,
    contract: "ForgeREP_RLI",
    address: rliContract.address,
    deployer: deployer.address,
    timestamp: new Date().toISOString(),
    config: config,
    transactionHash: rliContract.deployTransaction.hash
  };
  
  const outputPath = path.join(__dirname, '../deployments', `rli-${hre.network.name}.json`);
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, JSON.stringify(deploymentInfo, null, 2));
  
  console.log("\n📝 Deployment info saved to:", outputPath);
  
  // Verify on Etherscan (if not local network)
  if (hre.network.name !== "hardhat" && hre.network.name !== "localhost") {
    console.log("\n⏳ Waiting for block confirmations before verification...");
    await rliContract.deployTransaction.wait(6);
    
    console.log("\n🔍 Verifying contract on Etherscan...");
    try {
      await hre.run("verify:verify", {
        address: rliContract.address,
        constructorArguments: [
          config.linkToken,
          config.chainlinkOracle,
          config.jobId
        ]
      });
      console.log("✅ Contract verified!");
    } catch (error) {
      console.log("⚠️  Verification failed:", error.message);
    }
  }
  
  // Display next steps
  console.log("\n=== Next Steps ===");
  console.log("1. Update config/rli/rli-oracle.json with contract address");
  console.log("2. Configure Chainlink oracle job (if not already done)");
  console.log("3. Run database migration: psql -f migrations/002_rli_extensions.sql");
  console.log("4. Start RLI oracle backend: python -m backend.layers.layer6_reputation.rli.rli_oracle");
  console.log("5. Test integration: pytest tests/integration/test_rli_flow_e2e.py");
  
  console.log("\n✨ Deployment complete!\n");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
