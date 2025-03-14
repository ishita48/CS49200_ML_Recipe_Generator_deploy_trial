from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

MODEL_NAME_OR_PATH = "flax-community/t5-recipe-generation"  # Or another t5 recipe model
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME_OR_PATH)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME_OR_PATH)

app = FastAPI()

class RecipeRequest(BaseModel):
    ingredients: str

def generate_recipe(text):
    prefix = "items: "
    inputs = tokenizer(prefix + text, return_tensors="pt", padding=True, truncation=True)  # Note "pt" for PyTorch
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

@app.post("/generate")
def generate(req: RecipeRequest):
    result = generate_recipe(req.ingredients)
    return {"recipe": result}

@app.get("/")
def read_root():
    return {"message": "Welcome to the Smart Recipe Generator API! Use POST /generate to generate recipes."}

