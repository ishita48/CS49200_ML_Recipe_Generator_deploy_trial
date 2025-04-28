import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if OpenAI API key is set
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key or openai_api_key == "your_openai_api_key_here":
    print("\n⚠️  WARNING: OpenAI API key not set in .env file!")
    print("Please edit the .env file and set your OpenAI API key.")
    print("Example: OPENAI_API_KEY=sk-your-actual-key-here\n")
    proceed = input("Do you want to proceed anyway? (y/n): ")
    if proceed.lower() != 'y':
        print("Exiting. Please set your API key and try again.")
        exit(1)

if __name__ == "__main__":
    print("\n🍳 Starting Recipe Generator Backend Server")
    print("----------------------------------------")
    print("API will be available at: http://localhost:8000")
    print("Image upload endpoint: http://localhost:8000/detect-ingredients")
    print("Recipe generation endpoint: http://localhost:8000/generate")
    print("\nPress CTRL+C to stop the server")
    print("----------------------------------------\n")
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
