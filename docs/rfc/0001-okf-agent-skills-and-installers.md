# RFC-0001: OKF agent skills and installers

- **Status:** Accepted
- **Author:** okf maintainers
- **Approver:** user
- **Date opened:** 2026-06-17
- **Date closed:** 2026-06-17
- **Related:** AGENTS.md; README.md; wiki/guides/authoring.md; wiki/reference/tools.md

## The ask

**Recommendation (BLUF):** approve a first-class OKF skill pack made of focused
skills and an explicit CLI installer:
`okf agent install claude-code|codex --scope project|user --update`. Do not
overload `okf init`; keep it reserved for bundle initialization. Subagents,
hooks, and full pack packaging stay deferred until a later spec approves their
exact contents.

**Why now:** OKF's v0.1 product surface is already agent-native: the core is
exposed through the `okf` CLI and `okf-mcp`, and the README promises an
`okf-author` skill. The current packaged skill is creation-oriented and stale
on link semantics, while the repo already dogfoods both Claude Code and Codex
agent artifacts. The question is whether OKF should treat those artifacts as
installable product assets or leave users to copy them by hand.

**Decisions requested:**

1. Approve the v0.1 skill set: `okf-search` plus an upgraded `okf-author` that
   supports updates as well as creation. Decide by RFC acceptance; default yes.
2. Approve `okf agent install <target>` as the installer namespace instead of
   `okf init <target>`. Decide by RFC acceptance; default yes.
3. Approve package-data work so installed wheels contain the agent assets the
   CLI copies. Decide by RFC acceptance; default yes.
4. Approve shared canonical skill assets with target-specific projections for
   Claude Code and Codex. Decide by RFC acceptance; default yes.

## Problem & goals

OKF is meant to be used by agents, not only by humans running CLI commands.
The format's load-bearing behavior is progressive context: search cheaply, read
one concept, then expand to linked neighbors only as needed. A generic coding
agent can do this if prompted carefully, but the behavior is important enough
to package as reusable skills.

The current project has four gaps:

- The committed `okf-author` skill covers the scaffold-author-link-validate-index
  loop, but it does not explicitly cover updating existing concepts.
- The same skill is stale: it says absolute links are not graph edges, while
  the current code, tests, and wiki say absolute bundle-relative links are
  supported and recommended.
- The public README promises `okf-author`, but the wheel built by `uv build`
  does not contain `okf-kit/skills/okf-author/SKILL.md`; an installed CLI cannot
  reliably copy that skill today.
- The repo contains Claude Code and Codex artifacts, but there is no product
  command that installs or updates OKF-owned skill artifacts for a user.

**Goals:**

- Make common OKF agent workflows discoverable and repeatable.
- Keep skills aligned with the canonical CLI/MCP/tool docs.
- Let an installed `okf` CLI install or update agent assets without requiring a
  source checkout.
- Support both Claude Code and Codex while respecting each tool's native
  directory conventions.
- Keep the OKF core pure; agent installation is CLI/package behavior, not core
  parsing/search/validation logic.

**Non-goals:**

- Do not build the full v0.2 Claude Code pack in this RFC.
- Do not approve concrete subagent or hook contents in this RFC.
- Do not add REST, GraphQL, or a hosted service.
- Do not add a second context-loading primitive beyond `read_concept(depth=N)`.
- Do not make agent install mutate a knowledge bundle.
- Do not solve marketplace/plugin publishing in the first implementation.

## Proposal

Add an agent-assets layer to the package and install skill assets through a new CLI
namespace:

```bash
okf agent install claude-code --scope project --update
okf agent install codex --scope project --update
okf agent install codex --scope user --dry-run
```

`okf init <dir>` remains only bundle initialization. This avoids the ambiguous
case where `okf init claude-code` could mean either "create a bundle named
claude-code" or "configure Claude Code".

The first shipped skills should be:

- `okf-search`: a read-only workflow for using `okf search`, `okf read`, and
  `okf-mcp` progressive context. It should push agents to start with cheap hit
  lists, read `depth=0`, and expand only when neighboring context matters.
- `okf-author`: the existing authoring skill, corrected and expanded. It should
  cover both creating and updating concepts: search/read nearby context, edit
  Markdown directly or create a stub with `okf new`, prefer absolute
  bundle-relative links, validate, and regenerate indexes.

The second wave may add:

- `okf-maintain` or `okf-curator`: bundle hygiene, stale pages, broken-link
  triage, index regeneration, and conformance cleanup.
