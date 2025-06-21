#!/bin/bash

echo "🚀 Starting ibiDs CRM Deployment..."
echo "=================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

echo "✅ Docker is running"

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start the services
echo "🔨 Building and starting Odoo with ibiDs CRM..."
docker-compose up -d

# Wait for Odoo to be ready
echo "⏳ Waiting for Odoo to start (this may take 2-3 minutes)..."
sleep 30

# Check if Odoo is running
if curl -s http://localhost:8069 > /dev/null; then
    echo "✅ Odoo is running successfully!"
    echo ""
    echo "🌐 Access your ibiDs CRM at: http://localhost:8069"
    echo ""
    echo "📋 Next steps:"
    echo "1. Open http://localhost:8069 in your browser"
    echo "2. Create a new database (Master Password: admin123)"
    echo "3. Install the govcon_crm module"
    echo "4. Configure your ibiDs API credentials"
    echo ""
    echo "🔧 To stop the services: docker-compose down"
    echo "🔧 To view logs: docker-compose logs -f odoo"
else
    echo "❌ Odoo failed to start. Check logs with: docker-compose logs odoo"
    exit 1
fi 