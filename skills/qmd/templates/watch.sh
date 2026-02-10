#!/bin/bash
# Watch a directory for markdown changes and auto-update qmd index.
# Useful when editing in Obsidian or other editors outside Claude Code.
#
# Requires: brew install fswatch
# Usage: ./watch.sh
# Stop: Ctrl+C

# --- CUSTOMIZE THIS ---
WATCH_DIR="/path/to/your/project"
# ----------------------

export PATH="$HOME/.bun/bin:$PATH"

if ! command -v fswatch >/dev/null 2>&1; then
    echo "fswatch not installed. Run: brew install fswatch"
    exit 1
fi

if ! command -v qmd >/dev/null 2>&1; then
    echo "qmd not found in PATH. Check installation."
    exit 1
fi

echo "Watching $WATCH_DIR for .md changes..."
echo "Press Ctrl+C to stop"

fswatch -0 --include '\.md$' --exclude '.*' "$WATCH_DIR" | while read -d "" event; do
    echo "$(date '+%H:%M:%S') Change: $event"
    qmd update >/dev/null 2>&1 && echo "$(date '+%H:%M:%S') Index updated"
done
