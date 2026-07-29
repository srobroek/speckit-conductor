# Brief: merge the SpecKit packages, then extract them as `speckit-conductor`

Repository: `~/personal/dev/agentic-packages` (live repo, do not clone). Take a
Worktrunk lease: `wt switch --create feat/speckit-conductor --base main --no-cd --format=json`.

Source of truth is `packages/*/.apm/`. `packages/*/.claude/` and
`packages/*/{agents,hooks}/` are generated build output -- never edit them
(`git check-ignore -v` if unsure). After changing any `apm.yml`, regenerate all three
artifact families or `check-artifacts` fails in CI:

```
python3 .apm/scripts/build-native-plugins.py && python3 .apm/scripts/render-docs.py all && apm run build-marketplace
```

That third command is easy to miss -- it is `apm pack && build-marketplace-block.py`,
and skipping it leaves `.claude-plugin/marketplace.json` stale.

Read first, in order: root `AGENTS.md`; `.specify/memory/constitution.md`;
`packages/beads/.apm/skills/build-formula/SKILL.md` and its
`references/{conditions,composition,gates,verify}.md`; then
`packages/speckit/.apm/skills/speckit-setup/scripts/setup-speckit.sh` (432 lines) and
`packages/speckit-beads/scripts/speckit-beads-tasks-guard.py`.

## Verified facts

Measured on this machine 2026-07-29. Re-verify anything you rely on; several
"confirmed" findings in this area turned out latent or unreproducible on inspection.

| Fact | Value |
|---|---|
| `bd` | 1.1.2 |
| `specify-cli` | 0.13.4 |
| Community catalog entries | **143** (was 142 earlier the same day -- it grows) |
| Extensions the setup script hardcodes | **12** |
| Extensions actually installed | **19** |
| `speckit-feature` formula | 26 steps, **3** human gates (not 6), 1 var |
| Formulas that exist in any beads store | **none** (`bd formula list` empty) |
| Skills that write `specs/*/tasks.md` | **7** |
| Orphaned `workflow.yml` files | 3 |
| `steering-speckit` size | 49 lines, ~20 restating the formula |

Package versions: `speckit` 11.0.0, `speckit-beads` 8.0.0, `steering-speckit` 3.3.2.

## Change 1: merge into one package

DECIDED: everything merges into `speckit`; `speckit-beads` and `steering-speckit` are
tombstoned. `speckit` keeps the name because it holds the version history worth keeping.

Everything moves, including runtime artifacts: 4 agents, both skills
(`speckit-setup`, `speckit-bugfix`), the formula, the tasks guard **and its
`tests/` directory** (`check-hook-contract` requires every hook script to ship tests,
and `speckit` ships no Python today), all four hook manifests, and the surviving
steering.

Dependency edges are shallow: only `speckit-beads` -> `speckit` internally, with the
root `apm.yml` listing all three. Count the external `apm.yml` files that pin the two
tombstoned names -- do not trust a number, count them -- and produce a migration note
per file rather than editing repositories you have no lease on. The merge must not land
until dependents are updated: a removed package fails `apm install` at resolution, the
same failure mode that ordered the `mcp-repomix` removal behind five dependent PRs.

Release-please tracks each package independently, so tombstoning two names is a
breaking change for three packages at once. State how tombstones are expressed
(deleted outright, or a deprecated stub that redirects) and why.

DEDUPLICATE THIS, which is why the merge exists: `speckit-beads` already uses
`--spec-id` at two places for the molecule root and task beads, and
`steering-speckit`'s DECISIONS block now requires it too, with no cross-reference.
One convention, two files, already drifting. After the merge there must be exactly one
statement of it.

## Change 2: drop what is already dead

**The three `workflow.yml` files** under
`packages/speckit/.apm/skills/speckit-setup/scripts/workflows/`. The package ships them
AND deletes them on install: `setup-speckit.sh:160` lists
`LEGACY_WORKFLOWS=(speckit speckit-quality speckit-full)` for removal, and the SKILL.md
already claims the package no longer ships them. All 8 `speckit-quality` phases exist
as formula steps; `speckit-full` is the `speckit` cycle plus those gates. Delete all
three, keep the `LEGACY_WORKFLOWS` cleanup so upgrades still tidy up.

**The duplicated steering.** `steering-speckit`'s PHASE ORDER table and GATES section
restate the formula's own DAG and its gates. The formula is executable and the prose is
not, so they drift silently.

