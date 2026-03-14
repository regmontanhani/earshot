#!/bin/bash
# Build and run Earshot with stable code signing
set -e

cd "$(dirname "$0")"

echo "Building..."
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer xcodebuild \
  -project Earshot.xcodeproj -scheme Earshot -configuration Debug \
  -derivedDataPath build ONLY_ACTIVE_ARCH=YES -quiet

echo "Signing..."
codesign --force --deep --sign "Earshot Dev" \
  build/Build/Products/Debug/Earshot.app

echo "Launching..."
open build/Build/Products/Debug/Earshot.app
