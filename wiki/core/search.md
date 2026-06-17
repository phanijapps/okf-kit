---
type: Module
title: core/search
description: Inverted-index full-text search with weighted ranking.
---
# Overview

`build_index(root)` tokenizes every non-reserved concept's title, description, tags, type, and body into a lightweight inverted index. `search(index, q, type, tag, limit)` ranks hits by an exact-title boost plus weighted term frequency: title counts most, then tags, type, description, and body. Results include a snippet with match context.

Ranking is intentionally simple and dependency-free; a future BM25 or vector ranker can swap in behind the same signature. Ordering is deterministic — score descending, then cid ascending — so results are reproducible. Search is the cheap first step of [progressive context](/concepts/progressive-context.md): it returns only ids, titles, types, and snippets, never full bodies.

# Examples

```
okf search mykb churn --type Metric --limit 10
okf search mykb "customer orders" --json
```

Consumed by [okf-mcp](/interfaces/okf-mcp.md) and [okf serve](/interfaces/okf-serve.md).