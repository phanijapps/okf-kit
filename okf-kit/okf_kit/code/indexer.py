"""Index source-code repositories into OKF CodeModule concepts."""
from __future__ import annotations

import posixpath
from contextlib import suppress
from dataclasses import replace
from pathlib import Path

from okf_kit.code.discovery import adapter_for_path, adapters_for, iter_source_files
from okf_kit.code.managed import merge_managed, split_generated
from okf_kit.code.model import CodeModule, CodeRelationship, DiscoveredSource, IndexResult
from okf_kit.code.paths import concept_id, concept_path, safe_segment
from okf_kit.code.render import render_concept, render_summary_concept
from okf_kit.code.treesitter.languages import LanguageAdapter
from okf_kit.core.links import is_within
from okf_kit.core.parse import split_frontmatter
from okf_kit.core.templates import init_bundle


def extract_module(path: Path, repo_root: Path, *, language: str | None = None) -> CodeModule:
    """Extract syntax-level facts from one source file.

    Args:
        path: Source file to parse.
        repo_root: Repository root used to compute repository-relative paths.
        language: Optional language name. When omitted, the adapter is inferred
            from the file extension.

    Returns:
        Extracted module facts ready for rendering.

    Raises:
        ValueError: If the language or file extension is unsupported.
    """

    adapters = adapters_for([language] if language else None)
    adapter = adapter_for_path(Path(path), adapters)
    return adapter.extract(Path(path), Path(repo_root))


def index_codebase(
    repo_root: Path,
    bundle_root: Path,
    *,
    languages: list[str] | None = None,
    update: bool = True,
    profile: str = "compact",
    include_tests: bool = False,
    include: list[str] | None = None,
    exclude: list[str] | None = None,
    repos: list[str] | None = None,
) -> IndexResult:
    """Index source code into OKF code concepts.

    Args:
        repo_root: Source repository or workspace root.
        bundle_root: OKF bundle root to write generated concepts into.
        languages: Optional language names to index. Defaults to all supported
            languages.
        update: Whether existing managed concepts may be refreshed.
        profile: Rendering profile, either ``compact`` or ``full``.
        include_tests: Whether test files should be indexed.
        include: Optional workspace-relative glob patterns to include.
        exclude: Optional workspace-relative glob patterns to exclude.
        repos: Optional repository ids or workspace-relative paths to select.

    Returns:
        Counts for module concepts written, updated, and skipped.

    Raises:
        ValueError: If inputs are invalid, paths escape their roots, or an
            existing unmanaged concept would be overwritten.
    """

    if profile not in {"compact", "full"}:
        raise ValueError("profile must be 'compact' or 'full'")
    adapters = adapters_for(languages)
    repo = Path(repo_root).resolve()
    bundle = Path(bundle_root).resolve()
    if not repo.is_dir():
        raise ValueError(f"repository does not exist: {repo_root}")

    written = 0
    updated = 0
    skipped = 0
    modules: list[CodeModule] = []
    cid_by_source: dict[str, str] = {}
    source_by_cid: dict[str, str] = {}
    for source in iter_source_files(
        repo,
        bundle,
        adapters,
        include_tests=include_tests,
        include=include,
        exclude=exclude,
        repos=repos,
    ):
        adapter = adapter_for_path(source.path, adapters)
        module = _extract_discovered(adapter, source, profile=profile)
        cid = concept_id(module.source_path, repo_id=module.repo_id)
        source_key = _source_key(module)
        existing_source = source_by_cid.get(cid)
        if existing_source is not None and existing_source != source_key:
            raise ValueError(
                "duplicate code concept id after path normalization: "
                f"{existing_source} and {source_key} both map to {cid}"
            )
        modules.append(module)
        cid_by_source[source_key] = cid
        source_by_cid[cid] = source_key

    # An explicit empty scope means "nothing selected", not "prune the generated code map".
    if not modules and _has_explicit_scope(include=include, repos=repos):
        return IndexResult(written=0, updated=0, skipped=0)

    module_keys = _module_keys(modules, cid_by_source)
    modules = [_with_relationships(module, cid_by_source, module_keys) for module in modules]
    modules = _with_reverse_relationships(modules, cid_by_source)
    summary_concepts = _summary_concepts(modules, cid_by_source)
    desired_cids = set(cid_by_source.values()) | set(summary_concepts)
    _preflight_destinations(bundle, modules, cid_by_source)
    _preflight_existing_concepts(bundle, modules, cid_by_source)
    _preflight_managed_roots(bundle)
    _preflight_summary_destinations(bundle, summary_concepts)
    _preflight_existing_summaries(bundle, summary_concepts)
    if not (bundle / "index.md").is_file():
        init_bundle(bundle, name=bundle.name)
    else:
        bundle.mkdir(parents=True, exist_ok=True)
    _prune_stale_generated(bundle, desired_cids)
    for module in modules:
        cid = cid_by_source[_source_key(module)]
        dest = concept_path(bundle, cid)
        if not is_within(dest, bundle):
            raise ValueError(f"concept path escapes bundle: {cid}")
        rendered = render_concept(module)
        if dest.exists():
            if not update:
                skipped += 1
                continue
            existing = dest.read_text(encoding="utf-8")
            dest.write_text(merge_managed(existing, rendered), encoding="utf-8")
            updated += 1
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(rendered, encoding="utf-8")
            written += 1
    _write_summaries(bundle, summary_concepts, update=update)
    return IndexResult(written=written, updated=updated, skipped=skipped)


