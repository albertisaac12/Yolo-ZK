// use dep::poseidon::poseidon2::Poseidon2;

// global N: u32 = 4;

// fn main(embedding: [Field; N]) -> pub Field {
//     // Compute Poseidon2 hash over the embedding array
//     let h = Poseidon2::hash(embedding, embedding.len());
//     h
// }
//===================================================================================//

use dep::poseidon::poseidon2::Poseidon2;

global N: u32 = 4; // Set it to 4 So that I can expriment with it revert back to 512

fn main(embedding: [Field; N], enrolled: [Field; N], commitment_hash: pub Field) {
    let threshold: Field = 10_000_000;

    // Use Poseidon2 hash instead of bn254::sponge
    let h = Poseidon2::hash(enrolled, enrolled.len());
    assert(h == commitment_hash, "commitment mismatch");

    let mut dist: Field = 0;
    for i in 0..N {
        let d = embedding[i] - enrolled[i];
        dist += d * d;
    }

    assert(dist.lt(threshold), "too far");
}



//==================================================

// Old Code

// use dep::poseidon::poseidon::bn254;

// // number of dims
// global N: u32 = 512;

// fn main(embedding: [Field; N], enrolled: [Field; N], commitment_hash: pub Field) {
//     let threshold: Field = 1_000_000;

//     // compute poseidon over enrolled embedding
//     let h = bn254::sponge(enrolled);
//     assert(h == commitment_hash, "commitment mismatch");

//     // distance check
//     let mut dist: Field = 0;
//     for i in 0..N {
//         let d = embedding[i] - enrolled[i];
//         dist += d * d;
//     }

//     // Use the .lt() method to compare Fields for less-than
//     assert(dist.lt(threshold), "too far");
// }

