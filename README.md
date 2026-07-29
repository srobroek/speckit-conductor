# speckit-conductor

SpecKit workflow orchestration on [beads](https://github.com/gastownhall/beads):
phase-DAG formulas, human approval gates, and bonded loops for spec-driven
development.

## State at HEAD

A scaffold: `apm.yml`, the release machinery, and a build plan. No formula, skill,
or script has been written yet. [`docs/BUILD-PLAN.md`](docs/BUILD-PLAN.md) specifies
the work.

The SpecKit workflow layer lives in `srobroek/agentic-packages` as three packages:
`speckit`, `speckit-beads`, and `steering-speckit`. Those merge into one package
there, and this repository receives the merged result. Extraction waits for the
merge and for its dependents to migrate, because a package that is renamed and
relocated in one step breaks `apm install` at resolution.

## What it will hold

Phase-DAG formulas at three depths, `minimal`, `lean`, and `full`, each poured once
per feature. Each declares its own step graph. A formula that composes from a parent
drops the parent's `[steps.gate]` on any step it redeclares, silently, and this
workflow carries three human approval gates.

Bonded loop formulas for `fix-findings`, `iterate`, `bugfix`, and `refine`, attached
to a running molecule with `bd mol bond`. Their iteration count is unknown when the
formula is cooked, which a fixed step list cannot express.

A `bugfix-spec` formula that creates its own spec directory, for a defect found with
no active spec.

Routes reached by judgement rather than as steps: `converge`, `tinyspec`,
`reconcile`.

A guard that keeps task state in beads rather than `tasks.md`.

Authoring docs, so a consumer can add an extension or a formula. The community
catalog holds 143 extensions and grows; the traps that make a formula fail silently
are documented with their reproductions.

## The name

A sibling package, `orchestrate`, coordinates parallel subagents through beads DAGs.
This one sequences phases for a single feature. A conductor keeps time through a
score, which is what phase sequencing is.
