'use client';

import { useState } from 'react';

export default function Memory() {
  const [scope, setScope] = useState('');
  const [memory, setMemory] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function loadMemory() {
    if (!scope) return;

    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8787/memory?scope=${encodeURIComponent(scope)}`);
      const data = await res.json();
      setMemory(data);
    } catch (e) {
      console.error('Failed to load memory:', e);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container">
      <h1 style={{ marginBottom: '2rem' }}>🧠 Memory Browser</h1>

      <div className="card">
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
          <input
            type="text"
            value={scope}
            onChange={e => setScope(e.target.value)}
            placeholder="Enter memory scope (e.g., printify, tiktok, compliance)"
            style={{ flex: 1 }}
          />
          <button onClick={loadMemory} className="btn btn-primary" disabled={loading}>
            {loading ? '⏳ Loading...' : '🔍 Search'}
          </button>
        </div>

        <div style={{ fontSize: '0.9rem', color: '#9ca3af' }}>
          Common scopes: printify, tiktok, ads, compliance, architecture
        </div>
      </div>

      {memory && (
        <>
          {memory.value && (
            <div className="card">
              <h3 style={{ marginBottom: '1rem' }}>📌 Latest Memory</h3>
              <pre>{typeof memory.value === 'string' ? memory.value : JSON.stringify(memory.value, null, 2)}</pre>
            </div>
          )}

          {memory.history && memory.history.length > 0 && (
            <div className="card">
              <h3 style={{ marginBottom: '1rem' }}>📚 History</h3>
              {memory.history.map((item: any, i: number) => (
                <div key={i} style={{ marginBottom: '1.5rem', paddingBottom: '1.5rem', borderBottom: '1px solid #333' }}>
                  <div style={{ fontSize: '0.9rem', color: '#9ca3af', marginBottom: '0.5rem' }}>
                    {new Date(item.timestamp).toLocaleString()}
                  </div>
                  <pre>{typeof item.value === 'string' ? item.value : JSON.stringify(item.value, null, 2)}</pre>
                </div>
              ))}
            </div>
          )}

          {!memory.value && (!memory.history || memory.history.length === 0) && (
            <div className="card">
              <div style={{ textAlign: 'center', padding: '2rem', color: '#9ca3af' }}>
                No memory found for scope "{scope}"
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
