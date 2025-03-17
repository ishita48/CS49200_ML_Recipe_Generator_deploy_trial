from ultralytics import YOLO
import torch
from fastapi import UploadFile
import shutil
import os


model = YOLO("yolov8s.pt") 


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)



def detect_ingredients(upload_file: UploadFile):
    temp_path = f"temp_{upload_file.filename}"
    

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    results = model(temp_path)
    

    detections = []
    for result in results:
        for box in result.boxes:
            detections.append({
                "class_id": int(box.cls.item()),
                "class_name": model.names[int(box.cls.item())],  # the ingredient name
                # Optional: "confidence": float(box.conf.item()), "bbox": box.xyxy.tolist()[0]
            })
    
    #removing temporary file
    os.remove(temp_path)

    return detections