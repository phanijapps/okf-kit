---
type: Module
title: core/context
description: 'Progressive-context loader: read one concept, then expand its N-hop
  neighborhood.'
---
# Overview

`read_concept(root, cid, depth=0, token_budget=8000)` is the progressive-context primitive. At depth zero it returns the raw concept — frontmatter plus body. At depth one through N it walks the relative and absolute link neighborhood via [`core/links`](/core/links.md), concatenating the seed and its neighbors as Markdown in breadth-first order, within the token budget.

The seed concept is always included in full; neighbors are added until the budget is reached, and a trailing marker names anything omitted so the caller knows to raise depth or read a specific concept. The walk is deterministic (breadth-first, then alphabetical cid tiebreak) and cycle-safe, so the same input always yields the same output.

# Examples

```
okf read mykb tables/users                  # one concept
okf read mykb tables/users --depth 2        # concept + 2-hop neighborhood
okf read mykb tables/users --token-budget 4000
```

See [progressive context](/concepts/progressive-context.md).