# Code Review — FEAT-41-one-station-vocabulary — c1 (FEAT41Panel1.CodeReviewC1)

Reviewed `9f2a070..fc08375` inside the worktree. Both stages ran unconditionally: Stage 1 (spec
compliance against BRIEF REQ-01..07, SC-01..09, SC-05/12 confirmed struck-not-deleted) and
Stage 2 (code quality, explicit file set + fail-open hunt), in that order.

**Collision note:** `notes/review-harness-code-reviewer-c1.md` already held a complete c1 review
(apparently Feat41Panel2's code reviewer — both panels share this worktree with no discriminator
in the path convention). I read it, cross-checked its claims independently rather than trusting
them, and this write replaces it. Flagged to Main via hub before overwriting.

**VERDICT: PASS.** Every one of the 8 dispatch items verified correct at source, with my own
commands/mutations, not on narrative alone. One real, previously-under-recorded gap (item 8 /
SC-08) and one coverage gap (F-04's realpath-evasion claim) — both med, both non-blocking, both
already substantively disclosed elsewhere in the record. Zero high+.

## The 8 dispatch items

1. **F-01 — closure correct.** `gh-sync.py:618,627` (`_record_station`): both failure prints
   lead `gh-sync: FAILED`. `_commit_terminal_station:649-699` says neither `SKIP` nor `FAILED`
   (`WARNING - station committed nowhere` / `WARNING - station recorded but NOT committed`) —
   read both bodies at source, asymmetry is deliberate and correct: unwritten is unrecoverable,
   uncommitted is not. `test-gh-sync.py:3218-3245`'s `_GATE_LITERALS = re.findall(r'if "([^"]+)"
   in combined:', open(post-merge-sweep.sh).read())` genuinely reads the literals out of the
   sweep — I ran the regex myself against `post-merge-sweep.sh` and it yields exactly
   `["gh-sync: SKIP", "gh-sync: FAILED"]` (lines 192, 206); the F-01 fixture drives both
   `_record_station` failure branches (unlink, garbled YAML) and asserts one of those literals
   appears. Not retyped, not vacuous.

2. **F-02 — closure correct, layers genuinely independent.** `_field_lines` (plan-merge.py:245)
   routes through `yaml.safe_dump`; I ran all six hostile probes (`Dr: Bob`, `#845 owner`,
   `yes`, `Bob:`, quote, embedded newline) through the actual function — every one round-trips
   exactly. Then I hand-simulated the OLD raw-interpolation (`f"{indent}{key}: {value}"`) against
   the same probes with bare `yaml.safe_load`: every one either raises `YAMLError` or reloads to
   a different value (`None`, `True`, `'Bob'` instead of the full string) — confirming
   `_verify_signature`'s value-comparison (plan-merge.py:271) is a real second net, not
   redundant decoration. `harness_merge.locked_update` (:121-149) confirmed: `transform` runs
   fully, including `_verify_signature`, before any bytes are written; a `MergeRefusal` leaves
   the file untouched. The "byte-identical on refusal" claim holds structurally, not just by
   assertion.

3. **F-03 — closure correct, fallback verified independently.** Read `plan-sign-gate.py:82-152`
   in full. Token scan skips a run of `--` before matching the verb (:130-146); `RAW_SIGN`
   (:96-97) independently skips separators in the text fallback. I confirmed with Python's
   `shlex` that the test's own fixture line — `echo it's fine; python3 .../plan-merge.py --
   sign-approval` — genuinely raises `ValueError: No closing quotation` (forces the fallback
   path), and that `RAW_SIGN` matches `plan-merge.py -- sign-approval` inside it. The fallback
   is exercised, not merely present.

4. **F-05 — closure correct.** Ran `code-grade.py --base 9f2a070 --head fc08375` myself (not
   trusted from the handoff): **0 `SEVERITY: high`, exactly 6 `RESULT: FAIL` records, all
   `GRADE: 2`** — `_verify_spliced` (plan-merge.py:313), `_task_status_line` (:678),
   `cmd_sign_approval.transform` (:833), `denies` (plan-sign-gate.py:112),
   `case_set_task_station_one_line` (test-plan-merge.py:625),
   `case_f02_sign_approval_...` (test-plan-merge.py:745). Each carries a specific, non-generic
   written reason (cohesive invariant, inherent branching-is-correctness, test-loop ABC) rather
   than "acceptable" — adequate. Grade 2 never gates per the tool's own contract; confirmed.

5. **T-18 struck — correct.** `git diff origin/main -- validate-digest.py test-validate-digest.py`
   is empty (0 lines) — byte-identical, confirmed directly, not narrative. `plan.yaml:1707`
   T-18's `status: abandoned` (not `done`) — read at source.

6. **T-14 → INV-33, no shadowing — correct.** `check-state.sh:264-387` is `# INV-32 BEGIN/END
   (FEAT-45 T-07)`; `:488-558` is a separate, non-overlapping `# INV-33` block (FEAT-41 T-14).
   `test-check-state.py` carries disjoint helpers (`_inv32_*` vs `_inv33_*`/`case_inv33a/b/c`)
   with no shared fixture path between them. No duplicate id, no shadowing.

