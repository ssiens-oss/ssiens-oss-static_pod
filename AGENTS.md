# StaticWaves Agent Automation System

Complete autonomous agent framework for POD automation with browser automation, market research, trend analysis, and AI-powered prompt generation.

---

## 🤖 Overview

The Agent Automation System provides a multi-agent framework that autonomously:

- 🌐 **Monitors marketplaces** (Etsy, Redbubble, etc.)
- 📊 **Analyzes trends** and identifies opportunities
- 🎨 **Generates AI prompts** based on market data
- 🏷️ **Optimizes pricing** and product positioning
- 🔄 **Coordinates workflows** across multiple agents
- 🧠 **Learns from performance** to improve over time

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│          Agent Orchestrator (Coordinator)           │
└──────────┬──────────────────────────────────────────┘
           │
     ┌─────┴──────┬──────────┬──────────┬─────────┐
     │            │          │          │         │
┌────▼───┐  ┌────▼────┐ ┌──▼────┐ ┌───▼──┐ ┌───▼───┐
│Browser │  │Research │ │Prompt │ │Social│ │Worker │
│Agents  │  │ Agents  │ │ Gen   │ │Media │ │Agents │
└────────┘  └─────────┘ └───────┘ └──────┘ └───────┘
     │            │          │         │         │
     └────────────┴──────────┴─────────┴─────────┘
                    │
              Data Pipeline
                    ↓
          Queue → ComfyUI → Publish
```

---

## 📦 Agent Types

### Browser Automation Agents
- **MarketplaceMonitorAgent** - Scrapes marketplaces for trends
- **CompetitorAnalysisAgent** - Monitors competitor products
- **SocialMediaScraperAgent** - Tracks social media trends

### Research Agents
- **TrendAnalysisAgent** - Analyzes collected data for patterns
- **OpportunityFinderAgent** - Identifies market gaps
- **SeasonalTrendsAgent** - Predicts seasonal demand

### AI Agents
- **PromptGeneratorAgent** - Creates AI art prompts from trends
- **SmartPromptOptimizerAgent** - Optimizes prompts based on performance

### Processor Agents
- Base classes for creating custom data processing agents

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Install Playwright browsers (for browser automation)
playwright install
```

### 2. Start Agent Service

```bash
# Start agent orchestrator
sudo systemctl start staticwaves-agents

# Check status
sudo systemctl status staticwaves-agents

# View logs
sudo journalctl -u staticwaves-agents -f
```

### 3. Use API to Control Agents

```bash
# Check agent status
curl http://localhost:5000/agents/status

# Run specific agent
curl -X POST http://localhost:5000/agents/marketplace_monitor_etsy/run

# Execute workflow
curl -X POST http://localhost:5000/agents/workflows/daily_research/run
```

---

## 🔌 API Reference

### Agent Management

#### `GET /agents/status`
Get status of all agents
```json
{
  "orchestrator_running": true,
  "total_agents": 5,
  "agents": {
    "marketplace_monitor_etsy": {
      "state": "idle",
      "last_run": "2024-01-15T12:00:00Z",
      "run_count": 42
    }
  }
}
```

#### `GET /agents/agents`
List all registered agents
```json
{
  "count": 5,
  "agents": [
    "marketplace_monitor_etsy",
    "trend_analysis",
    "prompt_generator"
  ]
}
```

#### `POST /agents/<agent_name>/run`
Manually run a specific agent
```bash
curl -X POST http://localhost:5000/agents/trend_analysis/run
```

#### `POST /agents/<agent_name>/pause`
Pause an agent
```bash
curl -X POST http://localhost:5000/agents/marketplace_monitor_etsy/pause
```

#### `POST /agents/<agent_name>/resume`
Resume a paused agent
```bash
curl -X POST http://localhost:5000/agents/marketplace_monitor_etsy/resume
```

### Workflows

#### `GET /agents/workflows`
List available workflows
```json
{
  "count": 5,
  "workflows": {
    "daily_research": "Daily automated market research",
    "full_automation": "Complete autonomous POD workflow"
  }
}
```

