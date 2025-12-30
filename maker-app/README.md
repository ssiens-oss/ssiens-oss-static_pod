# StaticWaves Maker - AI Content Creation Platform

**Complete production-ready system for AI-powered image, video, music, and book generation with monetization built-in.**

---

## 🎯 Overview

StaticWaves Maker is a multi-platform content creation app that generates:
- **Images** (AI art, thumbnails, designs)
- **Videos** (TikTok clips, animations, promos)
- **Music** (lo-fi, ambient, background tracks)
- **Books** (ebooks, PDFs, EPUBs)

**Platforms:**
- 🌐 Web App (PWA)
- 📱 Android APK (Google Play)
- 🍎 iOS App (App Store)

**Monetization:**
- 💰 Subscriptions ($19-$99/mo)
- 🪙 Token packs (pay-per-use)
- 📺 Rewarded ads (earn free tokens)

---

## 📦 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Mobile Apps                             │
│         (React PWA + Capacitor → APK/iOS)                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                  FastAPI Backend                             │
│  - Token enforcement                                         │
│  - Stripe billing                                           │
│  - Generation job queue                                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                  Background Worker                           │
│  - Processes generation jobs                                 │
│  - Autoscaling based on queue size                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              Generation Services                             │
│  - Image: ComfyUI / SDXL (RunPod)                           │
│  - Video: Diffusion / ffmpeg                                │
│  - Music: Riffusion / MusicGen                              │
│  - Book: Claude → PDF/EPUB                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Docker (optional)

### 1. Backend Setup

```bash
cd maker-app/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Initialize database
python -c "from app.database import init_db; init_db()"

# Run API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run worker (in separate terminal)
python worker/worker.py
```

**API will be available at:** http://localhost:8000

**API docs:** http://localhost:8000/docs

### 2. Frontend Setup (Next.js PWA)

```bash
cd maker-app/frontend

# Install dependencies
npm install

# Set up environment
cp .env.example .env.local
# Edit with your backend URL

# Run development server
npm run dev
```

**App will be available at:** http://localhost:3000

### 3. Mobile Build (APK)

```bash
cd maker-app/frontend

# Build production PWA
npm run build

# Initialize Capacitor
npx cap init

# Add Android platform
npx cap add android

# Copy web assets
npx cap copy

# Open Android Studio
npx cap open android

# Build APK in Android Studio
```

---

## 💰 Monetization Setup

### Stripe Configuration

1. Create Stripe account: https://dashboard.stripe.com
2. Create products and prices:

```
Creator Tier:  $19/mo → 300 tokens/month
Studio Tier:   $49/mo → 800 tokens/month
Pro Tier:      $99/mo → 2000 tokens/month

Token Pack 100:   $10
Token Pack 300:   $25
Token Pack 1000:  $75
```

3. Copy price IDs to `.env`:

```env
STRIPE_PRICE_CREATOR=price_xxxxx
STRIPE_PRICE_STUDIO=price_xxxxx
STRIPE_PRICE_PRO=price_xxxxx
```

4. Set up webhook endpoint:
   - URL: `https://yourapi.com/billing/webhook`
   - Events: `checkout.session.completed`, `invoice.paid`, `customer.subscription.deleted`

### AdMob Integration (Mobile)

1. Create AdMob account: https://admob.google.com
2. Create app and ad units:
   - Rewarded ad unit (for earning tokens)
3. Install Capacitor plugin:

```bash
npm install @capacitor-community/admob
```

4. Configure in `capacitor.config.ts`:

```typescript
admob: {
  appId: "ca-app-pub-xxxxx~xxxxx",
  testingDevices: ["xxxxx"]
}
```

5. Implement rewarded ads (see frontend implementation below)

---

## 🎨 Frontend Implementation

### Key Pages

#### `/pages/index.tsx` - Home/Dashboard

```typescript
import { useState } from 'react'
import { GenerationTabs } from '@/components/GenerationTabs'
import { TokenBalance } from '@/components/TokenBalance'

export default function Home() {
  return (
    <div className="container">
      <TokenBalance />
      <GenerationTabs />
    </div>
  )
}
```

#### `/pages/maker/image.tsx` - Image Generation

