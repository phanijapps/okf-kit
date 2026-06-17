---
type: Module
title: core/index + core/templates
description: Build the bundle — init_bundle, create_concept (type templates), regenerate_indexes.
tags: [core, build]
---

- `init_bundle(root)` — scaffolds a root `index.md` declaring `okf_version`.
- `create_concept(root, cid, type, …)` — writes a concept from a built-in type template (Table/Metric/Runbook/Playbook/API/generic); cid-validated, parent contained, atomic exclusive create.
- `regenerate_indexes(root)` — writes per-directory `index.md` files (concepts grouped by type, SPEC §6 style).

These back the [`okf` CLI](/interfaces/okf-cli.md) build commands.
