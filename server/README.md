# StaticWaves POD API Server

Backend API service for the StaticWaves Print-on-Demand Studio application.

## Features

- RESTful API endpoints for design generation
- Provider integration endpoints
- Blueprint and provider management
- CORS enabled for frontend integration

## Endpoints

### Health Check
```
GET /api/health
```

### Get Providers
```
GET /api/providers
```

### Get Blueprints
```
GET /api/blueprints
```

### Generate Design
```
POST /api/design/generate
Content-Type: application/json

{
  "prompt": "Abstract art design",
  "dropName": "Drop7",
  "blueprintId": 6,
  "style": "modern"
}
```

### Upload to Provider
```
POST /api/provider/upload
Content-Type: application/json

{
  "designUrl": "https://...",
  "mockupUrl": "https://...",
  "dropName": "Drop7",
  "providerId": 1,
  "blueprintId": 6
}
```

## Setup

1. Install dependencies:
```bash
cd server
npm install
```

2. Run development server:
```bash
npm run dev
```

3. Build for production:
```bash
npm run build
npm start
```

## Configuration

The server runs on port 3001 by default. Set `PORT` environment variable to change:

```bash
PORT=3002 npm run dev
```

## Integration

The frontend is pre-configured to connect to this API at `http://localhost:3001/api`.

Update the `.env` file in the frontend to point to a different API endpoint if needed.
