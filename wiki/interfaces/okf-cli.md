---
type: Interface
title: okf CLI
description: The `okf` command — init, new, validate, search, read, index regen, serve.
tags: [cli]
---

A thin argparse layer over [`okf_kit.core`](/architecture.md):

| command | purpose |
|---|---|
| `okf init <dir>` | scaffold a bundle |
| `okf new <bundle> <type> <id>` | create a concept from a template ([`core/build`](/core/build.md)) |
| `okf validate <bundle>` | SPEC §9 ([`core/validate`](/core/validate.md)); exit 1 if not conformant |
| `okf search <bundle> <q>` | [`core/search`](/core/search.md) |
| `okf read <bundle> <id> --depth N` | [`core/context`](/core/context.md) |
| `okf index regen <bundle>` | [`core/build`](/core/build.md) |
| `okf serve <bundle>` | [`okf serve`](/interfaces/okf-serve.md) |

`--json` on validate/search; exit codes `0`/`1`/`2`. The agent-facing author loop
is the `okf-author` skill.
