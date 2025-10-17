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

1. Capture faces

	Use the YOLO model outputs (bounding boxes) to crop faces per image/frame. Use OpenCV or PIL to crop and either store the crops or pass them directly to the embedding model.

2. Generate embeddings

	Pick a pre-trained face embedding model (FaceNet / ArcFace / InsightFace or a suitable lightweight alternative).

	For each cropped face compute a fixed-size embedding vector (e.g., 128 or 512 floats) and store it with metadata (image id, bbox, timestamp, model version).

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
- `FaceDetectTest.py` — model load & inference example
- `detect.py` — environment/detection utilities
- `runs/detect/` — training & inference outputs
- `yoloface/` — Python virtual environment directory

## Try it (quick commands)

Run conversion:

```powershell
python .\wider_to_yolo.py
```

Run a GPU check/detect script:

```powershell
python .\detect.py
```

Run inference/test camera script:

```powershell
python .\FaceDetectTest.py
```

## Completion summary

- What changed: `ReadMe.md` was created/updated to document current project progress, reproduce steps, and next steps (capture → embed → zk-proof).
- Files updated: `ReadMe.md` only.
- Next action I can take: add starter scripts (`capture_faces.py`, `embed_faces.py`, `quantize_hash.py`) and/or implement a small proof prototype in Circom if you want — tell me which one to start with.
