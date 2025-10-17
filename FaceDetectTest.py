from ultralytics import YOLO
model = YOLO(r"C:\YoLo-Face\runs\detect\train3\weights\best.pt")
results = model(source=0, show=True)
