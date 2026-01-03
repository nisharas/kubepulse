#!/bin/bash

# ------------------------------------------------------------------------------
# AUTHOR:      Nishar A Sunkesala / FixMyK8s
# KubeCuro Shell Completion Installer (v1.0)
# ------------------------------------------------------------------------------

set -e

# Visual styling
BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BOLD}${CYAN}❤️  KubeCuro: Setting up smart tab-completions...${NC}"

# 1. Path Check: Is kubecuro installed?
if ! command -v kubecuro &> /dev/null; then
    echo -e "${RED}❌ Error: 'kubecuro' binary not found in your PATH.${NC}"
    echo -e "Please move the binary to ${BOLD}/usr/local/bin${NC} or add its directory to your PATH first."
    exit 1
fi

# 2. Detect Shell
CURRENT_SHELL=$(basename "$SHELL")
CONFIG_FILE=""

if [[ "$CURRENT_SHELL" == "zsh" ]]; then
    CONFIG_FILE="$HOME/.zshrc"
elif [[ "$CURRENT_SHELL" == "bash" ]]; then
    CONFIG_FILE="$HOME/.bashrc"
else
    echo -e "${RED}❌ Unsupported shell: $CURRENT_SHELL${NC}"
    exit 1
fi

echo -e "🔍 Detected shell: ${BOLD}$CURRENT_SHELL${NC}"
echo -e "📝 Target config: ${BOLD}$CONFIG_FILE${NC}"

# 3. Permanence Logic (Idempotent Check)
COMPLETION_LINE="source <(kubecuro completion $CURRENT_SHELL)"

if grep -q "kubecuro completion" "$CONFIG_FILE" 2>/dev/null; then
    echo -e "${GREEN}✅ Completion logic already exists in $CONFIG_FILE.${NC}"
else
    echo -e "\n# KubeCuro Tab-Completion" >> "$CONFIG_FILE"
    echo "$COMPLETION_LINE" >> "$CONFIG_FILE"
    echo -e "${GREEN}🚀 Added completion bridge to $CONFIG_FILE${NC}"
fi

# 4. Final Instructions
echo -e "\n${BOLD}------------------------------------------------------------------${NC}"
echo -e "${GREEN}✨ Setup Complete!${NC}"
echo -e "To use it now, run: ${BOLD}source $CONFIG_FILE${NC}"
echo -e "Otherwise, it will be active the next time you open a terminal."
echo -e "${BOLD}------------------------------------------------------------------${NC}"
