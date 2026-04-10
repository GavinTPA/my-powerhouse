#!/bin/bash
# install-hook.sh - Install the secret detection pre-commit hook
# Part of the security-check skill
#
# Usage: ./install-hook.sh [repo-path]
#   repo-path: Optional path to git repo (defaults to current repo root)

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BOLD='\033[1m'
NC='\033[0m'

# Determine script location (so we can find the hook script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK_SOURCE="${SCRIPT_DIR}/pre-commit-hook.sh"

# Determine repo root
if [[ -n "${1:-}" ]]; then
    REPO_ROOT="$(cd "$1" && git rev-parse --show-toplevel 2>/dev/null)" || {
        echo -e "${RED}Error: $1 is not a git repository${NC}"
        exit 1
    }
else
    REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
        echo -e "${RED}Error: Not inside a git repository${NC}"
        exit 1
    }
fi

HOOKS_DIR="${REPO_ROOT}/.git/hooks"
HOOK_TARGET="${HOOKS_DIR}/pre-commit"

# Verify the hook source exists
if [[ ! -f "$HOOK_SOURCE" ]]; then
    echo -e "${RED}Error: Hook script not found at ${HOOK_SOURCE}${NC}"
    exit 1
fi

# Check for existing pre-commit hook
if [[ -f "$HOOK_TARGET" ]] || [[ -L "$HOOK_TARGET" ]]; then
    echo -e "${YELLOW}Existing pre-commit hook found at ${HOOK_TARGET}${NC}"
    echo -e "${YELLOW}Backing up to ${HOOK_TARGET}.bak${NC}"
    cp "$HOOK_TARGET" "${HOOK_TARGET}.bak" 2>/dev/null || true
fi

# Install the hook (platform-aware)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "mingw"* || "$OSTYPE" == "cygwin"* ]]; then
    # Windows Git Bash: copy instead of symlink (symlinks require Developer Mode)
    cp "$HOOK_SOURCE" "$HOOK_TARGET"
    chmod +x "$HOOK_TARGET"
    echo -e "${YELLOW}Note: On Windows, the hook is a copy. Re-run install-hook.sh after updates.${NC}"
else
    ln -sf "$HOOK_SOURCE" "$HOOK_TARGET"
fi

# Verify it's executable (the source should be, but double-check)
chmod +x "$HOOK_SOURCE"

# Verify installation
if [[ -f "$HOOK_TARGET" ]] && [[ -x "$HOOK_TARGET" ]]; then
    echo ""
    echo -e "${GREEN}${BOLD}Pre-commit hook installed successfully${NC}"
    echo ""
    echo "  Hook: ${HOOK_TARGET}"
    echo "  Source: ${HOOK_SOURCE}"
    echo ""
    echo "The hook will scan staged files for hardcoded secrets before each commit."
    echo ""
    echo -e "To add exceptions for false positives, create a ${BOLD}.secretsignore${NC} file"
    echo "in the repo root with regex patterns (one per line)."
    echo ""
    echo -e "To uninstall: ${YELLOW}rm ${HOOK_TARGET}${NC}"
else
    echo -e "${RED}Error: Installation failed${NC}"
    exit 1
fi
