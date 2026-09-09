# Panel cycle 1 transcribed into plan.yaml — record now shows the second panel

**Done.** `panel:` in `plan.yaml` is now the cycle-1 record: `cycle: 1`,
`last_run: 2026-09-06-panelc1b-validator`, 11 findings (7 cycle-0 carried unchanged + 4 cycle-1, all
`resolved`), and a reader roster describing cycle 1. `approval:` is byte-identical to `HEAD`
(sha256 `b6515d5c…dff6`, 892 bytes, both sides), so all four operator rulings still name live
findings. Nothing else in the file was touched — the only write route used was
`plan-merge.py set-panel --value-file /tmp/panel-c1-value.yaml`.

## Which run is the cycle-1 record, and how that was decided

`runs/2026-09-06-panelc1b-validator`. Both candidates' `state.yaml` are equivalent (same two steps,
same personas, same notes, `status: complete`), so the state files do not decide it. The digests do:

- `panelc1b/digest.md:1-47` opens with the DEC-156 contract block (`VERDICT: BLOCKED`, full DIGEST,
  `findings_by_severity`, `must_fix`, `readers_status`, `escalations`). `panelc1/digest.md` has no
  contract block at all — it is the prose assessment only.
- The lead states the split itself: `panelc1b/digest.md:57-60` ("This directory is the canonical
  record for cycle 1") and Q3 at `:32` — DEC-156 wants the block at the top while `check-domain.sh`
  permits only appends to a recorded digest, so the lead opened a second directory. One panel, one
  cycle, two directories; no member re-dispatched.

## Id derivation — reproduced against a recorded id

Rule per `panel_findings.py`. Proof it reproduces: cycle-0 `PF-a882c9b854373d226faa38bddba8fcc7`
(reader `scope`, summary taken as `yaml.safe_load` parses it) fed through
`panel_findings.py id` returned that id exactly. **Reproduced.** All 11 recorded findings were then
re-fed through the CLI post-write and every one matched its stored id, so no cycle-0 summary drifted
during the splice.

| # | id | sev | reader | resolved_by | summary source |
|---|---|---|---|---|---|
| F1 | `PF-3781ff9d687a7f96acd48a819e76b00e` | high | should-not-exist | T-12 | digest table verbatim |
| F2 | `PF-717b076d285ff02ec57c3ca893f5fe9c` | high | scope | T-11 | digest table verbatim |
| F3 | `PF-7255aa4e7ce57178e474e734fbe218dc` | med | scope | T-11 | digest table verbatim |
| F4 | `PF-47028d6bcadb6f2d12a3356a887e1350` | low | should-not-exist | T-11 | digest table verbatim |

All four summaries were lifted from `panelc1b/digest.md:73-76` — the "Findings — reader's own
severity, unaltered" table — with no rewording, backtick-stripping or bold-stripping, because the
`transcription_rule` makes any alteration a different id. **None had to be authored.** The batch
context's four descriptions were used as cross-check only and agree with the digest text.

`T-12` (`Strip the trailing separator before taking the feature identity in the Build refusal
preflight`, `.claude/skills/harness/bin/gh-sync.py`) is the F1 closer, confirmed from the plan's own
task list rather than assumed; `T-11.depends_on` now includes `T-12`.

## The two judgement calls

- **F3 was lead-rated, and `lead` is not in the reader vocabulary.** Recorded under `scope` — F3 is
  a fourth instance of F2 on F2's own standard, so `scope` is the reader whose scope produced it.
  This follows the precedent the existing `transcription_rule` already records for LEAD-01. The
  lead rating is preserved in the appended `transcription_rule` sentence, not dropped.
- **The roster is keyed by reader, so it cannot hold two rows per reader.** It therefore describes
  cycle 1 only, each row carrying `cycle: 1` explicitly: `should-not-exist` **ran**,
  `scope` **ran**, `goalcheck` **skipped** with `persona: harness-goal-checker` and a reason naming
  that cycle 1 re-read the amended T-10/T-11 only and that goalcheck ran in cycle 0 under
  `2026-09-06-01-validator`. Cycle 0's roster stays recoverable from that run; the appended
  `transcription_rule` says so.
- **`scope` is recorded `ran`, never `skipped`.** Its work completed and was adopted; only its
  return envelope was refused by `validate-digest.py`'s `code_grade_bound_to_review`. That is a
  harness defect, not a reader outcome, and the appended rule sentence records the distinction.

## Acceptance — all green

1. `yaml.safe_load` clean. `panel.cycle == 1`, `len(findings) == 11`, cycle-0 dispositions unchanged
   (`resolved, open, resolved, open, open, open, resolved`), four new entries all `resolved` with a
   non-empty `resolved_by`; `should-not-exist: ran`, `scope: ran`.
2. Rulings check — all four `approval.rulings[].finding` ids resolve to live findings:
   `PF-1aa3b36ca…`, `PF-8bfef7ee6…`, `PF-23f51fd8e…`, `PF-6030c547e…` → **LIVE**.
3. `approval:` block byte-identical to `HEAD` (raw-text sha256 match above). Tasks 12, decisions 11.
4. `check-plan-routes.py <plan> → exit 0`, `0 violation(s) across 1 plan(s)`. The six `DEVIATION`
   lines (T-04, T-06, T-07, T-10, T-12) are the expected DEC-174 carve-out output; only
   `VIOLATION` gates.

## Open questions

- **Q1 (non-blocking, harness defect, already raised by the lead as Q1/Q3):** the panel's own
  `validate-digest.py` gap and the DEC-156/`check-domain.sh` digest-file conflict are unresolved, and
  the second produced the run-directory pair this transcription had to disambiguate by hand. Nothing
  in the plan record fixes either; both belong to the harness owner.
- No open question about the panel content itself. All four cycle-1 findings are recorded resolved
  against the amendment that landed; `severity_max` for cycle 1 was `high` but both high findings
  carry `disposition: resolved`, so INV-32 warns rather than gating.
