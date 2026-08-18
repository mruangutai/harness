# QA — FEAT-23 final pass — distributive-claim sweep and apply-bounds check

Pin confirmed: `git rev-parse feat/FEAT-23-ship-flow-fixes` = `afc8cfd97ac6ced14fc1d40372336b972f84733e`. All reads below are `git show afc8cfd:<path>`. **Matrix not re-run this pass** — the prior gate at `83e769b` stands (PASS, `matrix_ok: true`, `severity_max: low`, one applied-and-killed mutant, per `notes/ship-review-2026-08-17-13.md`).

## Probe 1 — SC-05 per-section, at `afc8cfd`

`.claude/skills/harness-simplify/SKILL.md`, section ranges by `## ` heading line to next heading:

| Angle | Lines | `plan surface` | `code surface` |
|---|---|---|---|
| REUSE | 37–48 | 1 (:41) | 1 (:44) |
| SIMPLIFICATION | 49–61 | 1 (:53) | 1 (:57) |
| EFFICIENCY | 62–78 | 1 (:73) | 1 (:76) |
| ALTITUDE | 79–100 | 1 (:90) | 1 (:94) |

Matches your prediction exactly. All four 1/1. SC-05 is currently true.

## Probe 2 — distributive-claim sweep

**Method anchor, run first.** File-global `grep -c` at `490c37c` (pre-fix): `plan surface` = 4, `code surface` = 4 — the file-global total looks fine and masks that ALTITUDE (lines 79–93 at that commit) has **zero** of either phrase in its own range. A per-section count reproduces the known defect (ALTITUDE 0/0). Confirmed the sweep method would have caught B-5's instance before trusting any null result below.

**Addendum to B-5, not a new instance — reporting because it sharpens the existing row.** `plan.yaml` T-02's `verify:` (unchanged by the SC-05 fix commit `2cba9fb`, which touched only `SKILL.md` — confirmed via `git show 2cba9fb --stat`) still reads:
```
grep -qF "plan surface" "$S" || { echo "T-02: the plan-surface variant is absent"; exit 1; }
grep -qF "code surface" "$S" || { echo "T-02: the code-surface variant is absent"; exit 1; }
```
File-global, existence-only — the same shape B-5 already names. This is T-02's own instance, the one the dispatch says not to re-file; I looked because the dispatch also asked whether the *fix* was content-only or whether the gate itself was hardened. It was content-only: the fix commit touched `SKILL.md` alone (`git show 2cba9fb --stat`), and the verify clause that let ALTITUDE's gap through is byte-identical to its pre-fix form. **At `afc8cfd` nothing is false** — Probe 1's table shows all four sections 1/1 — so this is not a live gap and not blocking on its own; it is evidence that B-5's remedy has not yet been applied anywhere, including to the clause that caused it. Note also: T-02's `verify:` sits inside a **signed, approved** `plan.yaml` — patching it is an edit to a signed plan of a done feature, which needs operator re-signature (the same logic the ship review already applied to B-14). Not something a downstream agent can quietly fix.

**Finding — genuinely new instance. SC-03 quantifies over four gh-sync behaviours; T-01's `verify:` (the cited automated/integration evidence) names only two of them.** SC-03: "the milestone still closes, an adopted parent is still left open, a created parent still closes, and `--body-file` still posts exactly once." T-01's `verify:` explicitly greps only:
```
"ok    ship closes the milestone regardless of parent origin"
"ok    ship leaves an adopted parent open"
```
It does **not** name `"ship closes a created parent completed"` (present at `test-gh-sync.py:760`) or `"ship --body-file posts once"` (present at `:831`) — both exist and currently pass, so SC-03 is currently true, but T-01's verify relies only on the file-wide `grep -E "^FAIL"` catch-all to protect them. That catch-all catches a case that *runs and fails*; it does not catch a case that is silently deleted or renamed during a future refactor of `gh-sync.py`. **Scenario:** a later change to `_apply_parent_rule` or the body-file post breaks "created parent still closes" and, in the same edit, the corresponding test case is deleted rather than left red (e.g. "simplified" away, or renamed without the exact label). T-01's verify still reports `T-01 GREEN` (rc 0, no `^FAIL` line, both named `ok` lines still present), and SC-03 stays marked `verify: automated evidence: integration` while two of its four quantified sub-claims go unchecked. **Severity: medium — advisory, not a live failure today** (both cases exist and pass now). Remedy: add the two missing case labels to T-01's `verify:` grep list, matching the pattern already used for the other two. Same caveat as above — this is a signed `plan.yaml`, so the remedy is a re-signature item, not a quiet fix.

