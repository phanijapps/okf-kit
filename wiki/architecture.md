---
type: Overview
title: Architecture
description: okf-kit is one pure Python core exposed as a CLI, an MCP server, and an on-demand web UI.
tags: [architecture]
---

okf-kit implements the Open Knowledge Format as **agent-native tooling**: one
pure core library with three thin presentation layers over it — no logic is
duplicated between them.

- **`okf_kit.core`** — pure, deterministic, no network/randomness: parse, validate, search, context, links, index, templates.
- **`okf_kit.cli`** — the [`okf`](/interfaces/okf-cli.md) CLI (argparse).
- **`okf_kit.mcp`** — the [`okf-mcp`](/interfaces/okf-mcp.md) server (FastMCP/stdio).
- **`okf_kit.web`** — [`okf serve`](/interfaces/okf-serve.md), a read-only web UI (stdlib http.server).

The core is the source of truth; see [`core/parse`](/core/parse.md),
[`core/links`](/core/links.md), and [progressive context](/concepts/progressive-context.md).