#### `POST /agents/workflows/<workflow_name>/run`
Execute a pre-built workflow
```bash
curl -X POST http://localhost:5000/agents/workflows/daily_research/run
```

### Pipelines

#### `POST /agents/pipeline`
Run custom agent pipeline (sequential)
```bash
curl -X POST http://localhost:5000/agents/pipeline \
  -H "Content-Type: application/json" \
  -d '{
    "agents": ["trend_analysis", "opportunity_finder", "prompt_generator"]
  }'
```

#### `POST /agents/parallel`
Run agents in parallel
```bash
curl -X POST http://localhost:5000/agents/parallel \
  -H "Content-Type: application/json" \
  -d '{
    "agents": ["marketplace_monitor_etsy", "trend_analysis"]
  }'
```

### Quick Launch

#### `POST /agents/quick-launch`
Rapid product launch from keyword
```bash
curl -X POST http://localhost:5000/agents/quick-launch \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "cosmic waves",
    "product_type": "hoodie",
    "auto_publish": true
  }'
```

---

## 📋 Pre-Built Workflows

### 1. Daily Market Research
**Schedule**: Every 24 hours

**Steps**:
1. Monitor Etsy, Redbubble marketplaces (parallel)
2. Scrape Instagram trends (parallel)
3. Analyze trends → Find opportunities
4. Generate prompts

**Usage**:
```bash
curl -X POST http://localhost:5000/agents/workflows/daily_research/run
```

### 2. Full Automation
**Description**: Complete autonomous workflow

**Steps**:
1. Research markets (parallel)
2. Generate prompts
3. Create designs (ComfyUI)
4. Generate mockups
5. Upload to Printify
6. Publish to Shopify/TikTok

**Usage**:
```bash
curl -X POST http://localhost:5000/agents/workflows/full_automation/run
```

### 3. Competitive Analysis
**Schedule**: Weekly

**Steps**:
1. Monitor competitor products
2. Analyze pricing
3. Generate competitive report

### 4. Weekly Optimization
**Schedule**: Every Monday

**Steps**:
1. Analyze product performance
2. Optimize prompts based on conversion data
3. Adjust pricing strategies

---

## ⚙️ Configuration

Edit `/opt/staticwaves-pod/config/agents.json`:

```json
{
  "agents": {
    "marketplace_monitor_etsy": {
      "enabled": true,
      "schedule": "every 6 hours",
      "config": {
        "marketplace": "etsy",
        "search_query": "trending",
        "headless": true
      }
    },
    "prompt_generator": {
      "enabled": true,
      "schedule": "every 6 hours",
      "config": {
        "min_prompts": 10,
        "max_prompts": 20
      }
    }
  }
}
```

---

## 🔨 Creating Custom Agents

### Simple Agent

```python
from agents.core.agent import Agent

class MyCustomAgent(Agent):
    async def execute(self) -> Dict[str, Any]:
        # Your agent logic here
        result = {"status": "success", "data": []}
        return result
```

### Data Collector Agent

```python
from agents.core.agent import DataCollectorAgent

class MyDataAgent(DataCollectorAgent):
    async def execute(self) -> Dict[str, Any]:
        data = {"collected": "data"}
        self.save_data(data, "output.json")
        return data
```

### Scheduled Agent

```python
from agents.core.agent import ScheduledAgent

# Runs every hour
agent = ScheduledAgent("my_agent", interval_seconds=3600)

# Register with orchestrator
orchestrator.register_agent(agent)
```

---

## 📊 Agent Monitoring

### Check Agent Status
```bash
# All agents
curl http://localhost:5000/agents/status

# Specific agent
curl http://localhost:5000/agents/trend_analysis

# View logs
sudo journalctl -u staticwaves-agents -f
```

### Agent States
- **idle** - Ready to run
- **running** - Currently executing
- **paused** - Temporarily disabled
- **stopped** - Shut down

---

## 🧪 Browser Automation Examples

### Scrape Marketplace
```python
from agents.browser.automation import MarketplaceMonitorAgent

agent = MarketplaceMonitorAgent(
    "etsy_monitor",
    output_dir,
    {
        "marketplace": "etsy",
        "search_query": "trending art",
        "headless": True
    }
)

result = await agent.run()
```

