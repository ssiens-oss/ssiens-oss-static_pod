# StaticWaves POD Studio v6.0

> A web-based simulation of the StaticWaves Print-on-Demand automation suite, featuring batch processing, real-time logging, localStorage persistence, export functionality, and an interactive design editor.

![Version](https://img.shields.io/badge/version-6.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Tests](https://img.shields.io/badge/tests-42%20passing-brightgreen.svg)

## 🌟 Features

### Core Functionality
- **🚀 Single & Batch Processing** - Process one or multiple product drops
- **🎨 Live Design Preview** - Real-time preview of generated designs
- **👕 Product Mockups** - Visualize designs on products (T-shirts, etc.)
- **📊 Progress Tracking** - Global progress bar with batch calculation
- **📝 Real-time Logging** - Color-coded terminal output (INFO, SUCCESS, WARNING, ERROR)
- **📦 Printify Queue** - Visual queue management with status tracking

### New in v6.0
- **💾 localStorage Persistence** - Auto-save/load configuration and queue
- **📥 Export Functionality** - Export queue and logs as CSV
- **⏹️ Stop Button** - Halt execution at any time
- **✨ Enhanced Editor** - Zoom and pan design previews
- **🧪 Comprehensive Testing** - 42 unit tests with full coverage
- **🚀 CI/CD Pipeline** - Automated deployment with GitHub Actions

## 📦 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ssiens-oss/ssiens-oss-static_pod.git
cd ssiens-oss-static_pod

# Install dependencies
npm install

# Start development server
npm run dev
```

### Available Scripts

```bash
npm run dev              # Start development server (Vite)
npm run build            # Build for production
npm run preview          # Preview production build
npm test                 # Run tests
npm run test:ui          # Run tests with UI
npm run test:coverage    # Run tests with coverage report
```

## 🎯 Usage

### Basic Workflow

1. **Configure Settings**
   - Drop Name: Name your product collection
   - Design Count: Number of designs to generate
   - Blueprint ID: Product type (6 = T-Shirt)
   - Provider ID: POD provider (1 = Printify)

2. **Run Process**
   - **Single Drop**: Click "Run Single Drop" for one collection
   - **Batch Mode**: Enter comma-separated drops, click "Run Batch Mode"
   - **Stop**: Click "Stop Execution" to halt mid-process

3. **Monitor Progress**
   - Watch terminal logs for real-time updates
   - Track progress bar (shows batch progress for multiple drops)
   - View queue items with status indicators

4. **Export Data**
   - Click download icon on queue to export as CSV
   - Click download icon on terminal to export logs as CSV

### Configuration Example

```typescript
{
  dropName: 'Summer2024',
  designCount: 10,
  blueprintId: 6,        // T-Shirt
  providerId: 1,         // Printify
  batchList: 'Drop1, Drop2, Drop3'  // For batch mode
}
```

### Batch Processing

Enter multiple drops separated by commas:

```
Summer2024, Fall2024, Winter2024
```

The system will:
- Process each drop sequentially
- Calculate cumulative progress
- Generate unique designs and mockups per drop
- Track all items in queue

## 🏗️ Architecture

```
├── App.tsx                      # Main application component
├── components/
│   ├── Terminal.tsx             # Log display component
│   └── EditorControls.tsx       # Design editor tools
├── services/
│   └── mockEngine.ts            # POD workflow simulation
├── config/
│   └── podConfig.ts             # Centralized configuration
├── utils/
│   ├── podUtils.ts              # Shared utility functions
│   ├── storage.ts               # localStorage persistence
│   └── export.ts                # CSV/JSON export utilities
├── types.ts                     # TypeScript definitions
└── tests/                       # Comprehensive test suite
    ├── podUtils.test.ts
    ├── storage.test.ts
    └── export.test.ts
```

## 🔧 Configuration

### Environment Variables

No environment variables required for the simulation. For real API integration, see [API Integration Guide](./docs/API_INTEGRATION.md).

### LocalStorage Keys

The app uses these localStorage keys:
- `pod_studio_config` - Saved configuration
- `pod_studio_queue` - Queue state
- `pod_studio_logs` - Recent logs (last 100)

## 🧪 Testing

```bash
# Run all tests
npm test

# Run with UI
npm run test:ui

# Generate coverage report
npm run test:coverage
```

**Test Coverage:**
- ✅ 18 tests for utility functions
- ✅ 13 tests for storage persistence
- ✅ 11 tests for export functionality
- **Total: 42 tests passing**

## 🚀 Deployment

### RunPod (Docker/Cloud)

```bash
# Build and deploy to RunPod
./scripts/deploy-runpod.sh

# Or test locally first
./scripts/test-local.sh
```

**See detailed guide**: [RunPod Deployment](./docs/RUNPOD_DEPLOYMENT.md)

### GitHub Pages

1. Enable GitHub Pages in repository settings
2. Push to main branch
3. GitHub Actions will automatically deploy

### Netlify

```bash
# One-click deploy
netlify deploy --prod

# Or connect your GitHub repo in Netlify dashboard
```

### Vercel

```bash
# One-click deploy
vercel --prod

# Or import project in Vercel dashboard
```

## 📊 Workflow Stages

The POD simulation executes these stages:

1. **Initialization** (5% progress)
   - Start process
   - Initialize modules

2. **Design Generation** (5% → 25%)
   - Create design assets
   - Generate PNG files
   - Update preview

3. **Mockup Creation** (25% → 50%)
   - Apply design to product
   - Render displacement maps (3 phases)
   - Generate mockup preview

4. **API Upload** (50% → 100%)
   - Authenticate with Printify
   - Create queue item
   - Stream workflow steps (8 stages)
   - Complete upload

## 🎨 UI Components

### Terminal
- Color-coded logs (green=success, red=error, yellow=warning, blue=info)
- Auto-scrolling
- Export logs as CSV
- Clear button

### Queue Management
- Real-time status updates
- Visual indicators (pending ⏳, uploading ⟳, completed ✓, failed ✖️)
- Export queue as CSV
- Item count badge

### Design Editor
- Zoom controls (90%, 110%)
- 4-way movement pad
- Real-time transform preview
- Save functionality

## 📝 API Integration

For integrating with real Printify API, see [API Integration Guide](./docs/API_INTEGRATION.md).

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- Built with [React 19](https://react.dev/)
- Styled with [Tailwind CSS](https://tailwindcss.com/)
- Icons by [Lucide](https://lucide.dev/)
- Build tool: [Vite](https://vitejs.dev/)
- Testing: [Vitest](https://vitest.dev/)

## 📞 Support

- 📧 Email: support@staticwaves.io
- 🐛 Issues: [GitHub Issues](https://github.com/ssiens-oss/ssiens-oss-static_pod/issues)
- 📖 Docs: [Documentation](./docs/)

---

Made with ❤️ by the StaticWaves Team
