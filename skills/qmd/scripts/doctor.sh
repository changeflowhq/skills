#!/bin/bash
# qmd doctor - check installation and automation health
# Usage: bash ~/.claude/skills/qmd/scripts/doctor.sh

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

PASS=0
FAIL=0
WARN=0

check() {
    local label="$1"
    local cmd="$2"
    local fix="${3:-}"

    if eval "$cmd" >/dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} $label"
        ((PASS++))
    else
        echo -e "  ${RED}✗${NC} $label"
        [ -n "$fix" ] && echo -e "    Fix: $fix"
        ((FAIL++))
    fi
}

warn() {
    local label="$1"
    local cmd="$2"
    local note="${3:-}"

    if eval "$cmd" >/dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} $label"
        ((PASS++))
    else
        echo -e "  ${YELLOW}~${NC} $label (optional)"
        [ -n "$note" ] && echo -e "    Note: $note"
        ((WARN++))
    fi
}

echo "qmd Doctor"
echo "=========="
echo ""

# 1. Core installation
echo "Core:"
check "bun installed" "command -v bun" "curl -fsSL https://bun.sh/install | bash"
check "qmd binary found" "command -v qmd" "bun install -g github:tobi/qmd"
check "qmd runs" "qmd --help" "Reinstall: bun install -g github:tobi/qmd"
check "sqlite installed" "command -v sqlite3" "brew install sqlite"

echo ""

# 2. Collections
echo "Collections:"
if command -v qmd >/dev/null 2>&1; then
    COLLECTIONS=$(qmd collection list 2>/dev/null || echo "")
    if [ -n "$COLLECTIONS" ]; then
        echo -e "  ${GREEN}✓${NC} Collections found:"
        echo "$COLLECTIONS" | while read -r line; do
            echo "    $line"
        done
        ((PASS++))
    else
        echo -e "  ${RED}✗${NC} No collections indexed"
        echo "    Fix: qmd collection add /path/to/docs --name my-project && qmd update"
        ((FAIL++))
    fi
else
    echo -e "  ${RED}✗${NC} Cannot check (qmd not installed)"
    ((FAIL++))
fi

echo ""

# 3. Claude Code hook
echo "Claude Code Hook:"
HOOK_FILE="$HOME/.claude/hooks/qmd-update.sh"
HOOK_FILE_ALT=$(find "$HOME/.claude/hooks/" -name "qmd-update*" -o -name "qmd*attention*" 2>/dev/null | head -1)
if [ -f "$HOOK_FILE" ] || [ -n "$HOOK_FILE_ALT" ]; then
    FOUND="${HOOK_FILE_ALT:-$HOOK_FILE}"
    echo -e "  ${GREEN}✓${NC} Hook script exists: $FOUND"
    ((PASS++))
else
    echo -e "  ${YELLOW}~${NC} No hook script found (optional)"
    echo "    Setup: cp ~/.claude/skills/qmd/templates/hook.sh ~/.claude/hooks/qmd-update.sh"
    ((WARN++))
fi

if [ -f "$HOME/.claude/settings.json" ]; then
    if grep -q "qmd-update" "$HOME/.claude/settings.json" 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} Hook registered in settings.json"
        ((PASS++))
    else
        echo -e "  ${YELLOW}~${NC} Hook not in settings.json (optional)"
        echo "    Setup: See ~/.claude/skills/qmd/setup/README.md section 3"
        ((WARN++))
    fi
fi

echo ""

# 4. launchd job
echo "Overnight Embeddings (launchd):"
PLIST=$(find "$HOME/Library/LaunchAgents/" -name "*qmd*" 2>/dev/null | head -1)
if [ -n "$PLIST" ]; then
    echo -e "  ${GREEN}✓${NC} Plist found: $PLIST"
    ((PASS++))

    if launchctl list 2>/dev/null | grep -q "qmd"; then
        echo -e "  ${GREEN}✓${NC} Job loaded in launchctl"
        ((PASS++))
    else
        echo -e "  ${YELLOW}~${NC} Job not loaded"
        echo "    Fix: launchctl load $PLIST"
        ((WARN++))
    fi
else
    warn "launchd plist installed" "false" "Setup: See ~/.claude/skills/qmd/setup/README.md section 4"
fi

echo ""

# 5. Optional extras
echo "Optional:"
warn "fswatch installed" "command -v fswatch" "brew install fswatch"
warn "Shell aliases" "alias qmd-update 2>/dev/null || grep -q 'qmd-update' ~/.zshrc 2>/dev/null" "Add aliases to ~/.zshrc"

echo ""
echo "=========="
echo -e "Results: ${GREEN}$PASS passed${NC}, ${RED}$FAIL failed${NC}, ${YELLOW}$WARN optional${NC}"

if [ "$FAIL" -gt 0 ]; then
    echo ""
    echo "Run the fixes above, then re-run this doctor script."
    exit 1
fi
