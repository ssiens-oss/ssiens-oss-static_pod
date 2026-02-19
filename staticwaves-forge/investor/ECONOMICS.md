# StaticWaves Forge - Unit Economics

## Cost Structure

### Per-Asset Cost Breakdown

| Component                  | Cost    | Notes                              |
|----------------------------|---------|-------------------------------------|
| GPU compute (30s)          | $0.08   | RunPod RTX 4090 @ $0.34/hr         |
| Storage (2MB asset)        | $0.01   | R2/S3 storage + CDN                |
| API overhead               | $0.01   | Server costs amortized             |
| **Total Cost per Asset**   | **$0.10** | Can scale down to $0.05 with optimization |

### SaaS Cost Structure

#### Starter Tier ($29/mo, 100 assets)
- Asset generation cost: 100 × $0.10 = **$10**
- Gross margin: **$19 (65%)**

#### Creator Tier ($79/mo, 500 assets)
- Asset generation cost: 500 × $0.10 = **$50**
- Gross margin: **$29 (37%)**

#### Studio Tier ($199/mo, unlimited)
- Average usage: ~2,000 assets/mo
- Asset generation cost: 2,000 × $0.10 = **$200**
- Gross margin: **-$1 (-0.5%)** ← incentivizes pack purchasing

**Blended SaaS Margin Target: 55-60%**

### Asset Pack Economics

#### Example: Fantasy Creatures Pack ($39)

**Costs:**
| Item                       | Cost    |
|----------------------------|---------|
| 25 assets @ $0.10          | $2.50   |
| Pack creation (automated)  | $0.10   |
| Storage & hosting          | $0.20   |
| Marketplace fee (30%)      | $11.70  |
| **Total Cost**             | **$14.50** |

**Revenue:**
- Sale price: $39
- Net after marketplace: $27.30
- **Gross profit: $12.80 (47% margin)**

**Payback:**
- 1 sale = 128 assets generated for free
- Break-even: 1.2 sales per pack
- Target: 100 sales per pack = **$1,280 profit**

---

## Revenue Projections

### Year 1 (Conservative)

#### SaaS Revenue
| Tier       | Users | Price | MRR    | ARR      |
|------------|-------|-------|--------|----------|
| Starter    | 300   | $29   | $8,700 | $104,400 |
| Creator    | 150   | $79   | $11,850| $142,200 |
| Studio     | 40    | $199  | $7,960 | $95,520  |
| Enterprise | 10    | $500  | $5,000 | $60,000  |
| **Total**  | **500** | -   | **$33,510** | **$402,120** |

#### Asset Pack Revenue
| Metric                     | Value        |
|----------------------------|--------------|
| Packs published            | 100          |
| Avg price                  | $39          |
| Avg sales per pack         | 100          |
| Total sales                | 10,000       |
| Gross revenue              | $390,000     |
| Marketplace fees (30%)     | -$117,000    |
| Net revenue                | **$273,000** |

**Year 1 Total Revenue: $675,120**

### Year 2 (Growth)

#### SaaS Revenue
| Tier       | Users  | Price | ARR       |
|------------|--------|-------|-----------|
| Starter    | 1,200  | $29   | $417,600  |
| Creator    | 600    | $79   | $568,800  |
| Studio     | 150    | $199  | $358,200  |
| Enterprise | 50     | $500  | $300,000  |
| **Total**  | **2,000** | -  | **$1,644,600** |

#### Asset Pack Revenue
| Metric                     | Value          |
|----------------------------|----------------|
| Packs published            | 300            |
| Avg sales per pack         | 150            |
| Net revenue                | **$1,228,500** |

**Year 2 Total Revenue: $2,873,100**

---

## Customer Acquisition

### CAC by Channel

| Channel              | CAC    | LTV (2yr) | LTV:CAC |
|---------------------|--------|-----------|---------|
| Organic (SEO, viral)| $0     | $1,896    | ∞       |
| Marketplace listing | $20    | $1,896    | 94.8x   |
| Content marketing   | $50    | $1,896    | 37.9x   |
| Paid ads (YouTube)  | $120   | $1,896    | 15.8x   |

**Blended CAC Target: $45**

### LTV Calculation

**Average Customer:**
- Subscription: $79/mo × 18 months = $1,422
- Asset pack purchases: 6 packs × $39 = $234
- Referral value: $240
- **Total LTV: $1,896**

**LTV:CAC = 42:1** (excellent)

---

## Path to Profitability

### Monthly Operating Costs

| Category              | Amount   |
|-----------------------|----------|
| Engineering (3 FTE)   | $45,000  |
| Infrastructure        | $15,000  |
| Marketing             | $25,000  |
| Operations            | $10,000  |
| **Total Monthly**     | **$95,000** |

**Break-even:**
- Monthly costs: $95,000
- Blended margin: 60%
- Revenue needed: $95,000 / 0.60 = **$158,333/mo**
- **$1.9M ARR**

**Timeline to profitability: Month 18-20**

---

## Sensitivity Analysis

### Best Case (130% of projections)
- Year 1: $878k revenue, -$262k EBITDA
- Year 2: $3.7M revenue, $1.1M EBITDA
- **Profitable Month 14**

### Base Case (100% of projections)
- Year 1: $675k revenue, -$465k EBITDA
- Year 2: $2.9M revenue, $600k EBITDA
- **Profitable Month 20**

### Worst Case (70% of projections)
- Year 1: $473k revenue, -$667k EBITDA
- Year 2: $2M revenue, $60k EBITDA
- **Profitable Month 24**

---

## Exit Scenarios

### Valuation Multiples (SaaS Industry)

| Metric          | Multiple | Value at $3M ARR | Value at $10M ARR |
|-----------------|----------|------------------|-------------------|
| Revenue (ARR)   | 8-12x    | $24-36M          | $80-120M          |
| Subscribers     | $3,000   | -                | $6M (2k subs)     |

**Target Exit:**
- Timeline: 5-7 years
- ARR at exit: $10-25M
- Valuation: **$80-200M**
- Investor return: **50-100x** (on $1.5M seed)

---

## Risk Factors & Mitigations

### Key Risks

1. **GPU Cost Volatility**
   - Mitigation: Multi-cloud strategy, spot instances, optimization

2. **Marketplace Dependency**
   - Mitigation: Build direct sales channel, own marketplace

3. **Quality Concerns**
   - Mitigation: Human-in-the-loop QA, iterative improvement

4. **Competitor Entry**
   - Mitigation: Speed to market, data moat, brand building

5. **Churn**
   - Mitigation: Asset library retention, annual discounts, community

---

*Last Updated: January 2026*
