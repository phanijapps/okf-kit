---
type: CodeModule
title: okf_kit/code/indexer.py
description: Generated code map for okf_kit/code/indexer.py. Depends on okf_kit.code.discovery.adapter_for_path,
  okf_kit.code.managed.merge_managed, okf_kit.code.model.CodeModule, okf_kit.code.paths.concept_id,
  okf_kit.code.render.render_concept.
resource: okf_kit/code/indexer.py
tags:
- code
- python
- depends-on
source_path: okf_kit/code/indexer.py
language: python
source_hash: d0bae4269a7cf9ff53f1df7df47598e0bbf7e6919f7c15d3b210c5506395164f
managed_by: okf-code
generated_profile: compact
---
<!-- okf-code:start -->
# Overview

Generated CodeModule concept for `okf_kit/code/indexer.py`. Purpose: okf_kit/code/indexer.py is a `python` module. Role: module. high-signal symbols: `extract_module`, `index_codebase`, `_has_explicit_scope`, `_extract_discovered`, `_source_key`. Dependency context: 9 local dependencies and 2 local dependents are linked when resolvable. Impact: changes here may affect linked dependents, imported dependencies, and callers identified by generated reverse edges. This page is syntax-derived for code finding, code-logic search, and impact-analysis groundwork.

# Symbols

| Kind | Name | Lines |
|---|---|---|
| function | `extract_module` | 20-38 |
| function | `index_codebase` | 41-149 |
| function | `_has_explicit_scope` | 152-153 |
| function | `_extract_discovered` | 156-169 |
| function | `_source_key` | 172-173 |
| function | `_preflight_destinations` | 176-195 |
| function | `_preflight_existing_concepts` | 198-219 |
| function | `_write_summaries` | 222-238 |
| function | `_preflight_summary` | 241-251 |
| function | `_preflight_summary_destinations` | 254-270 |
| function | `_preflight_managed_roots` | 273-288 |
| function | `_preflight_existing_summaries` | 291-294 |
| function | `_prune_stale_generated` | 297-319 |
| function | `_remove_empty_dirs` | 322-325 |
| function | `_summary_concepts` | 328-383 |
| function | `_with_relationships` | 386-402 |
| function | `_with_reverse_relationships` | 405-435 |
| function | `_relationship_label` | 438-441 |
| function | `_module_keys` | 444-479 |
| function | `_rust_crate_keys` | 482-495 |

10 symbols omitted from compact profile.

# Relationships

Depends on:
- [okf_kit.code.discovery.adapter_for_path](/code/okf_kit/code/discovery.py.md)
- [okf_kit.code.managed.merge_managed](/code/okf_kit/code/managed.py.md)
- [okf_kit.code.model.CodeModule](/code/okf_kit/code/model.py.md)
- [okf_kit.code.paths.concept_id](/code/okf_kit/code/paths.py.md)
- [okf_kit.code.render.render_concept](/code/okf_kit/code/render.py.md)
- [okf_kit.code.treesitter.languages.LanguageAdapter](/code/okf_kit/code/treesitter/languages/__init__.py.md)
- [okf_kit.core.links.is_within](/code/okf_kit/core/links.py.md)
- [okf_kit.core.parse.split_frontmatter](/code/okf_kit/core/parse.py.md)
- [okf_kit.core.templates.init_bundle](/code/okf_kit/core/templates.py.md)
- `__future__.annotations`
- `contextlib.suppress`
- `dataclasses.replace`
- `okf_kit.code.discovery.adapters_for`
- `okf_kit.code.discovery.iter_source_files`
- `okf_kit.code.managed.split_generated`
- `okf_kit.code.model.CodeRelationship`
- `okf_kit.code.model.DiscoveredSource`
- `okf_kit.code.model.IndexResult`
- `okf_kit.code.paths.concept_path`
- `okf_kit.code.paths.safe_segment`
- `okf_kit.code.render.render_summary_concept`
- 3 imports omitted from compact profile.

Used by:
- [okf_kit/cli.py](/code/okf_kit/cli.py.md)
- [okf_kit/code/__init__.py](/code/okf_kit/code/__init__.py.md)

# Impact notes

Impact candidates on this page are syntax-derived. Treat them as a starting point for inspection, not as complete semantic proof of all callers, callees, or runtime effects.

# Citations

- Source: `okf_kit/code/indexer.py`
- Source hash: `d0bae4269a7cf9ff53f1df7df47598e0bbf7e6919f7c15d3b210c5506395164f`
<!-- okf-code:end -->
