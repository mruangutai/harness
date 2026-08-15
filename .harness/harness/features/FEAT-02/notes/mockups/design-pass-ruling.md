# Design-pass ruling — FEAT-02 (verdict-shadowing fix in validate-digest.py)

**Ruling: no end-user interaction. `needs_prototype: false`. No DESIGN.md required.**

## Why

- The feature is a bugfix to `.claude/skills/harness/bin/validate-digest.py`, a
  stdlib Python CLI (BRIEF.md, Constraints). Its consumers are agents and hooks —
  the validator runs in hook mode and via the test suite, never in front of a human.
- There is no screen, control, or flow a person operates. Per the interaction table,
  this is squarely "an API with no UI surface" / background tooling.
- The only human-visible surface is unchanged error text on stderr in fail-open hook
  mode, which BRIEF constraint 4 explicitly freezes ("must not change") — so there is
  no new experience to judge, hence nothing a prototype could de-risk.

## What was NOT produced, deliberately

- No DESIGN.md for FEAT-02 — a design contract (palette, type scale, spacing) has no
  object here.
- No mockups, no prototype.

## Scope note (non-blocking)

If a future feature ever surfaces validator output to the user (e.g. a formatted
contract-violation report in the main session), that feature should take its own
design pass; this ruling covers FEAT-02 only.
