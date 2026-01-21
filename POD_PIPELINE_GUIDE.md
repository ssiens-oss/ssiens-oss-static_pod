# POD Pipeline - Automated Print-on-Demand System

Complete automation pipeline for generating, approving, and publishing POD designs with RunPod serverless ComfyUI integration.

## 🚀 Quick Start

### 1. Start the Gateway

```bash
./start-gateway-runpod.sh
```

The gateway will start on `http://localhost:5000` with RunPod serverless integration.

### 2. Run Proof of Life

Generate and publish a single design with automated metadata:

```bash
./run-pod-pipeline.sh
```

Or with custom theme:

```bash
./run-pod-pipeline.sh --theme "cyberpunk neon cityscape"
```

## 📋 Features

### ✨ Complete Automation
- **Automated Metadata Generation**: Uses Claude API to generate SEO-friendly titles and descriptions
- **Serverless Image Generation**: RunPod serverless ComfyUI with Flux-dev-fp8 model
- **Auto-Publishing**: One-click publish to Printify with automated approval
- **Proof of Life**: End-to-end testing from generation to publishing

### 🔧 Optimizations for POD
- **Extended Timeout**: 300s timeout for complex POD workflows
- **Auto-Polling**: Automatically polls RunPod for job completion
- **High Quality**: 25 sampling steps, 1024x1024 resolution
- **Error Handling**: Comprehensive retry logic and error recovery
- **Current Branch Detection**: Automatically uses your current git branch

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│  POD Pipeline (pod-pipeline.py)                 │
│  - Metadata generation (Claude API)             │
│  - Workflow orchestration                       │
│  - Publishing automation                        │
└────────────┬────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│  Gateway (Flask - gateway/app/main.py)          │
│  - Image generation API                         │
│  - Approval UI (optional)                       │
│  - Printify integration                         │
└────────────┬────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│  RunPod Serverless (runpod_adapter.py)          │
│  - ComfyUI workflow submission                  │
│  - Job status polling                           │
│  - Image download                               │
└────────────┬────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│  Printify API (printify_client.py)              │
│  - Product creation                             │
│  - Image upload                                 │
│  - Publishing to store                          │
└─────────────────────────────────────────────────┘
```

## 📝 Usage Examples

### Proof of Life (Default)

Single generation with auto-publish:

```bash
./run-pod-pipeline.sh --theme "abstract geometric patterns"
```

### Generate Without Publishing

Useful for testing or review:

```bash
./run-pod-pipeline.sh --theme "nature landscape" --no-publish
```

### Save Results to File

Get detailed JSON output:

```bash
./run-pod-pipeline.sh --theme "retro 80s synthwave" --output results.json
```

### Batch Mode

Generate multiple designs:

```bash
BATCH_COUNT=5 ./run-pod-pipeline.sh --mode batch --theme "minimalist art"
```

### Continuous Mode

Keep generating until stopped:

```bash
./run-pod-pipeline.sh --mode continuous --theme "space exploration"
```

### Auto-Run on Gateway Startup

Set environment variable to run proof-of-life automatically:

```bash
PROOF_OF_LIFE=true ./start-gateway-runpod.sh
```

## 🔧 Configuration

### Environment Variables

Create or update `.env`:

```bash
# ComfyUI / RunPod
COMFYUI_API_URL=https://api.runpod.ai/v2/{your-endpoint}/runsync
RUNPOD_API_KEY=your-runpod-api-key

# Claude API (for metadata generation)
ANTHROPIC_API_KEY=sk-ant-your-claude-api-key
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# Printify (for publishing)
PRINTIFY_API_KEY=your-printify-api-key
PRINTIFY_SHOP_ID=your-shop-id
PRINTIFY_BLUEPRINT_ID=77  # Gildan 18500 Hoodie
PRINTIFY_PROVIDER_ID=39   # SwiftPOD

