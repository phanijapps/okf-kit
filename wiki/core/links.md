---
type: Module
title: core/links
description: Build graph edges from relative + absolute Markdown links, with a path-containment guard.
tags: [core, graph, security]
---

The OKF knowledge graph: every Markdown link to another concept is a directed
edge (SPEC §5). Both forms are edges:

- **absolute** (`/core/parse.md`) — resolved against the bundle root (the recommended form).
- **relative** (`../x.md`) — resolved against the source document's directory.
- external (`://`) links are not edges.

`concept_outgoing` / `build_adjacency` / `build_backlinks` derive the graph;
`broken_links` feeds the validator's warnings. All resolution is **confined to
the bundle root** — see [path containment](/concepts/path-containment.md). The
edges power [progressive context](/core/context.md) and the
[`okf serve`](/interfaces/okf-serve.md) graph view.
