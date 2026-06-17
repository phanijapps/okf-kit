---
type: Module
title: core/validate
description: Check SPEC §9 conformance — errors, warnings, info (permissive consumer).
tags: [core, conformance]
---

`validate_bundle(root)` walks the bundle and classifies findings:

- **errors** (block conformance) — missing/unparseable frontmatter, empty `type`, malformed reserved files.
- **warnings** — missing `title`/`description`, broken links, invalid cid.
- **info** — extension keys, nested sub-bundle markers, `okf_version` status.

The consumer is permissive: it never rejects for optional fields, unknown types,
extension keys, or broken links. See [conformance](/concepts/conformance.md) and
[`core/parse`](/core/parse.md).