# Pipeline
AUTO_PUBLISH=true
PROOF_OF_LIFE=false  # Set to true for auto-run on startup
```

### Gateway Configuration

The gateway automatically configures based on `.env`:

- **Flask Host**: `0.0.0.0` (accessible externally)
- **Flask Port**: `5000`
- **Image Directory**: `/workspace/comfyui/output`
- **State File**: `/workspace/gateway/state.json`

## 🎯 Pipeline Modes

### 1. Proof of Life (Default)

**Purpose**: End-to-end validation of the entire pipeline

**What it does**:
1. Generates automated title and description using Claude
2. Submits generation to RunPod serverless
3. Polls for completion (auto-waits)
4. Auto-publishes to Printify
5. Returns product ID

**Use case**: Daily health checks, deployment validation

**Command**:
```bash
./run-pod-pipeline.sh
```

### 2. Batch Mode

**Purpose**: Generate multiple designs in sequence

**What it does**:
1. Runs proof-of-life pipeline multiple times
2. Waits between generations
3. Saves results for each design

**Use case**: Bulk content creation, design library building

**Command**:
```bash
BATCH_COUNT=10 ./run-pod-pipeline.sh --mode batch
```

### 3. Continuous Mode

**Purpose**: Keep generating designs until manually stopped

**What it does**:
1. Infinite loop of proof-of-life pipeline
2. Automatic retry on failures
3. Continuous monitoring

**Use case**: Stress testing, production monitoring

**Command**:
```bash
./run-pod-pipeline.sh --mode continuous
```

## 📊 Output Format

### JSON Result Structure

```json
{
  "success": true,
  "theme": "vibrant abstract art",
  "started_at": "2026-01-21T10:30:00",
  "completed_at": "2026-01-21T10:31:45",
  "duration_seconds": 105.3,
  "metadata": {
    "title": "Vibrant Flow - Abstract Energy Art",
    "description": "Bold, dynamic abstract design featuring flowing energy patterns in vivid colors. Perfect for statement-making apparel.",
    "tags": ["abstract", "vibrant", "modern"]
  },
  "prompt_id": "abc123",
  "image_id": "generated_def456_0",
  "product_id": "printify_789xyz",
  "errors": []
}
```

## 🔍 Monitoring

### Check Gateway Health

```bash
curl http://localhost:5000/health
```

### View Gateway Logs

```bash
# If using systemd
./gateway/pod-gateway-ctl.sh logs

# If running manually
# Check terminal where start-gateway-runpod.sh is running
```

### Check Pipeline Results

```bash
# View saved results
cat /tmp/pod-proof-of-life.json | jq
```

## 🐛 Troubleshooting

### Gateway Not Starting

```bash
# Check Python dependencies
cd gateway
pip install -r requirements.txt

# Verify .env configuration
cat ../.env | grep -E "(COMFYUI|RUNPOD|PRINTIFY)"
```

### Generation Timeout

Increase timeout in `pod-pipeline.py`:

```python
response = requests.post(
    f"{self.gateway_url}/api/generate",
    json={...},
    timeout=600  # Increase to 10 minutes
)
```

### Claude API Not Working

Check if API key is valid:

```bash
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-3-5-sonnet-20241022","max_tokens":100,"messages":[{"role":"user","content":"Hi"}]}'
```

### Publishing Failed

Verify Printify credentials:

```bash
curl -X GET "https://api.printify.com/v1/shops.json" \
  -H "Authorization: Bearer $PRINTIFY_API_KEY"
```

## 🔐 Security Notes

### API Keys

- **Never commit** `.env` or `.env.runpod-config` to git
- These files are gitignored for security
- Keep API keys in environment variables or secure vaults

### Input Validation

- All user inputs are validated
- XSS prevention on titles and descriptions
- Path traversal protection on file operations
- SQL injection not applicable (no SQL database)

## 📈 Performance Optimizations

### RunPod Serverless

- **Auto-polling**: Eliminates manual status checks
- **Extended timeout**: 300s for complex workflows
- **Proper error handling**: Retry logic with backoff

### Image Generation

- **High quality**: 25 steps (up from 20)
- **POD-optimized**: 1024x1024 resolution
- **Professional prompts**: Enhanced with quality keywords

### Metadata Generation

- **Fallback mode**: Works without Claude API
- **SEO-friendly**: Titles optimized for search
- **Engaging descriptions**: Customer-focused copy

## 🎨 Customization

### Custom Workflow

Edit `pod-pipeline.py` to customize the ComfyUI workflow:

```python
def build_pod_workflow(self, prompt: str, seed: Optional[int] = None) -> Dict[str, Any]:
    # Modify workflow nodes here
    # Add custom samplers, upscalers, post-processing
    workflow = {
        # Your custom workflow
    }
    return workflow
```

### Custom Metadata Prompts

Modify the Claude prompt in `generate_automated_metadata`:

```python
prompt = f"""Generate a catchy product title for {theme}.

Focus on:
- Target audience appeal
- SEO keywords
- Emotion-driven language

Return JSON: {{"title": "...", "description": "...", "tags": [...]}}"""
```

## 📚 Related Documentation

- [Gateway Features](./GATEWAY_FEATURES.md) - Complete gateway feature list
- [RunPod Setup](./RUNPOD_SETUP.md) - RunPod serverless configuration
- [Printify Blueprints](./docs/PRINTIFY_BLUEPRINTS.md) - Available product templates

## 🤝 Contributing

Improvements welcome! Areas for enhancement:

1. **Multi-model support**: Add SDXL, Stable Diffusion 3
2. **Quality upscaling**: Integrate Real-ESRGAN
3. **Advanced prompting**: Chain-of-thought prompt generation
4. **Analytics**: Track success rates, generation times
5. **A/B testing**: Compare different workflows

## 📄 License

See main repository LICENSE file.

## 🆘 Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Documentation**: See `/docs` directory

---

**Built with**: Python, Flask, RunPod, ComfyUI, Anthropic Claude, Printify

**Last Updated**: 2026-01-21
