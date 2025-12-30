# StaticWaves Maker - Complete Build & Test Guide

**From zero to running APK on Samsung S25 Ultra in under 30 minutes**

---

## 🎯 What You're Building

A complete AI content creation platform that:
- Generates images, videos, music, and books with AI
- Sells generated content as prints/merch through Printify
- Monetizes via subscriptions, token sales, and rewarded ads
- Runs as PWA (web) and native Android APK
- Optimized for Samsung S25 Ultra

---

## 📋 Prerequisites Checklist

### Required Software

- [ ] **Node.js 18+** - https://nodejs.org/
- [ ] **Python 3.11+** - https://python.org/
- [ ] **PostgreSQL 14+** - https://postgresql.org/
- [ ] **Java JDK 17+** - https://adoptium.net/
- [ ] **Android Studio** - https://developer.android.com/studio
- [ ] **Docker** (optional) - https://docker.com/

### Required Accounts & API Keys

- [ ] **Anthropic Claude API** - https://console.anthropic.com/
- [ ] **Stripe Account** - https://dashboard.stripe.com/
- [ ] **Printify Account** - https://printify.com/
- [ ] **AdMob Account** - https://admob.google.com/
- [ ] **RunPod Account** (optional) - https://runpod.io/

---

## 🚀 Quick Start (Docker)

### Fastest Path - Use Docker Compose

```bash
cd maker-app

# 1. Set up environment
cp backend/.env.example backend/.env

# Edit backend/.env with your API keys:
# - ANTHROPIC_API_KEY=sk-ant-xxxxx
# - STRIPE_SECRET_KEY=sk_test_xxxxx
# - (others optional for initial testing)

# 2. Start entire backend with one command
./start.sh

# Or manually:
docker-compose up -d

# 3. Verify backend is running
curl http://localhost:8000/health

# Should return: {"status":"healthy","service":"maker-api","version":"1.0.0"}
```

**Backend is now running!**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Database: localhost:5432

---

## 💻 Development Setup (No Docker)

### Backend Setup

```bash
cd maker-app/backend

# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment
cp .env.example .env

# Edit .env with API keys

# 4. Set up database
# Create PostgreSQL database:
createdb maker_app

# Initialize tables
python -c "from app.database import init_db; init_db()"

# 5. Start API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 6. Start worker (in new terminal)
source venv/bin/activate
python worker/worker.py
```

### Frontend Setup

```bash
cd maker-app/frontend

# 1. Install dependencies
npm install

# 2. Set up environment
cp .env.example .env.local

# Edit .env.local:
# NEXT_PUBLIC_API_URL=http://localhost:8000
# (or your computer's IP for mobile testing: http://192.168.1.100:8000)

# 3. Start development server
npm run dev

# Frontend now running at: http://localhost:3000
```

---

## 📱 Build Android APK for S25 Ultra

### Method 1: Automated Build Script

```bash
cd maker-app/frontend

# Run automated build
./build-apk.sh

# This will:
# 1. Install dependencies
# 2. Build Next.js app
# 3. Initialize Capacitor (if needed)
# 4. Sync assets to Android
# 5. Open Android Studio

# Then in Android Studio:
# - Wait for Gradle sync
# - Build → Generate Signed Bundle/APK
# - Choose APK
# - Create/select keystore
# - Build release APK
```

### Method 2: Manual Build

```bash
cd maker-app/frontend

# 1. Build web app
npm run build

# 2. Initialize Capacitor (first time only)
npx cap init "StaticWaves Maker" "com.staticwaves.maker" --web-dir=out
npx cap add android

# 3. Sync web assets
npx cap sync android

# 4. Open Android Studio
npx cap open android

# 5. In Android Studio:
#    Build → Generate Signed Bundle/APK → APK
#    Create keystore (first time)
#    Build release

# APK location:
# android/app/build/outputs/apk/release/app-release.apk
```

---

## 🧪 Testing on Samsung S25 Ultra

### Option A: USB Debugging

```bash
# 1. Enable Developer Mode on S25 Ultra:
#    Settings → About Phone → Tap "Build Number" 7 times

# 2. Enable USB Debugging:
#    Settings → Developer Options → USB Debugging

# 3. Connect S25 Ultra via USB

# 4. In Android Studio, click Run (green play button)

# 5. Select your S25 Ultra device

# App installs and launches automatically
```

### Option B: Manual APK Install

```bash
# 1. Transfer APK to S25 Ultra:
#    - USB cable and copy file
#    - Or upload to cloud (Google Drive, Dropbox)
#    - Or email to yourself

# 2. On S25 Ultra:
#    - Open Files app
#    - Navigate to APK
#    - Tap to install
#    - Allow "Install from Unknown Sources" if prompted

# 3. Open app from launcher
```

