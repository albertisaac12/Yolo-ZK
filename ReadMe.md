# YoLo-Face - Current Progress

## Status

The **YoLo-Face** project integrates a YOLO-based face detection model with embedding generation, FAISS-based face search, and a zero-knowledge proof (zk-proof) verification flow.

- **Detection and embedding (Steps 1–2)** are fully implemented in `Face_To_Embedding.py`.
- **zk-proof and a basic smart contract** are implemented in the `server` branch.

---

## Project Overview

**YoLo-Face** is an end-to-end system for private face verification using computer vision and zero-knowledge proofs.
The pipeline combines:

- **YOLO** - for face detection (trained on the WIDER FACE dataset)
- **DeepFace/ArcFace** - for embedding extraction
- **FAISS** - for efficient face similarity search
- **zk-Proof** - for privacy-preserving verification
- **Smart Contract** - for on-chain validation and proof anchoring

---

## Repository Structure

### Key Scripts

| File | Description |
|------|--------------|
| `wider_to_yolo.py` | Converts WIDER FACE annotations into YOLO-style `.txt` label files. |
| `detect.py` | Utility script for environment and CUDA/PyTorch status checks. |
| `FaceDetectTest.py` | Loads a YOLO checkpoint and runs detection on test images or webcam input. |
| `Face_To_Embedding.py` | Implements the main capture → embedding → indexing pipeline using YOLO, ArcFace, and FAISS. |

### Additional Components

| Directory / File | Description |
|------------------|-------------|
| `runs/` | Training and inference outputs (e.g., `runs/detect/train3/weights/best.pt`). |
| `yolov8s.pt`, `yolo11n.pt` | Example pretrained model weights. |
| `server/` | Contains zk-proof implementation and a basic smart contract. |

---

## Dataset Layout

```
dataset/
├── images/
│   ├── train/
│   └── val/
├── labels/
│   ├── train/
│   └── val/
dataset_raw/
├── WIDER_train/
├── WIDER_val/
└── wider_face_split/
```

> Note: The dataset and images are not included in the repository due to size constraints.

---

## Completed Work

### Data Preparation
- Converted WIDER FACE annotations into YOLO-style label files using `wider_to_yolo.py`.

### Model Training
- Trained YOLO model for face detection.
- Training artifacts and best checkpoints are available in `runs/detect/...`.

### Face Detection & Embedding
- Implemented a unified capture and embedding pipeline in `Face_To_Embedding.py`.
- Components:
  - **Detection:** YOLO (PyTorch)
  - **Embedding:** ArcFace (via DeepFace)
  - **Indexing/Search:** FAISS

### Zero-Knowledge Proof Integration
- Implemented zk-proof generation and verification in the `server` branch.
- Proofs validate the integrity of face embeddings without revealing underlying data.

### Smart Contract
- Developed a basic smart contract (in `server` branch) for proof verification and on-chain proof storage.

---

## How to Reproduce the Pipeline

### 1. Convert WIDER Annotations
Edit paths in `wider_to_yolo.py`:

```python
source_label_file = "<path_to_annotation_file>"
images_base_dir = "<path_to_WIDER_images>"
target_dir = "<output_label_directory>"
```

Then run:
```bash
python wider_to_yolo.py
```

---

### 2. Check Environment / GPU
```bash
python detect.py
```

---

### 3. Run YOLO Inference
To perform inference using your trained model:
```bash
python FaceDetectTest.py
```
By default, the script loads a model from `runs/detect/...`.  
Adjust the model path as necessary.

---

### 4. Run Capture + Embedding (Interactive)
```bash
python Face_To_Embedding.py
```
This script:
- Opens the webcam feed.
- Detects faces in real time using YOLO.
- Allows:
  - **Registration** - press `r` to capture and store embeddings.
  - **Search/Verification** - press `s` to compare current faces against the database.
- Persists:
  - FAISS index: `face_db.index`
  - Label mapping: `face_labels.pkl`

---

## zk-Proof and Smart Contract

Both the **zk-proof system** and a **basic smart contract** for verification are implemented in the `server` branch.

The zk-proof component ensures that facial embeddings can be verified without exposing sensitive identity data, while the smart contract provides an on-chain validation interface for these proofs.

---

## Summary of Progress

| Stage | Description | Status |
|--------|-------------|---------|
| Data Conversion | WIDER → YOLO annotation format | ✅ Completed |
| Model Training | YOLO-based face detection | ✅ Completed |
| Embedding & Indexing | Capture, ArcFace embedding, FAISS search | ✅ Completed |
| zk-Proof System | Generation & verification pipeline | ✅ Completed |
| Smart Contract | On-chain proof validation | ✅ Completed |

---

## Next Steps

- Integrate zk-proof verification results directly into the embedding workflow.
- Extend smart contract logic for multi-user and decentralized verification.
- Optimize face embedding storage for scalability.

---


**Branches:**  
- `main` - training, detection, embedding pipeline
- `server` - zk-proof and smart contract implementation
