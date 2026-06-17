---
type: Module
title: core/links
description: Graph edges from relative + absolute Markdown links, with a path-containment
  guard.
---
# Overview

The OKF knowledge graph treats every Markdown link to another concept as a directed edge (SPEC 5). Both forms are edges: absolute (`/core/parse.md`, resolved against the bundle root and the recommended form) and relative (`../x.md`, resolved against the source document's directory). External links containing `://` are not edges.

`concept_outgoing`, `build_adjacency`, and `build_backlinks` derive the graph; `broken_links` feeds the validator's warnings. `extract_link_targets` returns the raw relative and absolute targets; `_resolve_target` picks the right base. All resolution is confined to the bundle root.

# Schema

| function | returns |
|---|---|
| `resolve_cid_path(root, cid)` | contained existing path or None |
| `build_adjacency(root, concepts)` | cid -> outgoing cids |
| `iter_concept_files(root)` | safe enumeration (no symlink escapes) |

See [path containment](/concepts/path-containment.md) and [core/context](/core/context.md).