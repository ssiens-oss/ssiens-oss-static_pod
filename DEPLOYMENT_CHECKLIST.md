# POD Pipeline - Deployment Checklist

Use this checklist when deploying to RunPod for the first time.

## Pre-Deployment (Local Machine)

- [ ] Code is on branch: `claude/setup-pod-pipeline-siF3A`
- [ ] All commits are pushed to remote
- [ ] You have your API keys ready:
  - [ ] Anthropic API key (Claude)
  - [ ] Printify API key and Shop ID
  - [ ] Shopify credentials (optional)
  - [ ] Other platform credentials (optional)

## RunPod Setup

- [ ] Create new pod on RunPod
  - [ ] GPU: A4000 or better selected
  - [ ] Disk: 50GB minimum
  - [ ] Port 8188 exposed
  - [ ] Port 3000 exposed (for web UI)
- [ ] Pod is running and ready
- [ ] SSH key is configured

## Initial Connection

- [ ] SSH into pod: `ssh <pod-id>@ssh.runpod.io -i ~/.ssh/id_ed25519`
- [ ] Verify Node.js 20+ is installed: `node --version`
- [ ] Navigate to app: `cd /workspace/app`
- [ ] Code is present: `ls -la`

## Dependency Installation

- [ ] Run: `npm install`
- [ ] Verify installation succeeded: `npm list @anthropic-ai/sdk axios dotenv tsx`
- [ ] Check for any warnings or errors
- [ ] Verify TypeScript compiles: `npx tsc --noEmit --skipLibCheck`

## Environment Configuration

- [ ] Copy example env: `cp .env.example .env`
- [ ] Edit .env: `nano .env` or `vim .env`
- [ ] Add `ANTHROPIC_API_KEY`
- [ ] Add `PRINTIFY_API_KEY` and `PRINTIFY_SHOP_ID`
- [ ] Add `SHOPIFY_STORE_URL` and `SHOPIFY_ACCESS_TOKEN` (if using)
- [ ] Add other platform credentials (if using)
- [ ] Verify .env: `cat .env | grep -v '^#' | grep '='`

## ComfyUI Setup

- [ ] Navigate to ComfyUI: `cd /workspace/ComfyUI`
- [ ] Check if running: `curl http://localhost:8188/system_stats`
- [ ] If not running, start it: `python3 main.py --listen 0.0.0.0 --port 8188 &`
- [ ] Verify it started: `curl http://localhost:8188/system_stats`
- [ ] Check for existing images: `ls output/*.png | wc -l`

## Pipeline Testing

- [ ] Navigate back to app: `cd /workspace/app`
- [ ] Test dry run: `npm run pipeline:single -- --theme="test design" --no-publish`
- [ ] Check output directory: `ls -la /data/designs/`
- [ ] Verify no errors in output
- [ ] Check generated image exists

## Platform Connection Tests

- [ ] Test Printify: `curl -H "Authorization: Bearer $PRINTIFY_API_KEY" https://api.printify.com/v1/shops.json`
- [ ] Verify shop ID is correct
- [ ] Test Shopify (if configured): `curl -H "X-Shopify-Access-Token: $SHOPIFY_ACCESS_TOKEN" https://$SHOPIFY_STORE_URL/admin/api/2024-01/shop.json`

## First Production Run

- [ ] Run single design with publish: `npm run pipeline:single -- --theme="your first theme"`
- [ ] Monitor output for errors
- [ ] Check Printify dashboard for new product
- [ ] Check Shopify store for new product (if configured)
- [ ] Verify images saved to `/data/designs/`

## Batch Testing

- [ ] Run small batch: `npm run pipeline:batch -- 3`
- [ ] Monitor progress
- [ ] Check for any errors
- [ ] Verify all 3 designs created
- [ ] Check platform dashboards

## Local Machine Auto-Download

- [ ] On local machine: `cd ~/ssiens-oss-static_pod`
- [ ] Set environment: `export RUNPOD_SSH_HOST="<pod-id>@ssh.runpod.io"`
- [ ] Set remote path: `export REMOTE_PATH="/data/designs"`
- [ ] Make script executable: `chmod +x scripts/auto-download-images.sh`
- [ ] Test download: `./scripts/download-images.sh`
- [ ] Verify images in `~/POD-Designs/`
- [ ] Start auto-sync: `./scripts/auto-download-images.sh`

## Automation Setup (Optional)

- [ ] Edit crontab on RunPod: `crontab -e`
- [ ] Add daily job: `0 3 * * * cd /workspace/app && npm run pipeline:batch -- 10 >> /var/log/pod-pipeline.log 2>&1`
- [ ] Verify crontab: `crontab -l`
- [ ] Test log file: `touch /var/log/pod-pipeline.log`

## Monitoring Setup

- [ ] Create log directory: `sudo mkdir -p /var/log`
- [ ] Set permissions: `sudo chmod 777 /var/log`
- [ ] Test logging: `echo "test" >> /var/log/pod-pipeline.log`
- [ ] Create monitoring script (optional)

## Production Readiness

- [ ] Pipeline runs without errors
- [ ] Products appear on Printify
- [ ] Products appear on Shopify (if configured)
- [ ] Images download to local machine
- [ ] Cron job scheduled (if using)
- [ ] All documentation reviewed

## Final Verification

- [ ] Run: `npm run pipeline:batch -- 5`
- [ ] All 5 designs generated successfully
- [ ] All products created on platforms
- [ ] No errors in logs
- [ ] Images synced to local machine
- [ ] Ready for production use!

## Documentation References

- [ ] Read `QUICK_START.md` for daily usage
- [ ] Bookmark `COMMANDS.md` for quick reference
- [ ] Review `RUNPOD_DEPLOYMENT.md` for detailed steps
- [ ] Keep `COMMANDS.md` open during operations

---

## Notes

**Date Deployed:** _________________

**Pod ID:** _________________

**Issues Encountered:**
-
-
-

**Custom Configuration:**
-
-
-

---

✅ **Deployment Complete!**

Your POD pipeline is now running and ready to generate designs automatically!
