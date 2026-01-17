═══════════════════════════════════════════════════════════════════════════════
  FRESH LINUX INSTALLATION - QUICK START
═══════════════════════════════════════════════════════════════════════════════

👉 ONE-LINE INSTALL (Automated):

bash <(curl -sSL https://raw.githubusercontent.com/ssiens-oss/ssiens-oss-static_pod/main/fresh-linux-install.sh)

───────────────────────────────────────────────────────────────────────────────

👉 MANUAL INSTALL (Step by Step):

1. Clone the repository:
   git clone https://github.com/ssiens-oss/ssiens-oss-static_pod.git
   cd ssiens-oss-static_pod

2. Run the installation script:
   ./fresh-linux-install.sh

───────────────────────────────────────────────────────────────────────────────

👉 AFTER INSTALLATION:

1. Configure your Printify API keys:
   nano ~/staticwaves-pod/gateway/.env

   Update:
   PRINTIFY_API_KEY=your_actual_api_key
   PRINTIFY_SHOP_ID=your_actual_shop_id

2. Start the gateway:
   ~/staticwaves-pod/start-gateway.sh

   Or manually:
   cd ~/staticwaves-pod/gateway
   .venv/bin/python app/main.py

3. Open your browser:
   http://localhost:5000

───────────────────────────────────────────────────────────────────────────────

👉 GET PRINTIFY API CREDENTIALS:

1. Sign up at: https://printify.com
2. Go to: Settings → API
3. Generate API Token
4. Copy API Key and Shop ID

───────────────────────────────────────────────────────────────────────────────

📚 FULL DOCUMENTATION:

See FRESH_INSTALL.md for complete installation guide with troubleshooting.

═══════════════════════════════════════════════════════════════════════════════
