---
type: CodeSummary
title: repository/okf_kit
description: 'Generated area code summary for repository/okf_kit. Top dependencies:
  okf_kit.agent_install.install_agent_assets, okf_kit.code.discovery.adapter_for_path,
  okf_kit.code.indexer.extract_module, okf_kit.code.indexer.index_codebase, okf_kit.code.managed.MANAGED_END.
  Top dependents: okf_kit/agent_install.py, okf_kit/cli.py, okf_kit/code/__init__.py,
  okf_kit/code/discovery.py, okf_kit/code/indexer.py.'
tags:
- code
- summary
- impact
- area
- depends-on
- used-by
summary_level: area
managed_by: okf-code
area: okf_kit
---
<!-- okf-code:start -->
# Overview

Generated area summary for `repository/okf_kit`. Purpose: provide a low-token entry point for code search and impact analysis before opening file-level concepts.

# Key modules

- [okf_kit/core/links.py](/code/okf_kit/core/links.py.md) - module; depends on 1; used by 11; high-signal symbols: `is_external_target`, `is_absolute_target`, `cid_segments_valid`
- [okf_kit/code/indexer.py](/code/okf_kit/code/indexer.py.md) - module; depends on 9; used by 2; high-signal symbols: `extract_module`, `index_codebase`, `_has_explicit_scope`
- [okf_kit/core/parse.py](/code/okf_kit/core/parse.py.md) - model module; depends on 1; used by 9; high-signal symbols: `FrontmatterResult`, `split_frontmatter`, `parse_concept`
- [okf_kit/cli.py](/code/okf_kit/cli.py.md) - module; depends on 8; used by 0; high-signal symbols: `main`, `_build_parser`, `_dispatch`
- [okf_kit/core/context.py](/code/okf_kit/core/context.py.md) - model module; depends on 4; used by 2; high-signal symbols: `ConceptNotFound`, `__init__`, `read_concept`
- [okf_kit/core/search.py](/code/okf_kit/core/search.py.md) - model module; depends on 2; used by 4; high-signal symbols: `_tokenize`, `_fm_str`, `_fm_str_list`
- [okf_kit/mcp.py](/code/okf_kit/mcp.py.md) - model module; depends on 6; used by 0; high-signal symbols: `BundleRegistry`, `__init__`, `get`
- [okf_kit/code/discovery.py](/code/okf_kit/code/discovery.py.md) - model module; depends on 4; used by 1; high-signal symbols: `WorkspaceRepo`, `discover_repositories`, `_all_repositories`
- [okf_kit/code/model.py](/code/okf_kit/code/model.py.md) - model module; depends on 0; used by 5; high-signal symbols: `DiscoveredSource`, `CodeSymbol`, `CodeRelationship`
- [okf_kit/core/validate.py](/code/okf_kit/core/validate.py.md) - model module; depends on 2; used by 3; high-signal symbols: `Finding`, `Report`, `conformant`
- [okf_kit/web/server.py](/code/okf_kit/web/server.py.md) - model module; depends on 4; used by 1; high-signal symbols: `Response`, `_json`, `_not_found`
- [okf_kit/code/treesitter/languages/base.py](/code/okf_kit/code/treesitter/languages/base.py.md) - model module; depends on 3; used by 1; high-signal symbols: `LanguageAdapter`, `extract`, `_walk`
- [okf_kit/core/index.py](/code/okf_kit/core/index.py.md) - module; depends on 3; used by 1; high-signal symbols: `regenerate_indexes`, `_render_index`, `_str_field`
- [okf_kit/core/model.py](/code/okf_kit/core/model.py.md) - model module; depends on 0; used by 4; high-signal symbols: `Concept`
- [okf_kit/core/templates.py](/code/okf_kit/core/templates.py.md) - module; depends on 1; used by 3; high-signal symbols: `init_bundle`, `create_concept`, `_render`
- [okf_kit/code/managed.py](/code/okf_kit/code/managed.py.md) - module; depends on 1; used by 2; high-signal symbols: `merge_managed`, `split_generated`
- [okf_kit/code/paths.py](/code/okf_kit/code/paths.py.md) - module; depends on 1; used by 2; high-signal symbols: `concept_id`, `concept_path`, `safe_segment`
- [okf_kit/code/render.py](/code/okf_kit/code/render.py.md) - module; depends on 2; used by 1; high-signal symbols: `render_concept`, `render_summary_concept`, `_managed_body`
- [okf_kit/code/treesitter/languages/__init__.py](/code/okf_kit/code/treesitter/languages/__init__.py.md) - module; depends on 1; used by 2
- [okf_kit/agent_install.py](/code/okf_kit/agent_install.py.md) - model module; depends on 1; used by 1; high-signal symbols: `InstallAction`, `_Asset`, `_TargetPaths`
- 6 modules omitted from compact summary.

# Impact map

| Module | Depends | Used by | Relationship signals |
|---|---:|---:|---|
| [okf_kit/core/links.py](/code/okf_kit/core/links.py.md) | 1 | 11 | okf_kit.core.model.Concept, okf_kit/code/discovery.py, okf_kit/code/indexer.py, okf_kit/code/paths.py |
| [okf_kit/code/indexer.py](/code/okf_kit/code/indexer.py.md) | 9 | 2 | okf_kit.code.discovery.adapter_for_path, okf_kit.code.managed.merge_managed, okf_kit.code.model.CodeModule, okf_kit/cli.py, okf_kit/code/__init__.py |
| [okf_kit/core/parse.py](/code/okf_kit/core/parse.py.md) | 1 | 9 | okf_kit.core.model.Concept, okf_kit/agent_install.py, okf_kit/code/indexer.py, okf_kit/code/managed.py |
| [okf_kit/cli.py](/code/okf_kit/cli.py.md) | 8 | 0 | okf_kit.agent_install.install_agent_assets, okf_kit.code.indexer.index_codebase, okf_kit.core.context |
| [okf_kit/core/context.py](/code/okf_kit/core/context.py.md) | 4 | 2 | okf_kit.core.links.build_adjacency, okf_kit.core.model.Concept, okf_kit.core.parse.parse_concept, okf_kit/cli.py, okf_kit/mcp.py |
| [okf_kit/core/search.py](/code/okf_kit/core/search.py.md) | 2 | 4 | okf_kit.core.links.iter_concept_files, okf_kit.core.parse.parse_concept, okf_kit/cli.py, okf_kit/core/context.py, okf_kit/mcp.py |
| [okf_kit/mcp.py](/code/okf_kit/mcp.py.md) | 6 | 0 | okf_kit.core.context, okf_kit.core.links.iter_concept_files, okf_kit.core.parse.parse_concept |
| [okf_kit/code/discovery.py](/code/okf_kit/code/discovery.py.md) | 4 | 1 | okf_kit.code.model.DiscoveredSource, okf_kit.code.paths.safe_segment, okf_kit.code.treesitter.languages.ADAPTERS, okf_kit/code/indexer.py |
| [okf_kit/code/model.py](/code/okf_kit/code/model.py.md) | 0 | 5 | okf_kit/code/__init__.py, okf_kit/code/discovery.py, okf_kit/code/indexer.py |
| [okf_kit/core/validate.py](/code/okf_kit/core/validate.py.md) | 2 | 3 | okf_kit.core.links.broken_links, okf_kit.core.parse.parse_concept, okf_kit/cli.py, okf_kit/mcp.py, okf_kit/web/server.py |

12 impact candidates omitted from compact summary.

# Impact notes

Use this summary to choose a target module, then read that module at depth 0 or depth 1 for dependency and dependent context.
<!-- okf-code:end -->
