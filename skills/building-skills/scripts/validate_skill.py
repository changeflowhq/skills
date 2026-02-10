#!/usr/bin/env python3
"""
Skill Validator - Checks structure, frontmatter, self-learning, and content.

Usage:
    python3 validate_skill.py <skill-directory>

Examples:
    python3 validate_skill.py ~/.claude/skills/managing-google-ads
    python3 validate_skill.py ~/dev/skills/skills/qmd
"""

import sys
import re
from pathlib import Path

ALLOWED_FRONTMATTER_KEYS = {'name', 'description', 'license', 'allowed-tools', 'metadata', 'compatibility'}


def count_lines(path):
    return len(path.read_text().splitlines())


def parse_frontmatter(content):
    """Extract YAML frontmatter as dict. Returns (dict, error)."""
    if not content.startswith('---'):
        return None, "SKILL.md must start with YAML frontmatter (---)"

    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return None, "Invalid frontmatter - must be enclosed in ---"

    fm = {}
    current_key = None
    current_value = []

    for line in match.group(1).split('\n'):
        # Multi-line value continuation (indented)
        if current_key and (line.startswith('  ') or line.startswith('\t')):
            current_value.append(line.strip())
            continue

        # Save previous key
        if current_key:
            fm[current_key] = ' '.join(current_value).strip()
            current_key = None
            current_value = []

        # New key
        if ':' in line:
            key = line.split(':')[0].strip()
            value = ':'.join(line.split(':')[1:]).strip()
            if value == '|' or value == '>':
                current_key = key
                current_value = []
            else:
                fm[key] = value

    if current_key:
        fm[current_key] = ' '.join(current_value).strip()

    return fm, None


def validate(skill_path):
    """Validate skill. Returns (errors: list, warnings: list)."""
    path = Path(skill_path).expanduser().resolve()
    errors = []
    warnings = []

    # Directory exists
    if not path.is_dir():
        return [f"Not a directory: {path}"], []

    # SKILL.md exists
    skill_md = path / 'SKILL.md'
    if not skill_md.exists():
        return ["SKILL.md not found (required)"], []

    content = skill_md.read_text()

    # Parse frontmatter
    fm, err = parse_frontmatter(content)
    if err:
        return [err], []

    # Required fields
    if 'name' not in fm:
        errors.append("Missing 'name' in frontmatter")
    if 'description' not in fm:
        errors.append("Missing 'description' in frontmatter")

    # Validate name
    name = fm.get('name', '')
    if name:
        if not re.match(r'^[a-z0-9-]+$', name):
            errors.append(f"Name '{name}' must be kebab-case (lowercase, digits, hyphens)")
        if name.startswith('-') or name.endswith('-'):
            errors.append(f"Name '{name}' cannot start/end with hyphen")
        if '--' in name:
            errors.append(f"Name '{name}' has consecutive hyphens")
        if len(name) > 64:
            errors.append(f"Name too long ({len(name)} chars, max 64)")
        if name != path.name:
            warnings.append(f"Name '{name}' doesn't match directory '{path.name}'")

    # Validate description
    desc = fm.get('description', '')
    if desc:
        if '<' in desc or '>' in desc:
            errors.append("Description cannot contain angle brackets")
        if len(desc) > 1024:
            errors.append(f"Description too long ({len(desc)} chars, max 1024)")
        if re.search(r'\b(I |I\'|my |you |your )\b', desc, re.IGNORECASE):
            warnings.append("Description should be third person (avoid I/you/my/your)")

        # Check for trigger keywords
        trigger_phrases = ['use when', 'use for', 'use to', 'triggers on', 'invoke when']
        has_trigger = any(p in desc.lower() for p in trigger_phrases)
        if not has_trigger:
            warnings.append("Description should include trigger conditions (e.g. 'Use when...')")

    # Check for unexpected frontmatter keys
    unexpected = set(fm.keys()) - ALLOWED_FRONTMATTER_KEYS
    if unexpected:
        warnings.append(f"Unexpected frontmatter keys: {', '.join(unexpected)}")

    # SKILL.md length
    lines = count_lines(skill_md)
    if lines > 500:
        warnings.append(f"SKILL.md is {lines} lines (max 500). Split to references/")
    elif lines > 300:
        warnings.append(f"SKILL.md is {lines} lines. Consider splitting soon (max 500)")

    # TODOs remaining
    if '[TODO' in content:
        warnings.append("SKILL.md contains [TODO] markers")

    # LEARNED.md exists
    learned = path / 'LEARNED.md'
    if not learned.exists():
        errors.append("LEARNED.md not found (required for self-learning)")
    else:
        learned_lines = count_lines(learned)
        if learned_lines > 50:
            warnings.append(f"LEARNED.md is {learned_lines} lines (cap: 50). Consolidate.")

    # Self-learning section in SKILL.md
    if 'self-learning' not in content.lower() and 'learned.md' not in content:
        warnings.append("SKILL.md has no Self-Learning section linking to LEARNED.md")

    # References TOC check
    refs_dir = path / 'references'
    if refs_dir.exists():
        for ref in refs_dir.glob('*.md'):
            ref_lines = count_lines(ref)
            ref_content = ref.read_text().lower()
            if ref_lines > 100 and '## contents' not in ref_content and '## table of contents' not in ref_content:
                warnings.append(f"references/{ref.name} ({ref_lines} lines) needs a table of contents")

    # Hardcoded credentials
    sensitive = [
        (r'["\']sk-[a-zA-Z0-9]{20,}["\']', "Possible API key in SKILL.md"),
        (r'["\'][a-f0-9]{32,}["\']', "Possible token/secret in SKILL.md"),
        (r'password\s*[=:]\s*["\'][^"\']+["\']', "Possible hardcoded password"),
    ]
    for pattern, msg in sensitive:
        if re.search(pattern, content, re.IGNORECASE):
            errors.append(msg)

    # Scripts outside skill directory
    if '~/.claude/skills/scripts/' in content or '~/.claude/scripts/' in content:
        warnings.append("Scripts should be inside skill directory, not global scripts/")

    return errors, warnings


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 validate_skill.py <skill-directory>")
        sys.exit(1)

    path = sys.argv[1]
    print(f"Validating: {path}\n")

    errors, warnings = validate(path)

    if errors:
        print("ERRORS (must fix):")
        for e in errors:
            print(f"  x {e}")
        print()

    if warnings:
        print("WARNINGS (should fix):")
        for w in warnings:
            print(f"  ~ {w}")
        print()

    if not errors and not warnings:
        print("Valid. No issues found.")
    elif not errors:
        print("Valid (with warnings).")
    else:
        print("Invalid. Fix errors above.")

    sys.exit(0 if not errors else 1)


if __name__ == "__main__":
    main()
