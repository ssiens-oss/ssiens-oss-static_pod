

# AI Code Review Pro - GitHub Action

> Multi-agent AI code review with GPT + Claude collaboration

## Features

- 🤖 **Dual AI Review**: GPT-4 + Claude Sonnet work together
- 🧠 **Multi-Agent Reasoning**: Plan → Execute → Critique pattern
- 🔒 **Security Focus**: Detects vulnerabilities, injection attacks, OWASP issues
- ⚡ **Auto-Escalation**: GPT reviews first, Claude verifies uncertain findings
- 💰 **Cost Optimized**: Budget guards prevent runaway spend
- 📊 **Detailed Reports**: Inline comments + PR summary

## Quick Start

### 1. Add to Your Workflow

Create `.github/workflows/ai-review.yml`:

```yaml
name: AI Code Review

on: [pull_request]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: AI Code Review
        uses: staticwaves/ai-code-review-pro@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          openai_api_key: ${{ secrets.OPENAI_API_KEY }}
          review_mode: 'multi'
          auto_comment: 'true'
```

### 2. Add API Keys

Go to **Settings → Secrets → Actions** and add:
- `ANTHROPIC_API_KEY`
- `OPENAI_API_KEY`

### 3. Open a PR

AI will automatically review and comment with findings.

## Configuration

### Review Modes

**`single`** - Single-pass review (GPT only, fastest, cheapest)
```yaml
review_mode: 'single'
# Cost: ~$0.01 per PR
# Time: ~30 seconds
```

**`multi`** - Multi-agent review (Plan → Execute → Critique)
```yaml
review_mode: 'multi'
# Cost: ~$0.06 per PR
# Time: ~2 minutes
# Best for: Critical PRs, production code
```

**`auto`** - Smart mode (escalates based on changes)
```yaml
review_mode: 'auto'
# Uses 'single' for minor changes
# Uses 'multi' for security-sensitive changes
# Cost: $0.01-0.06 per PR
```

### Advanced Options

```yaml
- uses: staticwaves/ai-code-review-pro@v1
  with:
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    openai_api_key: ${{ secrets.OPENAI_API_KEY }}

    # Review depth
    review_mode: 'multi'

    # Auto-comment on PR
    auto_comment: 'true'

    # Run compliance checks (FTC, GDPR, accessibility)
    check_compliance: 'true'

    # Budget limit (prevents overspend)
    budget_limit: '10'

    # Files to exclude
    exclude_paths: 'dist/**, *.min.js, *.lock'

    # Minimum severity to report
    min_severity: 'medium'
```

## Example Output

### PR Comment

```markdown
## 🤖 AI Code Review

**Verdict:** REQUEST_CHANGES
**Risk Level:** 🔴 HIGH
**Issues Found:** 3

### 🔴 Critical Issues

**SQL Injection Vulnerability** `src/api/users.js:42`
```javascript
const query = `SELECT * FROM users WHERE id = ${userId}`;
```
**Fix:** Use parameterized queries
```javascript
const query = 'SELECT * FROM users WHERE id = ?';
db.query(query, [userId]);
```

### 🟡 Warnings

**Missing Input Validation** `src/api/auth.js:15`
Email input not validated before processing

### ✅ Positive Notes

- Good test coverage (87%)
- Clear error handling in payment flow
- Proper async/await usage

---

**Models Used:** GPT-4 (planner) → Claude (executor) → GPT-4 (critic)
**Budget:** $0.06 / $10.00 daily limit
```

## Pricing

### For Users (Free Tier)

- ✅ Unlimited public repos
- ✅ 100 PR reviews/month (private repos)
- ✅ Single-agent mode only

### For Users (Pro - $10/month)

- ✅ Unlimited PR reviews
- ✅ Multi-agent mode
- ✅ Compliance checking
- ✅ Priority support

### For Enterprises (Custom)

- ✅ Self-hosted option
- ✅ Custom AI models
- ✅ SLA guarantee
- ✅ Dedicated support

## API Costs (Pass-Through)

You pay OpenAI/Anthropic directly:
- GPT-4: ~$0.01 per review
- Claude: ~$0.02 per review
- Multi-agent: ~$0.06 per review

Budget guards prevent surprises.

## How It Works

### 1. Code Changed
PR opened or updated

### 2. AI Analysis
```
GPT-4 (fast, cheap)
  ↓
Uncertain? → Claude (deep reasoning)
  ↓
GPT-4 critiques → Final verdict
```

### 3. Results Posted
- Inline comments on issues
- PR summary with verdict
- Risk assessment

## Use Cases

### Security Audits
```yaml
# Run deep security review on production PRs
- uses: staticwaves/ai-code-review-pro@v1
  if: github.base_ref == 'main'
  with:
    review_mode: 'multi'
    check_compliance: 'true'
```

### Fast Feedback
```yaml
# Quick review for draft PRs
- uses: staticwaves/ai-code-review-pro@v1
  if: github.event.pull_request.draft == true
  with:
    review_mode: 'single'
```

### Cost Control
```yaml
# Limit to $5/day for personal projects
- uses: staticwaves/ai-code-review-pro@v1
  with:
    budget_limit: '5'
```

## What It Catches

✅ **Security**
- SQL injection
- XSS vulnerabilities
- Authentication issues
- Exposed secrets
- CSRF vulnerabilities

✅ **Code Quality**
- Logic errors
- Performance issues
- Memory leaks
- Race conditions
- Error handling gaps

✅ **Best Practices**
- Code smells
- Anti-patterns
- Inconsistent style
- Missing tests
- Poor naming

✅ **Compliance** (if enabled)
- GDPR violations
- Accessibility (WCAG)
- FTC compliance
- License issues

## Limitations

❌ Does not replace human review for:
- Business logic validation
- Product requirements
- Design decisions
- Political/sensitive code

❌ May miss:
- Extremely complex logic
- Domain-specific issues
- Legacy codebase context

## FAQ

**Q: Is my code sent to OpenAI/Anthropic?**
A: Yes, diffs are sent to their APIs. Do not use on code with secrets. Use in private repos only if comfortable with this.

**Q: Can I self-host?**
A: Yes! Enterprise plan includes self-hosted option. Contact us.

**Q: What languages are supported?**
A: All languages. AI models understand: JavaScript, Python, Go, Rust, Java, PHP, Ruby, and more.

**Q: How do I reduce costs?**
A: Use `review_mode: 'single'` and set lower `budget_limit`.

**Q: Can I customize the review criteria?**
A: Yes, Pro/Enterprise plans allow custom prompts and rules.

## Support

- 📧 Email: support@staticwaves.io
- 💬 Discord: discord.gg/staticwaves
- 📖 Docs: docs.staticwaves.io/ai-code-review

## Pricing for Marketplace

**Free Tier**
- Public repos: Unlimited
- Private repos: 100 reviews/month
- Single-agent only
- **Price:** $0/month

**Pro Tier**
- Unlimited reviews
- Multi-agent mode
- Compliance checks
- **Price:** $10/month

**Team Tier**
- Everything in Pro
- 5 team members
- Shared budget pool
- **Price:** $50/month

**Enterprise**
- Self-hosted option
- Custom models
- SLA support
- **Price:** Custom

---

**Revenue Model:**
- 10,000 Pro users @ $10/month = $100k MRR
- 1,000 Team users @ $50/month = $50k MRR
- **Target:** $150k MRR within 12 months

**Built with StaticWaves AI Platform**
