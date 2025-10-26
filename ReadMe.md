# Poseidon Hash Generation and Noir Integration

## Overview

This repository documents my work in building and debugging the Poseidon-based hashing circuit for **ZK-Bio**, a zero-knowledge component designed for embedding and proof verification.
The main challenge I faced was generating the same **Poseidon (bn254 sponge)** hash **outside Noir** as the one produced **inside the circuit**.

This README explains that journey — from the initial implementation and debugging attempts to using **Noir AI** to finally achieve consistency with `Poseidon2`.

---

## Background

The first working version of the circuit used Noir’s internal `bn254::sponge` function:

```rust
use dep::poseidon::poseidon::bn254;

global N: u32 = 512;

fn main(embedding: [Field; N], enrolled: [Field; N], commitment_hash: pub Field) {
    let threshold: Field = 1_000_000;

    let h = bn254::sponge(enrolled);
    assert(h == commitment_hash, "commitment mismatch");

    let mut dist: Field = 0;
    for i in 0..N {
        let d = embedding[i] - enrolled[i];
        dist += d * d;
    }

    assert(dist.lt(threshold), "too far");
}
```

Inside Noir, this worked fine. However, I wasn’t able to find any working method to **generate the same `commitment_hash` outside Noir**, which meant external proof verification wasn’t possible.

---

## How I Solved It

After being stuck for a while, I turned to **Noir AI** (the assistant integrated in the Noir_Lang documentation). Noir AI analyzed the issue, then suggested migrating to **Poseidon2**.

I followed that advice, rewrote the circuit, and reduced the embedding size (`N`) from 512 to 4 for faster local testing.

---

## Updated Circuit (Poseidon2)

```rust
use dep::poseidon::poseidon2::Poseidon2;

global N: u32 = 4; // experimental mode; revert to 512 for production

fn main(embedding: [Field; N], enrolled: [Field; N], commitment_hash: pub Field) {
    let threshold: Field = 10_000_000;

    // Poseidon2 hash over enrolled embeddings
    let h = Poseidon2::hash(enrolled, enrolled.len());
    assert(h == commitment_hash, "commitment mismatch");

    let mut dist: Field = 0;
    for i in 0..N {
        let d = embedding[i] - enrolled[i];
        dist += d * d;
    }

    assert(dist.lt(threshold), "too far");
}
```

This change immediately resolved the mismatch. The Poseidon2 hash generated **outside Noir** (using a standard Poseidon2 library) matched exactly with the one computed **inside Noir**.

For off-chain generation, I used **bb.js** from the Aztec repository to compute the Poseidon2 hash. This can be found under `poseidon2Generator/src/main.ts`.

After this in `embedding_proof/` I ran the following command to check if the generated proof worked

```bash
nargo execute
```

```plaintext
Output

[embedding_proof] Circuit witness successfully solved
[embedding_proof] Witness saved to target/embedding_proof.gz
```

---

## Using Noir Codegen

Once the Poseidon2 circuit worked correctly, I attempted to integrate it into TypeScript using **Noir Codegen**. The goal was to automate proof generation and circuit execution through TypeScript bindings.

I followed the official guide from [Noir-Lang Docs](https://noir-lang.org/docs/reference/noir_codegen) and created a library under `embedding-to-ts/`.

I renamed the exported function to `testw` and generated the ABI JSON using:

```bash
nargo export
```

Then, I used Noir Codegen to generate the TypeScript bindings:

```bash
yarn noir-codegen embedding-to-ts/export/testw.json --out-dir poseidon2Generator/src
```

This successfully generated an `index.ts` file. However, since my `testw` function did not return a value, the Codegen tool produced an incorrect return type.

---

### Issue in Generated TypeScript Code

In `poseidon2Generator/src/index.ts`, the generated code looked like this:

```typescript
export async function testw(embedding: Field[], enrolled: Field[], commitment_hash: Field, foreignCallHandler?: ForeignCallHandler): Promise<null> {
  const program = new Noir(testw_circuit);
  const args: InputMap = { embedding, enrolled, commitment_hash };
  const { returnValue } = await program.execute(args, foreignCallHandler);

  return returnValue as null; //  Incorrect return type
}
```

The correct version should have been:

```typescript
return returnValue as unknown as null;
```

I manually fixed this type issue and proceeded with further testing.

---

## Testing the Exported Circuit

After fixing the return type, I created a test script `poseidon2Generator/src/export_test.ts`:

```typescript
import { testw } from "./index";

async function main() {
  const embedding = ["1", "2", "3", "4"];
  const enrolled = ["1", "2", "3", "4"];
  const commitment_hash = "0x130bf204a32cac1f0ace56c78b731aa3809f06df2731ebcf6b3464a15788b1b9"; // Generated from main.ts

  await testw(embedding, enrolled, commitment_hash);
  console.log("✅ Circuit executed successfully");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
```

When running the command:

```bash
npx ts-node poseidon2Generator/src/export_test.ts
```

The following error appeared:

```plaintext
Error: Failed to deserialize circuit. This is likely due to differing serialization formats between ACVM_JS and your compiler
    at module.exports.__wbg_constructor_590e27d4519f5f72 (/node_modules/@noir-lang/acvm_js/nodejs/acvm_js.js:558:17)
    at wasm://wasm/... (several wasm function traces)
```

```plaintext
Complete Error

Error: Failed to deserialize circuit. This is likely due to differing serialization formats between ACVM_JS and your compiler
    at module.exports.__wbg_constructor_590e27d4519f5f72 (poseidon2Generator/node_modules/@noir-lang/acvm_js/nodejs/acvm_js.js:558:17)
    at wasm://wasm/00b12d12:wasm-function[377]:0x1d1cf1
    at wasm://wasm/00b12d12:wasm-function[474]:0x1eb6d4
    at wasm://wasm/00b12d12:wasm-function[389]:0x1d518b
    at wasm://wasm/00b12d12:wasm-function[669]:0x222ad0
    at wasm://wasm/00b12d12:wasm-function[1774]:0x283f4d
    at wasm://wasm/00b12d12:wasm-function[1845]:0x28d469
    at __wbg_adapter_30 (poseidon2Generator/node_modules/@noir-lang/acvm_js/nodejs/acvm_js.js:531:10)
    at real (poseidon2Generator/node_modules/@noir-lang/acvm_js/nodejs/acvm_js.js:125:20)
    at node:internal/process/task_queues:151:7 {
  callStack: undefined,
  rawAssertionPayload: undefined,
  acirFunctionId: undefined,
  brilligFunctionId: undefined,
  noirCallStack: undefined
}
```

## Current Status

At this stage, the TypeScript bindings compile and load correctly, but circuit execution via `acvm_js` fails due to a version mismatch between the compiler and runtime libraries. This requires further debugging — likely involving rebuilding the Noir circuit using the same version as `acvm_js` or updating the JS dependencies.

Following this, I reached out on **LinkedIn** to get additional input from other developers in the Noir and ZK ecosystem for further debugging assistance.
