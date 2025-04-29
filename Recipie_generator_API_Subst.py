from ultralytics import YOLO
import cv2
import torch
import numpy as np
import requests

# Load the YOLOv8 pre-trained model
model = YOLO("yolov8s.pt")  # 's' for small model, replace with 'm', 'l', or 'x' for larger models

# Check if CUDA (GPU) is available for faster processing
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Load the image for inference
image_path = "image_recog/fridge.jpg"
image = cv2.imread(image_path)

# Run inference on the image
results = model(image)  # No need to save unless required

# Function to substitute detected objects with a placeholder
def substitute_objects(image, detections, placeholder_path="placeholder.jpg"):
    placeholder = cv2.imread(placeholder_path)
    if placeholder is None:
        raise ValueError("Placeholder image not found or could not be loaded.")

    for detection in detections:
        bbox = detection["bbox"]
        x1, y1, x2, y2 = map(int, bbox)
        # Resize placeholder to fit the bounding box
        placeholder_resized = cv2.resize(placeholder, (x2 - x1, y2 - y1))
        # Replace the detected object with the placeholder
        image[y1:y2, x1:x2] = placeholder_resized

    return image

# Extract detection results
detections = []
for result in results:
    for box in result.boxes:
        detections.append({
            "class_id": int(box.cls.item()),  # Class index
            "class_name": model.names[int(box.cls.item())],  # Class name
            "confidence": float(box.conf.item()),  # Confidence score
            "bbox": box.xyxy.tolist()[0]  # Bounding box (x1, y1, x2, y2)
        })

# Print the list of detected items
print("Detected Items:")
for detection in detections:
    print(f"Class: {detection['class_name']}, Confidence: {detection['confidence']:.2f}, BBox: {detection['bbox']}")

# Substitute detected objects with a placeholder
output_image = substitute_objects(image, detections)

# Save or display the output image
output_path = "output_image.jpg"
cv2.imwrite(output_path, output_image)
print(f"Output image saved to {output_path}")

# Optionally, display the output image
cv2.imshow("Output Image", output_image)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Spoonacular API Integration for Recipe Generation
def get_recipes_by_ingredients(ingredients, api_key):
    """
    Get recipes based on detected ingredients using Spoonacular API.
    """
    url = "https://api.spoonacular.com/recipes/findByIngredients"
    params = {
        "ingredients": ",".join(ingredients),  # Comma-separated list of ingredients
        "number": 5,  # Number of recipes to return
        "apiKey": api_key  # Your Spoonacular API key
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()  # Return the list of recipes
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

# Extract detected ingredients (class names)
detected_ingredients = [detection["class_name"] for detection in detections]

# Spoonacular API Key (replace with your own key)
api_key = "YOUR_SPOONACULAR_API_KEY"  # Replace with your Spoonacular API key

# Get recipes based on detected ingredients
if detected_ingredients:
    print("\nGenerating recipes based on detected ingredients...")
    recipes = get_recipes_by_ingredients(detected_ingredients, api_key)
    if recipes:
        print("\nRecipes Found:")
        for recipe in recipes:
            print(f"\nRecipe: {recipe['title']}")
            print(f"Missing Ingredients: {recipe['missedIngredientCount']}")
            print(f"Used Ingredients: {recipe['usedIngredients']}")
            print(f"Link: https://spoonacular.com/recipes/{recipe['title'].replace(' ', '-')}-{recipe['id']}")
    else:
        print("No recipes found or API error.")
else:
    print("No ingredients detected.")
