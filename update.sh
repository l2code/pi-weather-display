#!/bin/bash

# Get the absolute path to the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to that directory
cd "$SCRIPT_DIR" || {
  echo "❌ Could not access script directory: $SCRIPT_DIR"
  exit 1
}

# Pull the latest code
git pull origin master

# Update submodules (e.g., Waveshare library)
git submodule update --init --recursive

echo "✅ Project updated in: $SCRIPT_DIR"
