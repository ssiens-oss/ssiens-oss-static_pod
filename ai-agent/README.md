# AI Agent Quick Setup

## 1. Install Dependencies

```bash
cd ai-agent
npm install
```

## 2. Set Environment Variables

Create `.env` file:

```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
AI_BUDGET_DAILY_USD=10

# Optional
REDIS_URL=redis://localhost:6379
PGHOST=localhost
PGDATABASE=ai_memory
PGUSER=postgres
PGPASSWORD=yourpassword
```

Or export directly:

```bash
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
```

## 3. Start Agent

```bash
npm start
```

Agent runs on http://localhost:8787

## 4. Test It

```bash
curl http://localhost:8787/health
```

## 5. Start WebSocket Server (Optional)

```bash
# In another terminal
npm run ws
```

WebSocket runs on ws://localhost:8788

## API Endpoints

- `POST /run` - Single agent
- `POST /multi` - Multi-agent
- `POST /chain` - Task chain
- `GET /memory?scope=X` - Recall memory
- `GET /episodes` - Decision history
- `GET /budget` - Current spend
- `GET /health` - Status

## Example Request

```bash
curl -X POST http://localhost:8787/run \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Review this code for bugs",
    "role": "CI_AGENT"
  }'
```

## Agent Roles

- `POD_AGENT` - Print-on-Demand ops
- `ADS_AGENT` - TikTok Ads
- `COMPLIANCE_AGENT` - Risk & policy
- `ARCH_AGENT` - Architecture
- `CI_AGENT` - Code review

Leave blank for general purpose.
