#!/usr/bin/env node

/**
 * StaticWaves AI Agent Daemon
 * HTTP API for GPT↔Claude orchestration
 */

const http = require("http");
const route = require("./router");
const memory = require("./memory");
const budget = require("./budget");
const { runMultiAgent, runChain } = require("./agents");
const { formatPrompt, availableRoles } = require("./roles");
const episodes = require("./episodes");

const PORT = process.env.AI_AGENT_PORT || 8787;

async function handleRequest(req, res) {
  // CORS for dashboard
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") {
    res.writeHead(204);
    return res.end();
  }

  // Health check
  if (req.method === "GET" && req.url === "/health") {
    res.writeHead(200, { "Content-Type": "application/json" });
    return res.end(JSON.stringify({
      status: "ok",
      budget: budget.get(),
      roles: availableRoles()
    }));
  }

  // Single prompt
  if (req.method === "POST" && req.url === "/run") {
    let body = "";
    req.on("data", d => (body += d));
    req.on("end", async () => {
      try {
        const { prompt, scope, role, model } = JSON.parse(body);

        if (!prompt) {
          res.writeHead(400, { "Content-Type": "application/json" });
          return res.end(JSON.stringify({ error: "prompt required" }));
        }

        const finalPrompt = role ? formatPrompt(role, prompt) : prompt;
        const result = await route(finalPrompt, model);

        if (scope) {
          memory.remember(scope, "last", result.output);
        }

        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(JSON.stringify({
          result: result.output,
          model: result.model,
          escalated: result.escalated || false,
          budget: budget.get()
        }));
      } catch (e) {
        console.error("[ERROR]", e);
        res.writeHead(500, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: e.message }));
      }
    });
    return;
  }

  // Multi-agent orchestration
  if (req.method === "POST" && req.url === "/multi") {
    let body = "";
    req.on("data", d => (body += d));
    req.on("end", async () => {
      try {
        const { goal, role } = JSON.parse(body);

        if (!goal) {
          res.writeHead(400, { "Content-Type": "application/json" });
          return res.end(JSON.stringify({ error: "goal required" }));
        }

        const result = await runMultiAgent(goal, role);

        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(JSON.stringify({
          ...result,
          budget: budget.get()
        }));
      } catch (e) {
        console.error("[ERROR]", e);
        res.writeHead(500, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: e.message }));
      }
    });
    return;
  }

  // Task chain
  if (req.method === "POST" && req.url === "/chain") {
    let body = "";
    req.on("data", d => (body += d));
    req.on("end", async () => {
      try {
        const { tasks, role } = JSON.parse(body);

        if (!tasks || !Array.isArray(tasks)) {
          res.writeHead(400, { "Content-Type": "application/json" });
          return res.end(JSON.stringify({ error: "tasks array required" }));
        }

        const result = await runChain(tasks, role);

        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(JSON.stringify({
          ...result,
          budget: budget.get()
        }));
      } catch (e) {
        console.error("[ERROR]", e);
        res.writeHead(500, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: e.message }));
      }
    });
    return;
  }

  // Memory recall
  if (req.method === "GET" && req.url.startsWith("/memory")) {
    const url = new URL(req.url, `http://localhost:${PORT}`);
    const scope = url.searchParams.get("scope");

    if (!scope) {
      res.writeHead(400, { "Content-Type": "application/json" });
      return res.end(JSON.stringify({ error: "scope required" }));
    }

    const value = memory.recall(scope, "last");
    const history = memory.history(scope, 5);

    res.writeHead(200, { "Content-Type": "application/json" });
    return res.end(JSON.stringify({ value, history }));
  }

  // Episodes
  if (req.method === "GET" && req.url === "/episodes") {
    try {
      const recent = await episodes.recentEpisodes(10);
      res.writeHead(200, { "Content-Type": "application/json" });
      return res.end(JSON.stringify({ episodes: recent }));
    } catch (e) {
      res.writeHead(500, { "Content-Type": "application/json" });
      return res.end(JSON.stringify({ error: e.message }));
    }
  }

  // Budget
  if (req.method === "GET" && req.url === "/budget") {
    res.writeHead(200, { "Content-Type": "application/json" });
    return res.end(JSON.stringify(budget.get()));
  }

  // 404
  res.writeHead(404, { "Content-Type": "application/json" });
  res.end(JSON.stringify({ error: "Not found" }));
}

const server = http.createServer(handleRequest);

server.listen(PORT, () => {
  console.log(`🧠 StaticWaves AI Agent running on http://localhost:${PORT}`);
  console.log(`   Budget: $${budget.get().limit}/day`);
  console.log(`   Roles: ${availableRoles().join(", ")}`);
  console.log("");
  console.log("Endpoints:");
  console.log("  POST /run      - Single prompt");
  console.log("  POST /multi    - Multi-agent (plan→execute→critique)");
  console.log("  POST /chain    - Task chain");
  console.log("  GET  /memory   - Recall memory");
  console.log("  GET  /episodes - Recent decisions");
  console.log("  GET  /budget   - Current spend");
  console.log("  GET  /health   - Health check");
});

// Graceful shutdown
process.on("SIGTERM", async () => {
  console.log("\n[SHUTDOWN] Closing connections...");
  await episodes.close();
  server.close(() => {
    console.log("[SHUTDOWN] Server closed");
    process.exit(0);
  });
});
