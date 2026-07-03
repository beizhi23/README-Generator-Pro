#!/bin/bash
# Deployment script for README Generator Pro
# Supports: Docker, Railway, Cloudflare Tunnel

set -e

echo "README Generator Pro - Deployment"
echo "================================="
echo ""
echo "Choose deployment method:"
echo "  1) Docker (local)"
echo "  2) Railway (cloud, China-accessible)"
echo "  3) Fly.io (cloud, China-accessible)"
echo "  4) Cloudflare Tunnel (free, best China access)"
echo ""
read -p "Enter choice [1-4]: " choice

case $choice in
  1)
    echo "Building Docker image..."
    docker build -t readme-generator-pro .
    echo "Running on port 8000..."
    docker run -p 8000:8000 --env-file .env readme-generator-pro
    ;;
  2)
    echo "Deploying to Railway..."
    railway login
    railway init
    railway up
    ;;
  3)
    echo "Deploying to Fly.io..."
    fly launch
    ;;
  4)
    echo "Setting up Cloudflare Tunnel..."
    echo ""
    echo "Prerequisites:"
    echo "  1. Cloudflare account (free)"
    echo "  2. A domain managed by Cloudflare"
    echo "  3. cloudflared installed"
    echo ""
    echo "Steps:"
    echo "  1. Run: cloudflared tunnel login"
    echo "  2. Run: cloudflared tunnel create readme-gen"
    echo "  3. Configure DNS in Cloudflare dashboard:"
    echo "     CNAME readme.yourdomain.com -> <tunnel-id>.cfargotunnel.com"
    echo "  4. Run tunnel:"
    echo "     cloudflared tunnel run --url http://localhost:8000 readme-gen"
    echo ""
    echo "Then start the app: python run.py"
    ;;
  *)
    echo "Invalid choice"
    ;;
esac
