# Panel record — cycle 6 transcribed into plan.yaml

**Landed.** `plan-merge.py set-panel` **exit 0** replaced the plan's top-level `panel:` key —
which recorded cycle 4 (`verdict: FAIL`, `severity_max: high`) — with cycle 6's record:
`last_run: 2026-09-01-10-validator`, `cycle: 6`, `reviewed_at: 047f6914`, `severity_max: med`,
`verdict: PASS`, **16 findings (3 med / 11 low / 2 info)**, all three readers `ran`.
`approval.status` is untouched at `pending`; `status: plan`. Nothing outside `panel:` moved.
The plan's own last panel word is now PASS, so the sequencing hazard the validator raised as
Q2 is closed ahead of `sign-approval`.

This was a **transcription, not an adjudication**. No severity was re-graded, no finding was
added, dropped, merged or reworded — including the lead's 146-vs-117 reconciliation (`low`, the
scope reader's grade, not the advisor's `info`), which stands as authored.

## Source

`runs/2026-09-01-10-validator/digest.md`, the fenced block under `## panel value — cycle 6`.
Read end to end (the block spans two read windows) and compared **structurally**, not by eye:
`/tmp/feat48_panel_c6.py` `safe_load`s the digest's fenced block and my draft and asserts
equality of every scalar, the whole `readers:` list and all 16 findings, permitting exactly one
added key (`history`). Output: `VERBATIM CHECK OK — 16 findings, 3 readers` /
`severity counts: {'med': 3, 'low': 11, 'info': 2}`. After the id splice it reloads the final
file and re-asserts each finding minus its `id` is identical to the source finding.

The one addition the lead could not make is `history:`, a sibling scalar recording that
cycles 0-3 and 5 predate the `set-panel` route (their records live in their run digests and, for
cycle 5, `notes/panel-value-c5.yaml`) and that cycle 4's was the only panel value the plan ever
carried.

## Finding identity

**Hashed on the recorded strings, never paraphrases.** The driver reads each finding out of the
draft and passes `f["reader"]` and `f["summary"]` to
`panel_findings.py id` as an **argv list via `subprocess.run`** — no shell, so no quoting could
alter an em dash or apostrophe — one invocation per finding, 16 in total. The `reader:` value is
hashed as it appears on the finding (`code-reviewer`, not the `readers:` step id `scope`).
Distinctness checked by cardinality, printed: `distinct ids: 16 of 16 -> True`, and re-confirmed
against the applied plan: `len(set(ids)) == 16 | == 16: True`.

| id | severity | reader |
|---|---|---|
| `PF-5f4c0650bd59a2beac41e3a2e55b3408` | med | code-reviewer |
| `PF-e8d2d0c282876f52fbc822c54ad26369` | low | code-reviewer |
| `PF-963368450681cd9ef3131c2438dfb1b6` | low | should-not-exist |
| `PF-671c55da77e57d73d2e1c91da9317259` | info | should-not-exist |
| `PF-e69c81bad62702c3e661936347e706c4` | med | goalcheck |
| `PF-e2842b1b847c003d6ef308c31b0f40b2` | med | code-reviewer |
| `PF-507dd4d0868181ec33b6dcf486fdf657` | low | should-not-exist |
| `PF-0f52ff857acf41541231b508573db53d` | low | goalcheck |
| `PF-42e0aaa48a8a344a99680c58b40a836d` | low | goalcheck |
| `PF-498f50089a28a6bd78796dc6510bc117` | low | goalcheck |
| `PF-4241dce0871070cb4c75a9ad0f1f8f8a` | low | goalcheck |
| `PF-ae8a56b4f178f0a8df662ba275038636` | low | goalcheck |
| `PF-bb123e7e86e19b1cd849610f39ce47a2` | low | code-reviewer |
| `PF-77c77b2b4e62888b35293e566448f58c` | low | goalcheck |
| `PF-6e5e4d2b22b169d401d2bdcbab2425c1` | low | code-reviewer |
| `PF-3e841eea447e4dcb511236d5eb9fda8d` | info | should-not-exist |

## Evidence

`set-panel`:

```
PANEL cycle 6 -> …/FEAT-48-parallel-safe-suite/plan.yaml
APPLIED …/FEAT-48-parallel-safe-suite/plan.yaml
EXIT=0
```

The acceptance one-liner, against the applied plan:

