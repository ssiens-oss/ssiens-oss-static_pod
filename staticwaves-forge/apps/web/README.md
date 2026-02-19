# StaticWaves Forge - Web UI

Beautiful, production-ready Next.js interface for 3D asset generation.

---

## ✨ Features

### Pages

- **Home** (`/`) - Landing page with hero section and features
- **Generate** (`/generate`) - Interactive 3D asset generator with viewport
- **Library** (`/library`) - Browse and manage generated assets
- **Dashboard** (`/dashboard`) - Overview of activity and stats
- **Packs** (`/packs`) - Create and manage asset packs
- **Settings** (`/settings`) - Configure preferences and API keys

### Components

- **Navigation** - Global navigation with responsive mobile menu
- **PromptPanel** - Interactive asset configuration controls
- **Viewport3D** - Real-time 3D preview with Three.js
- **JobStatus** - Live job progress tracking
- **ExportPanel** - Multi-format export controls

---

## 🚀 Quick Start

### Install Dependencies

```bash
npm install
```

### Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### Build for Production

```bash
npm run build
npm start
```

---

## 🎨 Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS
- **3D**: React Three Fiber + Three.js + Drei
- **State**: Zustand (optional)
- **HTTP**: Axios
- **TypeScript**: Full type safety

---

## 📁 Project Structure

```
apps/web/
├── app/
│   ├── page.tsx                 # Home page
│   ├── generate/page.tsx        # Asset generator
│   ├── library/page.tsx         # Asset library
│   ├── dashboard/page.tsx       # Dashboard
│   ├── packs/page.tsx           # Pack manager
│   ├── settings/page.tsx        # Settings
│   ├── layout.tsx               # Root layout
│   └── globals.css              # Global styles
│
├── components/
│   ├── Navigation.tsx           # Global nav
│   ├── PromptPanel.tsx          # Generation controls
│   ├── Viewport3D.tsx           # 3D viewer
│   ├── JobStatus.tsx            # Job tracking
│   └── ExportPanel.tsx          # Export options
│
├── lib/
│   └── api.ts                   # API client
│
└── public/
    └── ...                      # Static assets
```

---

## 🔧 Configuration

### Environment Variables

Create `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### API Integration

The UI connects to the FastAPI backend:

```typescript
// lib/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Generate asset
await axios.post(`${API_URL}/api/generate/`, {...})

// Check status
await axios.get(`${API_URL}/api/jobs/{job_id}`)
```

---

## 🎨 Customization

### Colors

Edit `tailwind.config.js`:

```javascript
theme: {
  extend: {
    colors: {
      forge: {
        dark: '#0a0a0a',
        accent: '#3b82f6',
        // ...
      }
    }
  }
}
```

### Fonts

Update `app/layout.tsx`:

```typescript
import { YourFont } from 'next/font/google'

const yourFont = YourFont({ subsets: ['latin'] })
```

---

## 📱 Responsive Design

All pages are fully responsive:

- **Mobile**: Single column, collapsible nav
- **Tablet**: 2-column grid layouts
- **Desktop**: Full feature set with 3D viewport

---

## 🔌 API Integration

### Generate Asset

```typescript
const response = await axios.post('/api/generate/', {
  prompt: "A low-poly sword",
  asset_type: "weapon",
  style: "low-poly",
  poly_budget: 5000
})

const jobId = response.data.job_id
```

### Track Progress

```typescript
const status = await axios.get(`/api/jobs/${jobId}`)

console.log(status.data.progress) // 0.0 - 1.0
console.log(status.data.status)   // 'queued' | 'processing' | 'completed'
```

---

## 🎮 3D Viewport

The Viewport3D component uses React Three Fiber:

```typescript
<Canvas>
  <OrbitControls />
  <Environment preset="studio" />
  <Grid />
  {modelPath && <Model path={modelPath} />}
</Canvas>
```

Features:
- Real-time 3D preview
- Orbit controls (drag to rotate)
- Auto-rotation
- Environment lighting
- Grid helper

---

## 🚀 Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Docker

```bash
# Build
docker build -t forge-web -f Dockerfile.web .

# Run
docker run -p 3000:3000 forge-web
```

### Manual

```bash
npm run build
npm start
```

---

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or use different port
npm run dev -- -p 3001
```

### API Connection Failed

Check `NEXT_PUBLIC_API_URL` in `.env.local`

```bash
# Test API
curl http://localhost:8000/health
```

### Build Errors

```bash
# Clear cache
rm -rf .next

# Reinstall
rm -rf node_modules
npm install
```

---

## 📚 Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [React Three Fiber](https://docs.pmnd.rs/react-three-fiber)
- [Tailwind CSS](https://tailwindcss.com/docs)

---

## ✅ Checklist

Before deploying:

- [ ] Configure `NEXT_PUBLIC_API_URL`
- [ ] Test all pages load
- [ ] Test API integration
- [ ] Verify 3D viewport works
- [ ] Test on mobile devices
- [ ] Run `npm run build` successfully

---

**The StaticWaves Forge web UI is ready for production!** 🚀
