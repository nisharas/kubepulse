#!/bin/bash

# Linux/macOS):
PYINSTALLER_SEPARATOR=":"

# Cross-platform (add this for Windows CI/CD):
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    PYINSTALLER_SEPARATOR=";"
else
    PYINSTALLER_SEPARATOR=":"
fi


# --- ANCHOR THE DIRECTORY ---
# Double quotes here protect against paths with spaces
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# --- CLEANUP TRAP ---
LOG_FILE=$(mktemp)
cleanup() {
    local exit_code=$?
    tput cnorm # Restore cursor
    jobs -p | xargs -r kill > /dev/null 2>&1
    rm -f "$LOG_FILE"
    if [ "$exit_code" -ne 0 ] && [ "$exit_code" -ne 130 ]; then
        echo -e "\n\033[31m💥 Build interrupted or failed.\033[0m"
    fi
    exit "$exit_code"
}
trap cleanup EXIT INT TERM

# --- REPRODUCIBLE SPINNER FUNCTION ---
spinner() {
    local pid="$1"
    local delay=0.1
    # Declare once - IDE safe with double backslash
    local spinstr='|/-\\'
    tput civis # Hide cursor
    
    while ps -p "$pid" > /dev/null 2>&1; do
        # Just update the variable, don't re-declare 'local'
        local temp="${spinstr#?}"
        printf " [%c] " "$spinstr"
        spinstr="$temp${spinstr%"$temp"}"
        sleep "$delay"
        printf "\b\b\b\b\b"
    done
    
    wait "$pid"
    local res=$?
    
    # Clean up the 5 characters we printed
    printf "     \b\b\b\b\b"
    tput cnorm # Restore cursor
    return "$res"
}

# --- PRE-FLIGHT ---
ASSETS_DIR="$SCRIPT_DIR/src/kubecuro/assets"
echo -e "\033[1;35m🧬 KubeCuro Build System\033[0m"
echo "--------------------------------------"

# 1. Cleaning
echo -n "🧹 Deep cleaning workspace..."
{
    rm -rf build/ dist/ *.spec *.egg-info
} &
spinner "$!"
echo -e "[DONE]"

# 2. Building
echo -n "🐍 Compiling Dynamic Binary..."
{
    pyinstaller --onefile --clean --name kubecuro_dynamic \
                --paths "$SCRIPT_DIR/src" \
                --add-data "${ASSETS_DIR}${PYINSTALLER_SEPARATOR}kubecuro/assets" \
                --collect-all rich \
                --exclude-module argcomplete.scripts \
                --hidden-import argcomplete \
                --collect-all ruamel.yaml \
                --hidden-import ruamel.yaml \
                --exclude-module _ruamel_yaml_clib \
                --exclude-module ruamel.yaml.clib \
                "$SCRIPT_DIR/src/kubecuro/main.py"
} > "$LOG_FILE" 2>&1 &

if spinner "$!"; then
    echo -e "[DONE]"
else
    echo -e "[\033[31mFAIL\033[0m]"
    echo -e "\033[31mError during compilation. Build Log:\033[0m"
    echo "--------------------------------------"
    cat "$LOG_FILE"
    echo "--------------------------------------"
    exit 1
fi

# 3. StaticX
echo -n "🛡️  Hardening to Static Binary..."
if ! command -v staticx &> /dev/null; then
    # Fallback: Copy the dynamic binary to the final name
    cp "dist/kubecuro_dynamic" "dist/kubecuro"
    echo -e "[\033[33mSKIPPED\033[0m] (StaticX not found)"
    HAD_STATICX=false
else
    (staticx --strip dist/kubecuro_dynamic dist/kubecuro > /dev/null 2>&1) &
    if spinner "$!"; then
        echo -e "[DONE]"
        HAD_STATICX=true
    else
        echo -e "[\033[31mFAIL\033[0m]"
        exit 1
    fi
fi

# 4. Integrity Check
echo -n "🧪 Running Integrity Check..."
if "$SCRIPT_DIR/dist/kubecuro" --version > /dev/null 2>&1; then
    echo -e "[\033[32mPASSED\033[0m]"
else
    echo -e "[\033[31mFAILED\033[0m]"
    exit 1
fi

# --- ENGAGING SUMMARY ---
echo "--------------------------------------"
echo -e "✅ \033[1;32mBuild Complete!\033[0m"
if [ "$HAD_STATICX" = true ]; then
    echo -e "💎 Type:   \033[1;34mStatic (Portable)\033[0m"
else
    echo -e "📦 Type:   \033[1;33mDynamic (System Dependent)\033[0m"
fi
echo -e "📂 Binary: \033[34m$SCRIPT_DIR/dist/kubecuro\033[0m"
echo -e "🚀 Test:   \033[1;36m$SCRIPT_DIR/dist/kubecuro --help\033[0m"
echo ""
echo -e "💡 \033[33mTo use globally:\033[0m"
echo -e "   sudo cp \"$SCRIPT_DIR/dist/kubecuro\" /usr/local/bin/"
BINARY_SIZE=$(du -sh "$SCRIPT_DIR/dist/kubecuro" | cut -f1)
echo -e "📦 Final Binary Size: \033[1;33m$BINARY_SIZE\033[0m"
echo "--------------------------------------"
