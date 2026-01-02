/**
 * pgvector-backed semantic memory
 * Stores embeddings for similarity search
 */

const { Client } = require("pg");

class VectorStore {
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

      // Create tables if they don't exist
      await this.client.query(`
        CREATE TABLE IF NOT EXISTS memories (
          id BIGSERIAL PRIMARY KEY,
          scope TEXT,
          role TEXT,
          content TEXT,
          embedding VECTOR(1536),
          ts TIMESTAMP DEFAULT NOW()
        );
        CREATE INDEX IF NOT EXISTS idx_memories_embedding ON memories USING ivfflat (embedding vector_cosine_ops);
      `);
    } catch (err) {
      console.warn("pgvector unavailable:", err.message);
      this.connected = false;
    }
  }

  async store({ scope, role, content, embedding }) {
    if (!this.connected) await this.connect();
    if (!this.connected) return;

    await this.client.query(
      `INSERT INTO memories (scope, role, content, embedding)
       VALUES ($1, $2, $3, $4)`,
      [scope, role, content, `[${embedding.join(',')}]`]
    );
  }

  async search(embedding, limit = 5, scope = null) {
    if (!this.connected) await this.connect();
    if (!this.connected) return [];

    const query = scope
      ? `SELECT content, role, scope, ts,
               1 - (embedding <=> $1) as similarity
         FROM memories
         WHERE scope = $2
         ORDER BY embedding <=> $1
         LIMIT $3`
      : `SELECT content, role, scope, ts,
               1 - (embedding <=> $1) as similarity
         FROM memories
         ORDER BY embedding <=> $1
         LIMIT $2`;

    const params = scope
      ? [`[${embedding.join(',')}]`, scope, limit]
      : [`[${embedding.join(',')}]`, limit];

    const result = await this.client.query(query, params);
    return result.rows;
  }

  async close() {
    if (this.connected) {
      await this.client.end();
      this.connected = false;
    }
  }
}

module.exports = new VectorStore();
