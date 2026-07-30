# SpecKit on beads

The phase DAG is a beads molecule, not prose. A poured molecule carries the steps,
their ordering, and the human approval gates, so the workflow is executable rather
than described.

STATE AT HEAD
MUST Treat this package as a scaffold. It ships this steering and the release
  machinery; the formulas, skills, and guard specified in `docs/BUILD-PLAN.md` are
  not written yet.
NOT Pour a formula from this package. `bd formula list` returns nothing for it.
DEFAULT Until the formulas ship, the SpecKit workflow layer lives in
  `srobroek/agentic-packages` as `speckit`, `speckit-beads`, and
  `steering-speckit`. Install those.

WHAT THIS PACKAGE WILL OWN
| Piece | Shape |
|---|---|
| `minimal`, `lean`, `full` | standalone phase-DAG formulas, poured once per feature |
| `fix-findings`, `iterate`, `bugfix`, `refine` | bonded loop formulas, attached with `bd mol bond` |
| `bugfix-spec` | its own root, creates its own spec directory |
| `converge`, `tinyspec`, `reconcile` | routes reached by judgement, never steps |

MUST Keep profiles standalone rather than composing them. A formula that redeclares
  an inherited step to rewire its joins drops that step's `[steps.gate]` silently,
  and this workflow carries three human approval gates.
MUST Express a loop as a bonded molecule. A loop's iteration count is unknown when
  the formula is cooked, which a fixed step list cannot represent.
NOT Add a step for a route. A phase earns a step; a route is invoked when something
  goes wrong or when a change needs no lifecycle.

TASK STATE
MUST Keep task state in beads. `specs/*/tasks.md` is read-only legacy under this
  layer, and a guard denies writes to it.
DEFAULT Create implementation tasks as children of the molecule's implement step:
  `bd create "T00N <title>" --parent <implement-step-id> --spec-id <NNN-slug>`.

DIAGNOSING A FORMULA
MUST Use `bd cook <name>`. `bd mol pour` reports every formula error as `not found
  as formula or proto ID` while naming a file that exists, so a broken formula is
  indistinguishable from a missing one.
MUST Give every step's `needs` at least one unconditional entry. A step whose whole
  `needs` list is filtered keeps only its parent edge and becomes immediately ready,
  with no error at pour.
NOT `optional = true`. It is inert: unknown step keys are dropped silently at cook.
  `condition` is the working key, and it reads pour-time variables rather than
  filesystem state.
