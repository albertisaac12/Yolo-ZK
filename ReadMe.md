# YoLo-Face — Current Progress

Status: A YOLO-based face detector has been trained and inference is working. Capture and embedding (steps 1–2) are implemented in `FaceDetectEmbedding3.py`. The next planned step is to design and implement the zk-proof over embeddings (step 3).

## Project overview

This repository contains code and data for training and running a YOLO-based face detector (trained on WIDER FACE → YOLO labels) and for preparing data for downstream face-embedding and zk-proof steps.

Key scripts and files

- `wider_to_yolo.py` — utilities to convert WIDER FACE annotations into YOLO-style `.txt` label files.
- `FaceDetectTest.py` — example script that loads the trained YOLO model and runs detection (used for quick inference/camera tests).
- `detect.py` — small checks and detection utilities (prints PyTorch/CUDA status in this workspace).
- `runs/` — training and inference outputs, including checkpoints (e.g. `runs/detect/train3/weights/best.pt`).
- `yolov8s.pt`, `yolo11n.pt` — model weight files present in the repository.

Dataset layout

- `dataset/images/train/`, `dataset/images/val/` — images prepared for training/validation.
- `dataset/labels/train/`, `dataset/labels/val/` — YOLO label files generated from WIDER annotations.
- `dataset_raw/` — original WIDER FACE archive and annotation files (`wider_face_split/`, `WIDER_train/`, `WIDER_val/`).

## What has been done

- Converted (or prepared conversion) of WIDER FACE annotations to YOLO format using `wider_to_yolo.py`.
- Trained a YOLO model — outputs and checkpoints are in `runs/detect/...`.
# YoLo-Face — Current Progress

Status: A YOLO-based face detector has been trained and inference is working. The next planned steps are: capture detected faces, convert them into embeddings, and generate zk-proofs over those embeddings.

## Project overview

This repository contains code and data for training and running a YOLO-based face detector (trained on WIDER FACE → YOLO labels) and for preparing data for downstream face-embedding and zk-proof steps.

Key scripts and files

- `wider_to_yolo.py` — utilities to convert WIDER FACE annotations into YOLO-style `.txt` label files.
- `FaceDetectTest.py` — example script that loads the trained YOLO model and runs detection (used for quick inference/camera tests).
- `detect.py` — small checks and detection utilities (prints PyTorch/CUDA status in this workspace).
- `runs/` — training and inference outputs, including checkpoints (e.g. `runs/detect/train3/weights/best.pt`).
- `yolov8s.pt`, `yolo11n.pt` — model weight files present in the repository.

Dataset layout

- `dataset/images/train/`, `dataset/images/val/` — images prepared for training/validation.
- `dataset/labels/train/`, `dataset/labels/val/` — YOLO label files generated from WIDER annotations.
- `dataset_raw/` — original WIDER FACE archive and annotation files (`wider_face_split/`, `WIDER_train/`, `WIDER_val/`).

## What has been done

- Converted (or prepared conversion) of WIDER FACE annotations to YOLO format using `wider_to_yolo.py`.
- Trained a YOLO model — outputs and checkpoints are in `runs/detect/...`.
- Confirmed inference works via `FaceDetectTest.py`.

## How to reproduce the current steps

1. Convert WIDER to YOLO labels

	Edit the top variables in `wider_to_yolo.py` (`source_label_file`, `images_base_dir`, `target_dir`) and run:

	```powershell
	python .\wider_to_yolo.py
	```

2. Quick environment / GPU checks

	```powershell
	python .\detect.py
	```

3. Run trained YOLO inference (camera or image)

	`FaceDetectTest.py` loads a model path inside `runs/detect/...` by default; adjust to your checkpoint and run:

	```powershell
	python .\FaceDetectTest.py
	```

## Next steps (capture → embed → zk-proof)

Status update: Steps 1 (capture) and 2 (embedding) are complete. The implementation is in `FaceDetectEmbedding3.py` which uses YOLO (for detection), DeepFace/ArcFace (for embeddings), and FAISS (for indexing/search).

3. Design zk-proof (next)

	Decide the statement you want to prove — examples:

	- Membership: “Embedding is in an indexed set of enrolled identities.”

	- Authentication: “Distance(probe, enrolled) < threshold.”

	- Valid capture: “Embedding was computed from an image where YOLO detected a face.”

3. Design zk-proof

	Decide the statement you want to prove — examples:

	- Membership: “Embedding is in an indexed set of enrolled identities.”
	- Authentication: “Distance(probe, enrolled) < threshold.”
	- Valid capture: “Embedding was computed from an image where YOLO detected a face.”

	Practical choices and considerations:

	- Convert floating embeddings to fixed-point (quantize) for arithmetic circuits.
	- Commit to embeddings using a hash (Poseidon / SHA) and use the commitment as public input.
	- Prototype a circuit for a squared-Euclidean distance threshold (works with integer/quantized embeddings).
	- Frameworks: Circom + snarkjs, Halo2, Plonky2, or other stacks depending on performance and language preference.

Workflow sketch for zk-auth (distance check)

1. Crop image → compute embedding (float vector).

2. Quantize embedding: e_int = round(embedding * scale).

3. Compute commitment hash H(e_int) and publish as public input.

4. Build a circuit that takes e_int (witness) and an enrolled embedding e_enrolled (public or committed) and verifies distance <= T.

