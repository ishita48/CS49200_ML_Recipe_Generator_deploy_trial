import React, { useState } from 'react';
import axios from 'axios';

const RecipeGenerator = () => {
  const [ingredients, setIngredients] = useState("");
  const [allergies, setAllergies] = useState("");
  const [cuisine, setCuisine] = useState("Any");
  const [maxTime, setMaxTime] = useState(60);
  const [aiRecipes, setAiRecipes] = useState([]);
  const [selectedRecipeIndex, setSelectedRecipeIndex] = useState(0);
  const [spoonacularRecipes, setSpoonacularRecipes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [detectedIngredients, setDetectedIngredients] = useState([]);
  const [image, setImage] = useState(null);
  const [imageURL, setImageURL] = useState(null);
  const [showLowConfidence, setShowLowConfidence] = useState(true);


  // Handle image upload
  const handleImageUpload = async (file) => {
    setImage(URL.createObjectURL(file)); // Display uploaded image
    setLoading(true);
    setError("");
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/detect-ingredients', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      console.log("Detected Ingredients:", response.data.ingredients);
      setDetectedIngredients(response.data.ingredients);
      
      // Set the image URL to the processed image from the backend
      setImageURL(`http://localhost:8000${response.data.output_image_url}`);
      
      // Update ingredients input with detected ingredients
      setIngredients(response.data.ingredients.map(item => item.class_name).join(', ')); 

    } catch (err) {
      console.error("Image recognition failed", err);
      setError("Failed to detect ingredients from image: " + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  // Function to ensure image is loaded with correct dimensions
  const handleImageLoad = (e) => {
    // Force a re-render when the image is loaded to ensure bounding boxes align correctly
    if (e.target.complete) {
      // Apply a small timeout to ensure the image has fully rendered
      setTimeout(() => {
        const newUrl = imageURL + '?' + new Date().getTime();
        setImageURL(newUrl);
      }, 100);
    }
  };

  // Handle recipe generation
  const handleGenerate = async () => {
    if (!ingredients.trim()) {
      setError("Please enter some ingredients.");
      return;
    }
    setLoading(true);
    setError("");
    setAiRecipes([]);
    setSelectedRecipeIndex(0);
    setSpoonacularRecipes([]);

    try {
      const response = await axios.post('http://localhost:8000/generate', {
        ingredients,
        allergies,
        cuisine,
        max_time: maxTime
      });

      // Set AI-generated recipes
      if (response.data.ai_recipes && response.data.ai_recipes.length > 0) {
        setAiRecipes(response.data.ai_recipes);
      }
      
      // Set Spoonacular recipes if available
      if (response.data.spoonacular_recipes && response.data.spoonacular_recipes.length > 0) {
        setSpoonacularRecipes(response.data.spoonacular_recipes);
      }
    } catch (err) {
      console.error(err);
      setError("Failed to generate recipe: " + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  // Handle recipe selection
  const handleRecipeSelect = (index) => {
    setSelectedRecipeIndex(index);
  };

  return (
    <div className="generator-container">
      <h1>AI Recipe Generator</h1>
      <p>Upload a food image or enter ingredients manually to generate recipes</p>

      {/* Image Upload */}
      <div className="upload-section">
        <h2>Upload an image of your ingredients (optional)</h2>
        <input 
          type="file" 
          accept="image/*" 
          onChange={(e) => e.target.files[0] && handleImageUpload(e.target.files[0])} 
          className="file-upload" 
          disabled={loading}
        />
      </div>
      
      {/* Image Preview */}
      {image && (
        <div className="image-container">
          <img 
            src={imageURL || image} 
            alt="Uploaded ingredients" 
            className="uploaded-image" 
            onLoad={handleImageLoad}
            style={{ 
              width: '100%', 
              height: 'auto', 
              objectFit: 'contain',
              maxHeight: '500px'
            }}
          />
        </div>
      )}

      {/* Detected Ingredients List */}
      {detectedIngredients.length > 0 && (
        <div className="detected-container">
          <h3>Detected Ingredients:</h3>
          <ul className="ingredients-list">
            {detectedIngredients
              .filter(item => showLowConfidence || item.confidence > 0.5)
              .map((item, index) => (
                <li key={index} style={{ color: item.confidence > 0.5 ? 'green' : 'red' }}>
                  {item.class_name} ({(item.confidence * 100).toFixed(1)}%)
                </li>
            ))}
          </ul>
          <button 
            className="toggle-button" 
            onClick={() => setShowLowConfidence(!showLowConfidence)}
          >
            {showLowConfidence ? "Hide Low Confidence" : "Show All"}
          </button>
        </div>
      )}

      <div className="input-section">
        <h2>Enter or edit ingredients and preferences</h2>
        
        {/* Ingredients Input */}
        <label htmlFor="ingredients">Ingredients:</label>
        <textarea
          id="ingredients"
          rows="4"
          value={ingredients}
          onChange={(e) => setIngredients(e.target.value)}
          placeholder="List ingredients here, e.g., chicken, rice, onion..."
          className="textarea"
          disabled={loading}
        />

        <label htmlFor="allergies">Allergies (optional):</label>
        <input 
          id="allergies"
          type="text" 
          value={allergies} 
          onChange={(e) => setAllergies(e.target.value)} 
          placeholder="e.g., nuts, dairy, gluten..." 
          className="textarea"
          disabled={loading}
        />
        
        <label htmlFor="cuisine">Cuisine Type:</label>
        <select 
          id="cuisine"
          value={cuisine} 
          onChange={(e) => setCuisine(e.target.value)} 
          className="textarea"
          disabled={loading}
        >
          <option value="Any">Any</option>
          <option value="American">American</option>
          <option value="Chinese">Chinese</option>
          <option value="French">French</option>
          <option value="Greek">Greek</option>
          <option value="Indian">Indian</option>
          <option value="Italian">Italian</option>
          <option value="Japanese">Japanese</option>
          <option value="Korean">Korean</option>
          <option value="Mediterranean">Mediterranean</option>
          <option value="Mexican">Mexican</option>
          <option value="Middle Eastern">Middle Eastern</option>
          <option value="Thai">Thai</option>
          <option value="Vietnamese">Vietnamese</option>
        </select>
        
        <label htmlFor="maxTime">Maximum Cooking Time (minutes):</label>
        <input 
          id="maxTime"
          type="number" 
          value={maxTime} 
          onChange={(e) => setMaxTime(parseInt(e.target.value) || 60)} 
          min="10" 
          max="180" 
          className="textarea"
          disabled={loading}
        />
      </div>

      {/* Generate Button */}
      <div className="generate-section">
        <h2>Step 3: Generate your recipe</h2>
        <button 
          onClick={handleGenerate} 
          className="button"
          disabled={loading || !ingredients.trim()}
        >
          {loading ? "Generating..." : "Generate Recipe"}
        </button>
      </div>

      {/* Error Message */}
      {error && <p className="error-message">{error}</p>}

      {/* Recipe Results */}
      {aiRecipes.length > 0 && (
        <div className="results-section">
          {/* Recipe Selection Buttons */}
          <div className="recipe-buttons">
            <h2>AI-Generated Recipes:</h2>
            <div className="button-container">
              {aiRecipes.map((recipe, index) => (
                <button
                  key={index}
                  onClick={() => handleRecipeSelect(index)}
                  className={`recipe-button ${selectedRecipeIndex === index ? 'selected' : ''}`}
                >
                  Recipe {index + 1}
                </button>
              ))}
            </div>
          </div>

          {/* Selected Recipe Display */}
          <div className="recipe-box">
            <h3>Selected Recipe:</h3>
            <pre className="recipe-content">{aiRecipes[selectedRecipeIndex]}</pre>
          </div>
          
          {/* Spoonacular Recipes */}
          {spoonacularRecipes.length > 0 && (
            <div className="spoonacular-recipes">
              <h2>Alternative Recipe Suggestions:</h2>
              <div className="recipe-grid">
                {spoonacularRecipes.map((recipe, index) => (
                  <div key={index} className="recipe-card">
                    <h3>{recipe.title}</h3>
                    {recipe.image && (
                      <img src={recipe.image} alt={recipe.title} className="recipe-image" />
                    )}
                    <p>Used ingredients: {recipe.usedIngredientCount}</p>
                    <p>Missing ingredients: {recipe.missedIngredientCount}</p>
                    <a 
                      href={`https://spoonacular.com/recipes/${recipe.title.replace(/\s+/g, '-').toLowerCase()}-${recipe.id}`} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="view-recipe-btn"
                    >
                      View Full Recipe
                    </a>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default RecipeGenerator;
