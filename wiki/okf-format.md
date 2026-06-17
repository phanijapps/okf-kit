---
type: Overview
title: OKF format
description: An OKF bundle is a directory of Markdown concepts (YAML frontmatter +
  body) linked into a graph.
---
# Overview

A bundle is a directory tree of UTF-8 Markdown files. Each file is one concept; its concept id is the file path with `.md` removed (for example `core/parse.md` becomes `core/parse`). Concepts are cross-linked with standard Markdown links into a knowledge graph.

The frontmatter is a YAML block delimited by `---` on the first line. The only required field is `type`; `title`, `description`, `resource`, `tags`, and `timestamp` are recommended; producers may add any extension keys, which consumers preserve. The body is free-form Markdown; `# Schema`, `# Examples`, and `# Citations` are conventional headings.

Conformance is deliberately permissive: consumers must not reject a bundle for missing optional fields, unknown types, extension keys, or broken links. See [conformance](/concepts/conformance.md) and [`core/validate`](/core/validate.md).

# Examples

```
---
type: Table
title: Orders
description: One row per order.
---
# Schema
| order_id | STRING | unique id |
```

Links: [core/parse](/core/parse.md), [core/links](/core/links.md).