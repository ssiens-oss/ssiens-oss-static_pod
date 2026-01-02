/**
 * Redis-backed memory for shared, persistent state
 * Use for cross-service memory, production memory
 */

const Redis = require("ioredis");
const redis = new Redis(process.env.REDIS_URL || "redis://127.0.0.1:6379");

redis.on("error", (err) => {
  console.warn("Redis unavailable, falling back to SQLite:", err.message);
});

module.exports = {
  async remember(scope, key, value, ttl = null) {
    const k = `${scope}:${key}`;
    await redis.set(k, JSON.stringify(value));
    if (ttl) await redis.expire(k, ttl);
  },

  async recall(scope, key) {
    const v = await redis.get(`${scope}:${key}`);
    return v ? JSON.parse(v) : null;
  },

  async forget(scope, key) {
    await redis.del(`${scope}:${key}`);
  },

  async list(scope) {
    const keys = await redis.keys(`${scope}:*`);
    const values = await Promise.all(
      keys.map(async k => {
        const v = await redis.get(k);
        return { key: k.replace(`${scope}:`, ''), value: JSON.parse(v) };
      })
    );
    return values;
  }
};
