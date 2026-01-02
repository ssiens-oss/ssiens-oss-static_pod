/**
 * Episodic memory system
 * Stores decisions, not chat logs
 */

const { Client } = require("pg");

class EpisodicMemory {
  constructor() {
    this.client = new Client({
      host: process.env.PGHOST || "localhost",
      database: process.env.PGDATABASE || "ai_memory",
      user: process.env.PGUSER || "postgres",
      password: process.env.PGPASSWORD,
      port: process.env.PGPORT || 5432
    });
    this.connected = false;
  }

  async connect() {
    if (this.connected) return;
    try {
      await this.client.connect();
      this.connected = true;

      await this.client.query(`
        CREATE TABLE IF NOT EXISTS episodes (
          id BIGSERIAL PRIMARY KEY,
          event TEXT NOT NULL,
          context TEXT,
          resolution TEXT,
          outcome TEXT,
          risk_level TEXT,
          embedding VECTOR(1536),
          ts TIMESTAMP DEFAULT NOW()
        );
        CREATE INDEX IF NOT EXISTS idx_episodes_embedding ON episodes USING ivfflat (embedding vector_cosine_ops);
        CREATE INDEX IF NOT EXISTS idx_episodes_ts ON episodes(ts DESC);
      `);
    } catch (err) {
      console.warn("Episodic memory unavailable:", err.message);
      this.connected = false;
    }
  }

  async recordEpisode({ event, context, resolution, outcome, riskLevel, embedding }) {
    if (!this.connected) await this.connect();
    if (!this.connected) return;

    await this.client.query(
      `INSERT INTO episodes (event, context, resolution, outcome, risk_level, embedding)
       VALUES ($1, $2, $3, $4, $5, $6)`,
      [event, context, resolution, outcome, riskLevel, `[${embedding.join(',')}]`]
    );
  }

  async recallSimilar(embedding, limit = 3) {
    if (!this.connected) await this.connect();
    if (!this.connected) return [];

    const result = await this.client.query(
      `SELECT event, context, resolution, outcome, risk_level, ts,
              1 - (embedding <=> $1) as similarity
       FROM episodes
       ORDER BY embedding <=> $1
       LIMIT $2`,
      [`[${embedding.join(',')}]`, limit]
    );

    return result.rows;
  }

  async recentEpisodes(limit = 10) {
    if (!this.connected) await this.connect();
    if (!this.connected) return [];

    const result = await this.client.query(
      `SELECT event, context, resolution, outcome, risk_level, ts
       FROM episodes
       ORDER BY ts DESC
       LIMIT $1`,
      [limit]
    );

    return result.rows;
  }

  async close() {
    if (this.connected) {
      await this.client.end();
      this.connected = false;
    }
  }
}

module.exports = new EpisodicMemory();
