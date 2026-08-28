# Handoff — FEAT-37, build (partial) — written at e73d545

## Next

**The operator executes T-02, then build resumes.** T-02 is `main-session-direct` (`plan.yaml`
`- id: T-02`; issue #906) because `check-domain.sh --resolve` returns NOBODY on
`.claude/skills/harness-team/SKILL.md`. It is the ONLY runnable task: T-01 unblocks T-02 and T-04,
and T-02 unblocks T-05 which unblocks T-06, with T-01 and T-04 already done. After T-02 lands,
dispatch **T-05 to `harness-documentor` via product-lead** (DECISIONS.md and DECISIONS-INDEX.md
resolve to documentor, NOT eng), then **T-06 to the same**, then the qa segment, simplify,
`review_sha` pin, panel, goal-check. Set each task `building` in plan.yaml BEFORE
`gh-sync.py start-task`, and record `done` in the same act as its commit.

## Trust

- T-01 and T-04 both PASS, verify blocks re-run by me not taken on report: `T01_PASS` and
  `bound=0 registry=0 validatedigest=0` then `T04_PASS` — verified-at e73d545
- `test-validate-digest.py` exits 0 BOTH before and after T-04's edit; the two-sided identity is the
  evidence that a gate downstream of the diff is unaffected — verified-at e73d545
- The detector widening discriminates: DECISIONS.md occurrence failures went 2 to 3, the new one at
  line 6872 — predicted before the run, then re-confirmed by me — verified-at e73d545
- Expected red today, and ONLY this: `--group playbook` (closes at T-02), `--group coverage`
  (closes at T-05), `--group bound` with three DECISIONS.md failures `_6869_1 _6870_2 _6872_3`
  (all close at T-06). `--self-check` and `--check-kinds` exit 0 — verified-at e73d545
- The two `inflight_registry.py_339` bound failures are CLOSED by T-04; either returning is a
  regression, not expected red — verified-at e73d545
- `check-state.sh` exits 1 on two INV-26 violations I CANNOT clear: T-01 and T-04 cards read
  Building while the plan says done. INV-26 widens only at feature.json status `Review`
  (`check-state.sh:1522`), and the ONLY writer of the done station is `cmd_ship`
  (`gh-sync.py:1257`), a main-session subcommand — verified-at e73d545
- After the strike, T-02 is the ONLY main-session-direct task, though `lanes:` still lists two
  NOBODY surfaces — the second belonged to the struck task — verified-at e73d545

## Dead ends

- Do NOT grade or score SC-08 from this build — a spawned agent loads skills from the MAIN CHECKOUT;
  the eng lead's mid-run refusal printed the OLD sentence, confirming it — D-13, `BRIEF.md`
  — verified-at e73d545
- Do NOT treat the three DECISIONS.md bound failures as a regression — they are T-06's to close, and
  the third exists BECAUSE the detector was widened — `plan.yaml` D-11 — verified-at e73d545
- Do NOT restore the struck REQ-08/SC-09 regression — operator strike at signature, filed as issue
  #903, refuse and cite it — source: operator dispatch 2026-08-27
- Do NOT trust any line number in plan.yaml — measured at 8fc87f8 before origin/main (FEAT-42)
  merged. Four already found stale: `UNIT_SCRIPTS` 30 not 17, registry site 339 not 274. Find every
  site by TEXT — verified-at e73d545
- Do NOT run the qa segment before T-06 lands — the matrix cannot be green, the red is by design
  — verified-at e73d545
- Do NOT touch `refusal_lines` in inflight_registry.py — FEAT-42 already fixed its citation and
  T-04's intent forbids it — verified-at e73d545

## Working set

- `.harness/harness/features/FEAT-37-lead-stop-and-wake/plan.yaml`
- `.harness/harness/features/FEAT-37-lead-stop-and-wake/STATE.md`
- `.harness/harness/features/FEAT-37-lead-stop-and-wake/runs/2026-08-27-01-t04-eng/digest.md`
- `.harness/harness/features/FEAT-37-lead-stop-and-wake/runs/2026-08-27-01-t01-eng/digest.md`
- `.claude/skills/harness/bin/test-lead-stop-and-wake.py`
