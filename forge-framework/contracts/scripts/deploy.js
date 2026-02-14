const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying with:", deployer.address);

  const ForgeREP = await hre.ethers.getContractFactory("ForgeREP");
  const rep = await ForgeREP.deploy();
  await rep.waitForDeployment();

  const ForgeDAO = await hre.ethers.getContractFactory("ForgeDAO");
  const dao = await ForgeDAO.deploy(await rep.getAddress());
  await dao.waitForDeployment();

  const ForgePolicy = await hre.ethers.getContractFactory("ForgePolicy");
  const policy = await ForgePolicy.deploy(await dao.getAddress());
  await policy.waitForDeployment();

  const M2MEscrow = await hre.ethers.getContractFactory("M2MEscrow");
  const escrow = await M2MEscrow.deploy();
  await escrow.waitForDeployment();

  const Prediction = await hre.ethers.getContractFactory("PredictionMarketEngine");
  const prediction = await Prediction.deploy(await rep.getAddress());
  await prediction.waitForDeployment();

  const MetaBridge = await hre.ethers.getContractFactory("MetaBridge");
  const metaBridge = await MetaBridge.deploy();
  await metaBridge.waitForDeployment();

  const L3 = await hre.ethers.getContractFactory("L3RollupManager");
  const l3 = await L3.deploy();
  await l3.waitForDeployment();

  console.log({
    ForgeREP: await rep.getAddress(),
    ForgeDAO: await dao.getAddress(),
    ForgePolicy: await policy.getAddress(),
    M2MEscrow: await escrow.getAddress(),
    PredictionMarketEngine: await prediction.getAddress(),
    MetaBridge: await metaBridge.getAddress(),
    L3RollupManager: await l3.getAddress()
  });
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
