```yaml
VERDICT: FAIL
DIGEST:
  headline: "Both cited mutation claims (S2 count, edit-route redden count) hold, but the deepest mutation-proof I ran surfaces a THIRD, unmeasured squad inaccuracy: case 22's destination/content/shape assertions are silently vacuous on this OS (macOS symlink) and a genuine truncating-write regression gives a false PASS on its 'not truncating' check; the pre-domain edit route (harness-hooks.ts:234) is confirmed, by mutation, genuinely uncovered."
  suite: fail
  failures: 1
  matrix_ok: true
  kinds:
    - { kind: unit, state: satisfied, cmd: ".agents/skills/harness/bin/run-unit-tests.sh --kind unit", named_tests: 455 }
    - { kind: integration, state: satisfied, cmd: ".agents/skills/harness/bin/run-unit-tests.sh --kind integration", named_tests: 581 }
    - { kind: ts-unit-omp-hooks, state: satisfied, cmd: "bun test ./.claude/skills/harness/bin/omp-hooks.test.ts (run manually — NOT wired into any declared test_kinds cmd)", named_tests: 48 }
  coverage_gaps:
    - "harness-hooks.ts:234 (preDomain's edit branch, PreToolUse, no --post) — every new edit-route case drives tool_result (postDomain) only; zero tool_call cases use toolName edit. Mutation-confirmed unreachable by the suite (neutering it: 47 pass/1 fail, byte-identical to baseline's 1 pre-existing environmental fail)."
    - "test-factory-decompose.py case_22's 3 richest assertions (dest-is-fixture, source-in-same-dir, source-parses-as-YAML-with-factory-key) never execute on this OS: fake_open/fake_replace gate on os.path.abspath(x)==os.path.abspath(feature_json_path), but harness_merge resolves via os.path.realpath, and macOS resolves /var -> /private/var. Directly verified with REAL captured values from a live run: abspath('/private/var/folders/.../feature.json') != abspath('/var/folders/.../feature.json') -> False. The gate never fires for any call, on any of the ~90 scenarios that reach it, not just case 22."
    - "omp-hooks.test.ts is matched by test_kinds.unit's detect glob (**/*.test.*) but NOT executed by unit's cmd (run-unit-tests.sh's UNIT_SCRIPTS array has no bun/TS entries at all) — the kind reports satisfied for Python while the TS suite this diff most changes has no standing execution path in harness.json. I ran it manually; nothing in the matrix machinery would have."
    - "No BRIEF.md/plan.yaml exists for this feature (handoff-plan.md: 'There was no plan seam... Do not grade this against success criteria. There are none.'). sc_evidence is empty because there is nothing to cite evidence against."
  sc_evidence: []
  open_questions:
    - { id: Q1, question: "case_22's write-side path-matching bug (see coverage_gaps) predates this diff — case_22 is byte-identical pre/post (git diff confirms zero changes to that block). It is not something S1-S4 introduced, but it means the regression guard the squad's own Q3 relied on ('case 22's hooks no longer intercept...') was never a real mechanism either way: case_22 never changed, and its content checks were already vacuous on this OS before this feature touched anything. Should case_22 be fixed to compare against harness_merge.require_destination's resolved path (or os.path.realpath both sides) so its 3 dead assertions and its truncating-write detection actually run? Currently only 'os.replace was called at least once' is load-bearing there.", blocking: false }
    - { id: Q2, question: "The build handoff and analysis note both say 'six edit-route cases' / 'bun test ... 43 -> 44' (S1's own proof text). git diff shows exactly FIVE new test() blocks added, and the suite moved 43 -> 48. More coverage than promised is not a defect, but the count claims in both governing notes are measurably wrong and should not be cited as-is by a future reader.", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/BUG-1030-stale-anchor-write-hazard/notes/review-harness-qa-c0.md
```

# QA gate — BUG-1030-stale-anchor-write-hazard @ 83282dea

**Gate-only, read-only on source (DEC-174). No test/fixture/source authored.** All mutation
proofs ran against **scratch copies outside the worktree** (`/tmp/qa-scratch-*`, deleted after use)
or, where `bash-write-guard` denied a source write inside the worktree even from `/tmp` when the
sed target argument was relative, I used an absolute target path from `cwd /` — every attempted
mutation is labelled below by exactly how it was applied. **`git status --porcelain` in the
worktree, both before and after every mutation round, shows zero writes of mine** — only three
sibling reviewers' untracked artifact files, none touched.

