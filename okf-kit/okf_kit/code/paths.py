"""Path and concept-id helpers for generated code concepts."""
from __future__ import annotations

import re
from pathlib import Path

from okf_kit.core.links import cid_segments_valid, is_within


def concept_id(source_path: str, *, repo_id: str | None = None) -> str:
    """Build the generated concept id for a source file.

    Args:
        source_path: Repository-relative source path.
        repo_id: Optional repository identifier for multi-repo workspaces.

    Returns:
        Bundle-relative concept id without the ``.md`` suffix.

    Raises:
        ValueError: If the derived concept id is not valid OKF syntax.
    """

    path = Path(source_path)
    parts = ["code", *([repo_id] if repo_id else []), *path.parts]
    safe = [safe_segment(part) for part in parts]
    cid = "/".join(safe)
    if not cid_segments_valid(cid):
        raise ValueError(f"unable to derive valid concept id for source path: {source_path}")
    return cid


def concept_path(bundle: Path, cid: str) -> Path:
    """Resolve a generated concept id to a confined bundle path.

    Args:
        bundle: OKF bundle root.
        cid: Concept id without the ``.md`` suffix.

    Returns:
        Resolved Markdown path for the concept.

    Raises:
        ValueError: If the concept path escapes the bundle.
    """

    candidate = (bundle / f"{cid}.md").resolve()
    if not is_within(candidate.parent, bundle):
        raise ValueError(f"concept path escapes bundle: {cid}")
    return candidate


def safe_segment(segment: str) -> str:
    """Normalize a string into one OKF-safe path segment.

    Args:
        segment: Raw path or repository segment.

    Returns:
        Segment containing only OKF-compatible characters.
    """

    safe = re.sub(r"[^A-Za-z0-9_.-]+", "-", segment).strip(".-")
    if not safe:
        safe = "_"
    if not re.match(r"[A-Za-z0-9_]", safe):
        safe = f"_{safe}"
    return safe
