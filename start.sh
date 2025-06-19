#!/bin/bash

# Enhanced Company RAG Chatbot Startup Script
# This script sets up and starts the enhanced RAG chatbot

set -e

echo "🚀 Enhanced Company RAG Chatbot v2.0"
echo "======================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo "📝 Creating environment file..."
    cp backend/.env.example backend/.env
    echo "⚠️  Please edit backend/.env and add your OpenAI API key before continuing."
    echo "   You can do this by running: nano backend/.env"
    read -p "Press Enter when you've added your API key..."
fi

# Check if data directory exists and has files
if [ ! -d "data" ] || [ -z "$(ls -A data 2>/dev/null)" ]; then
    echo "📁 Creating data directory..."
    mkdir -p data
    echo "⚠️  Please add your company policy documents to the data/ directory."
    echo "   Supported formats: PDF, TXT, MD, CSV, DOCX, DOC"
    read -p "Press Enter when you've added your documents..."
fi

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
echo "🔍 Checking service status..."
if docker-compose ps | grep -q "Up"; then
    echo "✅ Services are running!"
else
    echo "❌ Some services failed to start. Check logs with: docker-compose logs"
    exit 1
fi

# Run document ingestion
echo "📚 Ingesting documents..."
docker-compose exec backend python enhanced_ingest.py

echo ""
echo "🎉 Setup complete! Your enhanced RAG chatbot is ready."
echo ""
echo "📱 Access your chatbot at:"
echo "   • Chat Interface: http://localhost"
echo "   • Admin Dashboard: http://localhost (click 'Admin' tab)"
echo "   • API Documentation: http://localhost:8000/docs"
echo ""
echo "🔧 Useful commands:"
echo "   • View logs: docker-compose logs -f"
echo "   • Stop services: docker-compose down"
echo "   • Restart services: docker-compose restart"
echo "   • Update documents: docker-compose exec backend python enhanced_ingest.py"
echo ""
echo "📊 Monitor your system:"
echo "   • Check system health in the Admin Dashboard"
echo "   • Review training reports for insights"
echo "   • Get improvement suggestions automatically"
echo ""
echo "🚀 Enjoy!" 