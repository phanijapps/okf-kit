"""Render source-code facts as OKF Markdown concepts."""
from __future__ import annotations

import yaml

from okf_kit.code.managed import MANAGED_END, MANAGED_START
from okf_kit.code.model import CodeModule, CodeSymbol

_COMPACT_SYMBOL_LIMIT = 20
_COMPACT_IMPORT_LIMIT = 20
_COMPACT_RELATIONSHIP_LIMIT = 10
_COMPACT_HINT_LIMIT = 5


def render_concept(module: CodeModule) -> str:
    """Render a ``CodeModule`` as OKF Markdown.

    Args:
        module: Extracted code module facts and relationships.

    Returns:
        Markdown document with YAML frontmatter and a managed generated body.
    """

    dependency_tags = (
        ["depends-on"]
        if any(relationship.kind == "depends_on" for relationship in module.relationships)
        else []
    )
    frontmatter = {
        "type": "CodeModule",
        "title": _title(module),
        "description": _description(module),
        "resource": _resource(module),
        "tags": [
            "code",
            module.language,
            *([module.repo_id] if module.repo_id else []),
            *dependency_tags,
        ],
        "source_path": module.source_path,
        "language": module.language,
        "source_hash": module.source_hash,
        "managed_by": "okf-code",
        "generated_profile": module.profile,
    }
    if module.repo_id is not None:
        frontmatter["repo"] = module.repo_id
    if module.repo_path is not None:
        frontmatter["repo_path"] = module.repo_path
    if module.package_id is not None:
        frontmatter["package"] = module.package_id
    yaml_text = yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True).strip()
    return f"---\n{yaml_text}\n---\n{_managed_body(module)}"


def render_summary_concept(
    *,
    title: str,
    summary_level: str,
    modules: list[tuple[CodeModule, str]],
    repo_id: str | None = None,
    area: str | None = None,
    package_id: str | None = None,
) -> str:
    """Render a generated code summary concept.

    Args:
        title: Summary title.
        summary_level: Summary scope, such as repository, area, or package.
        modules: Module and concept-id pairs included in the summary.
        repo_id: Optional repository identifier for multi-repo workspaces.
        area: Optional source area name.
        package_id: Optional repository-relative package path.

    Returns:
        Markdown document with YAML frontmatter and a managed summary body.
    """

    dependency_tags = ["depends-on"] if _summary_relationships(modules, "depends_on") else []
    dependent_tags = ["used-by"] if _summary_relationships(modules, "used_by") else []
    frontmatter = {
        "type": "CodeSummary",
        "title": title,
        "description": _summary_description(title, summary_level, modules),
        "tags": [
            "code",
            "summary",
            "impact",
            summary_level,
            *([repo_id] if repo_id else []),
            *dependency_tags,
            *dependent_tags,
        ],
        "summary_level": summary_level,
        "managed_by": "okf-code",
    }
    if repo_id is not None:
        frontmatter["repo"] = repo_id
    if area is not None:
        frontmatter["area"] = area
    if package_id is not None:
        frontmatter["package"] = package_id
    yaml_text = yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True).strip()
    return (
        f"---\n{yaml_text}\n---\n"
        f"{MANAGED_START}\n"
        "# Overview\n\n"
        f"Generated {summary_level} summary for `{title}`. Purpose: provide a "
        "low-token entry point for code search and impact analysis before "
        "opening file-level concepts.\n\n"
        "# Key modules\n\n"
        f"{_summary_links(modules)}\n\n"
        "# Impact map\n\n"
        f"{_summary_impact(modules)}\n\n"
        "# Impact notes\n\n"
        "Use this summary to choose a target module, then read that module at "
        "depth 0 or depth 1 for dependency and dependent context.\n"
        f"{MANAGED_END}\n"
    )


def _managed_body(module: CodeModule) -> str:
    return (
        f"{MANAGED_START}\n"
        "# Overview\n\n"
        f"{_overview(module)}\n\n"
        "# Symbols\n\n"
        f"{_symbols_table(module)}\n\n"
        "# Relationships\n\n"
        f"{_relationships_list(module)}\n\n"
        "# Impact notes\n\n"
        "Impact candidates on this page are syntax-derived. Treat them as a "
        "starting point for inspection, not as complete semantic proof of all "
        "callers, callees, or runtime effects.\n\n"
        "# Citations\n\n"
        f"- Source: `{module.source_path}`\n"
        f"- Source hash: `{module.source_hash}`\n"
        f"{MANAGED_END}\n"
    )


