import base64
import os
from openai import OpenAI

# Set API key - you'll need to have it saved as an environment variable as "OPENAI_API_KEY"
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analyze_image(image_path):
    with open(image_path, "rb") as f:
        image = base64.b64encode(f.read()).decode("utf-8")

    # Send to GPT-4V
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "List all food ingredients in this image." +
                                             "Be concise and make the output a list that can be input into another python function." +
                                             "Only output the list between square brackets"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image}"}},
                ],
            }
        ],
        max_tokens=300,
    )

    return response.choices[0].message.content

# Example usage
ingredients = analyze_image("image_recog\\fridge.jpg")
print(ingredients)