KEEP:
- The DECISIONS routing table (converge / iterate / bugfix / fix-findings / tinyspec).
  That is judgement, not a DAG.
- The DECISIONS phase table with its `--spec-id` and cite-before-close MUSTs. ADRs are
  now beads `decision` beads rendered to `docs/adr/` by a pre-commit hook;
  `packages/adr` owns the format, the `bd lint` gate, and `bd supersede`. The steering
  owns only WHICH phases produce a record. **Do not reintroduce the `adrs` binary.**
- `MUST Invoke SpecKit commands through their runtime-native skill interface`.
- Carry the `packages/adr#>=1.0.0 <2.0.0` dependency to the merged package.

TASK STATE: `speckit-beads-tasks-guard.py` DENIES every write to `specs/*/tasks.md`, so
"never author tasks.md" is enforced -- drop that prose. "Query task state by spec ID"
and "keep the implement parent open until every child is closed" are NOT hooked. The
second one now has two independent routes depending on it (converge and fix-findings
both add work after implement looked done), so make it enforceable or say why not.

## Change 3: three standalone formulas, no composition

Replace the single 26-step formula with three profiles. **Standalone, not composed.**

WHY NOT COMPOSITION, verified today: a child that redeclares a step to rewire its joins
**silently drops the parent's `[steps.gate]`**. Reproduced -- parent showed
`approval | gate: {'type': 'manual'}`, child showed `approval | gate: NONE`, no error.
This formula has 3 human approval gates sitting mid-chain exactly where a lean profile
must rewire, so composition risks silently deleting a human approval. Standalone also
removes the anchor-rule hazard entirely: nothing is conditional, so no `needs` entry can
be filtered out.

Cost: ~26 duplicated TOML blocks. Add a test asserting the three share identical step
definitions wherever they overlap.

Parallelism is expressed only through `needs`: two steps naming the same predecessor have
no edge between them, so both go ready at once, and the joining step names both.

### `minimal` -- 10 steps

| Stage | Steps |
|---|---|
| Specify | `specify` -> `clarify` -> GATE `clarify-approval` |
| Plan | `plan` -> `tasks` |
| Analyze | `analyze` -> GATE `analyze-approval` |
| Build | `implement` |
| Verify | GATE `verify-signoff` |
| Close | `final-checkpoint` |

Spec-kit core only, no extension required, fully linear. Note `clarify` is mandatory
here although spec-kit lists it as optional -- a deliberate divergence, say so in the
steering so it does not read as an accident.

### `lean` -- 18 steps

| Stage | Steps |
|---|---|
| Specify | `specify` -> `clarify` -> GATE `clarify-approval` |
| Plan | `plan` -> `tasks` -> `critique` |
| Analyze | `analyze` -> GATE `analyze-approval` |
| Assign | `assign` -> `validate` |
| Build | `roadmap-brief` -> `implement` |
| Verify | `verify-tasks` -> `verify` -> GATE `verify-signoff` |
| Review | `review` -> `qa` |
| Close | `docs-update` -> `roadmap-debrief` -> `final-checkpoint` |

`lean` is a subset in intent but a REWRITE in joins. `cleanup` needs
`[code-review, security-review-post]` and `retro` needs
`[sync-drift, sync-conflicts]` -- `lean` has none of those four, so its joins must be
re-anchored (`retro` on `qa`). Write them out; do not copy.

### `full` -- 31 steps

| Stage | Steps |
|---|---|
| Specify | `specify` -> `clarify` -> GATE `clarify-approval` |
| Plan | `plan` -> `tasks` -> `checklist` |
| Quality | `critique`, `security-review` (parallel, both on `checklist`) |
| Analyze | `analyze` -> GATE `analyze-approval` |
| Assign | `assign` -> `validate` |
| Build | `roadmap-brief` -> `implement` |
| Verify | `verify-tasks` -> `verify` -> GATE `verify-signoff` |
| Review | `review` -> `qa` -> `code-review`, `security-review-post` (parallel on `qa`) |
| Sync | `cleanup` -> `sync-drift`, `sync-conflicts` (parallel on `cleanup`) |
| Close | `retro` -> `docs-update` -> `roadmap-debrief` -> `archive` -> `final-checkpoint` |

### Formula authoring traps, each verified today

1. **Override drops gates and `condition` silently.** See above.
2. **`optional = true` is inert**; `condition` works. Unknown step keys are dropped
   silently at cook, so the broken spelling looks correct.
