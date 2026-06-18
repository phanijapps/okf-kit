"""Repository walking and language selection for code indexing."""
from __future__ import annotations

from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path

from okf_kit.code.model import DiscoveredSource
from okf_kit.code.paths import safe_segment
from okf_kit.code.treesitter.languages import ADAPTERS, LanguageAdapter
from okf_kit.core.links import is_within

_SKIP_DIRS = {
    ".git",
    ".hg",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "generated",
    "node_modules",
    "out",
    "static",
    "target",
    "templates",
    "vendor",
    "venv",
}
_TEST_DIRS = {
    "__tests__",
    "e2e",
    "spec",
    "test",
    "tests",
}
_REPO_MARKERS = {
    ".git",
    "Cargo.toml",
    "go.mod",
    "package.json",
    "pom.xml",
    "pyproject.toml",
    "settings.gradle",
}
_PACKAGE_MARKERS = {
    "Cargo.toml",
    "go.mod",
    "package.json",
    "pom.xml",
    "pyproject.toml",
}


@dataclass(frozen=True)
class WorkspaceRepo:
    """Repository discovered inside a source workspace.

    Attributes:
        root: Resolved repository root.
        repo_id: Stable generated identifier, or ``None`` for a single-root repo.
        repo_path: Workspace-relative path, or ``None`` for a single-root repo.
    """

    root: Path
    repo_id: str | None
    repo_path: str | None


def discover_repositories(
    workspace: Path,
    *,
    repos: list[str] | None = None,
) -> list[WorkspaceRepo]:
    """Discover repositories in a workspace.

    Args:
        workspace: Source repository or workspace root.
        repos: Optional repository ids or workspace-relative paths to select.

    Returns:
        Repositories to index, with stable ids for multi-repo workspaces.

    Raises:
        ValueError: If the workspace is missing, a selector escapes the workspace,
            or a selector is ambiguous.
    """

    root = Path(workspace).resolve()
    if not root.is_dir():
        raise ValueError(f"repository does not exist: {workspace}")
    selected = _validate_scope_patterns(root, repos or [], label="repo")
    all_repos = _all_repositories(root)
    if not selected:
        return all_repos
    selected_repos: list[WorkspaceRepo] = []
    seen_roots: set[Path] = set()
    for selector in selected:
        matches = [
            repo
            for repo in all_repos
            if selector in {repo.repo_id, repo.root.relative_to(root).as_posix()}
        ]
        unique_matches = {repo.root for repo in matches}
        if len(unique_matches) > 1:
            raise ValueError(f"repo selection is ambiguous: {selector}")
        for repo in matches:
            if repo.root not in seen_roots:
                selected_repos.append(repo)
                seen_roots.add(repo.root)
        if not matches:
            # Unmatched selectors are a no-op, except when they name an escaping symlink.
            candidate = root / selector
            if candidate.is_symlink():
                resolved = candidate.resolve()
                if not is_within(resolved, root):
                    raise ValueError(f"repo selection escapes workspace: {selector}")
    return selected_repos


def _all_repositories(workspace: Path) -> list[WorkspaceRepo]:
    # A real Git root is authoritative; package markers below it are packages, not repos.
    if (workspace / ".git").exists():
        return [WorkspaceRepo(root=workspace, repo_id=None, repo_path=None)]
    repos: list[Path] = []
    for child in sorted(workspace.iterdir()):
        if child.is_symlink():
            continue
        if child.is_dir() and _has_repo_marker(child):
            repos.append(child.resolve())
    if not repos and _has_repo_marker(workspace):
        return [WorkspaceRepo(root=workspace, repo_id=None, repo_path=None)]
    if not repos:
        return [WorkspaceRepo(root=workspace, repo_id=None, repo_path=None)]
    repo_paths = {repo.relative_to(workspace).as_posix() for repo in repos}
    used_ids: set[str] = set()
    discovered: list[WorkspaceRepo] = []
    for repo in repos:
        repo_path = repo.relative_to(workspace).as_posix()
        base_id = safe_segment(repo_path.replace("/", "-"))
        count = 1
        repo_id = base_id
        # Reserve real repo paths so --repo never matches one repo by id and another by path.
        while repo_id in used_ids or (repo_id in repo_paths and repo_id != repo_path):
            count += 1
            repo_id = f"{base_id}-{count}"
        used_ids.add(repo_id)
        discovered.append(WorkspaceRepo(root=repo, repo_id=repo_id, repo_path=repo_path))
    return discovered


def _has_repo_marker(path: Path) -> bool:
    return any((path / marker).exists() for marker in _REPO_MARKERS)


def _validate_scope_patterns(workspace: Path, values: list[str], *, label: str) -> list[str]:
    safe: list[str] = []
    for value in values:
        path = Path(value)
        if path.is_absolute():
            candidate = path.resolve()
            if not is_within(candidate, workspace):
                raise ValueError(f"{label} selection escapes workspace: {value}")
            safe.append(candidate.relative_to(workspace).as_posix())
            continue
        if ".." in path.parts:
            candidate = (workspace / path).resolve()
            if not is_within(candidate, workspace):
                raise ValueError(f"{label} selection escapes workspace: {value}")
        safe.append(value.replace("\\", "/"))
    return safe