## Phase 1 (no source) — what should exist

No `BRIEF.md`, no `plan.yaml` — `handoff-plan.md` states this plainly: "There was no plan seam...
Do not grade this against success criteria. There are none." From issue #1030 and the analysis
note's own S1/S2/S3 remedy list (the only spec surrogate available) I expected: (a) test coverage
proving the OMP edit route reaches `check-domain.sh` for both hook phases (pre AND post), (b) a
non-blocking notice when the edit-route extraction yields nothing, (c) every Python `feature.json`
writer routed through one locked core with its never-create/path-shape/schema policies pinned
per-caller. Phase 2 below is scored against this list.

## Matrix

No `plan.yaml` task list exists, so change_type is inferred directly from the diff: it touches
Python core + two Python callers + one TS enforcement-layer file — genuinely `cross_module`, which
floors `unit` + `integration` (also satisfies `bugfix`'s `unit` floor). Both ran green net of one
unrelated pre-existing environmental failure (`test-validate-feature-json.py`, not in the diff —
fails only because this worktree's live `.harness` tree has 41 real `feature.json` files, which its
own fixture assumes zero of; confirmed unrelated by `git diff --stat` showing neither
`validate-feature-json.py` nor its test touched). `run-unit-tests.sh --kind unit`: 455 named PASS,
1 unrelated FAIL. `--kind integration`: 581 named PASS, 0 FAIL. `bun test omp-hooks.test.ts`: 48/48
— **run manually**; nothing in `test_kinds.unit`'s `cmd` (the `UNIT_SCRIPTS` bash array) executes
any `.test.ts` file despite the `detect` glob matching one. Flagged as a coverage gap, not a matrix
failure, since the tests exist and I ran them myself.

## Mutation proofs — table

| # | Target | Mutation | How applied | Observed | Executed/Reasoned |
|---|---|---|---|---|---|
| 1 | `postDomain` edit branch (`harness-hooks.ts:259`) | `if (toolName === "edit")` → `if (false && toolName === "edit")` | scratch copy, absolute-path sed from `cwd /` (relative sed denied by write-guard even in `/tmp`) | Cases 1–3 (hashline, multi-section, MV) redden; case 4 (S2 non-string) and case 5 (well-formed-silent) stay green. **3 of first 4, exact match to claim.** | **Executed** |
| 2 | S2's condition (`harness-hooks.ts:845`) | `if (toolName === "edit" && extractEditPaths(...).length === 0)` → `if (false)` | same scratch, same method | Exactly 1 test reddens ("a non-string patch spawns no gate, and SAYS SO (S2)"). **Matches claim exactly.** | **Executed** |
| 3 | `preDomain` edit branch (`harness-hooks.ts:234`) | same neutering technique | same scratch | **Zero change** — 47 pass/1 fail (the one fail is the same pre-existing scratch-copy environment artifact, unrelated). Confirms the pre-domain route is genuinely unreached by any test. | **Executed**, corroborated by static grep: zero `tool_call` invocations with `toolName: "edit"` anywhere in the 770-line file |
| 4 | `write_feature_json`'s default (`feature_json_write.py`) | Probed directly: called with a schema-clean `transform`, absent base, canonical path, **no opt-in** | in-process python probe against the real (unmutated) module | **Created the file.** The shared core does NOT refuse an absent base by itself — confirms the module's own docstring ("NEVER-CREATE IS ALSO CALLER POLICY... this function has never refused an absent base itself") and directly contradicts framing an absent-base refusal as the core's default. | **Executed** |
| 5 | `case_14`'s target property | `FEATURE_JSON_TAIL = re.compile(r".*")` (permissive default path-shape) | in-process monkeypatch + direct call of `case_14` from the real test module | 2 of 3 `case_14` assertions redden. Case_14 genuinely pins **destination/path-shape strictness** (refuses a non-canonical path, code 9, creates nothing) — **not** absent-base/never-create strictness, which (per #4) the core doesn't have. | **Executed** |
| 6 | `harness_merge.locked_update`'s atomic-write pattern | Replaced the `tempfile.mkstemp` + `os.fdopen(fd,"wb")` + `os.replace` block with a bare `open(path, "wb")` (the exact "truncating open, partial-file-visible" shape this whole feature exists to eliminate) | scratch copy of `.claude/skills/harness/bin/`, mutated `harness_merge.py` directly (Write-tool path also denied in-worktree; scratch method identical to #1) | `test-factory-decompose.py`: **1 of 163 reddens** — `"(22) os.replace was called at least once"`. `"(22) feature.json was opened only for reading, never in a truncating mode"` **stays green** — a false pass on a real truncating-write mutant. Root cause isolated directly: `case_22`'s path-match guard compares `os.path.abspath(dst)` (harness_merge's realpath-resolved, `/private/var/...` on this macOS) against `os.path.abspath(feature_json_path)` (the test's own un-resolved `/var/...`); tested with the exact captured strings from a live run — `False`. **case_22 is byte-identical between base and HEAD** (`diff` of the block is empty), so this vacuousness predates the feature; the analysis note's own mechanistic claim ("case 22's hooks no longer intercept a primitive that moved into harness_merge") is false on its face — nothing about case_22 changed. | **Executed** |

All six mutations reverted; scratch directories (`/tmp/qa-scratch-1030`, `/tmp/qa-scratch-py`,
`/tmp/qa-scratch-orig`) and debug artifacts deleted. Confirmed via `git status --porcelain` in the
worktree: only three sibling reviewers' untracked notes, nothing of mine.

## Adequacy — what the suite could not tell me

- The suite proves the **presence** of the atomic-write pattern (`os.replace` called) but, on this
  OS, cannot independently prove its **shape** (no truncating open) for the migrated `write_factory`
  path — that assertion passes whether or not the write truncates, because it never observes a
  write-mode `open()` call at all (mutation #6). This is a real gap in the regression guard the
  squad's own notes point to as the property's home.
- Nothing exercises the pre-domain (`PreToolUse`, non-`--post`) edit route at all (mutation #3) —
  confirmed disclosed residual, now measured rather than assumed.
- `case_14` is real, mutation-proven coverage of path-shape strictness, but is not what "refuses an
  absent base" would mean, and the shared core has no such property to lose (mutation #4) — a
  precision gap in how the retired `C3-3` migration is described, not a functional defect.
- I could not determine, and no test in this diff attempts to determine, whether the OMP hook
  actually fires end-to-end inside a live OMP session (Q1 in the analysis note, explicitly marked
  undecidable from a static tree) — out of scope for a source-diff gate.

## Disclosed residuals — confirmed/refuted

- **`factory_decompose` basename-only path check** — confirmed by reading:
  `FEATURE_JSON_BASENAME_TAIL = re.compile(r"(?:^|/)feature\.json$")` constrains only the filename,
  not the directory; `write_factory` can target any directory the CLI positional names. Real
  loosening, as declared. **Reasoned**, not further measured (severity call is the squad's rated
  `med`, not independently re-derived here).
- **DEC-199 "exactly four consumers" is false** — confirmed by reading: `feature_json_write.py` and
  `feature-json-merge.py` are two new consumers of `harness_merge` beyond the original four
  (`plan-merge.py`, `observations-merge.py`, `expertise-merge.py`, `inflight_registry.py`) = six.
  **Reasoned** (grep + read).
- **S3 has not shipped** — confirmed: `feature-json-merge.py` is named nowhere in
  `.agents/skills/harness/SKILL.md`. **Reasoned** (grep, zero matches).
- **`tail_regex` is an unvalidated free parameter** — confirmed by reading `feature_json_write.py`:
  no constraint on the regex object itself; the core's only self-owned protection is
  `require_destination`'s realpath/symlink defeat, everything else is caller policy. **Reasoned**.

## Bottom line

`VERDICT: FAIL` — not because the two dispatch-named claims (S2's count, the postDomain-edit redden
count) are wrong (both are **exact, executed matches**), but because the deepest proof available —
mutating the actual atomic-write primitive — surfaces a false-pass in the test the squad's own
notes cite as guarding it (`case_22`'s "not truncating" assertion), plus a second, independently
confirmed genuine coverage hole (the pre-domain edit route) and a third measured inaccuracy in the
governing notes (the edit-route case count). A green suite with a silently vacuous assertion inside
it is exactly the shape this whole feature exists to eliminate elsewhere in the codebase.
