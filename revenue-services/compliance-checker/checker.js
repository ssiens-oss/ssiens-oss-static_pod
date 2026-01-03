#!/usr/bin/env node

/**
 * Compliance-as-a-Service Checker
 * Automated compliance checking for e-commerce, content, code
 *
 * Revenue Model:
 * - One-time audit: $500-2k
 * - Monthly monitoring: $200-1k/month
 * - Per-check API: $10-50/check
 *
 * Target: 20 monthly clients = $4k-20k MRR
 */

const AI_AGENT_URL = process.env.AI_AGENT_URL || "http://localhost:8787";

class ComplianceChecker {

  async checkTikTokShop(product) {
    console.log(`\n⚖️  Checking TikTok Shop Compliance: ${product.title || product.name}`);

    const response = await fetch(`${AI_AGENT_URL}/multi`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        role: "COMPLIANCE_AGENT",
        goal: `Comprehensive TikTok Shop compliance check:

PRODUCT DETAILS:
${JSON.stringify(product, null, 2)}

CHECK FOR:

1. PROHIBITED ITEMS
- Weapons, ammunition, weapon accessories
- Adult content, sexual wellness
- Supplements, vitamins, CBD
- Tobacco, vapes, drug paraphernalia
- Live animals
- Medical devices
- Counterfeit/replica items

2. FULFILLMENT RESTRICTIONS
- External fulfillment (Printify, other POD) = RESTRICTED
- Must use TikTok-approved warehouses OR
- Ship within 7 days with tracking

3. SHIPPING REQUIREMENTS
- Max 7 business days delivery
- Tracking number required
- No P.O. boxes for some categories

4. CONTENT POLICY
- No misleading claims
- No before/after medical claims
- No income/earnings claims
- Proper disclaimers

5. PRICING COMPLIANCE
- No fake discounts
- Price must match description
- No hidden fees

RESPOND WITH JSON:
{
  "verdict": "APPROVED" | "REJECTED" | "REVIEW_NEEDED",
  "risk_level": "low" | "medium" | "high",
  "issues": [{
    "category": "Prohibited Item" | "Fulfillment" | "Shipping" | "Content" | "Pricing",
    "severity": "critical" | "warning" | "info",
    "description": "...",
    "fix": "..."
  }],
  "recommendations": ["..."],
  "estimated_fix_time": "immediate | 1-3 days | requires supplier change"
}`
      })
    });

    const result = await response.json();
    return this.parseComplianceResult(result.final || result.critique);
  }

  async checkFTCCompliance(content) {
    console.log("\n📋 Checking FTC Compliance (Endorsements & Testimonials)");

    const response = await fetch(`${AI_AGENT_URL}/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        role: "COMPLIANCE_AGENT",
        prompt: `FTC Compliance Check for Marketing Content:

CONTENT:
${content}

CHECK FOR:

1. DISCLOSURE REQUIREMENTS
- Sponsored content must be clearly disclosed
- Affiliate links must be disclosed
- Material connections must be disclosed
- Disclosures must be clear and conspicuous

2. TESTIMONIAL RULES
- Must be from real customers
- Must represent typical results (or disclose if exceptional)
- No fake reviews
- Must have permission to use

3. HEALTH/EARNINGS CLAIMS
- No unsubstantiated health claims
- No guaranteed earnings claims
- Must have scientific backing for health claims
- Income disclaimers required

4. ENDORSEMENT RULES
- Influencers must disclose brand relationships
- No fake celebrity endorsements
- Must actually use the product

Respond with JSON verdict and specific violations.`
      })
    });

    const result = await response.json();
    return this.parseComplianceResult(result.result);
  }

  async checkGDPR(website) {
    console.log("\n🇪🇺 Checking GDPR Compliance");

    const response = await fetch(`${AI_AGENT_URL}/multi`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        role: "COMPLIANCE_AGENT",
        goal: `GDPR Compliance Audit for: ${website}

CHECK FOR:

1. CONSENT MANAGEMENT
- Cookie consent banner present
- Granular consent options
- Easy to decline
- Records of consent

2. PRIVACY POLICY
- What data is collected
- How it's used
- How long it's stored
- User rights explained
- Contact information

3. USER RIGHTS
- Right to access data
- Right to deletion
- Right to portability
- Right to object
- Response within 30 days

4. DATA PROCESSING
- Lawful basis for processing
- Data minimization
- Purpose limitation
- Security measures

5. THIRD-PARTY DATA SHARING
- List all third parties
- User consent for sharing
- Data processing agreements

Provide detailed compliance report with priority fixes.`
      })
    });

    const result = await response.json();
    return this.parseComplianceResult(result.final || result.critique);
  }

  async checkAccessibility(content) {
    console.log("\n♿ Checking ADA/WCAG Accessibility");

    const response = await fetch(`${AI_AGENT_URL}/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        role: "COMPLIANCE_AGENT",
        prompt: `Accessibility Compliance Check (WCAG 2.1 Level AA):

CONTENT/CODE:
${content}

CHECK FOR:

1. IMAGES
- Alt text present and descriptive
- Decorative images marked as such

2. COLOR/CONTRAST
- Sufficient color contrast (4.5:1 text, 3:1 large text)
- Info not conveyed by color alone

3. KEYBOARD NAVIGATION
- All interactive elements keyboard accessible
- Focus indicators visible
- Logical tab order

4. FORMS
- Labels associated with inputs
- Error messages clear and descriptive
- Required fields marked

5. MULTIMEDIA
- Captions for videos
- Transcripts for audio
- Audio descriptions if needed

6. HEADINGS/STRUCTURE
- Logical heading hierarchy (H1, H2, H3)
- Semantic HTML
- Skip links present

Provide specific violations and fixes.`
      })
    });

    const result = await response.json();
    return this.parseComplianceResult(result.result);
  }

  async checkCryptoCompliance(content) {
    console.log("\n🪙 Checking Crypto/Securities Compliance");

    const response = await fetch(`${AI_AGENT_URL}/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        role: "COMPLIANCE_AGENT",
        prompt: `Crypto/Securities Compliance Check:

CONTENT:
${content}

CHECK FOR:

1. INVESTMENT ADVICE DISCLAIMERS
- "Not financial advice" disclaimer
- Appropriate risk warnings
- No guarantees of returns

2. SECURITIES LAW (Howey Test)
- Not promoting unregistered securities
- No promises of profits
- Educational vs promotional

3. AML/KYC REFERENCES
- If accepting payments, mention KYC/AML
- Not facilitating illegal transactions

4. REGULATORY WARNINGS
- Appropriate for jurisdiction
- Mentions regulatory uncertainty

5. PROHIBITED CLAIMS
- No "guaranteed returns"
- No "risk-free" claims
- No specific price predictions

Severity: CRITICAL if violates securities laws.`
      })
    });

    const result = await response.json();
    return this.parseComplianceResult(result.result);
  }

  parseComplianceResult(resultText) {
    try {
      // Try to parse as JSON first
      const jsonMatch = resultText.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
    } catch (e) {
      // Not JSON, create structured response
    }

    // Fallback: parse text response
    const hasIssues = /REJECTED|CRITICAL|WARNING|VIOLATION/i.test(resultText);

    return {
      verdict: hasIssues ? "REVIEW_NEEDED" : "APPROVED",
      risk_level: hasIssues ? "medium" : "low",
      issues: this.extractIssues(resultText),
      rawReport: resultText
    };
  }

  extractIssues(text) {
    const issues = [];
    const lines = text.split('\n');

    for (const line of lines) {
      if (/CRITICAL|ERROR|VIOLATION|PROHIBITED/i.test(line)) {
        issues.push({
          severity: "critical",
          description: line.trim()
        });
      } else if (/WARNING|ISSUE|CONCERN/i.test(line)) {
        issues.push({
          severity: "warning",
          description: line.trim()
        });
      }
    }

    return issues;
  }

  generateReport(checks) {
    const criticalIssues = checks.filter(c =>
      c.issues?.some(i => i.severity === "critical")
    ).length;

    console.log("\n" + "=".repeat(60));
    console.log("📊 COMPLIANCE REPORT");
    console.log("=".repeat(60));
    console.log(`Total Checks: ${checks.length}`);
    console.log(`Critical Issues: ${criticalIssues}`);
    console.log(`Overall Status: ${criticalIssues > 0 ? '❌ FAILED' : '✅ PASSED'}`);
    console.log("=".repeat(60));

    return {
      summary: {
        total: checks.length,
        critical: criticalIssues,
        passed: checks.filter(c => c.verdict === "APPROVED").length
      },
      checks,
      billingAmount: this.calculateBilling(checks.length)
    };
  }

  calculateBilling(checkCount) {
    const basePrice = 50; // $50 per check
    const total = basePrice * checkCount;

    return {
      perCheck: basePrice,
      totalChecks: checkCount,
      subtotal: total,
      discount: total > 500 ? total * 0.2 : 0, // 20% off if >$500
      total: total > 500 ? total * 0.8 : total
    };
  }
}

// CLI Usage
if (require.main === module) {
  const checker = new ComplianceChecker();

  const sampleProduct = {
    title: "Vintage Streetwear Hoodie",
    description: "Premium quality hoodie with unique design. Ships in 3-5 business days.",
    category: "Apparel & Accessories",
    price: 39.99,
    supplier: "Printify (POD)",
    shippingTime: "3-5 business days",
    fulfillment: "external"
  };

  const sampleContent = `
    🔥 AMAZING OPPORTUNITY! 🔥

    This product will change your life! Guaranteed results in 30 days!

    I personally made $10,000 in my first month using this system!

    Click here to buy now! Limited time offer!

    #ad #sponsored
  `;

  async function runDemo() {
    console.log("🚀 Compliance Checker Demo\n");

    const checks = [];

    // Check 1: TikTok Shop
    const tiktokCheck = await checker.checkTikTokShop(sampleProduct);
    checks.push({ type: "TikTok Shop", ...tiktokCheck });

    // Check 2: FTC
    const ftcCheck = await checker.checkFTCCompliance(sampleContent);
    checks.push({ type: "FTC", ...ftcCheck });

    // Generate report
    const report = checker.generateReport(checks);

    console.log("\n💰 Billing:");
    console.log(`  ${report.billingAmount.totalChecks} checks @ $${report.billingAmount.perCheck} = $${report.billingAmount.subtotal}`);
    if (report.billingAmount.discount > 0) {
      console.log(`  Discount: -$${report.billingAmount.discount.toFixed(2)}`);
    }
    console.log(`  Total: $${report.billingAmount.total.toFixed(2)}`);
  }

  runDemo().catch(console.error);
}

module.exports = ComplianceChecker;
