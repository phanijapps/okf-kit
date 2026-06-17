---
type: Interface
title: okf-mcp
description: MCP server (FastMCP/stdio) exposing search, read_concept, validate + okf:// resources.
tags: [mcp]
---

`okf-mcp <bundle>` registers the bundle (by directory name) and exposes it to any
MCP client (Claude Code, Antigravity) over stdio:

- **`search`** — [`core/search`](/core/search.md).
- **`read_concept`** — [`core/context`](/core/context.md); the [progressive context](/concepts/progressive-context.md) loader via `depth`.
- **`validate`** — [`core/validate`](/core/validate.md).
- **resources** — `okf://<bundle>/concepts/<id>.md` per concept.

It is read + validate; building is done via the [`okf` CLI](/interfaces/okf-cli.md).
