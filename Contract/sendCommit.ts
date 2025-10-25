import axios from "axios";
import { task } from "hardhat/config";

// You can keep this file in /scripts or run it directly with hardhat run
const BASE_URL = "http://localhost:3000";

// Helper to send commit
async function sendCommit(id: bigint, hash: bigint) {
  const res = await axios.post(`${BASE_URL}/commit`, {
    id: id.toString(),
    hash: hash.toString(),
  });
  console.log("Commit Response:", res.data);
}

// Helper to retrieve
async function retrieveCommit(id: bigint) {
  const res = await axios.get(`${BASE_URL}/retrieve/${id.toString()}`);
  console.log("Retrieve Response:", res.data);
}

// Entry point for Hardhat
async function main() {
  const args = process.argv.slice(2); // after script name
  const action = args[0];             // "commit" or "retrieve"
  const idArg = args[1];
  const hashArg = args[2];

  if (!action || !idArg) {
    console.error("Usage:");
    console.error("  npx hardhat run scripts/sendCommit.ts --network localhost commit <id> <hash>");
    console.error("  npx hardhat run scripts/sendCommit.ts --network localhost retrieve <id>");
    process.exit(1);
  }

  const id = BigInt(idArg);

  if (action === "commit") {
    if (!hashArg) {
      console.error("Missing hash for commit");
      process.exit(1);
    }
    const hash = BigInt(hashArg);
    await sendCommit(id, hash);
  } else if (action === "retrieve") {
    await retrieveCommit(id);
  } else {
    console.error("Invalid action. Use 'commit' or 'retrieve'.");
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