def _has_explicit_scope(*, include: list[str] | None, repos: list[str] | None) -> bool:
    return bool(include or repos)


def _extract_discovered(
    adapter: LanguageAdapter,
    source: DiscoveredSource,
    *,
    profile: str,
) -> CodeModule:
    module = adapter.extract(source.path, source.repo_root)
    return replace(
        module,
        repo_id=source.repo_id,
        repo_path=source.repo_path,
        package_id=source.package_id,
        profile=profile,
    )


def _source_key(module: CodeModule) -> str:
    return f"{module.repo_id or ''}\0{module.repo_path or ''}\0{module.source_path}"


def _preflight_destinations(
    bundle: Path,
    modules: list[CodeModule],
    cid_by_source: dict[str, str],
) -> None:
    for module in modules:
        cid = cid_by_source[_source_key(module)]
        dest = bundle / f"{cid}.md"
        current = bundle
        rel_parent = dest.parent.relative_to(bundle)
        for part in rel_parent.parts:
            current = current / part
            if current.is_symlink():
                raise ValueError(
                    f"code concept destination escapes bundle through symlink: {current}"
                )
            if current.exists() and not current.is_dir():
                raise ValueError(f"code concept destination parent is not a directory: {current}")
        if dest.exists() and not dest.is_file():
            raise ValueError(f"code concept destination is not a file: {dest}")


def _preflight_existing_concepts(
    bundle: Path,
    modules: list[CodeModule],
    cid_by_source: dict[str, str],
) -> None:
    for module in modules:
        dest = concept_path(bundle, cid_by_source[_source_key(module)])
        if not dest.exists():
            continue
        existing = dest.read_text(encoding="utf-8")
        frontmatter = split_frontmatter(existing)
        if (
            not frontmatter.present
            or frontmatter.data.get("managed_by") != "okf-code"
            or frontmatter.data.get("source_path") != module.source_path
            or frontmatter.data.get("repo") != module.repo_id
            or split_generated(existing) is None
        ):
            raise ValueError(
                "refusing to index over existing non-okf-code concept: "
                f"{cid_by_source[_source_key(module)]}"
            )


def _write_summaries(
    bundle: Path,
    summary_concepts: dict[str, str],
    *,
    update: bool,
) -> None:
    for cid, rendered in summary_concepts.items():
        dest = concept_path(bundle, cid)
        _preflight_summary(dest, cid)
        if dest.exists():
            if not update:
                continue
            existing = dest.read_text(encoding="utf-8")
            dest.write_text(merge_managed(existing, rendered), encoding="utf-8")
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(rendered, encoding="utf-8")


