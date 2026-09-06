# Plan fix cycle 1 — BUG-1305 — F-01..F-08 applied

*(Dispatch named `notes/plan-fix-BUG-1305-c1.md`; check-domain.sh denies that path for harness-pm —
permitted is `notes/research-*.md`. Written here instead, per harness-handoff #216.)*

## BLUF

**All eight findings applied; none declined.** The plan now specifies both branches of T-04's
measurement up front (new **T-09**), the residual is disclosed in REQ-01 and SC-01 where the operator
signs, T-07 has a home (REQ-08/SC-08) and its DEC-145 supersession is named in Constraints, and the
three under-specified criteria (SC-01 route set, SC-03 discriminator, SC-07 artifact) are now
falsifiable. Approval remains `pending`; `panel:` absent; top-level `status: plan` unchanged.

## Disposition, by finding

| ID | Applied | Where |
|---|---|---|
| F-01 | yes | `amend` D-01.choice + D-01.because; `apply` **T-09**; `amend` T-04.intent |
| F-02 | yes | BRIEF REQ-01 (route table + contingent closure), SC-01 (contingent clause) |
| F-03 | yes | BRIEF REQ-08, SC-08, DEC-145 Constraints bullet; `amend` T-07.traces → `[REQ-08]` |
| F-04 | yes | BRIEF SC-07 — names `notes/regression-delta-BUG-1305.md`, four explicit FAIL conditions |
| F-05 | yes | BRIEF REQ-01 + SC-01 — four routes enumerated, Bash and NotebookEdit exclusions reasoned |
| F-06 | yes | `amend` D-04.choice (reported for the operator's ruling); BRIEF DEC-208 bullet as a live choice |
| F-07 | yes | `amend` T-02.intent (the DEC-171 paragraph); mirrored in BRIEF's DEC-171 bullet |
| F-08 | yes | BRIEF SC-03 — the `non-checkpoint top-level key` prohibition moved into the criterion |

## F-01, the shape of the fix

D-01 no longer bars the identity signal; it makes the denial **conditional**: it fires only when both
sides carry a resolvable identity **and** they disagree, gated on T-04's per-runtime answer. **T-09**
(`depends_on: [T-04]`) wires it: `run_identity.identity_denial()` beside `identity_disagreement`,
consumed in check-domain.sh's `RE_STATE_YAML` PRE branch after T-02's `conflict()` check, with seven
enumerated fail-open rows (no marker; null recorded identity; unresolvable `_resolve_identity`; equal
identities; no live claim or a raising registry read; a `runtime: "omp"` claim — `inflight_registry.py:255-258`;
a runtime T-04 did not record as discriminating). `conflict()` still never consults identity, so
check-state.sh's sweep is unaffected. **No-op branch named:** on `discriminates: no|inconclusive` T-09
changes no code and writes `notes/identity-denial-BUG-1305.md` with `disposition: not-executed` and
the residual in operator terms — that note is where the report lands, and SC-01's contingent clause
points at it. T-04's intent now states what each answer triggers; the "do not write a task for it"
clause is gone.

## REQ → task → SC, after the change

- **Mode A** — REQ-01 → T-01, T-02, T-04, **T-09** → SC-01 · REQ-02 → T-01, T-03 → SC-02 ·
  REQ-03 → T-03 → SC-03
- **Mode B** — REQ-04 → T-05 → SC-04 · REQ-05 → T-06 → SC-05 · REQ-06 → T-06 → SC-06
- **Both** — REQ-07 → T-02, T-05, T-06, T-08 → SC-07
- **Doctrine** — REQ-08 → T-07 → SC-08 (T-07 no longer traces REQ-01; strikeable alone)

Mode separation still holds: no task and no criterion spans A and B except SC-07 by design.

## Write route — every plan.yaml change went through `plan-merge.py`

`amend` (compare-and-swap, `--show` then `--expect-sha256 --value-file`): D-01.choice, D-01.because,
D-04.choice, T-07.traces (`--yaml-value`), T-02.intent, T-04.intent, T-09.intent.
`apply --proposal`: T-09 (`ADDED T-09`). **No CAS failure occurred**; every amend exited 0. BRIEF.md
was edited normally; `## Approval` untouched.

## Gate output, verbatim

```
$ python3 /Users/molchairuangutai/GitHub/harness/.claude/skills/harness/bin/check-plan-routes.py <abs plan.yaml>
... 8 DEVIATION lines (the expected DEC-174 carve-out shape) + "OK T-07"
0 violation(s) across 1 plan(s)
EXIT_CHECK_PLAN_ROUTES=0
```
```
$ python3 .../bin/check-instruction-paths.py <abs plan.yaml>
check-instruction-paths: <abs plan.yaml> selects nothing in scope
EXIT_CHECK_INSTRUCTION_PATHS=2
$ python3 .../bin/check-instruction-paths.py <worktree root>
check-instruction-paths: <worktree root> selects nothing in scope
EXIT_CHECK_INSTRUCTION_PATHS_ROOT=2
$ python3 .../bin/check-instruction-paths.py /Users/molchairuangutai/GitHub/harness
scanned 62 file(s), 0 violation(s)
EXIT_ROOT=0
```
That checker takes a **checkout root**, not a plan: it scans `.omp/agents`, `.claude/agents`,
`.claude/skills/harness-*/SKILL.md`, references and templates (`scope()`, :43-57). The worktree carries
none of those, hence exit 2 on both the plan-path and worktree-root invocations; the control-plane
root answers `0 violation(s)`. Exit 2 there is a bad-argument answer, not a finding against this plan.

Structural re-check after the writes: `yaml.safe_load` OK; `approval: {status: pending}`; `panel`
absent; `status: plan`; all nine tasks carry `traces`/`change_type`/`execution_mode`/`files`/`verify`/
`intent`; every `verify:` is a literal `|`. The only `<...>` tokens in the plan are T-07's pre-existing
slug **grammars** (`<task-or-purpose>-<squad>`, `<YYYY-MM-DD>-<seq>-<squad>`) — notation, not
placeholders, and outside this cycle's change list.

T-09's verify ladder was smoke-tested on four synthetic notes: implemented without `## Red proof` → 1,
implemented with it → 0, `not-executed` → 0, no `disposition:` line → 1.

## git status (verbatim, run at end)

```
?? .harness/harness/features/BUG-1305-run-state-clobber/
```
No tracked file modified; BRIEF.md and plan.yaml live inside that untracked directory.

## Open question for the panel

Q1 (non-blocking): T-09 traces `REQ-01` only, per dispatch. It edits `check-domain.sh` and its test
file, so REQ-07 ("no protection traded away") arguably binds it too, and T-08's `depends_on` does not
include T-09. If the panel agrees, the fix is one `amend` on each.
