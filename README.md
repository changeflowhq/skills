# Claude Skills

A collection of skills for [Claude Code](https://claude.ai/claude-code).

## Skills

### [animator](skills/animator/)

Create short mp4 videos from HTML/CSS/JS animations. Write CSS animations normally, the recorder pauses them and steps frame-by-frame at 30fps. JS-driven animation works too via a `renderFrame()` callback. Stitches frames into h264 mp4 via ffmpeg.

- Deterministic, smooth, pixel-perfect output
- CSS easing, delays, fill-mode all work
- Supports staggered entrances, scene transitions, typewriter effects
- [Full docs and examples](skills/animator/README.md)

### [building-skills](skills/building-skills/)

The meta-skill. Create, restructure, and validate Claude Code skills following production-tested patterns. Includes an init script that scaffolds the full directory structure and a validator that catches common mistakes.

- Directory structure, YAML frontmatter, progressive disclosure
- Credential management via `~/.claude/settings.json` env vars
- Self-learning with LEARNED.md and 50-line consolidation
- Script best practices (Python, Bash, Node)
- [Patterns reference](skills/building-skills/references/patterns.md)

### [qmd](skills/qmd/)

Local semantic search for markdown knowledge bases using [tobi/qmd](https://github.com/tobi/qmd). Two-tier indexing: BM25 keyword search updates instantly on every edit (via Claude Code hook), vector embeddings refresh overnight (via launchd). Turns any folder of markdown into a searchable knowledge base.

- `qmd search` for keyword matching, `qmd vsearch` for semantic search
- Claude Code hook auto-indexes after every Edit/Write
- launchd job refreshes embeddings at midnight
- CLAUDE.md integration pattern forces Claude to search before answering
- [Setup guide and indexing strategy](skills/qmd/setup/README.md)

### [stealth-browser](skills/stealth-browser/)

Invisible Chrome automation for web scraping via CDP. Launches your real Chrome install completely hidden, sends commands via Chrome DevTools Protocol. Sites see a normal browser with real extensions, no detectable automation. Learns which domains block and skips straight to stealth on future requests.

- Falls back automatically when WebFetch gets blocked (403, Cloudflare, bot protection)
- Three-layer learning: PreToolUse hook, PostToolUse hook, CLAUDE.md rule
- Ships with uBlock Origin Lite and cookie banner dismisser
- macOS only
- [Full docs, architecture, and hook setup](skills/stealth-browser/README.md)

## Install

```bash
npx skills add changeflowhq/skills
```

## License

MIT
