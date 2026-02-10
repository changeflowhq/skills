# qmd - Learned

## Installation

- qmd binary lives at `~/.bun/bin/qmd`. Never install to `/private/tmp/` - macOS cleans it periodically and breaks the symlink.
- If `/usr/local/bin/qmd` breaks, fix with: `ln -sf ~/.bun/bin/qmd /usr/local/bin/qmd`
- Bun must be in PATH for all automation (hooks, launchd, watch). Always prefix with `export PATH="$HOME/.bun/bin:$PATH"`.

## Search Patterns

## Index Management

## CLAUDE.md Integration

- The "you have failed" language in CLAUDE.md is necessary. Softer phrasing like "please search first" gets ignored.
- Forbidding Grep/Glob/Explore forces all discovery through qmd, which gives ranked results instead of raw matches.