- `okf-import` or `okf-producer`: turning external source material into OKF
  concepts. This should wait until producer/import scope is real.
- Target-specific reviewer agents for conformance, link quality, and security
  boundaries. These are useful but should not block the first installer.

Package the canonical assets inside the installed wheel, for example under
`okf_kit/agent_assets/`. The implementation should include package-data tests
that build a wheel and assert the skill files are present. Source-only layout is
not sufficient.

Projection rules:

- Claude Code project scope writes `.claude/skills`.
- Codex project scope writes `.codex/skills`.
- User scope writes the corresponding user-level directories.
- `--dry-run` prints planned writes.
- `--update` replaces files owned by OKF when their generated marker or manifest
  matches; it refuses to overwrite unmanaged local files unless a future
  `--force` is added.
- The installer writes a small manifest recording target, installed asset
  versions, and ownership markers so later updates are deterministic.

The installer namespace may later grow `--component agents` or
`--component hooks`, but this RFC approves only skill installation. Adding
subagents, hooks, MCP config, or plugin bundles requires a follow-on spec that
names the files, trust behavior, and verification gates.

The CLI should stay a thin presentation layer over small installation helpers.
Those helpers may live outside `okf_kit.core` because installation mutates
editor/agent configuration and is not part of the pure OKF data model.

## Options considered

### Decision 1: skill set

The option space is MECE along how much reusable workflow OKF ships now.

| Option | Prior art | Trade-offs |
|---|---|---|
| Do nothing | Existing README and `okf-author` mention manual use. | Lowest cost, but users keep hand-prompting and the stale link guidance remains product debt. |
| Keep only `okf-author` | Current v0.1 scope names `okf-author`. | Preserves the approved v0.1 shape, but mixes discovery and authoring and leaves read-only progressive context under-specified. |
| Ship `okf-search` + upgraded `okf-author` | OKF progressive context is explicitly `search` -> `read_concept(depth=0)` -> `read_concept(depth=N)`; Codex and Claude Code skills both favor focused progressive-disclosure workflows. | Recommended first slice: small, directly tied to v0.1 behavior, and easy to test. |
| Ship the full pack now | Codex and Claude Code plugins can bundle skills, agents, hooks, and MCP config. | Too broad for this RFC and conflicts with the repo's v0.2 deferral for the full pack. |

### Decision 2: installer namespace

The option space is MECE along whether agent setup is a bundle operation, an
agent-environment operation, or an external plugin operation.

| Option | Prior art | Trade-offs |
|---|---|---|
| Do nothing / docs only | README currently gives manual MCP setup. | No new CLI surface, but no reliable skill installation path. |
| `okf init claude-code` | `okf init <dir>` already initializes a bundle. | Short, but ambiguous with creating a bundle named `claude-code`. |
| `okf agent install claude-code|codex` | Codex and Claude Code both treat skills/plugins as agent-environment assets, not knowledge-bundle files. | Recommended: explicit, leaves room for `list`, `doctor`, `update`, and `uninstall`. |
| Plugin-only install | Native for Codex/Claude plugin ecosystems. | Good later distribution channel, but does not give the OKF CLI a universal setup path. |

### Decision 3: distribution source

The option space is MECE along where installable assets come from.

| Option | Prior art | Trade-offs |
|---|---|---|
| Do nothing / source checkout only | The sdist contains `okf-kit/skills/okf-author/SKILL.md`. | Works for contributors, but not for normal wheel-installed users. |
| Package assets in the wheel | Python package data is the normal way an installed CLI carries non-code assets. | Recommended: works after install and is testable; requires package-data changes. |
| External plugin repository only | Codex and Claude Code plugins are native distribution units for bundles of skills and integrations. | Useful later, but creates a second release channel before the CLI path works. |

### Decision 4: target projection

The option space is MECE along which agent environments receive projected skill
assets.

| Option | Prior art | Trade-offs |
|---|---|---|
| Do nothing / no projection | Users can manually copy skills. | Avoids compatibility work, but leaves setup undocumented and inconsistent. |
| Claude Code only | AGENTS.md names a future Claude Code pack. | Matches the original deferred pack direction, but ignores Codex users and the repo's existing Codex artifacts. |
| Codex only | Codex docs define repo/user skill locations and plugin distribution. | Aligns with this coding environment, but does not serve Claude Code users. |
| Shared canonical skills with target-specific projection | Agent Skills is a cross-tool skill format; both Codex and Claude Code consume `SKILL.md` directories. | Recommended: one source of truth for workflow text, with small per-target path rules. |

