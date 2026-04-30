const express = require("express");
const session = require("express-session");
const bodyParser = require("body-parser");
const path = require("path");

const app = express();
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, "public")));
app.use(session({ secret: "doc2test", resave: false, saveUninitialized: true }));
app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "views"));

const products = [
  { id: "p1", name: "Wireless Mouse",   price: 19.99, stock: 50 },
  { id: "p2", name: "Mechanical Keyboard", price: 89.00, stock: 25 },
  { id: "p3", name: "USB-C Hub",        price: 29.50, stock: 40 },
  { id: "p4", name: "27\" Monitor",     price: 249.00, stock: 10 },
  { id: "p5", name: "Webcam HD",        price: 59.99, stock: 30 },
  { id: "p6", name: "Standing Desk",    price: 399.00, stock: 5 },
  { id: "p7", name: "Office Chair",     price: 199.00, stock: 12 },
  { id: "p8", name: "Headset",          price: 79.00, stock: 22 },
];
const orders = {};

const requireAuth = (req, res, next) =>
  req.session.user ? next() : res.redirect("/login");

app.get("/", (req, res) => res.render("home", { user: req.session.user }));

app.get("/login", (req, res) => res.render("login", { error: null }));
app.post("/login", (req, res) => {
  const { email, password } = req.body;
  if (email && password) {
    req.session.user = { email };
    req.session.cart = req.session.cart || [];
    return res.redirect("/products");
  }
  res.render("login", { error: "Email and password required" });
});
app.post("/logout", (req, res) => req.session.destroy(() => res.redirect("/")));

app.get("/register", (req, res) => res.render("register"));
app.post("/register", (req, res) => {
  req.session.user = { email: req.body.email };
  req.session.cart = [];
  res.redirect("/products");
});

app.get("/products", (req, res) =>
  res.render("products", { products, user: req.session.user }));

app.get("/products/:id", (req, res) => {
  const p = products.find((x) => x.id === req.params.id);
  if (!p) return res.status(404).send("Not found");
  res.render("product", { product: p, user: req.session.user });
});

app.post("/cart/add", requireAuth, (req, res) => {
  req.session.cart = req.session.cart || [];
  const { productId, quantity } = req.body;
  const existing = req.session.cart.find((c) => c.productId === productId);
  if (existing) existing.quantity += parseInt(quantity || "1", 10);
  else req.session.cart.push({ productId, quantity: parseInt(quantity || "1", 10) });
  res.json({ ok: true, cartSize: req.session.cart.reduce((s, c) => s + c.quantity, 0) });
});

app.get("/cart", requireAuth, (req, res) => {
  const cart = (req.session.cart || []).map((c) => ({
    ...c, product: products.find((p) => p.id === c.productId),
  }));
  const total = cart.reduce((s, c) => s + c.product.price * c.quantity, 0);
  res.render("cart", { cart, total, user: req.session.user });
});

app.post("/cart/remove", requireAuth, (req, res) => {
  req.session.cart = (req.session.cart || []).filter((c) => c.productId !== req.body.productId);
  res.redirect("/cart");
});

app.get("/checkout", requireAuth, (req, res) => {
  const cart = req.session.cart || [];
  if (!cart.length) return res.redirect("/cart");
  res.render("checkout", { user: req.session.user });
});

app.post("/checkout", requireAuth, (req, res) => {
  const id = "ORD-" + Date.now();
  orders[id] = { user: req.session.user, items: req.session.cart || [], shipping: req.body, status: "CONFIRMED" };
  req.session.cart = [];
  res.redirect(`/orders/${id}`);
});

app.get("/orders/:id", requireAuth, (req, res) => {
  const o = orders[req.params.id];
  if (!o) return res.status(404).send("Not found");
  res.render("order", { order: o, id: req.params.id, products });
});

app.get("/orders", requireAuth, (req, res) => res.render("orders", { orders }));
app.get("/account", requireAuth, (req, res) => res.render("account", { user: req.session.user }));
app.get("/about", (req, res) => res.render("about"));
app.get("/contact", (req, res) => res.render("contact", { sent: false }));
app.post("/contact", (req, res) => res.render("contact", { sent: true }));
app.get("/health", (req, res) => res.json({ status: "ok" }));

const port = process.env.PORT || 3000;
app.listen(port, "0.0.0.0", () => console.log(`PRATICA-DAI on :${port}`));
