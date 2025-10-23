from ultralytics import YOLO
import cv2

# Load your trained face model
model = YOLO(r"C:\YoLo-Face\runs\detect\train3\weights\best.pt")

# Open webcam (source=0)
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Run YOLO on the current frame
    results = model(frame, verbose=False)

    # Get boxes for all detections
    boxes = results[0].boxes

    faces = []

    for box in boxes:
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        conf = float(box.conf[0])
        cls = int(box.cls[0])

        # Optional: skip weak detections
        if conf < 0.5:
            continue

        area = (x2 - x1) * (y2 - y1)
        faces.append((x1, y1, x2, y2, area, conf, cls))

    # Only keep the face with the largest bounding box (closest face)
    if faces:
        closest_face = max(faces, key=lambda f: f[4])
        x1, y1, x2, y2, area, conf, cls = closest_face

        # Draw the bounding box and label
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        cv2.putText(frame, f'Closest Face ({conf:.2f})', (int(x1), int(y1) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Show the frame
    cv2.imshow("Closest Face", frame)

    # Exit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
