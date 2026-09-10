# STATE

## Current

- feature: FEAT-104-strict-digest-schema
- runs: `2026-09-09-10-panel-validator` (reviewer panel, cycle 9, at the corrected pin `168f875f`)
- squads: validator (the four-reviewer `review` team, hosted by `harness-validator-lead`)
- status: validate — **the reviewer panel PASSES at `168f875f` with `must_fix: []`.** No gating
  defect remains. Still owed before ship: the pm goal-check (SC-01..SC-16, SC-14 struck), the SC-13
  UAT, the CEO briefing. None was run in this mission.

**The panel re-graded rather than rediscovered.** `runs/2026-09-09-10-panel-validator/digest.md`:
`code_grade: pass` (42/42 graded functions), `severity_max: med`, `matrix_ok: true`, all four
reviewers `PASS`, zero send-backs.

- **F1 (high, schema downgrade) — CLOSED**, confirmed at source and by execution, including a
  string-type-confusion route security added itself.
- **F3 (med, omitted-file route missing from the rejection message) — CLOSED.** ui FALSIFIED ITS OWN
  c7 finding by capturing the verbatim emitted text at the pin instead of inheriting round 1.
- **F2 (med, raw-persona at-rest sweep) — DECLINATION UPHELD; nobody re-raised it.** Two reviewers
  independently reproduced the REQ-08/SC-12 stranding on the real artifact and showed no digest-side
  discriminator exists that a remedy could use. Its runtime residual is below, not gating.
- **c7's F4 and F5 retired on the merits.** F4's premise (SIMPLIFY S2 as F1's structural cause) no
  longer holds now `check-domain.sh` alone makes a strict run's version monotonic; F5 (the S4
  restatement across four instruction files) is what signed T-03 required, so reversing it is a plan
  change, not a review finding.

**Both self-scoping reviewers scoped themselves IN after measuring** — security because the diff
changes a write-time guard and an at-rest sweep, ui after a 62-file extension census and a
`DESIGN.md` glob returning zero. That is why four PASSes are not a shallow panel.

**Four findings survive, ALL non-gating and none routable to a squad** (DEC-174 carve-out or above
squad authority), so no fix cycle exists and `must_fix` is empty. Each is an operator decision below.