def _preflight_summary(dest: Path, cid: str) -> None:
    if not dest.exists():
        return
    existing = dest.read_text(encoding="utf-8")
    frontmatter = split_frontmatter(existing)
    if (
        not frontmatter.present
        or frontmatter.data.get("managed_by") != "okf-code"
        or split_generated(existing) is None
    ):
        raise ValueError(f"refusing to index over existing non-okf-code concept: {cid}")


def _preflight_summary_destinations(bundle: Path, summaries: dict[str, str]) -> None:
    for cid in summaries:
        dest = bundle / f"{cid}.md"
        current = bundle
        rel_parent = dest.parent.relative_to(bundle)
        for part in rel_parent.parts:
            current = current / part
            if current.is_symlink():
                raise ValueError(
                    f"summary concept destination escapes bundle through symlink: {current}"
                )
            if current.exists() and not current.is_dir():
                raise ValueError(
                    f"summary concept destination parent is not a directory: {current}"
                )
        if dest.exists() and not dest.is_file():
            raise ValueError(f"summary concept destination is not a file: {dest}")


def _preflight_managed_roots(bundle: Path) -> None:
    for root_name in ("code", "code-summaries"):
        root = bundle / root_name
        if not root.exists() and not root.is_symlink():
            continue
        if root.is_symlink():
            raise ValueError(f"managed root escapes bundle through symlink: {root}")
        if not root.is_dir():
            raise ValueError(f"managed root is not a directory: {root}")
        for path in root.rglob("*.md"):
            # Pruning reads existing generated trees, so reject symlinked parents up front.
            if any(parent.is_symlink() for parent in path.parents if parent != bundle.parent):
                raise ValueError(f"managed concept path escapes bundle through symlink: {path}")
            resolved = path.resolve()
            if not is_within(resolved, bundle):
                raise ValueError(f"managed concept path escapes bundle: {path}")


def _preflight_existing_summaries(bundle: Path, summaries: dict[str, str]) -> None:
    for cid in summaries:
        dest = concept_path(bundle, cid)
        _preflight_summary(dest, cid)


def _prune_stale_generated(bundle: Path, desired_cids: set[str]) -> None:
    for root_name in ("code", "code-summaries"):
        root = bundle / root_name
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.md"), reverse=True):
            cid = path.relative_to(bundle).with_suffix("").as_posix()
            if cid in desired_cids:
                continue
            text = path.read_text(encoding="utf-8")
            frontmatter = split_frontmatter(text)
            generated = split_generated(text)
            if (
                not frontmatter.present
                or frontmatter.data.get("managed_by") != "okf-code"
                or generated is None
            ):
                continue
            prefix, _body, suffix = generated
            if split_frontmatter(prefix).body.strip() or suffix.strip():
                continue
            path.unlink()
        _remove_empty_dirs(root)


def _remove_empty_dirs(root: Path) -> None:
    for path in sorted((item for item in root.rglob("*") if item.is_dir()), reverse=True):
        with suppress(OSError):
            path.rmdir()


