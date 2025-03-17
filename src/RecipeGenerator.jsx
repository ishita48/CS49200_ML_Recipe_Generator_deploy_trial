import React, { useState } from 'react';
import axios from 'axios';

const RecipeGenerator = () => {
  const [ingredients, setIngredients] = useState("");
  const [allergies, setAllergies] = useState("");
  const [cuisine, setCuisine] = useState("Any");
  const [maxTime, setMaxTime] = useState(60);
  const [recipe, setRecipe] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [detectedIngredients, setDetectedIngredients] = useState([]);
  const [image, setImage] = useState(null); // To store uploaded image

  // Function to handle image upload and send to backend
  const handleImageUpload = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/detect-ingredients', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      console.log(response.data.ingredients);
      setDetectedIngredients(response.data.ingredients.map(item => item.class_name));
      setIngredients(response.data.ingredients.map(item => item.class_name).join(', ')); // Auto-fill ingredients
    } catch (err) {
      console.error("Image recognition failed", err);
      setError("Failed to detect ingredients from image.");
    }
  };

  // Recipe generation function
  const handleGenerate = async () => {
    if (!ingredients.trim()) {
      setError("Please enter some ingredients.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const response = await axios.post('http://localhost:8000/generate', {
        ingredients,
        allergies,
        cuisine,
        max_time: maxTime
      });
      setRecipe(response.data.recipe);
    } catch (err) {
      console.error(err);
      setError("Failed to generate recipe. Please try again.");
    }
    setLoading(false);
  };

  return (
    <div className="generator-container">

      {/* Image Upload Section */}
      <input type="file" accept="image/*" onChange={(e) => handleImageUpload(e.target.files[0])} className="textarea" />
      {detectedIngredients.length > 0 && (
        <div>
          <p>Detected Ingredients: {detectedIngredients.join(', ')}</p>
        </div>
      )}

      {/* Ingredients Text Input (editable) */}
      <textarea
        rows="4"
        value={ingredients}
        onChange={(e) => setIngredients(e.target.value)}
        placeholder="List ingredients here, e.g., chicken, rice, onion..."
        className="textarea"
      />
      <input
        type="text"
        value={allergies}
        onChange={(e) => setAllergies(e.target.value)}
        placeholder="Allergies (optional)..."
        className="textarea"
      />
      <select value={cuisine} onChange={(e) => setCuisine(e.target.value)} className="textarea">
        <option value="Any">Any</option>
        <option value="Indian">Indian</option>
        <option value="Italian">Italian</option>
        <option value="Mexican">Mexican</option>
      </select>
      <input
        type="number"
        value={maxTime}
        onChange={(e) => setMaxTime(e.target.value)}
        min="10"
        max="120"
        className="textarea"
        placeholder="Max Cooking Time (minutes)"
      />

      {/* Generate Button */}
      <button onClick={handleGenerate} className="button">
        {loading ? "Generating..." : "Generate Recipe"}
      </button>

      {/* Error Message */}
      {error && <p className="error-message">{error}</p>}

      {/* Recipe Result */}
      {recipe && (
        <div className="recipe-box">
          <h2>Generated Recipe:</h2>
          <pre>{recipe}</pre>
        </div>
      )}
    </div>
  );
};

export default RecipeGenerator;
