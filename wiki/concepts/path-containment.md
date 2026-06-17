---
type: Concept
title: Path containment
description: 'Security: every concept id and link target is confined to the bundle
  root (traversal and symlink escapes rejected).'
---
# Overview

The MCP server and CLI resolve caller-supplied concept ids and link targets to filesystem paths, so path handling is a security boundary. okf-kit defends it in depth, on both the read path and the write path.

The first layer is lexical: concept ids must match a path-segment regex, which rejects dot-dot and leading slashes. The second layer is semantic: every resolved path is checked with `is_within` against the bundle root, so dot-dot traversal and symlink escapes are rejected. This applies to reads (`resolve_cid_path`), writes (`create_concept` resolves the parent and uses an atomic exclusive create), and enumeration (`iter_concept_files` skips anything that resolves outside the root).

The read path is the most exercised and best-tested part of the codebase; the write path and enumeration reuse the same containment primitive. See [`core/links`](/core/links.md) and [`core/build`](/core/build.md).

# Examples

```
resolve_cid_path(root, "../../etc/passwd")  # -> None
create_concept(..., cid="../escape", ...)    # -> rejected
```

Related: [okf-mcp](/interfaces/okf-mcp.md).