from ultralytics import YOLO
from deepface import DeepFace
import cv2
import numpy as np
import faiss
import os
import pickle
import requests
from datetime import datetime

# ===== CONFIG =====
YOLO_WEIGHTS = r"C:\\YoLo-Face\\runs\\detect\\train3\\weights\\best.pt"
DB_PATH = "face_db.index"
LABELS_PATH = "face_labels.pkl"
CONF_THRESH = 0.5
EMBED_MODEL = "ArcFace"
DIST_THRESHOLD = 1.2
SERVER_URL = "https://noe-uninducible-cheerlessly.ngrok-free.dev"
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
print("[INFO] Press 'r' to register face, 's' to search, 'v' to verify, 'q' to quit")

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
        cv2.putText(frame, f"Face ({conf:.2f})", (x1p, y1p - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    cv2.imshow("YOLO + ArcFace + FAISS", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == 255:
        continue

    # ===== Register =====
    if key == ord('r'):
        if current_crop is None:
            print("[!] No face detected to register.")
            continue

        register_counter += 1
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = f"face_{register_counter}_{timestamp}"
        print(f"[+] Capturing embedding for {name}...")

        try:
            rgb = cv2.cvtColor(current_crop, cv2.COLOR_BGR2RGB)
            emb = DeepFace.represent(rgb, model_name=EMBED_MODEL, detector_backend="skip", enforce_detection=False)[0]["embedding"]
            emb_np = np.array(emb, dtype="float32").reshape(1, -1)
            emb_np = emb_np / np.linalg.norm(emb_np)

            emb_dim = emb_np.shape[1]
            if index is None:
                print(f"[+] Creating FAISS index with dimension {emb_dim}")
                index = faiss.IndexFlatL2(emb_dim)

            if index.d != emb_dim:
                print("[ERROR] Embedding dimension mismatch.")
                continue

            index.add(emb_np)
            labels.append(name)
            faiss.write_index(index, DB_PATH)
            with open(LABELS_PATH, "wb") as f:
                pickle.dump(labels, f)
            print(f"[✓] {name} added to FAISS DB.")

            try:
                payload = {"face_index": name, "embedding": emb_np.flatten().tolist() }
                resp = requests.post(f"{SERVER_URL}/face-data", json=payload, timeout=10)
                if resp.status_code == 200:
                    print(f"[✅] Server commit OK for {name}")
                else:
                    print(f"[❌] Server error {resp.status_code}: {resp.text}")
            except Exception as e:
                print("[❌] Failed sending to server:", e)

        except Exception as e:
            print("[ERROR] Registration failed:", e)

    # ===== Search =====
    elif key == ord('s'):
        if current_crop is None:
            print("[!] No face detected.")
            continue
        if index is None or len(labels) == 0:
            print("[!] DB empty.")
            continue

        try:
            rgb = cv2.cvtColor(current_crop, cv2.COLOR_BGR2RGB)
            emb = DeepFace.represent(rgb, model_name=EMBED_MODEL, detector_backend="skip", enforce_detection=False)[0]["embedding"]
            emb_np = np.array(emb, dtype="float32").reshape(1, -1)
            emb_np = emb_np / np.linalg.norm(emb_np)
            D, I = index.search(emb_np, 1)
            name = labels[I[0][0]]
            dist = float(D[0][0])
            if dist < DIST_THRESHOLD:
                print(f"[MATCH] {name} ({dist:.4f})")
            else:
                print(f"[NO MATCH] ({dist:.4f})")
            cv2.waitKey(500)
        except Exception as e:
            print("[ERROR] Search failed:", e)

    # ===== Verify (ZK) =====
    elif key == ord('v'):
        if current_crop is None:
            print("[!] No face detected to capture.")
            continue

        print("[+] Capturing embedding & sending to server for ZK verification...")

        try:
            rgb = cv2.cvtColor(current_crop, cv2.COLOR_BGR2RGB)
            emb = DeepFace.represent(rgb, model_name=EMBED_MODEL, detector_backend="skip", enforce_detection=False)[0]["embedding"]

            emb_np = np.array(emb, dtype="float32").reshape(1, -1)
            emb_np = emb_np / np.linalg.norm(emb_np)

            if index is None or len(labels) == 0:
                print("[!] No registered faces in DB.")
                continue

            D, I = index.search(emb_np, 1)
            idx = int(I[0][0])
            label = labels[idx]

            print(f"[+] Closest match: {label}")

            enrolled_vector = index.reconstruct(idx).tolist()

            payload = {
                "face_index": label,
                "embedding": emb_np.flatten().tolist(),
                "enrolled": enrolled_vector,
            }

            resp = requests.post(f"{SERVER_URL}/face-verify", json=payload, timeout=20)

            if resp.status_code == 200:
                print("[✅] ZK Proof Valid — Biometrics UNLOCKED")
                cv2.putText(frame, "UNLOCKED ✅", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 255, 0), 3)
            else:
                print("[❌] ZK Proof Failed — Access DENIED")
                cv2.putText(frame, "ACCESS DENIED ❌", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 0, 255), 3)

            cv2.imshow("YOLO + ArcFace + FAISS", frame)
            cv2.waitKey(800)

        except Exception as e:
            print("[ERROR] Verification failed:", e)

    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
