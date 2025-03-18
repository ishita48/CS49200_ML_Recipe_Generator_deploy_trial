import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

const RecipeGenerator = () => {
  const [ingredients, setIngredients] = useState("");
  const [allergies, setAllergies] = useState("");
  const [cuisine, setCuisine] = useState("Any");
  const [maxTime, setMaxTime] = useState(60);
  const [recipe, setRecipe] = useState("");
  const [spoonacularRecipes, setSpoonacularRecipes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [detectedIngredients, setDetectedIngredients] = useState([]);
  const [outputImageUrl, setOutputImageUrl] = useState(null);
  const canvasRef = useRef(null);
  const confidenceThreshold = 0.5;

  const filteredIngredients = detectedIngredients.filter(item => item.confidence >= confidenceThreshold);

  const handleImageUpload = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/detect-ingredients', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setDetectedIngredients(response.data.ingredients);
      setIngredients(response.data.ingredients.map(item => item.class_name).join(', '));
      setOutputImageUrl('http://localhost:8000' + response.data.output_image_url);
    } catch (err) {
      setError("Failed to detect ingredients.");
    }
  };

  const handleGenerate = async () => {
    if (!ingredients.trim()) {
      setError("Please enter ingredients.");
      return;
    }
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/generate', {
        ingredients,
        allergies,
        cuisine,
        max_time: maxTime
      });
      setRecipe(response.data.ai_recipe);
      setSpoonacularRecipes(response.data.spoonacular_recipes);
    } catch {
      setError("Failed to generate recipe.");
    }
    setLoading(false);
  };

  useEffect(() => {
    if (!outputImageUrl || filteredIngredients.length === 0) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const image = new Image();

    image.onload = () => {
      canvas.width = image.width;
      canvas.height = image.height;
      ctx.drawImage(image, 0, 0);
      filteredIngredients.forEach(item => {
        const [x1, y1, x2, y2] = item.bbox;
        ctx.strokeStyle = 'red';
        ctx.lineWidth = 3;
        ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
        ctx.font = "18px Arial";
        ctx.fillStyle = "red";
        ctx.fillText(`${item.class_name} (${Math.round(item.confidence * 100)}%)`, x1, y1 > 20 ? y1 - 5 : y1 + 20);
      });
    };

    image.src = outputImageUrl;
  }, [outputImageUrl, filteredIngredients]);

  return (
    <div className="generator-container">
      

      <input type="file" accept="image/*" onChange={(e) => handleImageUpload(e.target.files[0])} className="textarea" />

      {/*Detected Image with Boxes*/}
      {outputImageUrl && (
        <div style={{ position: 'relative', display: 'inline-block', maxWidth: '100%' }}>
          <canvas ref={canvasRef} style={{ maxWidth: '100%', borderRadius: '16px' }} />
        </div>
      )}

      {/*Filtered Ingredients*/}
      {filteredIngredients.length > 0 && (
        <div className="detected-ingredients">
          <p><strong>Detected (Filtered):</strong></p>
          <ul>
            {filteredIngredients.map((item, idx) => (
              <li key={idx}>{item.class_name} ({(item.confidence * 100).toFixed(1)}%)</li>
            ))}
          </ul>
        </div>
      )}

      {/* Manual Inputs */}
      <textarea value={ingredients} onChange={(e) => setIngredients(e.target.value)} placeholder="Ingredients..." className="textarea" />
      <input type="text" value={allergies} onChange={(e) => setAllergies(e.target.value)} placeholder="Allergies (optional)" className="textarea" />
      <select value={cuisine} onChange={(e) => setCuisine(e.target.value)} className="textarea">
        <option value="Any">Any</option>
        <option value="Indian">Indian</option>
        <option value="Italian">Italian</option>
        <option value="Mexican">Mexican</option>
      </select>
      <input type="number" value={maxTime} onChange={(e) => setMaxTime(e.target.value)} min="10" max="120" className="textarea" placeholder="Max Cooking Time (minutes)" />

     
      <button onClick={handleGenerate} className="button">
        {loading ? "Generating..." : "Generate Recipe"}
      </button>


      {error && <p className="error-message">{error}</p>}


      {recipe && <div className="recipe-box"><h3>Generated Recipe</h3><pre>{recipe}</pre></div>}

      {/* Spoonacular Recipes */}
      {spoonacularRecipes.length > 0 && (
        <div className="recipe-box spoonacular-recipes">
          <h3>Spoonacular Recipes</h3>
          <ul>{spoonacularRecipes.map((rec, idx) => <li key={idx}><a href={`https://spoonacular.com/recipes/${rec.title.replace(/ /g, "-")}-${rec.id}`} target="_blank" rel="noopener noreferrer">{rec.title}</a></li>)}</ul>
        </div>
      )}
    </div>
  );
};

export default RecipeGenerator;
