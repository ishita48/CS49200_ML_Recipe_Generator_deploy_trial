from ultralytics import YOLO
import torch
import os
import cv2

# Load YOLO model
model = YOLO("yolov8s.pt")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

def detect_ingredients(image_path):
    print(f"[INFO] Detecting ingredients from: {image_path}")

    results = model(image_path)
    detections = []

    for result in results:
        print(f"[DEBUG] Found {len(result.boxes)} boxes")
        for box in result.boxes:
            detection = {
                "class_id": int(box.cls.item()),
                "class_name": model.names[int(box.cls.item())],
                "confidence": float(box.conf.item()),
                "bbox": box.xyxy.tolist()[0]
            }
            print(f"[DETECTED] {detection}")
            detections.append(detection)

    if not detections:
        print("[INFO] No ingredients detected.")

    return detections


def substitute_objects(image_path, detections, output_path, placeholder_path="static/placeholder.jpg"):

    if not os.path.exists(placeholder_path):
        print(f"[WARNING] Placeholder image not found. Creating an empty placeholder.")
        placeholder = 255 * (cv2.imread(image_path) * 0)
        cv2.imwrite(placeholder_path, placeholder)

    image = cv2.imread(image_path)
    placeholder = cv2.imread(placeholder_path)

    if image is None:
        raise ValueError(f"[ERROR] Cannot read input image at {image_path}.")
    if placeholder is None:
        raise ValueError(f"[ERROR] Placeholder image at {placeholder_path} is missing or unreadable.")

    print(f"[INFO] Substituting {len(detections)} objects in image.")

    for detection in detections:
        x1, y1, x2, y2 = map(int, detection["bbox"])
        placeholder_resized = cv2.resize(placeholder, (x2 - x1, y2 - y1))
        image[y1:y2, x1:x2] = placeholder_resized

    cv2.imwrite(output_path, image)
    print(f"[INFO] Substituted image saved to: {output_path}")
