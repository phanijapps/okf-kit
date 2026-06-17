---
type: Module
title: core/parse
description: Split YAML frontmatter from Markdown; parse concepts; serialize (SPEC
  4.1).
---
# Overview

`split_frontmatter(text)` separates a file's YAML frontmatter from its Markdown body. A valid block opens with `---` on the very first line (no leading whitespace or byte-order mark) and closes with a later `---`. When no block is present, the parser falls back gracefully — empty mapping, whole text as body. When a block is present but the YAML is unparseable or is not a mapping, it records a `frontmatter_error` rather than raising, so the validator can report it.

`parse_concept(path, root)` builds a [`Concept`](/core/model.md): cid, frontmatter, body, reserved flag, and parse diagnostics. `serialize_concept` round-trips all frontmatter keys. The parser never raises on malformed input — reporting is the validator's job.

# Examples

```
from okf_kit.core.parse import parse_concept, split_frontmatter
res = split_frontmatter("---\ntype: Table\n---\nbody")
c = parse_concept(path, root)         # -> Concept(cid, frontmatter, body, ...)
```

Related: [`core/validate`](/core/validate.md), [OKF format](/okf-format.md).