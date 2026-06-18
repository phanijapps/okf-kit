"""Data model for source-code facts rendered as OKF concepts."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DiscoveredSource:
    """Source file selected for code indexing.

    Attributes:
        path: Resolved source file path.
        repo_root: Resolved root of the repository that owns the source file.
        repo_id: Stable repository identifier used in generated concept ids.
        repo_path: Workspace-relative repository path, when indexing a workspace.
        package_id: Repository-relative package path, when a package marker owns the file.
    """

    path: Path
    repo_root: Path
    repo_id: str | None
    repo_path: str | None
    package_id: str | None = None


@dataclass(frozen=True)
class CodeSymbol:
    """Syntax-level symbol extracted from a source file.

    Attributes:
        kind: Parser-specific symbol category, such as class, function, or method.
        name: Display name for the symbol.
        start_line: One-based start line.
        end_line: One-based end line.
    """

    kind: str
    name: str
    start_line: int
    end_line: int


@dataclass(frozen=True)
class CodeRelationship:
    """Resolved local relationship between generated code concepts.

    Attributes:
        label: Human-readable import or source label.
        target_cid: Target OKF concept id without the ``.md`` suffix.
        kind: Relationship category, such as ``depends_on`` or ``used_by``.
    """

    label: str
    target_cid: str
    kind: str = "depends_on"


@dataclass(frozen=True)
class CodeModule:
    """Extracted source-file facts rendered as a ``CodeModule`` concept.

    Attributes:
        source_path: Repository-relative source path.
        language: Adapter language name.
        source_hash: Content hash for citations and change detection.
        imports: Raw import labels extracted from syntax.
        symbols: Syntax-level symbol inventory.
        relationships: Resolved local dependency and reverse-dependent edges.
        repo_id: Stable repository identifier in multi-repo workspaces.
        repo_path: Workspace-relative repository path.
        package_id: Repository-relative package path.
        profile: Generated rendering profile, either ``compact`` or ``full``.
    """

    source_path: str
    language: str
    source_hash: str
    imports: tuple[str, ...]
    symbols: tuple[CodeSymbol, ...]
    relationships: tuple[CodeRelationship, ...] = ()
    repo_id: str | None = None
    repo_path: str | None = None
    package_id: str | None = None
    profile: str = "compact"


@dataclass(frozen=True)
class IndexResult:
    """Counts returned by a code indexing run.

    Attributes:
        written: Number of new module concepts written.
        updated: Number of existing module concepts refreshed.
        skipped: Number of existing module concepts left untouched.
    """

    written: int
    updated: int
    skipped: int
