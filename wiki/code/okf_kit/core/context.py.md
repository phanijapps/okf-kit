---
type: CodeModule
title: okf_kit/core/context.py
description: Generated code map for okf_kit/core/context.py. Depends on okf_kit.core.links.build_adjacency,
  okf_kit.core.model.Concept, okf_kit.core.parse.parse_concept, okf_kit.core.search.build_index.
resource: okf_kit/core/context.py
tags:
- code
- python
- depends-on
source_path: okf_kit/core/context.py
language: python
source_hash: 32fa36dbe665c23e46e9bacbeae4cc91df3d32075d5498532a263ba24e8c82f8
managed_by: okf-code
generated_profile: compact
---
<!-- okf-code:start -->
# Overview

Generated CodeModule concept for `okf_kit/core/context.py`. Purpose: okf_kit/core/context.py is a `python` model module. Role: model module. high-signal symbols: `ConceptNotFound`, `__init__`, `read_concept`, `_bfs_levels`, `_load_concepts`. Dependency context: 4 local dependencies and 2 local dependents are linked when resolvable. Impact: changes here may affect linked dependents, imported dependencies, and callers identified by generated reverse edges. This page is syntax-derived for code finding, code-logic search, and impact-analysis groundwork.

# Symbols

| Kind | Name | Lines |
|---|---|---|
| class | `ConceptNotFound` | 20-27 |
| function | `__init__` | 23-27 |
| function | `read_concept` | 30-83 |
| function | `_bfs_levels` | 86-101 |
| function | `_load_concepts` | 104-110 |
| function | `_suggest` | 113-115 |
| function | `_estimate` | 118-119 |

# Relationships

Depends on:
- [okf_kit.core.links.build_adjacency](/code/okf_kit/core/links.py.md)
- [okf_kit.core.model.Concept](/code/okf_kit/core/model.py.md)
- [okf_kit.core.parse.parse_concept](/code/okf_kit/core/parse.py.md)
- [okf_kit.core.search.build_index](/code/okf_kit/core/search.py.md)
- `__future__.annotations`
- `okf_kit.core.links.iter_concept_files`
- `okf_kit.core.links.resolve_cid_path`
- `okf_kit.core.search.search`
- `pathlib.Path`

Used by:
- [okf_kit/cli.py](/code/okf_kit/cli.py.md)
- [okf_kit/mcp.py](/code/okf_kit/mcp.py.md)

# Impact notes

Impact candidates on this page are syntax-derived. Treat them as a starting point for inspection, not as complete semantic proof of all callers, callees, or runtime effects.

# Citations

- Source: `okf_kit/core/context.py`
- Source hash: `32fa36dbe665c23e46e9bacbeae4cc91df3d32075d5498532a263ba24e8c82f8`
<!-- okf-code:end -->
