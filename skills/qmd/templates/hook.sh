#!/bin/bash
# Claude Code PostToolUse hook: Auto-update qmd index after editing markdown files
# Runs silently in background after Edit and Write tool calls.
#
# Setup:
#   1. Copy to ~/.claude/hooks/qmd-update.sh
#   2. Change PROJECT_DIR below to your indexed project path
#   3. Add to ~/.claude/settings.json (see setup/README.md)

# --- CUSTOMIZE THIS ---
PROJECT_DIR="/path/to/your/project"
# ----------------------

# Parse the file path from hook input (JSON via stdin)
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | grep -o '"file_path":"[^"]*"' | cut -d'"' -f4)

# Only run for markdown files in the target project
if [[ "$FILE_PATH" == *"$PROJECT_DIR"* ]] && [[ "$FILE_PATH" == *.md ]]; then
    export PATH="$HOME/.bun/bin:$PATH"
    qmd update >/dev/null 2>&1 &
fi

exit 0
