#!/usr/bin/env node
/**
 * Test script for RunPod Serverless integration
 * Usage: node test-runpod.mjs
 */

import { readFileSync } from 'fs';

// Simple .env parser
function loadEnv() {
  try {
    const envContent = readFileSync('.env', 'utf-8');
    const lines = envContent.split('\n');

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('#')) continue;

      const [key, ...valueParts] = trimmed.split('=');
      const value = valueParts.join('=').trim();

      if (key && value) {
        process.env[key] = value;
      }
    }
  } catch (error) {
    console.error('Warning: Could not load .env file:', error.message);
  }
}

loadEnv();

// Simple RunPod API test
async function testRunPodConnection() {
  const apiKey = process.env.RUNPOD_API_KEY;
  const endpointId = process.env.RUNPOD_ENDPOINT_ID;

  console.log('🚀 Testing RunPod Serverless Connection...\n');

  if (!apiKey || !endpointId) {
    console.error('❌ Missing credentials:');
    console.error('   RUNPOD_API_KEY:', apiKey ? '✓ Set' : '✗ Missing');
    console.error('   RUNPOD_ENDPOINT_ID:', endpointId ? '✓ Set' : '✗ Missing');
    console.error('\nPlease check your .env file');
    process.exit(1);
  }

  console.log('✓ Credentials found:');
  console.log('  Endpoint ID:', endpointId);
  console.log('  API Key:', apiKey.substring(0, 15) + '...\n');

  const baseUrl = `https://api.runpod.ai/v2/${endpointId}`;

  // Test 1: Health Check
  console.log('🏥 Test 1: Health Check');
  try {
    const response = await fetch(`${baseUrl}/health`, {
      headers: {
        'Authorization': `Bearer ${apiKey}`
      }
    });

    if (response.ok) {
      console.log('✅ Health check passed!');
      const data = await response.json();
      console.log('   Response:', JSON.stringify(data, null, 2));
    } else {
      console.log('⚠️  Health check returned:', response.status, response.statusText);
      const text = await response.text();
      console.log('   Response:', text);
    }
  } catch (error) {
    console.log('❌ Health check failed:', error.message);
  }

  console.log('\n');

  // Test 2: Simple Image Generation
  console.log('🎨 Test 2: Simple Image Generation');
  console.log('   Generating image with prompt: "a beautiful sunset over mountains"');

  const workflow = {
    "3": {
      "inputs": {
        "seed": 42,
        "steps": 20,
        "cfg": 7,
        "sampler_name": "euler",
        "scheduler": "normal",
        "denoise": 1,
        "model": ["4", 0],
        "positive": ["6", 0],
        "negative": ["7", 0],
        "latent_image": ["5", 0]
      },
      "class_type": "KSampler"
    },
    "4": {
      "inputs": {
        "ckpt_name": "sd_xl_base_1.0.safetensors"
      },
      "class_type": "CheckpointLoaderSimple"
    },
    "5": {
      "inputs": {
        "width": 1024,
        "height": 1024,
        "batch_size": 1
      },
      "class_type": "EmptyLatentImage"
    },
    "6": {
      "inputs": {
        "text": "a beautiful sunset over mountains, digital art, highly detailed",
        "clip": ["4", 1]
      },
      "class_type": "CLIPTextEncode"
    },
    "7": {
      "inputs": {
        "text": "text, watermark, low quality, worst quality",
        "clip": ["4", 1]
      },
      "class_type": "CLIPTextEncode"
    },
    "8": {
      "inputs": {
        "samples": ["3", 0],
        "vae": ["4", 2]
      },
      "class_type": "VAEDecode"
    },
    "9": {
      "inputs": {
        "filename_prefix": "ComfyUI",
        "images": ["8", 0]
      },
      "class_type": "SaveImage"
    }
  };

  try {
    console.log('   Submitting job...');
    const response = await fetch(`${baseUrl}/run`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: JSON.stringify({
        input: {
          workflow: workflow,
          images: []
        }
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.log(`❌ Job submission failed (${response.status}):`, errorText);
      return;
    }

    const { id: jobId } = await response.json();
    console.log('✅ Job submitted! Job ID:', jobId);

    // Poll for completion
    console.log('   Polling for completion...');
    let attempts = 0;
    const maxAttempts = 60; // 2 minutes max

    while (attempts < maxAttempts) {
      await new Promise(resolve => setTimeout(resolve, 2000)); // Wait 2 seconds

      const statusResponse = await fetch(`${baseUrl}/status/${jobId}`, {
        headers: {
          'Authorization': `Bearer ${apiKey}`
        }
      });

      if (!statusResponse.ok) {
        console.log('⚠️  Status check failed:', statusResponse.status);
        break;
      }

      const status = await statusResponse.json();
      attempts++;

      console.log(`   [${attempts}] Status: ${status.status}${status.status === 'IN_PROGRESS' ? ' (generating...)' : ''}`);

      if (status.status === 'COMPLETED') {
        console.log('✅ Generation completed!');
        console.log('   Output:', JSON.stringify(status.output, null, 2));

        if (status.output?.images && status.output.images.length > 0) {
          console.log('\n🖼️  Generated images:');
          status.output.images.forEach((img, i) => {
            console.log(`   ${i + 1}. ${img}`);
          });
        }
        break;
      }

      if (status.status === 'FAILED') {
        console.log('❌ Generation failed!');
        console.log('   Error:', status.error || 'Unknown error');
        break;
      }
    }

    if (attempts >= maxAttempts) {
      console.log('⏱️  Timeout: Generation took too long');
    }

  } catch (error) {
    console.log('❌ Generation test failed:', error.message);
  }

  console.log('\n✅ Test completed!');
}

// Run the test
testRunPodConnection().catch(console.error);
