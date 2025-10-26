use dep::poseidon::poseidon2::Poseidon2;

global N: u32 = 4;

#[export]
fn testw(embedding: [Field; N], enrolled: [Field; N], commitment_hash: Field) {
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