3. **`condition` is undocumented upstream** -- zero hits in published bd docs, functional
   on 1.1.0+. Forms: `condition = "{{want_x}}"` (truthy) and
   `condition = "{{target}} == staging"` (equality).
4. **Conditions are pour-time variables, not filesystem state.** There is no
   "skip if the file exists".
5. **THE ANCHOR RULE.** Every step's `needs` must name at least one unconditional step.
   A step whose entire `needs` list is filtered keeps only its `parent-child` edge and
   becomes **immediately ready with no error at pour**. Reproduced today: `Implement`
   appeared in `bd ready` alongside `Plan`. Write the anchor assertions BEFORE the
   formulas and prove they fail on a deliberately broken one.
6. **Diamond composition fails** with `duplicate id`.
7. **Diagnose with `bd cook`, never `bd mol pour`** -- pour reports every formula error
   as `not found as formula or proto ID`, naming a file that plainly exists.
8. **`formula = "name"`, not `name = "name"`** -- the wrong key fails validation with
   `name is required`, which reads as the opposite problem.

## Change 4: bonded formulas for the loops

A loop of unknown length cannot be formula steps -- the step count is unknown at cook.
Use `bd mol bond`, which is polymorphic (`proto+proto`, `proto+mol`, `mol+mol`).

| Formula | Phases | Bonds onto | Trigger |
|---|---|---|---|
| `fix-findings` | analyze -> fix -> re-analyze, cap 5 | `review`, `qa`, or `security-review-post` | actionable defects reported |
| `iterate` | `iterate.define` -> `iterate.apply` | current phase step | approved intent or approach changes |
| `bugfix` | `report` -> `patch` -> `verify` -> retry `patch`, capped | `implement` | defect in code under an active spec |
| `refine` | `refine.diff` -> `update` -> `propagate` -> `status` | `specify` subtree | spec needs iterative refinement |

`fix-findings` applies to all four review-stage steps, not just `review`/`qa`. The
formula already routes it from `review` and `qa`; `code-review` and
`security-review-post` produce the same class of finding.

**Split `verify` findings by verdict.** The verify agent emits a fixed enum
(`VERIFIED|PARTIAL|WEAK|NOT_FOUND`):

| Verdict | Route | Why |
|---|---|---|
| `WEAK` | `fix-findings` | implemented but poorly evidenced -- code to repair |
| `NOT_FOUND` / `PARTIAL` | `converge` | requirement unbuilt -- fix-findings is spec-safe and only fixes existing code |

Steering promises `mol-speckit-fix-findings` and `mol-speckit-iterate` and **neither
exists**. These are the formulas that close that gap.

## Change 5: `bugfix-spec` -- a standalone bugfix formula

A defect found in shipped code with no active spec. The extension REQUIRES a feature
directory: `bugfix.report` writes `specs/{feature}/bugs/BUG-{NNN}.md` and
`bugfix.patch` edits that feature's `spec.md`, `plan.md`, `tasks.md`. With no spec there
is nowhere to write and nothing to trace to.

So `bugfix-spec` creates its own spec directory on the existing `NNN-slug` convention
(this repo has `001-agent-conformance`, `002-bead-as-brief`), then runs the loop:

```
create-spec -> report -> patch -> verify -> (retry patch, capped)
```

Its own root bead, not bonded -- a bonded molecule assumes a parent. The loop body is
shared with `bugfix`; only the anchoring differs. `patch` writes `tasks.md`, so it needs
the beads redirect below.

Note this produces a permanent spec per standalone bug. `tinyspec` remains the lighter
route for trivial defects that do not warrant traceability.

## Change 6: routes, not steps

| Command | Why a route |
|---|---|
| `converge` | single command; writes work rather than being a phase |
| `tinyspec` | single command; change fits one paragraph |
| `reconcile` | **manual only** -- its input is a hand-written prose gap report |

**What `converge` actually does**, from its skill file: reads `spec.md`/`plan.md`/
`tasks.md` as *"the sole source of intent"*, assesses the code, and appends remaining
work. It MUST run only after implement. APPEND-ONLY: its only write is a new
`## Phase N: Convergence` section in `tasks.md`; it must not touch `spec.md`, `plan.md`,
existing tasks, or code. Not a diff tool -- no git, no branch comparison. The
constitution is authority: a MUST violation is the highest-severity finding.

