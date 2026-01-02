'use client';

import { useState, useEffect } from 'react';
import { getBudget, getHealth, type Budget } from '@/lib/api';

export default function Dashboard() {
  const [budget, setBudget] = useState<Budget | null>(null);
  const [health, setHealth] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [budgetData, healthData] = await Promise.all([
          getBudget(),
          getHealth()
        ]);
        setBudget(budgetData);
        setHealth(healthData);
      } catch (e) {
        console.error('Failed to load dashboard:', e);
      } finally {
        setLoading(false);
      }
    }

    load();
    const interval = setInterval(load, 10000); // Refresh every 10s
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <div className="container loading">Loading dashboard...</div>;
  }

  const budgetPercent = budget ? (budget.spent / budget.limit) * 100 : 0;
  const budgetColor = budgetPercent > 80 ? 'red' : budgetPercent > 50 ? 'yellow' : 'green';

  return (
    <div className="container">
      <h1 style={{ marginBottom: '2rem' }}>AI Control Panel</h1>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
        <div className="card">
          <h3 style={{ marginBottom: '1rem' }}>💰 Budget</h3>
          {budget && (
            <>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
                ${budget.spent.toFixed(2)} / ${budget.limit.toFixed(2)}
              </div>
              <div style={{ background: '#333', borderRadius: '8px', height: '12px', overflow: 'hidden' }}>
                <div style={{
                  width: `${budgetPercent}%`,
                  height: '100%',
                  background: budgetColor === 'red' ? '#ef4444' : budgetColor === 'yellow' ? '#f59e0b' : '#10b981',
                  transition: 'width 0.3s'
                }} />
              </div>
              <div style={{ marginTop: '0.5rem', fontSize: '0.9rem', color: '#9ca3af' }}>
                ${budget.remaining.toFixed(2)} remaining ({(100 - budgetPercent).toFixed(1)}%)
              </div>
            </>
          )}
        </div>

        <div className="card">
          <h3 style={{ marginBottom: '1rem' }}>🤖 Agent Status</h3>
          {health && (
            <>
              <div style={{ marginBottom: '1rem' }}>
                <span className={`badge badge-${health.status === 'ok' ? 'green' : 'red'}`}>
                  {health.status === 'ok' ? '✓ Online' : '✗ Offline'}
                </span>
              </div>
              <div style={{ fontSize: '0.9rem', color: '#9ca3af' }}>
                {health.roles?.length || 0} specialized roles active
              </div>
            </>
          )}
        </div>

        <div className="card">
          <h3 style={{ marginBottom: '1rem' }}>🎯 Active Roles</h3>
          {health?.roles && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {health.roles.map((role: string) => (
                <div key={role} style={{ fontSize: '0.9rem' }}>
                  <code>{role.replace('_AGENT', '')}</code>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="card" style={{ marginTop: '2rem' }}>
        <h3 style={{ marginBottom: '1rem' }}>🚀 Quick Actions</h3>
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
          <a href="/agents">
            <button className="btn btn-primary">Launch Agent</button>
          </a>
          <a href="/memory">
            <button className="btn btn-secondary">View Memory</button>
          </a>
          <a href="/episodes">
            <button className="btn btn-secondary">Review Decisions</button>
          </a>
        </div>
      </div>

      <div className="card">
        <h3 style={{ marginBottom: '1rem' }}>📖 Quick Start</h3>
        <ol style={{ paddingLeft: '1.5rem', lineHeight: 2 }}>
          <li>Choose a specialized agent role</li>
          <li>Enter your prompt or goal</li>
          <li>Select single/multi-agent mode</li>
          <li>Review output and budget usage</li>
        </ol>
      </div>
    </div>
  );
}
