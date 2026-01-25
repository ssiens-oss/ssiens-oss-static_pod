#!/usr/bin/env node
/**
 * Simple RunPod Serverless Test using /runsync
 * Usage: node test-runpod-sync.mjs
 */

import { readFileSync } from 'fs';
import https from 'https';

// Load .env
function loadEnv() {
  try {
    const envContent = readFileSync('.env', 'utf-8');
    for (const line of envContent.split('\n')) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('#')) continue;
      const [key, ...valueParts] = trimmed.split('=');
      const value = valueParts.join('=').trim();
      if (key && value) process.env[key] = value;
    }
  } catch (error) {
    console.error('Could not load .env:', error.message);
  }
}

loadEnv();

const apiKey = process.env.RUNPOD_API_KEY;
const endpointId = process.env.RUNPOD_ENDPOINT_ID;

console.log('🚀 Testing RunPod Serverless with /runsync...\n');

if (!apiKey || !endpointId) {
  console.error('❌ Missing credentials in .env file');
  console.error('   RUNPOD_API_KEY:', apiKey ? '✓' : '✗');
  console.error('   RUNPOD_ENDPOINT_ID:', endpointId ? '✓' : '✗');
  process.exit(1);
}

console.log('✓ Credentials loaded:');
console.log('  Endpoint ID:', endpointId);
console.log('  API Key:', apiKey.substring(0, 20) + '...\n');

// Build minimal ComfyUI workflow
const workflow = {
  "3": {
    "inputs": {
      "seed": 42,
      "steps": 15,
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
    "inputs": { "ckpt_name": "sd_xl_base_1.0.safetensors" },
    "class_type": "CheckpointLoaderSimple"
  },
  "5": {
    "inputs": { "width": 512, "height": 512, "batch_size": 1 },
    "class_type": "EmptyLatentImage"
  },
  "6": {
    "inputs": { "text": "a beautiful sunset over mountains", "clip": ["4", 1] },
    "class_type": "CLIPTextEncode"
  },
  "7": {
    "inputs": { "text": "text, watermark, low quality", "clip": ["4", 1] },
    "class_type": "CLIPTextEncode"
  },
  "8": {
    "inputs": { "samples": ["3", 0], "vae": ["4", 2] },
    "class_type": "VAEDecode"
  },
  "9": {
    "inputs": { "filename_prefix": "test", "images": ["8", 0] },
    "class_type": "SaveImage"
  }
};

const payload = JSON.stringify({
  input: {
    workflow: workflow,
    images: []
  }
});

const options = {
  hostname: 'api.runpod.ai',
  port: 443,
  path: `/v2/${endpointId}/runsync`,
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${apiKey}`,
    'Content-Length': Buffer.byteLength(payload)
  }
};

console.log('🎨 Generating image (synchronous mode)...');
console.log('   Endpoint:', `https://api.runpod.ai/v2/${endpointId}/runsync`);
console.log('   This will wait for completion (may take 30-60 seconds)...\n');

const req = https.request(options, (res) => {
  let data = '';

  res.on('data', (chunk) => {
    data += chunk;
  });

  res.on('end', () => {
    console.log('📥 Response received!\n');
    console.log('Status Code:', res.statusCode);
    console.log('Headers:', JSON.stringify(res.headers, null, 2), '\n');

    if (res.statusCode === 200) {
      try {
        const result = JSON.parse(data);
        console.log('✅ Generation successful!\n');
        console.log('Response:', JSON.stringify(result, null, 2));

        if (result.output && result.output.images) {
          console.log('\n🖼️  Generated Images:');
          result.output.images.forEach((img, i) => {
            console.log(`   ${i + 1}. ${img}`);
          });
        }
      } catch (e) {
        console.log('Raw response:', data);
      }
    } else {
      console.log('❌ Request failed');
      console.log('Response:', data);
    }
  });
});

req.on('error', (error) => {
  console.error('❌ Request error:', error.message);
  console.error('   This might be a network/firewall issue');
});

req.write(payload);
req.end();
