from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from imagerecognition import detect_ingredients  # Import the detection function
from fastapi import UploadFile, File



# Model & Tokenizer
MODEL_NAME_OR_PATH = "flax-community/t5-recipe-generation"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME_OR_PATH)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME_OR_PATH)

# FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # both localhost and 127.0.0.1
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)
# Home route (optional, informative)
@app.get("/")
def read_root():
    return {"message": "Welcome to the Smart Recipe Generator API. Use POST /generate to generate recipes."}

# Request schema
class RecipeRequest(BaseModel):
    ingredients: str

# API Request schema
class RecipeRequest(BaseModel):
    ingredients: str
    allergies: str = ""
    cuisine: str = "Any"
    max_time: int = 60  # In minutes

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

# Recipe generation logic using the model
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
    generated = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
    return generated[0]

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

# API endpoint
@app.post("/generate")
def generate(req: RecipeRequest):
    result = generate_recipe(req.ingredients)
    return {"recipe": result}


# another endpoint for image recognition
@app.post("/detect-ingredients")
async def detect(file: UploadFile = File(...)):
    detected_items = detect_ingredients(file)
    return {"ingredients": detected_items}