---

## ✅ Testing Checklist

### Backend Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test image generation (requires auth token)
curl -X POST http://localhost:8000/maker/generate/image \
  -H "Authorization: Bearer brand_123" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"cyberpunk neon city"}'

# Should return job_id and status

# Check API docs
open http://localhost:8000/docs
```

### Frontend Testing (Web)

- [ ] Open http://localhost:3000
- [ ] UI loads correctly
- [ ] Tabs work (Image, Video, Music, Book, Print)
- [ ] Token balance displays
- [ ] Can enter prompt
- [ ] Generate button works (with backend running)

### Mobile Testing (APK on S25 Ultra)

#### UI Tests
- [ ] App launches < 3 seconds
- [ ] All text readable
- [ ] Touch targets easy to tap (48x48px minimum)
- [ ] Smooth scrolling
- [ ] Tabs switch smoothly
- [ ] No visual glitches

#### Functional Tests
- [ ] Generate Image (costs 1 token)
  - Enter prompt: "neon cyberpunk cityscape"
  - Tap "Generate Image (1 token)"
  - Wait for generation (~15-30 seconds)
  - Image appears
  - Token balance decreases by 1

- [ ] Watch Rewarded Ad
  - Tap "🎁 Watch Ad (+5)"
  - Ad plays
  - Tap to close after video
  - Tokens increase by +5
  - Success message appears

- [ ] Create Printify Product
  - Generate an image first
  - Tap "Create & Sell as Print"
  - Product created in Printify shop
  - Success message appears

- [ ] Generate Video (costs 5 tokens)
  - Enter prompt: "glitch logo animation"
  - Tap "Generate Video (5 tokens)"
  - Wait for generation (~45-60 seconds)
  - Video player appears with MP4

- [ ] Generate Music (costs 2 tokens)
  - Enter prompt: "lo-fi chill beats"
  - Tap "Generate Music (2 tokens)"
  - Wait for generation (~30-40 seconds)
  - Audio player appears with MP3

- [ ] Generate Book (costs 15 tokens)
  - Enter prompt: "children's monster coloring book"
  - Tap "Generate Book (15 tokens)"
  - Wait for generation (~90-120 seconds)
  - Download button appears for PDF/EPUB

#### Performance Tests
- [ ] App doesn't crash
- [ ] No freezing or lag
- [ ] Smooth animations (60fps)
- [ ] Battery usage acceptable
- [ ] Memory usage stable

#### S25 Ultra Specific
- [ ] Display looks crisp (QHD+ native resolution)
- [ ] No black bars (edge-to-edge display)
- [ ] Landscape mode works
- [ ] Haptic feedback works (light vibration on taps)
- [ ] Status bar correct color
- [ ] Touch response instant

---

## 🐛 Common Issues & Fixes

### Backend Issues

**Issue:** Database connection failed
```bash
# Fix: Ensure PostgreSQL is running
sudo service postgresql start

# Create database if missing
createdb maker_app

# Re-initialize
python -c "from app.database import init_db; init_db()"
```

**Issue:** Module not found
```bash
# Fix: Install dependencies
pip install -r requirements.txt
```

**Issue:** Port 8000 already in use
```bash
# Fix: Kill process using port
lsof -i :8000
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8001
```

### Frontend Issues

**Issue:** Cannot connect to backend
```bash
# Fix: Check API URL in .env.local
# For mobile testing, use your computer's IP:
NEXT_PUBLIC_API_URL=http://192.168.1.100:8000

# Find your IP:
# Mac/Linux: ifconfig | grep inet
# Windows: ipconfig
```

**Issue:** npm install fails
```bash
# Fix: Clear cache and reinstall
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

**Issue:** Build fails
```bash
# Fix: Check Node.js version
node --version  # Should be 18+

# Update if needed
nvm install 18
nvm use 18
```

### Mobile/APK Issues

**Issue:** Gradle sync failed
```bash
# Fix in Android Studio:
# File → Invalidate Caches → Restart
# Clean Project
# Rebuild Project
```

**Issue:** Can't install APK on S25 Ultra
```bash
# Fix: Enable unknown sources
# Settings → Security → Install Unknown Apps
# Enable for Files app or your browser
```

**Issue:** App crashes on launch
```bash
# Fix: Check logs in Android Studio
# Logcat tab → Filter by "Maker"

# Common causes:
# - Wrong API URL (backend not accessible)
# - Missing permissions in AndroidManifest.xml
# - JavaScript errors (check Chrome DevTools via chrome://inspect)
```

