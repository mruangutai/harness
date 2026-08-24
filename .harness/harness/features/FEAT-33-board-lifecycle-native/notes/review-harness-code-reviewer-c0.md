# Code review — FEAT-33 board-lifecycle-native — c0

**Verdict: FAIL.** `severity_max: high`. Reviewed `faf409e8..e8a6058` (`git merge-base main HEAD`
`..HEAD`, no `[harness:human]` commits in range). Stage 1 (spec compliance) completed first, one
`verify: inspection` clause (SC-15) only partially satisfied. Stage 2 found two real gaps in
`board_lifecycle.py`'s exit-code contract — the exact surface the dispatch named as highest-risk —
both in code paths that already executed live writes against board 3/2 or that will on the next
run.

## must_fix

### 1. `cmd_provision`'s create-then-link sequence has no local catch — a mid-sequence failure
reports "nothing mutated" after a real mutation already landed, and a naive retry recreates the
exact duplicate-board disaster the module's own docstring says `project_resolve` exists to prevent.

`board_lifecycle.py:419-434`:
```python
created = factory_gh.project_create(owner, f"{repo_name} board")      # mutation 1 — lands
factory_gh.project_link_repository(created["id"], repo_name)          # mutation 2 — can fail
_out(f"... created project {created['number']} and linked {repo_name}; record number "
     f"{created['number']} in {repo_name}'s harness.json")
sys.exit(3)
```
Both calls are separate GraphQL mutations; neither is wrapped locally. If `project_create`
succeeds (a new Projects v2 board now exists on the operator's account) and
`project_link_repository` then raises `GhError` (repo lookup blip, transient network failure,
secondary rate limit — `run_gh` already implements rate-limit detection, so this is an anticipated
class of failure, not a hypothetical), the exception propagates uncaught out of `cmd_provision`
to `factory_cli.run`'s generic `expected` trap, which prints one line (naming only the value the
second call failed on — never the newly created project's number, since the success `_out(...)`
line never executes) and calls `sys.exit(EXIT_REFUSED)` = **2**.

`factory_cli.py`'s own documented contract for exit 2 is *"refused ... nothing mutated"*. That is
false here: the board was created. An operator reading exit 2 per that contract has no way to
learn the orphan project's number and, following the ordinary "exit 2, fix input, retry" pattern,
re-runs `provision` against the same `harness.json`. `project_resolve(owner, number)` still
resolves the OLD (unlinked, still-nonexistent-by-that-number) target to `None` — the config was
never updated with the number the previous run created — so the code takes the "no project"
branch again and calls `project_create` a **second time**, producing a second duplicate board.
This is precisely the scenario the module's own FIELD-ID-GAP and disaster-guard prose (lines
109-160) describes as the thing `project_resolve` exists to prevent; it is reachable through a
different gap the docstring does not address.

No test exercises this: every `provision` invocation in `test-board-lifecycle.py` (9 call sites,
checked by grep) passes no `fail_match`, so a `GhError` between `project_create` and
`project_link_repository` has never been simulated.

### 2. `cmd_retitle`'s apply loop contradicts its own docstring: a `GhError` from a rename call is
NOT caught locally, so it leaks to the generic trap and exits 2 ("refused, nothing mutated")
after real renames already landed.

Docstring (`board_lifecycle.py:42-44`): *"A `GhError` from either the enumeration or a rename call
propagates as exit 4, caught explicitly here exactly as `audit` and `reconcile` catch it — never
left to `factory_cli.run`'s generic trap, which would exit 2..."* The code does not do this. Only
the enumeration call is wrapped (`:756-764`); the apply loop is not:
```python
for num, old, new in to_rename:
    factory_gh.run_gh(["issue", "edit", str(num), "--repo", repo_name, "--title", new])  # unwrapped
    renamed += 1
    _out(f"renamed #{num}: {old!r} -> {new!r}")
```
Concrete scenario: mid-run over N tickets (this tool already renamed 188 real tickets per SC-19),
the call for the 51st ticket hits a transient `GhError`. 50 renames already landed. The exception
is uncaught, reaches `factory_cli.run`'s trap (`GhError` is in `expected`), and exits **2** — the
same code `factory_config`/caller errors use, and which the contract defines as "nothing mutated."
`retitle` is idempotent on a clean re-run, which limits the blast radius, but the exit code itself
is wrong and untested: none of the six `retitle` test cases in `test-board-lifecycle.py` (has
milestone / no milestone / already correct / truncated enumeration / dry-run / unknown repo)
inject a failure mid-rename-loop.

**Both 1 and 2 are the same defect class**: a bulk or sequential live-write operation in
`board_lifecycle.py` relies on `factory_cli.run`'s single generic trap instead of a local catch,
so a failure partway through a sequence of real mutations is reported with the code reserved for
"nothing happened." `reconcile`'s own apply loop (`:701-708`) gets this right — it catches
`(BoardError, GhError)` per finding and continues — and is the template both of these should have
followed.

