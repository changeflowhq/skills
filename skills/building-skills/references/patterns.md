# Skill Patterns Reference

## Contents

- Script Best Practices
- Workflow Patterns
- Output Patterns
- Credential Patterns
- Hook Integration Patterns
- Testing Patterns

## Script Best Practices

### Python Scripts

**Environment:** Use system Python 3 (`/usr/bin/env python3`). No virtualenvs, no conda, no pyenv. Claude Code runs scripts directly via `python3`, so the system interpreter must have what you need.

**Shebang:** Always `#!/usr/bin/env python3` on line 1.

**Running scripts from SKILL.md:** Prefix with `source ~/.zshrc &&` to ensure PATH, aliases, and env are loaded:

```markdown
source ~/.zshrc && python3 .claude/skills/my-skill/scripts/my_script.py "arg1"
```

**Dependencies: stdlib first.** Prefer Python standard library whenever possible. Most skill scripts only need `os`, `sys`, `json`, `urllib.request`, `pathlib`, `datetime`, `base64`, `collections`. These are always available with zero setup.

**When you need third-party packages** (e.g. `requests`, `google-ads`), install them system-wide with `pip3 install`. Document required packages in `setup/README.md` and check for them in `check_setup.py`:

```python
try:
    import requests
except ImportError:
    print("Missing: requests")
    print("Fix: pip3 install requests")
    sys.exit(1)
```

**Script structure:**

```python
#!/usr/bin/env python3
"""
One-line description of what this script does.

Usage: python3 scripts/my_script.py <arg1> [--flag]
"""

import os, sys, json

# 1. Credential check (if API script)
required = ['MY_API_KEY']
missing = [v for v in required if not os.environ.get(v)]
if missing:
    print(f"Missing: {', '.join(missing)}")
    print("Add to ~/.claude/settings.json under \"env\"")
    sys.exit(1)

# 2. Argument parsing
if len(sys.argv) < 2:
    print("Usage: python3 scripts/my_script.py <arg1>")
    sys.exit(1)

# 3. Do the work
def main():
    ...

if __name__ == "__main__":
    main()
```

**Key rules:**
- Credential check FIRST, before any imports that might fail or any work
- Print human-readable output (Claude reads stdout to decide next steps)
- Exit 0 on success, exit 1 on error
- Write results to files if they're large (don't dump 500 lines to stdout)
- Use `json.dumps(data, indent=2)` for structured output Claude needs to parse

### Bash Scripts

**Shebang:** `#!/bin/bash` (not zsh - bash is more portable and predictable for scripts).

**When to use bash vs Python:**
- **Bash:** Piping CLI tools together, file operations, calling other programs, simple conditionals
- **Python:** API calls, JSON parsing, anything with data structures, anything over ~30 lines

**Structure:**

```bash
#!/bin/bash
# One-line description
# Usage: bash scripts/my_script.sh <arg>

set -euo pipefail  # Fail on errors, undefined vars, pipe failures

# Check dependencies
if ! command -v my-tool >/dev/null 2>&1; then
    echo "Missing: my-tool"
    echo "Fix: brew install my-tool"
    exit 1
fi

# Do the work
...
```

**Key rules:**
- `set -euo pipefail` at the top of every script
- Check for required commands with `command -v` before using them
- Quote all variables: `"$VAR"` not `$VAR`
- Use `exit 0` / `exit 1` for success/failure
- Background jobs with `>/dev/null 2>&1 &` when the caller doesn't need the output (e.g. index updates in hooks)

### Node.js Scripts

**Shebang:** `#!/usr/bin/env node`

**When to use:** Browser automation (Playwright), heavy async work, when the skill wraps an npm package.

**Dependencies:** Include a `package.json` in the skill directory. Run `npm install` or `bun install` in setup.

```json
{
  "name": "my-skill",
  "private": true,
  "dependencies": {
    "playwright": "^1.58.2"
  }
}
```

## Workflow Patterns

### Sequential Workflow

For fixed-step processes. Provide numbered checklists:

````markdown
## Deploy Workflow

```
- [ ] Step 1: Run tests locally
- [ ] Step 2: Build artifacts
- [ ] Step 3: Deploy to staging
- [ ] Step 4: Verify staging
- [ ] Step 5: Deploy to production
```

**Step 1: Run tests**
```bash
python scripts/run_tests.py
```
If any fail, fix before proceeding.
````

### Conditional Workflow

For branching paths based on task type:

```markdown
## Determine your task

**Creating new content?** → See [Creation Workflow](#creation)
**Editing existing content?** → See [Editing Workflow](#editing)
**Debugging an issue?** → See [references/troubleshooting.md](references/troubleshooting.md)
```

### Feedback Loop

For validation/iteration cycles:

```markdown
1. Make changes
2. Run: `python scripts/validate.py`
3. If errors, fix and return to step 2
4. Only proceed when validation passes
```

### Decision Tree

For complex routing:

```markdown
Is it an API skill?
├── Yes → needs setup/README.md with credential docs
│   ├── Has OAuth? → document refresh token flow
│   └── API key only? → simple env var pattern
└── No → skip setup/ directory
```

## Output Patterns

### Strict Template

For consistent output format. Put exact template in assets/:

````markdown
## Report Format

ALWAYS use this exact structure:

```markdown
# [Title]

## Summary
[One paragraph]

## Findings
- Finding 1
- Finding 2

## Recommendations
1. Action 1
2. Action 2
```
````

### Examples Pattern

Show input/output pairs so Claude learns the style:

```markdown
## Commit Message Format

**Example 1:**
Input: Added user authentication with JWT tokens
Output: feat(auth): implement JWT-based authentication

**Example 2:**
Input: Fixed crash when uploading large files
Output: fix(upload): handle files exceeding 100MB limit
```

