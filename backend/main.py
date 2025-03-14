from fastapi import FastAPI
from pydantic import BaseModel
from transformers import FlaxAutoModelForSeq2SeqLM, AutoTokenizer

# Load model once
MODEL_NAME_OR_PATH = "flax-community/t5-recipe-generation"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME_OR_PATH, use_fast=True)
model = FlaxAutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME_OR_PATH)

app = FastAPI()

# Request structure
class RecipeRequest(BaseModel):
    ingredients: str

# Preprocess and generate recipe
def generate_recipe(text):
    prefix = "items: "
    inputs = tokenizer(prefix + text, return_tensors="jax", padding=True, truncation=True)
    output_ids = model.generate(input_ids=inputs.input_ids, **{
        "max_length": 512,
        "min_length": 64,
        "no_repeat_ngram_size": 3,
        "do_sample": True,
        "top_k": 60,
        "top_p": 0.95
    }).sequences
    generated = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
    return generated[0]

# API endpoint
@app.post("/generate")
def generate(req: RecipeRequest):
    result = generate_recipe(req.ingredients)
    return {"recipe": result}
