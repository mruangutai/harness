# FEAT-48 plan-panel cycle 4 — code-reviewer (scope re-read at tip `a80d54a5`)

**BLUF: I would NOT sign this plan.** pm's F-01 survives my own independent re-derivation, at
my own severity of **HIGH** (not adopted from pm — separately re-earned below): the task set as
written leaves three groups of live-tree mutation hazard sites unowned, and this is not merely
cosmetic — it makes T-02's and T-03's `verify:` blocks **reddens on fully-correct execution of
those tasks as scoped**. That is a structural defect in the plan, not a stale number.

## F-01, independently re-derived — HIGH (my own severity)

I opened all seven cited sites myself, read the surrounding function, and confirmed basenames
and write targets. All check out exactly as cited:

- `test-bash-write-guard.py:899` (`open(path, "w")`) + `:901` (`os.chmod`) — writes
  `.feat50-bash-write-guard-<pid>.sh` into `HERE` = `os.path.dirname(os.path.abspath(__file__))`,
  i.e. live `bin/`. `grep -c "test-bash-write-guard" plan.yaml` → **0**. This file appears in
  **no task's `files:` list**, anywhere in the plan.
- `test-check-domain.py:3286`/`:3288` — `_feat50_mutant_between`/`_feat50_binding_red_case`
  writes `.feat50-check-domain-<pid>.sh` into `HERE` (same pattern). The file
  `test-check-domain.py` IS in T-01's `files:` list, but I read T-01's full `intent:` top to
  bottom (`plan.yaml:255-322`) and it addresses only `run_schema` case 3 (the
  `feature_schema.py` rewrite). `_feat50_mutant_between` is a separate function; T-01 never
  names it.
