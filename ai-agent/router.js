/**
 * GPT ↔ Claude router with uncertainty detection
 * Automatically escalates to Claude when GPT is uncertain
 */

const budget = require("./budget");

const GPT_COST_PER_CALL = 0.01;
const CLAUDE_COST_PER_CALL = 0.02;

async function callGPT(prompt) {
  const r = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${process.env.OPENAI_API_KEY}`
    },
    body: JSON.stringify({
      model: "gpt-4-turbo-preview",
      temperature: 0.3,
      messages: [{ role: "user", content: prompt }]
    })
  });

  if (!r.ok) {
    throw new Error(`GPT API error: ${r.status} ${await r.text()}`);
  }

  const j = await r.json();
  budget.check(GPT_COST_PER_CALL);
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
    throw new Error(`Claude API error: ${r.status} ${await r.text()}`);
  }

  const j = await r.json();
  budget.check(CLAUDE_COST_PER_CALL);
  return j.content[0].text;
}

function isUncertain(text) {
  const uncertaintyPatterns = [
    /not sure/i,
    /uncertain/i,
    /depends on/i,
    /cannot guarantee/i,
    /might be/i,
    /could be/i,
    /unclear/i,
    /ambiguous/i,
    /need more context/i,
    /hard to say/i
  ];

  return uncertaintyPatterns.some(pattern => pattern.test(text));
}

async function route(prompt, forceModel = null) {
  if (forceModel === "claude") {
    const output = await callClaude(prompt);
    return { model: "claude", output, escalated: false };
  }

  if (forceModel === "gpt") {
    const output = await callGPT(prompt);
    return { model: "gpt", output, escalated: false };
  }

  // Default: GPT first, escalate to Claude if uncertain
  const gpt = await callGPT(prompt);

  if (isUncertain(gpt)) {
    const claude = await callClaude(
      `The following response was uncertain. Provide a definitive, well-reasoned answer:\n\nOriginal prompt: ${prompt}\n\nUncertain response: ${gpt}\n\nYour task: Resolve the uncertainty and provide a clear, actionable answer.`
    );
    return { model: "claude", output: claude, escalated: true, gptResponse: gpt };
  }

  return { model: "gpt", output: gpt, escalated: false };
}

module.exports = route;
module.exports.callGPT = callGPT;
module.exports.callClaude = callClaude;
