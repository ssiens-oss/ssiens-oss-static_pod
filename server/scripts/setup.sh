#!/bin/bash

# TikTok Webhook Server Setup Script

set -e

echo "🚀 Setting up TikTok Webhook Server..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

echo "✅ Node.js version: $(node --version)"

# Check if PostgreSQL is available
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL client not found. Make sure PostgreSQL is installed and accessible."
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please update .env with your actual configuration values!"
else
    echo "✅ .env file already exists"
fi

# Create database if needed (optional)
read -p "Do you want to create the database now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Load environment variables
    if [ -f .env ]; then
        export $(cat .env | grep -v '^#' | xargs)
    fi

    echo "🗄️  Creating database..."
    createdb -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME 2>/dev/null || echo "Database may already exist"

    echo "📋 Initializing database schema..."
    npm run db:init
fi

echo ""
echo "✨ Setup completed!"
echo ""
echo "Next steps:"
echo "1. Update your .env file with actual configuration values"
echo "2. Ensure PostgreSQL is running"
echo "3. Run 'npm run dev' to start the development server"
echo "4. Configure TikTok webhook URL to point to: http://your-domain/webhook/tiktok"
echo ""
