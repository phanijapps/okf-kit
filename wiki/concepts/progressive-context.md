---
type: Concept
title: Progressive context
description: 'Load the minimum and expand on demand: search then read_concept depth
  0..N, under a token budget.'
---
# Overview

Progressive context is OKF's progressive-disclosure principle applied to the LLM context window: an agent loads the minimum it needs and expands on demand, always under a token budget. It is the antidote to dumping a whole knowledge base into a prompt.

The funnel has three steps. First, `search` returns a cheap hit list — id, title, type, snippet, score — with no full bodies. Second, `read_concept` at depth zero returns one full concept. Third, `read_concept` at depth one through N returns the concept plus its N-hop link neighborhood, concatenated in breadth-first order within the token budget, with a trailing marker naming any omissions.

The seed concept is always included in full; ordering is deterministic; the walk is cycle-safe. Implemented in [`core/context`](/core/context.md); exposed by [`okf-mcp`](/interfaces/okf-mcp.md).

# Examples

```
search(bundle='mykb', query='churn')
read_concept(bundle='mykb', concept_id='metrics/churn', depth=1)
```

Related: [`core/search`](/core/search.md).