- `test-check-state.py:3598` (`open`), `:3600` (`copymode`), `:3613` (`unlink`) —
  `case_inv32_era_guard_is_load_bearing` (defined at `:3584`) writes
  `.check-state-inv32-era-mutant.sh` — confirmed a **distinct basename** from
  `.check-state-inv32-mutant.sh` at `:3286` (T-02's D-10-cited FEAT-45 site). T-02's `files:`
  list does include `test-check-state.py`, but T-02's `intent:` names exactly four sites
  ("THE FOUR SITES", `plan.yaml:373-382`) and this era-guard function is not one of them.

**Claim (a) — is the task set as written leaving these unowned?** Yes, confirmed by direct
grep and by reading every task's `intent:` in full. `test-bash-write-guard.py` is unowned
outright (no task even lists the file). The other two are file-list-adjacent but
intent-excluded — an implementer following the `intent:` prose literally, which is what
Stage-1 spec compliance holds them to, would never touch either site.

**Claim (b) — does this make T-02's and T-03's verify exit 1 on correct work?** Confirmed by
tracing execution, not assumed:

- **T-02** (`plan.yaml:340-374`): the verify block runs `test-check-state.py` and
  `test-feature-worktree.py` as subprocesses while a background thread busy-polls `bin_dir`
  for any name outside the pre-run snapshot (`appeared`), and fails if `appeared` is non-empty.
  I confirmed `case_inv32_era_guard_is_load_bearing()` is called unconditionally from the
  case-list at `test-check-state.py:4317` — it runs on *every* invocation of the file, not
  behind a flag. It writes `.check-state-inv32-era-mutant.sh` into the exact directory the
  poll thread watches, and the file persists across two nested `_inv32_run` subprocess
  invocations before its `finally: os.unlink(mutant)` — a real, multi-subprocess dwell window,
  not a sub-millisecond race. A busy-loop `os.listdir` poll running concurrently in the parent
  process will observe it. So even a T-02 that perfectly fixes its four named sites still runs
  a `test-check-state.py` that trips T-02's own verify block, because the hazard T-02 doesn't
  own lives in a file T-02's verify block executes.
- **T-03** (`plan.yaml:430-463`): the verify block requires `live.returncode == 0` from
  invoking the newly-built static scanner with no arguments (a full live-tree scan). The
  scanner's own spec (`plan.yaml:495-505`) taints a name "whose value expression *mentions* a
  tainted name" — I checked the three unowned sites against that literal rule: `HERE`
  (`test-bash-write-guard.py:16`, `test-check-domain.py:17`) is `os.path.dirname(...__file__)`
  — directly tainted; `SCRIPT` in `test-check-state.py:17-19` is
  `os.environ.get(...) or os.path.join(os.path.dirname(os.path.realpath(__file__)), ...)` —
  `__file__` appears in the RHS expression, so it also taints under the stated rule. All three
  writes (`open(path,"w")` / `open(mutant,"w")`) are then flagged sinks per the same spec. A
  scanner built faithfully to the intent's own rule **will** report non-zero on the live tree
  regardless of how well T-01/T-02 execute their assigned four-plus-two sites, because three
  more violations exist in code no task touches. This is corroborated from inside the plan
  itself: T-03's own intent text (`plan.yaml:617-621`) states the live tree was **THIRTEEN**
  findings at `ccf674a` (ten historical + FEAT-45's fourth site, "which T-02 removes") — i.e.
  the plan's own arithmetic assumes zero remain after T-01+T-02. That arithmetic is stale: the
  rebase added seven more (13 + 7 = 20), none of which any task removes, so T-03's "zero
  findings on the live tree" case cannot pass under a faithful implementation.

**No tree exists in which T-02 and T-03 pass as currently scoped.** Not "reddens sometimes" —
reddens on every faithful, spec-compliant execution of the plan as written, because the gap is
in files/functions no task is instructed to touch.

## Satisfiability sweep — explicit yield: **2** (T-02, T-03)

I swept all six `verify:` blocks for "can it redden on broken work, and does some tree exist
where it passes":

| Task | Verified against | Result |
|---|---|---|
| T-01 | feature_schema.py bytes/mtime + case markers, scoped to that one file's own subprocess run | satisfiable — no external hazard reachable through this check |
| T-02 | polls whole `bin_dir` during `test-check-state.py`/`test-feature-worktree.py` runs | **UNSATISFIABLE as scoped** — see F-01(b) above |
| T-03 | full-tree static scan, requires zero live findings | **UNSATISFIABLE as scoped** — see F-01(b) above |
| T-04 | `--mutation-check` pointed at fixture tempdirs (`w`, `tempfile.mkdtemp()`), never `bin_dir` | satisfiable — isolated from the live-tree hazard entirely |
| T-06 | `--check-kinds` (registration-agreement check only, does not execute the suite) + measurement-note regex | satisfiable |
| T-05 | DECISIONS.md section content + index regeneration, separator-agnostic per its own text | satisfiable |

Method cross-checked against a known positive: T-02's poll mechanism is the *same* poll shape
D-10 already describes catching FEAT-45's fourth site pre-rebase (`plan.yaml:150-153`,
"polling the live bin directory... reports appeared [...]"), so a poll picking up a real
concurrent write is an established, not hypothetical, effect of this exact code shape.

## Item 3/4 — did the rebase invalidate other path-specific assertions?

- **`check-state.sh`**: plan.yaml makes no line-specific claim about this file (only the
  general "test-check-state.py is the test of check-state.sh" sentence, `:332`). Nothing to
  invalidate.
- **`plan-merge.py` / `test-plan-merge.py`**: `grep -c "plan-merge" plan.yaml` → **0**. **The
  plan asserts nothing about this file** — explicit ruling, not silence. I checked the
  substance anyway: `test-plan-merge.py` (1815 lines, +827 on the rebase) uses `HERE`/`CLI`/
  `TEMPLATE_PLAN` only as subprocess arguments and read targets — no `open(CLI/HERE/
  TEMPLATE_PLAN, "w")`, no `shutil` write onto them (grepped, zero hits) — so it introduces
  **no new live-tree mutation site** despite the size, and the BUG-1128 verbs
  (`set-task-station`, `set-feature-station`, `amend`) it adds to `plan-merge.py` are unrelated
  to FEAT-48's scope. It was already registered in `INTEGRATION_SCRIPTS` before the rebase (not
  a new file), so **no discovered-count or registration assertion FEAT-48 makes is affected**.
  I independently re-ran D-03's exact walk rule (prune `.git`/`.claude/worktrees`/
  `node_modules`/`.venv`, collect `test-*.py`/`test_*.py`) and measured **59** files, all under
  `.claude/skills/harness/bin`, confirming T-03's `>= 50` floor holds regardless.
