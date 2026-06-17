---
type: Overview
title: OKF format
description: An OKF bundle is a directory of Markdown concepts (YAML frontmatter + body) linked into a graph.
tags: [okf, spec]
---

A **bundle** is a directory tree of UTF-8 `.md` files. Each file is one
**concept**; its **concept id** is the path with `.md` removed (e.g.
`core/parse.md` -> `core/parse`).

- **Frontmatter** — a YAML block (`---` on line 1). `type` is the only required field; `title`/`description`/`resource`/`tags`/`timestamp` are recommended; extension keys are preserved.
- **Body** — Markdown. `# Schema` / `# Examples` / `# Citations` are conventional headings.
- **Links** — standard Markdown links are graph edges; absolute (`/core/parse.md`) is the recommended form, relative works too. See [`core/links`](/core/links.md).
- **Reserved** — `index.md` (directory listing) and `log.md` (history) are not concepts.

Conformance is permissive — see [SPEC §9](/concepts/conformance.md) and
[`core/validate`](/core/validate.md).
