#!/usr/bin/env bash
# Run Earshot directly without building an app bundle

cd "$(dirname "$0")"
python3 -m earshot.app
