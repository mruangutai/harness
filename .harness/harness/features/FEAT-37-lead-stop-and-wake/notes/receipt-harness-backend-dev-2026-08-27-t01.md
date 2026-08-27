# Receipt — harness-backend-dev — FEAT-37 T-01

## Task

Add `.claude/skills/harness/bin/test-lead-stop-and-wake.py`, a stdlib-only Python 3 guard test
for three not-yet-shipped FEAT-37 invariants (`playbook`, `bound`, `coverage`), and register it
in `run-unit-tests.sh`'s `UNIT_SCRIPTS` array.

## Task verify — run from worktree root, literal output

```
$ cd "$(git rev-parse --show-toplevel)"
$ python3 .claude/skills/harness/bin/test-lead-stop-and-wake.py --self-check; sc=$?
$ python3 .claude/skills/harness/bin/test-lead-stop-and-wake.py --group playbook; pb=$?
$ python3 .claude/skills/harness/bin/test-lead-stop-and-wake.py --group coverage; cv=$?
$ .claude/skills/harness/bin/run-unit-tests.sh --check-kinds; ck=$?
$ echo "selfcheck=$sc playbook=$pb coverage=$cv checkkinds=$ck"
selfcheck=0 playbook=1 coverage=1 checkkinds=0
T01_PASS
```

`--self-check`: all six variants (A FAIL / B PASS / C FAIL / D FAIL / E FAIL / F FAIL) matched
their required verdicts — `SELFCHECK PASS` on every line. `--group playbook` exits 1 (all 9
region/window cases fail against the real `harness-team/SKILL.md` — nothing has shipped).
`--group coverage` exits 1 (`case_index_row`, `case_entry_heading`, `case_entry_scope` all fail —
DEC-201 still names only the orchestrator). `run-unit-tests.sh --check-kinds` exits 0 (drift
detector and kind cross-check agree). **`task_verify: pass`** — the block requires exactly this
combination and got it.

`--group bound` (not in the verify block, required to exist by dispatch): ran clean, two sites
(`DECISIONS.md`, `inflight_registry.py`), each with a floor PASS (occurrences found, never
graded against an empty set) and per-occurrence FAILs — both DECISIONS.md occurrences (lines
6869, 6870) and the one inflight_registry.py occurrence (line 339, which the once-only
alternation matches twice on the same line — disambiguated with a trailing `_1`/`_2` index so
the two case names don't collide) lack a qualifier and sit outside a STRUCK entry. Exit 1,
consistent with nothing having shipped.

Full unit suite (`run-unit-tests.sh --kind unit`) run for regression sanity: exit 1 overall
(expected — the new test's whole-file run fails by design), but the runner's per-script summary
shows `FAIL test-lead-stop-and-wake.py` as the *only* failing script among all 27 registered
unit scripts; the other 26 (including `test-orchestrator-playbook.py`) all print `PASS`.

## Anchors re-derived at HEAD (branch `feat/FEAT-37-lead-stop-and-wake`, base `1d8ad0a`)

- `UNIT_SCRIPTS` array: **line 30** of `run-unit-tests.sh`, not line 17 as the intent's stale
  8fc87f8 pin says (already flagged in the dispatch). Found by array name, appended
  `"test-lead-stop-and-wake.py"` immediately after `"test-orchestrator-playbook.py"`, before
  `"test-omp-hooks.py"`. Nothing else in that file changed.
- `.claude/skills/harness-team/SKILL.md`: confirmed 240 lines at HEAD (matches dispatch).
  `**d. ` line is still line 97, `**e. ` line still 112, `Until every step is terminal` still
  line 81 — unchanged from the intent's 8fc87f8 measurement; `grep -n "^\*\*d\. \|^\*\*e\. "`
  shows exactly the two expected lines, no earlier false match.
- `.harness/harness/docs/DECISIONS.md`: 7276 lines at HEAD (matches dispatch's re-measurement,
  not the intent's stale 6968-for-DEC-201). DEC-201 heading is still at line 6968 and DEC-202 at
  7063 (region: 6968–7063 exclusive) — coincidentally unmoved even though the file grew
  elsewhere. `lead` occurs exactly 3 times in that span (lines 6979, 7051, 7059 relative — all
  incidental, none co-occurring with an end-turn phrase in the same sentence), matching the
  dispatch's claim.
- **Bound-site once-only occurrence count drifted from the intent's own numbers and I did not
  trust them**: intent (re-plan pin) names DECISIONS.md lines 6869, 6870 **and 6872**. At HEAD,
  `grep -noE "fires at most once|fires ONCE|fires once|refusal fires once|one-correction-round"`
  finds only **two** occurrences, lines 6869 and 6870. Line 6872 in the current file reads "no
  once-only bound" — not a member of the alternation the task itself defines. My detector uses
  the two it can prove, not three; this is correctly reflected in the test's own two
  `case_occurrence_DECISIONS.md_*` results.
- DECISIONS-INDEX.md DEC-201 row: found by `^- DEC-201\b` marker (never by the intent's stale
  "line 219" claim, though it still happens to be line 219 at HEAD — verified, not assumed).

## Files touched

- `.claude/skills/harness/bin/test-lead-stop-and-wake.py` (new)
- `.claude/skills/harness/bin/run-unit-tests.sh` (one array entry appended)
- this receipt

## Scope fence — respected

Did not edit `.claude/skills/harness-team/SKILL.md`, `.claude/skills/harness/SKILL.md`,
`inflight_registry.py`, or anything under `.harness/harness/docs/`. Read all of them to build
detectors against. No group in the new test reads `.claude/skills/harness/SKILL.md`; the
"orchestrator" group and its verify line were never added (T-03/D-12/#903).

## Notes for later tasks (not edits, just observed)

- T-02 will need to add the inoculation paragraph strictly inside the `**d. `→`**e. ` region
  (case1–case7) *and* two short insertions outside it: right after "Until every step is
  terminal, or you halt:" (case8, needs an across-turns alternation AND `state.yaml` within 400
  chars) and right after "**e. Collect returns." (case9, needs an on-waking alternation within
  400 chars).
- T-05/T-06 need `DECISIONS-INDEX.md`'s DEC-201 row (right of `::`) and `DECISIONS.md`'s DEC-201
  heading to name the lead tier, plus one sentence of the entry body co-occurring lead-language
  with an end-turn phrase — the existing three incidental "lead" mentions in the body do not
  satisfy this and must not be mistaken for coverage.
- The `bound` group's real-file state (2 DECISIONS.md occurrences, 1 inflight_registry.py
  occurrence, all failing today) is pre-existing content, not something this task's scope
  includes fixing — flagging for whichever task in this feature or a follow-up owns qualifying
  or exempting them.

## Digest

```yaml
VERDICT: PASS
DIGEST:
  headline: test-lead-stop-and-wake.py guards FEAT-37's playbook/bound/coverage invariants and correctly fails both required groups pre-ship
  tests_added: 1
  suite: pass
  task: T-01
  task_verify: pass
  blocked_on: none
  open_questions: []
  files_touched:
    - .claude/skills/harness/bin/test-lead-stop-and-wake.py
    - .claude/skills/harness/bin/run-unit-tests.sh
    - .harness/harness/features/FEAT-37-lead-stop-and-wake/notes/receipt-harness-backend-dev-2026-08-27-t01.md
  expertise_update: []
artifact: .harness/harness/features/FEAT-37-lead-stop-and-wake/notes/receipt-harness-backend-dev-2026-08-27-t01.md
```
