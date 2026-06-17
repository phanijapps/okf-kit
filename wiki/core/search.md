---
type: Module
title: core/search
description: Inverted-index full-text search with weighted ranking (title > frontmatter > body).
tags: [core, search]
---

`build_index(root)` tokenizes every non-reserved concept's title, description,
tags, type, and body. `search(...)` ranks by an exact-title boost plus weighted
term frequency (title 5, tag 4, type 3, description 2, body 1), with `type`/`tag`
filters and snippets. Deterministic order (score desc, then cid).

Consumed by [`okf-mcp`](/interfaces/okf-mcp.md) and
[`okf serve`](/interfaces/okf-serve.md), and the first (cheap) step of
[progressive context](/concepts/progressive-context.md).