**Issue:** Ads not showing
```bash
# Fix: Replace test ad ID with real AdMob ID
# Edit capacitor.config.ts:
# AdMob.appId = "ca-app-pub-YOUR-REAL-ID~xxxxx"

# For testing, use:
# "ca-app-pub-3940256099942544~3347511713" (Google test ID)
```

**Issue:** Printify integration fails
```bash
# Fix: Add Printify credentials
# 1. Get API token from Printify dashboard
# 2. Get Shop ID
# 3. In app, save to localStorage:
localStorage.setItem('printify_token', 'your_token');
localStorage.setItem('printify_shop_id', 'shop_id');

# Or add authentication page (future enhancement)
```

---

## 🎨 Customization

### Change App Name

**Android:**
```xml
<!-- android/app/src/main/res/values/strings.xml -->
<string name="app_name">Your App Name</string>

<!-- android/app/src/main/AndroidManifest.xml -->
android:label="Your App Name"
```

**PWA:**
```json
// frontend/public/manifest.json
{
  "name": "Your App Name",
  "short_name": "YourApp"
}
```

### Change App Icon

Replace these files in `frontend/public/`:
- icon-72.png
- icon-96.png
- icon-128.png
- icon-144.png
- icon-192.png
- icon-512.png

Or use icon generator: https://easyappicon.com/

### Change Color Theme

**Primary color:**
```javascript
// frontend/tailwind.config.js
colors: {
  primary: {
    500: '#7B2CFF',  // Change this
    600: '#7c3aed',  // And this
  }
}
```

**Dark background:**
```javascript
colors: {
  dark: {
    300: '#050507',  // Main background
  }
}
```

---

## 📊 Monitoring & Analytics

### Check Backend Logs

```bash
# Docker
docker-compose logs -f backend

# Manual
tail -f logs/maker.log

# Worker logs
docker-compose logs -f worker
```

### Check Database

```bash
# Connect to database
psql maker_app

# Check token balances
SELECT * FROM token_balances;

# Check recent jobs
SELECT * FROM generation_jobs ORDER BY created_at DESC LIMIT 10;

# Check subscriptions
SELECT * FROM subscriptions;
```

### Monitor Mobile App

In Android Studio:
- Logcat → Filter by package name
- Profiler → Monitor CPU, Memory, Network
- Device File Explorer → Check app data

---

## 🚀 Deploy to Production

### Backend

```bash
# Deploy to Railway
railway init
railway up

# Or Render
render deploy

# Set environment variables in dashboard
```

### Frontend

```bash
# Deploy to Vercel
vercel --prod

# Or Netlify
netlify deploy --prod
```

### Mobile

1. Build signed APK (release variant)
2. Test on real device
3. Go to Google Play Console: https://play.google.com/console
4. Create app
5. Upload APK
6. Complete store listing
7. Submit for review

---

## 💰 Monetization Setup

### Stripe

1. Create products in Stripe Dashboard
2. Copy price IDs to backend/.env:
```env
STRIPE_PRICE_CREATOR=price_xxxxx
STRIPE_PRICE_STUDIO=price_xxxxx
STRIPE_PRICE_PRO=price_xxxxx
```

3. Set up webhook:
   - URL: https://your-api.com/billing/webhook
   - Events: checkout.session.completed, invoice.paid, customer.subscription.deleted

### AdMob

1. Create app in AdMob
2. Create Rewarded ad unit
3. Copy ad unit ID to capacitor.config.ts:
```typescript
AdMob: {
  appId: 'ca-app-pub-xxxxx~xxxxx',
}
```

### Printify

1. Create Printify account
2. Create shop
3. Get API token from Settings → API
4. Add to frontend localStorage or create auth page

---

## 📈 Success Metrics

Track these to measure success:

- **Users:** Total registered users
- **Daily Active Users (DAU)**
- **Generations:** Total AI generations
- **Revenue:**
  - Subscription MRR
  - Token pack sales
  - Ad revenue
- **Printify Sales:** Products created and sold
- **Retention:** 7-day, 30-day retention rates
- **Conversion:** Free → Paid conversion rate

Target:
- Month 1: 100 users, $500 MRR
- Month 3: 500 users, $5,000 MRR
- Month 6: 2,000 users, $20,000 MRR

---

## 🎯 Next Steps

1. **Test locally** - Verify everything works
2. **Build APK** - Use ./build-apk.sh
3. **Test on S25 Ultra** - Install and test all features
4. **Deploy backend** - Railway or Render
5. **Deploy frontend** - Vercel or Netlify
6. **Set up monetization** - Stripe + AdMob
7. **Submit to Google Play** - Launch!

---

**You're ready to launch! 🚀**

Questions? Check:
- maker-app/README.md (main docs)
- maker-app/frontend/README.md (frontend/mobile docs)
- http://localhost:8000/docs (API docs)
