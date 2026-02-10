# qmd Command Reference

## Collection Management

```bash
# Add a directory to index
qmd collection add /path/to/docs --name my-project

# List all collections
qmd collection list

# Remove a collection
qmd collection remove my-project
```

## Indexing

```bash
# Update text index (fast, ~1 sec)
# Run after adding/editing files
qmd update

# Generate/refresh embeddings (slow, ~3-4 min)
# Required for vsearch and query commands
qmd embed

# Check index health, collection stats
qmd status
```

## Search

### Keyword Search (BM25)
Fast, no model needed. Best for exact terms.

```bash
qmd search "website change detection" --json -n 10
qmd search "topic" --files -n 20        # File paths only
```

### Semantic Search (Vector)
Finds conceptually related content even without keyword matches. Requires embeddings.

```bash
qmd vsearch "how do we position against competitors" -n 10
```

### Hybrid Search (BM25 + Vectors + Reranking)
Best quality but slowest. Uses query expansion and LLM reranking.

```bash
qmd query "what is our strategy for legal vertical" --json -n 10
```

## Document Retrieval

```bash
# Get full document by path
qmd get "grounding/strategy.md" --full

# Get by document ID (from search results)
qmd get "#42" --full

# Get multiple files by glob
qmd multi-get "targets/*.md"
```

## Common Flags

| Flag | Description |
|------|-------------|
| `-n 10` | Limit to N results |
| `--json` | JSON output |
| `--csv` | CSV output |
| `--md` | Markdown output |
| `--files` | File paths only (no content) |
| `-c name` | Filter to specific collection |
| `--full` | Full document content (with `get`) |

## Tips

- Scores below 0.3 are usually noise
- `search` is good enough for 90% of queries
- Use `vsearch` when keywords don't match the concept you want
- Use `--files` to find all files that need updating after a change
- Combine qmd with `Read` tool: qmd finds, Read gets full content
