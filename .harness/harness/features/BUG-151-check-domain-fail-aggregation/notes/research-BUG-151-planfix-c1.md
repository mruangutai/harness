# Plan fix cycle 1 — BUG-151 — both must_fix applied, plan re-loads clean

**All three edits landed; nothing else moved.** F-1 (med) and F-2 (low) from the cycle-0 goal-check
are applied as additive clarifications; the BRIEF's out-of-scope bullet now carries measured counts.
`approval.status` is still `pending`, `status` still `plan`, id set still `T-01 T-02 D-01 D-02`, and
`panel:`, `lanes:`, every `traces:` and both `verify:` blocks are byte-untouched.

## What changed

| Fix | Field | Amend exit | New sha256 |
|---|---|---|---|
| F-1 | `tasks:T-01.intent` | 0 | `d6c03d138cfdf815b50fe6f14ba0bfbd714630d962f2086588b1be6de1b3439c` |
| F-2 | `decisions:D-02.because` | 0 | `54ce209ce3bc51cc9a2d9e821dd9c92ed648b0610cc016ad40a357c5844d2a51` |
| — | `BRIEF.md:41-47` | n/a (direct edit) | — |

**F-1** adds a `STEP 0 RECOVERY ROUTE` paragraph between STEP 0 and STEP 1. It makes the doer check
`git status --porcelain tests/integration/test-check-domain.py` first, forbids shaing a dirty working
file, recovers the pre-change text with `git show 6d969ed3:tests/integration/test-check-domain.py`,
requires the copy at a **sibling path inside `tests/integration/`** (named
`tests/integration/_bug151_baseline_tmp.py`, with the `__file__`/ROOT reason stated and `/tmp`
explicitly excluded), and requires the copy be deleted with `git status --porcelain` clean at report
time. STEPS 1-5 and the closing `5207-5210` note are verbatim — verified by token, see below.

**F-2** keeps D-02's original reason verbatim and appends one `DEPARTURE FROM THE ISSUE` clause: #151
concluded the arithmetic self-check alone catches both directions; on disk it does not, because each
block couples printing to return inside one function, so an uncalled block prints nothing and returns
nothing and the arithmetic agrees with itself. Discovery is therefore added *alongside* the
self-check, not instead of it.

**BRIEF change 3** — counts re-measured here, both matched the goal-check note: 13 sites in
`test-validate-digest.py` (4280-4292), 8 in `test-bash-write-guard.py` (1316-1323), at 6d969ed3. The
bullet now says the issue's "different shapes" guess is falsified and that a follow-up starts from
measurement. **Scope unchanged** — both suites stay out; no REQ, no SC, no exclusion widened.

## Evidence

- `yaml.safe_load` → `pending plan ['T-01', 'T-02'] ['D-01', 'D-02']`.
- T-01 intent token check, all `True`: `6d969ed3`, `_bug151_baseline_tmp.py`,
  `DELETE the sibling copy`, `/tmp/bug151_probe.py`, `(a)`–`(f) captured`, `_AggTee`,
  `_aggregation_verdict`, `fails += run_bug151_selfcheck_cases()`, `5207-5210`.
- D-02 because: `#151` present, tail intact (`… not instead of it.`) — no plain-scalar `#` comment
  truncation; `amend` emitted it in a form `safe_load` reads whole.
- `panel.cycle: 0`, `lanes.resolved_at: 6d969ed3`, T-02 `verify:` still carries
  `assert len(blocks)==24`.
- `git status --porcelain` in the worktree: only the untracked feature directory. Scratch value files
  lived in `/tmp` and are deleted. No source file touched; no suite run.

## Open items for the panel

- The ruled-on advisory stands as ruled: T-01 STEP 1's red measurement is **kept**, untouched. I
  agree with the ruling — D-01 is deferred to that measurement, so removing it would leave a choice
  between two invariant strengths settled by preference.
- F-3 (REQ-02 holds only for `run_`-prefixed blocks) and F-4 ("net DELETION" is T-02-local, the
  ticket is ~+30 lines net) were not in this dispatch and remain unaddressed by design. F-4 is a
  framing claim inside `T-02.intent:141` that an operator could quote at signature.
