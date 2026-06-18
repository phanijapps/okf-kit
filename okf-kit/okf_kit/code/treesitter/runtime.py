"""Runtime adapter over tree-sitter-language-pack."""
from __future__ import annotations

import builtins
from typing import Any, cast


def parse_source(language: str, source: str) -> Any:
    """Parse source text with a Tree-sitter language parser.

    Args:
        language: Parser name understood by ``tree_sitter_language_pack``.
        source: Source text to parse.

    Returns:
        Tree-sitter parse tree.

    Raises:
        ValueError: If Tree-sitter parser support is not installed.
    """

    parser = _parser(language)
    return parser.parse(source)


def root_node(tree: Any) -> Any:
    """Return a parse tree root node.

    Args:
        tree: Tree-sitter parse tree.

    Returns:
        Root syntax node.
    """

    value = tree.root_node
    return value() if callable(value) else value


def node_kind(node: Any) -> str:
    """Return a node kind across Tree-sitter API variants.

    Args:
        node: Tree-sitter syntax node.

    Returns:
        Node kind or type as a string.
    """

    try:
        value = node.type
    except AttributeError:
        value = node.kind
    resolved = value() if callable(value) else value
    return str(resolved)


def children(node: Any) -> list[Any]:
    """Return all child nodes for a syntax node.

    Args:
        node: Tree-sitter syntax node.

    Returns:
        Child nodes in parser order.
    """

    return [node.child(idx) for idx in range(child_count(node))]


def child_count(node: Any) -> int:
    """Return a node child count across Tree-sitter API variants.

    Args:
        node: Tree-sitter syntax node.

    Returns:
        Number of child nodes.
    """

    value = node.child_count
    resolved = value() if callable(value) else value
    return int(resolved)


def child_by_field_name(node: Any, field: str) -> Any | None:
    """Return a named child field from a syntax node.

    Args:
        node: Tree-sitter syntax node.
        field: Field name to read.

    Returns:
        Matching child node, or ``None`` when absent.
    """

    value = node.child_by_field_name(field)
    return value


def node_text(node: Any, source_bytes: bytes) -> str:
    """Return source text for a syntax node.

    Args:
        node: Tree-sitter syntax node.
        source_bytes: Full source text encoded as bytes.

    Returns:
        Decoded node text.
    """

    try:
        text = node.text
    except AttributeError:
        text = None
    if text is not None:
        value = text() if callable(text) else text
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="replace")
        return str(value)
    start, end = byte_range(node)
    return source_bytes[start:end].decode("utf-8", errors="replace")


def byte_range(node: Any) -> tuple[int, int]:
    """Return byte offsets for a syntax node.

    Args:
        node: Tree-sitter syntax node.

    Returns:
        ``(start, end)`` byte offsets.
    """

    try:
        value = node.byte_range
    except AttributeError:
        value = None
    if value is not None:
        byte_range_value: Any = value() if callable(value) else value
        if hasattr(byte_range_value, "start") and hasattr(byte_range_value, "end"):
            return int(byte_range_value.start), int(byte_range_value.end)
        start, end = cast(tuple[int, int], byte_range_value)
        return int(start), int(end)
    return int(node.start_byte), int(node.end_byte)


def start_line(node: Any) -> int:
    """Return a one-based start line for a syntax node.

    Args:
        node: Tree-sitter syntax node.

    Returns:
        One-based start line.
    """

    return _point_row(_node_start(node)) + 1


def end_line(node: Any) -> int:
    """Return a one-based end line for a syntax node.

    Args:
        node: Tree-sitter syntax node.

    Returns:
        One-based end line.
    """

    return _point_row(_node_end(node)) + 1


def first_descendant_text(node: Any, source_bytes: bytes, kinds: tuple[str, ...]) -> str | None:
    """Find text for the first descendant whose kind is allowed.

    Args:
        node: Tree-sitter syntax node to search.
        source_bytes: Full source text encoded as bytes.
        kinds: Allowed node kinds.

    Returns:
        Descendant text, or ``None`` when no matching descendant exists.
    """

    if node_kind(node) in kinds:
        return node_text(node, source_bytes)
    for child in children(node):
        found = first_descendant_text(child, source_bytes, kinds)
        if found is not None:
            return found
    return None


def _parser(language: str) -> Any:
    try:
        pack = builtins.__import__("tree_sitter_language_pack", fromlist=["get_parser"])
    except ModuleNotFoundError as exc:
        raise ValueError(
            "Tree-sitter parser support is not installed; install okf-kit[treesitter]"
        ) from exc
    return pack.get_parser(language)


def _node_start(node: Any) -> Any:
    try:
        value = node.start_point
    except AttributeError:
        value = node.start_position
    return value() if callable(value) else value


def _node_end(node: Any) -> Any:
    try:
        value = node.end_point
    except AttributeError:
        value = node.end_position
    return value() if callable(value) else value


def _point_row(point: Any) -> int:
    if hasattr(point, "row"):
        return int(point.row)
    return int(point[0])
