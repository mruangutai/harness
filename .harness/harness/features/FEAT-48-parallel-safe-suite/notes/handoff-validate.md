# Handoff — FEAT-48, validate → ship — written at 27f8105b, seq-7

## Next

**Ship. Validate is complete and PASS; the operator has ruled and nothing is open.**
Both c8 `must_fix` are closed with proofs re-taken at the pin, `code_grade` is clean, and pm grades
**all ten SCs MET** (`notes/research-FEAT-48-goalcheck-validate-c9.md`). The panel's one escalation
— a test blinding `--mutation-check` by removing a directory's execute bit — is **settled by
ruling, not left open**: ship it, record it as B-1, fold nothing in
(`notes/answers-2026-09-02-c9.md`). The ship phase owes three acts and no engineering: open the PR
at the current tip with **`review_sha` UNMOVED at `27f8105b`**; file **B-1 … B-15** as backlog
issues on ship acceptance (DEC-138), table in `notes/ship-review-2026-09-02-c9.md`; close issue
**#1053** through `gh-sync.py ship`. **B-9 becomes its own `BUG-NN`.** No source, plan or BRIEF
change is authorised.

## Trust

- `code-grade.py --base origin/main --head 27f8105b` → exit 0, `PASSING: 70`, zero blocking records;
  still 0 at the tip, whose delta from the pin is feature artifacts only — mine, at 27f8105b.
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
- T-06's `verify:` exits 1 solely on `post == ["0"]`; accepted as B-6, NOT fixed — mine, at pin.
- SC-01..SC-10 all MET on evidence re-taken at the pin —
  `notes/research-FEAT-48-goalcheck-validate-c9.md` — pm's, not mine.
- `check-state.sh`: **zero FEAT-48 violations**; the two VIOLATIONs are FEAT-51's, pre-existing and
  outside this feature. One FEAT-48 note, INV-22 — mine, verified-at the tip.

## Dead ends

- Do not move `review_sha`. The rulings authorised no code change and the pin is `27f8105b`.
- Do not fold any backlog row into this feature — ruling 5. B-1 … B-15 are issues filed at ship.
- Do not re-run the six self-tests, the ten pinned sites, or `code_grade` — this note's Trust.
- Do not re-open B-1 as a fix: ruled accepted, it fails no criterion, and `bin/**` is
  `main-session-direct` by the DEC-174 carve-out — `plan.yaml:15-23` — verified-at 27f8105b.
- Do not accept that DEC-211:6599-6604 is false. *"Caught only when…"* is a **necessary**-condition
  sentence. The overclaim is D-11's "Inside DIR it is vector-agnostic", scoped as B-2.
- Do not delete the duplicate `post-fix broken reads 0` line to green T-06's verify: it sits inside
  the fenced transcript T-06's intent mandates. The clause is wrong; all five graders concur.
- Do not read a red suite as a FEAT-48 defect before unsetting `HARNESS_AGENT_TYPE`, which fails 11
  checks in `test-plan-merge.py`, a file not in the diff — verified-at 27f8105b.

## Working set

- `notes/answers-2026-09-02-c9.md` · `notes/ship-review-2026-09-02-c9.md`
- `notes/validate-evidence-c9.md` · `notes/research-FEAT-48-goalcheck-validate-c9.md`
- `feature.json` (review_sha 27f8105b, runs 21, cycles 8/10) · `plan.yaml` (`status: review`)
