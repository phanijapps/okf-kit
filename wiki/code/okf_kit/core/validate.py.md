---
type: CodeModule
title: okf_kit/core/validate.py
description: Generated code map for okf_kit/core/validate.py. Depends on okf_kit.core.links.broken_links,
  okf_kit.core.parse.parse_concept.
resource: okf_kit/core/validate.py
tags:
- code
- python
- depends-on
source_path: okf_kit/core/validate.py
language: python
source_hash: af49a63d72497d675218bfe957e10bf618c743c4f6871f83f0d91515ee9f89df
managed_by: okf-code
generated_profile: compact
---
<!-- okf-code:start -->
# Overview

Generated CodeModule concept for `okf_kit/core/validate.py`. Purpose: okf_kit/core/validate.py is a `python` model module. Role: model module. high-signal symbols: `Finding`, `Report`, `conformant`, `to_dict`, `validate_bundle`. Dependency context: 2 local dependencies and 3 local dependents are linked when resolvable. Impact: changes here may affect linked dependents, imported dependencies, and callers identified by generated reverse edges. This page is syntax-derived for code finding, code-logic search, and impact-analysis groundwork.

# Symbols

| Kind | Name | Lines |
|---|---|---|
| class | `Finding` | 36-41 |
| class | `Report` | 45-60 |
| function | `conformant` | 51-52 |
| function | `to_dict` | 54-60 |
| function | `validate_bundle` | 63-121 |
| function | `_check_concept` | 124-176 |
| function | `_check_okf_version` | 179-192 |

# Relationships

Depends on:
- [okf_kit.core.links.broken_links](/code/okf_kit/core/links.py.md)
- [okf_kit.core.parse.parse_concept](/code/okf_kit/core/parse.py.md)
- `__future__.annotations`
- `dataclasses.dataclass`
- `dataclasses.field`
- `okf_kit.core.links.cid_segments_valid`
- `okf_kit.core.links.iter_concept_files`
- `pathlib.Path`
- `typing.Any`

Used by:
- [okf_kit/cli.py](/code/okf_kit/cli.py.md)
- [okf_kit/mcp.py](/code/okf_kit/mcp.py.md)
- [okf_kit/web/server.py](/code/okf_kit/web/server.py.md)

# Impact notes

Impact candidates on this page are syntax-derived. Treat them as a starting point for inspection, not as complete semantic proof of all callers, callees, or runtime effects.

# Citations

- Source: `okf_kit/core/validate.py`
- Source hash: `af49a63d72497d675218bfe957e10bf618c743c4f6871f83f0d91515ee9f89df`
<!-- okf-code:end -->
