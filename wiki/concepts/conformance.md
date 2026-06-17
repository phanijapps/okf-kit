---
type: Concept
title: Conformance (SPEC §9)
description: A bundle is conformant iff every concept has parseable frontmatter with a non-empty type.
tags: [concept, spec]
---

A bundle is **conformant** with OKF v0.1 iff:

1. every non-reserved `.md` has a parseable YAML frontmatter block;
2. every frontmatter has a non-empty `type`;
3. reserved files (`index.md`/`log.md`) follow §6/§7 structure when present.

Consumers MUST NOT reject for missing optional fields, unknown types, extension
keys, broken links, or missing `index.md`. Enforced by [`core/validate`](/core/validate.md);
see the [OKF format](/okf-format.md).
