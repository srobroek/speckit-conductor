# speckit-conductor

SpecKit workflow orchestration on [beads](https://github.com/gastownhall/beads):
phase-DAG formulas, human approval gates, and bonded loops for spec-driven
development.

## Status

**Scaffold.** The build plan is in [`docs/BUILD-PLAN.md`](docs/BUILD-PLAN.md).

This repository is the extraction target for the SpecKit workflow layer currently
living in `srobroek/agentic-packages` as three packages: `speckit`,
`speckit-beads`, and `steering-speckit`. Those merge into one package first; this
repository receives the merged result. Extraction happens **after** the merge lands
and its dependents are migrated, not before -- a package that is renamed and
relocated in one step breaks `apm install` at resolution.

## What it will be

- Three standalone phase-DAG formulas -- `minimal`, `lean`, `full` -- poured once
  per feature, each declaring its own step graph rather than composing, because a
  composing child silently drops a parent's approval gate.
- Bonded loop formulas -- `fix-findings`, `iterate`, `bugfix`, `refine` -- attached
  to a running molecule via `bd mol bond`, because a loop of unknown length cannot
  be expressed as formula steps.
- A standalone `bugfix-spec` formula that creates its own spec directory.
- Routes reached by judgement rather than as steps: `converge`, `tinyspec`,
  `reconcile`.
- A guard that keeps task state in beads rather than `tasks.md`.
- Authoring docs so consumers can add their own extensions and formulas.

## Naming

Chosen over `speckit-orchestrator` because a sibling package already coordinates
parallel subagents through beads DAGs; the names would not convey that this one
sequences phases for a single feature while that one dispatches agents. A conductor
keeps time through a score, which is what phase sequencing is.
