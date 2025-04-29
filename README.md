# Recipe Generator with ChatGPT Vision

This application allows users to generate recipes based on ingredients they have. It features an image recognition system powered by ChatGPT Vision API that can detect ingredients from uploaded photos.

## Features

- Upload images of ingredients for automatic detection
- Generate recipes based on detected or manually entered ingredients
- Specify cuisine type, allergies, and maximum cooking time
- Visually highlights detected ingredients in the uploaded image

## Project Structure

- `frontend`: React-based user interface
- `backend`: FastAPI server with ChatGPT Vision integration

## Setup Instructions

### Prerequisites

- Node.js (v14+)
- Python (v3.8+)
- OpenAI API key with access to GPT-4 Vision

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

3. Configure your API keys:
   - Open the `.env` file in the backend directory
   - Replace `your_openai_api_key_here` with your actual OpenAI API key
   - (Optional) Replace `your_spoonacular_api_key_here` with a Spoonacular API key if you want to use that feature

4. Start the backend server:
   ```
   uvicorn main:app --reload --port 8000
   ```

### Frontend Setup

1. Install the required npm packages:
   ```
   npm install
   ```

2. Start the development server:
   ```
   npm run dev
   ```

3. Open your browser and navigate to:
   ```
   http://localhost:5173
   ```

## Usage

1. Click on the "Upload Image" button to select a photo of your ingredients
2. The system will detect ingredients and display them with confidence scores
3. You can manually edit the ingredients list if needed
4. Specify any allergies, preferred cuisine, and maximum cooking time
5. Click "Generate Recipe" to get a recipe based on your ingredients

## Technologies Used

- **Frontend**: React, Vite, Axios
- **Backend**: FastAPI, ChatGPT Vision API, OpenCV
- **Image Processing**: OpenCV, PIL
- **Recipe Generation**: T5 Transformer Model

## Notes

- The image recognition feature requires an OpenAI API key with access to GPT-4 Vision
- For best results, take clear photos of ingredients with good lighting