## Stage 1 finding — SC-15 (`verify: inspection`) only half-satisfied

SC-15 requires (a) a six-row writer map in `DECISIONS.md` — present, `DECISIONS.md:6500-6508`,
amendment 4, and `DECISIONS-INDEX.md:214` reflects it — **and** (b) that
`.claude/skills/harness/SKILL.md` "names the main session as the owner of `start-task` **and of**
`gh-sync.py status <dir> <Status>` for a `main-session-direct` task." Only half of (b) is true:
`SKILL.md:197` does name main session for `start-task`. `SKILL.md:199`, the phase-transition row
for `status`, reads **"the actor performing the transition"** — no `main-session-direct` naming
at all, unlike every other row in the same table (`open`, `abandon`, `ship`, `backlog`,
`record-pr`, `closes` all name a specific role). `grep -n "main-session-direct"
.claude/skills/harness/SKILL.md` returns exactly two lines (`:134`, unchanged run-counting note;
`:197`, the `start-task` row) — the `status` row is not among them. Runtime behavior may still be
correct in practice (the orchestrator's own "entering validate" instruction at `SKILL.md:76` runs
the Review transition; `harness-plan.md:24`'s addition implies main session runs Ready) but the
inspection SC's literal text is not met, and this is the exact surface (`main-session-direct`
ownership of station writes) the feature exists to close per REQ-09 and the BRIEF's "the hole: a
station write is REMEMBERED, not caused" section. Medium severity — a documentation-traceability
gap, not a runtime defect on its own.

## What I checked and found sound (not re-reported)

- **The destructive path named in the dispatch** — `project_single_select_extend` replaces
  rather than appends. `cmd_provision` (`:454-462`) correctly computes `existing + missing` and
  sends the union; `factory_gh.project_single_select_extend` itself sends exactly what it is
  given, per its own docstring. `test-board-lifecycle.py` case 2 (`:370-388`) is a genuine
  discriminating test — it asserts `Backlog < Plan < Ready < Building < Review < Done` all appear
  in the one `updateProjectV2Field` call, which would fail if the union dropped any existing
  option.
- **`cmd_audit` / `cmd_reconcile` exit-code contract** — both explicitly catch `GhError` locally
  and exit 4, matching the docstring and DEC-186's inverse-of-the-mirror posture. `reconcile`'s
  apply loop correctly catches per-fix and continues (the right pattern, contrasted with the two
  `must_fix` items above).
- **T-07's `start-task` guard fail-open** — deliberate, and correctly scoped: both guard reads
  (`gh_board.board_stations`, `factory_gh.issue_view`) raise `factory_gh.GhError`, exactly the
  type the guard's `except` clause catches, so the documented "falls through to the original
  write" behavior is real, not a crash from a mismatched exception type. This posture did not
  leak into `board_lifecycle.py`'s control-plane subcommands, which do exit non-zero (modulo the
  two gaps above) — nor into `cmd_status`'s board writes, which follow the pre-existing
  `gh-sync.py` mirror posture (catch `BoardError` per write, print, continue; never gates),
  consistent with DEC-138/146 and distinct from the control-plane contract DEC-186 requires of
  `board_lifecycle.py` itself.
- **SC-20 / INV-26 widening (`check-state.sh:1345-1375`, T-22)** — bounded correctly: accepts
  `review`/`building` for a `done` task only when `feature.json.status == "Review"`; still flags
  `Building`-status and `Backlog`-card cases. `test-check-state.py` cases v.T22a-d
  (`:1605-1650`) are genuinely discriminating on both directions of the bound, not just presence.
- **#783's STATUS self-skip** — `_audit_findings`'s class 6 correctly gates `_status_findings` on
  `repo_name == own_repo`, matching the fix already landed for the measured 18/29 false-finding
  defect.
- **`_status_findings`'s three exemptions** (Abandoned, no parent, factory-lane issues) — read as
  documented; no Done exemption, matching D-22.
- Six-key station declaration, byte-for-byte case sensitivity (`_missing_options`), and
  `harness.json`'s `plan` key addition all match DEC-192/DEC-196 am.3 as decided.

## Open questions

None blocking a fix — both must_fix items have an obvious remedy (wrap the risky calls locally,
matching `reconcile`'s own pattern), and the SC-15 gap is a one-line SKILL.md edit.

## Severity ranking

1. **high** — `cmd_provision` create/link gap (finding 1): realistic transient-failure trigger,
   directly reproduces the disaster the code's own safety design exists to prevent, on a tool that
   writes to a live, already-migrated board.
2. **high** — `cmd_retitle` apply-loop gap (finding 2): same defect class, live tool, already run
   for real against 188 tickets; contract violation is real even though idempotency bounds the
   practical damage of a naive retry.
3. **med** — SC-15 `SKILL.md` naming gap: documentation/traceability, not a runtime defect.
