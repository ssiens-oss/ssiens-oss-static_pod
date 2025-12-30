# StaticWaves POD Studio v6.0 + Autonomous Backend

> A complete Print-on-Demand automation suite with multi-LLM AI agents, autonomous design generation, and social media publishing. Includes a web-based frontend for monitoring and a powerful Python backend with LangChain & CrewAI integration.

![Version](https://img.shields.io/badge/version-6.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Tests](https://img.shields.io/badge/tests-42%20passing-brightgreen.svg)
![Backend](https://img.shields.io/badge/backend-Python%203.11-blue.svg)
![AI](https://img.shields.io/badge/AI-GPT%20%7C%20Claude%20%7C%20Grok%20%7C%20Llama-purple.svg)

## 🤖 Autonomous Backend System (NEW)

The POD Studio now includes a **complete autonomous backend** powered by cutting-edge AI:

### 🧠 Multi-LLM Orchestration

Sequential AI pipeline using **4 different LLM providers**:

```
Grok-4 (Trend Analysis)
    → Claude 3.5 (Prompt Engineering)
        → Llama 3.3 (Creative Variations)
            → GPT-4 (Marketing Polish)
```

- **Grok-4** (X.AI): Deep trend analysis with DeepSearch capabilities
- **Claude 3.5** (Anthropic): Technical prompt engineering for ComfyUI
- **Llama 3.3** (Groq): High-speed creative variations and alternatives
- **GPT-4** (OpenAI): Final marketing polish and metadata generation

### 🤖 CrewAI Agent System

Three autonomous agents working together:

1. **Trend Analyst Agent**
   - Role: Streetwear trend researcher
   - LLM: Grok-4
   - Output: Market trends, viral aesthetics, emerging themes

2. **Prompt Engineer Agent**
   - Role: ComfyUI prompt specialist
   - LLM: Claude 3.5
   - Output: Technical image generation prompts with optimal parameters

3. **Caption Writer Agent**
   - Role: Social media content creator
   - LLM: GPT-4
   - Output: Viral captions, hashtags, and product descriptions

### ✨ Key Features

- ✅ **AI Image Generation**: RunPod ComfyUI with SDXL/Stable Diffusion
- ✅ **Auto-Publishing**: Printify, Shopify, WooCommerce, Etsy, Amazon
- ✅ **Social Media**: Instagram & TikTok automation with AI captions
- ✅ **Webhooks**: Real-time event handling (Printify, WooCommerce)
- ✅ **Product Research**: Trend analysis from AliExpress, Etsy, Shopify
- ✅ **Batch Processing**: Handle 10-50+ products simultaneously
- ✅ **Automated Scheduling**: Daily runs at 2 AM + hourly during business hours
- ✅ **Caching**: Redis-powered caching with intelligent TTL
- ✅ **Monitoring**: Prometheus metrics + Grafana dashboards
- ✅ **Error Handling**: Retry logic with exponential backoff
- ✅ **Notifications**: Email, Telegram, Discord, Slack alerts

### 🚀 Quick Start (Backend)

```bash
cd backend

# Copy and configure environment
cp .env.example .env.pod
nano .env.pod  # Add your API keys

# Docker deployment (recommended)
docker-compose up -d

# OR manual setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python autonomous_pod.py
```

**📖 Full deployment guide**: See [DEPLOYMENT.md](./DEPLOYMENT.md) for complete setup instructions including:
- Local development setup
- Production deployment (Docker, Supervisor, Systemd)
- HTTPS configuration with Nginx
- RunPod ComfyUI setup
- Social media configuration
- Monitoring & troubleshooting

### 🏗️ Backend Architecture

```
Frontend (Browser) → Flask Backend → Multi-LLM Chain → CrewAI Agents
                                    ↓
                              RunPod ComfyUI (GPU)
                                    ↓
                          Printify / Shopify / Etsy
                                    ↓
                       Instagram / TikTok Publishing
```

**Backend Stack:**
- Python 3.11 with Flask
- LangChain (Multi-LLM orchestration)
- CrewAI (Agent framework)
- PostgreSQL (Data storage)
- Redis (Caching)
- Prometheus + Grafana (Monitoring)
- Gunicorn (Production server)

---

## 🌟 Frontend Features

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

## 📦 Quick Start (Frontend)

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

## 🏗️ Project Structure

```
ssiens-oss-static_pod/
├── backend/                     # 🆕 Autonomous Backend System
│   ├── autonomous_pod.py        # Main Flask app with multi-LLM integration
│   ├── scheduler.py             # Automated scheduling service
│   ├── requirements.txt         # Python dependencies
│   ├── .env.example             # Configuration template
│   ├── Dockerfile               # Container image
│   ├── docker-compose.yml       # Multi-container deployment
│   └── supervisor.conf          # Process management config
├── dist/
│   └── pod-studio-complete.html # Enhanced frontend with agent monitoring
├── src/                         # Frontend React Application
│   ├── App.tsx                  # Main application component
│   ├── components/
│   │   ├── Terminal.tsx         # Log display component
│   │   └── EditorControls.tsx   # Design editor tools
│   ├── services/
│   │   └── mockEngine.ts        # POD workflow simulation
│   ├── config/
│   │   └── podConfig.ts         # Centralized configuration
│   ├── utils/
│   │   ├── podUtils.ts          # Shared utility functions
│   │   ├── storage.ts           # localStorage persistence
│   │   └── export.ts            # CSV/JSON export utilities
│   ├── types.ts                 # TypeScript definitions
│   └── tests/                   # Comprehensive test suite
│       ├── podUtils.test.ts
│       ├── storage.test.ts
│       └── export.test.ts
├── DEPLOYMENT.md                # 🆕 Complete deployment guide
└── README.md                    # This file
```

## 🔧 Configuration

### Backend Environment Variables

The autonomous backend requires API keys for:

```bash
# Multi-LLM Providers (at least 2 recommended)
OPENAI_API_KEY=sk-your-key          # GPT-4/5
ANTHROPIC_API_KEY=sk-ant-your-key   # Claude 3.5
XAI_API_KEY=xai-your-key            # Grok-4
GROQ_API_KEY=gsk_your-key           # Llama 3.3 (free tier)

# AI Image Generation
COMFYUI_URL=https://your-pod-8188.proxy.runpod.net
RUNPOD_API_KEY=your-runpod-key

# Print-on-Demand
PRINTIFY_API_KEY=your-printify-key
PRINTIFY_SHOP_ID=12345678

# Social Media
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password
TIKTOK_SESSION_ID=your-session-id
```

**See `backend/.env.example` for complete configuration template.**

### Frontend Configuration

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

### Backend Deployment

**Docker Compose (Recommended)**

```bash
cd backend
docker-compose up -d

# View logs
docker-compose logs -f pod-backend
docker-compose logs -f pod-scheduler
```

**Supervisor (VPS)**

```bash
cd backend
sudo cp supervisor.conf /etc/supervisor/conf.d/pod-studio.conf
sudo supervisorctl reread && sudo supervisorctl update
sudo supervisorctl start pod-studio:*
```

**Systemd (Production Linux)**

See [DEPLOYMENT.md](./DEPLOYMENT.md) for systemd service configurations.

**📖 Complete Guide**: [DEPLOYMENT.md](./DEPLOYMENT.md) includes:
- Local development setup
- Three deployment options (Docker/Supervisor/Systemd)
- HTTPS with Nginx + Certbot
- RunPod ComfyUI configuration
- Monitoring & troubleshooting
- Scaling strategies
- Cost estimates ($10-20 per 100 designs)

### Frontend Deployment

#### RunPod (Docker/Cloud)

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

### Autonomous Backend APIs

The backend provides REST endpoints for:

- `POST /webhook/printify` - Printify webhook handler (order events)
- `POST /webhook/woocommerce` - WooCommerce webhook handler
- `GET /health` - Health check endpoint
- `POST /test/workflow` - Test complete workflow
- `GET /api/analytics` - Analytics dashboard data
- `GET /api/trends` - Current trend analysis

### Frontend Integration

For integrating the frontend with real Printify API, see [API Integration Guide](./docs/API_INTEGRATION.md).

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

**Frontend:**
- Built with [React 19](https://react.dev/)
- Styled with [Tailwind CSS](https://tailwindcss.com/)
- Icons by [Lucide](https://lucide.dev/)
- Build tool: [Vite](https://vitejs.dev/)
- Testing: [Vitest](https://vitest.dev/)

**Backend:**
- [LangChain](https://python.langchain.com/) - Multi-LLM orchestration
- [CrewAI](https://docs.crewai.com/) - Agent framework
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [RunPod](https://runpod.io/) - GPU compute for ComfyUI
- [Printify](https://printify.com/) - Print-on-Demand API
- AI Providers: OpenAI, Anthropic, X.AI, Groq

## 📞 Support

- 📧 Email: support@staticwaves.io
- 🐛 Issues: [GitHub Issues](https://github.com/ssiens-oss/ssiens-oss-static_pod/issues)
- 📖 Docs: [Documentation](./docs/)

---

Made with ❤️ by the StaticWaves Team
