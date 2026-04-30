import React, { useState } from "react";
import { Routes, Route, Link, useNavigate, useParams } from "react-router-dom";
import { useDropzone } from "react-dropzone";
import { loadRecipes, addRecipe, updateRecipe, deleteRecipe } from "./store.js";

function Layout({ children }) {
  return (
    <div className="layout">
      <header data-test-id="header">
        <Link to="/" className="brand" data-test-id="brand">CodeBites</Link>
        <nav>
          <Link to="/recipes" data-test-id="nav-recipes">Recipes</Link>
          <Link to="/recipes/new" data-test-id="nav-new">New Recipe</Link>
          <Link to="/login" data-test-id="nav-login">Login</Link>
        </nav>
      </header>
      <main>{children}</main>
    </div>
  );
}

function Home() {
  return (
    <Layout>
      <h1 data-test-id="home-title">Welcome to CodeBites</h1>
      <p>Share, edit and discover recipes — drag-and-drop images supported.</p>
      <Link to="/recipes" id="cta-browse">Browse recipes</Link>
    </Layout>
  );
}

function Login() {
  const navigate = useNavigate();
  const [error, setError] = useState("");
  const submit = (e) => {
    e.preventDefault();
    const data = new FormData(e.target);
    if (data.get("email") && data.get("password")) {
      sessionStorage.setItem("codebites:user", data.get("email"));
      navigate("/recipes");
    } else {
      setError("Please fill in both fields.");
    }
  };
  return (
    <Layout>
      <h1>Login</h1>
      <form onSubmit={submit} aria-label="login-form">
        <input id="email" name="email" type="email" placeholder="Email" />
        <input id="password" name="password" type="password" placeholder="Password" />
        <button type="submit" id="login-submit">Sign in</button>
        {error && <p role="alert" data-test-id="login-error">{error}</p>}
      </form>
    </Layout>
  );
}

function Register() {
  const navigate = useNavigate();
  const submit = (e) => {
    e.preventDefault();
    sessionStorage.setItem("codebites:user", new FormData(e.target).get("email"));
    navigate("/recipes");
  };
  return (
    <Layout>
      <h1>Register</h1>
      <form onSubmit={submit}>
        <input id="reg-name" name="name" placeholder="Full name" />
        <input id="reg-email" name="email" type="email" placeholder="Email" />
        <input id="reg-password" name="password" type="password" placeholder="Password" />
        <button type="submit" id="register-submit">Create account</button>
      </form>
    </Layout>
  );
}

function RecipeList() {
  const [recipes, setRecipes] = useState(loadRecipes());
  return (
    <Layout>
      <h1 data-test-id="recipes-title">Recipes</h1>
      <Link to="/recipes/new" id="new-recipe">+ New recipe</Link>
      <ul data-test-id="recipes-list">
        {recipes.map((r) => (
          <li key={r.id} data-recipe-id={r.id}>
            <Link to={`/recipes/${r.id}`}>{r.title}</Link>
            <button
              data-test-id={`delete-${r.id}`}
              onClick={() => { deleteRecipe(r.id); setRecipes(loadRecipes()); }}
            >Delete</button>
          </li>
        ))}
      </ul>
      {recipes.length === 0 && <p data-test-id="empty-state">No recipes yet.</p>}
    </Layout>
  );
}

function RecipeForm({ initial = {}, onSubmit, submitLabel = "Save" }) {
  const [title, setTitle] = useState(initial.title || "");
  const [body, setBody] = useState(initial.body || "");
  const [image, setImage] = useState(initial.image || "");
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: { "image/*": [] },
    onDrop: (files) => {
      const reader = new FileReader();
      reader.onload = () => setImage(reader.result);
      reader.readAsDataURL(files[0]);
    },
  });

  return (
    <form
      onSubmit={(e) => { e.preventDefault(); onSubmit({ title, body, image }); }}
      aria-label="recipe-form"
    >
      <input id="recipe-title" name="title" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Title" required />
      <textarea id="recipe-body" name="body" value={body} onChange={(e) => setBody(e.target.value)} placeholder="Description" required />
      <div {...getRootProps()} id="recipe-dropzone" data-test-id="dropzone" className={isDragActive ? "active" : ""}>
        <input {...getInputProps()} />
        {image ? <img src={image} alt="recipe" style={{ maxWidth: 200 }} /> : <p>Drag &amp; drop an image, or click to select</p>}
      </div>
      <button type="submit" id="recipe-submit">{submitLabel}</button>
    </form>
  );
}

function RecipeNew() {
  const navigate = useNavigate();
  return (
    <Layout>
      <h1 data-test-id="new-recipe-title">New recipe</h1>
      <RecipeForm
        submitLabel="Create"
        onSubmit={(data) => { addRecipe(data); navigate("/recipes"); }}
      />
    </Layout>
  );
}

function RecipeDetail() {
  const { id } = useParams();
  const recipe = loadRecipes().find((r) => r.id === id);
  if (!recipe) return <Layout><p data-test-id="not-found">Recipe not found.</p></Layout>;
  return (
    <Layout>
      <h1 data-test-id="recipe-title">{recipe.title}</h1>
      {recipe.image && <img src={recipe.image} alt={recipe.title} style={{ maxWidth: 320 }} />}
      <p data-test-id="recipe-body">{recipe.body}</p>
      <Link to={`/recipes/${id}/edit`} id="edit-link">Edit</Link>
    </Layout>
  );
}

function RecipeEdit() {
  const { id } = useParams();
  const navigate = useNavigate();
  const recipe = loadRecipes().find((r) => r.id === id);
  if (!recipe) return <Layout><p data-test-id="not-found">Recipe not found.</p></Layout>;
  return (
    <Layout>
      <h1>Edit recipe</h1>
      <RecipeForm
        initial={recipe}
        submitLabel="Update"
        onSubmit={(data) => { updateRecipe(id, data); navigate(`/recipes/${id}`); }}
      />
    </Layout>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/recipes" element={<RecipeList />} />
      <Route path="/recipes/new" element={<RecipeNew />} />
      <Route path="/recipes/:id" element={<RecipeDetail />} />
      <Route path="/recipes/:id/edit" element={<RecipeEdit />} />
    </Routes>
  );
}
