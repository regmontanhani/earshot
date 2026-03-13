#!/bin/bash
# Run Earshot v2 floating window app

cd "$(dirname "$0")"

# Use venv if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

python3 -m earshot.window