```
2026-09-01-10-validator 6 med 16 3
['info', 'low', 'med']
{'status': 'pending', 'approved_by': None, 'date': None} plan
['PF-5f4c0650bd59a2beac41e3a2e55b3408', 'PF-e8d2d0c282876f52fbc822c54ad26369', 'PF-963368450681cd9ef3131c2438dfb1b6']
```

Shape, read back from the applied file:

```
readers: [('goalcheck', 'ran'), ('scope', 'ran'), ('should-not-exist', 'ran')]
len(set(ids)) == 16 | == 16: True
all have id/severity/disposition: True
sev: {'med': 3, 'low': 11, 'info': 2}
panel keys: ['cycle', 'findings', 'history', 'last_run', 'readers', 'reviewed_at', 'reviewed_at_note', 'severity_max', 'transcription_rule', 'verdict']
approval.status: pending
```

INV-32 (`check-state.sh:455-527`) is satisfiable by inspection: `last_run` non-empty, `findings`
a list, all three reader ids present with `status: ran`, every finding carrying
`id`/`severity`/`disposition`, and **no severity outside `{info, low, med}`** — so no
open-and-un-overruled finding becomes a hard violation when `approval.status` flips.

`git diff --stat`:

```
 .../features/FEAT-48-parallel-safe-suite/plan.yaml | 278 ++++++++++++++-------
 1 file changed, 183 insertions(+), 95 deletions(-)
```

Diff hunk ranges (`-U0`), all three inside `panel:` and hunk-headed `panel:`:
`@@ -1335,7 +1335,20 @@`, `@@ -1343,13 +1356,22 @@`, `@@ -1357,75 +1379,141 @@`.
`panel:` is the plan's last key at line 1334 and the final hunk ends at the new EOF (1519), so
every changed line is inside the replaced mapping and nothing before 1334 moved.
`git status --porcelain` shows one modified tracked file, `plan.yaml`. It also shows one
**untracked** file, `notes/review-harness-code-reviewer-planpanel-c6.md` — the scope reader's
own artifact, not mine, present before this write (the dispatch's "working tree clean" refers to
tracked state).

Document integrity around the whole-mapping replace, from T-02's `verify:` derivation half only
(`plan.yaml:465-475`, `:496`) — no subprocess, no poll thread, no test file executed:

```
absorbed ['.claude/skills/harness/bin/test-bash-write-guard.py']
run_set ['test-bash-write-guard.py', 'test-check-state.py', 'test-feature-worktree.py']
absorbed non-empty: True | run_set size: 3
```

That matches the validator digest's report of the same derivation at `047f6914` (`absorbed`
non-empty, `run_set` the three files), so the replace disturbed neither `tasks:` nor the loader's
view of the document.

Scratch inputs live at `/tmp/FEAT-48-panel-value-c6.yaml` (the applied value),
`/tmp/FEAT-48-panel-value-c6-draft.yaml`, `/tmp/feat48_panel_c6.py`, `/tmp/feat48_t02_deriv.py`.
`/tmp` was not refused.

## Open — for the tier above, not for me

- **Q2 is now closed by this write**, but the guard gap it named is not: `plan-sign-gate.py`
  still does not read `panel:`, so a future feature can be signed against a stale FAIL. That is a
  harness defect, raised as an open question rather than recorded anywhere in this plan.
- Finding `PF-963368450681cd9ef3131c2438dfb1b6` (should-not-exist, low) **describes the very
  state this write repaired**, and is transcribed `disposition: open` because that is its
  reader's word and no reader graded it resolved. Resolving it here would have been an
  adjudication. The operator may wish to mark it `resolved` at signature.

## The applied panel value

