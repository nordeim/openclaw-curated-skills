#!/usr/bin/env node
"use strict";

// Telegram Mini App Canvas server
// - HTTP server for static files + REST endpoints
// - WebSocket server for pushing canvas updates

const http = require("http");
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const { WebSocketServer } = require("ws");

// ---- Config ----
const BOT_TOKEN = process.env.BOT_TOKEN || "";
const ALLOWED_USER_IDS = (process.env.ALLOWED_USER_IDS || "")
  .split(",")
  .map((s) => s.trim())
  .filter(Boolean);
const JWT_SECRET = process.env.JWT_SECRET || crypto.randomBytes(32).toString("hex");
const JWT_TTL_SECONDS = parseInt(process.env.JWT_TTL_SECONDS || "900", 10); // 15m
const INIT_DATA_MAX_AGE_SECONDS = parseInt(process.env.INIT_DATA_MAX_AGE_SECONDS || "300", 10); // 5m
const PORT = parseInt(process.env.PORT || "3721", 10);
const PUSH_TOKEN = process.env.PUSH_TOKEN || ""; // optional
const RATE_LIMIT_AUTH_PER_MIN = parseInt(process.env.RATE_LIMIT_AUTH_PER_MIN || "30", 10);
const RATE_LIMIT_STATE_PER_MIN = parseInt(process.env.RATE_LIMIT_STATE_PER_MIN || "120", 10);

// ---- Helpers ----
const MINIAPP_DIR = path.join(__dirname, "miniapp");

function isLoopbackAddress(addr) {
  return addr === "127.0.0.1" || addr === "::1" || addr === "::ffff:127.0.0.1";
}

function sendJson(res, statusCode, obj) {
  const body = JSON.stringify(obj);
  res.writeHead(statusCode, {
    "Content-Type": "application/json",
    "Content-Length": Buffer.byteLength(body),
  });
  res.end(body);
}

function readBodyJson(req) {
  return new Promise((resolve, reject) => {
    let data = "";
    req.on("data", (chunk) => {
      data += chunk;
      if (data.length > 1e6) {
        // 1MB limit
        req.destroy();
        reject(new Error("Body too large"));
      }
    });
    req.on("end", () => {
      try {
        const parsed = JSON.parse(data || "{}");
        resolve(parsed);
      } catch (err) {
        reject(err);
      }
    });
    req.on("error", reject);
  });
}

function base64url(input) {
  return Buffer.from(input)
    .toString("base64")
    .replace(/=/g, "")
    .replace(/\+/g, "-")
    .replace(/\//g, "_");
}

function signJwt(payload) {
  const header = { alg: "HS256", typ: "JWT" };
  const headerB64 = base64url(JSON.stringify(header));
  const payloadB64 = base64url(JSON.stringify(payload));
  const data = `${headerB64}.${payloadB64}`;
  const sig = crypto.createHmac("sha256", JWT_SECRET).update(data).digest("base64")
    .replace(/=/g, "")
    .replace(/\+/g, "-")
    .replace(/\//g, "_");
  return `${data}.${sig}`;
}

function verifyJwt(token) {
  try {
    const parts = token.split(".");
    if (parts.length !== 3) return null;
    const [headerB64, payloadB64, sig] = parts;
    const data = `${headerB64}.${payloadB64}`;
    const expectedSig = crypto.createHmac("sha256", JWT_SECRET).update(data).digest("base64")
      .replace(/=/g, "")
      .replace(/\+/g, "-")
      .replace(/\//g, "_");
    if (!crypto.timingSafeEqual(Buffer.from(sig), Buffer.from(expectedSig))) return null;
    const payloadJson = Buffer.from(payloadB64.replace(/-/g, "+").replace(/_/g, "/"), "base64").toString();
    const payload = JSON.parse(payloadJson);
    const now = Math.floor(Date.now() / 1000);
    if (!payload.exp) return null;
    if (now > payload.exp) return null;
    if (payload.iat && payload.iat > now + 60) return null;
    return payload;
  } catch (err) {
    return null;
  }
}

function verifyTelegramInitData(initData) {
  if (!BOT_TOKEN) {
    return { ok: false, error: "BOT_TOKEN not configured" };
  }
  const params = new URLSearchParams(initData);
  const hash = params.get("hash");
  if (!hash) return { ok: false, error: "Missing hash" };

  // Build data check string
  const pairs = [];
  for (const [key, value] of params.entries()) {
    if (key === "hash") continue;
    pairs.push([key, value]);
  }
  pairs.sort((a, b) => a[0].localeCompare(b[0]));
  const dataCheckString = pairs.map(([k, v]) => `${k}=${v}`).join("\n");

  // HMAC-SHA256 per Telegram spec:
  // secret_key = HMAC-SHA256(key="WebAppData", data=BOT_TOKEN)
  const secretKey = crypto.createHmac("sha256", "WebAppData").update(BOT_TOKEN).digest();
  const computedHash = crypto.createHmac("sha256", secretKey).update(dataCheckString).digest("hex");

  if (computedHash !== hash) {
    return { ok: false, error: "Invalid initData hash" };
  }

  const userRaw = params.get("user");
  let user = null;
  try {
    user = userRaw ? JSON.parse(userRaw) : null;
  } catch (_) {
    return { ok: false, error: "Invalid user JSON" };
  }

  if (!user || typeof user.id === "undefined") {
    return { ok: false, error: "Missing user.id" };
  }

  if (!ALLOWED_USER_IDS.includes(String(user.id))) {
    return { ok: false, error: "User not allowed" };
  }

  const authDate = parseInt(params.get("auth_date") || "0", 10);
  if (!authDate) {
    return { ok: false, error: "Missing auth_date" };
  }
  const nowSec = Math.floor(Date.now() / 1000);
  if (authDate > nowSec + 60) {
    return { ok: false, error: "auth_date is in the future" };
  }
  if (nowSec - authDate > INIT_DATA_MAX_AGE_SECONDS) {
    return { ok: false, error: "initData expired" };
  }

  const replayKey = `${user.id}:${authDate}:${hash}`;
  if (isInitDataReplayed(replayKey)) {
    return { ok: false, error: "initData replayed" };
  }
  markInitDataUsed(replayKey, INIT_DATA_MAX_AGE_SECONDS);

  return { ok: true, user };
}

function contentTypeFor(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  switch (ext) {
    case ".html": return "text/html";
    case ".js": return "text/javascript";
    case ".css": return "text/css";
    case ".json": return "application/json";
    case ".png": return "image/png";
    case ".jpg":
    case ".jpeg": return "image/jpeg";
    case ".svg": return "image/svg+xml";
    case ".gif": return "image/gif";
    default: return "application/octet-stream";
  }
}

function serveFile(res, filePath) {
  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404);
      res.end("Not found");
      return;
    }
    res.writeHead(200, { "Content-Type": contentTypeFor(filePath) });
    res.end(data);
  });
}