def adapters_for(languages: list[str] | None) -> list[LanguageAdapter]:
    """Resolve requested language names to Tree-sitter adapters.

    Args:
        languages: Language names requested by the caller, or ``None`` for all
            supported adapters.

    Returns:
        Adapters in deterministic order.

    Raises:
        ValueError: If any requested language is unsupported.
    """

    if not languages:
        return [ADAPTERS[language] for language in sorted(ADAPTERS)]
    unknown = sorted(set(languages) - set(ADAPTERS))
    if unknown:
        supported = ", ".join(sorted(ADAPTERS))
        raise ValueError(f"unsupported language(s): {', '.join(unknown)} (supported: {supported})")
    return [ADAPTERS[language] for language in languages]


def language_help() -> str:
    """Return a comma-separated list of supported language names.

    Returns:
        Human-readable language list for CLI help text.
    """

    return ", ".join(sorted(ADAPTERS))


def iter_source_files(
    repo: Path,
    bundle: Path,
    adapters: list[LanguageAdapter],
    *,
    include_tests: bool = False,
    include: list[str] | None = None,
    exclude: list[str] | None = None,
    repos: list[str] | None = None,
) -> list[DiscoveredSource]:
    """Select source files eligible for code indexing.

    Args:
        repo: Source repository or workspace root.
        bundle: OKF bundle root; files under this path are ignored.
        adapters: Language adapters that determine supported file extensions.
        include_tests: Whether test files should be indexed.
        include: Optional workspace-relative glob patterns to include.
        exclude: Optional workspace-relative glob patterns to exclude.
        repos: Optional repository ids or workspace-relative paths to select.

    Returns:
        Discovered source files with repo and package identity attached.

    Raises:
        ValueError: If a selected source path or scope pattern escapes its root.
    """

    extensions = {ext for adapter in adapters for ext in adapter.extensions}
    workspace = Path(repo).resolve()
    bundle_root = Path(bundle).resolve()
    include_patterns = _validate_scope_patterns(workspace, include or [], label="include")
    exclude_patterns = _validate_scope_patterns(workspace, exclude or [], label="exclude")
    files: list[DiscoveredSource] = []
    for discovered_repo in discover_repositories(workspace, repos=repos):
        repo_root = discovered_repo.root
        for path in sorted(repo_root.rglob("*")):
            # Match explicit scope lexically before resolving, so no-match runs
            # do not follow symlinks.
            rel_lexical = path.relative_to(workspace).as_posix()
            if include_patterns and not _matches_any(rel_lexical, include_patterns):
                continue
            if exclude_patterns and _matches_any(rel_lexical, exclude_patterns):
                continue
            if not path.is_file() or path.suffix.lower() not in extensions:
                continue
            resolved = path.resolve()
            if not is_within(resolved, repo_root):
                raise ValueError(f"source path escapes repository: {path}")
            if is_within(resolved, bundle_root):
                continue
            rel_to_repo = resolved.relative_to(repo_root)
            rel_to_workspace = resolved.relative_to(workspace).as_posix()
            explicit_include = bool(include_patterns) and _matches_any(
                rel_to_workspace, include_patterns
            )
            if _is_default_skipped(
                rel_to_repo,
                include_tests=include_tests,
                explicit_include=explicit_include,
            ):
                continue
            files.append(
                DiscoveredSource(
                    path=resolved,
                    repo_root=repo_root,
                    repo_id=discovered_repo.repo_id,
                    repo_path=discovered_repo.repo_path,
                    package_id=_package_id(repo_root, resolved),
                )
            )
    return files


def adapter_for_path(path: Path, adapters: list[LanguageAdapter]) -> LanguageAdapter:
    """Select the language adapter for a source path.

    Args:
        path: Source file path.
        adapters: Candidate adapters.

    Returns:
        Adapter whose extension set contains ``path.suffix``.

    Raises:
        ValueError: If the path extension is unsupported by the adapters.
    """

    for adapter in adapters:
        if path.suffix.lower() in adapter.extensions:
            return adapter
    raise ValueError(f"unsupported source file extension: {path.suffix}")


def _is_default_skipped(path: Path, *, include_tests: bool, explicit_include: bool) -> bool:
    if _is_test_path(path):
        return not include_tests
    if _is_noisy_path(path):
        return not explicit_include
    return False


def _is_test_path(path: Path) -> bool:
    parts = path.parts
    return (
        any(part in _TEST_DIRS for part in parts)
        or path.name.startswith("test_")
        or path.name.endswith("_test.go")
        or ".test." in path.name
        or ".spec." in path.name
    )


def _is_noisy_path(path: Path) -> bool:
    parts = path.parts
    if any(part in _SKIP_DIRS or part.startswith(".") for part in parts):
        return True
    return path.name.endswith(".min.js") or path.name.endswith(".min.css")


def _matches_any(path: str, patterns: list[str]) -> bool:
    return any(fnmatch(path, pattern) or fnmatch(Path(path).name, pattern) for pattern in patterns)


def _package_id(repo_root: Path, source: Path) -> str | None:
    current = source.parent
    nearest: Path | None = None
    while is_within(current, repo_root):
        if any((current / marker).is_file() for marker in _PACKAGE_MARKERS):
            nearest = current
            break
        if current == repo_root:
            break
        current = current.parent
    if nearest is None or nearest == repo_root:
        return None
    return nearest.relative_to(repo_root).as_posix()
