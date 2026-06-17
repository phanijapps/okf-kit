---
type: Module
title: core/context
description: Progressive-context loader — read one concept, then expand its N-hop link neighborhood.
tags: [core, context]
---

`read_concept(root, cid, depth=0, token_budget=8000)`:

- `depth=0` -> the raw concept (frontmatter + body).
- `depth=1..N` -> the seed plus its N-hop neighborhood via [`core/links`](/core/links.md), concatenated in BFS order within `token_budget`, with a trailing marker naming any omissions.

Deterministic and cycle-safe. This is the mechanism behind
[progressive context](/concepts/progressive-context.md).