## Risks & what would make this wrong

**Pre-mortem:** this ships and fails because the installer overwrites user
customizations, writes to the wrong Codex skill directory, or packages stale
skill text. Mitigations: require ownership markers, add `--dry-run`, refuse
unmanaged overwrites, test target paths, and keep skill docs synced against OKF
tool docs.

**Key assumptions:**

- Users benefit from separate read-only and authoring skills. This is false if
  most OKF usage is one-shot creation and no one asks agents to browse bundles.
- Codex and Claude Code skill layouts remain stable enough for projection. This
  is false if either tool replaces local skills/plugins with a different install
  contract before implementation.
- Package-data installation is acceptable. This is false if the project chooses
  plugin publishing as the only supported distribution path.
- Agent installation belongs in the CLI presentation layer, outside the pure
  core. This is false if the project wants `okf_kit.core` to model all
  filesystem writes, including non-bundle config writes.

**Drawbacks:**

- The CLI grows beyond bundle operations into agent-environment setup.
- Supporting both Claude Code and Codex skills adds compatibility work and docs
  burden.
- Ownership markers are another small state file to maintain.
- The installer namespace is likely to grow later when agents, hooks, MCP config,
  and plugin packaging are approved.

## Evidence & prior art

**Spike / de-risk result:** `uv build` succeeded on 2026-06-17, but inspecting
`dist/okf_kit-0.1.0-py3-none-any.whl` showed no `skills/okf-author/SKILL.md`.
The sdist contains `okf-kit/skills/okf-author/SKILL.md`; the wheel does not.
Therefore, a wheel-installed CLI cannot currently copy bundled skills.

**Repo precedent:**

- `AGENTS.md` says v0.1 ships Python core + CLI + MCP + `okf-author`, while
  full skills/subagents/hooks pack work is deferred.
- `README.md` publicly describes OKF as agent-native tooling and names
  `okf-author`.
- `wiki/architecture/progressive-context.md` defines the read workflow:
  `search` -> `read_concept(depth=0)` -> `read_concept(depth=N)`.
- `wiki/format/links.md`, `okf-kit/okf_kit/core/links.py`, and
  `okf-kit/tests/test_links.py` confirm absolute bundle-relative links are
  graph edges and are the recommended form.
- `.claude/*` and `.codex/*` already exist in this repo, so both ecosystems are
  already part of project operations. This RFC only approves installing OKF
  skills into those ecosystems.

**External prior art:**

- Codex skills are progressive-disclosure directories with `SKILL.md`; Codex
  scans repo/user/admin/system skill locations and recommends plugins for
  reusable distribution:
  https://developers.openai.com/codex/skills.md
- Codex plugins can bundle skills, MCP config, app integrations, and lifecycle
  hooks:
  https://developers.openai.com/codex/plugins/build.md
- Codex custom agents live in `.codex/agents` or `~/.codex/agents`:
  https://developers.openai.com/codex/subagents.md
- Codex hooks are discovered from `hooks.json` or inline config and may also be
  bundled by plugins:
  https://developers.openai.com/codex/hooks.md
- Claude Code skills, subagents, and plugins provide the comparable target
  surfaces for `.claude` projection:
  https://code.claude.com/docs/en/skills,
  https://code.claude.com/docs/en/sub-agents,
  https://code.claude.com/docs/en/plugins
- The Agent Skills specification defines the cross-tool skill shape:
  https://agentskills.io/specification

## Open questions

- **Exact ownership manifest path:** use `.okf-agent-assets.json` at the target
  root or per-target manifests under `.claude` / `.codex`? Recommended default:
  per-target manifests to keep local tool state local; owner: implementer;
  decide-by: implementation spec.
- **User-scope install paths:** confirm final user-level Claude Code and Codex
  paths against the current tool docs before implementation. Recommended
  default: follow each tool's documented user locations at implementation time;
  owner: implementer; decide-by: implementation spec.

## Follow-on artifacts

- Spec: `docs/specs/okf-agent-installer/`
- Skill updates: `okf-search`; upgraded `okf-author`
- Tests: package-data wheel test; installer dry-run/update tests; skill
  frontmatter/trigger tests; CLI `--help` coverage for `okf agent install`
- Docs: README install section; `wiki/interfaces/okf-cli.md`;
  `wiki/reference/tools.md`; `wiki/guides/authoring.md`
