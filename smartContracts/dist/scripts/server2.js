import express from "express";
import { Barretenberg, Fr, UltraHonkBackend } from "@aztec/bb.js";
import { Noir } from "@noir-lang/noir_js";
import { network } from "hardhat";
import fs from "fs";
// ---- Express Config ----
const app = express();
app.use(express.json({ limit: "10mb" }));
// ---- Constants ----
const SCALE = 1e6;
const SHIFT = 1;
const FIELD_PRIME = BigInt("21888242871839275222246405745257275088548364400416034343698204186575808495617");
// ---- Poseidon Initialize ----
let api;
(async () => {
    console.log("[+] Initializing Poseidon...");
    api = await Barretenberg.new({ threads: 4 });
    console.log("[+] Poseidon Ready ✅");
})();
// ---- Hardhat Connect ----
const { ethers } = await network.connect();
const [sender] = await ethers.getSigners();
const address = fs.readFileSync("zkbio-address.txt", "utf8").trim();
const Contract = await ethers.getContractFactory("ZKBioRegistry");
const contract = Contract.attach(address);
console.log(`[+] Using contract: ${address}`);
// ---- Noir + Backend ----
// ESM JSON import
// import circuitData from "./../../embedding_proof_2/circuit/target/embedding_proof_2.json";
// // Explicitly cast it
// const circuit: any = circuitData;
// import fs from "fs";

const circuit = JSON.parse(
  fs.readFileSync(new URL("./../embedding_proof_2/circuit/target/embedding_proof_2.json", import.meta.url))
);


const noir = new Noir(circuit);
const backend = new UltraHonkBackend(circuit.bytecode);
// ===============================================
// 🧠 1. COMMIT ENDPOINT — /face-data
// ===============================================
app.post("/face-data", async (req, res) => {
    try {
        const { face_index, embedding } = req.body;
        if (!embedding)
            return res.status(400).json({ error: "embedding missing" });
        console.log(`[+] Received embedding length = ${embedding.length}`);
        // Float → BigInt (shift + scale)
        const embeddingBigInt = embedding.map((x) => BigInt(Math.floor((x + SHIFT) * SCALE)));
        // BigInt → Fr[]
        const fieldElements = embeddingBigInt.map((x) => new Fr(x % FIELD_PRIME));
        // Poseidon2 Hash
        const hashFr = await api.poseidon2Hash(fieldElements);
        const hash = BigInt(hashFr.toString());
        console.log("===============================================");
        console.log("Poseidon2 Hash (Fr format):");
        console.log(hash.toString());
        console.log("===============================================");
        const id = BigInt(face_index ?? 0n);
        // Commit to chain
        const tx = await contract.connect(sender).commit(id, hash);
        await tx.wait();
        console.log(`[✓] Commit successful for ID=${id}, hash=${hash}`);
        return res.status(200).json({
            status: "committed",
            id: id.toString(),
            hash: hash.toString(),
            txHash: tx.hash,
        });
    }
    catch (err) {
        console.error("❌ ERROR:", err);
        return res.status(500).json({ error: err.toString() });
    }
});
// ===============================================
// 🧩 2. VERIFY ENDPOINT — /face-verify
// ===============================================
app.post("/face-verify", async (req, res) => {
    try {
        const { face_index, embedding, enrolled } = req.body;
        if (!embedding || !enrolled)
            return res.status(400).json({ error: "embedding or enrolled missing" });
        const id = BigInt(face_index ?? 0n);
        console.log(`[+] Verifying for ID=${id}`);
        // Fetch on-chain commitment
        const commitment_hash = await contract.reterieve(id);
        console.log(`[+] On-chain commitment hash: ${commitment_hash.toString()}`);
        // Float → scaled field strings for Noir input
        const embeddingStr = embedding.map((x) => Math.floor((x + SHIFT) * SCALE).toString());
        const enrolledStr = enrolled.map((x) => Math.floor((x + SHIFT) * SCALE).toString());
        // Generate witness
        console.log("🔹 Generating witness...");
        const { witness } = await noir.execute({
            embedding: embeddingStr,
            enrolled: enrolledStr,
            commitment_hash: commitment_hash.toString(),
        });
        console.log("✅ Witness generated");
        // Generate proof
        console.log("🔹 Generating proof...");
        const proof = await backend.generateProof(witness);
        console.log("✅ Proof generated");
        // Verify proof
        console.log("🔹 Verifying proof...");
        const isValid = await backend.verifyProof(proof);
        console.log(`✅ Proof is ${isValid ? "valid ✅" : "invalid ❌"}`);
        if (isValid) {
            return res.status(200).json({
                status: "verified",
                id: id.toString(),
                commitment_hash: commitment_hash.toString(),
            });
        }
        else {
            return res.status(400).json({ status: "failed", reason: "invalid proof" });
        }
    }
    catch (err) {
        console.error("❌ ERROR:", err);
        return res.status(500).json({ error: err.toString() });
    }
});
// ===============================================
// 🚀 Start Server
// ===============================================
app.listen(5000, () => {
    console.log("🚀 Face → Hash → Commit/Verify server running on :5000");
});
