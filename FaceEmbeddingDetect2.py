from ultralytics import YOLO
from deepface import DeepFace
import cv2
import numpy as np
import faiss
import os
import pickle
from datetime import datetime

# ===== CONFIG =====
YOLO_WEIGHTS = r"C:\YoLo-Face\runs\detect\train3\weights\best.pt"
DB_PATH = "face_db.index"
LABELS_PATH = "face_labels.pkl"
CONF_THRESH = 0.5
EMBED_MODEL = "Facenet"   # can also use: "ArcFace", "VGG-Face", etc.
# ===================

model = YOLO(YOLO_WEIGHTS)

index = None
labels = []
if os.path.exists(DB_PATH) and os.path.exists(LABELS_PATH):
    print("[+] Loading existing FAISS index...")
    index = faiss.read_index(DB_PATH)
    with open(LABELS_PATH, "rb") as f:
        labels = pickle.load(f)
else:
    print("[+] No existing FAISS DB found. It will be created on first registration.")

cap = cv2.VideoCapture(0)
print("[INFO] Press 'r' to register face, 's' to search, 'q' to quit")

current_crop = None
register_counter = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, verbose=False)
    boxes = results[0].boxes

    faces = []
    for box in boxes:
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        conf = float(box.conf[0])
        if conf < CONF_THRESH:
            continue
        area = (x2 - x1) * (y2 - y1)
        faces.append((int(x1), int(y1), int(x2), int(y2), area, conf))

    if faces:
        x1, y1, x2, y2, area, conf = max(faces, key=lambda f: f[4])
        pad = 10
        x1p = max(x1 - pad, 0)
        y1p = max(y1 - pad, 0)
        x2p = min(x2 + pad, frame.shape[1])
        y2p = min(y2 + pad, frame.shape[0])
        current_crop = frame[y1p:y2p, x1p:x2p]

        cv2.rectangle(frame, (x1p, y1p), (x2p, y2p), (0, 255, 0), 2)
        cv2.putText(frame, f"Face ({conf:.2f})", (x1p, y1p - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    cv2.imshow("YOLO + DeepFace + FAISS", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == 255:
        continue

    # ===== Register without user input =====
    if key == ord('r'):
        if current_crop is None:
            print("[!] No face detected to register.")
            continue

        # auto-generate a unique label
        register_counter += 1
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = f"face_{register_counter}_{timestamp}"

        print(f"[+] Capturing embedding for {name}...")

        try:
            rgb = cv2.cvtColor(current_crop, cv2.COLOR_BGR2RGB)
            emb = DeepFace.represent(
                rgb,
                model_name=EMBED_MODEL,
                detector_backend="skip",
                enforce_detection=False
            )[0]["embedding"]

            emb_np = np.array(emb, dtype="float32").reshape(1, -1)
            emb_dim = emb_np.shape[1]

            if index is None:
                print(f"[+] Creating FAISS index with dimension {emb_dim}")
                index = faiss.IndexFlatL2(emb_dim)

            if index.d != emb_dim:
                print("[ERROR] Embedding dimension mismatch. Skipping registration.")
                continue

            index.add(emb_np)
            labels.append(name)
            faiss.write_index(index, DB_PATH)
            with open(LABELS_PATH, "wb") as f:
                pickle.dump(labels, f)
            print(f"[✓] {name} added to database.")
        except Exception as e:
            print("[ERROR] Registration failed:", e)

    # ===== Search Mode =====
    elif key == ord('s'):
        if current_crop is None:
            print("[!] No face detected to search.")
            continue
        if index is None or len(labels) == 0:
            print("[!] Database is empty.")
            continue

        print("[+] Searching for closest match...")
        try:
            rgb = cv2.cvtColor(current_crop, cv2.COLOR_BGR2RGB)
            emb = DeepFace.represent(
                rgb,
                model_name=EMBED_MODEL,
                detector_backend="skip",
                enforce_detection=False
            )[0]["embedding"]
            emb_np = np.array(emb, dtype="float32").reshape(1, -1)

            D, I = index.search(emb_np, 1)
            name = labels[I[0][0]]
            dist = float(D[0][0])

            if dist < 0.9:
                print(f"[MATCH] {name} (distance={dist:.4f})")
                cv2.putText(frame, f"{name}", (x1, y1 - 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            else:
                print("[NO MATCH] Unknown face.")
                cv2.putText(frame, "Unknown", (x1, y1 - 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            cv2.imshow("YOLO + DeepFace + FAISS", frame)
            cv2.waitKey(500)
        except Exception as e:
            print("[ERROR] Search failed:", e)

    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
