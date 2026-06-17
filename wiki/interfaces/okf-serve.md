---
type: Interface
title: okf serve
description: 'On-demand, read-only local web UI: tree, search, graph, reader.'
---
# Overview

`okf serve <bundle>` starts a localhost HTTP server that picks a free port, prints the URL, and runs until interrupted. It is launched on demand by an agent harness when a human wants to browse the bundle visually; it is not started by `okf-mcp`. The server is stdlib-only — no new dependency — and serves a JSON API over the core plus a vanilla-JS single-page app with vendored marked, cytoscape, and dompurify, so it works fully offline with no build step.

A pure `route(method, path, root)` function maps requests to responses, which makes the router testable without sockets. Concept ids flow through `resolve_cid_path` and static paths are contained to the static directory. Markdown output is sanitized with DOMPurify before insertion.

# Examples

```
okf serve mykb            # -> http://127.0.0.1:54321
# routes: /api/index /api/search /api/concepts/<id> /api/graph /api/validate
```

Related: [architecture](/architecture.md), [`core/links`](/core/links.md).