**Two claims re-verified at this tier, not relayed.** CF-1: `check-state.sh:1525-1526` does
interpolate `run_id` and `_step_id` bare while `_names` beside them is a list repr. CF-3: `abff2a84`
is the CHILD of merge-base `78e34f06` — this branch's root commit — and `git rev-list
origin/main..168f875f` contains it, so it ships with the PR and `code-grade.py`'s merge-base range is
blind to it by construction.

**The pin held.** HEAD `71040f1c` is two commits ahead of `review_sha`, both feature-bookkeeping only
(`git diff --name-only 168f875f..HEAD`). The panel reviewed `origin/main..168f875f`; the pin did not
move.

**`cycles_used` stays 8 — this panel is not new rework, deliberately read against DEC-157.** The
handoff recommended 9. The F1/F3 fix loop was already counted at 7 → 8 (`71040f1c`); the qa re-run,
the simplify re-run and this panel are the re-verify leg of that ONE loop. DEC-157 counts loops, not
runs. Zero send-backs, panel PASS: no rework event occurred here. Two cycles remain.

**`len(runs)` is 20 of `max_total_runs` 20 — the informational tripwire is reached, surfaced here and
not only at the next `/harness` entry.** It stops nothing (issue #79). My read: the runs still earn
their place, but runs 05–10 trace to one avoidable cause — a commit amended under a LIVE validator
cycle (`99035a9c` replaced by its sibling `168f875f`), which forced a re-grade of everything. That is
not a feature thrashing on its own merits.

## Open Questions

- Q1 (not blocking, main session, DEC-174): **CF-1** (security, `med`).
  `check-state.sh:1525-1526`'s INV-16 at-rest message interpolates `run_id` and the step id as bare
  strings — alone among this diff's attacker-controlled interpolations — so the accepted DEC-85
  Bash-write route can spoof or erase the audit line that reports it. One-line remedy (`!r`, or
  list-wrapping to match `_names`). No operator-channel witness: security reproduced the terminal
  render in a throwaway script, but driving it through the real `/harness` sweep needs a write
  capability no reviewer holds.
- Q2 (not blocking, main session): **CF-3** (code, `low`). `abff2a84`, a FEAT-56 `plan.yaml` station
  flip, is this branch's root commit and merges with this PR, untracked by any FEAT-104 REQ or D.
  Lead recommends ACCEPT and record in the ship note — benign, arguably correcting, on an
  already-merged feature, and excising it means rewriting history beneath a signed pinned
  `review_sha`. I concur; the call is the operator's.
- Q3 (not blocking, main session): **CF-2** severity CONTESTED and carried unreconciled — qa `med`,
  code `info`, lead `low` (the regression is loud at the next `/harness` entry, not silent).
  `check-state.sh:1590`'s literal-`lead` at-rest exemption has no test able to report RED. The remedy
  is a test inside the carve-out, so no squad may close it at any severity. Supersedes the earlier
  form of this gap.
- Q4 (not blocking, main session, harness defect): the `lead` digest schema declares no `code_grade`
  (absent from `SCHEMAS['lead']`, `PASSTHROUGH['lead']`, `DOCUMENTED_OPTIONAL`), so a lead hosting a
  code-grading run cannot declare it at top level without tripping this feature's own undeclared-key
  rejection; the panel carried it on the `code` member entry. Plausibly deliberate — the mechanical
  recomputation at `validate-digest.py:1430-1441` binds only `harness-code-reviewer` — but my
  dispatch demanded a top-level field the contract forbids, which is my error, not the lead's. Should
  `PASSTHROUGH['lead']` gain it as an unverified roll-up, or keep forbidding it?
- Q5 (not blocking, main session, DEC-174): **CF-4** (ui, `low`). The `schema_version` downgrade
  branch renders a raw Python `None` in the omitted-on-update edge case instead of reusing the floor
  check's "schema_version is absent" phrasing; `T-06` has no omitted-on-update case, which is why no
  test saw it.
- Q6 (BLOCKING, main session, DEC-174 — carried forward unchanged): `check-domain.sh:1327`'s
  append-only correction channel cannot repair a run digest, because `validate-digest.py`'s parser
  stops at the indent-0 `artifact:` line. Two digests are stranded (`runs/-06`, missing
  `adequacy_notes`; `runs/-08`, `PASS` beside a `FAIL` member step). A harness defect, not a finding
  about this diff. The panel was told not to attempt either repair and did not.
- Q7 (not blocking, main session): the 3 complete + 2 partial strict-version predicate spellings
  (`check-domain.sh:1594-1597`, `:1761-1764`, `check-state.sh:1487-1489`; partials
  `check-domain.sh:1601`, `:1767-1768`) want one `is_strict_schema_version()` home beside the schema
  loader. SIMPLIFY's surviving reuse residual. Backlog row or fold-in before ship?
- Residual non-gating risks, so they do not die silently: (1) the pre-existing DEC-85 Bash-write
  bypass, CF-1's precondition; (2) F2's runtime residual — `stop_hook_active`'s accepted one-shot
  plus the persona-blind at-rest sweep leaves an undeclared key on a NEW lead digest uncaught AT
  REST, though new returns stay closed at write time; (3) `check-domain.sh`'s pre-existing
  `_no_parser` bootstrap early return, newly checked by security and confirmed caught by the next
  sweep.
- Coverage gap the panel could not close (DEC-174): `run-state-schema.json`'s guards
  (`check-domain.sh:1618-1667`, `check-state.sh:1486-1535`) are ARGUED fail-closed plus a
  non-tautological DECLARED-literal cross-check (`test-check-domain.py:14,114-124`), but not
  mutation-proven — the mutation would edit a carve-out file. Unlike F1, whose witness discriminates
  (11/12 pre-fix, downgrade ACCEPTED → 12/12 post-fix), their red capability rests on reasoning.
- qa's `F-QA-1`, dismissed as a gate, kept as a note: `T-05`'s `change_type` logic vs DEC-212's
  `touches_config_shape`. Integration coverage exists regardless; this is its SECOND cycle raised — a
  matrix-classification note for the next task on this surface.
- `matrix_ok: true` is ADOPTED from same-pin evidence (`notes/qa-feat104-tip-168f875f.md`), not
  freshly measured at cycle 9. qa says so in its own note, verified provenance by md5, and re-ran the
  two applicable kinds itself rather than taking the whole matrix on trust.
- SC-12 (`inspection`) and SC-13 (`uat`) remain unexercised — no goal-check ran here. SC-13 gates and
  no harness run can close it: it is the DEC-174 operator read. CF-4's message text and CF-1's
  audit-line spoof are concrete things for that read to look for.
- Unchanged: whether the INV-26 card/plan mismatch is a harness defect rather than drift; and
  `check-domain.sh`'s worktree-claim guard being keyed per persona with no per-session identity, so a
  live claim on another feature refuses this feature's same-persona agent its own writes.
