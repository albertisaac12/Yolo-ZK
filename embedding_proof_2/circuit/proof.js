// import { Noir } from "@noir-lang/noir_js";
// import { UltraHonkBackend } from "@aztec/bb.js";
// import {circuit} from "./target/circuit.json";

const {Noir} = require("@noir-lang/noir_js");
const {UltraHonkBackend} = require("@aztec/bb.js");
const circuit = require("./target/embedding_proof_2.json");

async function main() {
  try {
    console.log("⏳ Initializing Noir and Barretenberg backend...");
    const noir = new Noir(circuit);
    const backend = new UltraHonkBackend(circuit.bytecode);

    const commitment_hash = "0x130bf204a32cac1f0ace56c78b731aa3809f06df2731ebcf6b3464a15788b1b9";
    const embedding = ["1", "2", "3", "4"];
    const enrolled = ["1", "2", "3", "4"];

    console.log("🔹 Generating witness...");
    const { witness } = await noir.execute({ embedding,enrolled,commitment_hash });
    console.log("✅ Witness generated");

    console.log("🔹 Generating proof...");
    const proof = await backend.generateProof(witness);
    console.log("✅ Proof generated");

    console.log("🔹 Verifying proof...");
    const isValid = await backend.verifyProof(proof);
    console.log(`✅ Proof is ${isValid ? "valid ✅" : "invalid ❌"}`);
  } catch (err) {
    console.error("❌ Error:", err);
  }
}

main();
