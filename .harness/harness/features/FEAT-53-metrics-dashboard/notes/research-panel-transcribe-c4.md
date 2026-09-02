# Panel cycle-4 transcription — FEAT-53-metrics-dashboard

**BLUF. Cycle 4 is in `plan.yaml`'s `panel:` key: `cycle: 4`, `last_run: 2026-09-02-05-validator`,
two readers both `ran`, 25 findings — 13 cycle-1/2 `PF-*` byte-identical, V-1..V-5 flipped to
`resolved` with closure citations, C4-01..C4-07 added `open`. `remedy_size` went in as its own
key on each C4 finding; `set-panel` accepted it without complaint. Nothing else moved:
`approval.status: pending`, top-level `status: plan`.**

**The dispatch's "20 entries total" is arithmetically wrong and was not followed.** The pre-write
panel already held 18 findings (13 `PF-*` + V-1..V-5); 18 + 7 new = **25**. `set-panel` replaces the
whole mapping, so honouring 20 would have deleted five immutable records. Lead notified before the
write. The acceptance probe therefore prints `4 25`, not `4 20` — the discrepancy is in the
expectation, not in the file.

## Diff summary — per finding id (semantic, `harness_yaml.load_plan` both sides)

- **13 × `PF-*`: `IDENTICAL`** — every field, including all nine settled `overruled`/`backlog`
  dispositions and their notes. No PF entry's `disposition`, `note` or `summary` moved.
- **5 × `V-*`: `CHANGED ['disposition','note','resolved_by']`** only. `id`, `cycle`, `severity`,
  `reader`, `summary` untouched. `disposition: open` → `resolved`; `resolved_by:` = `D-22 + T-19`
  (V-1), `T-06 + T-11` (V-2), `T-06` (V-3), `T-11` (V-4), `D-21 + T-11` (V-5); each `note:` cites
  the operator ruling `notes/answers-2026-09-02-plan-signature-c3.md` plus the panel's own Job 1
  field citations (not re-derived here).
- **7 × `C4-*`: `ADDED`** — C4-01/02/03/04 `med`, C4-05/06/07 `low`, all `disposition: open`,
  all carrying `remedy_size`. Listed in id order; severities and readers verbatim from the Job 2
  table. Q3 is not a finding of its own — its defective part (e) is carried as C4-06, as instructed.
- `readers` list unchanged in content (both `ran`); `last_run`/`cycle` advanced.

## Probe outputs (literal)

```
$ python3 -c "...harness_yaml.load_plan(...)...print(cycle, len(findings))"
4 25

$ git -C <worktree> diff --stat
 .../BRIEF.md                              |  75 ++--
 .../DESIGN.md                              |  95 +++--
 .../feature.json                            |   8 +-
 .../observations/harness-pm.md              |   9 +
 .../observations/harness-visual-designer.md |   2 +
 .../plan.yaml                               | 407 +++++++++++++++++----
 6 files changed, 474 insertions(+), 122 deletions(-)
 (plan.yaml numstat: 330 insertions, 77 deletions)

$ git diff -U0 -- plan.yaml | grep '^@@'   # tail
@@ -1667 +1821,7    @@ -1674 +1834,7    @@ -1682 +1848,7    @@ -1688,0 +1861,81

$ approval/status grep + live read
approval: {'status': 'pending', 'approved_by': 'none', 'date': 'none'}
status: plan
```

**On `diff --stat` naming six files, not one.** The other five were already dirty when I started —
mtimes: `plan.yaml` 08:32:20 (my `set-panel`), `BRIEF.md` 07:55:10, `DESIGN.md` 07:23:33,
`feature.json` 08:10:18, `observations/harness-pm.md` 08:06:26, all 22–70 min older than my single
write. They are earlier cycle-4 work in this worktree, not mine. Scope of my write: one
`set-panel` call, and every diff hunk at or after the `panel:` key (line 1652 of 1942) is the panel
splice — `+1821`, `+1834`, `+1848`, `+1861,81`.

**On the `approval` grep matching.** It matches `D-14.choice`, `D-21.choice`, `T-06.intent`,
`T-11.intent` — pre-existing cycle-4 amendments containing the word "approval" — plus one line of my
V-2 `note` naming `approval_date()`. No line touches the `approval:` block, `approved_by`, or
top-level `status:`; both confirmed by direct read above.

## Open questions

- **Q1 (non-blocking):** dispatch and acceptance both stated 25 findings as 20. Recorded here so the
  operator does not read `4 25` as an over-transcription.
- **Q2 (non-blocking, for the operator at signature):** all seven C4 findings are `open` by design —
  none gates (`must_fix: []`), and the budget ruling routes them to the operator, not to a fix
  cycle. `remedy_size` is the routing signal: six single-clause, C4-03 larger.
