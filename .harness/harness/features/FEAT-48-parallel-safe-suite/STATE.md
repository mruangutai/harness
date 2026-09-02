# STATE

## Current

- feature: FEAT-48-parallel-safe-suite
- run: `2026-09-02-c9-validator` (panel, ESCALATE) and `2026-09-02-c9-product` (goal-check, PASS)
- squad: validator, then product
- status: awaiting_user — **buildable work is done**; one operator scope ruling stands before ship

Station `review`. `review_sha: 27f8105b`. HEAD is `de0b0d31`, whose only delta from the pin is
`feature.json`'s own `review_sha` line, so grading at the pin grades the shipped code.

**The headline: both c8 `must_fix` are closed, all ten SCs are met, and the only thing left is a
scope call on a coverage limit that has been in this code since its first commit.**

**What I verified at my own tier rather than accepting on report.**
- **`code_grade` is CLEAN.** `code-grade.py --base origin/main --head 27f8105b` → exit 0,
  `PASSING: 70`, zero blocking records. c8's nine records — three `high` — are gone at source:
  `run_self_tests` is now CYC 3 / COG 0 / ABC 6.5 against c8's 14 / 29 / 49.7, and `snapshot` is
  2 / 1 / 4.6 with the walk body extracted to `_snapshot_directory`.
- **The lstat guard is closed AND reachable.** Both the directory-symlink branch and the file
  branch route through `_record`'s `except OSError`. Fault injection scoped to `run_pool`'s own
  `os` (a globally patched `os.lstat` silently makes `islink` false and measures the wrong branch):
  `snapshot()` survives in both branches and drops exactly the raced entry; with the guard bypassed
  the same injection escapes in both. 15/15 probe assertions.
- **All six in-file self-tests DISCRIMINATE at this pin.** The file was rewritten wholesale in
  `993ac997`, so the c8 proof did not carry. Three monkeypatch probes, no edit to the checkout:
  blinding `scan_file` reddens the three red cases; an over-eager `scan_file` also reddens
  clean-controls and live-tree; patching `resolve_scan_root` never to refuse reddens root-refusal.
  **Never-red cases: none.**
- **SC-03 on both halves.** T-03's verify block verbatim → exit 0: root correct, `discovered 63`
  (floor 50), zero live findings, `selfcmp []`; and the three pinned `ea6f51f` blobs yield **all ten
  named sites individually, `missing [] extra []`**.
- **The `__pycache__` boundary is exactly SC-10's text.** Rewritten *and* newly created
  `__pycache__` entries ignored; a loose `.pyc` outside it reported `MUTATED`; missing and empty
  watched dirs exit 2.
- **Suite green:** `--kind all` exit 0, 63 files, 8 workers, 48.29s, zero `FAIL`, zero `MUTATED`,
  `git status --porcelain` empty before and after. `--kind unit` exit 0, 33 files, emits
  `PASS test-suite-independence.py`. `--check-kinds` exit 0 with zero test lines; `--kind nope`
  exit 2. SC-01: `feature_schema.py` identical at `st_mtime_ns 1788333510516825193` / 15881 /
  `943ef7a7…`, and the crashing-schema case still asserts exit 2 with `CRASHED`. SC-09: the index
  is `cmp`-identical.

**What stands between this and the ship — one operator ruling, and it is not an engineering call.**
- **A test can blind `--mutation-check` deterministically.** Create a directory under the watched
  `bin/`, write a payload into it, `chmod 0o600` — `os.walk` still lists the name, `os.lstat` on it
  raises `PermissionError`, `_record` swallows it, so the entry is absent from **both** snapshots
  and never compared. Exit 0, no `MUTATED`, payload persists. The security reviewer found it and
  I reproduced it end to end through the real CLI.
- **It is NOT a regression from this cycle.** Same reproduction against `run_pool.py` at
  `b86ce66a`, `e64e863e` and `27f8105b`: **exit 0, no `MUTATED` at all three.** The `except OSError`
  on the file leg has been there since the feature's first commit; `993ac997` only extended the same
  guard to the dir-symlink leg, which is what c8 asked for.
