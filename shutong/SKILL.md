---
name: shutong
description: >
  Expert usage of the gb (Ground Base) CLI — a local-first semantic search engine
  over document collections. Use when the user asks to: search their knowledge base,
  find documents, manage collections, add/check context, retrieve files by path or
  docid, run hybrid queries, manage the daemon, check index status, or any task
  involving the gb command. Triggers on: "gb", "ground base", "search my notes",
  "find in my docs", "knowledge base", "collection", "reindex", "embeddings".
---

# gb CLI Skill

gb is a local-first knowledge engine providing BM25, vector, and hybrid search over
markdown document collections. It uses SQLite FTS5, sqlite-vec, and node-llama-cpp.

## Critical Rules

- **Never run `gb collection add`, `gb embed`, or `gb update` automatically.** Always
  write out example commands for the user to run manually.
- **Never run `bun build --compile`** — it overwrites the shell wrapper and breaks sqlite-vec.
- **Never modify the SQLite database directly.** Use gb commands only.
- Run from source: `bun src/gb.ts <command>` or use `gb` if linked globally.

## Command Reference

### Search (read-only, safe to run)

```sh
# BM25 keyword search (fastest, <100ms)
gb search <query> [-n 10] [-c collection] [--full] [--min-score 0.3] [--json|--csv|--md|--xml|--files]

# Vector similarity search (semantic, 500-800ms, requires gb embed first)
gb vsearch <query> [-n 10] [-c collection] [--full] [--json|--csv|--md|--xml|--files]

# Hybrid search with query expansion + reranking (best quality, 3-5s)
gb query <query> [-n 10] [-c collection] [--full] [--json|--csv|--md|--xml|--files]
  [--expander api|local] [--expander-model <model>]
  [--ranker api|local|jina] [--ranker-endpoint <url>] [--ranker-count 20]
  [--context "additional context"] [--fast] [--benchmark] [--no-lex]
```

**Default limits:** 5 results for CLI output, 20 for `--json`/`--files`.
Use `--all` to return all matches. Use `--line-numbers` to add line numbers.

### Document Retrieval (read-only, safe to run)

```sh
# Get single document by path, virtual path, or docid
gb get <file>[:line] [--from <line>] [-l <lines>] [--line-numbers]
# Examples:
gb get gb://notes/readme.md          # Virtual path
gb get notes/readme.md               # Collection/path
gb get "#abc123"                      # Docid (6-char content hash)
gb get readme.md:50 -l 20            # Lines 50-69

# Get multiple documents
gb multi-get <pattern> [-l <lines>] [--max-bytes 10240] [--json|--csv|--md|--xml|--files]
# Examples:
gb multi-get "journals/2025-05*.md"  # Glob pattern
gb multi-get "#abc123, #def456"      # Comma-separated docids
```

### Collection Management (write operations — provide as examples)

```sh
gb collection list                              # List all collections (safe)
gb collection add <path> --name <n> [--mask '**/*.md']  # Index a directory
gb collection remove <name>                     # Remove collection
gb collection rename <old> <new>                # Rename collection
gb ls [collection[/path]]                       # List files (safe)
```

### Context Management

```sh
gb context list                                  # List all contexts (safe)
gb context check                                 # Find missing contexts (safe)
gb context add [path] "description"              # Add context
gb context add / "global system message"         # Global context
gb context add gb://journals/2024 "2024 entries" # Virtual path context
gb context rm <path>                             # Remove context
```

### Indexing (write operations — provide as examples)

```sh
gb update [--pull]     # Re-index all collections (--pull: git pull first)
gb embed [--force]     # Generate vector embeddings (--force: re-embed all)
```

### System

```sh
gb status              # Index status, collections, DB path (safe)
gb cleanup             # Clean orphaned data, vacuum DB

# Daemon (keeps models loaded for faster queries)
gb daemon start [--embed]   # Start (--embed: also load embedding model)
gb daemon stop              # Stop daemon
gb daemon status            # Check status, PID, uptime
gb daemon restart [--embed] # Restart

# Telemetry
gb metrics summary          # Query stats
gb metrics history [--limit 20]
gb metrics dashboard        # Interactive dashboard
gb metrics prune            # Delete old logs (30-day retention)

# MCP server for Claude Desktop/Code
gb mcp
```

### Global Options

```sh
--index <name>    # Use named index (default: "index", stored at ~/.cache/gb/<name>.sqlite)
--help, -h        # Show help
```

## Environment Variables

| Variable | Purpose | Default |
|---|---|---|
| `GB_QUERY_EXPANDER` | Query expansion backend: `local` or `api` | `local` |
| `OPENAI_API_KEY` | Required for `api` expansion | — |
| `GB_API_MODEL` | OpenAI model for expansion | `openai/gpt-oss-120b` |
| `GB_RERANK_API` | External llama.cpp reranker URL | — |
| `JINA_API_KEY` | Jina AI reranker API key | — |
| `GB_DAEMON_AUTO` | Auto-start daemon (`1` to enable) | disabled |
| `GB_DAEMON_TIMEOUT` | Daemon inactivity timeout | 30 min |
| `NO_COLOR` | Disable terminal colors | — |

## Reranker Auto-Detection Order

1. `JINA_API_KEY` set → Jina AI reranker
2. `GB_RERANK_API` set → external llama.cpp server
3. Daemon running → daemon reranker
4. Fallback → load model directly (slow cold start)

Override with `--ranker=jina|api|local`.

## Key Concepts

**Virtual paths:** `gb://collection/path` — consistent addressing across commands.

**Docids:** `#abc123` — 6-char content hash shown in search results. Use with `gb get` and `gb multi-get`.

**Context hierarchy:** Global (`/`) → collection root → nested paths. All matching contexts are joined. Use `gb context check` to find gaps.

**Search quality tiers:**
- `search` — fast keyword matching (BM25)
- `vsearch` — semantic similarity (needs embeddings)
- `query` — best quality: expansion → parallel BM25+vector → RRF fusion → LLM reranking

**Chunking:** 800 tokens/chunk, 15% overlap, smart breaks at paragraph/sentence/line boundaries.

## Typical Workflows

**Set up a new knowledge base:**
```sh
gb collection add ~/notes --name notes --mask '**/*.md'
gb context add gb://notes/ "Personal notes and journal entries"
gb embed
```

**Search effectively:**
```sh
gb search "meeting notes Q4"          # Quick keyword search
gb query "how does auth work"         # Deep semantic search
gb query "auth" -c backend --full     # Scoped + full content
```

**Investigate a search result:**
```sh
gb query "deployment process" --json  # Get docids in results
gb get "#abc123" --line-numbers       # Read the document
gb get "#abc123":50 -l 30            # Read specific section
```

**Feed results to another tool:**
```sh
gb search "api endpoints" --files     # Just file paths
gb multi-get "docs/*.md" --xml        # Bulk retrieve as XML
gb query "auth" --json | jq '.[]'     # Pipe JSON to jq
```

## File Locations

- Config: `~/.config/gb/index.yml`
- Database: `~/.cache/gb/index.sqlite`
- Models: `~/.cache/gb/models/`
- Daemon socket: `~/.cache/gb/daemon.sock`
- Daemon PID: `~/.cache/gb/daemon.pid`
- Daemon log: `~/.cache/gb/daemon.log`
