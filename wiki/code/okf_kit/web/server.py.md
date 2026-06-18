---
type: CodeModule
title: okf_kit/web/server.py
description: Generated code map for okf_kit/web/server.py. Depends on okf_kit.core.links.(
  build_adjacency, okf_kit.core.parse.parse_concept, okf_kit.core.search.Hit, okf_kit.core.validate.validate_bundle.
resource: okf_kit/web/server.py
tags:
- code
- python
- depends-on
source_path: okf_kit/web/server.py
language: python
source_hash: e582306fd640e45ff18fb09c39db587ce84af61bcfe33aef733433977fb4a9fb
managed_by: okf-code
generated_profile: compact
---
<!-- okf-code:start -->
# Overview

Generated CodeModule concept for `okf_kit/web/server.py`. Purpose: okf_kit/web/server.py is a `python` model module. Role: model module. high-signal symbols: `Response`, `_json`, `_not_found`, `route`, `_int`. Dependency context: 4 local dependencies and 1 local dependents are linked when resolvable. Impact: changes here may affect linked dependents, imported dependencies, and callers identified by generated reverse edges. This page is syntax-derived for code finding, code-logic search, and impact-analysis groundwork.

# Symbols

| Kind | Name | Lines |
|---|---|---|
| class | `Response` | 34-37 |
| function | `_json` | 40-43 |
| function | `_not_found` | 46-47 |
| function | `route` | 50-71 |
| function | `_int` | 74-78 |
| function | `_api_index` | 81-85 |
| function | `_api_graph` | 88-107 |
| function | `_api_search` | 110-114 |
| function | `_api_concept` | 117-136 |
| function | `_backlinks` | 139-143 |
| function | `_hit_dict` | 146-153 |
| function | `_as_str` | 156-157 |
| function | `_static` | 160-173 |
| function | `_serve_file` | 176-178 |
| function | `make_handler` | 181-197 |
| class | `Handler` | 185-195 |
| function | `do_GET` | 186-192 |
| function | `log_message` | 194-195 |
| function | `serve` | 200-212 |

# Relationships

Depends on:
- [okf_kit.core.links.( build_adjacency](/code/okf_kit/core/links.py.md)
- [okf_kit.core.parse.parse_concept](/code/okf_kit/core/parse.py.md)
- [okf_kit.core.search.Hit](/code/okf_kit/core/search.py.md)
- [okf_kit.core.validate.validate_bundle](/code/okf_kit/core/validate.py.md)
- `__future__.annotations`
- `dataclasses.dataclass`
- `http.server.BaseHTTPRequestHandler`
- `http.server.ThreadingHTTPServer`
- `json`
- `mimetypes`
- `okf_kit.core.links.)`
- `okf_kit.core.links.build_backlinks`
- `okf_kit.core.links.iter_concept_files`
- `okf_kit.core.links.resolve_cid_path`
- `okf_kit.core.search.build_index`
- `okf_kit.core.search.search`
- `pathlib.Path`
- `typing.Any`
- `urllib.parse.parse_qs`
- `urllib.parse.unquote`
- 1 imports omitted from compact profile.

Used by:
- [okf_kit/cli.py](/code/okf_kit/cli.py.md)

# Impact notes

Impact candidates on this page are syntax-derived. Treat them as a starting point for inspection, not as complete semantic proof of all callers, callees, or runtime effects.

# Citations

- Source: `okf_kit/web/server.py`
- Source hash: `e582306fd640e45ff18fb09c39db587ce84af61bcfe33aef733433977fb4a9fb`
<!-- okf-code:end -->
