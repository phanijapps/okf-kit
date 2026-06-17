
# Module
* [core/build](build.md) - Authoring primitives: init_bundle, create_concept (type templates), regenerate_indexes.
* [core/context](context.md) - Progressive-context loader: read one concept, then expand its N-hop neighborhood.
* [core/links](links.md) - Graph edges from relative + absolute Markdown links, with a path-containment guard.
* [core/model](model.md) - The Concept dataclass — cid, frontmatter, body, reserved, parse diagnostics.
* [core/parse](parse.md) - Split YAML frontmatter from Markdown; parse concepts; serialize (SPEC 4.1).
* [core/search](search.md) - Inverted-index full-text search with weighted ranking.
* [core/validate](validate.md) - Check SPEC 9 conformance: errors, warnings, info (permissive consumer).
