---
type: CodeModule
title: okf_kit/core/search.py
description: Generated code map for okf_kit/core/search.py. Depends on okf_kit.core.links.iter_concept_files,
  okf_kit.core.parse.parse_concept.
resource: okf_kit/core/search.py
tags:
- code
- python
- depends-on
source_path: okf_kit/core/search.py
language: python
source_hash: 59b8ab06b75977935f95bf175f9dacc4d3c3d9f0e34f6d31c8c9e7c3afe937f1
managed_by: okf-code
generated_profile: compact
---
<!-- okf-code:start -->
# Overview

Generated CodeModule concept for `okf_kit/core/search.py`. Purpose: okf_kit/core/search.py is a `python` model module. Role: model module. high-signal symbols: `_tokenize`, `_fm_str`, `_fm_str_list`, `_frontmatter_text`, `Hit`. Dependency context: 2 local dependencies and 4 local dependents are linked when resolvable. Impact: changes here may affect linked dependents, imported dependencies, and callers identified by generated reverse edges. This page is syntax-derived for code finding, code-logic search, and impact-analysis groundwork.

# Symbols

| Kind | Name | Lines |
|---|---|---|
| function | `_tokenize` | 24-25 |
| function | `_fm_str` | 28-30 |
| function | `_fm_str_list` | 33-37 |
| function | `_frontmatter_text` | 40-47 |
| class | `Hit` | 51-66 |
| class | `_Doc` | 70-82 |
| class | `Index` | 86-105 |
| function | `to_dict` | 95-105 |
| function | `build_index` | 108-144 |
| function | `search` | 147-191 |
| function | `_score` | 194-210 |
| function | `_snippet` | 213-228 |

# Relationships

Depends on:
- [okf_kit.core.links.iter_concept_files](/code/okf_kit/core/links.py.md)
- [okf_kit.core.parse.parse_concept](/code/okf_kit/core/parse.py.md)
- `__future__.annotations`
- `collections.Counter`
- `dataclasses.dataclass`
- `dataclasses.field`
- `pathlib.Path`
- `re`
- `typing.Any`

Used by:
- [okf_kit/cli.py](/code/okf_kit/cli.py.md)
- [okf_kit/core/context.py](/code/okf_kit/core/context.py.md)
- [okf_kit/mcp.py](/code/okf_kit/mcp.py.md)
- [okf_kit/web/server.py](/code/okf_kit/web/server.py.md)

# Impact notes

Impact candidates on this page are syntax-derived. Treat them as a starting point for inspection, not as complete semantic proof of all callers, callees, or runtime effects.

# Citations

- Source: `okf_kit/core/search.py`
- Source hash: `59b8ab06b75977935f95bf175f9dacc4d3c3d9f0e34f6d31c8c9e7c3afe937f1`
<!-- okf-code:end -->
