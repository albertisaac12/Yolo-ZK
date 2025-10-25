import { network } from "hardhat";
import hre from "hardhat";
import fs from "fs";

const { ethers } = await network.connect();

async function main() {
  const [sender] = await ethers.getSigners();

  const address = fs.readFileSync("zkbio-address.txt", "utf-8").trim();
  console.log("Using contract at:", address);

  const Contract = await ethers.getContractFactory("ZKBioRegistry");
  const contract = Contract.attach(address);

  await contract.connect(sender).commit(1n, 1000n);
  console.log("Commit successful");

  const value = await contract.reterieve(1n);
  console.log("Retrieved:", value.toString());
}

await main();
