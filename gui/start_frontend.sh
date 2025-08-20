#!/bin/bash

echo "🎨 Starting Supreme Jarvis Frontend..."
echo "=================================="

cd "$(dirname "$0")/frontend"

if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

echo "🚀 Starting development server..."
npm run dev