# SC-11 landed, D-18 recorded — BUG-1309-mirror-build-entry — 2026-09-08

**Operator ruling R-6 is now in the record and R-4 clause 3 traces to a criterion.** `BRIEF.md`
gained SC-11 as a pure append (12 insertions, 0 deletions, one hunk at `+161`); `plan.yaml` gained
exactly one decision, D-18, through `plan-merge.py apply` (22 insertions, first changed line 308).
No source, test, hook, UAT, STATE.md or feature.json byte moved. **`BRIEF.md ## Approval` is
untouched and therefore stale over amended text — the main session's re-signature is what clears it,
and it gates the ship.**

## SC-11, as landed (`BRIEF.md:161-172`)

- SC-11: `git merge --abort`, `git merge --continue` and `git merge --quit`, issued on a branch
  whose feature owes a Build-entry receipt — `github.build_entry` ABSENT under enabled sync, or
  reading `recovery-required`, with the feature NOT in `feature_schema.BUILD_ENTRY_ERA_EXEMPT` —
  are each ALLOWED: exit 0 with NO permissionDecision object on stdout. They are merge CONTROL
  operations that recover an interrupted merge, not the merge action REQ-07 refuses. All three are
  graded by the cases T-05 declares — `T-05 merge --abort on an owing branch allows`,
  `T-05 merge --continue on an owing branch allows` and
  `T-05 merge --quit on an owing branch allows`. Each is DISCRIMINATING at `review_sha`: run against
  the pre-change copy recovered with
  `git show e374c9a2:.claude/skills/harness/bin/merge-gate.py`, each case FAILS — and a case that
  cannot be made to redden is reported as non-discriminating rather than kept.
  verify: automated        evidence: integration

## D-18, as landed (`plan.yaml`, `decisions[-1]`, `dec: DEC-132`)

`choice` — the three merge control operations are graded by a NEW criterion SC-11, never by an
exclusion sentence inside SC-04; SC-04 stays byte-identical and SC-11 carries the whole allow.
`because` — cites R-6 (`notes/rulings-2026-09-08-c16-sc11.md`), names the contradiction (SC-04 read
literally mandates the deny R-4 clause 3 reverses; read narrowly it is silent and the allow is
graded by nothing), and records that the code contract is unchanged — D-16 already specifies the
exemption and T-05's `verify:` already gates the three case names.

**`dec: DEC-132`, chosen over `none`.** DEC-132 is the decision that makes this form legitimate:
"wording, numbering and verify methods stay pm's" and adding a criterion beyond the operator's
mandated outcome is *expected*. `DEC-174` (D-16/D-17's `dec:`) governs the main-session-direct
implementation route and is irrelevant to a criterion's shape; `none` would have understated a real
governing decision.

## What changed, per file

| file | change | proof |
|---|---|---|
| `BRIEF.md` | SC-11 appended after SC-10 | `git diff --stat`: `12 ++++++++++++`, `1 file changed, 12 insertions(+)`; `git diff -U0` prints ONE hunk header, `@@ -160,0 +161,12 @@` — a zero-length old range, so SC-01..SC-10, `## Requirements`, `## Constraints` and `## Verification gaps` cannot have been touched |
| `BRIEF.md ## Approval` | none | verbatim, post-edit: `## Approval` / `` / `status: approved` / `approved-by: Mike Ruangutai` / `date: 2026-09-08` — and outside the single hunk's range |
| `plan.yaml` | `decisions` += D-18 | `22 ++++++++++++++++++++++`, 22 insertions, 0 deletions |
| `plan.yaml approval:` / `panel:` | none | first changed line is **308** vs. `approval:` at lines 3-24; old lines 3-24 compare equal to new 3-24. `panel:` shifted 308 -> 330 by the 22 inserted lines and `panel:`..`tasks:` compares byte-equal, as does `tasks:`..EOF |

## Proof items, measured

- Three case names present, **wrap-tolerant**: the criterion wraps at column 100, and
  `T-05 merge --quit on an owing branch allows` sits on its own physical line while the others do
  not straddle one. Ran a whitespace-collapsing search over the whole file
  (`re.sub(r'\s+',' ', ' '.join(l.strip() for l in lines))`, then `str.count` per name) rather than
  a line-oriented grep: **1, 1, 1** — one occurrence each, all three verbatim.
- SC-11's trailing line is `  verify: automated        evidence: integration`, byte-identical to the
  eight existing `automated` criteria (two-space indent, eight spaces before `evidence:`).
- `plan.yaml` decision ids are exactly `D-01 .. D-18` under `safe_load`, D-18 last, keys
  `['id','choice','because','dec']`, and its `because` tail survives intact (no `#`-truncation).
- `git status --porcelain`, verbatim:
  `` M .harness/harness/features/BUG-1309-mirror-build-entry/BRIEF.md``,
  `` M .harness/harness/features/BUG-1309-mirror-build-entry/plan.yaml``,
  `?? .harness/harness/features/BUG-1309-mirror-build-entry/notes/rulings-2026-09-08-c16-sc11.md`
  (the `??` note is the orchestrator's R-6 transcription, not this dispatch's write; this note adds
  a second `??` after it was taken).
- `check-plan-routes.py <plan.yaml>`: **0 violations across 1 plan, exit 0** — the six `DEVIATION`
  lines are the expected DEC-174 carve-out output.
- No suite, linter or formatter was run. Nothing was committed.

## Open

- `BRIEF.md ## Approval` and `plan.yaml approval:` are both stale over amended text. One main-session
  re-signature of the brief plus one `sign-approval` on the plan clears both; neither is reachable
  from any governed agent (`approval_guard`; `sign-approval` refused at the tool).
- Carried forward from `notes/research-BUG-1309-planamend-c16.md`: T-05's enumerated case-name
  contract lists 21 names while its `verify:` gates 26. Pre-existing, harmless, still unreconciled.
