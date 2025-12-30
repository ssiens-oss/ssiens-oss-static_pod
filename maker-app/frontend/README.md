# StaticWaves Maker - Frontend & APK Build Guide

**Production-ready PWA + Android APK optimized for Samsung S25 Ultra**

---

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Java JDK 17+ (for Android build)
- Android Studio (latest version)
- Samsung S25 Ultra or Android emulator

### 1. Install Dependencies

```bash
cd maker-app/frontend
npm install
```

### 2. Configure Environment

```bash
cp .env.example .env.local
```

Edit `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://your-backend-url:8000
```

**For local testing on S25 Ultra:**
```env
# Replace with your computer's local IP
NEXT_PUBLIC_API_URL=http://192.168.1.100:8000
```

### 3. Run Development Server

```bash
npm run dev
```

Open http://localhost:3000

---

## 📱 Build APK for Samsung S25 Ultra

### Step 1: Build PWA

```bash
npm run build
```

This creates an optimized static export in the `out/` folder.

### Step 2: Initialize Capacitor

```bash
# First time only
npx cap init "StaticWaves Maker" "com.staticwaves.maker"

# Add Android platform
npx cap add android
```

### Step 3: Sync Web Assets to Android

```bash
npm run mobile:sync
```

This copies the `out/` folder to the Android project.

### Step 4: Configure for S25 Ultra

The app is already optimized for S25 Ultra's QHD+ display (3088 x 1440).

**Key optimizations:**
- Responsive layouts with Tailwind CSS
- Touch-optimized button sizes (min 48x48px)
- High-res icons (512x512px)
- Viewport configured for high-density displays

### Step 5: Open in Android Studio

```bash
npx cap open android
```

This opens the Android project in Android Studio.

### Step 6: Configure Build Settings

In Android Studio:

1. **File → Project Structure**
   - **Compile SDK**: 34 (Android 14)
   - **Min SDK**: 24 (Android 7.0)
   - **Target SDK**: 34

2. **Build → Generate Signed Bundle/APK**
   - Choose **APK**
   - Create new keystore (first time):
     - **Keystore path**: `~/.android/maker-release.jks`
     - **Password**: (choose strong password)
     - **Alias**: `maker-key`
     - **Validity**: 25 years

   - Or use existing keystore

3. **Select build variant**: `release`

4. **Click Finish**

APK will be generated at:
```
android/app/build/outputs/apk/release/app-release.apk
```

### Step 7: Test on S25 Ultra

#### Option A: USB Debugging

1. Enable Developer Mode on S25 Ultra:
   - Settings → About Phone
   - Tap "Build Number" 7 times

2. Enable USB Debugging:
   - Settings → Developer Options
   - Enable "USB Debugging"

3. Connect S25 Ultra via USB

4. In Android Studio, click **Run** (green play button)

5. Select your S25 Ultra device

#### Option B: Install APK Manually

1. Transfer APK to S25 Ultra via USB or cloud

2. On S25 Ultra:
   - Open Files app
   - Navigate to APK
   - Tap to install
   - Allow "Install from Unknown Sources" if prompted

---

## 🎨 S25 Ultra Specific Features

### Display Optimization

- **Resolution**: 3088 x 1440 (QHD+)
- **Aspect Ratio**: 19.3:9
- **DPI**: 501 ppi

**Tailwind breakpoints configured:**
```javascript
sm: 640px   // Phone landscape
md: 768px   // Tablet
lg: 1024px  // Desktop
xl: 1280px  // Large desktop
2xl: 1536px // S25 Ultra landscape
```

### Touch Targets

All interactive elements are minimum 48x48px for comfortable touch:
- Buttons: 48px height minimum
- Tab buttons: 52px height
- Icon buttons: 48x48px

### Haptic Feedback

Using Capacitor Haptics API:
```typescript
import { Haptics, ImpactStyle } from '@capacitor/haptics';

// Light tap
await Haptics.impact({ style: ImpactStyle.Light });

// Medium feedback
await Haptics.impact({ style: ImpactStyle.Medium });

// Strong confirmation
await Haptics.impact({ style: ImpactStyle.Heavy });
```

