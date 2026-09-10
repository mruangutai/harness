# STATE

## Current

- feature: FEAT-104-strict-digest-schema
- runs: `2026-09-10-12-qa-gate-validator` (qa gate, `harness-validator-lead`, PASS) and
  `2026-09-10-13-simplify-eng` (simplify, `harness-eng-lead`, PASS), both at tip `790023f0`
- squads: validator, eng
- status: validate — **SC-08's proof gap is CLOSED and both build-side gates are green at the new
  tip.** `review_sha` re-pinned `168f875f` → `790023f0`. Owed before ship: the SC-13 UAT and the CEO
  briefing. No panel re-run, no goal-check re-run, no merge.

**The delta re-validated is two lines and nothing else.** `git diff 168f875f 790023f0 -- tests/` is
`tests/integration/test-check-domain.py` at +4/-2, inside `_undeclared_cases()`: the version-2
undeclared-step-key case gained `"run-state-schema.json" in strict.stderr` and
`` "`evidence`" in strict.stderr ``, and its name gained "and gives its route". No source file, gate
script, config or other test changed. DEC-174 held: every agent was read-only and
`git status --porcelain` showed zero tracked modifications at both returns.

**QA gate PASS, and I re-ran both suites myself rather than adopting the figures** (`runs/-12`).
`run-unit-tests.sh --kind unit` → exit 0, 36 files, 2.20s; `--kind integration` → exit 0, 70 files,
71.08s, zero raw `^FAIL ` lines. Both counts are EXACTLY the `168f875f` baseline (36 / 70), so
nothing was silently dropped from discovery — the failure a green exit code cannot see.
`test-check-domain.py` reports **12/12** with `ok    schema_version 2 refuses an undeclared step
key, names it and gives its route`. `matrix_ok: true`, re-derived for this test-only delta; every
other kind resolved `not_applicable`.

**The 4 raw `FAIL ` tokens on the unit suite are a self-test's own evidence, not a masked red.**
`tests/unit/test-factory-claim-mutation.py:98` builds the literal `"FAIL  BUG-1290 {case_id}:"` and
`:199-200` prints it as a PASSING mutation proof. My acceptance wording was unsatisfiable-as-literal
on a green suite — my defect, raised as Q-B2.

**I verified the emitter at source, at the commit under grade.** `git show
790023f0:.claude/skills/harness/bin/check-domain.sh` — one unconditional `out.append` pair inside
`if _schema_errors:` emits all four asserted substrings: the head `undeclared step key or evidence
shape.`, the offending key name, `.claude/skills/harness/bin/run-state-schema.json`, and backticked
`` `evidence` ``. The only other `run-state-schema.json` occurrence is the `except Exception` branch,
which emits a DIFFERENT head and so carries neither `undeclared step key` nor backticked `evidence`
— it cannot satisfy the assertion SET. The conjunction is pinned uniquely to the intended producer.
**Red capability stays reasoned, not mutated** (the mutation would edit a carve-out) — unchanged
from c9, not new debt.

**SIMPLIFY PASS with `applied: none`** (`runs/-13`). Four angles, each with its own verdict — reuse
(`harness-data-engineer`): no substring-set helper exists to duplicate, the inline and-chain is the
file's own idiom (`:144-146`); simplification (`harness-backend-dev`): the four-clause conjunction is
the weakest sufficient form, clauses 3–4 co-emitted with clause 2 is real but backlog-only;
efficiency (`harness-dev-ops`): zero added work, one subprocess before and after; altitude
(`harness-ai-dev`): LEAVE, both substrings pin the route SC-08 demands. **No reader would have
applied anything**, so DEC-174 bound nothing. Findings: high 0, med 0, low 2, neither gating. The eng
lead REJECTED its own reader's alternative of dropping the backticks from `` `evidence` ``: the head
line already contains the bare word, so the backticks are what discriminate body from head.

