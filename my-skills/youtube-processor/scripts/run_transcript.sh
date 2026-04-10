#!/bin/bash
# Wrapper script that runs get_transcript.py using the skill's Python environment.
# Called by the SKILL.md — members don't need to run this directly.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

VENV_PYTHON="$SKILL_DIR/.venv/bin/python"

if [ ! -f "$VENV_PYTHON" ]; then
    echo "SETUP_NEEDED"
    echo ""
    echo "The YouTube Processor needs a one-time setup."
    echo "Copy and paste this into your terminal:"
    echo ""
    echo "  bash $SKILL_DIR/scripts/setup.sh"
    echo ""
    exit 1
fi

"$VENV_PYTHON" "$SKILL_DIR/tools/get_transcript.py" "$@"