### Status Bar

Configured in `capacitor.config.ts`:
```typescript
StatusBar: {
  style: 'dark',
  backgroundColor: '#050507'
}
```

---

## 🎯 Features Included

### AI Generation

✅ **Image** - 1 token, ~15 seconds
- ComfyUI/SDXL integration
- High-res output (512x512 - 2048x2048)
- Download and share

✅ **Video** - 5 tokens, ~45 seconds
- AI video or ffmpeg effects
- MP4 output
- 5-30 second clips

✅ **Music** - 2 tokens, ~30 seconds
- AI music generation
- MP3 output
- Loopable tracks

✅ **Books** - 15 tokens, ~90 seconds
- Claude AI content generation
- PDF and EPUB formats
- 5-10 chapters

### Printify Integration

✅ **Create Products**
- Upload generated images to Printify
- Auto-create posters, t-shirts, mugs, etc.
- Set pricing and publish to store

✅ **Sell Through App**
- Users generate art
- One-click create print product
- Auto-published to Printify shop

### Monetization

✅ **Token System**
- Balance display in header
- Real-time updates
- Token cost per generation

✅ **Rewarded Ads** (AdMob)
- Watch ad → +5 tokens
- 10 ads per day limit
- Native mobile ads

✅ **Subscriptions** (Stripe)
- Creator: $19/mo → 300 tokens
- Studio: $49/mo → 800 tokens
- Pro: $99/mo → 2000 tokens

---

## 🔧 Development

### Available Scripts

```bash
# Development
npm run dev              # Start dev server

# Build
npm run build            # Build for production
npm run export           # Export static files
npm run start            # Start production server

# Mobile
npm run mobile:sync      # Sync web to mobile
npm run mobile:open      # Open Android Studio
npm run mobile:build     # Build + sync + open
```

### Project Structure

```
frontend/
├── pages/
│   ├── _app.tsx         # App wrapper
│   └── index.tsx        # Main generator page
├── lib/
│   ├── api.ts           # API client + Printify
│   └── store.ts         # Zustand state management
├── styles/
│   └── globals.css      # Global styles + Tailwind
├── public/
│   └── manifest.json    # PWA manifest
├── capacitor.config.ts  # Mobile configuration
├── next.config.js       # Next.js + PWA config
└── tailwind.config.js   # Tailwind CSS config
```

### API Integration

All endpoints configured in `lib/api.ts`:

**Maker API:**
- `POST /maker/generate/image`
- `POST /maker/generate/video`
- `POST /maker/generate/music`
- `POST /maker/generate/book`
- `GET /maker/job/{id}`

**Printify API:**
- `GET /shops.json`
- `POST /shops/{id}/uploads/images.json`
- `POST /shops/{id}/products.json`
- `POST /shops/{id}/products/{id}/publish.json`

### State Management

Using Zustand with persistence:

```typescript
import { useStore } from '../lib/store';

const { tokenBalance, user, setAuth } = useStore();
```

---

## 🐛 Troubleshooting

### Build Errors

**"Cannot find module '@capacitor/...'"**
```bash
npm install
npx cap sync
```

**"AAPT: error: resource android:attr/lStar not found"**
- Update `android/build.gradle`:
  ```gradle
  compileSdkVersion 34
  ```

**Gradle sync failed**
- File → Invalidate Caches → Restart
- Clean and rebuild

### Runtime Errors

**"Network request failed"**
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- For local testing, use your computer's IP, not `localhost`
- Ensure backend is running

**Ads not showing**
- Replace test ad ID with your AdMob ID in `capacitor.config.ts`
- Enable test mode for development

**Printify integration failing**
- Add Printify token to localStorage:
  ```javascript
  localStorage.setItem('printify_token', 'your_token');
  localStorage.setItem('printify_shop_id', 'shop_id');
  ```