- **No approved criterion fails on it.** SC-10's three vectors, two refusals and `__pycache__`
  clause all pass, and pm grades all ten SCs MET at the pin.
- **No lead may fix it.** `.claude/skills/harness/bin/**` is `main-session-direct` by the DEC-174
  policy carve-out (`plan.yaml:15-23`). The ladder ends at the operator.
- **My recommendation: ship, record it as B-1, and fix the CLAIM in the same act (B-2).** The actor
  is a test deliberately hiding its own writes, which already has arbitrary same-user execution
  inside the suite. What should not ship unchanged is D-11's "Inside DIR it is vector-agnostic",
  which is now measurably false — this feature's own doctrine says an overclaim is worse than a gap.

**On the security reviewer's second charge, stated precisely.** DEC-211's *"caught only when it
changes an entry's mode, size or observed nanosecond mtime"* is a **necessary**-condition sentence,
so an uncaught write whose metadata changed does not falsify it. That charge does not hold on a
literal reading. What does overclaim is `plan.yaml` D-11's affirmative "Inside DIR it is
vector-agnostic". B-2 is scoped to that.

**Also open, none of them gating:** the `__pycache__` skip is keyed on the directory basename and
checked before the symlink branch, so anything under any `__pycache__` at any depth is invisible
(c8 M4, `med`); `snapshot()` never records plain directories, so a new empty directory is invisible;
D-11 and T-04's intent still mandate a `*.pyc` suffix skip the code no longer has (the code is the
safer one); T-06's `verify:` has never returned 0 since `b86ce66a` on a duplicate-line regex bug all
four panel members and pm rule a clause defect, not a note defect; two `low` items in
`test-check-fixture-secrets.py` and `_scan_statements`; the suite is green only with
`HARNESS_AGENT_TYPE` unset. Full table with IDs: `notes/ship-review-2026-09-02-c9.md`.

Budgets: `cycles_used` stays **8 of 10** — both leads reported **zero** send-backs and I routed no
`FAIL` back, so no rework loop ran. `runs` is now **21 of an informational 20 — crossed**. It stops
nothing, and the operator should see it: my read is that the runs earned their place, since the last
four each closed something real, and what the count actually signals is that the plan was
under-specified about what "the check catches" means, not that the runs were wasted.

## Open Questions

- **BLOCKING — operator scope ruling.** B-1: ship with the traversal-permission blind spot recorded
  as backlog, or fix `_record` (swallow only `FileNotFoundError`) before ship? A fix needs a re-pin
  and a re-run of this validation. Recommended: ship + record, with B-2 in the same act.
- **Needs a call.** B-9: the suite is green only with `HARNESS_AGENT_TYPE` unset —
  `test-plan-merge.py` fails 11 checks, in a file outside this diff. pm rules it a genuinely NEW
  criterion no REQ or SC covers, so adopting it is the operator's. pm and I recommend a separate
  `BUG-NN` rather than FEAT-48 scope.
- **Needs a call.** B-5, B-6 and the remaining backlog rows: fold into the ship, or take as rows?
  B-6 in particular leaves T-06 at `status: done` behind a verify that has never returned 0.
- **Record hygiene.** B-10: `BRIEF.md`'s `## Approval` block is byte-identical across `b86ce66a`,
  `e64e863e` and `993ac997`, so the approved SC-03 amendment carries no distinct re-signature act in
  the file. Only the operator's hand can date it.
- **Harness defects, not FEAT-48 findings.** B-13: `bash-write-guard.sh` blocks even `/tmp` writes
  for the read-only `harness-ui-reviewer`. B-14, carried from c8: `harness-qa` returned
  `severity_max: medium` where the enum is `med`, and `validate-digest.py` accepted it.
- Whether issue #1053 closes on ship remains the operator's call; its `## Scope` still reads
  "Folded into FEAT-47" and only the operator's hand fixes an issue body.
