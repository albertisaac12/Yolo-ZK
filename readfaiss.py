import faiss
import pickle
import numpy as np
import os

DB_PATH = "face_db.index"
LABELS_PATH = "face_labels.pkl"

def main():
    if not os.path.exists(DB_PATH) or not os.path.exists(LABELS_PATH):
        print("[!] No FAISS database or labels file found.")
        return

    # Load FAISS index
    print("[+] Loading FAISS index...")
    index = faiss.read_index(DB_PATH)

    # Load labels
    with open(LABELS_PATH, "rb") as f:
        labels = pickle.load(f)

    ntotal = index.ntotal
    dim = index.d

    print(f"\n=== FAISS Database Info ===")
    print(f"Total faces stored : {ntotal}")
    print(f"Embedding dimension: {dim}")
    print(f"Labels count       : {len(labels)}")

    # Sanity check
    if ntotal != len(labels):
        print("[⚠] Warning: number of embeddings and labels mismatch!")

    # Extract embeddings
    print("\n[+] Reading all vectors...")
    if hasattr(index, "xb"):
        vectors = faiss.vector_to_array(index.xb).reshape(ntotal, dim)
    else:
        vectors = np.array([index.reconstruct(i) for i in range(ntotal)])

    # Print embeddings
    print("\n=== Stored Faces ===")
    for i, label in enumerate(labels):
        print(f"\n[{i}] Label: {label}")
        print(f"Embedding (first 10 dims): {vectors[i][:]}")
        # Uncomment below line to print the full 512-dim vector
        # print(vectors[i])

    print("\n[✓] Done.")

if __name__ == "__main__":
    main()
