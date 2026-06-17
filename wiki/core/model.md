---
type: Module
title: core/model
description: The Concept dataclass — cid, frontmatter, body, reserved, parse diagnostics.
---
# Overview

`Concept` is the dataclass at the center of the core: it holds one parsed Markdown file. Every consumer in the codebase — parse, validate, links, search, context, the MCP server, the web UI — reads from or produces a `Concept`. Keeping it a plain dataclass with no behavior keeps the core pure and easy to test.

The fields cover identity and parse diagnostics as well as content: the concept id, the resolved file path, the bundle root, the full frontmatter mapping (all keys preserved, including extension keys), the raw Markdown body, the reserved-file flag, and two diagnostics — whether a frontmatter block was present and whether it was invalid.

# Schema

| field | meaning |
|---|---|
| `cid` | concept id (path without `.md`) |
| `frontmatter` | all keys preserved (incl. extension) |
| `body` | raw Markdown, no frontmatter |
| `reserved` | 'index' / 'log' / None |
| `frontmatter_error` | set when a block was present but invalid |
| `frontmatter_present` | True if the file opened with `---` |

Built by [`core/parse`](/core/parse.md); validated by [`core/validate`](/core/validate.md).