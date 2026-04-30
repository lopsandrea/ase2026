const express = require("express");
const path = require("path");

const app = express();
app.use(express.static(path.join(__dirname, "public")));

const allRecipes = Array.from({ length: 200 }, (_, i) => ({
  id: i + 1,
  title: `Recipe #${i + 1}`,
  category: ["Pasta", "Salad", "Soup", "Dessert", "Bread"][i % 5],
  prepTime: 10 + (i % 9) * 5,
  imageHue: (i * 37) % 360,
}));

app.get("/api/recipes", (req, res) => {
  const offset = parseInt(req.query.offset || "0", 10);
  const limit = parseInt(req.query.limit || "20", 10);
  res.json({ items: allRecipes.slice(offset, offset + limit), total: allRecipes.length });
});

app.get("/health", (req, res) => res.json({ status: "ok" }));

const port = process.env.PORT || 3000;
app.listen(port, "0.0.0.0", () => console.log(`RoCooky on :${port}`));
