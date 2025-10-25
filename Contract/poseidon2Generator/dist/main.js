import { Barretenberg, Fr } from "@aztec/bb.js";
async function main() {
    // Initialize Barretenberg WASM backend
    const api = await Barretenberg.new({ threads: 4 });
    // Example embedding (replace with real 512D embedding)
    const embedding = Array.from({ length: 512 }, (_, i) => BigInt(i + 1));
    // Convert bigint[] → Fr[]
    const fieldElements = embedding.map((x) => new Fr(x));
    // Poseidon2 hash
    const hash = await api.poseidon2Hash(fieldElements);
    console.log("===============================================");
    console.log("Poseidon2 Hash (Fr format):");
    console.log(hash.toString());
    console.log("===============================================");
}
main().catch(console.error);
// 0x130bf204a32cac1f0ace56c78b731aa3809f06df2731ebcf6b3464a15788b1b9
// 0x130bf204a32cac1f0ace56c78b731aa3809f06df2731ebcf6b3464a15788b1b9