- `test-bash-write-guard.py` / `test-check-domain.py`: covered under F-01 above.

## pm's other findings — re-measured, not adopted

- **F-02** (T-02 anchors stale): confirmed. `.mutant-check-state-t14.sh` is now at `:2241`
  (was `2109-2133`), `.mutant-check-state-t10.sh` at `:2377` (was `2245-2269`),
  `.check-state-inv32-mutant.sh` at `:3286` (was `3066-3088`). **I rate this LOW, not med** —
  T-02's own intent text already says "Re-derive the line numbers before you edit; do not
  trust these four anchors... The basenames are the durable identifier" (`:381-382`), which is
  exactly the self-mitigation that makes stale anchors non-blocking here.
- **F-03** (58→59 discovered files): confirmed by direct measurement above (59). Floor of 50
  unaffected. LOW, non-gating, agree with pm.
- **F-05** (190/DEC-207 → 192/DEC-209): confirmed — `grep -c "^## DEC-"` gives **192**, last
  heading is `DEC-209`. LOW: the plan's own text calls this "a convenience, never a constraint
  the gate enforces" (`plan.yaml`, T-05 intent), and the verify block is separator-agnostic and
  does not check the count or heading number. Agree with pm.
- **F-06/F-07** (#1053 Scope, BRIEF open question stale): confirmed via `gh issue view 1053`
  — Scope section still reads "Folded into FEAT-47." Confirmed FEAT-47's `plan.yaml` D-13
  already settles the reverse ("FEAT-48 ships WHOLE and lands BEFORE this feature"). Both are
  doc staleness only — LOW, agree with pm, worth a cleanup pass before merge but not a plan-sign
  blocker on their own.
- **"13 hazard sites" → 20/59**: this is the same defect as F-01, not a separate finding — I
  used it above as internal corroboration (13 + 7 new unowned sites = 20).

## Standing hunt (orphan REQ / depends_on / verify-vs-delete)

- REQ-01..REQ-08 all defined in BRIEF.md and all traced by at least one task; no orphan REQ,
  no task tracing to a REQ that doesn't exist.
- `depends_on` forms one valid chain: T-01[]→T-02[T-01]→T-03[T-01,T-02]→T-04[T-03]→T-06[T-04]→
  T-05[T-06]. No cycle, no forward reference.
- No verify block asserts a case a predecessor task deletes (T-04/T-05/T-06 verify blocks
  don't reference content T-01/T-02/T-03 remove).

## Exit-state confirmation

`git -C <worktree> status --porcelain` at the end of this run:
```
 M .harness/harness/features/FEAT-48-parallel-safe-suite/feature.json
 M .harness/harness/features/FEAT-48-parallel-safe-suite/observations/harness-pm.md
 M .harness/harness/features/FEAT-48-parallel-safe-suite/plan.yaml
?? .harness/harness/features/FEAT-48-parallel-safe-suite/STATE.md
?? .harness/harness/features/FEAT-48-parallel-safe-suite/notes/research-FEAT-48-goalcheck-plan-c4.md
```
`git diff --numstat plan.yaml` → `7  6` (matches the described pre-existing diff exactly; I
wrote nothing to it). `approval.status` still reads `pending` in the working tree. No
`review_sha` written anywhere by me. This note is the only file I created.

## Open questions

None blocking beyond what's already in the DIGEST — F-01's remedy (own each of the three
newly-discovered site groups with a task, or explicitly amend D-10's census) is the operator's
or the plan author's to make; it is not mine to prescribe an implementation for.
