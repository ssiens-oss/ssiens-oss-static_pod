/**
 * Multi-agent orchestration
 * Planner → Executor → Critic pattern
 */

const route = require("./router");
const { formatPrompt } = require("./roles");

async function planner(goal, role = null) {
  const prompt = role
    ? formatPrompt(role, `Break this goal into concrete, actionable steps:\n\n${goal}`)
    : `You are a planning expert. Break this goal into concrete, actionable steps:\n\n${goal}\n\nProvide a numbered list of specific tasks.`;

  return route(prompt);
}

async function executor(plan, role = null) {
  const prompt = role
    ? formatPrompt(role, `Execute this plan and provide concrete implementation details:\n\n${plan.output}`)
    : `Execute this plan and provide concrete implementation details:\n\n${plan.output}`;

  return route(prompt);
}

async function critic(result, role = null) {
  const prompt = role
    ? formatPrompt(role, `Review this implementation and suggest improvements:\n\n${result.output}`)
    : `You are a senior technical reviewer. Critique this implementation for:\n- Correctness\n- Security\n- Performance\n- Maintainability\n\nImplementation:\n${result.output}`;

  return route(prompt);
}

async function runMultiAgent(goal, role = null) {
  console.log(`[MULTI-AGENT] Starting: ${goal.substring(0, 50)}...`);

  const plan = await planner(goal, role);
  console.log(`[MULTI-AGENT] Plan created with ${plan.model}`);

  const exec = await executor(plan, role);
  console.log(`[MULTI-AGENT] Executed with ${exec.model}`);

  const critique = await critic(exec, role);
  console.log(`[MULTI-AGENT] Critiqued with ${critique.model}`);

  return {
    plan: plan.output,
    execution: exec.output,
    critique: critique.output,
    final: critique.output
  };
}

async function runChain(tasks, role = null) {
  let context = "";
  const results = [];

  for (const task of tasks) {
    const prompt = role
      ? formatPrompt(role, `${context}\n\nNext task:\n${task}`)
      : `${context}\n\nNext task:\n${task}`;

    const result = await route(prompt);
    context += `\n\nCompleted: ${task}\nResult: ${result.output}`;
    results.push({ task, result: result.output, model: result.model });
  }

  return { results, finalContext: context };
}

module.exports = {
  planner,
  executor,
  critic,
  runMultiAgent,
  runChain
};