```typescript
import { useState } from 'react'
import axios from 'axios'

export default function ImageMaker() {
  const [prompt, setPrompt] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)

  const generate = async () => {
    setLoading(true)
    try {
      const { data } = await axios.post('/api/maker/generate/image', {
        prompt
      })

      // Poll for completion
      const jobId = data.job_id
      const interval = setInterval(async () => {
        const { data: job } = await axios.get(`/api/maker/job/${jobId}`)
        if (job.status === 'completed') {
          setResult(job.output_url)
          clearInterval(interval)
          setLoading(false)
        }
      }, 2000)

    } catch (error) {
      alert(error.response?.data?.detail || 'Generation failed')
      setLoading(false)
    }
  }

  return (
    <div className="maker-container">
      <h1>Generate Image</h1>

      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Describe your image..."
        rows={4}
      />

      <button onClick={generate} disabled={loading}>
        {loading ? 'Generating...' : 'Generate (1 token)'}
      </button>

      {result && (
        <div className="result">
          <img src={result} alt="Generated" />
          <button onClick={() => saveToLibrary(result)}>
            Save to Library
          </button>
        </div>
      )}
    </div>
  )
}
```

#### `/components/AdReward.tsx` - Rewarded Ad Component

```typescript
import { AdMob, RewardAdOptions } from '@capacitor-community/admob'
import axios from 'axios'

export function AdRewardButton() {
  const [available, setAvailable] = useState(true)

  const checkAvailability = async () => {
    const { data } = await axios.get('/api/rewards/ad-availability')
    setAvailable(data.available)
  }

  const watchAd = async () => {
    try {
      await AdMob.prepareRewardVideoAd({
        adId: 'ca-app-pub-xxxxx/rewarded'
      })

      await AdMob.showRewardVideoAd()

      // Reward tokens
      const { data } = await axios.post('/api/rewards/ad-complete', {
        ad_network: 'admob',
        ad_unit_id: 'ca-app-pub-xxxxx/rewarded'
      })

      alert(`Earned ${data.tokens_awarded} tokens!`)

    } catch (error) {
      console.error('Ad failed:', error)
    }
  }

  return (
    <button onClick={watchAd} disabled={!available}>
      {available ? '🎁 Watch Ad for 5 Tokens' : '✓ Daily Limit Reached'}
    </button>
  )
}
```

### PWA Configuration

#### `/public/manifest.json`

```json
{
  "name": "StaticWaves Maker",
  "short_name": "Maker",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#050507",
  "theme_color": "#7B2CFF",
  "icons": [
    {
      "src": "/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icon-512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any maskable"
    }
  ]
}
```

#### `/next.config.js`

```javascript
const withPWA = require('next-pwa')({
  dest: 'public',
  disable: process.env.NODE_ENV === 'development'
})

module.exports = withPWA({
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL
  }
})
```

---

## 📱 Mobile Configuration

### Capacitor Setup

#### `/capacitor.config.ts`

```typescript
import { CapacitorConfig } from '@capacitor/cli'

const config: CapacitorConfig = {
  appId: 'com.staticwaves.maker',
  appName: 'StaticWaves Maker',
  webDir: 'out',
  bundledWebRuntime: false,
  server: {
    androidScheme: 'https'
  },
  plugins: {
    AdMob: {
      appId: 'ca-app-pub-xxxxx~xxxxx',
      testingDevices: ['xxxxx']
    }
  }
}

export default config
```

### Build APK

```bash
# Build Next.js for static export
npm run build

# Copy to mobile
npx cap copy

# Open Android Studio
npx cap open android

# In Android Studio:
# 1. Build → Generate Signed Bundle/APK
# 2. Choose APK
# 3. Create keystore or use existing
# 4. Build release APK
```

### Publish to Google Play

1. Create developer account: https://play.google.com/console
2. Create new app
3. Upload APK
4. Complete store listing:
   - Screenshots
   - Description
   - Privacy policy
5. Submit for review

---

## 🔧 Generation Services Configuration

### Image Generation (ComfyUI)

**Option 1: Local ComfyUI**

```bash
# Clone ComfyUI
git clone https://github.com/comfyanonymous/ComfyUI
cd ComfyUI

# Install dependencies
pip install -r requirements.txt

# Download models (SDXL base)
# Place in models/checkpoints/

# Run server
python main.py --listen 0.0.0.0 --port 8188
```

**Option 2: RunPod with ComfyUI**

1. Go to https://www.runpod.io/
2. Deploy ComfyUI template
3. Copy Pod IP and ID
4. Add to `.env`:

```env
COMFYUI_URL=http://your-pod-ip:8188
RUNPOD_POD_ID=xxxxx
RUNPOD_API_KEY=xxxxx
```

### Video Generation

**Option 1: ffmpeg Motion Graphics (Fast)**

```bash
# Install ffmpeg
sudo apt install ffmpeg

# Enable in worker
```

**Option 2: AI Video (Advanced)**

```python
# Install text-to-video models
# pip install diffusers transformers

# Example: ModelScope text-to-video
from diffusers import DiffusionPipeline

pipe = DiffusionPipeline.from_pretrained(
    "damo-vilab/text-to-video-ms-1.7b",
    torch_dtype=torch.float16
)

video = pipe(prompt, num_frames=16).frames
```

