---
type: Concept
title: Progressive context
description: Load the minimum and expand on demand — search then read_concept(depth=0..N) — under a token budget.
tags: [concept, context]
---

Agents load the minimum they need and expand on demand:

1. **`search`** — a cheap hit list (id/title/type/snippet/score).
2. **`read_concept(depth=0)`** — one full concept.
3. **`read_concept(depth=1..N)`** — concept + N-hop neighborhood.

The seed is always full; neighbors are added in BFS order within `token_budget`,
with a trailing marker naming any omissions. Deterministic. Implemented in
[`core/context`](/core/context.md); exposed by [`okf-mcp`](/interfaces/okf-mcp.md).
