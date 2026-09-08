# QA c7 — gate re-run + adjudication, merge-gate.py @ 894adc0f

Fresh re-derivation (c6 read only as hypothesis; nothing copied forward without re-measurement).
Worktree is currently at `5d672120`, a re-pin commit directly on `894adc0f` with a bare
`feature.json` housekeeping diff (`git diff --stat 894adc0f HEAD` → 1 file, `feature.json`, no
diff on any code/test surface) — so the pin's content is exactly what is on disk; no checkout
performed, none needed.

## BLUF
**matrix_ok: true.** unit (33 files) and integration (50 files) both exit 0 with non-empty
discovered sets; `test-merge-gate.py` itself: 19/19 `ok`, exit 0. The DEC-138 stderr line **is**
misleading when a receipt is held during a remote-read failure (severity **low**, wording only, no
decision wrong) — reproduced verbatim below, and **confirmed pre-existing** at `894adc0f^` by direct
`git show`, not by trusting the c6 note. Adequacy: the branch's **own** would-be record being
non-dict/unparseable/unreadable is bound by **zero** committed cases — hand-verification only, same
gap c6 named. On the mutation-proof question I **diverge from c6**: replaying the exact parent-shape
sentinel mutation against both L102-116 and L136-148 reddens **both** cases, not one — see §3.

## 1. Matrix re-run
T-05 (`merge-gate.py`/`.sh`, `.claude/settings.json`, `settings.snippet.json`, `harness-hooks.ts`),
`plan.yaml:873` → `change_type: feature`. Floor: `.harness/harness.json:191-195`, `feature.always`
= `[unit, integration]`.

| kind | cmd | exit | discovered |
|---|---|---|---|
| unit | `env -u HARNESS_AGENT_TYPE bash .agents/skills/harness/bin/run-unit-tests.sh --kind unit` | 0 | 33 files, all `PASS`, no FAIL/ERROR-as-failure lines |
| integration | same, `--kind integration` | 0 | 50 files, all `PASS`; `test-merge-gate.py` exit 0, 19/19 `ok`, `ALL PASSED` |

Both env-scrubbed per repo Expertise G-07 (`HARNESS_AGENT_TYPE` unset — otherwise
`test-plan-merge.py` false-fails). Non-empty discovered sets on both kinds — not an exit-0-over-
nothing false pass. **A gate that ran and passed, honestly.**

## 2. DEC-138 stderr adjudication — reproduced and pre-existence established myself

`merge-gate.py:135-147` (pin): when `document is None` (no attributable record) **or** when
`entry in {opened, not-applicable, recovered-terminal}` (a receipt exists and is **held**), and the
gh-resolution `failure` is truthy, **both branches print the identical f-string**:
`"...and the local branch {branch} owes no build-entry receipt; allowing it..."` (lines 137 and
146, byte-identical string).

**Repro** (disposable `/tmp` fixture, script not committed): built a project root with
`github.sync=true`, `github.repo` pinned, one feature `FEAT-9001-fixture-non-era` on
`branch=feature/test` with `github.build_entry="opened"` (a **held** state, not owed), then:

```
echo '{"tool_input": {"command": "gh pr merge 7"}}' \
  | HARNESS_PROJECT_DIR=/tmp/qa_repro GH_BIN=/nonexistent/gh bash merge-gate.sh
```
exit 0, stdout empty (allow, no deny emitted), **stderr verbatim**:
```
merge-gate: could not verify this merge - the head branch could not be resolved through gh ([Errno 2] No such file or directory: '/nonexistent/gh') and the local branch feature/test owes no build-entry receipt; allowing it, because GitHub is a mirror and never a gate (DEC-138).
```
The allow decision is correct (a held receipt should not block); the **claim "owes no build-entry
receipt" is false** — a receipt exists and is merely unconfirmed pending gh recovery. Wording
defect, not a gating defect.

