/**
 * SQLite-backed memory for quick local storage
 * Use for session memory, temp state
 */

const Database = require("better-sqlite3");
const db = new Database("agent.db");

db.exec(`
  CREATE TABLE IF NOT EXISTS memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scope TEXT,
    key TEXT,
    value TEXT,
    ts INTEGER
  );
  CREATE INDEX IF NOT EXISTS idx_scope_key ON memory(scope, key);
`);

module.exports = {
  remember(scope, key, value) {
    db.prepare(
      "INSERT INTO memory (scope,key,value,ts) VALUES (?,?,?,?)"
    ).run(scope, key, JSON.stringify(value), Date.now());
  },

  recall(scope, key) {
    const row = db.prepare(
      "SELECT value FROM memory WHERE scope=? AND key=? ORDER BY ts DESC LIMIT 1"
    ).get(scope, key);
    return row ? JSON.parse(row.value) : null;
  },

  history(scope, limit = 10) {
    const rows = db.prepare(
      "SELECT key, value, ts FROM memory WHERE scope=? ORDER BY ts DESC LIMIT ?"
    ).all(scope, limit);
    return rows.map(r => ({
      key: r.key,
      value: JSON.parse(r.value),
      timestamp: r.ts
    }));
  }
};
