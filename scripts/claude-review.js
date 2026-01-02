#!/usr/bin/env node

/**
 * Local Claude code review script
 * Run: node scripts/claude-review.js [path]
 */

const fs = require("fs");
const path = require("path");

const API_KEY = process.env.ANTHROPIC_API_KEY;
if (!API_KEY) {
  console.error("❌ ANTHROPIC_API_KEY not set");
  console.error("   export ANTHROPIC_API_KEY=sk-ant-...");
  process.exit(1);
}

const TARGET_PATH = process.argv[2] || "backend/src";

async function main() {
  console.log(`🔍 Reviewing code in: ${TARGET_PATH}\n`);

  if (!fs.existsSync(TARGET_PATH)) {
    console.error(`❌ Path not found: ${TARGET_PATH}`);
    process.exit(1);
  }

  const files = collectFiles(TARGET_PATH);
  console.log(`📁 Found ${files.length} files\n`);

  if (files.length === 0) {
    console.log("✅ No files to review");
    return;
  }

  const content = files
    .map(f => `FILE: ${f}\n${"=".repeat(60)}\n${fs.readFileSync(f, "utf8")}`)
    .join("\n\n");

  console.log("🧠 Sending to Claude...\n");

  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": API_KEY,
      "anthropic-version": "2023-06-01"
    },
    body: JSON.stringify({
      model: "claude-3-5-sonnet-20241022",
      max_tokens: 4096,
      messages: [{
        role: "user",
        content: `You are a senior engineer conducting a code review.

Review the following code for:
- 🐛 Bugs and logic errors
- 🔒 Security vulnerabilities (SQL injection, XSS, etc.)
- ⚡ Performance issues
- 🧹 Code quality and maintainability
- 📦 Dependencies and architecture

Provide specific, actionable feedback with file:line references.

Code to review:
${content}
        `
      }]
    })
  });

  if (!res.ok) {
    console.error(`❌ Claude API error: ${res.status}`);
    console.error(await res.text());
    process.exit(1);
  }

  const json = await res.json();
  console.log("📝 REVIEW RESULTS");
  console.log("=".repeat(60));
  console.log(json.content[0].text);
  console.log("\n" + "=".repeat(60));
  console.log(`✅ Review complete`);
}

function collectFiles(dir) {
  let out = [];

  const stats = fs.statSync(dir);
  if (!stats.isDirectory()) {
    // Single file
    if (isCodeFile(dir)) out.push(dir);
    return out;
  }

  // Directory traversal
  for (const item of fs.readdirSync(dir)) {
    if (item.startsWith('.') || item === 'node_modules') continue;

    const p = path.join(dir, item);
    const itemStats = fs.statSync(p);

    if (itemStats.isDirectory()) {
      out.push(...collectFiles(p));
    } else if (isCodeFile(p)) {
      out.push(p);
    }
  }

  return out;
}

function isCodeFile(filepath) {
  const exts = ['.js', '.ts', '.jsx', '.tsx', '.py', '.go', '.rs', '.java'];
  return exts.some(ext => filepath.endsWith(ext));
}

main().catch(e => {
  console.error("❌ Error:", e.message);
  process.exit(1);
});