**Pre-existence, established directly** (not accepting c6's claim): 
`git -C <worktree> show 894adc0f^:.claude/skills/harness/bin/merge-gate.py | grep -n "owes no build-entry receipt"`
→ **2 hits**, at the parent's lines 141 and 150. Read the surrounding parent code
(`894adc0f^` lines 120-152): the parent's `entry in {opened, not-applicable, recovered-terminal}`
branch (its line ~149-150) contains the **identical** f-string in the identical held-receipt
position. This is not something the decision-table rewrite touched — the rewrite's only change in
this file is `feature_for`'s return shape (2-tuple vs. the parent's 3-tuple with the `unusable`
sentinel) and the `document is None` dispatch in `main()`; the held-branch print block is untouched
prose carried forward verbatim. **Verdict: pre-existing, not introduced at this pin. No decision is
wrong here — only a diagnostic string is imprecise. Severity: low.**

## 3. Adequacy — what the suite binds, what it does not, and a correction to c6

Read the full `tests/integration/test-merge-gate.py` (150 lines, 19 cases) directly. Every
malformed-record fixture in the file (`FEAT-9002-unrelated-malformed`, `json.dump([])`) is planted
under a **different** feature directory than the branch-matching one, and/or the matching record's
own `branch` field is deliberately set to `"other"` before the malformed record is added
(L106-121, L136-148). **No case ever makes the branch's OWN candidate record itself non-dict,
unparseable, or unreadable.** That state — the branch's own would-be record failing
`isinstance(document, dict)` or `json.load` — is bound by **zero** committed cases; only by
hand-verification (mine, and independently c6's, agree it allows correctly when constructed by
hand in `/tmp`). This is a real coverage gap in the strict sense (nothing pins it), though not
a live regression risk today, because the code path treats "own record unusable" identically to
"own record absent" (both fall through to `continue`/no-match) — the *design* does not distinguish
them, so there is no missing *decision*, only a missing *pin* of that decision.

