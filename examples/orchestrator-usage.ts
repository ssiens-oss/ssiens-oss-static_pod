/**
 * POD Pipeline Orchestrator - Usage Examples
 *
 * This file demonstrates how to use the improved orchestrator
 * with retry logic, circuit breakers, and parallel processing.
 */

import { Orchestrator } from '../services/orchestrator';

// ============================================================================
// Example 1: Basic Configuration
// ============================================================================

const orchestrator = new Orchestrator({
  comfyui: {
    apiUrl: process.env.COMFYUI_API_URL || 'http://localhost:8188',
    outputDir: '/workspace/comfyui/output',
    timeout: 300000,           // 5 minutes
    maxRetries: 3,             // Retry failed operations
    pollInterval: 2000,        // Start with 2s polling
    enableCircuitBreaker: true // Enable circuit breaker
  },
  claude: {
    apiKey: process.env.ANTHROPIC_API_KEY!
  },
  storage: {
    type: 'local',
    basePath: '/workspace/storage'
  },
  printify: {
    apiKey: process.env.PRINTIFY_API_KEY!,
    shopId: process.env.PRINTIFY_SHOP_ID!,
    maxRetries: 3,
    enableCircuitBreaker: true,
    enableCache: true
  },
  shopify: {
    storeUrl: process.env.SHOPIFY_STORE_URL!,
    accessToken: process.env.SHOPIFY_ACCESS_TOKEN!
  },
  options: {
    enabledPlatforms: ['printify', 'shopify'],
    autoPublish: true,
    tshirtPrice: 19.99,
    hoodiePrice: 34.99
  }
});

// ============================================================================
// Example 2: Run Pipeline with Prompt
// ============================================================================

async function runBasicPipeline() {
  try {
    const result = await orchestrator.run({
      prompt: 'A majestic dragon in cyberpunk style',
      productTypes: ['tshirt', 'hoodie'],
      count: 1,
      autoPublish: true
    });

    console.log('Pipeline Result:', {
      success: result.success,
      imagesGenerated: result.generatedImages.length,
      productsCreated: result.products.length,
      totalTime: `${(result.totalTime / 1000).toFixed(2)}s`,
      errors: result.errors
    });

    // Display created products
    result.products.forEach(product => {
      console.log(`✓ ${product.platform}: ${product.url}`);
    });

  } catch (error) {
    console.error('Pipeline failed:', error);
  }
}

// ============================================================================
// Example 3: Generate with Custom Theme
// ============================================================================

async function runThemedPipeline() {
  const result = await orchestrator.run({
    theme: 'nature',
    style: 'watercolor',
    niche: 'wildlife',
    productTypes: ['tshirt'],
    count: 3,
    autoPublish: false // Don't auto-publish, review first
  });

  console.log(`Generated ${result.generatedImages.length} images`);

  return result;
}

// ============================================================================
// Example 4: Monitor Pipeline Health
// ============================================================================

async function monitorHealth() {
  // Check overall health
  const health = await orchestrator.getHealth();

  console.log('Pipeline Health:', {
    healthy: health.healthy,
    issues: health.issues
  });

  if (!health.healthy) {
    console.warn('⚠️  Pipeline has issues:', health.issues);
  }

  // Get detailed statistics
  const stats = await orchestrator.getStats();

  console.log('Pipeline Statistics:', {
    totalRuns: stats.pipeline.totalRuns,
    successRate: stats.pipeline.successRate,
    totalProducts: stats.pipeline.totalProducts,
    averageProductsPerRun: stats.pipeline.averageProductsPerRun
  });

  // Check circuit breakers
  console.log('Circuit Breakers:', stats.circuitBreakers);

  // Check service health
  console.log('Services:', {
    comfyui: stats.services.comfyui.healthy,
    printify: stats.services.printify.enabled,
    shopify: stats.services.shopify.enabled
  });
}

// ============================================================================
// Example 5: Handle Errors Gracefully
// ============================================================================

async function runWithErrorHandling() {
  try {
    const result = await orchestrator.run({
      prompt: 'Epic fantasy landscape',
      productTypes: ['tshirt', 'hoodie'],
      count: 1,
      autoPublish: true
    });

    // Check for partial success
    if (result.success && result.errors.length > 0) {
      console.log('✓ Pipeline succeeded with warnings:');
      result.errors.forEach(error => console.warn('  -', error));
    }

    // Check if any products were created
    if (result.products.length === 0) {
      console.error('❌ No products were created');
      console.error('Errors:', result.errors);
      return;
    }

    // Success!
    console.log(`✅ Created ${result.products.length} products`);

  } catch (error) {
    console.error('❌ Pipeline failed completely:', error);
  }
}

// ============================================================================
// Example 6: Batch Processing with Error Recovery
// ============================================================================

async function runBatchPipeline() {
  const prompts = [
    'Mystical forest scene',
    'Futuristic city skyline',
    'Abstract geometric patterns',
    'Vintage botanical illustration',
    'Space exploration theme'
  ];

  const results = [];

  for (const prompt of prompts) {
    console.log(`\nProcessing: ${prompt}`);

    try {
      const result = await orchestrator.run({
        prompt,
        productTypes: ['tshirt'],
        count: 1,
        autoPublish: true
      });

      if (result.success) {
        console.log(`✓ Success: ${result.products.length} products`);
        results.push({ prompt, success: true, result });
      } else {
        console.warn(`⚠️  Partial failure: ${result.errors.length} errors`);
        results.push({ prompt, success: false, errors: result.errors });
      }

    } catch (error) {
      console.error(`❌ Failed: ${error}`);
      results.push({ prompt, success: false, error: String(error) });
    }

    // Small delay between batches to avoid overwhelming services
    await new Promise(resolve => setTimeout(resolve, 2000));
  }

  // Summary
  const successful = results.filter(r => r.success).length;
  console.log(`\n📊 Batch Summary: ${successful}/${prompts.length} succeeded`);

  return results;
}

// ============================================================================
// Example 7: Reset Statistics
// ============================================================================

function resetStats() {
  orchestrator.resetStats();
  console.log('📊 Statistics reset');
}

// ============================================================================
// Example 8: Custom Logging
// ============================================================================

orchestrator.setLogger((message, type) => {
  const timestamp = new Date().toISOString();
  const emoji = {
    INFO: 'ℹ️',
    SUCCESS: '✅',
    WARNING: '⚠️',
    ERROR: '❌'
  }[type] || '•';

  console.log(`[${timestamp}] ${emoji} ${message}`);
});

// ============================================================================
// Export Examples
// ============================================================================

export {
  runBasicPipeline,
  runThemedPipeline,
  monitorHealth,
  runWithErrorHandling,
  runBatchPipeline,
  resetStats
};

// ============================================================================
// Main Execution (if run directly)
// ============================================================================

if (require.main === module) {
  (async () => {
    console.log('🚀 POD Pipeline Examples\n');

    // Example: Monitor health
    await monitorHealth();

    // Example: Run basic pipeline
    console.log('\n--- Running Basic Pipeline ---');
    await runBasicPipeline();

    // Example: Check stats after run
    console.log('\n--- Final Statistics ---');
    await monitorHealth();
  })();
}
