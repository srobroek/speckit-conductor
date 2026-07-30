# speckit-conductor

The beads-native SpecKit workflow: the `speckit-feature` formula whose poured
molecule *is* the phase DAG, human approval gates as real DAG nodes, four SpecKit
agents, the setup and bugfix skills, and a guard that keeps task state in beads
rather than `tasks.md`.

Extracted from [`srobroek/agentic-packages`](https://github.com/srobroek/agentic-packages),
where it lived as three packages (`speckit`, `speckit-beads`, `steering-speckit`)
before they were merged into one.

## Install

```bash
apm install srobroek/speckit-conductor --target claude,codex
```

Or as a dependency:

```yaml
dependencies:
  apm:
    - git: srobroek/speckit-conductor
      ref: '>=3.0.0 <4.0.0'
      targets: [claude, codex]
```

Then, before pouring anything:

```bash
# Installs spec-kit, its extensions, and the formula into .beads/formulas/
```

Invoke the `speckit-setup` skill ("set up SpecKit"). **This is a precondition, not a
convenience.** 14 of the formula's 26 steps invoke a `/speckit.*` skill, and those
come from spec-kit and its community extensions rather than from this package. The
mandatory implementation path (`assign` -> `validate` -> `execute`) is the
`agent-assign` extension. Pour without running setup and you get 30 beads whose steps
name skills that do not exist.

Requires the `bd` CLI (`gastownhall/beads` >= 1.1.0) and `python3` on `PATH`. The
guard and the steering are inert in a repository without `.beads/`, so installing
it costs nothing until beads is initialised.

**APM install only.** Do not install this as a native plugin. `apm pack` synthesises
a `plugin.json` with no `dependencies` field, and a Codex plugin manifest has no such
field at all, so a native `/plugin` install resolves the skills and hooks here and
silently none of the dependencies below. The steering would then describe a `bd`
workflow with no `bd` package behind it. APM composes the full graph; verified on both
runtimes in a fresh repository, where `apm install --target claude,codex` pulls three
packages and wires two agents and four skills on each.

## What arrives

| Piece | Does |
|---|---|
| `formulas/speckit-feature.formula.toml` | 26 steps, 3 human gates; the poured molecule is the phase DAG |
| `scripts/speckit-tasks-guard.py` | denies a write to `specs/*/tasks.md` in a beads repo, through Write, Edit, `apply_patch`, or a shell redirect; reads stay allowed for migration |
| `scripts/speckit-pr-title.py` | derives a PR title from the spec |
| `speckit-sync` agent | audits artifacts in two scopes: `drift` (spec versus code) and `conflicts` (spec versus spec) |
| `speckit-verify` agent | audits in two modes: `tasks` (phantom completion) and `requirements` (code against `spec.md`) |
| `speckit-setup` skill | installs spec-kit, its extensions, and the formula into `.beads/formulas/` |
| `speckit-bugfix` skill | the bugfix route |
| steering | one spec dir to one molecule root, the routing table, and why `tasks.md` is never authored |

## Dependencies

Two, both resolved from published tags in the monorepo:

- `beads` — the workflow engine
- `adr-as-beads` — architecture decisions as `decision` beads, rendered to `docs/adr/`

They are referenced rather than vendored. A copy across a repository boundary has
no checker behind it, and a drifted guard script is not recoverable the way a
drifted generated file is.

## Human gates, and running without one

Three steps carry a human approval gate: `clarify-approval`, `analyze-approval`, and
`verify-signoff`. An interactive run resolves each with `bd gate resolve <gate-id>`.

An unattended run cannot. `bd gate check` does not see a human gate at all -- it
reports `Checked 0 gates` -- so a molecule poured with gates and left to an agent
stalls at `clarify-approval` with `bd ready` empty, eight steps before `implement`.

Pour with `--var autonomous=yes` when the operator has said the run may proceed
unattended:

```bash
bd mol pour speckit-feature --var feature=001-slug --var autonomous=yes
```

That filters the three gate steps out: 24 steps instead of 30, and the DAG runs to
completion. Sequencing is preserved, because each step that followed a gate also names
the gate's own predecessor.

**Skipping a gate is not skipping its judgement.** Record on the preceding step's bead
what a reviewer would have been asked and why the run proceeded, before closing it. A
run that leaves no note where a gate stood has discarded the gate rather than
satisfied it.

## Task state

`specs/*/tasks.md` is read-only legacy. Implementation tasks are children of the
molecule's implement step:

```bash
bd create "T00N <title>" --parent <implement-step-id> --spec-id <NNN-slug>
```

Reads of an existing `tasks.md` stay allowed, so a brownfield repository can
migrate.

## Diagnosing a formula

Use `bd cook <name>`. `bd mol pour` reports every formula error as `not found as
formula or proto ID` while naming a file that exists, so a broken formula is
indistinguishable from a missing one.

Every step's `needs` must name at least one unconditional step. A step whose whole
`needs` list is filtered keeps only its parent edge and becomes immediately ready,
with no error at pour.

`optional = true` is inert; `condition` is the working key, and it reads pour-time
variables rather than filesystem state.

## Roadmap

[`docs/BUILD-PLAN.md`](docs/BUILD-PLAN.md) specifies the work still to come: three
standalone profiles (`minimal`, `lean`, `full`) replacing the single 26-step
formula, bonded loop formulas for the review and iterate cycles, a standalone
`bugfix-spec` formula, and the authoring docs for adding an extension or a formula.

## The name

A sibling package, `orchestrate`, coordinates parallel subagents through beads
DAGs. This one sequences phases for a single feature. A conductor keeps time
through a score, which is what phase sequencing is.
