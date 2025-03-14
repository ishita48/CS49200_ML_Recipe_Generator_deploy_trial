from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

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

# Recipe generation
def generate_recipe(text):
    prefix = "items: "
    inputs = tokenizer(prefix + text, return_tensors="pt", padding=True, truncation=True)
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
    return generated[0]  # Return raw text for now

# API endpoint
@app.post("/generate")
def generate(req: RecipeRequest):
    result = generate_recipe(req.ingredients)
    return {"recipe": result}
