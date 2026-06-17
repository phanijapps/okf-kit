---
type: Module
title: core/parse
description: Split YAML frontmatter from Markdown body; parse concepts; serialize (SPEC §4.1).
tags: [core, parsing]
---

`split_frontmatter(text)` returns the frontmatter mapping + body:

- A valid block opens with `---` on line 1 (no leading whitespace/BOM) and closes with a later `---`.
- No block -> graceful fallback (empty frontmatter, whole text is the body).
- Present-but-invalid (non-mapping or unparseable YAML) -> records `frontmatter_error` for the validator.

`parse_concept(path, root)` builds a [`Concept`](/core/model.md) (cid, frontmatter,
body, reserved, diagnostics). `serialize_concept` round-trips all keys. The parser
never raises on malformed input — see [`core/validate`](/core/validate.md).
