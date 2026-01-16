/**
 * RunPod Serverless Usage Examples
 *
 * This file demonstrates how to use the RunPod Serverless integration
 * for production image generation.
 */

import { imageGenService } from '../services/imageGeneration';

/**
 * Example 1: Basic Image Generation
 */
async function basicGeneration() {
  console.log('=== Example 1: Basic Image Generation ===');

  const result = await imageGenService.generate({
    prompt: 'a majestic dragon flying over a medieval castle, fantasy art, highly detailed',
    width: 1024,
    height: 1024,
    steps: 25,
    cfg_scale: 7.5
  });

  if (result.status === 'completed') {
    console.log('✅ Generation successful!');
    console.log('Images:', result.images);
    console.log('Job ID:', result.jobId);
  } else {
    console.error('❌ Generation failed:', result.error);
  }
}

/**
 * Example 2: Batch Generation for POD Designs
 */
async function batchGeneration() {
  console.log('\n=== Example 2: Batch POD Design Generation ===');

  const designs = [
    {
      prompt: 'minimalist geometric mountain design, vector art, clean lines',
      width: 4500,
      height: 5400 // Standard POD dimensions
    },
    {
      prompt: 'retro wave sunset with palm trees, synthwave aesthetic, vibrant colors',
      width: 4500,
      height: 5400
    },
    {
      prompt: 'abstract watercolor galaxy, cosmic nebula, purple and blue tones',
      width: 4500,
      height: 5400
    }
  ];

  console.log(`Generating ${designs.length} designs...`);

  const results = await imageGenService.generateBatch(designs);

  results.forEach((result, index) => {
    if (result.status === 'completed') {
      console.log(`✅ Design ${index + 1}: Success (${result.images.length} images)`);
    } else {
      console.log(`❌ Design ${index + 1}: Failed - ${result.error}`);
    }
  });
}

/**
 * Example 3: Health Check and Service Detection
 */
async function checkService() {
  console.log('\n=== Example 3: Service Health Check ===');

  const serviceType = imageGenService.getServiceType();
  console.log('Active Service:', serviceType === 'runpod' ? 'RunPod Serverless' : 'Local ComfyUI');

  const isHealthy = await imageGenService.healthCheck();
  console.log('Health Status:', isHealthy ? '✅ Healthy' : '❌ Unhealthy');

  if (serviceType === 'runpod') {
    console.log('💡 Using production RunPod Serverless endpoint');
  } else {
    console.log('💡 Using local ComfyUI (set RUNPOD_API_KEY and RUNPOD_ENDPOINT_ID for production)');
  }
}

/**
 * Example 4: Controlled Generation with Seeds
 */
async function reproducibleGeneration() {
  console.log('\n=== Example 4: Reproducible Generation ===');

  const seed = 42; // Fixed seed for reproducibility

  const result1 = await imageGenService.generate({
    prompt: 'a serene Japanese garden with cherry blossoms',
    seed: seed,
    width: 1024,
    height: 1024,
    steps: 20
  });

  console.log('First generation:', result1.status);

  // Generate again with same seed - should produce identical result
  const result2 = await imageGenService.generate({
    prompt: 'a serene Japanese garden with cherry blossoms',
    seed: seed,
    width: 1024,
    height: 1024,
    steps: 20
  });

  console.log('Second generation:', result2.status);
  console.log('💡 Using the same seed produces identical images');
}

/**
 * Example 5: High-Quality Product Design Generation
 */
async function podProductDesign() {
  console.log('\n=== Example 5: High-Quality POD Product Design ===');

  const result = await imageGenService.generate({
    prompt: `premium streetwear graphic design,
            bold typography with "URBAN LEGENDS" text,
            graffiti style, vibrant colors,
            white background,
            print-ready, high resolution,
            centered composition`,
    width: 4500,  // Standard print width (15" at 300 DPI)
    height: 5400, // Standard print height (18" at 300 DPI)
    steps: 30,    // Higher quality
    cfg_scale: 8  // Stronger prompt adherence
  });

  if (result.status === 'completed') {
    console.log('✅ High-quality design generated!');
    console.log('Download URL:', result.images[0]);
    console.log('💡 Ready for Printify upload');
  }
}

/**
 * Example 6: Error Handling and Retry Logic
 */
async function robustGeneration() {
  console.log('\n=== Example 6: Error Handling ===');

  const maxRetries = 3;
  let attempt = 0;
  let result;

  while (attempt < maxRetries) {
    try {
      console.log(`Attempt ${attempt + 1}/${maxRetries}...`);

      result = await imageGenService.generate({
        prompt: 'futuristic cyberpunk cityscape at night',
        width: 1024,
        height: 1024
      });

      if (result.status === 'completed') {
        console.log('✅ Success on attempt', attempt + 1);
        break;
      } else {
        console.log('⚠️ Failed:', result.error);
        attempt++;

        if (attempt < maxRetries) {
          // Exponential backoff
          const waitTime = Math.pow(2, attempt) * 1000;
          console.log(`Waiting ${waitTime}ms before retry...`);
          await new Promise(resolve => setTimeout(resolve, waitTime));
        }
      }
    } catch (error) {
      console.error('❌ Error:', error);
      attempt++;
    }
  }

  if (result?.status !== 'completed') {
    console.error('❌ Failed after', maxRetries, 'attempts');
  }
}

/**
 * Main execution
 */
async function main() {
  console.log('🚀 RunPod Serverless Examples\n');

  try {
    // Run all examples
    await checkService();
    await basicGeneration();
    await reproducibleGeneration();
    await podProductDesign();
    await batchGeneration();
    await robustGeneration();

    console.log('\n✅ All examples completed!');
  } catch (error) {
    console.error('❌ Error running examples:', error);
  }
}

// Uncomment to run examples
// main();

export {
  basicGeneration,
  batchGeneration,
  checkService,
  reproducibleGeneration,
  podProductDesign,
  robustGeneration
};
