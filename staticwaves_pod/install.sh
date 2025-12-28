#!/usr/bin/env bash
set -e

echo "🚀 Installing StaticWaves POD..."

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "Installing Python 3..."
    sudo apt install -y python3 python3-venv python3-pip
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate and install dependencies
echo "Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create .env from example if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your API keys"
fi

# Create necessary directories
echo "Creating queue directories..."
mkdir -p queues/{incoming,processed,failed,published}
mkdir -p exports
mkdir -p assets

echo "✅ StaticWaves POD Installed"
echo ""
echo "Next steps:"
echo "1. Edit .env with your API credentials"
echo "2. Add a base mockup image to assets/hoodie_base.png"
echo "3. Run workers: python3 workers/rmbg_worker.py"
echo "4. Start API: python3 api/app.py"
echo ""
echo "For systemd deployment:"
echo "sudo cp systemd/*.service /etc/systemd/system/"
echo "sudo systemctl daemon-reload"
echo "sudo systemctl enable staticwaves-*.service"
echo "sudo systemctl start staticwaves-*.service"
