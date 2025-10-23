// src/main.nr

// Import the specific bn254 module from the poseidon library
use dep::poseidon::poseidon::bn254;

// Define a global constant for the number of dimensions (compile-time)
global N: u32 = 128;

// Main function definition
// Takes three inputs:
// - embedding: The new 128D face embedding (private)
// - enrolled: The previously stored 128D face embedding (private)
// - commitment_hash: The public Poseidon hash of the 'enrolled' embedding
fn main(embedding: [Field; N], enrolled: [Field; N], commitment_hash: pub Field) {
    
    // Define a constant threshold for the maximum allowed distance
    let threshold: Field = 1_000_000;

    // --- Verification Step 1: Check Commitment ---
    
    // Calculate the Poseidon hash of the private 'enrolled' embedding.
    // The `sponge` function is used because the input (enrolled) is an array
    // longer than the fixed sizes (like hash_1, hash_2, etc.).
    let h = bn254::sponge(enrolled);
    
    // Assert that the calculated hash 'h' matches the public 'commitment_hash'.
    // If they don't match, the proof generation will fail with the message.
    // This proves that the 'enrolled' embedding provided privately is the
    // same one that was publicly committed to earlier.
    assert(h == commitment_hash, "commitment mismatch");

    // --- Verification Step 2: Check Distance ---
    
    // Initialize a variable to store the squared Euclidean distance.
    let mut dist: Field = 0;
    
    // Loop through each dimension of the embeddings (0 to 127).
    for i in 0..N {
        // Calculate the difference between the new and enrolled embedding
        // in this dimension.
        let d = embedding[i] - enrolled[i];
        
        // Add the square of the difference to the total distance.
        dist += d * d;
    }
    
    // Assert that the calculated squared distance 'dist' is less than
    // the predefined 'threshold'.
    // We use the `.lt()` method because direct '<' comparison isn't
    // defined for Field types.
    // If the distance is greater than or equal to the threshold, the proof
    // generation will fail. This proves that the new 'embedding' is
    // "close enough" to the 'enrolled' one.
    assert(dist.lt(threshold), "too far");
}