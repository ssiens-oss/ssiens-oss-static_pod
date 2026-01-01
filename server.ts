/**
 * Production API Server
 * Handles POD pipeline orchestration with real services
 */

import express, { Request, Response } from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { Orchestrator } from './services/orchestrator';
import { LogEntry, LogType } from './types';

// Load environment variables
dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('dist'));

// In-memory storage for active pipelines
const activePipelines = new Map<string, {
  orchestrator: Orchestrator;
  logs: LogEntry[];
  progress: number;
  status: 'pending' | 'running' | 'completed' | 'failed';
  result?: any;
}>();

/**
 * Initialize orchestrator with environment config
 */
function createOrchestrator(): Orchestrator {
  const config: any = {
    comfyui: {
      apiUrl: process.env.COMFYUI_API_URL || 'http://localhost:8188',
      outputDir: process.env.COMFYUI_OUTPUT_DIR || '/data/comfyui/output'
    },
    claude: {
      apiKey: process.env.ANTHROPIC_API_KEY || ''
    },
    storage: {
      type: (process.env.STORAGE_TYPE as any) || 'local',
      basePath: process.env.STORAGE_PATH || '/data/designs'
    },
    options: {
      enabledPlatforms: process.env.ENABLE_PLATFORMS?.split(',') || ['printify'],
      autoPublish: process.env.AUTO_PUBLISH === 'true',
      tshirtPrice: parseFloat(process.env.DEFAULT_TSHIRT_PRICE || '19.99'),
      hoodiePrice: parseFloat(process.env.DEFAULT_HOODIE_PRICE || '34.99')
    }
  };

  // Add platform configs
  if (process.env.PRINTIFY_API_KEY && process.env.PRINTIFY_SHOP_ID) {
    config.printify = {
      apiKey: process.env.PRINTIFY_API_KEY,
      shopId: process.env.PRINTIFY_SHOP_ID
    };
  }

  if (process.env.SHOPIFY_STORE_URL && process.env.SHOPIFY_ACCESS_TOKEN) {
    config.shopify = {
      storeUrl: process.env.SHOPIFY_STORE_URL,
      accessToken: process.env.SHOPIFY_ACCESS_TOKEN
    };
  }

  if (process.env.TIKTOK_APP_KEY) {
    config.tiktok = {
      appKey: process.env.TIKTOK_APP_KEY,
      appSecret: process.env.TIKTOK_APP_SECRET,
      shopId: process.env.TIKTOK_SHOP_ID,
      accessToken: process.env.TIKTOK_ACCESS_TOKEN
    };
  }

  if (process.env.ETSY_API_KEY) {
    config.etsy = {
      apiKey: process.env.ETSY_API_KEY,
      shopId: process.env.ETSY_SHOP_ID,
      accessToken: process.env.ETSY_ACCESS_TOKEN
    };
  }

  if (process.env.INSTAGRAM_ACCESS_TOKEN) {
    config.instagram = {
      accessToken: process.env.INSTAGRAM_ACCESS_TOKEN,
      businessAccountId: process.env.INSTAGRAM_BUSINESS_ACCOUNT_ID
    };
  }

  if (process.env.FACEBOOK_PAGE_ID) {
    config.facebook = {
      pageId: process.env.FACEBOOK_PAGE_ID,
      accessToken: process.env.FACEBOOK_ACCESS_TOKEN,
      catalogId: process.env.FACEBOOK_CATALOG_ID
    };
  }

  return new Orchestrator(config);
}

/**
 * Health check endpoint
 */
app.get('/health', (req: Request, res: Response) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    config: {
      comfyui: !!process.env.COMFYUI_API_URL,
      claude: !!process.env.ANTHROPIC_API_KEY,
      printify: !!(process.env.PRINTIFY_API_KEY && process.env.PRINTIFY_SHOP_ID),
      shopify: !!(process.env.SHOPIFY_STORE_URL && process.env.SHOPIFY_ACCESS_TOKEN)
    }
  });
});

/**
 * Start pipeline
 */
