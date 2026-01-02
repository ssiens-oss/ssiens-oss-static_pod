'use client';

import { useState } from 'react';
import { runPrompt, runMultiAgent, ROLES, type Role } from '@/lib/api';

export default function Agents() {
  const [prompt, setPrompt] = useState('');
  const [role, setRole] = useState<Role | ''>('');
  const [mode, setMode] = useState<'single' | 'multi'>('single');
  const [model, setModel] = useState<'auto' | 'gpt' | 'claude'>('auto');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      if (mode === 'single') {
        const res = await runPrompt(
          prompt,
          role || undefined,
          model === 'auto' ? undefined : model
        );
        setResult(res);
      } else {
        const res = await runMultiAgent(prompt, role || undefined);
        setResult(res);
      }
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container">
      <h1 style={{ marginBottom: '2rem' }}>🤖 AI Agents</h1>

      <form onSubmit={handleSubmit}>
        <div className="card">
          <div style={{ marginBottom: '1rem' }}>
            <label>Agent Role</label>
            <select value={role} onChange={e => setRole(e.target.value as Role | '')}>
              <option value="">General Purpose</option>
              {ROLES.map(r => (
                <option key={r} value={r}>{r.replace('_AGENT', '')}</option>
              ))}
            </select>
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <label>Mode</label>
            <select value={mode} onChange={e => setMode(e.target.value as 'single' | 'multi')}>
              <option value="single">Single Agent</option>
              <option value="multi">Multi-Agent (Plan → Execute → Critique)</option>
            </select>
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <label>Model Preference</label>
            <select value={model} onChange={e => setModel(e.target.value as any)}>
              <option value="auto">Auto (GPT → Claude if uncertain)</option>
              <option value="gpt">Force GPT</option>
              <option value="claude">Force Claude</option>
            </select>
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <label>Prompt / Goal</label>
            <textarea
              value={prompt}
              onChange={e => setPrompt(e.target.value)}
              placeholder={mode === 'single'
                ? "Enter your question or task..."
                : "Enter your high-level goal..."}
              rows={6}
              required
            />
          </div>

          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? '⏳ Processing...' : '🚀 Run Agent'}
          </button>
        </div>
      </form>

      {error && (
        <div className="error">
          <strong>Error:</strong> {error}
        </div>
      )}

      {result && (
        <div className="card">
          <h3 style={{ marginBottom: '1rem' }}>📝 Results</h3>

          {mode === 'single' ? (
            <>
              <div style={{ marginBottom: '1rem' }}>
                <span className="badge badge-blue">{result.model.toUpperCase()}</span>
                {result.escalated && (
                  <span className="badge badge-yellow" style={{ marginLeft: '0.5rem' }}>
                    Escalated to Claude
                  </span>
                )}
              </div>
              <pre>{result.result}</pre>
            </>
          ) : (
            <>
              <div style={{ marginBottom: '1.5rem' }}>
                <h4 style={{ marginBottom: '0.5rem' }}>1️⃣ Plan</h4>
                <pre>{result.plan}</pre>
              </div>
              <div style={{ marginBottom: '1.5rem' }}>
                <h4 style={{ marginBottom: '0.5rem' }}>2️⃣ Execution</h4>
                <pre>{result.execution}</pre>
              </div>
              <div style={{ marginBottom: '1.5rem' }}>
                <h4 style={{ marginBottom: '0.5rem' }}>3️⃣ Critique & Final</h4>
                <pre>{result.critique}</pre>
              </div>
            </>
          )}

          <div style={{ marginTop: '1.5rem', fontSize: '0.9rem', color: '#9ca3af' }}>
            💰 Budget: ${result.budget.spent.toFixed(2)} / ${result.budget.limit.toFixed(2)}
            ({((result.budget.spent / result.budget.limit) * 100).toFixed(1)}%)
          </div>
        </div>
      )}
    </div>
  );
}
