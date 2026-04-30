const express = require("express");
const http = require("http");
const path = require("path");
const { WebSocketServer } = require("ws");

const app = express();
app.use(express.static(path.join(__dirname, "public")));
app.get("/health", (req, res) => res.json({ status: "ok" }));

const server = http.createServer(app);
const wss = new WebSocketServer({ server, path: "/ws" });

const WORDS = [
  { word: "DOG", taboo: ["puppy", "bark", "tail", "pet"] },
  { word: "BEACH", taboo: ["sand", "sea", "wave", "sun"] },
  { word: "PIZZA", taboo: ["cheese", "tomato", "italy", "slice"] },
  { word: "CAR", taboo: ["wheel", "drive", "engine", "road"] },
];
const rooms = new Map();

function broadcast(roomId, msg) {
  const room = rooms.get(roomId);
  if (!room) return;
  const payload = JSON.stringify(msg);
  for (const c of room.clients) try { c.send(payload); } catch {}
}

function nextTurn(roomId) {
  const room = rooms.get(roomId);
  if (!room) return;
  room.activeIdx = (room.activeIdx + 1) % room.players.length;
  room.card = WORDS[Math.floor(Math.random() * WORDS.length)];
  room.deadline = Date.now() + 60_000;
  broadcast(roomId, { type: "turn", active: room.players[room.activeIdx], card: room.card, deadline: room.deadline, score: room.score });
}

wss.on("connection", (ws) => {
  ws.on("message", (raw) => {
    let m; try { m = JSON.parse(raw); } catch { return; }
    if (m.type === "join") {
      let room = rooms.get(m.roomId);
      if (!room) { room = { id: m.roomId, players: [], activeIdx: -1, score: 0, clients: new Set() }; rooms.set(m.roomId, room); }
      room.clients.add(ws);
      ws.roomId = m.roomId;
      ws.player = m.player;
      if (!room.players.includes(m.player)) room.players.push(m.player);
      broadcast(m.roomId, { type: "lobby", players: room.players });
      if (room.players.length >= 2 && room.activeIdx === -1) nextTurn(m.roomId);
    }
    if (m.type === "guess") {
      const room = rooms.get(ws.roomId);
      if (!room) return;
      const correct = room.card && m.guess && m.guess.toUpperCase() === room.card.word;
      if (correct) { room.score += 1; broadcast(ws.roomId, { type: "correct", by: ws.player, score: room.score }); nextTurn(ws.roomId); }
      else broadcast(ws.roomId, { type: "wrong", by: ws.player, guess: m.guess });
    }
    if (m.type === "skip") {
      if (rooms.has(ws.roomId)) nextTurn(ws.roomId);
    }
  });
  ws.on("close", () => {
    const room = rooms.get(ws.roomId);
    if (room) room.clients.delete(ws);
  });
});

const port = process.env.PORT || 3000;
server.listen(port, "0.0.0.0", () => console.log(`Taboo on :${port}`));
