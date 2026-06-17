---
type: Interface
title: okf serve
description: On-demand, read-only local web UI — tree, search, graph, reader (stdlib http.server + vanilla JS).
tags: [web]
---

`okf serve <bundle>` starts a localhost server (auto free port, prints the URL,
runs until Ctrl-C) — launched by an agent harness on demand, not by `okf-mcp`.
A pure `route()` router serves a JSON API over the core and a vanilla-JS SPA
(vendored marked/cytoscape/dompurify; no build step, offline):

- `/api/index`, `/api/search`, `/api/concepts/<id>`, `/api/graph` ([`core/links`](/core/links.md)), `/api/backlinks/<id>`, `/api/validate`.

Concept ids flow through `resolve_cid_path`; Markdown output is DOMPurify-sanitized.
Read-only v1; editing is next. See [architecture](/architecture.md).
