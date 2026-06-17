---
type: Module
title: core/model
description: The Concept dataclass — cid, path, frontmatter, body, reserved, parse diagnostics.
tags: [core, model]
---

`Concept` holds one parsed `.md` file:

| field | meaning |
|---|---|
| `cid` | concept id (path without `.md`) |
| `frontmatter` | all keys preserved (incl. extension keys) |
| `body` | raw Markdown, no frontmatter |
| `reserved` | `'index'` / `'log'` / `None` |
| `frontmatter_error` | set when a frontmatter block was present but invalid |
| `frontmatter_present` | `True` if the file opened with `---` |

Built and populated by [`core/parse`](/core/parse.md).
