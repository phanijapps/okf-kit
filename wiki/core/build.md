---
type: Module
title: core/build
description: 'Authoring primitives: init_bundle, create_concept (type templates),
  regenerate_indexes.'
---
# Overview

`core/build` is the authoring side of the core: the primitives that create and regenerate a bundle. It backs both the `okf` CLI build commands and the MCP write tools, so there is no duplicated logic between them.

`init_bundle(root)` scaffolds a bundle root, writing an `index.md` that declares `okf_version`. `create_concept(root, cid, type, ...)` writes a concept from a built-in type template — it validates the cid against the segment regex, contains the parent directory inside the bundle root, and uses an atomic exclusive create so an existing concept is never silently clobbered. `regenerate_indexes(root)` writes a per-directory `index.md` grouping concepts by type in the spec style.

The type templates cover the common kinds — Table, Metric, Runbook, Playbook, API — with a generic fallback, and producers can use any custom type.

# Examples

```
okf init mykb
okf new mykb Table tables/users --title Users --desc "User accounts."
okf index regen mykb
```

Related: [okf CLI](/interfaces/okf-cli.md), [path containment](/concepts/path-containment.md).