---
type: Overview
title: Architecture
description: okf-kit is one pure Python core exposed as a CLI, an MCP server, and
  a web UI.
---
# Overview

okf-kit implements the Open Knowledge Format as agent-native tooling: one pure Python core exposed three ways — the `okf` CLI, the `okf-mcp` server, and the `okf serve` web UI. No logic is duplicated across the surfaces; each is a thin layer over `okf_kit.core`.

The core is pure — deterministic, no network, no randomness. It holds the data model (`Concept`), frontmatter parsing, the link graph, full-text search, the progressive-context loader, conformance validation, and the build primitives (`init`, type templates, index regeneration). The CLI wraps it in argparse subcommands; the MCP server wraps it as tools for agent clients; the web UI wraps it as a localhost JSON API plus a vanilla-JS SPA.

This keeps OKF's cat-a-file ethos: the on-disk Markdown is the source of truth, and every surface reads the same core.

# Examples

```
okf init mykb
okf new mykb Table tables/users --title Users
okf validate mykb
okf read mykb tables/users --depth 1
```

Surfaces: [okf CLI](/interfaces/okf-cli.md), [okf-mcp](/interfaces/okf-mcp.md), [okf serve](/interfaces/okf-serve.md).