'use client';

import { useState, useEffect } from 'react';
import { getEpisodes, type Episode } from '@/lib/api';

export default function Episodes() {
  const [episodes, setEpisodes] = useState<Episode[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await getEpisodes();
        setEpisodes(data.episodes || []);
      } catch (e) {
        console.error('Failed to load episodes:', e);
      } finally {
        setLoading(false);
      }
    }

    load();
  }, []);

  if (loading) {
    return <div className="container loading">Loading episodes...</div>;
  }

  const getRiskBadge = (risk: string) => {
    const colors: Record<string, string> = {
      low: 'green',
      medium: 'yellow',
      high: 'red'
    };
    return `badge-${colors[risk] || 'blue'}`;
  };

  return (
    <div className="container">
      <h1 style={{ marginBottom: '2rem' }}>📜 Episodic Memory</h1>

      <div className="card" style={{ marginBottom: '2rem' }}>
        <p style={{ color: '#9ca3af' }}>
          Episodic memory stores critical decisions, not raw conversations.
          This allows the AI to learn from past outcomes and apply that knowledge to new situations.
        </p>
      </div>

      {episodes.length === 0 ? (
        <div className="card">
          <div style={{ textAlign: 'center', padding: '2rem', color: '#9ca3af' }}>
            No episodes recorded yet. Episodes are created when the AI makes significant decisions.
          </div>
        </div>
      ) : (
        episodes.map((ep, i) => (
          <div key={i} className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1rem' }}>
              <h3 style={{ margin: 0 }}>{ep.event}</h3>
              <div>
                <span className={`badge ${getRiskBadge(ep.risk_level)}`}>
                  {ep.risk_level?.toUpperCase() || 'UNKNOWN'}
                </span>
                <div style={{ fontSize: '0.8rem', color: '#9ca3af', marginTop: '0.25rem', textAlign: 'right' }}>
                  {new Date(ep.ts).toLocaleString()}
                </div>
              </div>
            </div>

            {ep.context && (
              <div style={{ marginBottom: '1rem' }}>
                <strong style={{ fontSize: '0.9rem', color: '#9ca3af' }}>Context:</strong>
                <div style={{ marginTop: '0.25rem' }}>{ep.context}</div>
              </div>
            )}

            {ep.resolution && (
              <div style={{ marginBottom: '1rem' }}>
                <strong style={{ fontSize: '0.9rem', color: '#9ca3af' }}>Resolution:</strong>
                <div style={{ marginTop: '0.25rem' }}>{ep.resolution}</div>
              </div>
            )}

            {ep.outcome && (
              <div>
                <strong style={{ fontSize: '0.9rem', color: '#9ca3af' }}>Outcome:</strong>
                <div style={{ marginTop: '0.25rem', color: '#10b981' }}>{ep.outcome}</div>
              </div>
            )}
          </div>
        ))
      )}
    </div>
  );
}
