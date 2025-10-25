import express, { Request, Response } from "express";
import { network } from "hardhat";
import fs from "fs";

const { ethers } = await network.connect();

const app = express();
app.use(express.json());

// Helper: get the deployed contract address
function getDeployedAddress(): string {
  const path = "zkbio-address.txt";
  if (!fs.existsSync(path)) {
    throw new Error("zkbio-address.txt not found. Please deploy the contract first.");
  }
  return fs.readFileSync(path, "utf-8").trim();
}

// Helper: get the contract instance
async function getContract() {
  const address = getDeployedAddress();
  const [signer] = await ethers.getSigners();
  const Contract = await ethers.getContractFactory("ZKBioRegistry");
  return Contract.attach(address).connect(signer);
}

// POST /commit
app.post("/commit", async (req: Request, res: Response) => {
  try {
    const { id, hash } = req.body;

    if (id === undefined || hash === undefined) {
      return res.status(400).json({ error: "Missing 'id' or 'hash' in request body" });
    }

    const contract = await getContract();
    const tx = await contract.commit(BigInt(id), BigInt(hash));
    await tx.wait();

    console.log(`Committed id=${id}, hash=${hash}`);
    res.json({ message: "Commit successful", transactionHash: tx.hash });
  } catch (error: any) {
    console.error(error);
    res.status(500).json({ error: error.message });
  }
});

// GET /retrieve/:id
app.get("/retrieve/:id", async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const contract = await getContract();
    const value = await contract.reterieve(BigInt(id));
    res.json({ id, value: value.toString() });
  } catch (error: any) {
    console.error(error);
    res.status(500).json({ error: error.message });
  }
});

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
