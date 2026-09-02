# STATE

## Current

- feature: FEAT-48-parallel-safe-suite
- run: `2026-09-02-c9-validator` (panel, ESCALATE) and `2026-09-02-c9-product` (goal-check, PASS),
  closed by the operator's rulings in `notes/answers-2026-09-02-c9.md`
- squad: validator, then product
- status: **validate complete — PASS, ready to ship**

Station `review`. `review_sha: 27f8105b`, **unmoved** — the operator's rulings authorised no code
change, and the only commits since the pin are this feature's own `.harness/` records.

**The headline: validate is done. Both c8 `must_fix` are closed with proofs re-taken at the pin,
all ten success criteria are met, `code_grade` is clean, and the one escalation is settled by
operator ruling rather than left open.**

**What I verified at my own tier rather than accepting on report.**
- **`code_grade` is CLEAN.** `code-grade.py --base origin/main --head 27f8105b` → exit 0,
  `PASSING: 70`, zero blocking records; still 0 at the current tip, whose delta from the pin is
  feature artifacts only. c8's nine records — three `high` — are gone at source: `run_self_tests`
  is CYC 3 / COG 0 / ABC 6.5 against c8's 14 / 29 / 49.7, `snapshot` is 2 / 1 / 4.6 with the walk
  body extracted to `_snapshot_directory`.
- **The lstat guard is closed AND reachable.** Both the directory-symlink branch and the file branch
  route through `_record`'s `except OSError`. Fault injection scoped to `run_pool`'s own `os` — a
  globally patched `os.lstat` silently makes `islink` false and measures the wrong branch:
  `snapshot()` survives in both branches and drops exactly the raced entry, and with the guard
  bypassed the same injection escapes in both. 15/15 probe assertions.
- **All six in-file self-tests DISCRIMINATE.** The file was rewritten wholesale in `993ac997`, so
  c8's proof did not carry and I re-took it. Three monkeypatch probes, no edit to the checkout;
  **never-red cases: none.**
- **SC-03 on both halves.** T-03's verify verbatim → exit 0: root correct, `discovered 63` (floor
  50), zero live findings, `selfcmp []`; the three pinned `ea6f51f` blobs yield **all ten named
  sites individually, `missing [] extra []`**.
- **The `__pycache__` boundary is exactly SC-10's text**, and the suite is green: `--kind all`
  exit 0, 63 files, 8 workers, 48.29s, zero `FAIL`, zero `MUTATED`, clean tree; `--kind unit` emits
  `PASS test-suite-independence.py`; `--check-kinds` exit 0 with zero test lines; `--kind nope`
  exit 2; SC-01 `feature_schema.py` identical on mtime_ns+size+sha256 with the `CRASHED` assertion
  intact; SC-09 index `cmp`-identical.
- **pm grades all ten SCs MET**, every row re-taken at the pin
  (`notes/research-FEAT-48-goalcheck-validate-c9.md`).

**The escalation, and how it was settled.** The security reviewer found — and I reproduced end to
end through the real CLI — that a test can blind `run_pool.py --mutation-check` by creating a
directory under the watched `bin/`, writing a payload into it and removing its execute bit:
`os.walk` still lists the name, `os.lstat` raises `PermissionError`, `_record` swallows it, so the
entry is absent from **both** snapshots and never compared. Exit 0, no `MUTATED`, payload persists.
**It is not a regression:** the same reproduction gives exit 0 with no `MUTATED` at `b86ce66a`,
`e64e863e` and `27f8105b` alike. It fails no criterion, and `.claude/skills/harness/bin/**` is
`main-session-direct` (`plan.yaml:15-23`), so the ladder ended at the operator.
**Ruling: ship, record it as B-1, fold nothing in.** All fifteen backlog rows accepted, B-9 taken as
its own bug, issue #1053 to close through the ship. Full record:
`notes/answers-2026-09-02-c9.md`.

**On the security reviewer's second charge, stated precisely.** DEC-211's *"caught only when it
changes an entry's mode, size or observed nanosecond mtime"* is a **necessary**-condition sentence,
so an uncaught write whose metadata changed does not falsify it — that charge does not hold on a
literal reading. What does overclaim is `plan.yaml` D-11's affirmative "Inside DIR it is
vector-agnostic". B-2 is scoped to that and nothing wider.

**Accepted and recorded, not fixed here (B-1 … B-15).** The traversal-permission blind spot; the
`__pycache__` basename skip that admits any payload at any depth and defeats symlink tracking when
the symlink is named `__pycache__`; `snapshot()` never recording plain directories; D-11 and T-04's
intent still mandating a `*.pyc` suffix skip the code no longer has (the code is the safer one);
T-06's `verify:` never having returned 0 since `b86ce66a` on a duplicate-line regex bug all five
graders rule a clause defect; two `low` items in `test-check-fixture-secrets.py` and
`_scan_statements`; the `HARNESS_AGENT_TYPE` dependence; the unre-signed `## Approval` block; issue
#1053's stale `## Scope`; BACKLOG-C; and two harness defects. Table with natures:
`notes/ship-review-2026-09-02-c9.md`.

Budgets: `cycles_used` stays **8 of 10** — both leads reported **zero** send-backs, I routed no
`FAIL` back, and the escalation was settled by ruling rather than rework, so no cycle was spent.
`runs` is **21 of an informational 20 — crossed**. It gates nothing. My read: the runs earned their
place, since the last four each closed something real; what the count signals is that the plan was
under-specified about what "the check catches" means, not that the runs were wasted.

## Open Questions

- **None blocking.** Every question this seam raised is settled in `notes/answers-2026-09-02-c9.md`.
- **Carried into the ship phase, by ruling and not as open work:** file B-1 … B-15 as backlog issues
  on ship acceptance (DEC-138); close issue #1053 through `gh-sync.py ship`, whose `## Scope` still
  reads "Folded into FEAT-47" and which only the operator's hand can edit; open B-9 as its own
  `BUG-NN`.
