---
type: Interface
title: okf-mcp
description: 'MCP server (FastMCP, stdio): search, read_concept, validate, create_concept,
  init_bundle + okf resources.'
---
# Overview

`okf-mcp <bundle>` registers a bundle by its directory name and exposes it to any MCP client — Claude Code, Antigravity, or any stdio client — as five tools plus a resource per concept. It is the universal layer for agent consumption and, now, agent authoring.

The read tools are `search`, `read_concept` (the progressive-context loader via `depth`), and `validate`. The write tools are `init_bundle` (create the bundle root) and `create_concept`, which enforces a richness floor — at least 120 words and a depth section — so anything authored through MCP is rich by construction; thin bodies are rejected with an actionable message. Resources use the `okf://<bundle>/concepts/<id>.md` scheme.

# Examples

```
okf-mcp mykb                       # stdio server over the mykb bundle
# in an MCP client:
search(bundle='mykb', query='churn')
create_concept(bundle='mykb', cid='core/parse', type='Module', ...)
```

Related: [okf CLI](/interfaces/okf-cli.md), [`core/context`](/core/context.md).