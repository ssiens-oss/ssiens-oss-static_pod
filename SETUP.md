# StaticWaves AI Platform Setup

## Prerequisites Checklist

- [ ] Node.js 20+ installed
- [ ] OpenAI API key
- [ ] Anthropic API key
- [ ] (Optional) Redis installed
- [ ] (Optional) PostgreSQL with pgvector

## Step-by-Step Setup

### 1. Clone and Navigate
```bash
cd /path/to/ssiens-oss-static_pod
```

### 2. Set API Keys
```bash
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
export AI_BUDGET_DAILY_USD=10
```

Add to `~/.bashrc` or `~/.zshrc` for persistence.

### 3. Install AI Agent
```bash
cd ai-agent
npm install
```

### 4. Install Dashboard
```bash
cd ../ai-dashboard
npm install
```

### 5. (Optional) Setup PostgreSQL + pgvector

```bash
# Install
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres psql
CREATE DATABASE ai_memory;
\c ai_memory
CREATE EXTENSION vector;
\q

# Set credentials
export PGHOST=localhost
export PGDATABASE=ai_memory
export PGUSER=postgres
export PGPASSWORD=yourpassword
```

### 6. (Optional) Setup Redis

```bash
# Install
sudo apt-get install redis-server

# Start
sudo systemctl start redis

# Test
redis-cli ping
# Should return: PONG

# Set URL
export REDIS_URL=redis://localhost:6379
```

### 7. Start Services

**Terminal 1: AI Agent**
```bash
cd ai-agent
npm start
```

**Terminal 2: WebSocket Server**
```bash
cd ai-agent
npm run ws
```

**Terminal 3: Dashboard**
```bash
cd ai-dashboard
npm run dev
```

### 8. Verify Installation

```bash
# Health check
curl http://localhost:8787/health

# Should return:
# {"status":"ok","budget":{...},"roles":[...]}
```

### 9. Access Dashboard

Open browser: http://localhost:3001

### 10. Setup GitHub Actions

1. Go to repo Settings → Secrets → Actions
2. Add secrets:
   - `OPENAI_API_KEY`
   - `ANTHROPIC_API_KEY`
3. Push changes to trigger workflows

### 11. Test Local Scripts

```bash
# Test code review
node scripts/claude-review.js scripts/

# Test GPT↔Claude bridge
node scripts/ai-bridge.js arbiter "What is the best database for AI memory?"
```

## Verification Tests

### Test 1: Single Agent
```bash
curl -X POST http://localhost:8787/run \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Say hello"}'
```

### Test 2: Multi-Agent
```bash
curl -X POST http://localhost:8787/multi \
  -H "Content-Type: application/json" \
  -d '{"goal": "Explain multi-agent architecture"}'
```

### Test 3: Role-Based
```bash
curl -X POST http://localhost:8787/run \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Review Printify integration", "role": "POD_AGENT"}'
```

### Test 4: Budget Check
```bash
curl http://localhost:8787/budget
```

## Production Deployment

### Run as Daemon

```bash
# AI Agent
cd ai-agent
nohup npm start > agent.log 2>&1 &

# WebSocket
nohup npm run ws > ws.log 2>&1 &

# Dashboard (build first)
cd ../ai-dashboard
npm run build
nohup npm start > dashboard.log 2>&1 &
```

### Setup systemd (Linux)

Create `/etc/systemd/system/ai-agent.service`:

```ini
[Unit]
Description=StaticWaves AI Agent
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/ssiens-oss-static_pod/ai-agent
Environment="OPENAI_API_KEY=sk-..."
Environment="ANTHROPIC_API_KEY=sk-ant-..."
Environment="AI_BUDGET_DAILY_USD=10"
ExecStart=/usr/bin/npm start
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable ai-agent
sudo systemctl start ai-agent
sudo systemctl status ai-agent
```

## Troubleshooting

### Agent won't start
- Check API keys: `echo $ANTHROPIC_API_KEY`
- Check port 8787: `lsof -i :8787`
- View logs: `cat ai-agent/agent.log`

### Dashboard won't load
- Check agent is running: `curl http://localhost:8787/health`
- Check port 3001: `lsof -i :3001`
- Clear Next.js cache: `rm -rf ai-dashboard/.next`

### Budget exceeded
- Check spend: `curl http://localhost:8787/budget`
- Restart agent to reset (dev only)
- Increase limit: `export AI_BUDGET_DAILY_USD=20`

### PostgreSQL errors
- pgvector is optional
- Agent continues with SQLite if unavailable
- Check connection: `psql -h localhost -U postgres -d ai_memory`

### Redis errors
- Redis is optional
- Agent continues with SQLite if unavailable
- Check connection: `redis-cli ping`

## Security Checklist

- [ ] API keys in environment only (never committed)
- [ ] `.gitignore` includes `.env` files
- [ ] GitHub secrets configured
- [ ] Budget limits set
- [ ] PostgreSQL password changed from default
- [ ] Redis protected (if exposed)
- [ ] CORS configured for production domains

## Next Steps

1. ✅ Review README.md for full documentation
2. ✅ Test local code review: `node scripts/claude-review.js`
3. ✅ Explore dashboard: http://localhost:3001
4. ✅ Try different agent roles
5. ✅ Make a test PR to trigger GitHub Actions
6. ✅ Integrate API calls from your backend

## Getting Help

- Check logs: `ai-agent/agent.log`, `ai-agent/ws.log`
- Health check: `curl http://localhost:8787/health`
- Budget status: `curl http://localhost:8787/budget`
- Review episodes: `curl http://localhost:8787/episodes`

---

Setup complete! 🎉