Its four gap types: `missing`, `partial`, `contradicts`, and **`unrequested`** (code not
called for by the spec, surfaced for awareness -- converge appends a task to
review/justify, never deletes).

**`reconcile` is adopted as a manual route only.** It does not detect anything: its first
execution step is *"Parse the Gap Report to determine what drift occurred"*, so a human
must have already found and described the drift. `sync-drift` is what finds it, so they
are detect/act, not substitutes. Its `--spec-only` / `--plan-only` / `--tasks-only` flags
suit deliberate invocation. 17 stars, single maintainer, MIT, last pushed 2026-07-03. Be
deliberate about one behaviour: it *surgically updates* `spec.md` and `plan.md`, i.e.
edits the spec to match the code, which is sometimes exactly backwards.

**`taskstoissues` is dropped**, with an explicit NOT in the steering. It converts
`tasks.md` into GitHub issues; beads is the tracker and `tasks.md` is guard-denied, so it
has no input and its output would be a competing tracker. Say this plainly -- someone
reading spec-kit's own docs will otherwise wonder why a core command is missing.

## Change 7: the `tasks.md` collision -- 7 skills, and the guard half-covers it

The guard has two layers, and only one is complete:

- `Write|Edit|MultiEdit|apply_patch` -> **DENY**, with an actionable reason naming
  `bd create "T00N <title>" --parent <implement-step-id> --spec-id <NNN-slug>`.
- `Skill` -> **advisory, and only for `speckit-implement`**. The branch tests
  `if "speckit-implement" in haystack`; everything else passes silently.

So these seven run their whole analysis and only hit the deny at the final write:

`speckit-converge`, `speckit-reconcile-run`, `speckit-iterate-apply`,
`speckit-refine-propagate`, `speckit-cleanup`, `speckit-cleanup-run`,
`speckit-brownfield-migrate`.

Two fixes: extend the guard's `Skill` matcher to all seven so the redirect arrives
BEFORE the work, and add steering for each. Reuse the existing deny reason.

Converge additionally reads `tasks.md` to compute the next task ID and phase number, so
the adaptation must supply an ID scheme, not just a write target.

## Change 8: governance moves into setup, not a formula

`constitution` and `roadmap-write` are project-lifetime; the profiles are per-feature
(one spec dir = one root). A per-feature `constitution` step would either rewrite
governing principles per feature or be a permanent no-op with a gate rubber-stamped once
per spec -- and `condition` cannot express "skip if it exists". Converge confirms the
direction: it READS the constitution as `(if present)` authority. Every feature molecule
consumes it; none should produce it.

Setup step 5 already has the right idiom (`if ! bd where; then bd init --skip-hooks`).
Add there:

