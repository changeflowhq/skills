# building-skills - Learned

<!-- Keep under 50 lines. Consolidate before adding. -->

## Description Writing

- (2026-02-10) Description is the PRIMARY trigger mechanism. Claude reads all descriptions to decide which skill to fire. "When to use" info in the body is useless if the description doesn't trigger first.
- (2026-02-10) Good description pattern: [What] + [How/via what] + [Specific actions] + [Trigger keywords]. Front-load the trigger words.

## Structure

- (2026-02-10) `references/` loads into context (costs tokens). `scripts/` and `assets/` don't. Large templates and data should go in assets/, not references/.
- (2026-02-10) 6 separate reference files was too many. Consolidated to 1 (patterns.md). Easier to maintain, less navigation overhead.
- (2026-02-10) Production skills (animator, stealth-browser, qmd) all stayed well under 500 lines (103-114 lines). 300 is a better soft target.

## Self-Learning

- (2026-02-10) 50-line cap with dated entries and consolidation rules works well. Real skills stayed at 7-18 lines naturally.
- (2026-02-10) "Keep under 50 lines" HTML comment at top of LEARNED.md serves as a reminder during consolidation.

## Validation

- (2026-02-10) Validator should check for LEARNED.md and self-learning section in SKILL.md. Missing these is the most common gap.
- (2026-02-10) Anthropic allows only these frontmatter keys: name, description, license, allowed-tools, metadata, compatibility.
