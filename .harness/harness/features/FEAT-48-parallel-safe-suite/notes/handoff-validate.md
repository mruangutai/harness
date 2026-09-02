# Handoff — FEAT-48, validate → ship — written at 27f8105b, seq-6

## Next

**Take the operator's ruling on B-1, then ship or re-pin.** Validate is complete: both c8
`must_fix` closed with proofs I took myself, `code_grade` clean at the pin, no criterion failure
from the panel, and pm grades **all ten SCs MET**
(`notes/research-FEAT-48-goalcheck-validate-c9.md`). The one open item is a **scope ruling only the
operator can make**: a test blinds `--mutation-check` by removing a directory's execute bit (B-1);
it is present since `b86ce66a`, fails no criterion, and `.claude/skills/harness/bin/**` is
`main-session-direct` (`plan.yaml:15-23`) so no lead may fix it. Briefing and the full B-row table:
`notes/ship-review-2026-09-02-c9.md`. **Ship** → open the PR, then file the unstruck B-rows.
**Fix** → `_record` swallows only `FileNotFoundError`; that moves the tip, so re-pin `review_sha`
and re-run panel + goal-check.

## Trust

- `code-grade.py --base origin/main --head 27f8105b` → exit 0, `PASSING: 70`, zero blocking records;
  `run_self_tests` CYC 3 / COG 0 / ABC 6.5 — mine, verified-at 27f8105b.
- All six in-file self-tests **DISCRIMINATE**, never-red cases NONE — three monkeypatch probes, no
  edit to the checkout; the file was rewritten in `993ac997` so c8's proof did NOT carry — mine,
  verified-at 27f8105b.
- The lstat guard covers **both** branches and is **reachable** (bypassing it makes the same
  injection escape in both). Scope the injection to `run_pool`'s own `os`: patching `os.lstat`
  globally makes `os.path.islink` false and measures the wrong branch — mine, verified-at 27f8105b.
- SC-03 both halves: T-03's verify verbatim exits 0; the ten pinned `ea6f51f` sites found
  **individually**, `missing [] extra []` — mine, verified-at 27f8105b.
- `__pycache__` rewritten and newly created ignored; loose `.pyc` reported; missing/empty watched
  dirs exit 2 — mine, verified-at 27f8105b.
- Suite green: `--kind all` exit 0 / 63 files / 8 workers / 48.29s / zero `FAIL` / zero `MUTATED` /
  clean tree; `--kind unit` emits `PASS test-suite-independence.py`; SC-01 `feature_schema.py`
  identical on mtime_ns+size+sha256 with `CRASHED` intact; SC-09 index `cmp`-identical — mine, at pin.
- **B-1 reproduces identically at `b86ce66a`, `e64e863e` and `27f8105b`**, so it is NOT a regression
  from `993ac997` — mine, verified-at all three.
- T-06's `verify:` exits 1 solely on `post == ["0"]`; the duplicate predates the fixes — mine, at pin.
- SC-01..SC-10 all MET on evidence re-taken at the pin —
  `notes/research-FEAT-48-goalcheck-validate-c9.md` — pm's, not mine.
- The `__pycache__` basename skip admits any payload at any depth and defeats symlink tracking when
  the symlink is named `__pycache__` — `notes/review-harness-security-reviewer-c9.md` — theirs,
  UNVERIFIED beyond §3 of `notes/validate-evidence-c9.md`.

## Dead ends

- Do not route a remedy to a dev squad: `bin/**` is `main-session-direct` by the DEC-174 carve-out,
  not a missing grant — `plan.yaml:15-23` — verified-at 27f8105b.
- Do not re-run the six self-tests, the ten pinned sites, or `code_grade` — this note's Trust.
- Do not call B-1 introduced by `993ac997`, nor a criterion failure: SC-10's six clauses all pass.
- Do not accept that DEC-211:6599-6604 is false. *"Caught only when…"* is a **necessary**-condition
  sentence. The overclaim is D-11's "Inside DIR it is vector-agnostic" — verified-at 27f8105b.
- Do not delete the duplicate `post-fix broken reads 0` line to green T-06's verify: it sits inside
  the fenced transcript T-06's intent mandates. The clause is wrong; all five graders concur.
- Do not read a red suite as a FEAT-48 defect before unsetting `HARNESS_AGENT_TYPE`, which fails 11
  checks in `test-plan-merge.py`, a file not in the diff — verified-at 27f8105b.

## Working set

- `notes/ship-review-2026-09-02-c9.md` · `notes/validate-evidence-c9.md`
- `notes/research-FEAT-48-goalcheck-validate-c9.md` · `notes/review-harness-security-reviewer-c9.md`
- `.claude/skills/harness/bin/run_pool.py` (`_record` :29-34, `_snapshot_directory` :37-49)
- `feature.json` (runs 21, cycles 8/10)
