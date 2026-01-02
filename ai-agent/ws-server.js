#!/usr/bin/env node

/**
 * WebSocket streaming server
 * Streams AI responses in real-time
 */

const WebSocket = require("ws");
const route = require("./router");
const { formatPrompt } = require("./roles");
const budget = require("./budget");

const PORT = process.env.WS_PORT || 8788;

const wss = new WebSocket.Server({ port: PORT });

wss.on("connection", (ws) => {
  console.log("[WS] Client connected");

  ws.on("message", async (msg) => {
    try {
      const { prompt, role, model } = JSON.parse(msg.toString());

      if (!prompt) {
        ws.send(JSON.stringify({ error: "prompt required" }));
        return;
      }

      // Send start event
      ws.send(JSON.stringify({
        type: "start",
        prompt: prompt.substring(0, 100)
      }));

      const finalPrompt = role ? formatPrompt(role, prompt) : prompt;
      const result = await route(finalPrompt, model);

      // Stream chunks (simulated for non-streaming APIs)
      const chunks = result.output.split(/(?<=\.)\s+/);
      for (const chunk of chunks) {
        ws.send(JSON.stringify({
          type: "chunk",
          content: chunk + " "
        }));
        await new Promise(r => setTimeout(r, 50)); // Simulate streaming
      }

      // Send completion
      ws.send(JSON.stringify({
        type: "done",
        model: result.model,
        escalated: result.escalated || false,
        budget: budget.get()
      }));

    } catch (e) {
      console.error("[WS ERROR]", e);
      ws.send(JSON.stringify({
        type: "error",
        error: e.message
      }));
    }
  });

  ws.on("close", () => {
    console.log("[WS] Client disconnected");
  });

  ws.on("error", (err) => {
    console.error("[WS ERROR]", err);
  });
});

console.log(`🔌 WebSocket AI stream running on ws://localhost:${PORT}`);
console.log("   Send: { \"prompt\": \"your question\", \"role\": \"POD_AGENT\" }");
