# plan-fix-c6 — re-key panel.readers, one write

**Done, clean.** `panel.readers` now holds exactly three entries keyed `reader:` —
`should-not-exist`, `scope`, `goalcheck` — all `status: ran`, so INV-32's index expression resolves
all three required readers. Exactly ONE mutating command ran. The nine `PF-` ids are byte-identical
to baseline and `panel` minus `readers` is EQUAL to baseline, proven by comparison. **No block scalar
re-flowed anywhere**: the whole-file textual diff is one hunk, entirely inside `readers:`.

## The write — the only mutating command in this run

```
python3 /Users/molchairuangutai/GitHub/harness/.claude/skills/harness/bin/plan-merge.py set-panel \
  --file <plan> --value-file /tmp/bug1305-panel.yaml
```
stdout:
```
PANEL cycle 2 -> /Users/.../features/BUG-1305-run-state-clobber/plan.yaml
APPLIED /Users/.../features/BUG-1305-run-state-clobber/plan.yaml
```
stderr: empty. `EXIT=0`.

The value file was built PROGRAMMATICALLY (`/tmp/bug1305_build.py`): `safe_load` the plan, take
`plan['panel']`, rename `id`->`reader` in place (key order preserved, `persona`/`status`/`findings`/
`note` carried by reference), append the `goalcheck` entry, `yaml.safe_dump(panel, sort_keys=False)`.
Nothing was hand-transcribed. A pre-flight (`/tmp/bug1305_preflight.py`) confirmed
`value-file minus-readers == baseline: True` BEFORE the write, so the write was taken only once the
hazard was excluded.

## Verification — actual results, by comparison

| Check | Result |
|---|---|
| nine `PF-` ids vs baseline | equal per id 1..9, `list-equal=True`, count 9==9 |
| `panel` minus `readers` == baseline | `True` (covers every `summary`, `last_run`, `cycle`, `verdict`, `severity_max`, `code_grade`, `cycles_used`, `digest`, `transcribed_by/at`, `transcription_rule`, and each finding's `severity`/`reader`/`readers`/`disposition`/`resolved_by`/`resolution`/`note`) |
| everything outside `panel` | equal = `True` |
| plan `safe_load`s | OK — top keys `schema, feature, status, approval, source_issues, lanes, decisions, panel, tasks` |
| `approval.status` | `'pending'` |
| top-level `status:` | `'plan'` |
| task list | `True` unchanged — 12 ids, same order, `T-01..T-12` |
| INV-32 expression `[str(i.get('reader','')).strip() ...]` | `['should-not-exist', 'scope', 'goalcheck']`, statuses `['ran','ran','ran']`, legacy `id` key present in any entry: `False` |

Text diff, `diff -u /tmp/bug1305-plan-before.yaml <plan>` — ONE hunk `@@ -123,17 +123,22 @@`, +7/-2:
two `- id:` -> `- reader:` renames and the five-line `goalcheck` entry. **No other line changed and
no line re-flowed** — the `transcription_rule` and all nine `summary:` blocks re-emitted byte for
byte. File 1394 -> 1399 lines.

## git status — verbatim

```
?? .harness/harness/features/BUG-1305-run-state-clobber/
```
HEAD unchanged at `c369fb1fdfc74a8f78edc9a2df2a8fea738afc94`. No tracked file was modified at all
(the feature directory is untracked in this worktree), no commit, no test run.

## Open

- INV-32's block is skipped while approval is `pending`, so this record's effect is unobserved until
  the operator signs; it was deliberately not proven by running the full state gate (it would prove
  nothing either way). The construction was verified against INV-32's own indexing expression instead.
- `goalcheck` is recorded `ran` with no `findings:` count — the key is absent, not zero, since the
  three goalcheck rounds are notes, not severity-graded findings. INV-32 requires only `reader` and
  `status`.