```yaml
last_run: 2026-09-01-10-validator
cycle: 6
reviewed_at: 047f6914
reviewed_at_note: "Plan phase, so no review_sha exists and none can be pinned (INV-6/DEC-207); 047f6914 is the tip the panel graded, post-rebase onto origin/main a93a1df9 and post the three text amends. Working tree clean, confirmed by the scope reader at dispatch."
severity_max: med
verdict: PASS
transcription_rule: "Each summary and pointer is the reader's own wording, markdown emphasis and backticks removed and wrapping collapsed to single spaces. Severity is the reader's own and is never reassigned; unrated would be carried unchanged and is gating-equivalent to high. De-duplicated on normalized summary plus reader id, so the same defect seen by two readers stays two entries cross-referenced by corroborated_by. Ids are absent by design: the lead holds no Bash and pm computes identity once with panel_findings.py at transcription."
history: "Cycles 0-3 and 5 ran before plan-merge.py had a set-panel route, so their records live only in their run digests and, for cycle 5, in notes/panel-value-c5.yaml; cycle 4's record — replaced by this write — was the first and only panel value the plan itself ever carried."
readers:
  - reader: goalcheck
    persona: harness-pm
    status: ran
    artifact: .harness/harness/features/FEAT-48-parallel-safe-suite/notes/research-FEAT-48-goalcheck-plan-c5.md
    artifact_note: "NOT re-run in cycle 6. Graded at 2a5cbada, before the rebase and before all three amends. Its verdict stands and nine of its findings re-derive true at 047f6914; seven passages are superseded — the five listed in cycle 5's digest plus F-05 and F-10, both now closed by fix."
  - reader: scope
    persona: harness-code-reviewer
    status: ran
    artifact: .harness/harness/features/FEAT-48-parallel-safe-suite/notes/review-harness-code-reviewer-planpanel-c6.md
    artifact_note: "Terminal yield refused by SEC-01 after one briefed attempt; findings transcribed from the artifact on disk. Verdict PASS, would sign at 047f6914."
  - reader: should-not-exist
    persona: fable-advisor
    status: ran
    artifact: none
    artifact_note: "Holds no write grant; its findings reach disk only through this transcription. Returned one fenced block with exactly two top-level keys, findings and the one-cycle recommendation, per contract. approve: yes, with nine named residual risks quoted verbatim in this digest."
findings:
  - id: PF-5f4c0650bd59a2beac41e3a2e55b3408
    reader: code-reviewer
    severity: med
    summary: "D-10's claim that plan-merge.py amend refuses a list field is falsified by the rebase: the quoted exit-4 message exists nowhere in the tool, and --yaml-value can now write a list field, so the one undated present-tense capability claim in the entry that abolished undated prose is false at this tip"
    pointer: "plan.yaml:215-217; plan-merge.py:1410-1412 (the actual exit-4 message), :1497-1504 (--yaml-value writes a list), :1585-1586 (the flag); commit b1e346c6 absent at 2a5cbada and 38dd3622, present at a93a1df9"
    disposition: open
  - id: PF-e8d2d0c282876f52fbc822c54ad26369
    reader: code-reviewer
    severity: low
    summary: "T-01's 146-file figure and D-01/D-11's 117-file figure count different sets — 117 is tracked files directly under bin/, 146 is everything shutil.copytree traverses including fixtures and ephemeral __pycache__ — and the amended sentence juxtaposes them as if updating one metric without ever saying so"
    pointer: "plan.yaml:385-388 versus :44 (D-01) and :296 (D-11); real tracked growth ccf674a to 8ca95d65 is 117 to 122"
    disposition: open
  - id: PF-963368450681cd9ef3131c2438dfb1b6
    reader: should-not-exist
    severity: low
    summary: "The embedded panel block still records cycle 4's FAIL and severity_max high with every finding disposition open, while cycles 5 and 6 were never transcribed into the plan, and plan-sign-gate.py does not read the block so nothing mechanical stops a signature landing on it"
    pointer: "plan.yaml:1334-1340; runs/2026-09-01-07-validator/digest.md records cycle 5's PASS"
    disposition: open
  - id: PF-671c55da77e57d73d2e1c91da9317259
    reader: should-not-exist
    severity: info
    summary: "Standing question answered: nothing in this plan should not be built, and the census re-verification at 047f6914 confirms the derived-scope design absorbed a real rebase without a single plan edit — a 60th test file, a 193rd decision and a new zero-write test file falsified zero sentences"
    pointer: "plan.yaml:472-473; run-unit-tests.sh:148; test-quarantine.py:93"
    disposition: open
  - id: PF-e69c81bad62702c3e661936347e706c4
    reader: goalcheck
    severity: med
    summary: "No criterion would fail if issue #1053's own symptom persisted; SC-05's ten runs are declared non-probative by the BRIEF and nothing asserts test-gh-sync.py passes N consecutive 8-worker runs"
    pointer: "BRIEF.md:127-131; run-unit-tests.sh:31; plan.yaml:262-272"
    disposition: open
  - id: PF-e2842b1b847c003d6ef308c31b0f40b2
    reader: code-reviewer
    severity: med
    summary: "T-07's supersession is not mechanically uniform across tooling: check-plan-routes.py still emits a DEVIATION line for T-07 identical in shape to live tasks, and build.yaml's steps_from carries no task status filter, so a reliable skip rests on convention plus T-07's own prose refusal"
    pointer: "plan.yaml:1264; check-plan-routes.py run live at this tip (7 DEVIATION, 0 VIOLATION, exit 0); build.yaml steps_from"
    disposition: open
  - id: PF-507dd4d0868181ec33b6dcf486fdf657
    reader: should-not-exist
    severity: low
    summary: "The abandoned-task-as-ownership-carrier idiom collides with the factory-wide meaning of abandoned as dropped, and the collision has one verified live cost: gh-sync station review exits 2 for this feature's whole life"
    pointer: "gh-sync.py:1147-1154; plan.yaml:1264-1265"
    disposition: open
    corroborated_by: code-reviewer
  - id: PF-0f52ff857acf41541231b508573db53d
    reader: goalcheck
    severity: low
    summary: "D-10 claims the census is deterministic on a given tree, but two of the eight mutants embed os.getpid(), so two doers print textually different SITE lines and a reviewer reads drift where there is none"
    pointer: "plan.yaml:180"
    disposition: open
  - id: PF-42e0aaa48a8a344a99680c58b40a836d
    reader: goalcheck
    severity: low
    summary: "The derivation instrument and the completeness gate are different instruments: a chmod or utime-only site, or one under a subdirectory, is census-invisible and scan-visible, so T-03 returns BLOCKED on a site no task owns"
    pointer: "plan.yaml:185"
    disposition: open
  - id: PF-498f50089a28a6bd78796dc6510bc117
    reader: goalcheck
    severity: low
    summary: "The census is a 250s pass over the live tree; a sibling agent editing any file in bin during it fabricates a SITE line attributed to whichever test was running, and nothing enforces the quiet-tree assumption"
    pointer: "plan.yaml:169; :283-287"
    disposition: open
  - id: PF-4241dce0871070cb4c75a9ad0f1f8f8a
    reader: goalcheck
    severity: low
    summary: "The ea6f51f control run inside an isolated root exits 1 with a FileNotFoundError traceback after the schema window has been produced, so the doer pasting verbatim output pastes a traceback and may read it as a failed control"
    pointer: "T-06 SC-02 leg; test-check-domain.py:1770"
    disposition: open
  - id: PF-ae8a56b4f178f0a8df662ba275038636
    reader: goalcheck
    severity: low
    summary: "Issue #1053's Scope section still reads Folded into FEAT-47 and no task updates the issue body"
    pointer: "issue #1053 body; BRIEF.md:213-224"
    disposition: open
  - id: PF-bb123e7e86e19b1cd849610f39ce47a2
    reader: code-reviewer
    severity: low
    summary: "Issue #1053's Scope section is still stale and outside plan.yaml's write authority, flagged for the operator to close by hand"
    pointer: "issue #1053 body; BRIEF.md:213-227"
    disposition: open
    corroborated_by: goalcheck
  - id: PF-77c77b2b4e62888b35293e566448f58c
    reader: goalcheck
    severity: low
    summary: "#1053 headlines 5.3x while SC-06 accepts 120s against a 247s baseline, i.e. 2.06x, so a 119s outcome passes every criterion while delivering about 40 percent of the advertised win"
    pointer: "BRIEF.md:139-146"
    disposition: open
  - id: PF-6e5e4d2b22b169d401d2bdcbab2425c1
    reader: code-reviewer
    severity: low
    summary: "T-02's declared files understates its actual touch scope because it will also edit test-bash-write-guard.py; signable, since check-domain.sh authorizes by lane glob and not by files, but a build-cycle reviewer diffing only files could misflag the edit as scope creep"
    pointer: "plan.yaml:461-462; :533 (T-02 intent)"
    disposition: open
  - id: PF-3e841eea447e4dcb511236d5eb9fda8d
    reader: should-not-exist
    severity: info
    summary: "T-02's self-referential verify carries two residual couplings: plain yaml.safe_load instead of the duplicate-key-strict loader the scheduler uses, and the absorbed non-empty guard permanently hard-wiring T-07's continued presence into T-02's gate"
    pointer: "plan.yaml:468 (safe_load); :492 (absorbed non-empty); harness_yaml.py load_plan (D-12)"
    disposition: open
```
