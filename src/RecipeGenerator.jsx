import React, { useState } from 'react';
import axios from 'axios';

const RecipeGenerator = () => {
  const [ingredients, setIngredients] = useState("");
  const [recipe, setRecipe] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleGenerate = async () => {
    if (!ingredients.trim()) {
      setError("Please enter some ingredients.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const response = await axios.post('http://127.0.0.1:8000/generate', { ingredients });
      setRecipe(response.data.recipe);
    } catch (err) {
      console.error(err);
      setError("Failed to generate recipe. Please try again.");
    }
    setLoading(false);
  };

  return (
    <div className="p-6 max-w-2xl mx-auto text-center">
      <h1 className="text-3xl font-bold mb-6">🍳 Smart Recipe Generator</h1>
      <textarea
        rows="4"
        value={ingredients}
        onChange={(e) => setIngredients(e.target.value)}
        placeholder="Enter ingredients (comma separated)..."
        className="w-full p-3 border rounded mb-4"
      />
      <button
        onClick={handleGenerate}
        className="bg-green-500 text-white px-6 py-2 rounded hover:bg-green-600 transition"
      >
        {loading ? "Generating..." : "Generate Recipe"}
      </button>
      {error && <p className="text-red-500 mt-4">{error}</p>}
      {recipe && (
        <div className="mt-6 p-4 border rounded bg-gray-100 text-left">
          <h2 className="text-xl font-bold mb-2">Generated Recipe:</h2>
          <pre className="whitespace-pre-wrap">{recipe}</pre>
        </div>
      )}
    </div>
  );
};

export default RecipeGenerator;
