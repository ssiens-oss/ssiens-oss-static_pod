#!/usr/bin/env node

/**
 * GPT ↔ Claude bridge script
 * Modes: parallel | gpt-first | claude-first | arbiter
 */

const mode = process.argv[2] || "parallel";
const input = process.argv.slice(3).join(" ");

if (!input) {
  console.error("Usage: node ai-bridge.js <mode> <prompt>");
  console.error("");
  console.error("Modes:");
  console.error("  parallel      - Both answer simultaneously");
  console.error("  gpt-first     - GPT answers, Claude refines");
  console.error("  claude-first  - Claude answers, GPT optimizes");
  console.error("  arbiter       - Both answer, GPT merges best");
  console.error("");
  console.error("Example:");
  console.error('  node ai-bridge.js arbiter "Review this API design"');
  process.exit(1);
}

async function callGPT(prompt) {
  const r = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${process.env.OPENAI_API_KEY}`
    },
    body: JSON.stringify({
      model: "gpt-4-turbo-preview",
      messages: [{ role: "user", content: prompt }],
      temperature: 0.3
    })
  });

  if (!r.ok) {
    throw new Error(`GPT API error: ${r.status}`);
  }

  const j = await r.json();
  return j.choices[0].message.content;
}

async function callClaude(prompt) {
  const r = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": process.env.ANTHROPIC_API_KEY,
      "anthropic-version": "2023-06-01"
    },
    body: JSON.stringify({
      model: "claude-3-5-sonnet-20241022",
      max_tokens: 2048,
      messages: [{ role: "user", content: prompt }]
    })
  });

  if (!r.ok) {
    throw new Error(`Claude API error: ${r.status}`);
  }

  const j = await r.json();
  return j.content[0].text;
}

(async () => {
  console.log(`🤖 Running in ${mode} mode...\n`);

  if (mode === "parallel") {
    console.log("⏳ Querying GPT and Claude simultaneously...\n");
    const [gpt, claude] = await Promise.all([
      callGPT(input),
      callClaude(input)
    ]);

    console.log("═".repeat(60));
    console.log("GPT-4 RESPONSE:");
    console.log("═".repeat(60));
    console.log(gpt);
    console.log("\n" + "═".repeat(60));
    console.log("CLAUDE RESPONSE:");
    console.log("═".repeat(60));
    console.log(claude);
  }

  if (mode === "gpt-first") {
    console.log("⏳ GPT answering first...\n");
    const gpt = await callGPT(input);
    console.log("═".repeat(60));
    console.log("GPT RESPONSE:");
    console.log("═".repeat(60));
    console.log(gpt);

    console.log("\n⏳ Claude refining...\n");
    const claude = await callClaude(
      `Review, critique, and improve this response:\n\n${gpt}\n\nProvide an enhanced version.`
    );
    console.log("═".repeat(60));
    console.log("CLAUDE REFINED:");
    console.log("═".repeat(60));
    console.log(claude);
  }

  if (mode === "claude-first") {
    console.log("⏳ Claude answering first...\n");
    const claude = await callClaude(input);
    console.log("═".repeat(60));
    console.log("CLAUDE RESPONSE:");
    console.log("═".repeat(60));
    console.log(claude);

    console.log("\n⏳ GPT optimizing...\n");
    const gpt = await callGPT(
      `Refine and production-harden this response:\n\n${claude}\n\nMake it more actionable and concrete.`
    );
    console.log("═".repeat(60));
    console.log("GPT OPTIMIZED:");
    console.log("═".repeat(60));
    console.log(gpt);
  }

  if (mode === "arbiter") {
    console.log("⏳ Getting answers from both...\n");
    const [gpt, claude] = await Promise.all([
      callGPT(input),
      callClaude(input)
    ]);

    console.log("⏳ Merging best parts...\n");
    const judge = await callGPT(`
Two AI answers below. Merge the best parts into one final, optimal answer.

GPT-4:
${gpt}

CLAUDE:
${claude}

Provide the merged, best-of-both answer:`);

    console.log("═".repeat(60));
    console.log("FINAL MERGED ANSWER:");
    console.log("═".repeat(60));
    console.log(judge);
  }

  console.log("\n✅ Complete");
})().catch(err => {
  console.error("❌ Error:", err.message);
  process.exit(1);
});