def _summary_concepts(
    modules: list[CodeModule],
    cid_by_source: dict[str, str],
) -> dict[str, str]:
    summaries: dict[str, str] = {}
    repo_groups: dict[str | None, list[CodeModule]] = {}
    for module in modules:
        repo_groups.setdefault(module.repo_id, []).append(module)
    for repo_id, repo_modules in repo_groups.items():
        repo_title = repo_id or "repository"
        safe_repo = safe_segment(repo_id) if repo_id else None
        repo_cid = f"code-summaries/repos/{safe_repo}" if safe_repo else "code-summaries/repository"
        summaries[repo_cid] = render_summary_concept(
            title=repo_title,
            summary_level="repository",
            modules=[(module, cid_by_source[_source_key(module)]) for module in repo_modules],
            repo_id=repo_id,
        )
        area_groups: dict[str, list[CodeModule]] = {}
        for module in repo_modules:
            area = Path(module.source_path).parts[0] if Path(module.source_path).parts else "root"
            area_groups.setdefault(area, []).append(module)
        for area, area_modules in area_groups.items():
            area_cid = (
                f"code-summaries/repos/{safe_repo}/areas/{safe_segment(area)}"
                if safe_repo
                else f"code-summaries/areas/{safe_segment(area)}"
            )
            summaries[area_cid] = render_summary_concept(
                title=f"{repo_title}/{area}",
                summary_level="area",
                modules=[(module, cid_by_source[_source_key(module)]) for module in area_modules],
                repo_id=repo_id,
                area=area,
            )
        package_groups: dict[str, list[CodeModule]] = {}
        for module in repo_modules:
            if module.package_id:
                package_groups.setdefault(module.package_id, []).append(module)
        for package_id, package_modules in package_groups.items():
            safe_package = "/".join(safe_segment(part) for part in Path(package_id).parts)
            package_cid = (
                f"code-summaries/repos/{safe_repo}/packages/{safe_package}"
                if safe_repo
                else f"code-summaries/packages/{safe_package}"
            )
            summaries[package_cid] = render_summary_concept(
                title=f"{repo_title}/{package_id}",
                summary_level="package",
                modules=[
                    (module, cid_by_source[_source_key(module)]) for module in package_modules
                ],
                repo_id=repo_id,
                package_id=package_id,
            )
    return summaries


def _with_relationships(
    module: CodeModule,
    cid_by_source: dict[str, str],
    module_keys: dict[str, str],
) -> CodeModule:
    relationships: list[CodeRelationship] = []
    seen: set[str] = set()
    for imported in module.imports:
        source_cid = cid_by_source[_source_key(module)]
        for label, target in _resolve_imports(imported, module, module_keys):
            if target == source_cid or target in seen:
                continue
            relationships.append(
                CodeRelationship(label=label, target_cid=target, kind="depends_on")
            )
            seen.add(target)
    return replace(module, relationships=tuple(relationships))


def _with_reverse_relationships(
    modules: list[CodeModule],
    cid_by_source: dict[str, str],
) -> list[CodeModule]:
    modules_by_cid = {cid_by_source[_source_key(module)]: module for module in modules}
    dependents: dict[str, list[CodeRelationship]] = {cid: [] for cid in modules_by_cid}
    for module in modules:
        source_cid = cid_by_source[_source_key(module)]
        source_label = _relationship_label(module)
        for relationship in module.relationships:
            if relationship.kind != "depends_on":
                continue
            if relationship.target_cid in dependents:
                dependents[relationship.target_cid].append(
                    CodeRelationship(
                        label=source_label,
                        target_cid=source_cid,
                        kind="used_by",
                    )
                )
    updated: list[CodeModule] = []
    for module in modules:
        cid = cid_by_source[_source_key(module)]
        reverse = tuple(
            sorted(
                dependents[cid],
                key=lambda relationship: (relationship.label, relationship.target_cid),
            )
        )
        updated.append(replace(module, relationships=module.relationships + reverse))
    return updated


def _relationship_label(module: CodeModule) -> str:
    if module.repo_id is None:
        return module.source_path
    return f"{module.repo_id}/{module.source_path}"


