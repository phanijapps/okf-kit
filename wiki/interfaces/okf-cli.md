---
type: Interface
title: okf CLI
description: 'The okf command: init, new, validate, search, read, index regen, serve.'
---
# Overview

The `okf` CLI is a thin argparse layer over [`okf_kit.core`](/architecture.md). It is the primary way humans and scripts build and inspect a bundle: scaffold a new bundle, create concepts from type templates, validate conformance, search, read concepts with progressive context, regenerate per-directory index files, and launch the web UI.

Build commands produce thin stubs fast; for rich, agent-mediated authoring use the MCP `create_concept` tool, which enforces a richness floor. The CLI mirrors the core one-to-one, so there is no duplicated logic between the CLI, the MCP server, and the web UI — they all call the same functions.

# Schema

| command | purpose |
|---|---|
| `okf init <dir>` | scaffold a bundle |
| `okf new <b> <type> <id>` | create a concept from a template |
| `okf validate <b>` | SPEC 9 conformance |
| `okf search <b> <q>` | full-text search |
| `okf read <b> <id> --depth N` | progressive context |
| `okf index regen <b>` | regenerate index.md files |
| `okf serve <b>` | read-only web UI |

Related: [okf-mcp](/interfaces/okf-mcp.md), [`core/build`](/core/build.md).