"""The ``okf-mcp`` server (FastMCP, stdio).

Exposes an OKF bundle to MCP clients (Claude Code, Antigravity, any MCP client)
as five tools — ``search``, ``read_concept``, ``validate``, ``create_concept``,
``init_bundle`` — plus an
``okf://<bundle>/concepts/<cid>.md`` resource per concept. Tools are thin
wrappers over :mod:`okf_kit.core`; the bundle is registered at startup by
directory name.

Tool descriptions are the agent trigger surface (design §11); ``docs/tools.md``
is the source of truth and a test asserts they stay in sync.
"""
from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from okf_kit.core import context as context_mod
from okf_kit.core.links import iter_concept_files
from okf_kit.core.parse import parse_concept
from okf_kit.core.search import Hit, build_index, search
from okf_kit.core.templates import create_concept, init_bundle
from okf_kit.core.validate import validate_bundle

_SEARCH_DESC = (
    "Full-text search across an OKF bundle over title/description/body/tags/type. "
    "Returns ranked hits (exact title > frontmatter > body) with a snippet. Use this "
    "FIRST to discover concepts — it returns only id/title/type/snippet/score (no full "
    "bodies), the cheap entry point of progressive context loading. Narrow with type[]/tag[]. "
    "Params: bundle (registered bundle name), query, type[] (optional), tag[] (optional), "
    "limit (default 20). Example: search(bundle='analytics', query='customer churn', "
    "type=['Metric','Table'])."
)

_READ_DESC = (
    "Read one OKF concept by id (bundle-relative path without .md, e.g. 'tables/users'): "
    "returns frontmatter + Markdown body. Set depth=0 (default) for just this concept; set "
    "depth=1..N to progressively expand the N-hop neighborhood — the concept plus concepts it "
    "links to via Markdown links, concatenated in BFS order within token_budget "
    "(default 8000). This is the progressive-context loader: start at depth 0, raise depth only "
    "if you need surrounding context; a trailing marker names any neighbors omitted. Params: "
    "bundle, concept_id, depth, token_budget. Example: read_concept(bundle='analytics', "
    "concept_id='metrics/churn', depth=1)."
)

_VALIDATE_DESC = (
    "Validate an OKF bundle against v0.1 conformance (SPEC §9). Returns "
    "{conformant, errors, warnings, info}. Errors (missing frontmatter, empty type, malformed "
    "reserved files) block conformance; warnings (missing recommended fields, broken links); "
    "info (unknown types, extension keys, nested sub-bundle markers, okf_version). Permissive — "
    "never rejects for missing optional fields/unknown types. Use before publishing or in CI. "
    "Params: bundle. Example: validate(bundle='analytics')."
)

_CREATE_DESC = (
    "Create a rich OKF concept (MCP authoring). ENFORCES A RICHNESS FLOOR: the "
    "body must be >=120 words AND contain a depth section heading (# Examples / "
    "# Schema / # API / # Citations / # Steps / # Definition / # Overview). Thin "
    "bodies are REJECTED with a message saying what is missing — enrich and "
    "retry. This is why anything created via MCP has good information by "
    "construction. Params: bundle (registered name), cid (concept id, e.g. "
    "'tables/users'), type, title, description, body (Markdown), tags (optional "
    "list). Example: create_concept(bundle='wiki', cid='core/parse', "
    "type='Module', title='core/parse', description='Frontmatter parsing.', "
    "body='...at least 120 words with an # Examples section...')."
)

_INIT_DESC = (
    "Initialize (or re-initialize) an OKF bundle root: writes index.md declaring "
    "okf_version. Idempotent — use it to (re)create a bundle before authoring "
    "concepts via create_concept. Params: bundle (registered name), okf_version "
    "(default '0.1'). Example: init_bundle(bundle='wiki')."
)


class BundleRegistry:
    """Maps a registered bundle name to its resolved root path."""

    def __init__(self, bundles: dict[str, Any]) -> None:
        self._bundles: dict[str, Path] = {
            name: Path(path).resolve() for name, path in bundles.items()
        }

    def get(self, name: str) -> Path:
        if name not in self._bundles:
            registered = ", ".join(self._bundles) or "none"
            raise KeyError(f"unknown bundle {name!r} (registered: {registered})")
        return self._bundles[name]

    def names(self) -> list[str]:
        return sorted(self._bundles)


