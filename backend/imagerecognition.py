import os
import cv2
import base64
import requests
import json
from PIL import Image
import io

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI API configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

def encode_image_to_base64(image_path):
    """Convert an image to base64 encoding for API transmission"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def detect_ingredients(image_path):
    """Detect ingredients in an image using ChatGPT Vision API"""
    print(f"[INFO] Detecting ingredients from: {image_path}")
    
    # Encode the image
    base64_image = encode_image_to_base64(image_path)
    
    # Prepare the API request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Identify all food ingredients in this image. For each ingredient, provide: 1) the name, 2) a confidence score between 0 and 1, and 3) the approximate bounding box coordinates [x1, y1, x2, y2] where x1,y1 is the top-left corner and x2,y2 is the bottom-right corner. Express coordinates as percentages of image dimensions. Format your response as a JSON array of objects with properties: class_name, confidence, and bbox."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 1000
    }
    
    try:
        # Make the API request
        response = requests.post(OPENAI_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        # Extract the response content
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        # Parse the JSON response
        # Find the JSON part in the response (it might be embedded in text)
        import re
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            ingredients_data = json.loads(json_str)
        else:
            # If no JSON array is found, try to parse the entire content
            try:
                ingredients_data = json.loads(content)
            except:
                print("[WARNING] Could not parse JSON from API response. Using empty list.")
                ingredients_data = []
        
        # Convert percentage-based coordinates to pixel coordinates
        img = Image.open(image_path)
        width, height = img.size
        
        detections = []
        for item in ingredients_data:
            # Convert percentage coordinates to pixel coordinates
            if "bbox" in item:
                x1_pct, y1_pct, x2_pct, y2_pct = item["bbox"]
                bbox = [
                    int(x1_pct * width / 100),
                    int(y1_pct * height / 100),
                    int(x2_pct * width / 100),
                    int(y2_pct * height / 100)
                ]
            else:
                # If no bbox is provided, use the entire image
                bbox = [0, 0, width, height]
            
            detection = {
                "class_id": 0,  # Not used with ChatGPT but kept for compatibility
                "class_name": item["class_name"],
                "confidence": item["confidence"] if "confidence" in item else 0.9,
                "bbox": bbox
            }
            print(f"[DETECTED] {detection}")
            detections.append(detection)
        
        if not detections:
            print("[INFO] No ingredients detected.")
        
        return detections
    
    except Exception as e:
        print(f"[ERROR] API request failed: {str(e)}")
        return []


def substitute_objects(image_path, detections, output_path, placeholder_path="static/placeholder.jpg"):
    """Highlight detected ingredients in the image"""
    
    if not os.path.exists(placeholder_path):
        print(f"[WARNING] Placeholder image not found. Creating an empty placeholder.")
        placeholder = 255 * (cv2.imread(image_path) * 0)
        cv2.imwrite(placeholder_path, placeholder)

    image = cv2.imread(image_path)
    
    if image is None:
        raise ValueError(f"[ERROR] Cannot read input image at {image_path}.")
    
    print(f"[INFO] Highlighting {len(detections)} objects in image.")

    # Draw bounding boxes instead of substituting
    for detection in detections:
        x1, y1, x2, y2 = map(int, detection["bbox"])
        confidence = detection["confidence"]
        
        # Choose color based on confidence (green for high, red for low)
        color = (0, 255, 0) if confidence > 0.5 else (0, 0, 255)
        
        # Draw rectangle
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        
        # Add label
        label = f"{detection['class_name']} ({confidence:.2f})"
        cv2.putText(image, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    cv2.imwrite(output_path, image)
    print(f"[INFO] Highlighted image saved to: {output_path}")