def _module_keys(modules: list[CodeModule], cid_by_source: dict[str, str]) -> dict[str, str]:
    keys: dict[str, str] = {}
    for module in modules:
        source_path = module.source_path
        cid = cid_by_source[_source_key(module)]
        path = Path(source_path)
        stem_path = path.with_suffix("").as_posix()
        dotted = stem_path.replace("/", ".")
        rust_path = stem_path.replace("/", "::")
        for key in {source_path, stem_path, dotted, rust_path}:
            if module.repo_id:
                keys.setdefault(f"{module.repo_id}\0{key}", cid)
            keys.setdefault(key, cid)
        if path.name == "__init__.py":
            package = path.parent.as_posix().replace("/", ".")
            if package != ".":
                keys.setdefault(package, cid)
        for key in _rust_crate_keys(module):
            # Rust crate roots are package-local; global crate keys false-link sibling packages.
            if module.repo_id and module.package_id:
                keys.setdefault(f"{module.repo_id}\0{module.package_id}\0{key}", cid)
            if module.package_id:
                keys.setdefault(f"{module.package_id}\0{key}", cid)
            else:
                if module.repo_id:
                    keys.setdefault(f"{module.repo_id}\0{key}", cid)
                keys.setdefault(key, cid)
        for key in _package_relative_keys(module):
            if module.repo_id and module.package_id:
                keys.setdefault(f"{module.repo_id}\0{module.package_id}\0{key}", cid)
            if module.repo_id:
                keys.setdefault(f"{module.repo_id}\0{key}", cid)
            if module.package_id:
                keys.setdefault(f"{module.package_id}\0{key}", cid)
            keys.setdefault(key, cid)
    return keys


def _rust_crate_keys(module: CodeModule) -> tuple[str, ...]:
    source = module.source_path
    prefix = f"{module.package_id}/src/" if module.package_id else "src/"
    if not source.startswith(prefix):
        return ()
    rel = source.removeprefix(prefix)
    path = Path(rel)
    stem = path.with_suffix("").as_posix()
    if stem in {"lib", "main", "mod"}:
        return ("crate",)
    rust_key = "crate::" + stem.replace("/", "::")
    if path.name == "mod.rs":
        rust_key = "crate::" + path.parent.as_posix().replace("/", "::")
    return (rust_key,)


def _package_relative_keys(module: CodeModule) -> tuple[str, ...]:
    if module.package_id is None:
        return ()
    prefix = f"{module.package_id}/src/"
    if not module.source_path.startswith(prefix):
        return ()
    rel = module.source_path.removeprefix(prefix)
    stem = Path(rel).with_suffix("").as_posix()
    dotted = stem.replace("/", ".")
    return (stem, dotted)


def _resolve_imports(
    imported: str,
    module: CodeModule,
    module_keys: dict[str, str],
) -> list[tuple[str, str]]:
    normalized_labels = _normalize_import_labels(imported)
    # One grouped Rust use statement may produce several dependency edges.
    use_raw_label = len(normalized_labels) == 1 and ("{" in imported or "}" in imported)
    resolved: list[tuple[str, str]] = []
    for normalized in normalized_labels:
        target = _resolve_normalized_import(normalized, module, module_keys)
        if target is not None:
            resolved.append((imported if use_raw_label else normalized, target))
    return resolved


def _resolve_normalized_import(
    normalized: str,
    module: CodeModule,
    module_keys: dict[str, str],
) -> str | None:
    relative = _relative_import_candidates(normalized, module.source_path)
    for candidate in relative:
        resolved = _lookup_candidate(candidate, module, module_keys)
        if resolved is not None:
            return resolved
    candidates = [normalized]
    if "::" in normalized:
        candidates.extend(_rust_prefix_candidates(normalized))
    if "." in normalized:
        parts = normalized.split(".")
        candidates.extend(".".join(parts[:idx]) for idx in range(len(parts) - 1, 0, -1))
    if "/" in normalized:
        parts = normalized.split("/")
        candidates.extend("/".join(parts[:idx]) for idx in range(len(parts) - 1, 0, -1))
    for candidate in candidates:
        resolved = _lookup_candidate(candidate, module, module_keys)
        if resolved is not None:
            return resolved
    return None


def _lookup_candidate(
    candidate: str,
    module: CodeModule,
    module_keys: dict[str, str],
) -> str | None:
    if module.repo_id and module.package_id:
        repo_package_candidate = f"{module.repo_id}\0{module.package_id}\0{candidate}"
        if repo_package_candidate in module_keys:
            return module_keys[repo_package_candidate]
        # Missing crate imports stay unresolved instead of falling back outside the package.
        if candidate.startswith("crate"):
            return None
    if module.repo_id:
        repo_candidate = f"{module.repo_id}\0{candidate}"
        if repo_candidate in module_keys:
            return module_keys[repo_candidate]
        return None
    if module.package_id:
        package_candidate = f"{module.package_id}\0{candidate}"
        if package_candidate in module_keys:
            return module_keys[package_candidate]
        # Missing crate imports stay unresolved instead of falling back outside the package.
        if candidate.startswith("crate"):
            return None
    return module_keys.get(candidate)


