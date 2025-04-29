from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from imagerecognition import detect_ingredients, substitute_objects
import os
import shutil
import cv2

MODEL_NAME_OR_PATH = "flax-community/t5-recipe-generation"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME_OR_PATH)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME_OR_PATH)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

tokens_map = { "<sep>": "--", "<section>": "\n" }

def skip_special_tokens(text, special_tokens):
    for token in special_tokens:
        text = text.replace(token, "")
    return text

def target_postprocessing(texts, special_tokens):
    if not isinstance(texts, list):
        texts = [texts]
    new_texts = []
    for text in texts:
        text = skip_special_tokens(text, special_tokens)
        for k, v in tokens_map.items():
            text = text.replace(k, v)
        new_texts.append(text)
    return new_texts

def build_prompt(ingredients, cuisine=None, allergies=None, max_time=None):
    prompt = "items: " + ", ".join(ingredients)
    if cuisine and cuisine.lower() != "any":
        prompt += f" | cuisine: {cuisine}"
    if allergies:
        prompt += f" | avoid: {allergies}"
    if max_time:
        prompt += f" | max_time: {max_time} mins"
    return prompt

def generate_recipe(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    output_ids = model.generate(
        input_ids=inputs.input_ids,
        max_length=750,
        min_length=64,
        no_repeat_ngram_size=3,
        do_sample=True,
        top_k=60,
        top_p=0.95
    )
    generated = tokenizer.batch_decode(output_ids, skip_special_tokens=False)
    final_output = target_postprocessing(generated, tokenizer.all_special_tokens)
    return final_output[0]



class RecipeRequest(BaseModel):
    ingredients: str
    allergies: str = ""
    cuisine: str = "Any"
    max_time: int = 60
    source: str = "AI" 

@app.post("/generate")
def generate(req: RecipeRequest):
    ingredients_list = [item.strip().lower() for item in req.ingredients.split(',') if item.strip()]
    allergies = req.allergies.strip().lower() if req.allergies else ""
    final_prompt = build_prompt(ingredients_list, req.cuisine, allergies, req.max_time)
    
    generated_recipes = []
    
    # Generate 5 recipes
    for _ in range(5):
        generated = generate_recipe(final_prompt)  # still uses generate_recipe(text) that generates 1 at a time

        sections = generated.split("\n")
        formatted_recipe = ""

        for section in sections:
            section = section.strip()
            if section.startswith("title:"):
                title = section.replace("title:", "").strip().capitalize()
                formatted_recipe += f"[TITLE]: {title}\n\n"
            elif section.startswith("ingredients:"):
                formatted_recipe += "[INGREDIENTS]:\n"
                ingredients_text = section.replace("ingredients:", "").strip()
                ingredients_list = ingredients_text.split("--")
                for i, ingredient in enumerate(ingredients_list):
                    formatted_recipe += f"  - {i+1}: {ingredient.strip().capitalize()}\n"
                formatted_recipe += "\n"
            elif section.startswith("directions:"):
                formatted_recipe += "[DIRECTIONS]:\n"
                directions_text = section.replace("directions:", "").strip()
                directions_list = directions_text.split("--")
                for i, direction in enumerate(directions_list):
                    formatted_recipe += f"  - {i+1}: {direction.strip().capitalize()}\n"

        generated_recipes.append(formatted_recipe)

    return {"ai_recipes": generated_recipes}


@app.post("/detect-ingredients")
async def detect(file: UploadFile = File(...)):
    os.makedirs(STATIC_DIR, exist_ok=True)

   
    temp_path = os.path.join(STATIC_DIR, f"output_{file.filename}")
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    print(f"[INFO] Image successfully saved at: {temp_path}")

   
    placeholder_path = os.path.join(STATIC_DIR, "placeholder.jpg")
    if not os.path.exists(placeholder_path):
        print("[WARNING] Placeholder image not found. Creating a blank one.")
        blank_placeholder = 255 * (cv2.imread(temp_path) * 0)  # Create blank white placeholder
        cv2.imwrite(placeholder_path, blank_placeholder)

    # ✅ Detect ingredients
    detected_items = detect_ingredients(temp_path)
    filtered_items = [item for item in detected_items if item['confidence'] >= 0.5]

    # ✅ Substitute objects in saved image
    substitute_objects(temp_path, filtered_items, temp_path, placeholder_path)

    return {
        "ingredients": filtered_items,
        "output_image_url": f"/static/output_{file.filename}"
    }
