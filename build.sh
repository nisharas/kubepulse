#!/bin/bash
# KubeCuro Universal Static Binary Builder

set -e

echo "📦 1. Cleaning up old artifacts..."
rm -rf build/ dist/ *.spec

echo "🐍 2. Building Dynamic Binary with PyInstaller..."
# --exclude-module ensures the problematic C-lib is left behind
pyinstaller --onefile \
            --name kubecuro_dynamic \
            --paths src \
            --collect-all rich \
            --hidden-import ruamel.yaml \
            --exclude-module _ruamel_yaml_clib \
            src/kubecuro/main.py

echo "🛡️ 3. Converting to Static Binary with StaticX..."
# This step creates the ultra-portable version
staticx dist/kubecuro_dynamic dist/kubecuro

echo "✅ 4. Build Complete!"
echo "------------------------------------------------"
echo "Binary location: $(pwd)/dist/kubecuro"
echo "Test it now: ./dist/kubecuro --help"