// ---- Simple in-memory rate limiter ----
const rateLimitBuckets = new Map();
function rateLimit(key, limit, windowMs) {
  const now = Date.now();
  const bucket = rateLimitBuckets.get(key) || { count: 0, resetAt: now + windowMs };
  if (now > bucket.resetAt) {
    bucket.count = 0;
    bucket.resetAt = now + windowMs;
  }
  bucket.count += 1;
  rateLimitBuckets.set(key, bucket);
  return bucket.count <= limit;
}

// ---- initData replay cache ----
const initDataReplay = new Map();
function markInitDataUsed(key, ttlSeconds) {
  const now = Date.now();
  initDataReplay.set(key, now + ttlSeconds * 1000);
}
function isInitDataReplayed(key) {
  const now = Date.now();
  const expires = initDataReplay.get(key);
  if (!expires) return false;
  if (now > expires) {
    initDataReplay.delete(key);
    return false;
  }
  return true;
}

// ---- In-memory canvas state ----
let currentState = null; // { content, format }

// ---- WebSocket management ----
const wsClients = new Set();

function broadcast(obj) {
  const msg = JSON.stringify(obj);
  let count = 0;
  for (const ws of wsClients) {
    if (ws.readyState === ws.OPEN) {
      ws.send(msg);
      count++;
    }
  }
  return count;
}

