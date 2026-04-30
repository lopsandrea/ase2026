const KEY = "codebites:recipes";

export function loadRecipes() {
  try {
    return JSON.parse(localStorage.getItem(KEY) || "[]");
  } catch {
    return [];
  }
}

export function saveRecipes(list) {
  localStorage.setItem(KEY, JSON.stringify(list));
}

export function addRecipe(recipe) {
  const list = loadRecipes();
  recipe.id = Date.now().toString();
  list.push(recipe);
  saveRecipes(list);
  return recipe;
}

export function updateRecipe(id, patch) {
  const list = loadRecipes().map((r) => (r.id === id ? { ...r, ...patch } : r));
  saveRecipes(list);
}

export function deleteRecipe(id) {
  saveRecipes(loadRecipes().filter((r) => r.id !== id));
}