### Structured Output

For JSON/YAML schemas, show the exact shape:

```markdown
## API Response Format

```json
{
  "status": "success|error",
  "data": { ... },
  "meta": {
    "total": 100,
    "page": 1
  }
}
```
```

## Credential Patterns

### How it works

Claude Code loads `~/.claude/settings.json` at startup. Any key/value pairs under `"env"` become environment variables available to all scripts via `os.environ`. This means:

1. **Secrets live in one place**: `~/.claude/settings.json` (never committed to git)
2. **Scripts read via `os.environ`**: Standard Python/Node pattern, no custom config parsing
3. **Claude Code injects them**: No `source .env` or `export` needed - they're just there
4. **Restart required**: After adding new env vars, Claude Code must restart to pick them up

```json
// ~/.claude/settings.json
{
  "env": {
    "GOOGLE_ADS_DEVELOPER_TOKEN": "xxx",
    "GOOGLE_ADS_CLIENT_ID": "xxx",
    "DATAFORSEO_LOGIN": "xxx",
    "DATAFORSEO_PASSWORD": "xxx",
    "LATE_DEV_API_KEY": "xxx"
  }
}
```

### Credential Detection Script

Every API skill should include `scripts/check_setup.py`. This runs before any API call and tells the user exactly what's missing and how to fix it:

```python
import os, sys

def check_credentials():
    required = ['MY_API_KEY', 'MY_API_SECRET']
    missing = [v for v in required if not os.environ.get(v)]

    if missing:
        print(f"Missing: {', '.join(missing)}")
        print("")
        print("Add to ~/.claude/settings.json:")
        print('{')
        print('  "env": {')
        for v in missing:
            print(f'    "{v}": "your-value-here",')
        print('  }')
        print('}')
        print("\nRestart Claude Code after adding.")
        sys.exit(1)
    else:
        print("All credentials configured.")
        for v in required:
            val = os.environ[v]
            print(f"  {v}: {val[:4]}...")

check_credentials()
```

**Important:** Every script that calls an API should import and run credential checks at the top, before doing any work. Don't let a script fail 30 seconds in because of a missing key.

### Setup Documentation

For API-heavy skills, create `setup/README.md`:

```markdown
# Skill Name Setup

## Required Credentials

Add to `~/.claude/settings.json`:

```json
{
  "env": {
    "SERVICE_API_KEY": "your-key",
    "SERVICE_API_SECRET": "your-secret"
  }
}
```

## How to Obtain

1. Go to https://service.com/api
2. Create an API key
3. Copy key and secret

## Verify

```bash
python3 scripts/check_setup.py
```
```

## Hook Integration Patterns

Skills can integrate with Claude Code's hook system for automatic behavior.

### PreToolUse Hook

Runs BEFORE a tool executes. Can block or modify the call.

**Example: Domain blocklist for WebFetch**

```bash
#!/bin/bash
# Block WebFetch for known-blocked domains
INPUT=$(cat)
URL=$(echo "$INPUT" | grep -o '"url":"[^"]*"' | cut -d'"' -f4)
DOMAIN=$(echo "$URL" | sed 's|https\?://\([^/]*\).*|\1|')

if grep -qF "$DOMAIN" ~/.claude/skills/my-skill/data/blocked-domains.txt 2>/dev/null; then
    echo "BLOCKED: $DOMAIN is known to block. Use alternative."
    exit 2  # exit 2 = block the tool call
fi
exit 0
```

### PostToolUse Hook

Runs AFTER a tool executes. Can trigger follow-up actions.

**Example: Auto-index on file edits**

```bash
#!/bin/bash
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | grep -o '"file_path":"[^"]*"' | cut -d'"' -f4)

if [[ "$FILE_PATH" == *.md ]]; then
    my-indexer update >/dev/null 2>&1 &
fi
exit 0
```

### Registering Hooks

Add to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/my-hook.sh"
          }
        ]
      }
    ]
  }
}
```

### Three-Layer Learning Pattern

For skills that learn from failures (e.g., stealth-browser):

1. **PreToolUse hook**: Blocks known-bad requests (fast, no wasted calls)
2. **PostToolUse hook**: Detects soft failures (200 + challenge page), learns domain
3. **CLAUDE.md rule**: Handles hard failures (403, timeout), directs retry

## Testing Patterns

### Multi-Model Testing

Test skills with different models - they need different levels of detail:

| Model | Behavior | Adjustment |
|-------|----------|------------|
| Haiku | Skips steps, misses conditionals | Add explicit checklists, repeat key points |
| Sonnet | Baseline - follows well | Standard detail level |
| Opus | May over-interpret | Can be more concise |

### Test Scenarios

Write 3-5 test scenarios before finalizing:

```
Scenario: User asks to create a new campaign
Input: "Create a Google Ads campaign for website monitoring"
Expected:
  1. Skill triggers from "Google Ads campaign"
  2. Checks credentials
  3. Follows campaign creation workflow
  4. Validates before submitting
```

### Doctor Scripts

For skills with external dependencies, include a health checker:

```bash
#!/bin/bash
# Check all dependencies and configuration
check() {
    if eval "$2" >/dev/null 2>&1; then
        echo "  OK: $1"
    else
        echo "  FAIL: $1"
        echo "    Fix: $3"
    fi
}

echo "Skill Health Check"
check "binary installed" "command -v my-tool" "brew install my-tool"
check "credentials set" "test -n \"\$MY_API_KEY\"" "Add MY_API_KEY to ~/.claude/settings.json"
check "index exists" "my-tool status" "Run: my-tool init"
```
