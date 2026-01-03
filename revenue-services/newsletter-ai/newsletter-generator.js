#!/usr/bin/env node

/**
 * AI Newsletter Generator
 * Automated newsletter research, writing, and scheduling
 *
 * Revenue Model:
 * - Free tier: 100 subscribers
 * - $5/month: Up to 1,000 subscribers
 * - $20/month: Up to 10,000 subscribers
 * - $50/month: Up to 50,000 subscribers
 *
 * Target: 1,000 paying subscribers = $5k-50k/month
 */

const fs = require("fs");
const path = require("path");
const AI_AGENT_URL = process.env.AI_AGENT_URL || "http://localhost:8787";

class NewsletterGenerator {
  constructor(config) {
    this.config = config;
    this.outputDir = config.outputDir || "./newsletters";

    if (!fs.existsSync(this.outputDir)) {
      fs.mkdirSync(this.outputDir, { recursive: true });
    }
  }

  async generateIssue(topic, date = new Date()) {
    console.log(`\n📰 Generating newsletter: ${topic}`);
    console.log(`   Date: ${date.toLocaleDateString()}\n`);

    // Step 1: Research trending content
    const research = await this.researchTopic(topic);

    // Step 2: Create newsletter structure
    const structure = await this.createStructure(topic, research);

    // Step 3: Write full newsletter
    const newsletter = await this.writeNewsletter(structure);

    // Step 4: Generate subject lines
    const subjectLines = await this.generateSubjectLines(newsletter);

    // Step 5: Create email-ready HTML
    const html = await this.generateHTML(newsletter);

    const issue = {
      topic,
      date: date.toISOString(),
      research,
      structure,
      newsletter,
      subjectLines,
      html,
      metadata: {
        wordCount: newsletter.split(/\s+/).length,
        estimatedReadTime: Math.ceil(newsletter.split(/\s+/).length / 200),
        generatedAt: new Date().toISOString()
      }
    };

    // Save to file
    this.saveIssue(issue);

    return issue;
  }