def _description(module: CodeModule) -> str:
    dependencies = [
        relationship.label
        for relationship in module.relationships
        if relationship.kind == "depends_on"
    ]
    if dependencies:
        return f"Generated code map for {_title(module)}. Depends on {', '.join(dependencies[:5])}."
    return f"Generated code map for {_title(module)}."


def _overview(module: CodeModule) -> str:
    role = _role(module)
    important = _symbol_names(module.symbols[:_COMPACT_HINT_LIMIT])
    dependency_count = len([rel for rel in module.relationships if rel.kind == "depends_on"])
    dependent_count = len([rel for rel in module.relationships if rel.kind == "used_by"])
    package_text = f" in package `{module.package_id}`" if module.package_id else ""
    repo_text = f" in repo `{module.repo_id}`" if module.repo_id else ""
    return (
        f"Generated CodeModule concept for `{_title(module)}`. "
        f"Purpose: {_title(module)} is a `{module.language}` {role}{package_text}{repo_text}. "
        f"Role: {role}. "
        f"high-signal symbols: {important or 'none detected'}. "
        f"Dependency context: {dependency_count} local dependencies and "
        f"{dependent_count} local dependents are linked when resolvable. "
        "Impact: changes here may affect linked dependents, imported dependencies, "
        "and callers identified by generated reverse edges. This page is "
        "syntax-derived for code finding, code-logic search, and impact-analysis "
        "groundwork."
    )


def _symbols_table(module: CodeModule) -> str:
    symbols = module.symbols
    if not symbols:
        return "No classes, functions, methods, or elements detected."
    rendered = symbols if module.profile == "full" else symbols[:_COMPACT_SYMBOL_LIMIT]
    rows = ["| Kind | Name | Lines |", "|---|---|---|"]
    for symbol in rendered:
        rows.append(f"| {symbol.kind} | `{symbol.name}` | {symbol.start_line}-{symbol.end_line} |")
    if len(rendered) < len(symbols):
        rows.append(
            f"\n{len(symbols) - len(rendered)} symbols omitted from compact profile."
        )
    return "\n".join(rows)


def _relationships_list(module: CodeModule) -> str:
    rows: list[str] = []
    all_dependencies = [
        relationship for relationship in module.relationships if relationship.kind == "depends_on"
    ]
    all_dependents = [
        relationship for relationship in module.relationships if relationship.kind == "used_by"
    ]
    dependencies = all_dependencies
    dependents = all_dependents
    if module.profile != "full":
        # Compact output is bounded, but must disclose hidden edges for impact analysis.
        dependencies = dependencies[:_COMPACT_RELATIONSHIP_LIMIT]
        dependents = dependents[:_COMPACT_RELATIONSHIP_LIMIT]
    if dependencies:
        rows.append("Depends on:")
    for relationship in dependencies:
        rows.append(f"- [{relationship.label}](/{relationship.target_cid}.md)")
    if len(dependencies) < len(all_dependencies):
        omitted_dependencies = len(all_dependencies) - len(dependencies)
        rows.append(
            f"- {omitted_dependencies} dependencies omitted from compact profile."
        )
    linked_labels = {relationship.label for relationship in dependencies}
    imports = module.imports if module.profile == "full" else module.imports[:_COMPACT_IMPORT_LIMIT]
    for name in imports:
        if name not in linked_labels:
            rows.append(f"- `{name}`")
    if len(imports) < len(module.imports):
        rows.append(f"- {len(module.imports) - len(imports)} imports omitted from compact profile.")
    if dependents:
        if rows:
            rows.append("")
        rows.append("Used by:")
        for relationship in dependents:
            rows.append(f"- [{relationship.label}](/{relationship.target_cid}.md)")
        if len(dependents) < len(all_dependents):
            omitted_dependents = len(all_dependents) - len(dependents)
            rows.append(f"- {omitted_dependents} dependents omitted from compact profile.")
    if not rows:
        return "No imports detected."
    return "\n".join(rows)


def _title(module: CodeModule) -> str:
    if module.repo_id is None:
        return module.source_path
    return f"{module.repo_id}/{module.source_path}"


