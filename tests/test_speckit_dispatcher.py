#!/usr/bin/env python3
"""Tests for the SpecKit command dispatcher.

Driven through the real entrypoint over stdin, because the contract under test is the
payload in and the emitted decision out, which is what the runtime exercises. Each
event carries the command in a different field, and getting one wrong makes the hook a
silent no-op rather than an error, so every field is pinned here.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

DISPATCHER = Path(__file__).resolve().parents[1] / "scripts" / "speckit-dispatcher.py"


def run(payload: dict) -> tuple[int, dict | None]:
    proc = subprocess.run(  # noqa: S603
        [sys.executable, str(DISPATCHER)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    out = proc.stdout.strip()
    return proc.returncode, (json.loads(out) if out else None)


def context(result: dict | None) -> str:
    if not result:
        return ""
    h = result["hookSpecificOutput"]
    return h.get("additionalContext") or h.get("permissionDecisionReason") or ""


def decision(result: dict | None) -> str:
    if not result:
        return "silent"
    return result["hookSpecificOutput"].get("permissionDecision", "advise")


# --- each event finds the command in its own field ---------------------------


def test_expansion_reads_command_name():
    """A typed /speckit.x arrives as command_name, before the command expands."""
    _, r = run({"hook_event_name": "UserPromptExpansion", "command_name": "speckit.specify"})
    assert "Pour a molecule" in context(r)


def test_expansion_tolerates_a_leading_slash():
    _, r = run({"hook_event_name": "UserPromptExpansion", "command_name": "/speckit.specify"})
    assert "Pour a molecule" in context(r)


def test_submit_parses_the_slash_command_out_of_prose():
    """Codex has no expansion event, so the command arrives inside prompt text."""
    _, r = run(
        {"hook_event_name": "UserPromptSubmit", "prompt": "ok now please /speckit.converge for me"}
    )
    assert "Convergence phase" in context(r)


def test_pretooluse_reads_a_skill_name():
    """Deployed skills are speckit-x-y, so the separator differs from the command."""
    _, r = run({"hook_event_name": "PreToolUse", "tool_input": {"skill": "speckit-cleanup"}})
    assert "closeout sweep" in context(r)


def test_pretooluse_falls_back_to_prompt_for_codex():
    """Codex PreToolUse may carry no skill field at all."""
    _, r = run({"hook_event_name": "PreToolUse", "tool_input": {"prompt": "/speckit.retro.run"}})
    assert "learnings are in the beads" in context(r)


# --- the one deny ------------------------------------------------------------


def test_taskstoissues_is_denied_on_pretooluse():
    _, r = run({"hook_event_name": "PreToolUse", "tool_input": {"skill": "speckit-taskstoissues"}})
    assert decision(r) == "deny"
    assert "second task tracker" in context(r)


def test_taskstoissues_refusal_travels_as_context_on_a_prompt_event():
    """A prompt event has no tool call to stop, so the refusal has to be context."""
    _, r = run({"hook_event_name": "UserPromptSubmit", "prompt": "/speckit.taskstoissues"})
    assert decision(r) == "advise"
    assert context(r).startswith("DO NOT RUN THIS COMMAND")


# --- what must stay silent ---------------------------------------------------


@pytest.mark.parametrize("command", ["plan", "tasks", "review.code", "security-review.audit"])
def test_an_unhooked_command_is_silent(command):
    """62 SpecKit skills install; advising on all of them trains agents to ignore this."""
    _, r = run({"hook_event_name": "UserPromptSubmit", "prompt": f"/speckit.{command}"})
    assert r is None, f"{command} should carry no instruction"


def test_a_non_speckit_prompt_is_silent():
    _, r = run({"hook_event_name": "UserPromptSubmit", "prompt": "please fix the failing test"})
    assert r is None


def test_an_unknown_event_is_silent():
    _, r = run({"hook_event_name": "PostToolUse", "tool_input": {"skill": "speckit-cleanup"}})
    assert r is None


# --- prefix resolution -------------------------------------------------------


def test_a_longer_command_resolves_to_its_prefix_entry():
    """review.run.something must still find the review.run instruction."""
    _, r = run({"hook_event_name": "UserPromptSubmit", "prompt": "/speckit.review.run.extra"})
    assert "route by kind" in context(r)


# --- fail open ---------------------------------------------------------------


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"hook_event_name": "UserPromptExpansion"},
        {"hook_event_name": "UserPromptExpansion", "command_name": None},
        {"hook_event_name": "UserPromptExpansion", "command_name": {"not": "a string"}},
        {"hook_event_name": "PreToolUse", "tool_input": "a bare string"},
    ],
)
def test_a_malformed_payload_exits_zero_and_says_nothing(payload):
    code, r = run(payload)
    assert code == 0
    assert r is None


def test_empty_stdin_exits_zero():
    proc = subprocess.run(  # noqa: S603
        [sys.executable, str(DISPATCHER)], input="", capture_output=True, text=True, check=False
    )
    assert proc.returncode == 0
    assert proc.stdout.strip() == ""


def test_unparsable_stdin_exits_zero():
    proc = subprocess.run(  # noqa: S603
        [sys.executable, str(DISPATCHER)], input="NOT JSON", capture_output=True, text=True, check=False
    )
    assert proc.returncode == 0
    assert proc.stdout.strip() == ""


def test_never_emits_ask():
    """Constitution III: no guard may emit `ask`, which stalls an autonomous agent."""
    for payload in (
        {"hook_event_name": "PreToolUse", "tool_input": {"skill": "speckit-taskstoissues"}},
        {"hook_event_name": "UserPromptExpansion", "command_name": "speckit.specify"},
    ):
        _, r = run(payload)
        assert decision(r) != "ask"


# --- the instruction table itself -------------------------------------------


def test_every_instruction_names_a_concrete_next_action():
    """An instruction an agent cannot act on is noise in the context window."""
    sys.path.insert(0, str(DISPATCHER.parent))
    from speckit_instructions import DENIED, INSTRUCTIONS

    for command, text in {**INSTRUCTIONS, **DENIED}.items():
        assert "bd " in text or "speckit." in text or "formulas/" in text, (
            f"{command} gives no actionable command"
        )
        assert len(text) > 80, f"{command} is too thin to be worth the window"