**Swept and found clean (with what the sweep covered):**
- **T-03 / T-06 anchor checks** (`grep -cF "$anchor" ... [ "$n" = 1 ]`) are uniqueness claims about a whole file, not "each of N items" claims — a file-global count is the *correct* method for "occurs exactly once," so these are not instances of the defect class.
- **T-04**, DEC-195 / DEC-196: two separate `grep -qE "^## DEC-19[56] "` conjuncts, one per decision, each independently checked — genuinely per-item, not a merged count. SC-09's "Both decisions … recorded" is bound this way correctly.
- **T-05**, the seven `PASS ...` case-label conjuncts: each is a byte-exact, case-unique label. Checked directly, not taken from plan intent prose (P-01) — `test-board-station.py:139-148` shows case 1 first asserts `r.returncode == 0 and "board-station: #326 -> Plan" in r.stdout` under the label T-05's verify greps, then a **second**, separately-named check (`"the field-set invocation actually carries the issue number and the station"`) asserts `edit_calls` contains `OPT_PLAN` and `ITEM_326` — the fake's actual argument values, not just that a call happened. That second check is not itself named in T-05's verify grep list, but `check()` prints a `FAIL` line on any failing case (`:31-36`) and T-05's verify has `say | grep -E "^FAIL" && exit 1`, so a regression in the argument-value assertion is still caught, just not individually named. Per-item and content-checked overall. SC-10 ("for every failure class") is bound by the seven distinct branches.
- **SC-06** ("skill and both playbook steps name no outside file/plugin") is `verify: inspection`, not automated — T-02's `verify:` does carry an automated absence-check for `code-simplifier` on the skill file alone, but T-03's `verify:` (covering the two playbook files) carries no such automated check. Since SC-06 declares itself `inspection`, this is not a false-automated-corroboration risk, only worth naming: the automated coverage of SC-06 is partial (1 of 3 named surfaces), and a reader relying on "verify: inspection" already knows to check the other two by hand.
- No other `each` / `every` / `all four` / `both` / `for every` language appears inside any task's `verify:` block (swept via `awk` isolating each `verify: |` block, then grepped case-insensitively) beyond the instances above and one prose string inside an error message (T-05, not a check condition).
- DEC-195/DEC-196 prose: "Both bounds are stated authoritatively in `harness-simplify/SKILL.md`" is itself the subject of Probe 3, not a separately-verified distributive claim — see below.

## Probe 3 — the two apply bounds, at `afc8cfd`

1. **Present**, in `.claude/skills/harness-simplify/SKILL.md`, own voice, under `## Applying what comes back`:
   - `:121` — **"The apply may not delete or weaken an assertion."** followed by the qa-gate-already-PASSed rationale.
   - `:125` — **"The apply has a ceiling of one fix."** followed by the no-`max_cycles`-of-its-own rationale.
2. **Reachable by a reader of the skill alone.** Both are full sentences in the skill's own bullet/paragraph voice, not cross-references to `DECISIONS.md` or `harness/SKILL.md` — a reader who opens only this file learns both bounds and their reasons without needing either other document.
3. **Comparison against `.claude/skills/harness/SKILL.md`** (re-located at `:59–75`, not `:68–73` — the file has shifted since the dispatch's estimate):
   - Trigger: both gate the apply on "once the matrix is green" / "the qa gate has already PASSed on test-matrix judgement and coverage adequacy" — identical condition, worded near-identically ("nothing re-assesses [that] afterwards" in both).
   - Fail path: both say the same finding becomes "a backlog row, never an apply" (delete-or-weaken bound); both say "revert" then "file the finding as a backlog row" (ceiling bound) — `harness/SKILL.md:70–71` compresses to "revert and file the finding," `harness-simplify/SKILL.md:126` says "revert the apply and file the finding as a backlog row" — same action, `harness/SKILL.md` is terser but not narrower.
   - Reason: both cite "this is the only permanent build step with no `max_cycles` of its own" for the ceiling bound, word-for-word close.
   - **Verdict: agree.** No contradiction, neither is stricter — `harness/SKILL.md` is a compressed restatement of the same two rules, not an independent or looser formulation.

## Overall

At `afc8cfd` everything measured is correct: Probe 1's four sections are 1/1, Probe 3's two bounds are present, reachable, and non-contradictory. Probe 2 turns up one genuinely new instance (SC-03/T-01, medium, advisory — both protecting cases exist and pass today, just not individually named) and one addendum to the already-filed B-5 (T-02's own verify clause was never patched after the SC-05 fix — content-only fix, gate unchanged). Neither is a live failure at the pin, and both remedies are edits to a **signed** `plan.yaml`, so neither is mine to apply — they route back as backlog rows for the operator, same as B-5/B-6.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Nothing false at afc8cfd. One new advisory (SC-03's verify names 2 of 4 quantified behaviours) and one addendum to B-5 (T-02's verify was never patched — the SC-05 fix was content-only)."
  suite: pass   # prior gate's value at 83e769b; NOT re-run this pass — delta since 83e769b is the other member's job
  failures: 0
  matrix_ok: true   # prior gate at 83e769b, not re-measured this pass
  kinds: []   # no test-matrix run performed this pass; see matrix_ok note
  severity_max: medium
  coverage_gaps:
    - "T-01 verify (plan.yaml) — SC-03 names only 2 of 4 quantified gh-sync behaviours by label ('created parent still closes' and '--body-file posts once' exist and pass at test-gh-sync.py:760,:831 but are unnamed, protected only by a catch-all FAIL grep that cannot see a deleted case)"
    - "T-02 verify (plan.yaml) — still file-global grep for 'plan surface'/'code surface' after the SC-05 fix (2cba9fb touched SKILL.md only); addendum to already-filed B-5, not currently false"
  sc_evidence:
    - { id: SC-05, test: ".claude/skills/harness-simplify/SKILL.md (per-section count, this artifact's Probe 1 table)" }
    - { id: SC-03, test: ".claude/skills/harness/bin/test-gh-sync.py:760 (ship closes a created parent completed), :831 (ship --body-file posts once) — currently green but unnamed by T-01's verify" }
  open_questions:
    - { id: Q1, question: "B-5's remedy (per-section verify) was never applied to T-02's own signed plan.yaml clause — apply retroactively (needs re-signature) or accept forward-only (future features get the lesson, this one's gate stays as-is)?", blocking: false }
    - { id: Q2, question: "Add the two missing SC-03 case labels to T-01's verify as a hardening follow-up (also a signed-plan edit needing re-signature), or accept the current catch-all as sufficient since both cases pass today?", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-23-ship-flow-fixes/notes/qa-2026-08-17-14-finalpass-validator.md
```
