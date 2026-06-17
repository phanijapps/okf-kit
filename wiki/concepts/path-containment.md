---
type: Concept
title: Path containment
description: Security — every concept id and link target is confined to the bundle root (traversal + symlink escapes rejected).
tags: [concept, security]
---

The MCP server and CLI resolve caller-supplied concept ids and link targets to
filesystem paths. Defense in depth:

- **lexical** — concept ids match a path-segment regex (no `..` or leading `/`).
- **semantic** — every resolved path is checked `is_within` the bundle root; symlink escapes and `..` traversal are rejected, on both the read path (`resolve_cid_path`) and the write path (`create_concept`), and during enumeration (`iter_concept_files`).

See [`core/links`](/core/links.md) and [`core/build`](/core/build.md).
