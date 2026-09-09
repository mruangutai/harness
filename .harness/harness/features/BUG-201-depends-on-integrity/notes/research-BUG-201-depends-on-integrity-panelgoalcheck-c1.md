# Panel record repair — BUG-201 `panel.readers` goalcheck row

**BLUF.** The transcription omission is repaired. `panel.readers` now carries all three readers
INV-32 requires (`check-state.sh:534` — `expected_readers = {"should-not-exist", "scope",
"goalcheck"}`), each `status: ran`. The write went through the single legal route,
`plan-merge.py set-panel --value-file`, which printed `PANEL cycle 1 -> …` / `APPLIED …`, exit 0.
The diff is 3 insertions, 0 deletions. No task, decision, requirement, finding, severity, station,
lane, or approval value changed.

The `goalcheck` reader genuinely ran: run id `2026-09-07-02-product`, persona `harness-pm`, verdict
PASS, recorded at `notes/research-BUG-201-depends-on-integrity-goalcheck-plan-c1.md` (its BLUF
answers "does this plan deliver the operator's stated intent?" with **Yes**, and dispositions all
ten c0 findings plus three c1 defects). Its absence from the record was transcription, not a reader
that never ran.

## A — readers

| measure | value |
|---|---|
| row count | **3** (was 2) |
| reader name set | `{goalcheck, scope, should-not-exist}` — equals INV-32's expected set exactly |
| on-disk order | `scope`, `should-not-exist`, `goalcheck` (the two existing rows untouched, ahead) |
| every row `status: ran` | **True** |

New row: `reader: goalcheck` / `persona: harness-pm` / `status: ran`. No `reason` needed — `ran`,
not `skipped`. Order is not graded: INV-32 keys readers into a dict and iterates
`sorted(expected_readers)` (`check-state.sh:538-547`), so appending was chosen for a clean diff.

## B — findings preserved

- `len(panel['findings'])` **before = 19**, **after = 19**.
- Finding-id sets compared **equal** (`set(before) == set(after)` → `True`); all 19 ids distinct.
- `panel.last_run` = `2026-09-07-02-validator`, `panel.cycle` = `1`,
  `panel.transcription_rule` tail intact (`…carries its reason in its summary.`) — all unchanged.
- `approval:` unchanged: `status: approved`, `date: 2026-09-07`, `approved_by: mruangutai`.
  `tasks:` 6, `decisions:` 5, top-level keys unchanged.

The replacement mapping was derived from `yaml.safe_load` of the file itself and one `append` — no
value was retyped. Round-trip check of the scratch dump against the in-memory mapping: equal.

## C — diff

```
 .../BUG-201-depends-on-integrity/feature.json      | 25 +++++++++++++++++++++-
 .../BUG-201-depends-on-integrity/plan.yaml         |  3 +++
```
`git diff --numstat -- plan.yaml` → `3	0` (3 insertions, 0 deletions). The added lines, all of them:
```
+  - reader: goalcheck
+    persona: harness-pm
+    status: ran
```
**Honest note on "only changed file":** `feature.json` was ALREADY modified before my run — captured
by `git status --porcelain` prior to the write (` M …/feature.json`, sole entry). It is a sibling's
edit, not mine; I never opened it. Restricted to my target, plan.yaml is the only file I changed.

## D — no commit, HEAD unmoved, scratch gone

- `HEAD` = `bfc3747edff57ecf2834fa2aaa5dd5dd7e92ac48` before and after the write. No commit made.
- Scratch lived at `/tmp/panel-bug201.yaml` (plus `/tmp/panel-bug201-before.json` holding the
  before id set) — outside the feature dir, outside the worktree. Both deleted;
  `os.path.exists('/tmp/panel-bug201.yaml')` → `False`.

## Open questions

None.
