"""The anchor rule, checked on every shipped formula for every var combination.

`bd cook` does not catch an anchor violation and `bd mol pour` reports no error: a step
whose entire `needs` list is filtered out by `condition` keeps only its parent-child
edge and becomes immediately ready, in parallel with the first step. Verified against
bd 1.1.2 by removing `analyze` from `speckit-basic`'s `implement` step -- cook stayed
clean, and the pour put `implement` in `bd ready` beside `specify` with no `blocks` edge.

So the check has to be static, and it has to run per selection rather than once: a step
is safe when, for every combination of the formula's vars, at least one step it needs
survives.
"""

from __future__ import annotations

import itertools
import tomllib
from pathlib import Path

import pytest

FORMULA_DIR = Path(__file__).resolve().parent.parent / "formulas"
FORMULAS = sorted(FORMULA_DIR.glob("*.formula.toml"))


def _name(path: Path) -> str:
    """The stem bd resolves a formula by: the filename minus the .formula.toml suffix."""
    return path.name.removesuffix(".formula.toml")

# The values a condition treats as true, per bd's condition grammar. A condition is
# either `{{var}}` (truthy test) or `{{var}}` == value (equality test).
TRUTHY = {"true", "1", "yes", "on"}


def _selected(step: dict, values: dict[str, str]) -> bool:
    """Whether a step survives filtering under one set of var values."""
    cond = step.get("condition")
    if cond is None:
        return True
    if "==" in cond:
        lhs, rhs = (part.strip() for part in cond.split("==", 1))
        var = lhs.strip("{} ")
        return values.get(var, "") == rhs
    var = cond.strip("{} ")
    return values.get(var, "").lower() in TRUTHY


def _var_combinations(spec: dict) -> list[dict[str, str]]:
    """Every combination of the values each declared var can be poured with.

    `feature` is a free-text var that conditions nothing, so it is pinned. Every other
    var is a flag, and both of its states have to be checked -- a formula that only
    works at its defaults is a formula that breaks the first time someone passes a flag.
    """
    flags = [name for name in spec.get("vars", {}) if name != "feature"]
    combos = []
    for picks in itertools.product(["yes", "no"], repeat=len(flags)):
        values = dict(zip(flags, picks))
        values["feature"] = "001-probe"
        combos.append(values)
    return combos


@pytest.mark.parametrize("path", FORMULAS, ids=_name)
def test_every_needs_keeps_an_anchor(path: Path) -> None:
    spec = tomllib.loads(path.read_text())
    steps = {s["id"]: s for s in spec["steps"]}

    for values in _var_combinations(spec):
        alive = {sid for sid, s in steps.items() if _selected(s, values)}
        for sid in alive:
            needs = steps[sid].get("needs", [])
            if not needs:
                continue
            surviving = [n for n in needs if n in alive]
            assert surviving, (
                f"{_name(path)}: step {sid!r} needs {needs} and every one is filtered out "
                f"under {values}. It would pour immediately ready, in parallel with the "
                f"first step, with no error."
            )


@pytest.mark.parametrize("path", FORMULAS, ids=_name)
def test_needs_reference_declared_steps(path: Path) -> None:
    spec = tomllib.loads(path.read_text())
    ids = {s["id"] for s in spec["steps"]}
    for step in spec["steps"]:
        unknown = [n for n in step.get("needs", []) if n not in ids]
        assert not unknown, f"{_name(path)}: step {step['id']!r} needs unknown {unknown}"


@pytest.mark.parametrize("path", FORMULAS, ids=_name)
def test_formula_key_matches_filename(path: Path) -> None:
    """bd resolves a formula by filename stem, so a mismatch makes it unreachable."""
    spec = tomllib.loads(path.read_text())
    assert spec.get("formula") == _name(path), (
        f"{path.name} declares formula={spec.get('formula')!r}; bd resolves it as "
        f"{_name(path)!r} and lists it under the declared name, so the two must match."
    )


@pytest.mark.parametrize("path", FORMULAS, ids=_name)
def test_no_step_type_is_epic(path: Path) -> None:
    """Pour rejects an epic-to-task blocking dep: "epics can only block other epics"."""
    spec = tomllib.loads(path.read_text())
    for step in spec["steps"]:
        assert step.get("type") != "epic", f"{_name(path)}: step {step['id']!r} is an epic"


def test_bondable_formulas_carry_the_mol_prefix() -> None:
    """`bd mol bond` resolves a formula name only when the filename stem is prefixed.

    Without the prefix it reports `not found (not an issue ID or formula name)`.
    """
    profiles = {"speckit-feature", "speckit-lean", "speckit-basic"}
    for path in FORMULAS:
        if _name(path) in profiles:
            continue
        assert _name(path).startswith("mol-"), (
            f"{path.name} is a sub-process formula, so `bd mol bond` must be able to "
            f"resolve it, which requires a `mol-` prefixed filename."
        )


def test_every_profile_takes_the_same_vars() -> None:
    """A profile is picked by depth, so the pour interface cannot change with it."""
    expected = {"feature", "autonomous", "agent_assign"}
    for name in ("speckit-feature", "speckit-lean", "speckit-basic"):
        spec = tomllib.loads((FORMULA_DIR / f"{name}.formula.toml").read_text())
        assert set(spec["vars"]) == expected, f"{name} vars: {set(spec['vars'])}"
        assert spec["vars"]["autonomous"]["default"] == "no"
        assert spec["vars"]["agent_assign"]["default"] == "yes"
