/**
 * AI Agent API client
 */

const API_BASE = process.env.NEXT_PUBLIC_AI_AGENT_URL || "http://localhost:8787";
const WS_BASE = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8788";

export interface AgentResponse {
  result: string;
  model: string;
  escalated: boolean;
  budget: Budget;
}

export interface MultiAgentResponse {
  plan: string;
  execution: string;
  critique: string;
  final: string;
  budget: Budget;
}

export interface Budget {
  spent: number;
  limit: number;
  remaining: number;
}

export interface Episode {
  event: string;
  context: string;
  resolution: string;
  outcome: string;
  risk_level: string;
  ts: string;
}

export async function runPrompt(
  prompt: string,
  role?: string,
  model?: string
): Promise<AgentResponse> {
  const res = await fetch(`${API_BASE}/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt, role, model })
  });

  if (!res.ok) {
    throw new Error(`API error: ${res.status}`);
  }

  return res.json();
}

export async function runMultiAgent(
  goal: string,
  role?: string
): Promise<MultiAgentResponse> {
  const res = await fetch(`${API_BASE}/multi`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ goal, role })
  });

  if (!res.ok) {
    throw new Error(`API error: ${res.status}`);
  }

  return res.json();
}

export async function runChain(
  tasks: string[],
  role?: string
): Promise<{ results: any[]; finalContext: string; budget: Budget }> {
  const res = await fetch(`${API_BASE}/chain`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tasks, role })
  });

  if (!res.ok) {
    throw new Error(`API error: ${res.status}`);
  }

  return res.json();
}

export async function getBudget(): Promise<Budget> {
  const res = await fetch(`${API_BASE}/budget`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function getEpisodes(): Promise<{ episodes: Episode[] }> {
  const res = await fetch(`${API_BASE}/episodes`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function getHealth(): Promise<{
  status: string;
  budget: Budget;
  roles: string[];
}> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export function connectWebSocket(
  onMessage: (data: any) => void,
  onError?: (error: Error) => void
): WebSocket {
  const ws = new WebSocket(WS_BASE);

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch (e) {
      console.error("WS parse error:", e);
    }
  };

  ws.onerror = (event) => {
    const error = new Error("WebSocket error");
    if (onError) onError(error);
  };

  return ws;
}

export const ROLES = [
  "POD_AGENT",
  "ADS_AGENT",
  "COMPLIANCE_AGENT",
  "ARCH_AGENT",
  "CI_AGENT"
] as const;

export type Role = typeof ROLES[number];
