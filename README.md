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

Then, before pouring anything, invoke the `speckit-setup` skill ("set up SpecKit"). It
installs spec-kit, its extensions, and all seven formulas into `.beads/formulas/`.

**This is a precondition, not a convenience.** 14 of `speckit-feature`'s 26 steps invoke
a `/speckit.*` skill, and those come from spec-kit and its community extensions rather
than from this package. Its implementation path (`assign` -> `validate` -> `execute`) is
the `agent-assign` extension. Pour without running setup and you get 30 beads whose
steps name skills that do not exist.

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
| three depth profiles under `formulas/` | `speckit-basic` (10 steps), `speckit-lean` (18), `speckit-feature` (26); the poured molecule is the phase DAG |
| four sub-process formulas under `formulas/` | `mol-speckit-iterate`, `mol-speckit-fix-findings`, `mol-speckit-bugfix`, `mol-speckit-refine`; bonded onto a running molecule |
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

Every profile carries the same three human approval gates: `clarify-approval`,
`analyze-approval`, and `verify-signoff`. An interactive run resolves each with
`bd gate resolve <gate-id>`.

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

### Granting autonomy mid-run

The flag is read at pour, so it fixes one molecule's shape. To grant autonomy to a run
already in flight, resolve the remaining gates directly:

```bash
bd gate resolve <gate-id> --reason "<what a reviewer would have been asked>" --actor "<who granted it>"
bd close <step-id> --reason "autonomous: findings recorded on the gate"
```

No re-pour, and the `--reason` and `--actor` are a better audit trail than the
pour-time flag can leave, because they attach to the specific gate that was waived.

## Without the agent-assign extension

`assign`, `validate`, and `implement` are all `/speckit.agent-assign.*` commands. If
that extension is not installed, pour with `--var agent_assign=no` and those three
steps drop out.

That does not provide another way to implement — it removes the steps that would have
named a skill that does not exist, so the molecule reflects what can actually run.
Work the task beads under the implement step directly. `verify-tasks` anchors on
`analyze`, so the verification half of the DAG survives either way.

`speckit-basic` has no such chain. Its `implement` step works the task beads under it
directly, on every pour, so `agent_assign` conditions no step there.

## Depth profiles

`speckit-feature` is the default. Each profile is a standalone formula taking `feature`,
`autonomous`, and `agent_assign` with the same defaults, so the four var combinations
work on every one.

| Profile | Steps | Phases |
|---|---|---|
| `speckit-basic` | 10 | specify, clarify, plan, tasks, analyze, implement, plus the three gates |
| `speckit-lean` | 18 | basic plus critique, the agent-assign chain, verify-tasks, verify, review, qa, docs-update |
| `speckit-feature` | 26 | lean plus checklist, security-review, code-review, security-review-post, cleanup, sync-drift, sync-conflicts, retro |

```bash
bd mol pour speckit-lean --var feature=001-slug --var autonomous=yes
```

Beads poured, counting the gate bead each surviving gate step adds:

| Profile | `autonomous`=`no`, `agent_assign`=`yes` | `no`, `no` | `yes`, `yes` | `yes`, `no` |
|---|---|---|---|---|
| `speckit-feature` | 30 | 27 | 24 | 21 |
| `speckit-lean` | 22 | 19 | 16 | 13 |
| `speckit-basic` | 14 | 14 | 8 | 8 |

Every `/speckit.*` command in `speckit-basic` ships with spec-kit itself, so that
profile needs no community extension. `speckit-lean` needs `critique`, `agent-assign`,
`review`, and `qa`. `speckit-feature` needs those plus `cleanup`, `retro`, and
`security-review`.

## Sub-process formulas

These formulas run against a molecule already in flight. Bond one onto the step that
found the work:

```bash
bd mol bond mol-speckit-fix-findings <step-id> --var feature=001-slug
```

| Formula | Steps | Requires extension | For |
|---|---|---|---|
| `mol-speckit-iterate` | 2 | `iterate` | the approved approach changed |
| `mol-speckit-fix-findings` | 2 | `fix-findings` | review, QA, or security found actionable defects |
| `mol-speckit-bugfix` | 3 | `bugfix` | a defect in implemented code, traced to its spec artifacts |
| `mol-speckit-refine` | 4 | `refine` | spec.md text changed and plan and tasks must follow |

The bond target sets when the sub-molecule can run:

| Target | Edge onto the target | First step becomes ready |
|---|---|---|
| the feature root | `blocks` | after the whole feature closes |
| a step | `parent-child` | as soon as that step is ready |

Keep the `mol-` filename prefix. `bd` resolves a formula by filename stem, and
`bd mol bond` resolves a formula name only when it is prefixed:
`bd mol bond speckit-iterate <id>` reports `not found (not an issue ID or formula
name)`.

Neither loop is expressed as `needs` edges, because a cycle is rejected at pour with
`adding dependency would create a cycle`. `mol-speckit-bugfix`'s verify step sends work
back by reopening the patch bead (`bd update <id> --status open`).
`mol-speckit-fix-findings` relies on the extension's own 5-iteration cap; bond a second
copy for a second pass.

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

## The name

A sibling package, `orchestrate`, coordinates parallel subagents through beads
DAGs. This one sequences phases for a single feature. A conductor keeps time
through a score, which is what phase sequencing is.