def tool_search(
    reg: BundleRegistry,
    bundle: str,
    query: str,
    type: list[str] | None = None,
    tag: list[str] | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    index = build_index(reg.get(bundle))
    return [_hit_dict(h) for h in search(index, query, type=type, tag=tag, limit=limit)]


def tool_read_concept(
    reg: BundleRegistry,
    bundle: str,
    concept_id: str,
    depth: int = 0,
    token_budget: int = 8000,
) -> str:
    return context_mod.read_concept(
        reg.get(bundle), concept_id, depth=depth, token_budget=token_budget
    )


def tool_validate(reg: BundleRegistry, bundle: str) -> dict[str, Any]:
    return validate_bundle(reg.get(bundle)).to_dict()


# Richness floor — the mechanism that makes "created via MCP => good info".
_RICH_MIN_WORDS = 120
_RICHNESS_SECTIONS = frozenset(
    {"examples", "schema", "api", "citations", "steps", "definition", "endpoints", "overview"}
)


def _check_richness(body: str) -> None:
    """Reject thin concept bodies (too few words, or no depth section)."""
    words = len(body.split())
    sections = {
        line[2:].strip().lower() for line in body.splitlines() if line.startswith("# ")
    }
    found = sections & _RICHNESS_SECTIONS
    problems: list[str] = []
    if words < _RICH_MIN_WORDS:
        problems.append(f"{words} words (need >= {_RICH_MIN_WORDS})")
    if not found:
        problems.append(
            "no depth section (add one of: " + ", ".join(sorted(_RICHNESS_SECTIONS)) + ")"
        )
    if problems:
        raise ValueError("concept body is too thin: " + "; ".join(problems))


def tool_create_concept(
    reg: BundleRegistry,
    bundle: str,
    cid: str,
    type: str,
    title: str,
    description: str,
    body: str,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    """Create a concept via MCP, enforcing the richness floor.

    Delegates containment + atomic exclusive create to ``core.templates.create_concept``.
    """
    _check_richness(body)
    path = create_concept(
        reg.get(bundle), cid, type, title=title, description=description, tags=tags, body=body
    )
    return {"created": True, "cid": cid, "path": str(path)}


def tool_init_bundle(reg: BundleRegistry, bundle: str, okf_version: str = "0.1") -> dict[str, Any]:
    """Initialize a bundle root via MCP (idempotent)."""
    path = init_bundle(reg.get(bundle), okf_version=okf_version)
    return {"initialized": True, "path": str(path)}


def make_server(bundles: dict[str, Any]) -> FastMCP:
    """Build a FastMCP server with tools + per-concept ``okf://`` resources."""
    reg = BundleRegistry(bundles)
    server = FastMCP("okf")

    @server.tool(name="search", description=_SEARCH_DESC)
    def _search(
        bundle: str,
        query: str,
        type: list[str] | None = None,
        tag: list[str] | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        return tool_search(reg, bundle, query, type, tag, limit)

    @server.tool(name="read_concept", description=_READ_DESC)
    def _read_concept(
        bundle: str, concept_id: str, depth: int = 0, token_budget: int = 8000
    ) -> str:
        return tool_read_concept(reg, bundle, concept_id, depth, token_budget)

    @server.tool(name="validate", description=_VALIDATE_DESC)
    def _validate(bundle: str) -> dict[str, Any]:
        return tool_validate(reg, bundle)

    @server.tool(name="create_concept", description=_CREATE_DESC)
    def _create_concept(
        bundle: str,
        cid: str,
        type: str,
        title: str,
        description: str,
        body: str,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        return tool_create_concept(reg, bundle, cid, type, title, description, body, tags)

    @server.tool(name="init_bundle", description=_INIT_DESC)
    def _init_bundle(bundle: str, okf_version: str = "0.1") -> dict[str, Any]:
        return tool_init_bundle(reg, bundle, okf_version)

    _register_resources(server, reg)
    return server


def _register_resources(server: FastMCP, reg: BundleRegistry) -> None:
    def make_reader(path: Path) -> Callable[[], str]:
        # Static resource readers must take no params (FastMCP matches URI params
        # to function params); close over the path instead.
        def _reader() -> str:
            return path.read_text(encoding="utf-8")

        return _reader

    for name in reg.names():
        root = reg.get(name)
        for md in iter_concept_files(root):
            concept = parse_concept(md, root)
            if concept.reserved is not None:
                continue
            cid = concept.cid
            uri = f"okf://{name}/concepts/{cid}.md"
            title_value = concept.frontmatter.get("title")
            desc_value = concept.frontmatter.get("description")
            title = title_value if isinstance(title_value, str) else cid
            description = desc_value if isinstance(desc_value, str) else ""
            server.resource(uri, name=title, description=description)(make_reader(concept.path))


def _hit_dict(hit: Hit) -> dict[str, Any]:
    return {
        "cid": hit.cid,
        "title": hit.title,
        "type": hit.type,
        "snippet": hit.snippet,
        "score": hit.score,
    }


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        prog="okf-mcp",
        description="OKF MCP server (stdio). Registers each bundle by its directory name.",
    )
    parser.add_argument(
        "bundles", nargs="+", help="Bundle directories to serve (registered by directory name)."
    )
    args = parser.parse_args(argv)
    bundles = {Path(b).name: Path(b) for b in args.bundles}
    make_server(bundles).run()
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
