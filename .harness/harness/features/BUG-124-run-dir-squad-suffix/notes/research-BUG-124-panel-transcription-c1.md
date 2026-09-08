# Panel transcription c1 — BUG-124 `panel:` now records the cycle-1 run

**DONE.** `plan.yaml`'s top-level `panel:` reads `last_run: planpanel-c1-validator`, `cycle: 1`,
three readers all `ran`, and **13 findings**: the 8 cycle-0 entries carried forward verbatim (7 at
`disposition: resolved`, the `info` clean-bill at `open`) plus the 5 cycle-1 findings at `open`.
Nothing else in the plan moved — `approval: pending`, `status: plan`, 3 tasks, 5 decisions unchanged.
Written through `plan-merge.py set-panel` only. Nothing committed.

## The five cycle-1 findings, ids computed not typed

Source: `runs/planpanel-c1-validator/digest.md:145-149` (`findings_advisory`, R-1..R-5).

| R | reader | sev | id |
|---|---|---|---|
| R-1 | `scope` | med | `PF-334e1b370c596f88c39730bf43579f13` |
| R-2 | `scope` | med | `PF-c996440943e296d047bc8707c587ad89` |
| R-3 | `scope` | med | `PF-4ed20fe501059b1b0507f9eccfdc2fb7` |
| R-4 | `should-not-exist` | info | `PF-20b1d027656f333f87b7c54ddf742281` |
| R-5 | `scope` | low | `PF-fb7141e87d0ab54cb511a4c0dddcf184` |

Each id re-derived by `panel_findings.py id` **from the summary as it reads in plan.yaml after the
merge** — 5/5 MATCH (`/tmp/bug124_verify_panel.py`). R-1's split severity is recorded at the
adjudicated `scope` **med**; no severity was averaged or reassigned. All five are `open`: they are
live advisory findings for the operator's one batched signature review (DEC-176), and `gates.review`
is `advisory_unless_high` (`.harness/harness.json:376`), so none gates. **R-5 reports precisely the
staleness this dispatch removed and is still recorded `open`** — the operator rules on it, and the
record must not pre-empt that.

## The reader record — three, and why the third is `ran`

`check-state.sh:534` expects `{should-not-exist, scope, goalcheck}` and emits a HARD `INV-32 … bad`
for any of the three not recorded `ran`/`skipped` (`:542-548`). The cycle-0 block recorded two; that
was a latent defect, fixed by transcription.

`goalcheck: ran` is **my own check, not the dispatch's say-so**:
`notes/research-BUG-124-goalcheck-plan-c1.md` is a cycle-1 artifact — it grades the c1 revision by
name (`GOALCHECK-F1` closed against the `[.]` escape, REQ-06/SC-08/SC-09, `plan.yaml:174`/`:255`),
records `sha256 399154c5…` for plan.yaml at HEAD `ff2b749e`, and its Q1 is the same finding the panel
digest credits to goalcheck in R-5 (`digest.md:149`). No reader is `skipped`, so no `persona`/`reason`
is carried.

## Verification — commands and what they showed

- **`plan-merge.py set-panel`** → `PANEL cycle 1 -> …` / `APPLIED …`, exit 0. The verb itself reloads
  the spliced file and refuses if `panel` does not reload as supplied (`plan-merge.py:1062-1065`).
- **Re-load** (`/tmp/bug124_verify_panel.py`): `last_run='planpanel-c1-validator' cycle=1`,
  `should-not-exist:ran, scope:ran, goalcheck:ran`, `findings=13` (7 resolved / 6 open),
  `approval={'status': 'pending'} status='plan'`, `tasks=3 decisions=5`.
- **Verbatim carry-forward**: `git show HEAD:…plan.yaml` vs the working file — 8/8 cycle-0 ids
  present and `severity`/`reader`/`summary` byte-identical for all 8; every top-level key other than
  `panel` compares equal.
- **Diff scope**: `git -C <TREE> diff -U0 -- …/plan.yaml` → 9 hunks, every header `@@ … @@ panel:`,
  spanning old 93–159 (the block ran 92–160); `--stat` = `61 insertions, 14 deletions`, one file.
  `-U3` tail shows `tasks:` and `- id: T-01` as **context**, so the panel/tasks boundary is untouched.
  `git status --porcelain` (whole worktree) = only
  `M .harness/harness/features/BUG-124-run-dir-squad-suffix/plan.yaml` before this note was written.
- **`check-plan-routes.py <plan.yaml>`** from the worktree: `0 violation(s) across 1 plan(s)`, exit 0.
- **`resolved_by` omission accepted**: `check-state.sh`'s own INV-32 body (lines 473–555, extracted
  verbatim and executed over the landed panel — `/tmp/bug124_inv32_probe.py`) returns **0 bad, 7 warn**,
  the warns being the seven `disposition resolved` notes. `resolved` is the vocabulary token
  (`templates/plan.yaml:80`); `closed` would have made the two `high` cycle-0 entries HARD `bad`.

## Open questions

- **Q1 (non-blocking, harness owner).** The live `check-state.sh` cannot grade this plan at all:
  it globs the **owner** checkout's `.harness/*/features/*` (`:118-120`), which has no
  `BUG-124-run-dir-squad-suffix` dir, and INV-32 grades only `approved` plans (`:428-471`). A full
  run from inside the worktree printed 867 lines and **zero** mentioning BUG-124. Same
  owner-root-vs-worktree class as the digest's Q3. Hence the extracted-body probe above.
- **Q2 (non-blocking, operator).** R-1..R-5 remain `open` by design. Their remedies (one BRIEF
  disclosure clause; one caveat clause in T-03 sentence two; one assertion in case (h)) are the
  operator's call at signature — a plan edit now would unbind the panel verdict from the plan the
  readers read and force a cycle-2 panel.