**Which case carries the cycle-5 sentinel-regression weight — measured, not inferred from c6:**
I reinstated the exact parent-commit (`894adc0f^`) shape of `feature_for` (3-tuple return with the
`unusable` sentinel, plus `main()`'s `if unusable: deny(...)` branch) verbatim — confirmed
byte-identical against `git show 894adc0f^:...` — as a diagnostic-only mutant under
`/tmp/qa_mutant/merge-gate.py` (never written into any tracked path; `check-domain` correctly
refused my one attempt to write it into a scratch git worktree, confirming AUTHOR-NOTHING held).
Replayed both of the test file's two changed cases against it with a driver script that reproduces
their exact fixtures (`/tmp/qa_mutant/drive.py`):

| Case | Under the reinstated sentinel | c6's claim | My measurement |
|---|---|---|---|
| L102-116 `gh outage with no matching feature allows` (assert `d is None and "could not verify" in stderr`) | `d='deny'`, reason `"...Repair the malformed feature record..."` | claimed does NOT redden by itself | **REDDENS** (`d` flips `None`→`'deny'`) |
| L136-148 `no-record branch ignores unrelated malformed record` (assert `rc==0 and d is None`) | `d='deny'`, same reason | claimed this is the one that carries the weight | **REDDENS** (same) |

**I diverge from c6 here.** c6 asserted L102-116 does not discriminate because "MATCH is already
`no` via REMOTE=fail-cmd and the sentinel would only change the reason text when `document is
None`" — but the sentinel changes more than the reason text: it changes `main()`'s **branch**
(`if unusable: deny(...)` fires instead of falling through), which flips the *decision*, not just
its wording, precisely because in this fixture `document is None` is true (MATCH=no) **and**
`unusable` is true (the planted `FEAT-9002` record is `[]`). c6's own case-table lists this case as
"BOUND" against the historical pair, and my measurement agrees it is bound — just for a stronger
reason than c6 gave. **Both L102-116 and L136-148 independently redden under the exact reverted
sentinel; neither is a decoy.** (c6's F2 finding — "L102-116 does not discriminate by itself" — does
not hold under direct replay and should not be carried forward.)

## Coverage gaps (Phase 1 vs Phase 2)
- Own-branch record non-dict/unparseable/unreadable: no committed case (see above). Recommend a
  case using the exact pre-fix fixture shape (own record `[]`) the rewrite's diff dropped.
- REMOTE=fail × RECEIPT=held (the DEC-138 wording defect's precondition): no committed case exists
  that exercises the held-branch print path under a gh failure; the wording defect surfaced only by
  hand construction, both this cycle and last.

## Findings
- **F1 (low, pre-existing at 894adc0f^, confirmed by `git show`, not by inference):** duplicated
  f-string at `merge-gate.py:137,146` misreports "owes no build-entry receipt" when the true state
  is a held (unconfirmed) receipt during a gh outage. Diagnostics-only; the allow decision itself is
  correct in every case I or c6 constructed. Not gating.
- **F2 (info, correction of c6's F2):** the historical-pair binding table stands (all four named
  pairs bound), but c6's specific claim that L102-116 "does not discriminate by itself" is
  **not reproducible** — direct replay of the exact parent-shape mutant reddens it independently of
  L136-148. Both cases are independently load-bearing for the cycle-5 sentinel-regression class.
- **F3 (info):** own-branch-record-malformed remains suite-uncovered (repeat of c6's finding,
  independently re-confirmed by reading the fixtures myself). Not gating — the code's own design
  makes "own record unusable" behave identically to "own record absent," so no decision is
  unverified, only unpinned.

## SC evidence
Gate-only / audit dispatch; no SC text assigned to me this cycle. Matrix result and adequacy
findings above are the deliverable.

## Historical digest envelope diagnostics

Measurement only — neither digest edited; repair belongs to the validator lead.

**Command 1:**
```
python3 .../.agents/skills/harness/bin/validate-digest.py lead \
  .../features/BUG-1309-mirror-build-entry/runs/2026-09-07-03-validator/digest.md
```
Exit code: **1**
Stdout/stderr verbatim:
```
VERDICT: BLOCKED (contract violation)
  - only the optional fable-advisor may be recorded as skipped; mandatory members must carry their verdict.
  - only the optional fable-advisor may be recorded as skipped; mandatory members must carry their verdict.
```

**Command 2:**
```
python3 .../.agents/skills/harness/bin/validate-digest.py lead \
  .../features/BUG-1309-mirror-build-entry/runs/2026-09-06-panelc1-validator/digest.md
```
Exit code: **1**
Stdout/stderr verbatim:
```
VERDICT: BLOCKED (contract violation)
  - no VERDICT: line — this is a contract violation, not a verdict of any kind.
  - no DIGEST: block.
  - no artifact: path.
  - DIGEST has no headline: — the orchestrator routes on this.
  - missing 'team' — every field is required; write `[]` if there are none. An absent field is ambiguous; an explicit empty one asserts you looked.
  - missing 'steps_run' — every field is required; write `[]` if there are none. An absent field is ambiguous; an explicit empty one asserts you looked.
  - missing 'cycles_used' — every field is required; write `[]` if there are none. An absent field is ambiguous; an explicit empty one asserts you looked.
  - missing 'members' — every field is required; write `[]` if there are none. An absent field is ambiguous; an explicit empty one asserts you looked.
  - missing 'must_fix' — every field is required; write `[]` if there are none. An absent field is ambiguous; an explicit empty one asserts you looked.
  - missing 'branch' — every field is required; write `none` if genuinely not applicable. An absent field is ambiguous; an explicit empty one asserts you looked.
  - missing 'escalations' — every field is required; write `[]` if there are none. An absent field is ambiguous; an explicit empty one asserts you looked.
  - missing 'sc_status' — every field is required; write `[]` if there are none. An absent field is ambiguous; an explicit empty one asserts you looked.
  - missing 'open_questions' — every field is required; write `[]` if there are none. An absent field is ambiguous; an explicit empty one asserts you looked.
  - missing 'files_touched' — every field is required; write `[]` if there are none. An absent field is ambiguous; an explicit empty one asserts you looked.
  - missing 'expertise_update' — every field is required; write `[]` if there are none. An absent field is ambiguous; an explicit empty one asserts you looked.
```

Both digests are **BLOCKED (contract violation)** under the current validator, for distinct
reasons: run `2026-09-07-03-validator`'s digest has a member incorrectly recorded as skipped
(only `fable-advisor` may be); run `2026-09-06-panelc1-validator`'s digest is missing the entire
YAML envelope (no `VERDICT:`, no `DIGEST:` block at all — every required field flagged absent).
Neither was touched by me.