  async researchTopic(topic) {
    console.log("  🔍 Researching trending content...");

    const response = await fetch(`${AI_AGENT_URL}/multi`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        role: "ARCH_AGENT",
        goal: `Research newsletter content for topic: ${topic}

Find:
1. Top 5 trending stories/updates in this niche from the past week
2. Key takeaways from each story
3. Why it matters to subscribers
4. Actionable insights

Focus on:
- Recent developments (last 7 days)
- High-value insights
- Practical applications
- Interesting angles

Provide detailed research with sources.`
      })
    });

    const result = await response.json();
    return result.final || result.critique;
  }

  async createStructure(topic, research) {
    console.log("  📋 Creating newsletter structure...");

    const response = await fetch(`${AI_AGENT_URL}/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        role: "ADS_AGENT",
        prompt: `Create engaging newsletter structure for: ${topic}

Based on research:
${research}

Create structure with:
1. Opening hook (2-3 sentences that grab attention)
2. Main Story #1 (headline + 100 words + key takeaway)
3. Main Story #2 (headline + 100 words + key takeaway)
4. Quick Hits (3-5 brief updates, 20-30 words each)
5. Tool/Resource of the Week
6. Actionable Tip
7. Closing CTA

Tone: ${this.config.tone || 'Professional but conversational'}
Target audience: ${this.config.audience || 'Professionals in the field'}

Provide detailed outline with section headers.`
      })
    });

    const result = await response.json();
    return result.result;
  }

  async writeNewsletter(structure) {
    console.log("  ✍️  Writing full newsletter...");

    const response = await fetch(`${AI_AGENT_URL}/multi`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        role: "ADS_AGENT",
        goal: `Write complete newsletter based on this structure:

${structure}

Requirements:
- Engaging and scannable
- Mix of longer and shorter sections
- Include relevant emojis sparingly
- Conversational but professional
- Clear value in every section
- Strong CTA at the end

Format in Markdown.

Add:
- [Opening Hook]
- [Main Stories with headlines]
- [Quick Hits section]
- [Tool/Resource]
- [Actionable Tip]
- [Closing + CTA]

Make it compelling and valuable to read.`
      })
    });

    const result = await response.json();
    return result.final || result.critique;
  }

  async generateSubjectLines(newsletter) {
    console.log("  📧 Generating subject line variants...");

    const response = await fetch(`${AI_AGENT_URL}/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        role: "ADS_AGENT",
        prompt: `Generate 10 email subject line variants for this newsletter:

${newsletter.substring(0, 500)}...

Subject line requirements:
- 40-60 characters optimal
- Create curiosity without clickbait
- Highlight main value
- Test different angles

Provide 10 variants:
1. Curiosity-driven
2. Benefit-focused
3. Number-based
4. Question format
5. Urgency/FOMO
6. Straightforward
7. Controversial take
8. Insider language
9. Personal angle
10. Best performing (your recommendation)

Format as JSON array with "type" and "subject" fields.`
      })
    });

    const result = await response.json();
    return result.result;
  }

  async generateHTML(newsletter) {
    console.log("  🎨 Creating email HTML...");

    // Convert markdown to basic HTML
    let html = newsletter
      .replace(/^# (.*$)/gm, '<h1 style="color: #333; font-size: 24px; margin: 20px 0 10px 0;">$1</h1>')
      .replace(/^## (.*$)/gm, '<h2 style="color: #555; font-size: 20px; margin: 15px 0 8px 0;">$1</h2>')
      .replace(/^### (.*$)/gm, '<h3 style="color: #666; font-size: 18px; margin: 12px 0 6px 0;">$1</h3>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n\n/g, '</p><p>')
      .replace(/\n/g, '<br>');

    return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
  <div style="background: #f9f9f9; border-radius: 8px; padding: 20px; margin-bottom: 20px;">
    <p style="margin: 0; color: #666; font-size: 14px;">
      ${this.config.newsletterName || 'AI Newsletter'} • ${new Date().toLocaleDateString()}
    </p>
  </div>

  <div style="margin: 20px 0;">
    <p>${html}</p>
  </div>

  <div style="background: #f9f9f9; border-radius: 8px; padding: 20px; margin-top: 30px; text-align: center;">
    <p style="margin: 0; color: #666; font-size: 12px;">
      You're receiving this because you subscribed to ${this.config.newsletterName || 'our newsletter'}.
      <br><a href="{{unsubscribe_url}}" style="color: #999;">Unsubscribe</a>
    </p>
  </div>
</body>
</html>
    `.trim();
  }

  saveIssue(issue) {
    const filename = `${issue.date.split('T')[0]}-${issue.topic.toLowerCase().replace(/\s+/g, '-')}.json`;
    const filepath = path.join(this.outputDir, filename);

    fs.writeFileSync(filepath, JSON.stringify(issue, null, 2));
    console.log(`\n  💾 Saved: ${filepath}`);

    // Also save HTML version
    const htmlPath = filepath.replace('.json', '.html');
    fs.writeFileSync(htmlPath, issue.html);
    console.log(`  💾 Saved: ${htmlPath}`);
  }

  async generateWeeklySchedule(topics) {
    console.log("\n📅 Generating weekly newsletter schedule...\n");

    const issues = [];

    for (let i = 0; i < topics.length; i++) {
      const date = new Date();
      date.setDate(date.getDate() + i);

      const issue = await this.generateIssue(topics[i], date);
      issues.push(issue);

      console.log(`✅ Issue ${i + 1}/${topics.length} complete\n`);
    }

    return {
      schedule: issues,
      summary: {
        total: issues.length,
        avgWordCount: Math.round(
          issues.reduce((sum, i) => sum + i.metadata.wordCount, 0) / issues.length
        ),
        avgReadTime: Math.round(
          issues.reduce((sum, i) => sum + i.metadata.estimatedReadTime, 0) / issues.length
        )
      }
    };
  }
}

// CLI Usage
if (require.main === module) {
  const config = {
    newsletterName: "AI Automation Weekly",
    tone: "Professional but friendly",
    audience: "Developers and entrepreneurs interested in AI",
    outputDir: "./newsletters"
  };

  const generator = new NewsletterGenerator(config);

  const weeklyTopics = [
    "Latest AI coding assistants and productivity tools",
    "Breaking news in AI automation and workflows",
    "Top AI marketing and content creation updates",
    "AI agents and autonomous systems developments",
    "Weekend roundup: Best AI tools and tutorials"
  ];

  console.log("🚀 AI Newsletter Generator\n");
  console.log(`Generating ${weeklyTopics.length} newsletters...\n`);

  generator.generateWeeklySchedule(weeklyTopics)
    .then(schedule => {
      console.log("\n" + "=".repeat(60));
      console.log("✅ WEEKLY SCHEDULE COMPLETE");
      console.log("=".repeat(60));
      console.log(`Total Issues: ${schedule.summary.total}`);
      console.log(`Avg Word Count: ${schedule.summary.avgWordCount}`);
      console.log(`Avg Read Time: ${schedule.summary.avgReadTime} minutes`);
      console.log("\n📧 Ready to send via email platform (Mailchimp, ConvertKit, etc.)");
      console.log("\n💰 Revenue Potential:");
      console.log("  1,000 subscribers @ $5/month = $5,000/month");
      console.log("  10,000 subscribers @ $20/month = $200,000/month");
    })
    .catch(console.error);
}

module.exports = NewsletterGenerator;