7. **FEAT-45 migration — correct, `done` is true.** `git diff 9f2a070..fc08375 --
   FEAT-45.../feature.json FEAT-45.../plan.yaml` shows exactly the claimed edit: `"status":
   "Done"` deleted from feature.json, `status: done` inserted at plan.yaml's top level, nothing
   else touched. Parsed FEAT-45's plan.yaml directly: all 12 tasks `status: done`. In scope —
   REQ-06/SC-08 require exactly one station record per feature, and FEAT-45 shipped through the
   old path after T-04/T-07's sweep had already run, so this is finishing FEAT-41's own promise.
   **One thing I could not independently prove from the diff alone** (same gap the other c1
   code-reviewer flagged): whether the feature.json edit specifically routed through
   `feature_json_write.write_feature_json` (D-13's mandate) rather than a raw write — the diff
   shape (single clean key removal) is consistent with either. Not escalating: this is the same
   disclosed, unattributable-write gap the BRIEF's own "disclosure, not a decision" names for
   Bash-mediated plan.yaml/feature.json writes generally; it is not new to this item.

8. **BUG-1071 not migrated — right call, but SC-08 is measurably NOT literally true at this
   pin.** `.harness/harness/features/BUG-1071-inv32-era-guard/` has `feature.json` only — no
   `plan.yaml`, confirmed by directory listing — and its `feature.json` still carries
   `"status": "Review"`. **I ran T-07's own signed verify line verbatim**: `grep -l '"status"'
   .harness/harness/features/*/feature.json` returns
   `.harness/harness/features/BUG-1071-inv32-era-guard/feature.json` as a match — the literal
   verify block for this criterion does not pass today. Deferring is the right call (fabricating
   a plan.yaml to hold BUG-1071's only surviving station record would be worse), and it's
   disclosed in D-16 and the commit message — but **BRIEF.md's SC-08 text carries no
   cross-reference to this carve-out**, unlike SC-05/SC-12 which were explicitly amended to
   record their strikes. A reader of SC-08 alone would take it as true; it is not.
   **MED, non-blocking** (disclosed, deliberate, operator-ruling pending) — recommend SC-08 get
   the same amendment treatment SC-05/SC-12 already received.

## Stage 1 — spec compliance (independently re-run, not trusted from handoff/peer)

- SC-01: `grep -rn --exclude-dir=__pycache__ "_STATION_KEYS" .claude/skills/harness/bin/` → 0.
- SC-02: ran the criterion's own quoted-literal grep over non-test `.py`/`.sh` in `bin/` → 0.
- SC-04: `set_station(` call sites outside tests, read at source (not the BRIEF's own grep,
  which needs an escaped dot) — exactly 4: `board-station.py:175`, `board_lifecycle.py:1080`,
  `:1083`, `gh-sync.py:136`. Matches.
- SC-03: ran the anchored `status: pending` assertion over every live plan.yaml → 0 bad.
- SC-09: `git show fc08375:.../FEAT-40.../plan.yaml` → `status: done` at top level, confirmed.
- SC-05/SC-12: confirmed struck-and-recorded (not deleted) in `BRIEF.md`, matching PRINCIPLES
  rule 15 framing.
- harness.json: `github.board.stations` is exactly `["backlog","plan","ready","building",
  "review","done"]`, ordered lowercase list per D-04.
- D-01..D-16 read; D-15 (T-15 lane ratification) and D-16 (T-18 strike + renumber + migration)
  each state what happened rather than rewriting the signed block — add-only honored.

No scope creep found: every diffed file traces to a task's `files:` list or a `lanes:` row.

## Stage 2 — code quality / fail-open hunt (explicit file set)

Path note per dispatch: the "lib/" layout doesn't exist at this pin — `gh_board.py`,
`board_lifecycle.py`, `worktree_terminal.py`, `factory_config.py` are all under
`.claude/skills/harness/bin/`, same as the other named files. Used the real paths throughout.

- `gh_board.derive_station`/`project`/`_parent_station`/`_task_card`: read in full. Absence and
  illegal-value are cleanly separated code paths (never share one), matching D-11's mandate —
  an illegal station `raise`s `FleetError` naming the task/value; an undecidable one returns
  `None`/is omitted from the mapping, never guessed. `read_station`'s own docstring names
  exactly the "silence reads as proof" failure mode this feature exists to close, and its
  three-way `(station, reason)` return avoids it. No fail-open found here.
- `check-state.sh` INV-26 (:1884): confirmed the `_want is None` branch is now `bad.append(...)`
  (loud violation), not the old `continue` — matches SC-13's requirement, read at the site.
- `check-plan-routes.py` `_is_shipped` (:525): explicitly documented and structured to fail
  toward "examine" rather than "skip" on any unreadable/ambiguous input; the function's own
  docstring records the class of crash-exits-1-silently bug this replaces. No fail-open.
- **F-04 coverage gap (med, non-blocking) — verified, not just noted.** `test-check-domain.py`'s
  `_t09_spelling` (:2638) only exercises case-variant evasion (`Plan.yaml`, `PLAN.YAML`,
  `plan.YAML`) plus two negative controls; no case in `run_t09` drives `./`, `..`, doubled-slash,
  absolute-path, or a symlinked feature directory against `RE_PLAN_YAML` specifically, despite
  the code comment (`check-domain.sh:1065-1078`) and commit message asserting all five are
  "already denied." I checked the underlying mechanism myself: `_norm` (:984) resolves via
  `os.path.abspath` before the regex ever runs, which lexically collapses `.`/`..`/doubled-slash
  — sound. The symlinked-directory claim is also sound: the regex matches the path's *shape*
  (final component literally `plan.yaml`), so where an intermediate segment resolves is
  irrelevant to the match. The argument holds; it is simply untested for this specific pattern.
  Recommend a follow-up case in `_t09_spelling`, not a re-open of F-04.
- `plan-sign-gate.sh`/`.py` wiring: confirmed registered under `PreToolUse` → `Bash` matcher in
  `.claude/settings.json:31-46`, alongside `bash-write-guard.sh`/`gh-close-gate.sh` — not a
  guard that exists but never fires.
- No new bare `except:`, unchecked `subprocess` returncode, or "absence of a word means
  success" instance found beyond the F-01 class already fixed, across the explicit file set.

## Not examined

- `worktree_terminal.py`'s `_hook_feature_dir`/`inflight_registry` mechanism itself — it lives
  in `origin/main`, confirmed byte-identical to this feature's copy, so it is out of this diff's
  code-quality scope; security reviewer's lens per D-16's own framing.
- Full `check-state.sh`/`test-check-state.py` run — per this cycle's suite-serialization
  constraint, qa owns it exclusively; I read the specific INV-32/33 sites rather than executing
  the suite.

## Open questions

- Should `BRIEF.md`'s SC-08 be amended (same treatment as SC-05/SC-12) to name the BUG-1071
  carve-out explicitly, since its own literal verify line fails today and the criterion text
  gives no indication why? (non-blocking)
- Should `_t09_spelling` gain one case per named path-shape evasion (`./`, `..`, doubled-slash,
  absolute, symlinked dir) against `RE_PLAN_YAML`, closing the gap between "the argument is
  sound" and "the argument is tested"? (non-blocking)