5. Generate and verify proof with your chosen zk stack.

## Suggested small next tasks (concrete)

- Add `capture_faces.py`: run YOLO, crop faces, save crops + metadata (image id, bbox, timestamp).
- Add `embed_faces.py`: load crops, compute embeddings using a chosen embedding model, save embeddings as numpy files or JSON.
- Add `quantize_hash.py`: utility to quantize embeddings and compute a commitment hash suitable for use in a zk circuit.
- Prototype a small zk circuit (e.g., in Circom) that checks squared distance ≤ threshold on quantized embeddings.

## Files of interest (quick reference)

- `data.yaml`
- `wider_to_yolo.py` — annotation conversion
# YoLo-Face — Current Progress

Status

A YOLO-based face detector has been trained and inference is working. Capture and embedding (steps 1–2) are implemented in `FaceDetectEmbedding3.py`. The next planned step is to design and implement the zk-proof over embeddings (step 3).

Project overview

This repository contains code and data for training and running a YOLO-based face detector (WIDER FACE → YOLO labels) and for preparing data for downstream face-embedding and zk-proof steps.

Key scripts and files

- `wider_to_yolo.py` — convert WIDER FACE annotations into YOLO `.txt` label files.
- `FaceDetectEmbedding3.py` — capture (YOLO), embed (ArcFace via DeepFace), and index/search (FAISS) pipeline. This implements steps 1–2.
- `FaceDetectTest.py` — model load & quick inference example.
- `detect.py` — environment / CUDA / PyTorch checks.
- `runs/` — training and inference outputs (checkpoints, logs).
- `yolov8s.pt`, `yolo11n.pt` — pre-supplied model weights (examples).

Dataset layout

- `dataset/images/train/`, `dataset/images/val/` — images for training/validation.
- `dataset/labels/train/`, `dataset/labels/val/` — YOLO label files.
- `dataset_raw/` — original WIDER FACE files and splits.

What has been done

- Converted WIDER FACE annotations to YOLO format (utility: `wider_to_yolo.py`).
- Trained a YOLO model — outputs and checkpoints are in `runs/detect/...`.
- Implemented capture + embedding pipeline in `FaceDetectEmbedding3.py` (uses YOLO, DeepFace/ArcFace, FAISS).

How to reproduce the current steps

1) Convert WIDER to YOLO labels

	- Edit the top variables in `wider_to_yolo.py` (`source_label_file`, `images_base_dir`, `target_dir`).
	- Run:

```powershell
python .\wider_to_yolo.py
```

2) Quick environment / GPU checks

```powershell
python .\detect.py
```

3) Run capture + embedding (interactive webcam)

	- `FaceDetectEmbedding3.py` opens the webcam, performs detection, allows registration (`r`) and search (`s`), and persists a FAISS index (`face_db.index`) and labels (`face_labels.pkl`).

```powershell
python .\FaceDetectEmbedding3.py
```

Next step: zk-proof

Status update: Steps 1 (capture) and 2 (embedding) are complete and implemented in `FaceDetectEmbedding3.py`.

The next task (step 3) is to design and implement a zk-proof over embeddings. Example statements to prove:

- Membership: “Embedding is in an enrolled identity set (membership proof).”
- Authentication: “Distance(probe, enrolled) < threshold (authentication proof).”
- Capture validity: “Embedding was computed from an image where YOLO detected a face.”

Practical considerations

- Quantize floating embeddings to fixed-point integers before embedding them into arithmetic circuits.
- Commit to embeddings using a hash (Poseidon preferred for zk-friendly circuits, or SHA for off-circuit commitments).
- Prototype a circuit that verifies squared-Euclidean distance ≤ threshold on quantized embeddings.
- Candidate frameworks: Circom + snarkjs (JS), Halo2 / arkworks (Rust), Plonky2 (Fast recursion-friendly), or other stacks depending on performance/interop needs.

Workflow sketch for zk-auth (distance check)

1) Crop image → compute embedding (float vector).
2) Quantize embedding: e_int = round(embedding * scale).
3) Compute commitment hash H(e_int) and publish as public input.
4) Circuit: take e_int (witness) and verify squared distance to an enrolled embedding (public or provided via Merkle proof) ≤ T.
5) Generate and verify proof with chosen zk stack.

Suggested small next tasks (concrete)

- Add utility `quantize_hash.py` to quantize embeddings and compute Poseidon/SHA commitments.
- Prototype a small Circom circuit that checks squared distance ≤ threshold on quantized embeddings.
- Add unit tests for embedding quantization, hashing, and distance verification.

Files of interest (quick reference)

- `data.yaml`
- `wider_to_yolo.py`
- `FaceDetectEmbedding3.py` (capture + embed + faiss)
- `FaceDetectTest.py`
- `detect.py`
- `runs/detect/`

Try it (quick commands)

Run conversion:

```powershell
python .\wider_to_yolo.py
```

Run a GPU check/detect script:

```powershell
python .\detect.py
```

Run the capture+embed interactive script:

```powershell
python .\FaceDetectEmbedding3.py
```

Completion summary

- What changed: `ReadMe.md` was replaced with a cleaned, single README that documents current progress, reproduces steps 1–2, and outlines step 3 (zk-proof).
- Files updated: `ReadMe.md` only.
- Next action I can take: implement `quantize_hash.py` and a minimal Circom prototype for step 3 — tell me which to start with.
