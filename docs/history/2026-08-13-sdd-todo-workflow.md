# SDD TODO workflow

Date: 2026-08-13

## Changes

- Instruct agents to inspect `SDD/todo.md` at the start of every task.
- Define `[+]` entries as active work that must be acted on during the current
  task.
- Require agents to request missing material decisions instead of making unsafe
  assumptions.
- Define `[x]` as the completed marker and require completed work to be recorded
  under `sdd/changes/`.
- Leave ordinary `[ ]` backlog entries inactive unless explicitly requested.
- Require every newly discovered pending action, blocker, or incomplete portion
  to be recorded as an indented checklist sub-action beneath its parent TODO.
- Require all necessary sub-actions to be complete before closing their parent.

## Active item discovered

The TODO marked adding an open-source license as active. The project owner
selected MIT, and the item was subsequently completed.