### Music Generation

**Option 1: MusicGen (Facebook AudioCraft)**

```bash
# Install AudioCraft
pip install audiocraft

# Use in services/music.py (already implemented)
```

**Option 2: Riffusion API**

```bash
# Use Riffusion endpoint
# Implement in services/music.py
```

### Book Generation

Uses Claude API (already implemented):
- Generates structured content
- Exports to PDF (ReportLab)
- Exports to EPUB (ebooklib)

---

## 🚀 Deployment

### Docker Compose (Full Stack)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: maker_app
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/maker_app
      STRIPE_SECRET_KEY: ${STRIPE_SECRET_KEY}
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
    ports:
      - "8000:8000"
    depends_on:
      - postgres

  worker:
    build: ./backend
    command: python worker/worker.py
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/maker_app
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
    depends_on:
      - postgres
      - backend

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://backend:8000

volumes:
  postgres_data:
```

**Run:**

```bash
docker-compose up -d
```

### Deploy to Cloud

**Backend (Railway/Render/Fly.io)**

```bash
# Example: Railway
railway init
railway link
railway up

# Set environment variables in dashboard
```

**Frontend (Vercel/Netlify)**

```bash
# Example: Vercel
vercel init
vercel --prod

# Set NEXT_PUBLIC_API_URL in dashboard
```

---

## 💳 Pricing Tiers

| Tier | Price | Tokens/Month | Ads | Features |
|------|-------|--------------|-----|----------|
| **Free** | $0 | 10/day | Yes | Basic generation |
| **Creator** | $19 | 300 | No | No ads, priority queue |
| **Studio** | $49 | 800 | No | Advanced styles, faster |
| **Pro** | $99 | 2000 | No | Unlimited*, API access |

**Token Costs:**
- Image: 1 token
- Music: 2 tokens
- Video: 5 tokens
- Book: 15 tokens

**Token Packs (One-time):**
- $10 → 100 tokens
- $25 → 300 tokens
- $75 → 1000 tokens

---

## 📊 Revenue Projections

**Conservative (Month 3):**
- 5,000 free users (ad revenue: ~$500/mo)
- 500 paying users (avg $29/mo: $14,500/mo)
- Token pack sales: $2,000/mo
- **Total: ~$17,000 MRR**

**Growth (Month 12):**
- 50,000 free users (ad revenue: ~$5,000/mo)
- 2,500 paying users ($72,500/mo)
- Token pack sales: $10,000/mo
- **Total: ~$87,500 MRR**

---

## 🛠️ Development

### API Endpoints

**Generation:**
- `POST /maker/generate/image` - Generate image (1 token)
- `POST /maker/generate/video` - Generate video (5 tokens)
- `POST /maker/generate/music` - Generate music (2 tokens)
- `POST /maker/generate/book` - Generate book (15 tokens)
- `GET /maker/job/{id}` - Check job status
- `GET /maker/queue` - Get user's job queue

**Billing:**
- `POST /billing/subscribe` - Create subscription
- `POST /billing/buy-tokens` - Purchase token pack
- `POST /billing/webhook` - Stripe webhook
- `GET /billing/subscription` - Get current subscription

**Rewards:**
- `POST /rewards/ad-complete` - Claim ad reward (5 tokens)
- `GET /rewards/balance` - Get token balance
- `GET /rewards/ad-availability` - Check ad limits

**Library:**
- `GET /library/` - Get saved creations
- `POST /library/save` - Save to library
- `POST /library/{id}/favorite` - Toggle favorite
- `DELETE /library/{id}` - Delete from library

### Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# E2E tests
npm run test:e2e
```

---

## 🔒 Security

- All API endpoints require authentication
- Token balance validated server-side
- Stripe webhook signature verification
- Rate limiting on ad rewards (10/day)
- Input sanitization on prompts
- CORS configured for production

---

## 📈 Scaling

### Horizontal Scaling

- Run multiple worker instances
- Use Redis for job queue (instead of polling DB)
- Deploy to Kubernetes for auto-scaling

### Cost Optimization

- Auto-stop RunPod pods when idle
- CDN for static outputs (S3 + CloudFront)
- Cache frequently requested assets
- Use cheaper GPU instances for simple generations

---

## 📄 License

MIT License - Commercial use allowed

---

## 🙏 Support

- **Documentation:** This README
- **API Docs:** http://localhost:8000/docs
- **Issues:** GitHub Issues

---

**Built with:**
- FastAPI
- Next.js
- Capacitor
- Stripe
- Anthropic Claude
- ComfyUI
- PostgreSQL

**Ready to make money with AI content creation! 🚀💰**
