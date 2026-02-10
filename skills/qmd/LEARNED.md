# qmd - Learned

<!-- Keep under 50 lines. Consolidate before adding: merge duplicates, cut stale entries, archive if needed. -->

## Installation

- (2026-02-10) Binary lives at `~/.bun/bin/qmd`. Never install to `/private/tmp/` - macOS cleans it and breaks symlinks. Fix with: `ln -sf ~/.bun/bin/qmd /usr/local/bin/qmd`
- (2026-02-10) Bun must be in PATH for all automation (hooks, launchd, watch). Always prefix with `export PATH="$HOME/.bun/bin:$PATH"`.

## Search Patterns

## Index Management

## CLAUDE.md Integration

- (2026-02-10) The "you have failed" language is necessary. Softer phrasing gets ignored.
- (2026-02-10) Forbidding Grep/Glob/Explore forces all discovery through qmd, giving ranked results instead of raw matches.