### S25 Ultra Specific

**App looks zoomed in**
- Check viewport meta tag in `_app.tsx`:
  ```html
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
  ```

**Touch targets too small**
- Minimum 48x48px for all interactive elements
- Already configured in Tailwind classes

**Performance issues**
- Enable hardware acceleration in `android/app/src/main/AndroidManifest.xml`:
  ```xml
  android:hardwareAccelerated="true"
  ```

---

## 📦 Publishing to Google Play

### 1. Prepare Assets

Create:
- **Icon**: 512x512px (already in `/public/icon-512.png`)
- **Feature Graphic**: 1024x500px
- **Screenshots**:
  - Phone: 1440x3088px (S25 Ultra native)
  - 7-inch Tablet: 2048x1536px
  - 10-inch Tablet: 2560x1600px

### 2. Create Google Play Console Account

- Go to https://play.google.com/console
- Pay $25 one-time fee
- Complete developer profile

### 3. Create App

- Click "Create App"
- Fill in details:
  - **Name**: StaticWaves Maker
  - **Category**: Art & Design
  - **Content rating**: Everyone

### 4. Upload APK

- Navigate to "Release" → "Production"
- Click "Create new release"
- Upload `app-release.apk`
- Add release notes

### 5. Complete Store Listing

**Description:**
```
Create stunning images, videos, music, and books with AI. Sell your creations as prints and merch.

Features:
• AI Image Generation
• AI Video Creation
• AI Music Composition
• AI Book Writing
• Printify Integration - Sell prints, t-shirts, and more
• Token-based system
• Watch ads to earn free tokens
• Professional quality outputs

Perfect for:
- Content creators
- Digital artists
- Musicians
- Authors
- Print-on-demand sellers
```

### 6. Submit for Review

Review typically takes 1-3 days.

---

## 🎁 Bonus Features

### PWA Installation

Users can install as PWA on any device:
- **Android**: Tap "Add to Home Screen"
- **iOS**: Tap Share → "Add to Home Screen"
- **Desktop**: Click install icon in address bar

### Offline Support

Service worker caches:
- App shell
- Static assets
- Previous generations (for viewing)

### Deep Links

Configure in `capacitor.config.ts`:
```typescript
{
  plugins: {
    App: {
      appUrlScheme: 'maker'
    }
  }
}
```

Links like `maker://generate/image` open directly in app.

---

## 📊 Testing Checklist

### Functional Testing

- [ ] Generate image (1 token deducted)
- [ ] Generate video (5 tokens deducted)
- [ ] Generate music (2 tokens deducted)
- [ ] Generate book (15 tokens deducted)
- [ ] Watch rewarded ad (+5 tokens)
- [ ] Create Printify product from image
- [ ] Check token balance accuracy
- [ ] View generation queue
- [ ] Save to library
- [ ] Offline mode (view cached content)

### UI/UX Testing on S25 Ultra

- [ ] All text readable at native resolution
- [ ] Touch targets at least 48x48px
- [ ] Smooth scrolling
- [ ] No layout shifts
- [ ] Haptic feedback works
- [ ] Status bar color correct
- [ ] Landscape mode works
- [ ] Edge-to-edge display (no black bars)

### Performance Testing

- [ ] App launches < 3 seconds
- [ ] Page transitions smooth (60fps)
- [ ] Image generation completes
- [ ] No memory leaks (monitor in Android Studio)
- [ ] Battery usage acceptable

---

## 🚀 Production Deployment

### Backend

Deploy backend to cloud (Railway/Render/Fly.io)

Update `.env.local`:
```env
NEXT_PUBLIC_API_URL=https://your-api.railway.app
```

### Frontend

Deploy frontend to Vercel/Netlify for web version:

```bash
# Deploy to Vercel
vercel --prod

# Or Netlify
netlify deploy --prod
```

### Mobile

Rebuild APK with production API URL and publish to Google Play.

---

**Ready to generate AI content and make money! 🚀💰**

Test the app, build the APK, and start creating!