def _normalize_import_labels(imported: str) -> list[str]:
    normalized = imported.strip().strip("\"'").rstrip(";")
    for prefix in ("pub use ", "use "):
        if normalized.startswith(prefix):
            normalized = normalized.removeprefix(prefix).strip()
    if "::{" in normalized:
        return _expand_rust_group_import(normalized)
    if "{" in normalized or "}" in normalized:
        return []
    return [normalized.strip()] if normalized.strip() else []


def _expand_rust_group_import(imported: str) -> list[str]:
    prefix, _separator, rest = imported.partition("::{")
    if not prefix or not rest.endswith("}"):
        return []
    inner = rest[:-1]
    labels: list[str] = []
    for part in _split_rust_group_items(inner):
        item = part.strip()
        if not item or item == "*":
            continue
        item = item.split(" as ", maxsplit=1)[0].strip()
        if "::{" in item:
            item = item.split("::{", maxsplit=1)[0].strip()
        if "{" in item or "}" in item:
            continue
        labels.append(prefix if item == "self" else f"{prefix}::{item}")
    return labels


def _split_rust_group_items(imported: str) -> list[str]:
    items: list[str] = []
    depth = 0
    start = 0
    for index, char in enumerate(imported):
        if char == "{":
            depth += 1
        elif char == "}":
            depth = max(0, depth - 1)
        elif char == "," and depth == 0:
            items.append(imported[start:index])
            start = index + 1
    items.append(imported[start:])
    return items


def _rust_prefix_candidates(imported: str) -> list[str]:
    parts = imported.split("::")
    # Do not reduce crate::missing::Thing to bare crate; that would false-link to lib.rs.
    stop = 2 if parts[0] == "crate" and len(parts) > 1 else 1
    return ["::".join(parts[:idx]) for idx in range(len(parts) - 1, stop - 1, -1)]


def _relative_import_candidates(imported: str, source_path: str) -> list[str]:
    rust_relative = _rust_relative_import_candidates(imported, source_path)
    if rust_relative:
        return rust_relative
    if imported.startswith(("./", "../")):
        stem = (Path(source_path).parent / imported).as_posix()
        normalized = posixpath.normpath(stem)
        return [normalized, str(Path(normalized).with_suffix("")), f"{normalized}/index"]
    if not imported.startswith("."):
        return []
    dot_count = len(imported) - len(imported.lstrip("."))
    suffix = imported[dot_count:]
    package_parts = list(Path(source_path).parent.parts)
    if dot_count > 1:
        package_parts = package_parts[: -(dot_count - 1)]
    prefix = ".".join(package_parts)
    dotted = ".".join(part for part in (prefix, suffix) if part)
    candidates = [dotted]
    parts = dotted.split(".")
    candidates.extend(".".join(parts[:idx]) for idx in range(len(parts) - 1, 0, -1))
    return candidates


def _rust_relative_import_candidates(imported: str, source_path: str) -> list[str]:
    if not imported.startswith("super::"):
        return []
    source = Path(source_path)
    source_parts = list(source.with_suffix("").parts)
    if "src" not in source_parts:
        return []
    src_index = source_parts.index("src")
    module_parts = source_parts[src_index + 1 : -1]
    parts = imported.split("::")
    super_count = 0
    while super_count < len(parts) and parts[super_count] == "super":
        super_count += 1
    suffix = parts[super_count:]
    if super_count:
        module_parts = module_parts[: max(0, len(module_parts) - super_count + 1)]
    candidate_parts = ["crate", *module_parts, *suffix]
    candidate = "::".join(part for part in candidate_parts if part and part != "*")
    return [candidate, *_rust_prefix_candidates(candidate)]
