# Ship review — BUG-2295-handoff-one-per-phase

**Ready to merge.** Validate c2 over pin `7d76c1cea576822760e8bc42432f8c01fc3c8031` (base `dd04e52a`) returned a clean panel: five readers PASS, zero findings, `severity_max: none`, `matrix_ok: true`, all four SCs met. The one c1 must-fix (mixed-case cycle names bypassed the refusal) was closed main-session-direct at `c4c93ef1` inside the signed ruling of 1 round / 45 min — 1 round and 21 rework minutes used. Merge, PR and push remain yours; nothing was pushed.

No report round was spawned. Assembled from the digests on disk:
- `runs/2026-11-22-01-patch-product/digest.md` (patch intake, PASS)
- `runs/2026-11-22-02-validate-validator/digest.md` (validate c1, FAIL)
- `runs/2026-11-22-03-validate-c2-validator/digest.md` (validate c2, PASS)
- goal-check notes `notes/research-BUG-2295-handoff-one-per-phase-goalcheck-validate-c{1,2}.md`; reader notes `notes/review-harness-{qa,code-reviewer,security-reviewer,ui-reviewer}-c{1,2}.md`; `notes/red-first-T-01.md`.

## Definition of done — graded (validate c2 goal-check)

| Perspective (as signed) | Verdict | SCs | Evidence |
|---|---|---|---|
| **operator** — I receive an actionable refusal when I try a cycle-suffixed handoff name, pointing me to the single note to supersede. Shipping retains its existing validation prerequisite and shipped history remains untouched. | met | SC-01, SC-04 | `notes/review-harness-qa-c2.md:17–21` (lowercase and mixed-case Write/Edit refusal red→green, canonical names accepted); `notes/review-harness-code-reviewer-c2.md:11–14` (cmd_ship predicate/exemption byte-identical to base; no FEAT-2225/FEAT-2229 note touched) |
| **code maintainer** — I have regression coverage for the filename rule without losing existing handoff shape checks, and the ship comment accurately explains the remaining prerequisite. | met | SC-02, SC-03 | `notes/review-harness-qa-c2.md:18–21` (cap, required-section, Done-when cases retained green); `notes/review-harness-code-reviewer-c2.md:12–14` (`gh-sync.py:2586–2590` comment distinguishes the preventive prerequisite from DEC-252's exemption) |

SC status at the pin: SC-01 met (automated), SC-02 met (automated), SC-03 met (inspection), SC-04 met (inspection). Decision dispositions DEC-174/225/252/254: all `keep`, preserved.

## What shipped

`check-domain.py` handoff write rule refuses `notes/handoff-<phase>-c<N>.md` through Write and reconstructable Edit, naming `notes/handoff-<phase>.md` (lowercase) as the note to supersede; `_RE_HANDOFF_CYCLE` is case-insensitive like `RE_HANDOFF`. `tests/integration/test-check-domain-post.py` gains `_handoff_cycle_suffix_cases` (build-c1, validate-c12, plan-c305, Build-c1, build-C1, VALIDATE-C12 × Write/Edit, plus exact canonical-name assertions). `gh-sync.py` `cmd_ship`: comment only. Diff dd04e52a→pin outside the feature dir: those three files.

## Lead summaries

- **Patch intake** (`runs/2026-11-22-01-patch-product/digest.md`, PASS, 0 cycles): BRIEF 48 lines, one task T-01 main-session-direct, four SCs; no panel (DEC-225).
- **Validate c1** (`runs/2026-11-22-02-validate-validator/digest.md`, FAIL): qa 6 red → 96 green over the lowercase rows; code and PM found the mixed-case bypass (`check-domain.py:2296` case-sensitive vs `:1486`); orchestrator probe confirmed it at the pin. One consolidated substance finding, high.
- **Fix** (main-session-direct, `c4c93ef1`, not a run): red 12 assertion failures against the 253cdf2a `check-domain.py`, green 117 ok (`notes/red-first-T-01.md` § c1 fix).
- **Validate c2** (`runs/2026-11-22-03-validate-c2-validator/digest.md`, PASS): qa independently reproduced the 12-failure RED and the 117-ok GREEN at the pin — executed, not transcribed; unit rc 0 (63 files), integration rc 0 (91 files); code confirmed `c4c93ef1` is an ancestor of the pin with an empty source/test delta; security and ui scoped out; goal-check both perspectives pass.

## Open questions and escalations

None. No escalations were raised in any run.

## Spend and ledger

`feature-record.py spend`: 3 runs, 27 wall-clock minutes, 128,593 tokens, rework window 21 min / 1 round (ruling: 1 round / 45 min). `cycles_used` 0 / 10 — the rework round was built outside any run, so it is counted by the `regate` judgement (`rework_rounds: 1`), not by run attribution; the c2 lead reported 0 send-backs. 4 judgements: mission (patch), continue (fix main-session-direct), regate (validate cycle 2), succession (continue). Runs 3 / 20 — well inside `max_total_runs`.

## Amendments

None — the build changed no signed task text.

overrule rate: 0/0

## UAT

Not required: no interactive surface (BRIEF `## Verification gaps`).

## Proposed backlog

| ID | Nature | Item |
|---|---|---|
| B-1 | chore | DEC-252 commentary (`DECISIONS.md:8223–8224`) says the handoff note is demanded nowhere, while `gh-sync.py cmd_ship` already demands it before ship for non-exempt plans — a pre-existing wording/behaviour conflict, outside T-01 (c1 goal-check row 2; c2 readers: not a finding). Correction needs DECISIONS.md ownership. |
| B-2 | enhancement | The unit suite has no dedicated test for the handoff filename rule; integration is the binding evidence (c1 qa, assessed nonblocking in c1 and c2). Optional. |

Rows not struck become backlog issues on ship acceptance; nothing else survived collation.