// ---- HTTP server ----
const server = http.createServer(async (req, res) => {
  try {
    const url = new URL(req.url, `http://${req.headers.host}`);

    // Serve index
    if (req.method === "GET" && url.pathname === "/") {
      const indexPath = path.join(MINIAPP_DIR, "index.html");
      return serveFile(res, indexPath);
    }

    // Serve static miniapp files
    if (req.method === "GET" && url.pathname.startsWith("/miniapp/")) {
      const relPath = url.pathname.replace("/miniapp/", "");
      const safePath = path.normalize(relPath).replace(/^\.\.(\/|\\|$)/, "");
      const filePath = path.join(MINIAPP_DIR, safePath);
      return serveFile(res, filePath);
    }

    // Auth endpoint
    if (req.method === "POST" && url.pathname === "/auth") {
      const ip = req.socket.remoteAddress || "unknown";
      if (!rateLimit(`auth:${ip}`, RATE_LIMIT_AUTH_PER_MIN, 60_000)) {
        return sendJson(res, 429, { error: "Rate limit" });
      }
      const body = await readBodyJson(req);
      const initData = body.initData;
      if (!initData) return sendJson(res, 400, { error: "Missing initData" });

      const result = verifyTelegramInitData(initData);
      if (!result.ok) return sendJson(res, 401, { error: result.error });

      const now = Math.floor(Date.now() / 1000);
      const exp = now + JWT_TTL_SECONDS;
      const token = signJwt({ userId: String(result.user.id), iat: now, exp, jti: crypto.randomUUID() });
      return sendJson(res, 200, {
        token,
        user: { id: result.user.id, username: result.user.username || null },
      });
    }

    // State endpoint
    if (req.method === "GET" && url.pathname === "/state") {
      const ip = req.socket.remoteAddress || "unknown";
      if (!rateLimit(`state:${ip}`, RATE_LIMIT_STATE_PER_MIN, 60_000)) {
        return sendJson(res, 429, { error: "Rate limit" });
      }
      const token = url.searchParams.get("token") || "";
      const payload = verifyJwt(token);
      if (!payload) return sendJson(res, 401, { error: "Invalid token" });
      if (currentState) {
        return sendJson(res, 200, { content: currentState.content, format: currentState.format });
      }
      return sendJson(res, 200, { content: null });
    }

    // Health endpoint
    if (req.method === "GET" && url.pathname === "/health") {
      return sendJson(res, 200, {
        ok: true,
        uptime: process.uptime(),
        clients: wsClients.size,
        hasState: !!currentState,
      });
    }

    // Push endpoint (loopback only)
    if (req.method === "POST" && url.pathname === "/push") {
      if (!isLoopbackAddress(req.socket.remoteAddress)) {
        return sendJson(res, 403, { error: "Forbidden" });
      }
      if (PUSH_TOKEN) {
        const headerToken = req.headers["x-push-token"] || "";
        const auth = req.headers["authorization"] || "";
        const bearer = auth.startsWith("Bearer ") ? auth.slice(7) : "";
        const queryToken = url.searchParams.get("token") || "";
        const provided = headerToken || bearer || queryToken;
        if (provided !== PUSH_TOKEN) {
          return sendJson(res, 401, { error: "Invalid push token" });
        }
      }

      const ip = req.socket.remoteAddress || 'unknown';
      if (!rateLimit(`auth:${ip}`, RATE_LIMIT_AUTH_PER_MIN, 60_000)) {
        return sendJson(res, 429, { error: "Rate limit" });
      }
      const body = await readBodyJson(req);

      let content = body.content;
      let format = body.format || null;

      if (!format) {
        if (typeof body.html !== "undefined") {
          format = "html";
          content = body.html;
        } else if (typeof body.markdown !== "undefined") {
          format = "markdown";
          content = body.markdown;
        } else if (typeof body.text !== "undefined") {
          format = "text";
          content = body.text;
        } else if (typeof body.a2ui !== "undefined") {
          format = "a2ui";
          content = body.a2ui;
        }
      }

      if (!format) format = "html";
      if (typeof content === "undefined" || content === null) {
        return sendJson(res, 400, { error: "Missing content" });
      }

      currentState = { content, format };
      const clients = broadcast({ type: "canvas", content, format });
      return sendJson(res, 200, { ok: true, clients });
    }

    // Clear endpoint (loopback only)
    if (req.method === "POST" && url.pathname === "/clear") {
      if (!isLoopbackAddress(req.socket.remoteAddress)) {
        return sendJson(res, 403, { error: "Forbidden" });
      }
      currentState = null;
      broadcast({ type: "clear" });
      return sendJson(res, 200, { ok: true });
    }

    res.writeHead(404);
    res.end("Not found");
  } catch (err) {
    console.error("Request error:", err);
    sendJson(res, 500, { error: "Internal server error" });
  }
});

// ---- WebSocket server ----
const wss = new WebSocketServer({ noServer: true });

wss.on("connection", (ws, req, payload) => {
  wsClients.add(ws);

  // Send current state on connect
  if (currentState) {
    ws.send(JSON.stringify({ type: "canvas", content: currentState.content, format: currentState.format }));
  }

  ws.on("message", (data) => {
    try {
      const msg = JSON.parse(data.toString());
      if (msg && msg.type === "pong") {
        // keepalive response
      }
    } catch (_) {
      // ignore malformed
    }
  });

  ws.on("close", () => {
    wsClients.delete(ws);
  });
});

server.on("upgrade", (req, socket, head) => {
  const url = new URL(req.url, `http://${req.headers.host}`);
  if (url.pathname !== "/ws") {
    socket.destroy();
    return;
  }
  const ip = req.socket.remoteAddress || "unknown";
  if (!rateLimit(`ws:${ip}`, RATE_LIMIT_AUTH_PER_MIN, 60_000)) {
    socket.write("HTTP/1.1 429 Too Many Requests\r\n\r\n");
    socket.destroy();
    return;
  }
  const token = url.searchParams.get("token") || "";
  const payload = verifyJwt(token);
  if (!payload) {
    socket.write("HTTP/1.1 401 Unauthorized\r\n\r\n");
    socket.destroy();
    return;
  }
  wss.handleUpgrade(req, socket, head, (ws) => {
    wss.emit("connection", ws, req, payload);
  });
});

// Keepalive ping every 30s
setInterval(() => {
  broadcast({ type: "ping" });
}, 30_000).unref();

server.listen(PORT, () => {
  console.log(`tg-canvas server listening on :${PORT}`);
});