app.post('/api/pipeline/start', async (req: Request, res: Response) => {
  const { dropName, designCount, theme, style, niche, productTypes, customPrompt } = req.body;

  if (!dropName || !designCount) {
    return res.status(400).json({ error: 'Missing required fields: dropName, designCount' });
  }

  // Validate prompt mode - must have either (theme+style+niche) OR customPrompt
  if (!customPrompt && (!theme || !style)) {
    return res.status(400).json({
      error: 'Missing prompt configuration: provide either customPrompt or (theme, style, niche)'
    });
  }

  // Generate unique pipeline ID
  const pipelineId = `pipeline-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

  // Create orchestrator
  const orchestrator = createOrchestrator();
  const logs: LogEntry[] = [];

  // Set up logger
  orchestrator.setLogger((message: string, type: string) => {
    logs.push({
      id: Math.random().toString(36).substr(2, 9),
      timestamp: new Date().toLocaleTimeString('en-US', { hour12: false }),
      message,
      type: type as LogType
    });
  });

  // Store pipeline state
  activePipelines.set(pipelineId, {
    orchestrator,
    logs,
    progress: 0,
    status: 'pending'
  });

  // Start pipeline asynchronously
  (async () => {
    const pipeline = activePipelines.get(pipelineId)!;
    pipeline.status = 'running';

    try {
      // Prepare request based on prompt mode
      const pipelineRequest: any = {
        productTypes: productTypes || ['tshirt', 'hoodie'],
        count: designCount,
        autoPublish: true
      };

      if (customPrompt) {
        // Manual mode: use custom prompt directly
        pipelineRequest.prompt = customPrompt;
      } else {
        // Claude AI mode: use theme/style/niche for AI generation
        pipelineRequest.theme = theme;
        pipelineRequest.style = style;
        pipelineRequest.niche = niche;
      }

      const result = await orchestrator.run(pipelineRequest);

      pipeline.status = result.success ? 'completed' : 'failed';
      pipeline.result = result;
      pipeline.progress = 100;
    } catch (error) {
      pipeline.status = 'failed';
      pipeline.result = { error: error instanceof Error ? error.message : 'Unknown error' };
      pipeline.progress = 0;
    }
  })();

  res.json({ pipelineId, status: 'started' });
});

/**
 * Get pipeline status
 */
app.get('/api/pipeline/:pipelineId', (req: Request, res: Response) => {
  const { pipelineId } = req.params;
  const pipeline = activePipelines.get(pipelineId);

  if (!pipeline) {
    return res.status(404).json({ error: 'Pipeline not found' });
  }

  res.json({
    pipelineId,
    status: pipeline.status,
    progress: pipeline.progress,
    logs: pipeline.logs,
    result: pipeline.result
  });
});

/**
 * Get pipeline logs (streaming)
 */
app.get('/api/pipeline/:pipelineId/logs', (req: Request, res: Response) => {
  const { pipelineId } = req.params;
  const lastLogId = req.query.lastLogId as string;

  const pipeline = activePipelines.get(pipelineId);

  if (!pipeline) {
    return res.status(404).json({ error: 'Pipeline not found' });
  }

  // Get logs after lastLogId
  let logs = pipeline.logs;
  if (lastLogId) {
    const lastIndex = logs.findIndex(log => log.id === lastLogId);
    logs = lastIndex >= 0 ? logs.slice(lastIndex + 1) : logs;
  }

  res.json({ logs, status: pipeline.status, progress: pipeline.progress });
});

/**
 * Get orchestrator stats
 */
app.get('/api/stats', async (req: Request, res: Response) => {
  try {
    const orchestrator = createOrchestrator();
    const stats = await orchestrator.getStats();
    res.json(stats);
  } catch (error) {
    res.status(500).json({ error: error instanceof Error ? error.message : 'Unknown error' });
  }
});

/**
 * Test configuration
 */
app.get('/api/config/test', async (req: Request, res: Response) => {
  const results: any = {
    comfyui: false,
    claude: false,
    printify: false,
    shopify: false
  };

  try {
    const orchestrator = createOrchestrator();

    // Test ComfyUI
    try {
      const comfyuiHealth = await fetch(`${process.env.COMFYUI_API_URL}/system_stats`);
      results.comfyui = comfyuiHealth.ok;
    } catch (error) {
      results.comfyui = false;
    }

    // Test Claude (basic check)
    results.claude = !!process.env.ANTHROPIC_API_KEY;

    // Test Printify
    if (process.env.PRINTIFY_API_KEY && process.env.PRINTIFY_SHOP_ID) {
      try {
        const printifyHealth = await fetch(
          `https://api.printify.com/v1/shops/${process.env.PRINTIFY_SHOP_ID}/products.json?page=1&limit=1`,
          {
            headers: {
              'Authorization': `Bearer ${process.env.PRINTIFY_API_KEY}`
            }
          }
        );
        results.printify = printifyHealth.ok;
      } catch (error) {
        results.printify = false;
      }
    }

    // Test Shopify
    if (process.env.SHOPIFY_STORE_URL && process.env.SHOPIFY_ACCESS_TOKEN) {
      try {
        const shopifyHealth = await fetch(
          `https://${process.env.SHOPIFY_STORE_URL}/admin/api/${process.env.SHOPIFY_API_VERSION || '2024-01'}/shop.json`,
          {
            headers: {
              'X-Shopify-Access-Token': process.env.SHOPIFY_ACCESS_TOKEN
            }
          }
        );
        results.shopify = shopifyHealth.ok;
      } catch (error) {
        results.shopify = false;
      }
    }

    res.json(results);
  } catch (error) {
    res.status(500).json({ error: error instanceof Error ? error.message : 'Unknown error' });
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 POD Studio API Server running on port ${PORT}`);
  console.log(`📊 Health check: http://localhost:${PORT}/health`);
  console.log(`🔧 Config test: http://localhost:${PORT}/api/config/test`);
  console.log('\nEnvironment:');
  console.log(`  ComfyUI: ${process.env.COMFYUI_API_URL || 'NOT CONFIGURED'}`);
  console.log(`  Claude API: ${process.env.ANTHROPIC_API_KEY ? 'CONFIGURED' : 'NOT CONFIGURED'}`);
  console.log(`  Printify: ${process.env.PRINTIFY_API_KEY ? 'CONFIGURED' : 'NOT CONFIGURED'}`);
  console.log(`  Shopify: ${process.env.SHOPIFY_STORE_URL ? 'CONFIGURED' : 'NOT CONFIGURED'}`);
});

export default app;
