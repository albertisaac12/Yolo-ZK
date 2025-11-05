from ultralytics import YOLO
from deepface import DeepFace
import cv2
import numpy as np
import faiss
import os
import pickle
from datetime import datetime


class FaceRecognitionSystem:
    def __init__(self, yolo_weights, db_path, labels_path, conf_thresh=0.5, embed_model="ArcFace", dist_thresh=1.2):
        self.yolo_weights = yolo_weights
        self.db_path = db_path
        self.labels_path = labels_path
        self.conf_thresh = conf_thresh
        self.embed_model = embed_model
        self.dist_thresh = dist_thresh

        self.model = YOLO(self.yolo_weights)
        self.index = None
        self.labels = []
        self.current_crop = None
        self.register_counter = 0
        self.load_db()

    def load_db(self):
        if os.path.exists(self.db_path) and os.path.exists(self.labels_path):
            print("[+] Loading existing FAISS index...")
            self.index = faiss.read_index(self.db_path)
            with open(self.labels_path, "rb") as f:
                self.labels = pickle.load(f)
        else:
            print("[+] No existing FAISS DB. It will be created on first registration.")

    def get_embedding(self, crop):
        rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
        emb = DeepFace.represent(
            rgb,
            model_name=self.embed_model,
            detector_backend="skip",
            enforce_detection=False
        )[0]["embedding"]
        emb = np.array(emb, dtype="float32").reshape(1, -1)
        emb = emb / np.linalg.norm(emb)
        return emb

    def register_face(self):
        if self.current_crop is None:
            print("[!] No face detected to register.")
            return

        self.register_counter += 1
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = f"face_{self.register_counter}_{timestamp}"

        try:
            emb = self.get_embedding(self.current_crop)
            emb_dim = emb.shape[1]

            if self.index is None:
                print(f"[+] Creating FAISS index with dim {emb_dim}")
                self.index = faiss.IndexFlatL2(emb_dim)

            if self.index.d != emb_dim:
                print("[ERROR] Embedding dimension mismatch.")
                return

            self.index.add(emb)
            self.labels.append(name)
            faiss.write_index(self.index, self.db_path)
            with open(self.labels_path, "wb") as f:
                pickle.dump(self.labels, f)
            print(f"[✓] Registered {name}")
        except Exception as e:
            print("[ERROR] Registration failed:", e)

    def search_face(self, frame, x1, y1):
        if self.current_crop is None:
            print("[!] No face detected.")
            return
        if self.index is None or len(self.labels) == 0:
            print("[!] Database empty.")
            return

        try:
            emb = self.get_embedding(self.current_crop)
            D, I = self.index.search(emb, 1)
            name = self.labels[I[0][0]]
            dist = float(D[0][0])

            if dist < self.dist_thresh:
                print(f"[MATCH] {name} ({dist:.4f})")
                cv2.putText(frame, name, (x1, y1 - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)
            else:
                print(f"[NO MATCH] ({dist:.4f})")
                cv2.putText(frame, "Unknown", (x1, y1 - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)
        except Exception as e:
            print("[ERROR] Search failed:", e)

    def run(self):
        cap = cv2.VideoCapture(0)
        print("[INFO] r=register, s=search, q=quit")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            results = self.model(frame, verbose=False)
            boxes = results[0].boxes
            faces = []

            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = float(box.conf[0])
                if conf < self.conf_thresh:
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
                self.current_crop = frame[y1p:y2p, x1p:x2p]
                cv2.rectangle(frame, (x1p, y1p), (x2p, y2p), (0,255,0), 2)

            cv2.imshow("Face Recognition", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('r'):
                self.register_face()
            elif key == ord('s') and faces:
                self.search_face(frame, x1p, y1p)
            elif key == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()


app = FaceRecognitionSystem(
    yolo_weights=r"C:\YoLo-Face\runs\detect\train3\weights\best.pt",
    db_path="face_db.index",
    labels_path="face_labels.pkl"
)

app.run()
