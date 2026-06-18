---
type: CodeModule
title: okf_kit/cli.py
description: Generated code map for okf_kit/cli.py. Depends on okf_kit.agent_install.install_agent_assets,
  okf_kit.code.indexer.index_codebase, okf_kit.core.context, okf_kit.core.index.regenerate_indexes,
  okf_kit.core.search.build_index.
resource: okf_kit/cli.py
tags:
- code
- python
- depends-on
source_path: okf_kit/cli.py
language: python
source_hash: 725e509380a6aee036f32ee0af8c880832e0ab3a8f3dbf2e259baf8882fb8048
managed_by: okf-code
generated_profile: compact
---
<!-- okf-code:start -->
# Overview

Generated CodeModule concept for `okf_kit/cli.py`. Purpose: okf_kit/cli.py is a `python` module. Role: module. high-signal symbols: `main`, `_build_parser`, `_dispatch`, `_cmd_init`, `_cmd_new`. Dependency context: 8 local dependencies and 0 local dependents are linked when resolvable. Impact: changes here may affect linked dependents, imported dependencies, and callers identified by generated reverse edges. This page is syntax-derived for code finding, code-logic search, and impact-analysis groundwork.

# Symbols

| Kind | Name | Lines |
|---|---|---|
| function | `main` | 22-37 |
| function | `_build_parser` | 40-183 |
| function | `_dispatch` | 186-205 |
| function | `_cmd_init` | 208-211 |
| function | `_cmd_new` | 214-224 |
| function | `_cmd_validate` | 227-233 |
| function | `_cmd_search` | 236-249 |
| function | `_cmd_read` | 252-260 |
| function | `_cmd_index_regen` | 263-266 |
| function | `_cmd_code` | 269-272 |
| function | `_cmd_code_index` | 275-293 |
| function | `_cmd_serve` | 296-300 |
| function | `_cmd_agent` | 303-306 |
| function | `_cmd_agent_install` | 309-321 |
| function | `_print_report` | 324-333 |
| function | `_print_hits` | 336-342 |
| function | `_hit_dict` | 345-352 |

# Relationships

Depends on:
- [okf_kit.agent_install.install_agent_assets](/code/okf_kit/agent_install.py.md)
- [okf_kit.code.indexer.index_codebase](/code/okf_kit/code/indexer.py.md)
- [okf_kit.core.context](/code/okf_kit/core/context.py.md)
- [okf_kit.core.index.regenerate_indexes](/code/okf_kit/core/index.py.md)
- [okf_kit.core.search.build_index](/code/okf_kit/core/search.py.md)
- [okf_kit.core.templates.TEMPLATE_TYPES](/code/okf_kit/core/templates.py.md)
- [okf_kit.core.validate.Report](/code/okf_kit/core/validate.py.md)
- [okf_kit.web.server.serve](/code/okf_kit/web/server.py.md)
- `__future__.annotations`
- `argparse`
- `json`
- `okf_kit.core.context.ConceptNotFound`
- `okf_kit.core.search.search`
- `okf_kit.core.templates.create_concept`
- `okf_kit.core.templates.init_bundle`
- `okf_kit.core.validate.validate_bundle`
- `pathlib.Path`
- `sys`
- `typing.Any`

# Impact notes

Impact candidates on this page are syntax-derived. Treat them as a starting point for inspection, not as complete semantic proof of all callers, callees, or runtime effects.

# Citations

- Source: `okf_kit/cli.py`
- Source hash: `725e509380a6aee036f32ee0af8c880832e0ab3a8f3dbf2e259baf8882fb8048`
<!-- okf-code:end -->
