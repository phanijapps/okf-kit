---
type: CodeModule
title: okf_kit/agent_install.py
description: Generated code map for okf_kit/agent_install.py. Depends on okf_kit.core.parse.split_frontmatter.
resource: okf_kit/agent_install.py
tags:
- code
- python
- depends-on
source_path: okf_kit/agent_install.py
language: python
source_hash: f83ee00b6b12ef30323e6e49f1279e9d07b6f59a57891ce44d34d33595594beb
managed_by: okf-code
generated_profile: compact
---
<!-- okf-code:start -->
# Overview

Generated CodeModule concept for `okf_kit/agent_install.py`. Purpose: okf_kit/agent_install.py is a `python` model module. Role: model module. high-signal symbols: `InstallAction`, `_Asset`, `_TargetPaths`, `_StagedSkillWrite`, `install_agent_assets`. Dependency context: 1 local dependencies and 1 local dependents are linked when resolvable. Impact: changes here may affect linked dependents, imported dependencies, and callers identified by generated reverse edges. This page is syntax-derived for code finding, code-logic search, and impact-analysis groundwork.

# Symbols

| Kind | Name | Lines |
|---|---|---|
| class | `InstallAction` | 35-40 |
| class | `_Asset` | 44-47 |
| class | `_TargetPaths` | 51-54 |
| class | `_StagedSkillWrite` | 58-61 |
| function | `install_agent_assets` | 64-111 |
| function | `skill_root` | 114-116 |
| function | `manifest_path` | 119-121 |
| function | `_check_target` | 124-127 |
| function | `_check_scope` | 130-133 |
| function | `_target_paths` | 136-144 |
| function | `_is_okf_bundle_root` | 147-155 |
| function | `_inside_okf_bundle` | 158-160 |
| function | `_assets` | 163-171 |
| function | `_asset_for_target` | 174-176 |
| function | `_plan_actions` | 179-225 |
| function | `_read_manifest` | 228-271 |
| function | `_manifest_action` | 274-277 |
| function | `_stage_skill_writes` | 280-312 |
| function | `_commit_skill_writes` | 315-325 |
| function | `_cleanup_staged_skill_writes` | 328-332 |

17 symbols omitted from compact profile.

# Relationships

Depends on:
- [okf_kit.core.parse.split_frontmatter](/code/okf_kit/core/parse.py.md)
- `__future__.annotations`
- `contextlib.suppress`
- `dataclasses.dataclass`
- `hashlib`
- `importlib.resources`
- `json`
- `pathlib.Path`
- `typing.Any`
- `typing.Literal`

Used by:
- [okf_kit/cli.py](/code/okf_kit/cli.py.md)

# Impact notes

Impact candidates on this page are syntax-derived. Treat them as a starting point for inspection, not as complete semantic proof of all callers, callees, or runtime effects.

# Citations

- Source: `okf_kit/agent_install.py`
- Source hash: `f83ee00b6b12ef30323e6e49f1279e9d07b6f59a57891ce44d34d33595594beb`
<!-- okf-code:end -->
