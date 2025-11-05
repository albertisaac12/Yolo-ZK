import { network } from "hardhat";
import artifact from "../artifacts/contracts/Commitment.sol/ZKBioRegistry.json"
import { ethers as Ethers } from "ethers";

async function getProvider() {
    // ✅ If running from API — use JsonRpcProvider
    const provider = new Ethers.JsonRpcProvider("http://127.0.0.1:8545");
    return {
      provider,
      signerFactory: Ethers // so we can do new Contract
    };
}

async function main() {
  const { provider, signerFactory } = await getProvider();

  const contractAddress = "0x5FbDB2315678afecb367f032d93F642f64180aa3";

  // get signer (first account from Hardhat or RPC)
  const signer = await provider.getSigner(0);

  // attach contract
  const contract = new signerFactory.Contract(contractAddress, artifact.abi, provider);

  // call function
  const ret = await contract["reterieve"](1n);
  console.log("Retrieved:", ret.toString());
}

await main();
