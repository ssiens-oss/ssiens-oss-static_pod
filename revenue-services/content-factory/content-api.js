#!/usr/bin/env node

/**
 * Content Creation Factory API
 * High-volume, low-cost content generation service
 *
 * Revenue Model:
 * - Product descriptions: $5-20 each
 * - Blog articles: $50-200 each
 * - Social posts: $2-10 per post
 * - Bulk packages: 100 descriptions for $500-1000
 *
 * Target: 500 pieces/month = $2.5k-10k revenue
 */

const http = require("http");
const AI_AGENT_URL = process.env.AI_AGENT_URL || "http://localhost:8787";

class ContentFactory {
  async generateProductDescription(data) {
    const { productName, features, benefits, targetAudience, keywords } = data;

    const response = await fetch(`${AI_AGENT_URL}/chain`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        role: "ADS_AGENT",
        tasks: [
          `Create SEO-optimized product title for: ${productName}. Include keywords: ${keywords}`,
          `Write compelling 150-word product description focusing on benefits: ${benefits}`,
          `Generate 5 bullet points highlighting key features: ${features}`,
          `Create meta description (155 characters max) for SEO`,
          `Write 3 social media post variants (Twitter, Instagram, TikTok)`
        ]
      })
    });

    const result = await response.json();
    return this.parseChainResults(result);
  }

  async generateBlogArticle(data) {
    const { topic, keywords, targetLength, tone } = data;

    const response = await fetch(`${AI_AGENT_URL}/multi`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        role: "ADS_AGENT",
        goal: `Write comprehensive blog article:

Topic: ${topic}
Target Keywords: ${keywords}
Length: ${targetLength} words
Tone: ${tone}

Include:
- SEO-optimized title (H1)
- Meta description
- 3-5 H2 subheadings
- Introduction (100 words)
- Body with examples and data
- Conclusion with CTA
- 5 FAQ questions/answers

Format in Markdown.`
      })
    });

    const result = await response.json();
    return {
      article: result.final || result.critique,
      wordCount: (result.final || result.critique).split(/\s+/).length,
      estimatedReadTime: Math.ceil((result.final || result.critique).split(/\s+/).length / 200)
    };
  }

  async generateSocialPosts(data) {
    const { topic, platform, count, tone } = data;

    const platformSpecs = {
      twitter: "280 characters max, punchy hooks, hashtags",
      instagram: "125 characters first line, engaging caption, 10-15 hashtags",
      tiktok: "Video script 15-30 seconds, trending hooks, clear CTA",
      linkedin: "Professional tone, 150-200 words, thought leadership"
    };

    const response = await fetch(`${AI_AGENT_URL}/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        role: "ADS_AGENT",
        prompt: `Generate ${count} ${platform} posts about: ${topic}

Platform specs: ${platformSpecs[platform] || platformSpecs.instagram}
Tone: ${tone}

Each post should:
- Have a strong hook
- Include value/entertainment
- Have clear CTA
- Use relevant hashtags
- Be platform-optimized

Format as JSON array.`
      })
    });

    const result = await response.json();
    return result.result;
  }

  async generateEmailSequence(data) {
    const { product, sequenceType, emailCount } = data;

    const sequences = {
      welcome: "Welcome new subscribers, introduce brand",
      nurture: "Build relationship, provide value, soft sell",
      sales: "Convert leads to customers, overcome objections",
      reengagement: "Win back inactive customers"
    };

    const response = await fetch(`${AI_AGENT_URL}/multi`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        role: "ADS_AGENT",
        goal: `Create ${emailCount}-email ${sequenceType} sequence for: ${product}

Sequence goal: ${sequences[sequenceType]}

For each email provide:
1. Subject line (5 variants for A/B testing)
2. Preview text
3. Email body (300-500 words)
4. CTA
5. P.S. (if appropriate)

Format as JSON array of emails.`
      })
    });

    const result = await response.json();
    return result.final || result.critique;
  }

  async batchGenerate(items, type) {
    console.log(`📦 Batch processing ${items.length} ${type}s...`);

    const results = [];
    for (let i = 0; i < items.length; i++) {
      console.log(`  Processing ${i + 1}/${items.length}...`);

      let result;
      switch(type) {
        case 'product':
          result = await this.generateProductDescription(items[i]);
          break;
        case 'blog':
          result = await this.generateBlogArticle(items[i]);
          break;
        case 'social':
          result = await this.generateSocialPosts(items[i]);
          break;
        default:
          throw new Error(`Unknown type: ${type}`);
      }

      results.push({
        input: items[i],
        output: result,
        generatedAt: new Date().toISOString()
      });
    }

    return {
      totalProcessed: results.length,
      results,
      estimatedCost: results.length * 0.02, // ~$0.02 per piece
      billingAmount: this.calculateBilling(type, results.length)
    };
  }

  calculateBilling(type, count) {
    const pricing = {
      product: 10,  // $10 per description
      blog: 100,    // $100 per article
      social: 5     // $5 per post
    };

    const basePrice = pricing[type] * count;

    // Volume discounts
    let discount = 0;
    if (count >= 100) discount = 0.30;      // 30% off
    else if (count >= 50) discount = 0.20;  // 20% off
    else if (count >= 20) discount = 0.10;  // 10% off

    return {
      subtotal: basePrice,
      discount: basePrice * discount,
      total: basePrice * (1 - discount),
      perUnit: (basePrice * (1 - discount)) / count
    };
  }

  parseChainResults(chainResult) {
    const results = chainResult.results || [];
    return {
      title: results[0]?.result || "",
      description: results[1]?.result || "",
      bulletPoints: results[2]?.result || "",
      metaDescription: results[3]?.result || "",
      socialPosts: results[4]?.result || ""
    };
  }
}

// HTTP Server
const PORT = process.env.CONTENT_API_PORT || 8789;
const factory = new ContentFactory();

const server = http.createServer(async (req, res) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") {
    res.writeHead(204);
    return res.end();
  }

  if (req.method !== "POST") {
    res.writeHead(405);
    return res.end(JSON.stringify({ error: "Method not allowed" }));
  }

  let body = "";
  req.on("data", chunk => body += chunk);
  req.on("end", async () => {
    try {
      const data = JSON.parse(body);

      let result;
      switch (req.url) {
        case "/product":
          result = await factory.generateProductDescription(data);
          break;
        case "/blog":
          result = await factory.generateBlogArticle(data);
          break;
        case "/social":
          result = await factory.generateSocialPosts(data);
          break;
        case "/email":
          result = await factory.generateEmailSequence(data);
          break;
        case "/batch":
          result = await factory.batchGenerate(data.items, data.type);
          break;
        default:
          res.writeHead(404);
          return res.end(JSON.stringify({ error: "Endpoint not found" }));
      }

      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(JSON.stringify(result));
    } catch (err) {
      console.error("Error:", err);
      res.writeHead(500);
      res.end(JSON.stringify({ error: err.message }));
    }
  });
});

server.listen(PORT, () => {
  console.log(`\n💼 Content Factory API running on http://localhost:${PORT}`);
  console.log("\nEndpoints:");
  console.log("  POST /product - Generate product descriptions");
  console.log("  POST /blog    - Generate blog articles");
  console.log("  POST /social  - Generate social media posts");
  console.log("  POST /email   - Generate email sequences");
  console.log("  POST /batch   - Batch process multiple items");
  console.log("\n💰 Pricing:");
  console.log("  Product descriptions: $10 each");
  console.log("  Blog articles: $100 each");
  console.log("  Social posts: $5 each");
  console.log("  Volume discounts: 10% (20+), 20% (50+), 30% (100+)");
  console.log("");
});

module.exports = ContentFactory;
