
# Concept
* [Conformance (SPEC §9)](conformance.md) - A bundle is conformant iff every concept has parseable frontmatter with a non-empty type.
* [Path containment](path-containment.md) - Security — every concept id and link target is confined to the bundle root (traversal + symlink escapes rejected).
* [Progressive context](progressive-context.md) - Load the minimum and expand on demand — search then read_concept(depth=0..N) — under a token budget.