**`cycles_used` is 9 of 10 — the increment is the SC-08 unmet-SC re-dispatch, one, not two.** Both
leads reported ZERO send-backs, so neither run adds a cycle (DEC-157). **I did NOT count the
digest-contract repair below as rework, and that is visible rather than silent:** it was not a gate
failure and not a lead's error, it was my dispatch demanding a field the closed contract forbids.
One cycle remains. `len(runs)` is 23 of 20 — informational, PASSED, stops nothing (#79). My read:
both runs earn their place as the gates the SC-08 fix cannot ship without, each first-pass clean.

**A record repair, disclosed rather than buried.** The QA digest as returned carried an undeclared
key `suite_results` and failed `validate-digest.py`. **The cause is mine** — my acceptance demanded
per-kind exits and file counts as DIGEST fields and the contract has no key for them, so the lead
invented one; SECOND occurrence of this class (Q4 was the first). Nothing measured was lost: every
fact was already in `state.yaml`'s step `evidence`. A run digest is append-only, so the original
block is PRESERVED and a contract-valid block appended beneath it, attributed to me with the reason
and the Q6 measurement in full: `runs/2026-09-10-12-qa-gate-validator/digest.md`. Both digests and
both `state.yaml` files are `schema_version: 2` and validate at exit 0.

**The pin moved deliberately and only after both gates returned.** Simplify precedes the pin by
doctrine and applied nothing, so no commit moved the tip between the gates and the pin. The c9 panel
PASS at `168f875f` is NOT invalidated: the only difference between the commits is a strengthened
assertion inside a test the panel already read.

## Open Questions

- Q8 (**RESOLVED** — was blocking): SC-08's proof gap is closed by `790023f0`, the main session's own
  DEC-174 carve-out edit. Re-validated here: 12/12, both suites green, emitter traced. No
  re-signature needed — an approved criterion was satisfied, not amended.
- Q6 (**NARROWED**, was blocking, harness defect): the append-only channel CAN repair a digest whose
  defect is a REMOVABLE key — measured on a scratch copy, then used on `runs/-12`; the validator
  parses the APPENDED block, so Q6's "parser stops at `artifact:`" premise is false for this shape.
  It still cannot repair a MISSING required field (`runs/-06`) or a verdict CONTRADICTION
  (`runs/-08`), because appending cannot delete or reconcile. Those two stay stranded.
- Q-B3 (not blocking, harness defect — new): the digest contract has no home for per-kind suite exits
  and file counts, the natural product of a qa-gate run. Either the qa-gate lead schema gains a
  declared field, or dispatches stop asking. Same class as Q4.
- Q-B2 (not blocking, harness defect — new): "zero `^FAIL ` lines" is unsatisfiable-as-literal on a
  green unit suite (`test-factory-claim-mutation.py:98,199-200` prints that token as a passing
  proof). Say "zero runner-emitted FAIL verdicts", or count failing FILES. Measured: 4 unit, 0
  integration.
- Q9 (not blocking, main session): REQ-08's generic-lead archive exemption
  (`validate-digest.py:1407`) has no test able to redden. Does NOT falsify REQ-08. Backlog chore, or
  accept as a standing risk?
- Q1 (not blocking, main session, DEC-174): **CF-1** (security, `med`) — `check-state.sh:1525-1526`'s
  INV-16 message interpolates `run_id` and the step id as bare strings, so the accepted DEC-85
  Bash-write route can spoof or erase the audit line reporting it. One-line remedy (`!r`). Detail:
  `runs/2026-09-09-10-panel-validator/digest.md`.
- Q2 (not blocking, main session): **CF-3** (code, `low`) — `abff2a84`, a FEAT-56 `plan.yaml` station
  flip, is this branch's root commit and merges with this PR, untracked by any REQ or D. Lead
  recommends ACCEPT and record in the ship note; excising it rewrites history beneath a signed pin. I
  concur; the call is the operator's.
- Q3 (not blocking, main session): **CF-2** severity CONTESTED — qa `med`, code `info`, lead `low`.
  `check-state.sh:1590`'s literal-`lead` at-rest exemption has no test able to report RED; the remedy
  is a test inside the carve-out, so no squad may close it.
- Q4 (not blocking, main session, harness defect): the `lead` schema declares no `code_grade`, so a
  lead hosting a code-grading run cannot declare it without tripping this feature's own
  undeclared-key rejection. My c9 dispatch demanded it — my error, and Q-B3 repeats it. Should
  `PASSTHROUGH['lead']` gain it as an unverified roll-up?
- Q5 (not blocking, main session, DEC-174): **CF-4** (ui, `low`) — the `schema_version` downgrade
  branch renders a raw Python `None` in the omitted-on-update edge case; `T-06` has no such case.
- Q7 (not blocking, main session): the 3 complete + 2 partial strict-version predicate spellings
  (`check-domain.sh:1594-1597`, `:1761-1764`, `check-state.sh:1487-1489`) want one
  `is_strict_schema_version()` home. Carried as already-known, NOT re-raised this cycle.
- F-QA-1 (not blocking, main session): `T-05` declares `change_type: logic` while DEC-212's
  `touches_config_shape` arguably covers `run-state-schema.json`, making `integration` a floor line.
- Residual non-gating risks, detailed in the c9 panel digest: the DEC-85 Bash-write bypass (CF-1's
  precondition); F2's runtime residual; `check-domain.sh`'s `_no_parser` bootstrap early return.
  Coverage gap: the `run-state-schema.json` guards are ARGUED fail-closed, not mutation-proven. Also
  standing: the INV-26 card/plan mismatch and the per-persona worktree-claim guard.