- `constitution` -- run `/speckit.constitution` if `.specify/memory/constitution.md` is
  missing **or an unfilled template**. That second test matters: `specify init` scaffolds
  a template, so a naive `[ -f ]` check always passes and never prompts. Converge already
  makes this distinction. (This repo's own constitution is filled: 0 template markers.)
- `roadmap-write` -- after it, per roadmap's documented hook, if the extension is
  installed.
- `roadmap-sync` -- mention only. Its own spec says it *"looks at the whole project at
  once and is run on demand"*, unlike brief/debrief which are per-spec at a hook. It does
  not belong in a per-feature molecule.

The constitution loses its beads gate this way. If you want approval recorded, an ADR is
the better fit than a gate: it records what was decided and rejected, where a gate only
proves someone approved.

## Change 9: port `setup-speckit.sh` to Python

Four defects, each reproduced:

1. **The version gate reads the interpreter version.** `specify --version | grep -Eo
   '[0-9]+\.[0-9]+' | head -n1` takes the first two-part number anywhere in the output,
   so `running on Python 3.11 -- version 0.14.2` yields `3.11`. It is a hard `exit 1`
   gate, so it fails a repo that should pass.
2. **`grep -qw` false-matches.** `grep -qw review` matches `security-review`;
   `grep -qw assign` matches `agent-assign`. An extension is reported "already
   installed" and skipped, and the `LEGACY_WORKFLOWS` cleanup can fire on the wrong
   name -- that one is destructive.
3. **`.specify/integration.json` parsed with `grep -o` + `sed`** (~line 325).
4. **The GitHub releases API parsed with `grep -m1 '"tag_name"' | sed`** (~line 264).

Zero test coverage today, so tests first; that is the real cost, not the translation.

Dynamic selection: read the catalog JSON (the script already fetches it) rather than
hardcoding 12. `specify extension search` has no `--json`, so parse the catalog, not CLI
prose. Reconcile the 12-hardcoded / 19-installed gap: `agent-context`, `archive`,
`brownfield`, `reconcile`, `refine`, `verify`, `verify-tasks` are installed but
unmanaged. Keep the current set as the `standard` default so nothing changes for anyone.

`bd init` must stay conditional on `bd where` -- `project-scaffold`'s `agentic/beads`
layer runs `bd init --skip-hooks` and typically gets there first.

## Change 10: extension-to-fragment wiring

The rule that emerged: **a phase gets a step, a route does not.** Of the 12 hardcoded, 7
map 1:1 to a step (`agent-assign`->`assign`, `cleanup`, `critique`, `qa`, `retro`,
`review`, `security-review`) and 5 are routes (`fix-findings`, `iterate`, `roadmap`,
`status-report`, `tinyspec`).

Caveat the brief's earlier 1:1 assumption misses: **five steps have no backing command
at all** -- `validate`, `code-review`, `docs-update`, `sync-drift`, `sync-conflicts`.
They are either subcommands (`agent-assign.validate`, `review.code`) or plain agent
instructions (`docs-update`). They cannot be gated on "is the extension installed" the
way the others can.

Make the mapping declarative -- a manifest pairing an extension with the step it
requires, or recording that it is out-of-band -- with a check that fails when an
installed phase-extension has no step or a composed step has no installed extension. With
143 catalog entries and 19 installed, this is what keeps selection honest.

## Change 11: extract to `srobroek/speckit-conductor`

AFTER change 1 lands, not as part of it. Merging three packages and relocating them in
one change means simultaneously breaking dependents and moving them; the `mcp-repomix`
removal needed five dependent PRs landed first.

Name verified free: no `speckit-conductor` on GitHub, and `srobroek/speckit-conductor`
does not exist. Chosen over `speckit-orchestrator` because
`packages/orchestrate` (v15.0.0) already *"coordinates parallel subagents through
Beads-backed DAGs"* -- near-identical wording for a different job (parallel dispatch
versus phase sequencing), and the names would not convey the difference.

Follow the `project-setup` precedent: extracted from this monorepo, consumed as an
external marketplace source, pinned to a tag rather than a branch (`apm pack` rejects
branch refs). Duplicating the validators into the new repo is accepted -- reaching across
repos at runtime violates constitution I.

### Required docs in the new repo

Once people install this rather than inheriting it, the authoring model has to be
written down. Two documents:

**`docs/adding-extensions.md`** -- the phase-versus-route rule; the five-steps-with-no-
backing-command caveat; and above all the `tasks.md` adaptation. That last one is the most
likely thing to break someone's own extension, and without docs the failure reads as our
bug rather than a documented adaptation.

**`docs/authoring-formulas.md`** -- the eight traps in change 3, each written as a
verified fact with its reproduction, not as a warning. Plus: loops are bonded molecules,
never step chains; profiles are standalone, never composed, and why.

## Gates

All of: `apm run build-artifacts`, `apm pack --check-clean`,
`apm run check-readme-tables`, `apm run check-release-please`, the five validators
(`check-hook-contract`, `audit-codex-config`, `check-script-invocation`,
`check-release-baselines`, `check-instructions-apply-to`), `pytest` over every touched
package and `.apm/scripts/`, and `typos` tree-wide.

Formula-specific: `bd cook` clean on all three profiles, every bonded formula, and
`bugfix-spec`; `bd mol pour --dry-run` on each profile; anchor-rule assertions proven to
fail on a deliberately broken formula.

Conventional commits, one logical unit per change, explaining why. `dgit push` (NOT plain
`git push` -- github.com needs the wrapper). Open a PR filling
`.github/pull_request_template.md`.

## Report

Per change: what landed, with evidence. Then: how tombstones are expressed; the three
profiles' step counts and the `lean` re-anchoring; the extension-to-step manifest shape;
whether `mol-speckit-fix-findings` and `mol-speckit-iterate` now exist; the guard's
extended `Skill` coverage; the migration note for external dependents; and anything you
did not do, with the reason.

Be honest about gaps. Treat every claim above as a hypothesis to re-verify rather than a
fact to build on.
