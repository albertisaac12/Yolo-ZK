import os
from PIL import Image

# ========== CONFIGURE YOUR PATHS HERE ==========
# Example:
# source_label_file = r"C:\YoLo-Face\dataset_raw\wider_face_split\wider_face_train_bbx_gt.txt"
# images_base_dir = r"C:\YoLo-Face\dataset_raw\WIDER_train\images"
# target_dir = r"C:\YoLo-Face\dataset\labels\train"

# source_label_file = r"C:\YoLo-Face\dataset_raw\wider_face_split\wider_face_train_bbx_gt.txt"
# images_base_dir = r"C:\YoLo-Face\dataset_raw\WIDER_train\images"
# target_dir = r"C:\YoLo-Face\dataset\labels\train"

source_label_file = r"C:\YoLo-Face\dataset_raw\wider_face_split\wider_face_val_bbx_gt.txt"
images_base_dir = r"C:\YoLo-Face\dataset_raw\WIDER_val\images"
target_dir = r"C:\YoLo-Face\dataset\labels\val"


# ==============================================

# Create target directory if not exists
os.makedirs(target_dir, exist_ok=True)

# Read annotation lines
with open(source_label_file, "r", encoding="utf-8") as f:
    lines = [line.strip() for line in f.readlines() if line.strip()]

i = 0
while i < len(lines):
    line = lines[i]

    # Detect image line (always contains '/' or ends with an image extension)
    if not ("/" in line or line.lower().endswith(('.jpg', '.jpeg', '.png'))):
        i += 1
        continue

    image_path = line
    i += 1

    # Get bounding box count (next line)
    if i >= len(lines):
        break
    try:
        bbox_count = int(lines[i])
    except ValueError:
        bbox_count = 0
    i += 1

    bboxes = []
    for _ in range(bbox_count):
        if i >= len(lines):
            break
        try:
            bbox = list(map(float, lines[i].split()[:4]))  # x, y, w, h
            bboxes.append(bbox)
        except ValueError:
            pass
        i += 1

    # Locate image
    image_full_path = os.path.join(images_base_dir, image_path)
    if not os.path.exists(image_full_path):
        print(f"[WARN] Missing image: {image_full_path}")
        continue

    # Get image dimensions
    try:
        with Image.open(image_full_path) as img:
            img_width, img_height = img.size
    except Exception as e:
        print(f"[ERROR] Unable to open image {image_full_path}: {e}")
        continue

    # Convert boxes to YOLO format
    yolo_lines = []
    for (x, y, w, h) in bboxes:
        if w <= 0 or h <= 0:
            continue
        x_center = (x + w / 2.0) / img_width
        y_center = (y + h / 2.0) / img_height
        w_norm = w / img_width
        h_norm = h / img_height
        yolo_lines.append(f"0 {x_center:.6f} {y_center:.6f} {w_norm:.6f} {h_norm:.6f}")

    # Write YOLO label file
    out_path = os.path.join(target_dir, os.path.splitext(os.path.basename(image_path))[0] + ".txt")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(yolo_lines))

    print(f"[OK] Created label file: {out_path} ({len(yolo_lines)} faces)")