### Competitor Analysis
```python
from agents.browser.automation import CompetitorAnalysisAgent

agent = CompetitorAnalysisAgent(
    "competitor_monitor",
    output_dir,
    {
        "competitors": [
            "https://example.com/shop/competitor1",
            "https://example.com/shop/competitor2"
        ]
    }
)

result = await agent.run()
```

---

## 🎨 Prompt Generation

### Auto-Generate from Trends

The **PromptGeneratorAgent** automatically:
1. Loads trending keywords from market data
2. Combines with artistic styles and color palettes
3. Generates ready-to-use ComfyUI prompts
4. Queues designs for generation

**Output Example**:
```json
{
  "positive_prompt": "cosmic waves abstract art, vibrant colors, centered composition, high quality, detailed, 4k",
  "negative_prompt": "low quality, blurry, watermark, text, signature",
  "keyword": "cosmic",
  "style": "abstract",
  "estimated_appeal": "high"
}
```

### Custom Prompt Generation
```bash
curl -X POST http://localhost:5000/agents/quick-launch \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "neon cyberpunk city",
    "product_type": "hoodie"
  }'
```

---

## 🔄 Workflow Orchestration

### Sequential Pipeline
```bash
# Run agents one after another
curl -X POST http://localhost:5000/agents/pipeline \
  -d '{"agents": ["agent1", "agent2", "agent3"]}'
```

### Parallel Execution
```bash
# Run agents simultaneously
curl -X POST http://localhost:5000/agents/parallel \
  -d '{"agents": ["agent1", "agent2"]}'
```

### Custom Workflow
```python
workflow = {
    "name": "my_workflow",
    "steps": [
        {
            "type": "parallel",
            "agents": ["marketplace_monitor", "social_scraper"]
        },
        {
            "type": "sequential",
            "agents": ["trend_analysis", "prompt_generator"]
        }
    ]
}

result = await orchestrator.execute_workflow(workflow)
```

---

## 📈 Performance Optimization

### Prompt Optimization Agent

Analyzes product performance and optimizes future prompts:

```python
from agents.prompts.generator import SmartPromptOptimizerAgent

optimizer = SmartPromptOptimizerAgent(
    "prompt_optimizer",
    ["performance_data"]
)

insights = await optimizer.run()
# Returns: top styles, keywords, color palettes
```

**Insights Example**:
```json
{
  "top_styles": ["cyberpunk", "abstract", "watercolor"],
  "top_keywords": ["cosmic", "nature", "geometric"],
  "recommendations": [
    "Focus on 'cyberpunk' style - 40% higher conversion",
    "Use 'vibrant colors' palette - 25% better engagement"
  ]
}
```

---

## 🛡️ Security & Privacy

### Browser Automation
- Runs in **headless mode** by default
- **No cookies/login** stored
- Respects `robots.txt`
- Rate limiting built-in

### Data Collection
- Only public data
- No PII collection
- Configurable retention periods
- GDPR compliant

---

## 🐛 Troubleshooting

### Agent Not Starting
```bash
# Check logs
sudo journalctl -u staticwaves-agents -n 50

# Check dependencies
pip install -r requirements.txt
playwright install

# Restart service
sudo systemctl restart staticwaves-agents
```

### Playwright Issues
```bash
# Install browsers
playwright install

# Test installation
playwright show-capabilities
```

### Agent Stuck
```bash
# Check status
curl http://localhost:5000/agents/status

# Restart specific agent
curl -X POST http://localhost:5000/agents/<agent_name>/pause
curl -X POST http://localhost:5000/agents/<agent_name>/resume
```

---

## 📚 Additional Resources

- [Main POD Stack Documentation](POD_STACK.md)
- [API Reference](API.md)
- [Browser Automation Guide](https://playwright.dev/python/)

---

## 🔮 Future Enhancements

- ✅ Claude AI integration for advanced analysis
- ✅ Multi-language support
- ✅ Voice control via Alexa/Google Home
- ✅ Mobile app for agent management
- ✅ Real-time analytics dashboard

---

**Built with 🤖 by the StaticWaves team**
