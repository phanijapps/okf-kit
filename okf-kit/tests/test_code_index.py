"""Tests for Tree-sitter-backed source-code indexing into OKF concepts."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import tree_sitter_language_pack  # noqa: F401
from okf_kit.core.context import read_concept
from okf_kit.core.search import build_index, search
from okf_kit.core.validate import validate_bundle


def _require_tree_sitter_extra() -> None:
    return None


def _write_python_repo(root: Path) -> None:
    package = root / "pkg"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "service.py").write_text(
        "\n".join(
            [
                "import json",
                "from pathlib import Path",
                "",
                "class UserService:",
                "    def load_user(self, path: Path) -> dict:",
                "        return json.loads(path.read_text())",
                "",
                "def helper(value: str) -> str:",
                "    return value.strip()",
                "",
            ]
        ),
        encoding="utf-8",
    )


def test_discover_repositories_assigns_unique_ids_without_tree_sitter(tmp_path: Path):
    from okf_kit.code.discovery import discover_repositories

    workspace = tmp_path / "workspace"
    for repo_name in ("a b", "a-b", "a-b-2"):
        (workspace / repo_name / ".git").mkdir(parents=True)

    repos = discover_repositories(workspace)

    ids_by_path = {repo.repo_path: repo.repo_id for repo in repos}
    assert ids_by_path == {
        "a b": "a-b-3",
        "a-b": "a-b",
        "a-b-2": "a-b-2",
    }


def test_discover_repositories_selects_reserved_path_without_tree_sitter(tmp_path: Path):
    from okf_kit.code.discovery import discover_repositories

    workspace = tmp_path / "workspace"
    for repo_name in ("my repo", "my-repo"):
        (workspace / repo_name / ".git").mkdir(parents=True)

    repos = discover_repositories(workspace, repos=["my-repo"])

    assert [(repo.repo_path, repo.repo_id) for repo in repos] == [("my-repo", "my-repo")]


def test_discover_repositories_keeps_child_repos_when_workspace_has_marker(tmp_path: Path):
    from okf_kit.code.discovery import discover_repositories

    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "package.json").write_text("{}\n", encoding="utf-8")
    (workspace / "api" / ".git").mkdir(parents=True)
    (workspace / "worker" / ".git").mkdir(parents=True)

    repos = discover_repositories(workspace)

    assert [(repo.repo_path, repo.repo_id) for repo in repos] == [
        ("api", "api"),
        ("worker", "worker"),
    ]


def test_discover_repositories_treats_root_git_as_single_monorepo(tmp_path: Path):
    from okf_kit.code.discovery import discover_repositories

    workspace = tmp_path / "workspace"
    (workspace / ".git").mkdir(parents=True)
    (workspace / "gateway" / "Cargo.toml").parent.mkdir(parents=True)
    (workspace / "gateway" / "Cargo.toml").write_text(
        "[package]\nname = \"gateway\"\n",
        encoding="utf-8",
    )

    repos = discover_repositories(workspace)

    assert [(repo.repo_path, repo.repo_id) for repo in repos] == [(None, None)]


def test_rust_grouped_imports_resolve_all_targets_without_tree_sitter():
    from okf_kit.code.indexer import (
        _module_keys,
        _source_key,
        _with_relationships,
        _with_reverse_relationships,
    )
    from okf_kit.code.model import CodeModule

    config = CodeModule("src/config.rs", "rust", "1", (), ())
    runner = CodeModule("src/runner.rs", "rust", "2", (), ())
    core = CodeModule(
        "src/core.rs",
        "rust",
        "3",
        ("crate::{config::Config, runner::Runner}",),
        (),
    )
    cid_by_source = {
        _source_key(config): "code/src/config.rs",
        _source_key(runner): "code/src/runner.rs",
        _source_key(core): "code/src/core.rs",
    }

    module_keys = _module_keys([config, runner, core], cid_by_source)
    resolved = _with_relationships(core, cid_by_source, module_keys)

    assert {(rel.label, rel.target_cid) for rel in resolved.relationships} == {
        ("crate::config::Config", "code/src/config.rs"),
        ("crate::runner::Runner", "code/src/runner.rs"),
    }
    modules = _with_reverse_relationships([config, runner, resolved], cid_by_source)
    config_with_reverse = next(module for module in modules if module.source_path == "src/config.rs")
    runner_with_reverse = next(module for module in modules if module.source_path == "src/runner.rs")
    assert [(rel.kind, rel.target_cid) for rel in config_with_reverse.relationships] == [
        ("used_by", "code/src/core.rs")
    ]
    assert [(rel.kind, rel.target_cid) for rel in runner_with_reverse.relationships] == [
        ("used_by", "code/src/core.rs")
    ]


def test_unresolved_grouped_rust_import_does_not_link_crate_root_without_tree_sitter():
    from okf_kit.code.indexer import _module_keys, _source_key, _with_relationships
    from okf_kit.code.model import CodeModule

    lib = CodeModule("src/lib.rs", "rust", "1", (), ())
    core = CodeModule("src/core.rs", "rust", "2", ("crate::{missing::Thing}",), ())
    cid_by_source = {
        _source_key(lib): "code/src/lib.rs",
        _source_key(core): "code/src/core.rs",
    }

    module_keys = _module_keys([lib, core], cid_by_source)
    resolved = _with_relationships(core, cid_by_source, module_keys)

    assert resolved.relationships == ()


def test_package_scoped_crate_import_does_not_fallback_to_sibling_without_tree_sitter():
    from okf_kit.code.indexer import _module_keys, _source_key, _with_relationships
    from okf_kit.code.model import CodeModule

    sibling = CodeModule(
        "pkg-b/src/config.rs",
        "rust",
        "1",
        (),
        (),
        repo_id="repo",
        repo_path="repo",
        package_id="pkg-b",
    )
    core = CodeModule(
        "pkg-a/src/core.rs",
        "rust",
        "2",
        ("crate::config::Config",),
        (),
        repo_id="repo",
        repo_path="repo",
        package_id="pkg-a",
    )
    cid_by_source = {
        _source_key(sibling): "code/repo/pkg-b/src/config.rs",
        _source_key(core): "code/repo/pkg-a/src/core.rs",
    }

    module_keys = _module_keys([sibling, core], cid_by_source)
    resolved = _with_relationships(core, cid_by_source, module_keys)

    assert resolved.relationships == ()


def test_extract_python_module_facts_are_deterministic(tmp_path: Path):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import extract_module

    repo = tmp_path / "repo"
    _write_python_repo(repo)

    first = extract_module(repo / "pkg" / "service.py", repo, language="python")
    second = extract_module(repo / "pkg" / "service.py", repo, language="python")

    assert first == second
    assert first.source_path == "pkg/service.py"
    assert first.language == "python"
    assert first.imports == ("json", "pathlib.Path")
    assert [(s.kind, s.name, s.start_line, s.end_line) for s in first.symbols] == [
        ("class", "UserService", 4, 6),
        ("function", "load_user", 5, 6),
        ("function", "helper", 8, 9),
    ]
    assert len(first.source_hash) == 64


def test_index_codebase_writes_valid_searchable_managed_concepts(tmp_path: Path):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import index_codebase

    repo = tmp_path / "repo"
    bundle = tmp_path / "kb"
    _write_python_repo(repo)

    result = index_codebase(repo, bundle)

    assert result.written == 2
    assert result.updated == 0
    service = bundle / "code" / "pkg" / "service.py.md"
    assert service.is_file()
    text = service.read_text(encoding="utf-8")
    assert "type: CodeModule" in text
    assert "title: pkg/service.py" in text
    assert "source_path: pkg/service.py" in text
    assert "language: python" in text
    assert "managed_by: okf-code" in text
    assert "# Overview" in text
    assert "# Symbols" in text
    assert "UserService" in text
    assert "load_user" in text
    assert "# Relationships" in text
    assert "json" in text
    assert "# Impact notes" in text
    assert "syntax-derived" in text
    assert "# Citations" in text
    assert "<!-- okf-code:start -->" in text
    assert "<!-- okf-code:end -->" in text

    report = validate_bundle(bundle)
    assert report.conformant, report.to_dict()
    hits = search(build_index(bundle), "UserService")
    assert hits[0].cid == "code/pkg/service.py"


def test_index_codebase_preserves_narrative_outside_managed_section(tmp_path: Path):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import index_codebase

    repo = tmp_path / "repo"
    bundle = tmp_path / "kb"
    _write_python_repo(repo)
    index_codebase(repo, bundle)

    service = bundle / "code" / "pkg" / "service.py.md"
    original = service.read_text(encoding="utf-8")
    service.write_text(
        original.replace(
            "<!-- okf-code:start -->",
            "# Human preface\n\nKeep this preface.\n\n<!-- okf-code:start -->",
        )
        + "\n# Human notes\n\nKeep this explanation.\n",
        encoding="utf-8",
    )

    (repo / "pkg" / "service.py").write_text(
        (repo / "pkg" / "service.py").read_text(encoding="utf-8")
        + "\ndef normalize_email(value: str) -> str:\n    return value.lower()\n",
        encoding="utf-8",
    )
    result = index_codebase(repo, bundle, update=True)
    updated = service.read_text(encoding="utf-8")

    assert result.updated >= 1
    assert "# Human preface" in updated
    assert "Keep this preface." in updated
    assert "# Human notes" in updated
    assert "Keep this explanation." in updated
    assert "normalize_email" in updated


def test_index_codebase_does_not_overwrite_existing_root_index(tmp_path: Path):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import index_codebase

    repo = tmp_path / "repo"
    bundle = tmp_path / "kb"
    _write_python_repo(repo)
    bundle.mkdir()
    (bundle / "index.md").write_text(
        "---\nokf_version: '0.1'\n---\n# Curated root\n\nKeep me.\n",
        encoding="utf-8",
    )

    index_codebase(repo, bundle)

    assert "Keep me." in (bundle / "index.md").read_text(encoding="utf-8")


def test_index_codebase_rejects_normalized_concept_id_collisions(tmp_path: Path):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import index_codebase

    repo = tmp_path / "repo"
    src = repo / "src"
    src.mkdir(parents=True)
    (src / "a b.py").write_text("class SpaceName:\n    pass\n", encoding="utf-8")
    (src / "a-b.py").write_text("class DashName:\n    pass\n", encoding="utf-8")
    bundle = tmp_path / "kb"

    with pytest.raises(ValueError, match="duplicate code concept id"):
        index_codebase(repo, bundle, languages=["python"])

    assert not (bundle / "code").exists()


def test_index_codebase_preflights_destination_parent_conflicts_before_writing(
    tmp_path: Path,
):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import index_codebase

    repo = tmp_path / "repo"
    (repo / "aaa").mkdir(parents=True)
    (repo / "zzz" / "blocked").mkdir(parents=True)
    (repo / "aaa" / "first.py").write_text("class First:\n    pass\n", encoding="utf-8")
    (repo / "zzz" / "blocked" / "second.py").write_text(
        "class Second:\n    pass\n",
        encoding="utf-8",
    )
    bundle = tmp_path / "kb"
    blocking_parent = bundle / "code" / "zzz" / "blocked"
    blocking_parent.parent.mkdir(parents=True)
    blocking_parent.write_text("not a directory\n", encoding="utf-8")

    with pytest.raises(ValueError, match="parent is not a directory"):
        index_codebase(repo, bundle, languages=["python"])

    assert not (bundle / "code" / "aaa" / "first.py.md").exists()


def test_index_codebase_links_resolvable_local_imports_for_depth_reads(tmp_path: Path):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import index_codebase

    repo = tmp_path / "repo"
    package = repo / "pkg"
    package.mkdir(parents=True)
    (package / "models.py").write_text("class User:\n    pass\n", encoding="utf-8")
    (package / "service.py").write_text(
        "from .models import User\n\nclass UserService:\n    pass\n",
        encoding="utf-8",
    )
    bundle = tmp_path / "kb"

    index_codebase(repo, bundle, languages=["python"])

    service = (bundle / "code" / "pkg" / "service.py.md").read_text(encoding="utf-8")
    assert "[.models.User](/code/pkg/models.py.md)" in service
    context = read_concept(bundle, "code/pkg/service.py", depth=1)
    assert "# code/pkg/models.py (depth 1)" in context
    assert "User" in context


def test_index_codebase_writes_reverse_dependents_for_depth_reads(tmp_path: Path):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import index_codebase

    repo = tmp_path / "repo"
    package = repo / "pkg"
    package.mkdir(parents=True)
    (package / "models.py").write_text("class User:\n    pass\n", encoding="utf-8")
    (package / "service.py").write_text(
        "from .models import User\n\nclass UserService:\n    pass\n",
        encoding="utf-8",
    )
    bundle = tmp_path / "kb"

    index_codebase(repo, bundle, languages=["python"])

    models = (bundle / "code" / "pkg" / "models.py.md").read_text(encoding="utf-8")
    assert "Used by" in models
    assert "[pkg/service.py](/code/pkg/service.py.md)" in models
    context = read_concept(bundle, "code/pkg/models.py", depth=1)
    assert "# code/pkg/service.py (depth 1)" in context


def test_index_codebase_links_python_package_relative_imports_without_global_stem_fallback(
    tmp_path: Path,
):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import index_codebase

    repo = tmp_path / "repo"
    (repo / "pkg" / "feature").mkdir(parents=True)
    (repo / "other").mkdir(parents=True)
    (repo / "pkg" / "models.py").write_text("class PackageModel:\n    pass\n", encoding="utf-8")
    (repo / "pkg" / "feature" / "models.py").write_text(
        "class FeatureModel:\n    pass\n",
        encoding="utf-8",
    )
    (repo / "other" / "models.py").write_text("class OtherModel:\n    pass\n", encoding="utf-8")
    (repo / "pkg" / "service.py").write_text(
        "from . import models\n\nclass PackageService:\n    pass\n",
        encoding="utf-8",
    )
    (repo / "pkg" / "feature" / "service.py").write_text(
        "from .. import models\n\nclass FeatureService:\n    pass\n",
        encoding="utf-8",
    )
    bundle = tmp_path / "kb"

    index_codebase(repo, bundle, languages=["python"])

    package_context = read_concept(bundle, "code/pkg/service.py", depth=1)
    assert "# code/pkg/models.py (depth 1)" in package_context
    assert "# code/other/models.py (depth 1)" not in package_context
    feature_context = read_concept(bundle, "code/pkg/feature/service.py", depth=1)
    assert "# code/pkg/models.py (depth 1)" in feature_context
    assert "# code/pkg/feature/models.py (depth 1)" not in feature_context


def test_index_codebase_links_grouped_python_relative_imports(tmp_path: Path):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import index_codebase

    repo = tmp_path / "repo"
    package = repo / "pkg"
    package.mkdir(parents=True)
    (package / "models.py").write_text("class User:\n    pass\n", encoding="utf-8")
    (package / "utils.py").write_text("def normalize():\n    return None\n", encoding="utf-8")
    (package / "service.py").write_text(
        "from . import models, utils\n\nclass UserService:\n    pass\n",
        encoding="utf-8",
    )
    bundle = tmp_path / "kb"

    index_codebase(repo, bundle, languages=["python"])

    service = (bundle / "code" / "pkg" / "service.py.md").read_text(encoding="utf-8")
    assert "[.models](/code/pkg/models.py.md)" in service
    assert "[.utils](/code/pkg/utils.py.md)" in service
    context = read_concept(bundle, "code/pkg/service.py", depth=1)
    assert "# code/pkg/models.py (depth 1)" in context
    assert "# code/pkg/utils.py (depth 1)" in context


def test_index_codebase_links_grouped_python_direct_imports(tmp_path: Path):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import index_codebase

    repo = tmp_path / "repo"
    package = repo / "pkg"
    package.mkdir(parents=True)
    (package / "models.py").write_text("class User:\n    pass\n", encoding="utf-8")
    (package / "utils.py").write_text("def normalize():\n    return None\n", encoding="utf-8")
    (package / "service.py").write_text(
        "import pkg.models, pkg.utils\n\nclass UserService:\n    pass\n",
        encoding="utf-8",
    )
    bundle = tmp_path / "kb"

    index_codebase(repo, bundle, languages=["python"])

    service = (bundle / "code" / "pkg" / "service.py.md").read_text(encoding="utf-8")
    assert "[pkg.models](/code/pkg/models.py.md)" in service
    assert "[pkg.utils](/code/pkg/utils.py.md)" in service
    context = read_concept(bundle, "code/pkg/service.py", depth=1)
    assert "# code/pkg/models.py (depth 1)" in context
    assert "# code/pkg/utils.py (depth 1)" in context


def test_index_codebase_links_js_relative_imports_for_depth_reads(tmp_path: Path):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import index_codebase

    repo = tmp_path / "repo"
    src = repo / "src"
    src.mkdir(parents=True)
    (src / "foo.ts").write_text("export class Foo {}\n", encoding="utf-8")
    (src / "app.ts").write_text(
        'import { Foo } from "./foo";\nclass App { run(): Foo { return new Foo(); } }\n',
        encoding="utf-8",
    )
    bundle = tmp_path / "kb"

    index_codebase(repo, bundle, languages=["typescript"])

    app = (bundle / "code" / "src" / "app.ts.md").read_text(encoding="utf-8")
    assert "[./foo](/code/src/foo.ts.md)" in app
    context = read_concept(bundle, "code/src/app.ts", depth=1)
    assert "# code/src/foo.ts (depth 1)" in context
    assert "Foo" in context


def test_index_codebase_links_js_parent_relative_imports_for_depth_reads(tmp_path: Path):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import index_codebase

    repo = tmp_path / "repo"
    (repo / "src" / "components").mkdir(parents=True)
    (repo / "src" / "foo.ts").write_text("export class ParentFoo {}\n", encoding="utf-8")
    (repo / "src" / "components" / "app.ts").write_text(
        'import { ParentFoo } from "../foo";\nclass App { run(): ParentFoo { return new ParentFoo(); } }\n',
        encoding="utf-8",
    )
    bundle = tmp_path / "kb"

    index_codebase(repo, bundle, languages=["typescript"])

    app = (bundle / "code" / "src" / "components" / "app.ts.md").read_text(encoding="utf-8")
    assert "[../foo](/code/src/foo.ts.md)" in app
    context = read_concept(bundle, "code/src/components/app.ts", depth=1)
    assert "# code/src/foo.ts (depth 1)" in context
    assert "ParentFoo" in context


def test_index_codebase_links_rust_crate_and_super_imports_for_depth_reads(tmp_path: Path):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import index_codebase

    repo = tmp_path / "repo"
    src = repo / "src"
    (src / "runner").mkdir(parents=True)
    (repo / "Cargo.toml").write_text("[package]\nname = \"demo\"\nversion = \"0.1.0\"\n", encoding="utf-8")
    (src / "delegation.rs").write_text("pub struct DelegationRegistry;\n", encoding="utf-8")
    (src / "runner" / "core.rs").write_text(
        "use crate::delegation::{DelegationRegistry};\n"
        "pub struct ExecutionRunner;\n",
        encoding="utf-8",
    )
    (src / "runner" / "session_invoker.rs").write_text(
        "use super::core::ExecutionRunner;\n"
        "pub fn invoke() {}\n",
        encoding="utf-8",
    )
    bundle = tmp_path / "kb"

    index_codebase(repo, bundle, languages=["rust"])

    core = (bundle / "code" / "src" / "runner" / "core.rs.md").read_text(encoding="utf-8")
    assert "[crate::delegation::{DelegationRegistry}](/code/src/delegation.rs.md)" in core
    assert "[src/runner/session_invoker.rs](/code/src/runner/session_invoker.rs.md)" in core
    context = read_concept(bundle, "code/src/runner/core.rs", depth=1)
    assert "# code/src/delegation.rs (depth 1)" in context
    assert "# code/src/runner/session_invoker.rs (depth 1)" in context


def test_index_codebase_resolves_rust_crate_imports_within_current_package(tmp_path: Path):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import index_codebase

    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    apps = repo / "apps" / "cli"
    gateway = repo / "gateway" / "gateway-execution"
    for package in (apps, gateway):
        (package / "src").mkdir(parents=True)
        (package / "Cargo.toml").write_text(
            "[package]\nname = \"demo\"\nversion = \"0.1.0\"\n",
            encoding="utf-8",
        )
    (apps / "src" / "config.rs").write_text("pub struct CliConfig;\n", encoding="utf-8")
    (gateway / "src" / "config.rs").write_text("pub struct ExecutionConfig;\n", encoding="utf-8")
    (gateway / "src" / "core.rs").write_text(
        "use crate::config::ExecutionConfig;\npub struct ExecutionRunner;\n",
        encoding="utf-8",
    )
    bundle = tmp_path / "kb"

    index_codebase(repo, bundle, languages=["rust"])

    core = (bundle / "code" / "gateway" / "gateway-execution" / "src" / "core.rs.md").read_text(
        encoding="utf-8"
    )
    assert (
        "[crate::config::ExecutionConfig]"
        "(/code/gateway/gateway-execution/src/config.rs.md)"
    ) in core
    assert "(/code/apps/cli/src/config.rs.md)" not in core


def test_index_workspace_resolves_rust_crate_imports_within_repo_package(tmp_path: Path):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import index_codebase

    workspace = tmp_path / "workspace"
    repo = workspace / "gateway"
    apps = repo / "apps" / "cli"
    execution = repo / "gateway-execution"
    (repo / ".git").mkdir(parents=True)
    for package in (apps, execution):
        (package / "src").mkdir(parents=True)
        (package / "Cargo.toml").write_text(
            "[package]\nname = \"demo\"\nversion = \"0.1.0\"\n",
            encoding="utf-8",
        )
    (apps / "src" / "config.rs").write_text("pub struct CliConfig;\n", encoding="utf-8")
    (execution / "src" / "config.rs").write_text("pub struct ExecutionConfig;\n", encoding="utf-8")
    (execution / "src" / "core.rs").write_text(
        "use crate::config::ExecutionConfig;\npub struct ExecutionRunner;\n",
        encoding="utf-8",
    )
    bundle = tmp_path / "kb"

    index_codebase(workspace, bundle, languages=["rust"])

    core = (
        bundle
        / "code"
        / "gateway"
        / "gateway-execution"
        / "src"
        / "core.rs.md"
    ).read_text(encoding="utf-8")
    assert (
        "[crate::config::ExecutionConfig]"
        "(/code/gateway/gateway-execution/src/config.rs.md)"
    ) in core
    assert "(/code/gateway/apps/cli/src/config.rs.md)" not in core


def test_index_workspace_does_not_fallback_rust_crate_import_to_sibling_package(
    tmp_path: Path,
):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import index_codebase

    workspace = tmp_path / "workspace"
    repo = workspace / "gateway"
    apps = repo / "apps" / "cli"
    execution = repo / "gateway-execution"
    (repo / ".git").mkdir(parents=True)
    for package in (apps, execution):
        (package / "src").mkdir(parents=True)
        (package / "Cargo.toml").write_text(
            "[package]\nname = \"demo\"\nversion = \"0.1.0\"\n",
            encoding="utf-8",
        )
    (apps / "src" / "config.rs").write_text("pub struct CliConfig;\n", encoding="utf-8")
    (execution / "src" / "core.rs").write_text(
        "use crate::config::ExecutionConfig;\npub struct ExecutionRunner;\n",
        encoding="utf-8",
    )
    bundle = tmp_path / "kb"

    index_codebase(workspace, bundle, languages=["rust"])

    core = (
        bundle
        / "code"
        / "gateway"
        / "gateway-execution"
        / "src"
        / "core.rs.md"
    ).read_text(encoding="utf-8")
    assert "`crate::config::ExecutionConfig`" in core
    assert "(/code/gateway/apps/cli/src/config.rs.md)" not in core


def test_index_codebase_expands_grouped_rust_crate_imports_without_root_false_edge(
    tmp_path: Path,
):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import index_codebase

    repo = tmp_path / "repo"
    src = repo / "src"
    src.mkdir(parents=True)
    (repo / "Cargo.toml").write_text("[package]\nname = \"demo\"\nversion = \"0.1.0\"\n", encoding="utf-8")
    (src / "lib.rs").write_text("pub mod config;\n", encoding="utf-8")
    (src / "config.rs").write_text("pub struct Config;\n", encoding="utf-8")
    (src / "core.rs").write_text(
        "use crate::{config::Config};\npub struct Core;\n",
        encoding="utf-8",
    )
    bundle = tmp_path / "kb"

    index_codebase(repo, bundle, languages=["rust"])

    core = (bundle / "code" / "src" / "core.rs.md").read_text(encoding="utf-8")
    assert "[crate::{config::Config}](/code/src/config.rs.md)" in core
    assert "[crate::{config::Config}](/code/src/lib.rs.md)" not in core


def test_index_codebase_does_not_truncate_unresolved_grouped_rust_import_to_crate_root(
    tmp_path: Path,
):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import index_codebase

    repo = tmp_path / "repo"
    src = repo / "src"
    src.mkdir(parents=True)
    (repo / "Cargo.toml").write_text("[package]\nname = \"demo\"\nversion = \"0.1.0\"\n", encoding="utf-8")
    (src / "lib.rs").write_text("pub mod config;\n", encoding="utf-8")
    (src / "core.rs").write_text(
        "use crate::{missing::Thing};\npub struct Core;\n",
        encoding="utf-8",
    )
    bundle = tmp_path / "kb"

    index_codebase(repo, bundle, languages=["rust"])

    core = (bundle / "code" / "src" / "core.rs.md").read_text(encoding="utf-8")
    assert "`crate::{missing::Thing}`" in core
    assert "[crate::{missing::Thing}](/code/src/lib.rs.md)" not in core


def test_index_workspace_does_not_resolve_imports_across_repositories(tmp_path: Path):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import index_codebase

    workspace = tmp_path / "workspace"
    repo_a = workspace / "api"
    repo_b = workspace / "worker"
    (repo_a / ".git").mkdir(parents=True)
    (repo_a / "pkg").mkdir()
    (repo_b / ".git").mkdir(parents=True)
    (repo_b / "pkg").mkdir()
    (repo_a / "pkg" / "service.py").write_text(
        "import pkg.models\n\nclass ApiService:\n    pass\n",
        encoding="utf-8",
    )
    (repo_b / "pkg" / "models.py").write_text("class WorkerModel:\n    pass\n", encoding="utf-8")
    bundle = tmp_path / "kb"

    index_codebase(workspace, bundle, languages=["python"])

    service = (bundle / "code" / "api" / "pkg" / "service.py.md").read_text(encoding="utf-8")
    models = (bundle / "code" / "worker" / "pkg" / "models.py.md").read_text(encoding="utf-8")
    assert "[pkg.models](/code/worker/pkg/models.py.md)" not in service
    assert "Used by" not in models


def test_index_codebase_refuses_to_update_unmanaged_existing_concept(tmp_path: Path):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import index_codebase

    repo = tmp_path / "repo"
    package = repo / "pkg"
    package.mkdir(parents=True)
    (package / "service.py").write_text("class UserService:\n    pass\n", encoding="utf-8")
    bundle = tmp_path / "kb"
    unmanaged = bundle / "code" / "pkg" / "service.py.md"
    unmanaged.parent.mkdir(parents=True)
    unmanaged.write_text(
        "---\ntype: Note\ntitle: Hand written\n---\n# Keep this\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="non-okf-code concept"):
        index_codebase(repo, bundle, languages=["python"], update=True)

    assert unmanaged.read_text(encoding="utf-8") == (
        "---\ntype: Note\ntitle: Hand written\n---\n# Keep this\n"
    )


def test_index_codebase_refuses_to_skip_unmanaged_existing_concept(tmp_path: Path):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import index_codebase

    repo = tmp_path / "repo"
    package = repo / "pkg"
    package.mkdir(parents=True)
    (package / "service.py").write_text("class UserService:\n    pass\n", encoding="utf-8")
    bundle = tmp_path / "kb"
    unmanaged = bundle / "code" / "pkg" / "service.py.md"
    unmanaged.parent.mkdir(parents=True)
    unmanaged.write_text(
        "---\ntype: Note\ntitle: Hand written\n---\n# Keep this\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="non-okf-code concept"):
        index_codebase(repo, bundle, languages=["python"], update=False)

    assert unmanaged.read_text(encoding="utf-8") == (
        "---\ntype: Note\ntitle: Hand written\n---\n# Keep this\n"
    )


def test_missing_tree_sitter_dependency_error_is_actionable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    import okf_kit.code.treesitter.runtime as runtime

    repo = tmp_path / "repo"
    _write_python_repo(repo)

    real_import = __import__

    def fake_import(name, *args, **kwargs):  # type: ignore[no-untyped-def]
        if name == "tree_sitter_language_pack":
            raise ModuleNotFoundError(name)
        return real_import(name, *args, **kwargs)

    monkeypatch.delitem(sys.modules, "tree_sitter_language_pack", raising=False)
    monkeypatch.setattr(runtime.builtins, "__import__", fake_import)

    with pytest.raises(ValueError, match=r"okf-kit\[treesitter\]"):
        from okf_kit.code.indexer import extract_module

        extract_module(repo / "pkg" / "service.py", repo, language="python")


def test_requested_language_adapters_extract_symbols(tmp_path: Path):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import index_codebase

    repo = tmp_path / "polyglot"
    (repo / "src").mkdir(parents=True)
    samples = {
        "src/app.py": "class PyService:\n    def run(self):\n        pass\n",
        "src/app.js": "class JsService { run() {} }\nfunction jsHelper() {}\n",
        "src/app.ts": "interface TsShape { x: string }\nclass TsService { run(): void {} }\n",
        "src/card.tsx": "export function Card() { return <div>Hello</div>; }\n",
        "src/App.java": "import java.util.List;\nclass JavaService { void run() {} }\n",
        "src/App.scala": "class ScalaService { def run(): Unit = {} }\nobject ScalaObj {}\n",
        "src/lib.rs": "pub struct RustService;\nimpl RustService { pub fn run(&self) {} }\n",
        "src/main.go": "package main\n\ntype GoService struct{}\nfunc goHelper() {}\n",
        "src/App.kt": "class KotlinService { fun run() {} }\nfun kotlinHelper() {}\n",
        "src/app.pl": "package PerlService;\nsub run { return 1; }\n",
        "src/App.cs": "using System;\nclass CSharpService { void Run() {} }\n",
        "src/app.php": "<?php\nclass PhpService { public function run() {} }\nfunction php_helper() {}\n",
        "src/index.html": "<html><body><main id=\"app\"><h1>Hello</h1></main></body></html>\n",
    }
    for rel, text in samples.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    bundle = tmp_path / "kb"
    result = index_codebase(
        repo,
        bundle,
        languages=[
            "python",
            "javascript",
            "typescript",
            "java",
            "scala",
            "rust",
            "go",
            "kotlin",
            "perl",
            "csharp",
            "php",
            "html",
        ],
    )

    assert result.written == len(samples)
    assert validate_bundle(bundle).conformant
    index = build_index(bundle)
    for term in (
        "PyService",
        "JsService",
        "TsService",
        "Card",
        "JavaService",
        "ScalaService",
        "RustService",
        "GoService",
        "KotlinService",
        "PerlService",
        "CSharpService",
        "PhpService",
        "main",
    ):
        assert search(index, term), term


def test_index_workspace_preserves_repo_identity_for_colliding_paths(tmp_path: Path):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import index_codebase

    workspace = tmp_path / "workspace"
    repo_a = workspace / "api"
    repo_b = workspace / "worker"
    for repo, class_name in ((repo_a, "ApiService"), (repo_b, "WorkerService")):
        (repo / ".git").mkdir(parents=True)
        (repo / "src").mkdir()
        (repo / "src" / "app.py").write_text(f"class {class_name}:\n    pass\n", encoding="utf-8")
    bundle = tmp_path / "kb"

    result = index_codebase(workspace, bundle, languages=["python"])

    assert result.written >= 2
    api = bundle / "code" / "api" / "src" / "app.py.md"
    worker = bundle / "code" / "worker" / "src" / "app.py.md"
    assert api.is_file()
    assert worker.is_file()
    api_text = api.read_text(encoding="utf-8")
    worker_text = worker.read_text(encoding="utf-8")
    assert "repo: api" in api_text
    assert "source_path: src/app.py" in api_text
    assert "repo: worker" in worker_text
    assert "source_path: src/app.py" in worker_text
    assert validate_bundle(bundle).conformant


def test_index_workspace_assigns_unique_repo_ids_after_normalization(tmp_path: Path):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import index_codebase

    workspace = tmp_path / "workspace"
    for repo_name, class_name in (("my repo", "SpaceRepo"), ("my-repo", "DashRepo")):
        repo = workspace / repo_name
        (repo / ".git").mkdir(parents=True)
        (repo / "src").mkdir()
        (repo / "src" / "app.py").write_text(f"class {class_name}:\n    pass\n", encoding="utf-8")
    bundle = tmp_path / "kb"

    index_codebase(workspace, bundle, languages=["python"])

    actual_dash = bundle / "code" / "my-repo" / "src" / "app.py.md"
    normalized_space = bundle / "code" / "my-repo-2" / "src" / "app.py.md"
    assert actual_dash.is_file()
    assert normalized_space.is_file()
    dash_text = actual_dash.read_text(encoding="utf-8")
    space_text = normalized_space.read_text(encoding="utf-8")
    assert "repo: my-repo" in dash_text
    assert "repo_path: my-repo" in dash_text
    assert "DashRepo" in dash_text
    assert "repo: my-repo-2" in space_text
    assert "repo_path: my repo" in space_text
    assert "SpaceRepo" in space_text


def test_index_workspace_repo_ids_stay_unique_after_suffix_collision(tmp_path: Path):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import index_codebase

    workspace = tmp_path / "workspace"
    for repo_name, class_name in (("a b", "SpaceRepo"), ("a-b", "DashRepo"), ("a-b-2", "SuffixedRepo")):
        repo = workspace / repo_name
        (repo / ".git").mkdir(parents=True)
        (repo / "src").mkdir()
        (repo / "src" / "app.py").write_text(f"class {class_name}:\n    pass\n", encoding="utf-8")
    bundle = tmp_path / "kb"

    index_codebase(workspace, bundle, languages=["python"])

    assert (bundle / "code" / "a-b" / "src" / "app.py.md").is_file()
    assert (bundle / "code" / "a-b-2" / "src" / "app.py.md").is_file()
    assert (bundle / "code" / "a-b-3" / "src" / "app.py.md").is_file()


def test_index_workspace_repo_selector_prefers_unambiguous_repo_path(tmp_path: Path):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import index_codebase

    workspace = tmp_path / "workspace"
    for repo_name, class_name in (("my repo", "SpaceRepo"), ("my-repo", "DashRepo")):
        repo = workspace / repo_name
        (repo / ".git").mkdir(parents=True)
        (repo / "src").mkdir()
        (repo / "src" / "app.py").write_text(f"class {class_name}:\n    pass\n", encoding="utf-8")
    bundle = tmp_path / "kb"

    index_codebase(workspace, bundle, languages=["python"], repos=["my-repo"])

    assert (bundle / "code" / "my-repo" / "src" / "app.py.md").is_file()
    assert not (bundle / "code" / "my-repo-2" / "src" / "app.py.md").exists()


def test_index_workspace_skips_noisy_files_by_default_and_allows_tests(
    tmp_path: Path,
):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import index_codebase

    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True)
    (repo / "tests").mkdir()
    (repo / "dist").mkdir()
    (repo / "templates").mkdir()
    (repo / "static").mkdir()
    (repo / "src" / "service.py").write_text("class Service:\n    pass\n", encoding="utf-8")
    (repo / "tests" / "test_service.py").write_text(
        "class ServiceTest:\n    pass\n",
        encoding="utf-8",
    )
    (repo / "dist" / "generated.py").write_text("class Generated:\n    pass\n", encoding="utf-8")
    (repo / "templates" / "report.py").write_text("class Template:\n    pass\n", encoding="utf-8")
    (repo / "static" / "app.py").write_text("class StaticAsset:\n    pass\n", encoding="utf-8")
    bundle = tmp_path / "kb"

    result = index_codebase(repo, bundle, languages=["python"])

    assert result.written == 1
    assert (bundle / "code" / "src" / "service.py.md").is_file()
    assert not (bundle / "code" / "tests" / "test_service.py.md").exists()
    assert not (bundle / "code" / "dist" / "generated.py.md").exists()
    assert not (bundle / "code" / "templates" / "report.py.md").exists()
    assert not (bundle / "code" / "static" / "app.py.md").exists()

    bundle_with_tests = tmp_path / "kb-tests"
    result_with_tests = index_codebase(
        repo,
        bundle_with_tests,
        languages=["python"],
        include_tests=True,
    )

    assert result_with_tests.written == 2
    assert (bundle_with_tests / "code" / "tests" / "test_service.py.md").is_file()
    assert not (bundle_with_tests / "code" / "dist" / "generated.py.md").exists()

    bundle_with_generated = tmp_path / "kb-generated"
    result_with_generated = index_codebase(
        repo,
        bundle_with_generated,
        languages=["python"],
        include=["dist/generated.py", "static/app.py"],
    )

    assert result_with_generated.written == 2
    assert (bundle_with_generated / "code" / "dist" / "generated.py.md").is_file()
    assert (bundle_with_generated / "code" / "static" / "app.py.md").is_file()


def test_index_workspace_rejects_scope_escapes_before_writes(tmp_path: Path):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import index_codebase

    workspace = tmp_path / "workspace"
    outside = tmp_path / "outside"
    (workspace / "repo" / ".git").mkdir(parents=True)
    (workspace / "repo" / "src").mkdir()
    (workspace / "repo" / "src" / "service.py").write_text(
        "class Service:\n    pass\n",
        encoding="utf-8",
    )
    outside.mkdir()
    (outside / "escape.py").write_text("class Escape:\n    pass\n", encoding="utf-8")
    bundle = tmp_path / "kb"

    with pytest.raises(ValueError, match="escapes workspace"):
        index_codebase(workspace, bundle, languages=["python"], include=[str(outside / "*.py")])

    with pytest.raises(ValueError, match="escapes workspace"):
        index_codebase(workspace, bundle, languages=["python"], repos=["../outside"])

    assert not bundle.exists()


def test_index_workspace_rejects_bundle_symlink_destination_escape(tmp_path: Path):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import index_codebase

    repo = tmp_path / "repo"
    (repo / "src" / "escaped").mkdir(parents=True)
    (repo / "src" / "escaped" / "service.py").write_text(
        "class Service:\n    pass\n",
        encoding="utf-8",
    )
    bundle = tmp_path / "kb"
    outside = tmp_path / "outside"
    outside.mkdir()
    symlink_parent = bundle / "code" / "src" / "escaped"
    symlink_parent.parent.mkdir(parents=True)
    symlink_parent.symlink_to(outside, target_is_directory=True)

    with pytest.raises(ValueError, match="symlink"):
        index_codebase(repo, bundle, languages=["python"])

    assert not (outside / "service.py.md").exists()


def test_index_workspace_preflights_summary_destinations_before_module_writes(tmp_path: Path):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import index_codebase

    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True)
    (repo / "src" / "service.py").write_text("class Service:\n    pass\n", encoding="utf-8")
    bundle = tmp_path / "kb"
    outside = tmp_path / "outside"
    outside.mkdir()
    summary_parent = bundle / "code-summaries" / "areas"
    summary_parent.parent.mkdir(parents=True)
    summary_parent.symlink_to(outside, target_is_directory=True)

    with pytest.raises(ValueError, match="summary.*symlink"):
        index_codebase(repo, bundle, languages=["python"])

    assert not (bundle / "code" / "src" / "service.py.md").exists()
    assert not (outside / "src.md").exists()


def test_index_workspace_no_match_scope_does_not_follow_summary_symlink(
    tmp_path: Path,
):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import index_codebase

    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True)
    (repo / "src" / "service.py").write_text("class Service:\n    pass\n", encoding="utf-8")
    bundle = tmp_path / "kb"
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "repository.md").write_text(
        "---\ntype: CodeSummary\ntitle: stale\nmanaged_by: okf-code\n---\n"
        "<!-- okf-code:managed:start -->\nstale\n<!-- okf-code:managed:end -->\n",
        encoding="utf-8",
    )
    (bundle / "index.md").parent.mkdir(parents=True)
    (bundle / "index.md").write_text("---\ntype: Index\ntitle: kb\n---\n", encoding="utf-8")
    (bundle / "code-summaries").symlink_to(outside, target_is_directory=True)

    result = index_codebase(repo, bundle, languages=["python"], include=["src/missing.py"])

    assert result.written == 0
    assert result.updated == 0
    assert result.skipped == 0
    assert (outside / "repository.md").exists()


def test_index_workspace_no_match_include_does_not_follow_source_symlink(
    tmp_path: Path,
):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import index_codebase

    repo = tmp_path / "repo"
    outside = tmp_path / "outside"
    (repo / "src").mkdir(parents=True)
    outside.mkdir()
    (outside / "escape.py").write_text("class Escape:\n    pass\n", encoding="utf-8")
    (repo / "src" / "link.py").symlink_to(outside / "escape.py")
    bundle = tmp_path / "kb"

    result = index_codebase(repo, bundle, languages=["python"], include=["src/missing.py"])

    assert result.written == 0
    assert result.updated == 0
    assert result.skipped == 0
    assert not bundle.exists()


def test_index_workspace_matched_include_rejects_source_symlink_escape(
    tmp_path: Path,
):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import index_codebase

    repo = tmp_path / "repo"
    outside = tmp_path / "outside"
    (repo / "src").mkdir(parents=True)
    outside.mkdir()
    (outside / "escape.py").write_text("class Escape:\n    pass\n", encoding="utf-8")
    (repo / "src" / "link.py").symlink_to(outside / "escape.py")

    with pytest.raises(ValueError, match="source path escapes repository"):
        index_codebase(repo, tmp_path / "kb", languages=["python"], include=["src/link.py"])


def test_index_workspace_no_match_repo_does_not_follow_unselected_symlink_repo(
    tmp_path: Path,
):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import index_codebase

    workspace = tmp_path / "workspace"
    outside = tmp_path / "outside"
    (workspace / "real" / ".git").mkdir(parents=True)
    (workspace / "real" / "src").mkdir()
    (workspace / "real" / "src" / "service.py").write_text(
        "class Service:\n    pass\n",
        encoding="utf-8",
    )
    (outside / ".git").mkdir(parents=True)
    (workspace / "linked").symlink_to(outside, target_is_directory=True)
    bundle = tmp_path / "kb"

    result = index_codebase(workspace, bundle, languages=["python"], repos=["missing"])

    assert result.written == 0
    assert result.updated == 0
    assert result.skipped == 0
    assert not bundle.exists()


def test_index_workspace_matched_repo_rejects_symlink_escape(tmp_path: Path):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import index_codebase

    workspace = tmp_path / "workspace"
    outside = tmp_path / "outside"
    (workspace / "real" / ".git").mkdir(parents=True)
    (outside / ".git").mkdir(parents=True)
    (workspace / "linked").symlink_to(outside, target_is_directory=True)

    with pytest.raises(ValueError, match="repo selection escapes workspace"):
        index_codebase(workspace, tmp_path / "kb", languages=["python"], repos=["linked"])


def test_index_workspace_no_match_explicit_scope_preserves_existing_code_map(
    tmp_path: Path,
):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import index_codebase

    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True)
    (repo / "src" / "service.py").write_text("class Service:\n    pass\n", encoding="utf-8")
    bundle = tmp_path / "kb"
    index_codebase(repo, bundle, languages=["python"])
    module = bundle / "code" / "src" / "service.py.md"
    summary = bundle / "code-summaries" / "repository.md"
    assert module.is_file()
    assert summary.is_file()

    result = index_codebase(repo, bundle, languages=["python"], include=["src/missing.py"])

    assert result.written == 0
    assert result.updated == 0
    assert result.skipped == 0
    assert module.is_file()
    assert summary.is_file()


def test_compact_profile_synthesizes_context_and_caps_symbol_inventory(tmp_path: Path):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import index_codebase

    repo = tmp_path / "repo"
    src = repo / "src"
    src.mkdir(parents=True)
    functions = "\n".join(f"def helper_{idx}():\n    return {idx}\n" for idx in range(30))
    (src / "service.py").write_text(
        "class UserService:\n    pass\n\n" + functions,
        encoding="utf-8",
    )
    bundle = tmp_path / "kb"

    index_codebase(repo, bundle, languages=["python"], profile="compact")

    text = (bundle / "code" / "src" / "service.py.md").read_text(encoding="utf-8")
    assert "Purpose:" in text
    assert "Role:" in text
    assert "Impact:" in text
    assert "high-signal" in text
    assert "omitted from compact profile" in text
    assert "helper_0" in text
    assert "helper_29" not in text


def test_full_profile_renders_more_symbol_detail_when_requested(tmp_path: Path):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import index_codebase

    repo = tmp_path / "repo"
    src = repo / "src"
    src.mkdir(parents=True)
    functions = "\n".join(f"def helper_{idx}():\n    return {idx}\n" for idx in range(30))
    (src / "service.py").write_text(functions, encoding="utf-8")
    bundle = tmp_path / "kb"

    index_codebase(repo, bundle, languages=["python"], profile="full")

    text = (bundle / "code" / "src" / "service.py.md").read_text(encoding="utf-8")
    assert "helper_29" in text
    assert "omitted from compact profile" not in text


def test_compact_profile_reports_omitted_relationship_counts():
    from okf_kit.code.model import CodeModule, CodeRelationship
    from okf_kit.code.render import render_concept

    dependencies = tuple(
        CodeRelationship(label=f"dep{idx}", target_cid=f"code/dep{idx}")
        for idx in range(12)
    )
    dependents = tuple(
        CodeRelationship(label=f"caller{idx}", target_cid=f"code/caller{idx}", kind="used_by")
        for idx in range(13)
    )
    module = CodeModule(
        source_path="src/service.py",
        language="python",
        source_hash="hash",
        imports=(),
        symbols=(),
        relationships=dependencies + dependents,
    )

    text = render_concept(module)

    assert "2 dependencies omitted from compact profile." in text
    assert "3 dependents omitted from compact profile." in text


def test_index_codebase_generates_repository_and_area_summaries(tmp_path: Path):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import index_codebase

    repo = tmp_path / "repo"
    (repo / "src" / "api").mkdir(parents=True)
    (repo / "src" / "worker").mkdir(parents=True)
    (repo / "src" / "api" / "service.py").write_text(
        "from src.worker.jobs import WorkerJob\n\nclass ApiService:\n    pass\n",
        encoding="utf-8",
    )
    (repo / "src" / "worker" / "jobs.py").write_text(
        "class WorkerJob:\n    pass\n",
        encoding="utf-8",
    )
    bundle = tmp_path / "kb"

    index_codebase(repo, bundle, languages=["python"])

    repo_summary = bundle / "code-summaries" / "repository.md"
    area_summary = bundle / "code-summaries" / "areas" / "src.md"
    assert repo_summary.is_file()
    assert area_summary.is_file()
    repo_text = repo_summary.read_text(encoding="utf-8")
    area_text = area_summary.read_text(encoding="utf-8")
    assert "type: CodeSummary" in repo_text
    assert "summary_level: repository" in repo_text
    assert "[src/api/service.py](/code/src/api/service.py.md)" in repo_text
    assert "Impact map" in repo_text
    assert "depends on 1; used by 0" in repo_text
    assert "src.worker.jobs" in repo_text
    assert "used by 1" in repo_text
    assert "summary_level: area" in area_text
    assert "[src/worker/jobs.py](/code/src/worker/jobs.py.md)" in area_text
    context = read_concept(bundle, "code-summaries/areas/src", depth=1, token_budget=4000)
    assert "# code/src/api/service.py (depth 1)" in context


def test_index_codebase_generates_package_summaries_for_nested_packages(tmp_path: Path):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import index_codebase

    repo = tmp_path / "repo"
    package = repo / "services" / "billing"
    (package / "src").mkdir(parents=True)
    (package / "pyproject.toml").write_text("[project]\nname = \"billing\"\n", encoding="utf-8")
    (package / "src" / "service.py").write_text(
        "class BillingService:\n    pass\n",
        encoding="utf-8",
    )
    bundle = tmp_path / "kb"

    index_codebase(repo, bundle, languages=["python"])

    summary = bundle / "code-summaries" / "packages" / "services" / "billing.md"
    assert summary.is_file()
    text = summary.read_text(encoding="utf-8")
    assert "summary_level: package" in text
    assert "package: services/billing" in text
    assert "[services/billing/src/service.py](/code/services/billing/src/service.py.md)" in text


def test_summary_concept_ids_are_sanitized_and_addressable(tmp_path: Path):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import index_codebase

    workspace = tmp_path / "workspace"
    repo = workspace / "my repo"
    package = repo / "pkg space"
    (repo / ".git").mkdir(parents=True)
    (package / "src area").mkdir(parents=True)
    (package / "pyproject.toml").write_text("[project]\nname = \"pkg-space\"\n", encoding="utf-8")
    (package / "src area" / "service.py").write_text(
        "class SpaceService:\n    pass\n",
        encoding="utf-8",
    )
    bundle = tmp_path / "kb"

    index_codebase(workspace, bundle, languages=["python"])

    assert (bundle / "code-summaries" / "repos" / "my-repo.md").is_file()
    assert (
        bundle / "code-summaries" / "repos" / "my-repo" / "areas" / "pkg-space.md"
    ).is_file()
    assert (
        bundle / "code-summaries" / "repos" / "my-repo" / "packages" / "pkg-space.md"
    ).is_file()
    context = read_concept(bundle, "code-summaries/repos/my-repo/packages/pkg-space", depth=0)
    assert "SpaceService" in context


def test_index_codebase_prunes_stale_generated_concepts_when_scope_narrows(tmp_path: Path):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import index_codebase

    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True)
    (repo / "static").mkdir()
    (repo / "src" / "service.py").write_text("class Service:\n    pass\n", encoding="utf-8")
    (repo / "static" / "app.py").write_text("class StaticAsset:\n    pass\n", encoding="utf-8")
    bundle = tmp_path / "kb"

    index_codebase(repo, bundle, languages=["python"], include=["static/app.py"])
    assert (bundle / "code" / "static" / "app.py.md").is_file()
    assert (bundle / "code-summaries" / "areas" / "static.md").is_file()

    index_codebase(repo, bundle, languages=["python"])

    assert not (bundle / "code" / "static" / "app.py.md").exists()
    assert not (bundle / "code-summaries" / "areas" / "static.md").exists()
    assert (bundle / "code" / "src" / "service.py.md").is_file()


def test_nested_package_absolute_imports_link_within_package(tmp_path: Path):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import index_codebase

    repo = tmp_path / "repo"
    package = repo / "services" / "billing"
    source = package / "src" / "billing"
    source.mkdir(parents=True)
    (package / "pyproject.toml").write_text("[project]\nname = \"billing\"\n", encoding="utf-8")
    (source / "models.py").write_text("class Invoice:\n    pass\n", encoding="utf-8")
    (source / "service.py").write_text(
        "import billing.models\n\nclass BillingService:\n    pass\n",
        encoding="utf-8",
    )
    bundle = tmp_path / "kb"

    index_codebase(repo, bundle, languages=["python"])

    service = (
        bundle / "code" / "services" / "billing" / "src" / "billing" / "service.py.md"
    ).read_text(encoding="utf-8")
    assert (
        "[billing.models](/code/services/billing/src/billing/models.py.md)"
    ) in service
    context = read_concept(
        bundle,
        "code/services/billing/src/billing/service.py",
        depth=1,
    )
    assert "# code/services/billing/src/billing/models.py (depth 1)" in context


def test_generated_code_search_ranks_path_symbol_repo_language_and_dependency_queries(
    tmp_path: Path,
):
    _require_tree_sitter_extra()
    from okf_kit.code.indexer import index_codebase

    workspace = tmp_path / "workspace"
    repo = workspace / "billing repo"
    package = repo / "services" / "billing"
    source = package / "src" / "billing"
    (repo / ".git").mkdir(parents=True)
    source.mkdir(parents=True)
    (package / "pyproject.toml").write_text("[project]\nname = \"billing\"\n", encoding="utf-8")
    (source / "models.py").write_text("class Invoice:\n    pass\n", encoding="utf-8")
    (source / "service.py").write_text(
        "import billing.models\n\nclass BillingService:\n    pass\n",
        encoding="utf-8",
    )
    bundle = tmp_path / "kb"
    bundle.mkdir()
    (bundle / "note.md").write_text(
        "---\ntype: Note\ntitle: Billing Python Models\ndescription: python billing models\n---\n"
        "BillingService billing.models services/billing/src/billing/service.py python\n",
        encoding="utf-8",
    )

    index_codebase(workspace, bundle, languages=["python"])
    index = build_index(bundle)

    assert search(index, "services/billing/src/billing/service.py")[0].cid == (
        "code/billing-repo/services/billing/src/billing/service.py"
    )
    assert search(index, "BillingService")[0].cid == (
        "code/billing-repo/services/billing/src/billing/service.py"
    )
    assert search(index, "billing repo")[0].cid.startswith("code-summaries/repos/billing-repo")
    assert search(index, "python", type=["CodeModule"])[0].cid.startswith("code/billing-repo/")
    assert search(index, "depends-on billing.models")[0].cid == (
        "code/billing-repo/services/billing/src/billing/service.py"
    )