def _resource(module: CodeModule) -> str:
    if module.repo_path is None:
        return module.source_path
    return f"{module.repo_path}/{module.source_path}"


def _role(module: CodeModule) -> str:
    path = module.source_path.lower()
    symbol_kinds = {symbol.kind for symbol in module.symbols}
    if "test" in path or "/tests/" in path:
        return "test module"
    if "service" in path or any("service" in symbol.name.lower() for symbol in module.symbols):
        return "service module"
    if "model" in path or {"class", "struct", "type"} & symbol_kinds:
        return "model module"
    if path.endswith((".tsx", ".jsx", ".html")):
        return "UI module"
    if path.endswith(("main.py", "main.go", "main.rs", "index.ts", "index.js")):
        return "entry-point module"
    return "module"


def _symbol_names(symbols: tuple[CodeSymbol, ...]) -> str:
    return ", ".join(f"`{symbol.name}`" for symbol in symbols)


def _summary_links(modules: list[tuple[CodeModule, str]]) -> str:
    if not modules:
        return "No modules detected."
    rows: list[str] = []
    ranked = sorted(
        modules,
        key=lambda item: (
            -_impact_score(item[0]),
            item[0].source_path,
            item[1],
        ),
    )
    for module, cid in ranked[:20]:
        symbols = _symbol_names(module.symbols[:3])
        suffix = f"; high-signal symbols: {symbols}" if symbols else ""
        relationship_text = _relationship_counts(module)
        rows.append(
            f"- [{_title(module)}](/{cid}.md) - {_role(module)}; "
            f"{relationship_text}{suffix}"
        )
    if len(ranked) > 20:
        rows.append(f"- {len(ranked) - 20} modules omitted from compact summary.")
    return "\n".join(rows)


def _summary_description(
    title: str,
    summary_level: str,
    modules: list[tuple[CodeModule, str]],
) -> str:
    dependencies = _summary_relationships(modules, "depends_on")
    dependents = _summary_relationships(modules, "used_by")
    parts = [f"Generated {summary_level} code summary for {title}."]
    if dependencies:
        parts.append(f"Top dependencies: {', '.join(dependencies[:5])}.")
    if dependents:
        parts.append(f"Top dependents: {', '.join(dependents[:5])}.")
    return " ".join(parts)


def _summary_impact(modules: list[tuple[CodeModule, str]]) -> str:
    ranked = sorted(
        modules,
        key=lambda item: (
            -_impact_score(item[0]),
            item[0].source_path,
            item[1],
        ),
    )
    impacted = [item for item in ranked if _impact_score(item[0]) > 0]
    if not impacted:
        return "No local dependency edges detected in this summary scope."
    rows = [
        "| Module | Depends | Used by | Relationship signals |",
        "|---|---:|---:|---|",
    ]
    for module, cid in impacted[:10]:
        dependencies = [
            relationship.label
            for relationship in module.relationships
            if relationship.kind == "depends_on"
        ]
        dependents = [
            relationship.label
            for relationship in module.relationships
            if relationship.kind == "used_by"
        ]
        signals = ", ".join([*dependencies[:3], *dependents[:3]]) or "none"
        rows.append(
            f"| [{_title(module)}](/{cid}.md) | {len(dependencies)} | "
            f"{len(dependents)} | {signals} |"
        )
    if len(impacted) > 10:
        rows.append(f"\n{len(impacted) - 10} impact candidates omitted from compact summary.")
    return "\n".join(rows)


def _summary_relationships(modules: list[tuple[CodeModule, str]], kind: str) -> list[str]:
    seen: set[str] = set()
    labels: list[str] = []
    relationships = (
        relationship
        for module, _cid in modules
        for relationship in module.relationships
        if relationship.kind == kind
    )
    for relationship in sorted(relationships, key=lambda item: (item.label, item.target_cid)):
        if relationship.label in seen:
            continue
        seen.add(relationship.label)
        labels.append(relationship.label)
    return labels


def _impact_score(module: CodeModule) -> int:
    return len(module.relationships)


def _relationship_counts(module: CodeModule) -> str:
    dependencies = len(
        [relationship for relationship in module.relationships if relationship.kind == "depends_on"]
    )
    dependents = len(
        [relationship for relationship in module.relationships if relationship.kind == "used_by"]
    )
    return f"depends on {dependencies}; used by {dependents}"
