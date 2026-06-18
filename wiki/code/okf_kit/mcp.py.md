---
type: CodeModule
title: okf_kit/mcp.py
description: Generated code map for okf_kit/mcp.py. Depends on okf_kit.core.context,
  okf_kit.core.links.iter_concept_files, okf_kit.core.parse.parse_concept, okf_kit.core.search.Hit,
  okf_kit.core.templates.create_concept.
resource: okf_kit/mcp.py
tags:
- code
- python
- depends-on
source_path: okf_kit/mcp.py
language: python
source_hash: 4cb8cfedb30e242ebd303ee21eb3ab8d5627c2bb89a2e746f3aa97622b04d553
managed_by: okf-code
generated_profile: compact
---
<!-- okf-code:start -->
# Overview

Generated CodeModule concept for `okf_kit/mcp.py`. Purpose: okf_kit/mcp.py is a `python` model module. Role: model module. high-signal symbols: `BundleRegistry`, `__init__`, `get`, `names`, `tool_search`. Dependency context: 6 local dependencies and 0 local dependents are linked when resolvable. Impact: changes here may affect linked dependents, imported dependencies, and callers identified by generated reverse edges. This page is syntax-derived for code finding, code-logic search, and impact-analysis groundwork.

# Symbols

| Kind | Name | Lines |
|---|---|---|
| class | `BundleRegistry` | 201-216 |
| function | `__init__` | 204-207 |
| function | `get` | 209-213 |
| function | `names` | 215-216 |
| function | `tool_search` | 219-228 |
| function | `tool_read_concept` | 231-240 |
| function | `tool_validate` | 243-244 |
| function | `_check_richness` | 254-269 |
| function | `tool_create_concept` | 272-307 |
| function | `tool_init_bundle` | 310-315 |
| function | `make_server` | 318-403 |
| function | `_search` | 329-336 |
| function | `_read_concept` | 344-350 |
| function | `_validate` | 358-359 |
| function | `_create_concept` | 372-386 |
| function | `_init_bundle` | 399-400 |
| function | `_register_resources` | 406-427 |
| function | `make_reader` | 407-413 |
| function | `_reader` | 410-411 |
| function | `_hit_dict` | 430-437 |

1 symbols omitted from compact profile.

# Relationships

Depends on:
- [okf_kit.core.context](/code/okf_kit/core/context.py.md)
- [okf_kit.core.links.iter_concept_files](/code/okf_kit/core/links.py.md)
- [okf_kit.core.parse.parse_concept](/code/okf_kit/core/parse.py.md)
- [okf_kit.core.search.Hit](/code/okf_kit/core/search.py.md)
- [okf_kit.core.templates.create_concept](/code/okf_kit/core/templates.py.md)
- [okf_kit.core.validate.validate_bundle](/code/okf_kit/core/validate.py.md)
- `__future__.annotations`
- `argparse`
- `collections.abc.Callable`
- `mcp.server.fastmcp.FastMCP`
- `mcp.types.ToolAnnotations`
- `okf_kit.core.search.build_index`
- `okf_kit.core.search.search`
- `okf_kit.core.templates.init_bundle`
- `pathlib.Path`
- `pydantic.Field`
- `typing.Annotated`
- `typing.Any`

# Impact notes

Impact candidates on this page are syntax-derived. Treat them as a starting point for inspection, not as complete semantic proof of all callers, callees, or runtime effects.

# Citations

- Source: `okf_kit/mcp.py`
- Source hash: `4cb8cfedb30e242ebd303ee21eb3ab8d5627c2bb89a2e746f3aa97622b04d553`
<!-- okf-code:end -->
