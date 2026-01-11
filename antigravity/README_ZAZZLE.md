# Zazzle Integration - Quick Reference

Complete Zazzle marketplace integration with full Antigravity AI orchestration.

## 🚀 Quick Setup (5 Minutes)

```bash
cd antigravity

# 1. Run setup script
./setup_zazzle.sh

# 2. Validate configuration
python validate_zazzle.py

# 3. Test with a design
python -m antigravity.zazzle_cli design test.png --dry-run
```

## 📚 Documentation

- **Setup Guide**: `ZAZZLE_SETUP.md` - Step-by-step setup instructions
- **Integration Guide**: `ZAZZLE_INTEGRATION.md` - Complete feature documentation
- **Examples**: `examples/zazzle_quickstart.py` - Code examples

## 🔑 Getting Credentials

### Option 1: Associate Program (Recommended)
1. Go to: https://www.zazzle.com/sell/associates
2. Sign up (free, instant approval)
3. Get your Associate ID
4. Add to `.env`: `ZAZZLE_ASSOCIATE_ID=your_id`

### Option 2: Full API
1. Go to: https://www.zazzle.com/sell/developers
2. Apply for API access (3-7 days approval)
3. Generate API key
4. Add to `.env`: `ZAZZLE_API_KEY=your_key`

## 📦 Supported Products

- **Apparel**: T-shirts, Hoodies
- **Home**: Posters, Mugs, Pillows, Mousepads
- **Accessories**: Stickers, Phone Cases, Tote Bags, Keychains

## 🎨 Usage Examples

### Single Product
```bash
python -m antigravity.zazzle_cli design design.png \
  --product-type hoodie \
  --template hoodie_premium
```

### Multiple Product Types
```bash
python -m antigravity.zazzle_cli multi design.png \
  --product-types tshirt,hoodie,mug,poster
```

### Watch Directory (Autonomous)
```bash
python -m antigravity.zazzle_cli watch \
  --watch-dir /data/comfyui/output \
  --product-type tshirt
```

### Python API
```python
from antigravity.pod.zazzle_orchestrator import ZazzlePODOrchestrator

orchestrator = ZazzlePODOrchestrator()
result = orchestrator.process_design_for_zazzle(
    design_path="design.png",
    product_type="hoodie",
)
```

## 🔧 Configuration

**Minimum required** in `.env`:
```bash
ZAZZLE_ASSOCIATE_ID=your_id         # OR
ZAZZLE_API_KEY=your_key             # (need at least one)

ZAZZLE_STORE_ID=your_store_name
ZAZZLE_DEFAULT_TEMPLATE=tshirt_basic
ENABLE_ZAZZLE=true
```

## 📋 Templates

| Template | Price | Royalty | Use For |
|----------|-------|---------|---------|
| `tshirt_basic` | $19.99 | 10% | Volume |
| `tshirt_premium` | $24.99 | 15% | Margins |
| `hoodie_basic` | $39.99 | 10% | Entry |
| `hoodie_premium` | $49.99 | 15% | Premium |
| `poster` | $14.99 | 20% | Art |
| `mug` | $12.99 | 15% | Gifts |

## ✅ Features

✓ Multi-model AI decision-making (GPT + Claude + Grok)
✓ Risk assessment and safety checks
✓ A/B testing with multiple variants
✓ Uncertainty detection and human escalation
✓ Playwright verification
✓ Memory and learning
✓ Slack/Email notifications
✓ Complete audit trails

## 🆘 Troubleshooting

### "No credentials found"
```bash
./setup_zazzle.sh
```

### "Configuration incomplete"
```bash
python validate_zazzle.py  # See what's missing
nano .env                   # Add missing values
```

### Import errors
```bash
pip install -r requirements.txt
playwright install
```

## 📖 Read More

- **Complete Setup**: `ZAZZLE_SETUP.md`
- **Full Integration Guide**: `ZAZZLE_INTEGRATION.md`
- **Main Documentation**: `README.md`

## 🎯 Next Steps

1. ✅ Run setup script
2. ✅ Validate configuration
3. ✅ Test in dry-run mode
4. ✅ Enable production
5. ✅ Start autonomous processing

---

**Questions?** Check `ZAZZLE_SETUP.md` for detailed troubleshooting.
