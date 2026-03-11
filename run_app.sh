#!/usr/bin/env bash
# Run WhisperX directly without building an app bundle

cd "$(dirname "$0")"
python3 -m whisperx_app.app
