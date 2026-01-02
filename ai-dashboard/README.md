# AI Dashboard

Web interface for StaticWaves AI Agent control.

## Quick Start

```bash
npm install
npm run dev
```

Open http://localhost:3001

## Features

### Dashboard
- Real-time budget tracking
- Agent status monitoring
- Quick action buttons

### Agents
- Launch single/multi-agent tasks
- Choose specialized roles
- Stream results in real-time

### Memory
- Browse stored memories by scope
- View history
- Search functionality

### Episodes
- Review critical decisions
- Track outcomes
- Risk analysis

## Configuration

Dashboard connects to:
- AI Agent: http://localhost:8787
- WebSocket: ws://localhost:8788

Change in `lib/api.ts` or use env vars:

```bash
NEXT_PUBLIC_AI_AGENT_URL=http://localhost:8787
NEXT_PUBLIC_WS_URL=ws://localhost:8788
```

## Production Build

```bash
npm run build
npm start
```

Runs on http://localhost:3001

## Tech Stack

- Next.js 14 (App Router)
- TypeScript
- No external UI libraries (custom CSS)
- WebSocket for streaming
