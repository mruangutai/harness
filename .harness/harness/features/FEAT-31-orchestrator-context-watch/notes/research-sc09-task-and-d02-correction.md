# SC-09 gets a task, and D-02 stops lying about it

**BLUF.** `plan.yaml` now has `T-19`, the only task tracing SC-09, and D-02's `choice:` no longer
claims plan4 closed SC-09. Both premises the dispatch handed me were re-derived at `abcba0e` and
both held. One premise the dispatch got slightly wrong: HEAD is `abcba0e`, not `20ccac5` — the qa
gate commit landed after the dispatch text was written. Tree was clean before my edit; only
`plan.yaml` is dirty now.

## Premises re-derived at abcba0e

| Claim | Verdict | Evidence |
|---|---|---|
| DEC-159 has no mid-flight clause | true | `DECISIONS.md:3945-3996`; the only mid-phase words are "a mid-phase relay is the bounded escape", which names an escape and no rule |
| the falsified clause is present | true | `grep -c 'the watchdog remains the post-hoc audit'` inside the DEC-159/DEC-160 slice = **1**, on one physical line |
| D-02 falsely claimed plan4 closed SC-09 | true | old `plan.yaml:84`; contradicted by `plan.yaml:677` (T-09: "Do NOT edit DEC-159 — that is SC-09 and belongs to a later planning run") and by no later task tracing it |

## REQ trace: REQ-09, and it is the only fit

`BRIEF.md:98-99` — *"A warned orchestrator determines the nearest seam and writes the state a
successor needs before it ends. Where no seam is reachable, it writes a mid-phase handoff rather
than continuing."* That sentence **is** the rule SC-09 (`BRIEF.md:145-150`) requires DEC-159 to
state. REQ-08 is the warning's delivery (T-17, shipped); REQ-10 is the successor's resume. T-14
already carries `[REQ-09, REQ-10]` for the enforcement half; T-19 is REQ-09's doctrine half.

## DECISIONS-INDEX.md IS in `files:` — and not for the reason the dispatch guessed

The title and tags do not change, so the row's *text* is stable. The row's **anchor** is not:
`gen-decisions-index.py:347` emits `- {key} @{dec['line']}`, a source line number. Lengthening
DEC-159 shifts the anchor of DEC-160 through DEC-198, so the committed index stops matching a fresh
regeneration and `test-gen-decisions-index.py::test_committed_index_matches_a_fresh_regeneration`
goes red. Baseline: that suite exits **0** at `abcba0e`, so the red would be caused by this task and
nothing else. The index is therefore a deliverable of T-19, written only by re-running the generator.

## Lane grant — verified against the live guard, not the plan

`check-domain.sh --resolve` returns `harness-documentor` for both
`.harness/harness/docs/DECISIONS.md` and `.harness/harness/docs/DECISIONS-INDEX.md`. That agrees
with `plan.yaml`'s `lanes:` rows. `check-plan-routes.py` reports `OK T-19 granted to
harness-documentor`, 0 violations across the plan.

## The verify block is discriminating — every count measured at abcba0e first

Inside the `awk '/^## DEC-159 /,/^## DEC-160 /'` slice (52 lines, both boundaries anchored):
`^## DEC-159 ` = 1, `templates/HANDOFF.md` = 1, `the watchdog remains the post-hoc audit` = 1,
`mid-flight` = 0, `context-size` = 0, `context-watch-hook.py` = 0, `turn-count` = 1,
`STRUCK|am.[0-9]` = 0. `mid-flight`, `context-size` and `context-watch-hook.py` are also **0
file-wide** in `DECISIONS.md`, so a match can only come from this edit. The block fails on the
pre-change tree on two counts at once. Every mandated token is a single unbroken word, because
DEC-159's prose is hard-wrapped and a multi-word phrase can split across lines.

Two controls exist so an errored search cannot read as absence: the heading count and the
`templates/HANDOFF.md` count both come from the same variable and the same command shape and both
must be non-zero.

## Open

- **Approval.** The task set changed after signature. `harness-spec-driven` says that resets
  approval; the `approval:` block is not mine to write. It is byte-identical to HEAD.
- **Board.** `check-state.sh` INV-26 now wants issue #672 (T-19, auto-created on write) moved off
  Backlog. Orchestrator's.
- **Pre-existing, not mine:** `check-domain.sh --post` reports undeclared `agent` keys at
  `feature.json` `/runs/9-12`, and `check-state.sh` flags FEAT-26's unapproved BRIEF.
