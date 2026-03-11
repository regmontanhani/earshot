#!/usr/bin/env bash
# Build WhisperX as a standalone macOS app

set -euo pipefail

cd "$(dirname "$0")"

echo "🔧 Installing dependencies..."
pip install -r requirements.txt

echo "📦 Building app..."
python setup.py py2app

echo "✅ Build complete!"
echo "   App location: dist/WhisperX.app"
echo ""
echo "To install:"
echo "   cp -r dist/WhisperX.app /Applications/"
echo ""
echo "Or run directly:"
echo "   open dist/WhisperX.app"
