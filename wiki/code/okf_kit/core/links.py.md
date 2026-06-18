---
type: CodeModule
title: okf_kit/core/links.py
description: Generated code map for okf_kit/core/links.py. Depends on okf_kit.core.model.Concept.
resource: okf_kit/core/links.py
tags:
- code
- python
- depends-on
source_path: okf_kit/core/links.py
language: python
source_hash: 6a716e4e64a291c57e745b4e356260d648559b41ec9503b48d8fb11ac7091181
managed_by: okf-code
generated_profile: compact
---
<!-- okf-code:start -->
# Overview

Generated CodeModule concept for `okf_kit/core/links.py`. Purpose: okf_kit/core/links.py is a `python` module. Role: module. high-signal symbols: `is_external_target`, `is_absolute_target`, `cid_segments_valid`, `is_within`, `iter_concept_files`. Dependency context: 1 local dependencies and 11 local dependents are linked when resolvable. Impact: changes here may affect linked dependents, imported dependencies, and callers identified by generated reverse edges. This page is syntax-derived for code finding, code-logic search, and impact-analysis groundwork.

# Symbols

| Kind | Name | Lines |
|---|---|---|
| function | `is_external_target` | 27-29 |
| function | `is_absolute_target` | 32-34 |
| function | `cid_segments_valid` | 37-41 |
| function | `is_within` | 44-50 |
| function | `iter_concept_files` | 53-73 |
| function | `resolve_cid_path` | 76-90 |
| function | `extract_link_targets` | 93-105 |
| function | `_resolve_target` | 108-113 |
| function | `concept_outgoing` | 116-138 |
| function | `broken_links` | 141-158 |
| function | `build_adjacency` | 161-167 |
| function | `build_backlinks` | 170-180 |

# Relationships

Depends on:
- [okf_kit.core.model.Concept](/code/okf_kit/core/model.py.md)
- `__future__.annotations`
- `collections.abc.Iterator`
- `pathlib.Path`
- `re`

Used by:
- [okf_kit/code/discovery.py](/code/okf_kit/code/discovery.py.md)
- [okf_kit/code/indexer.py](/code/okf_kit/code/indexer.py.md)
- [okf_kit/code/paths.py](/code/okf_kit/code/paths.py.md)
- [okf_kit/code/treesitter/languages/base.py](/code/okf_kit/code/treesitter/languages/base.py.md)
- [okf_kit/core/context.py](/code/okf_kit/core/context.py.md)
- [okf_kit/core/index.py](/code/okf_kit/core/index.py.md)
- [okf_kit/core/search.py](/code/okf_kit/core/search.py.md)
- [okf_kit/core/templates.py](/code/okf_kit/core/templates.py.md)
- [okf_kit/core/validate.py](/code/okf_kit/core/validate.py.md)
- [okf_kit/mcp.py](/code/okf_kit/mcp.py.md)
- 1 dependents omitted from compact profile.

# Impact notes

Impact candidates on this page are syntax-derived. Treat them as a starting point for inspection, not as complete semantic proof of all callers, callees, or runtime effects.

# Citations

- Source: `okf_kit/core/links.py`
- Source hash: `6a716e4e64a291c57e745b4e356260d648559b41ec9503b48d8fb11ac7091181`
<!-- okf-code:end -->
