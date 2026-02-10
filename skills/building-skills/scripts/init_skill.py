#!/usr/bin/env python3
"""
Skill Initializer - Creates a new skill with proper structure.

Usage:
    python3 init_skill.py <skill-name> --path <path>

Examples:
    python3 init_skill.py managing-google-ads --path ~/.claude/skills
    python3 init_skill.py qmd --path ~/dev/skills/skills
"""

import sys
import re
from pathlib import Path


SKILL_TEMPLATE = '''---
name: {skill_name}
description: |
  [TODO: WRITE THIS FIRST. This is the trigger mechanism - Claude reads all descriptions
  to decide which skill to fire. Pattern: What it does + How/via what + Specific actions + Trigger keywords.
  Third person. Max 1024 chars. No angle brackets.]
allowed-tools: Bash Read Write
---

# {skill_title}

## Quick Start

[TODO: Minimal working example - the simplest successful use of this skill]

## Core Operations

[TODO: Brief list of main operations. Link to references/ if detail exceeds ~20 lines per operation.]

## Workflows

### [TODO: Primary Workflow]

```
- [ ] Step 1: [Description]
- [ ] Step 2: [Description]
- [ ] Step 3: [Description]
```

## Error Reference

| Error | Cause | Fix |
|-------|-------|-----|
| [TODO] | [Cause] | [Fix] |

## Self-Learning

Read [LEARNED.md](LEARNED.md) before using this skill.

**Update LEARNED.md when you discover:**
- [TODO: List skill-specific things to record]

**Consolidation (keep under 50 lines):**
Before adding a new entry, check file length. If over 50 lines:
1. Merge duplicate/overlapping entries into single proven patterns
2. Remove entries older than 3 months that haven't been reinforced
3. Drop one-off observations that never recurred
4. Move detailed context to `LEARNED-archive.md` if worth preserving
5. Keep only entries that would change behavior - if obvious, cut it
'''

LEARNED_TEMPLATE = '''# {skill_name} - Learned

<!-- Keep under 50 lines. Consolidate before adding: merge duplicates, cut stale entries, archive if needed. -->

'''

SETUP_README = '''# {skill_title} Setup

## Required Credentials

Add to `~/.claude/settings.json`:

```json
{{
  "env": {{
    "[TODO: ENV_VAR_NAME]": "your-value"
  }}
}}
```

## How to Obtain

1. [TODO: Where to get credentials]
2. [TODO: Steps to create key/token]

## Verify

Restart Claude Code, then run:

```bash
python3 scripts/check_setup.py
```
'''

CHECK_SETUP = '''#!/usr/bin/env python3
"""Setup verification for {skill_name}."""

import os, sys

REQUIRED = [
    # TODO: Add required environment variables
    # 'MY_API_KEY',
]

missing = [v for v in REQUIRED if not os.environ.get(v)]

if not REQUIRED:
    print("No credentials configured yet. Edit scripts/check_setup.py to add required env vars.")
elif missing:
    print(f"Missing: {{', '.join(missing)}}")
    print("\\nAdd to ~/.claude/settings.json under \\"env\\"")
    print("Then restart Claude Code.")
    sys.exit(1)
else:
    print("All credentials configured.")
    for v in REQUIRED:
        val = os.environ[v]
        print(f"  {{v}}: {{val[:4]}}...")
'''


def validate_name(name):
    """Validate skill name. Returns error message or None."""
    if not re.match(r'^[a-z0-9-]+$', name):
        return "Name must be lowercase letters, digits, and hyphens only"
    if name.startswith('-') or name.endswith('-'):
        return "Name cannot start or end with hyphen"
    if '--' in name:
        return "Name cannot contain consecutive hyphens"
    if len(name) > 64:
        return f"Name too long ({len(name)} chars, max 64)"
    return None


def title_case(name):
    return ' '.join(w.capitalize() for w in name.split('-'))


def init_skill(skill_name, path):
    skill_dir = Path(path).expanduser().resolve() / skill_name

    if skill_dir.exists():
        print(f"Error: {skill_dir} already exists")
        return False

    error = validate_name(skill_name)
    if error:
        print(f"Error: {error}")
        return False

    skill_title = title_case(skill_name)

    # Create structure
    skill_dir.mkdir(parents=True)
    (skill_dir / 'scripts').mkdir()
    (skill_dir / 'references').mkdir()
    (skill_dir / 'setup').mkdir()
    (skill_dir / 'assets').mkdir()

    # Write files
    (skill_dir / 'SKILL.md').write_text(
        SKILL_TEMPLATE.format(skill_name=skill_name, skill_title=skill_title))

    (skill_dir / 'LEARNED.md').write_text(
        LEARNED_TEMPLATE.format(skill_name=skill_name))

    (skill_dir / 'setup' / 'README.md').write_text(
        SETUP_README.format(skill_title=skill_title))

    check = skill_dir / 'scripts' / 'check_setup.py'
    check.write_text(CHECK_SETUP.format(skill_name=skill_name))
    check.chmod(0o755)

    print(f"Created skill: {skill_dir}")
    print()
    print("Files:")
    for f in sorted(skill_dir.rglob('*')):
        if f.is_file():
            print(f"  {f.relative_to(skill_dir)}")
    print()
    print("Next steps:")
    print("  1. Write the description FIRST (in SKILL.md frontmatter)")
    print("  2. Complete SKILL.md body (replace TODOs)")
    print("  3. Add scripts, references, assets as needed")
    print("  4. Validate: python3 ~/.claude/skills/building-skills/scripts/validate_skill.py " + str(skill_dir))
    return True


def main():
    if len(sys.argv) < 4 or sys.argv[2] != '--path':
        print("Usage: python3 init_skill.py <skill-name> --path <path>")
        print()
        print("Examples:")
        print("  python3 init_skill.py managing-google-ads --path ~/.claude/skills")
        print("  python3 init_skill.py qmd --path ~/dev/skills/skills")
        sys.exit(1)

    sys.exit(0 if init_skill(sys.argv[1], sys.argv[3]) else 1)


if __name__ == "__main__":
    main()
