import { network } from "hardhat";
import hre from "hardhat";
import fs from "fs";

const { ethers } = await network.connect();

async function main() {
  const [signer] = await ethers.getSigners();
  const Contract = await ethers.getContractFactory("ZKBioRegistry");
  const dp = await Contract.deploy(signer.address);
  await dp.waitForDeployment();

  const address = await dp.getAddress();
  console.log("Contract Deployed At:", address);

  fs.writeFileSync("zkbio-address.txt", address);
  console.log("Address saved to zkbio-address.txt");
}

await main();
