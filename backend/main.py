from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from imagerecognition import detect_ingredients  # Assuming imagerecognition.py is present

# Load PyTorch Model & Tokenizer
MODEL_NAME_OR_PATH = "flax-community/t5-recipe-generation"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME_OR_PATH)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME_OR_PATH)

# FastAPI app setup
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Development origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Home route (optional)
@app.get("/")
def read_root():
    return {"message": "Welcome to the Smart Recipe Generator API. Use POST /generate to generate recipes."}

# Request schema for recipe generation
class RecipeRequest(BaseModel):
    ingredients: str
    allergies: str = ""
    cuisine: str = "Any"
    max_time: int = 60  # In minutes

# Token post-processing
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

# Build smart prompt from user input
def build_prompt(ingredients, cuisine=None, allergies=None, max_time=None):
    prompt = "items: " + ", ".join(ingredients)
    if cuisine and cuisine.lower() != "any":
        prompt += f" | cuisine: {cuisine}"
    if allergies:
        prompt += f" | avoid: {allergies}"
    if max_time:
        prompt += f" | max_time: {max_time} mins"
    return prompt

# Recipe generation function
def generate_recipe(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    output_ids = model.generate(
        input_ids=inputs.input_ids,
        max_length=512,
        min_length=64,
        no_repeat_ngram_size=3,
        do_sample=True,
        top_k=60,
        top_p=0.95
    )
    generated = tokenizer.batch_decode(output_ids, skip_special_tokens=False)
    final_output = target_postprocessing(generated, tokenizer.all_special_tokens)
    return final_output[0]

# API endpoint for recipe generation
@app.post("/generate")
def generate(req: RecipeRequest):
    # Process ingredients list
    ingredients_list = [item.strip().lower() for item in req.ingredients.split(',') if item.strip()]

    # Optional: check and clean allergies
    allergies = req.allergies.strip().lower() if req.allergies else ""

    # Build smart prompt
    final_prompt = build_prompt(
        ingredients=ingredients_list,
        cuisine=req.cuisine,
        allergies=allergies,
        max_time=req.max_time
    )

    print(f"Using prompt: {final_prompt}")  # Debug print, optional

    # Generate recipe using the model
    recipe_output = generate_recipe(final_prompt)

    return {"recipe": recipe_output}

# Endpoint for image recognition
@app.post("/detect-ingredients")
async def detect(file: UploadFile = File(...)):
    detected_items = detect_ingredients(file)
    return {"ingredients": detected_items}