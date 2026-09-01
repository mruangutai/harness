# Plan review — FEAT-47-tests-layout — plan-panel / scope — cycle 1

**BLUF. Not signable as written.** T-06's own verify sweep is unsatisfiable against T-06's own
mandated content, guaranteed to fail on first execution, and this is provable from the plan text
alone — no execution needed. `plan.yaml` T-06 instructs "What forced it" in the rewritten DEC-197 to
stay "as history, in the past tense... Do not reword it into the present" (`plan.yaml` T-06 intent
step 3), and that paragraph in `.harness/harness/docs/DECISIONS.md:5585` reads `` Eight of twelve
`INTEGRATION_SCRIPTS` entries were absent from `integration.detect`... `` — literal, undisputed,
preserved on purpose. T-06's own verify then greps the whole tree for that literal string, excluding
only `.harness/notes/`, `.harness/harness/features/` and `.harness/logs/` — DECISIONS.md is not one
of the three, so the same task that mandates the sentence also asserts, in its own verify block, that
no such sentence may exist. This is not a rare edge condition; it fires on the very first run,
regardless of any other task's correctness. Everything else audited below is sound: T-01 through T-05
are each falsifiable and satisfiable, the census/floor mechanics correctly avoid the vacuous-glob trap
this dispatch asked me to hunt for, the pool-invocation parsing logic is rename-proof and I hand-
verified it token-by-token, and every cross-feature restatement of FEAT-48 internals I checked against
FEAT-48's actual plan text held up. The one blocker is real, concrete, and confined to T-06 and to
SC-07's exclusion list in the BRIEF.

## Findings

**1. [critical] T-06's own verify sweep cannot pass given T-06's own mandated content — self-contradictory, not merely fragile.**
`plan.yaml` T-06 intent step 3: `"What forced it" stays as history, in the past tense. Do not reword
it into the present.` That paragraph, unedited, is at `.harness/harness/docs/DECISIONS.md:5585`:
`` **What forced it.** Eight of twelve `INTEGRATION_SCRIPTS` entries were absent from
`integration.detect`... `` T-06's verify (`plan.yaml` T-06 `verify:`) then runs `git grep -n -e
UNIT_SCRIPTS -e INTEGRATION_SCRIPTS -e "check-kinds" -- ':!.harness/notes'
':!.harness/harness/features' ':!.harness/logs'` and fails (`"a live file still presents the arrays
as current"`, exit 1) on any match. DECISIONS.md is at `.harness/harness/docs/DECISIONS.md`, not
under any of the three excluded prefixes. I confirmed the exact text is present today (unrelated to
whether T-06 has run) via `read` at `DECISIONS.md:5560-5600`. Consequence: T-06 fails its own gate on
every execution, by design of its own two halves fighting each other — this is not fixable by writing
the task correctly, the task's spec is inconsistent.

Three more live sources compound the same class of gap, none excluded by SC-07's three-prefix list
(`BRIEF.md` Success Criteria, SC-07) or T-06's identical exclusion set, and none touched by any task:
- `.harness/harness/expertise/harness-code-reviewer.md:7` and
  `.harness/harness/expertise/harness-eng-lead.md:9-10` — pre-existing, untouched by any task in this
  plan, both git-tracked (`git ls-files` confirmed), both currently say to check
  `run-unit-tests.sh`'s `UNIT_SCRIPTS`/`INTEGRATION_SCRIPTS` arrays "by exact name" as live guidance.
  I can confirm these are actually injected and read, not dead text: the code-reviewer entry is
  verbatim in my own injected repository-tier Expertise this session (`G-04`). After T-05 deletes the
  arrays, this stops being stale-but-harmless — it becomes injected instruction, at every future
  code-reviewer and eng-lead spawn in this repo, to check something that no longer exists.
- `tests/manual/probe-omp-session-accessor.py:14` (post-T-04 move) — T-04's own intent says "Keep
  that history in past tense" for exactly the sentence `It was first registered in
  INTEGRATION_SCRIPTS with the reasoning that...` (I read this verbatim at the file's current bin
  path, lines 1-14). T-04 explicitly preserves this string; `tests/manual/` is not excluded.
- `tests/integration/test-factory-integration.py:1384,1434` (post-T-02 move) — two FEAT-33-era
  comments ("Adds no file to any list and edits neither `INTEGRATION_SCRIPTS` nor `harness.json`")
  that T-02's anchor-only repair recipe has no instruction to touch. `tests/integration/` is not
  excluded either.
Any ONE of these four sources alone fails T-06's grep. All four are independently guaranteed given
what the plan's own other tasks mandate. Remedy is a plan decision, not mine to make: either widen
SC-07's/T-06's exclusion pathspec to cover known-historical, deliberately-preserved mentions (and
justify why `.harness/harness/expertise/` gets the same "not current" exemption as `.harness/notes/`
— a harder case, since Expertise IS meant to be current craft, not a record), or add the two Expertise
files to T-06's `files:` and rewrite their stale guidance, or narrow T-04's and T-02's instructions to
paraphrase around the literal tokens. I'm not picking one; all three are legitimate but each changes
what T-06 is allowed to touch or what SC-07 promises.

## Verify audit table (T-01..T-06)

| Task | (a) What makes it red | (b) Is there a tree where it passes? |
|---|---|---|
| T-01 | Inline `python3 -I -c` block directly re-asserts `is_control_plane_target` True for the three `tests/**` shapes and `is_control_plane_glob` False for `tests/**`; either regressing breaks it independent of whether `test-harness-boundary.py`/`test-check-domain.py` were actually edited to add the new cases (the inline block is the load-bearing check, not the two files it also runs). | Yes. Satisfied by step 2's `HARNESS_CONTROL_PLANE` append and step 4's docstring/glob logic exactly as specified. Nothing else in the file's existing behaviour conflicts. |
| T-02 | Any migrated file that doesn't parse/run (`python3 "$f"` per file, non-zero exit under `set -e` aborts the whole verify); the discovery floor `n -ge 37` on `ls tests/integration/test-*.py \| wc -l`; a per-file `git diff -M --name-status` rename-record miss for any of the 37 basenames. | Yes. I hand-checked the vacuous-glob trap this dispatch flagged: `ls .../test-*.py \| wc -l \| tr -d " "` under `set -e` with no `pipefail` takes only `tr`'s (always-0) exit status, so an empty glob does NOT abort early — it correctly reaches `n=0` and fails the `-ge 37` floor loudly, before the per-file loop, so the loop's own bash no-match literal-string behaviour is unreachable. I also checked rename-detection risk directly: smallest file needing any edit is 104 lines (`test-sync-agent-adapters.py`), anchor edits are ~4-10 lines localized to a header block (`git diff -M`'s default 50% similarity threshold is nowhere close to being threatened); the one 12-line file in the whole set, `test-omp-hooks.py`, needs *zero* content edits under T-03's own recipe (it already resolves its sibling `.test.ts` via `Path(__file__).with_name(...)`), so its rename is 100%-similarity trivial, not a risk case. |
| T-03 | Same per-file run/rename mechanics as T-02, plus the exact-residue assertion (`bin` holds precisely `test-run-unit-tests-kinds.py` and no `*.test.ts`) and the ALLOW_LIST repair being exercised by running `test-no-distribution.py` from its new home in the same loop. | Yes. I re-derived the arithmetic independently: 56 baseline + FEAT-48's 2 = 58 tracked at task start; T-02 removes 37 (36+`test-run-pool.py`); T-03 removes 20 (19+`test-suite-independence.py`); 58−37−20=1, matching the residue assertion exactly. I also independently verified the `test-suite-independence.py` special-case paragraph against FEAT-48's actual plan text (`root_above`/`resolve_scan_root`, the `--scan-dir` override, the bare-name `harness_boundary` import) — every claim matched FEAT-48 `T-03` verbatim (lines ~436-527), not just the prior coupling note's say-so. |
| T-04 | `git ls-files --error-unmatch` on the new path; `bin` holding zero `probe-*`; `compile()` on the moved file. Weak by design — no runtime execution of a probe that makes a live model call, which is the accepted, disclosed constraint (REQ-08), not a new gap. | Yes, trivially — move plus a syntactically valid file satisfies it. |
| T-05 | Extensive and load-bearing: `--check-layout` exit 0, `--bogus` non-zero, exactly one non-comment `run_pool.py` line with a matching `--mutation-check` argument, zero lines starting `for s in`, per-kind tally-set equality against directory contents, the `suite_layout.py` unit tests over five synthetic trees, the sole-implementation sweep's exemption/positive-control/floor/three-shape-proof cases, and the two `suite-census.py` invocations (`migration --floor 56`, `verdict-lines`). | Yes, on every point I hand-traced. I simulated the `inv[0].split("run_pool.py")[0].split()[-1].strip(chr(34)).rstrip("/")` vs. `(inv[0].split("--mutation-check")[1:] or ["!missing"])[0].split()[0].strip(chr(34))` parse against the literal line `python3 "$BIN_DIR/run_pool.py" --mutation-check "$BIN_DIR" -- "${SCRIPTS[@]}"` (FEAT-48's own invocation with only the prefixing dropped, per T-05 step 4): both reduce to the string `$BIN_DIR` and compare equal — this is genuinely rename-proof, not dependent on the variable staying named `BIN_DIR`. I also traced the `for s in` assertion specifically, since the dispatch named this exact trap from the sibling plan: today's `run-unit-tests.sh` has two matching lines, `for s in "${ALL_SCRIPTS[@]}"` (line 64, inside the drift-detector loop) and `for s in "${SCRIPTS[@]}"` (line 148, the serial loop). FEAT-48 replaces line 148 with the pool call *before* this feature starts (confirmed against FEAT-48 `T-06`, which explicitly does NOT assert this pattern is absent, for exactly the reason line 64 survives FEAT-48's own edit). T-05 step 4 then deletes "the drift detector loop... including the embedded python heredoc," which is the block containing line 64. By the time T-05's own verify runs (after T-05's own edits), both lines are gone — unlike the sibling's version of this exact check, this one is satisfiable because the task that asserts absence is also the task that deletes the offending line. |
| T-06 | Index-sync check, the two absorbed test files, the `^## DEC-207 ` heading grep, and the negative sweep for `UNIT_SCRIPTS`/`INTEGRATION_SCRIPTS`/`check-kinds`. | **No.** See Finding 1. The sweep is unsatisfiable against T-06's own "keep `What forced it` in the past tense" instruction for `DECISIONS.md`, and independently against three other live-file sources none of this plan's tasks touch. |

## Checked and clean

- REQ-01..REQ-08 all traced by ≥1 task; every task's `traces:` cites a real REQ; no orphan either
  direction (verified against the current REQ set, not carried over from c0's REQ-01..REQ-11).
- SC-01..SC-10: every one has a task building its evidence and every instrument built
  (`suite_layout.py`, `tests/manual/suite-census.py`, the two new test files) is read by ≥1 SC.
- `depends_on`: acyclic; T-01/T-02 both `depends_on: []` is a correct call, not a defect — every task
  in this plan is `execution_mode: main-session-direct`, so T-02's writes to `tests/**` are not routed
  through the PreToolUse seat-grant machinery T-01 opens (`lanes:` block states this explicitly: "a
  squad dispatched over it would be executing the change through the path being changed"). T-01's
  grant matters for `harness-qa`/`harness-backend-dev`/`harness-dev-ops` going forward, not for this
  plan's own direct edits.
- The T-02→T-03 red window (`test-no-distribution.py`'s stale `ALLOW_LIST`, the runner being unusable)
  is bounded exactly as claimed: no task's verify calls the unqualified runner in that window, and
  T-03's own verify loop re-runs `test-no-distribution.py` from its new home, proving the repair.
  (Minor, unfiled: T-02's stated *mechanism* for "why the runner is unusable" — "with no test-*.py
  left in bin, its drift detector sees the unexpanded glob" — is imprecise; `test-run-
  unit-tests-kinds.py` remains a matching `test-*.py` in `bin` until T-05 deletes it, so the glob
  never actually goes unexpanded, and the real failure mode in that window is the tally loop reporting
  `FAIL`/file-not-found for the 37 already-moved names. The *conclusion* — don't call it unqualified in
  this window — is correct and nothing in the plan relies on the wrong mechanism, so this has no
  concrete consequence and I'm not filing it.)
- SC-05 / the sole-implementation sweep: the declared four-name exemption list matches word-for-word
  between the BRIEF and T-05 step 2b; I hand-checked the two regexes
  (`tests['"]?\s*[,/]\s*['"]?\s*unit` and the integration twin) against all three claimed planted
  shapes (slash literal, `os.path.join` components, `Path(r, "tests", "unit").glob`) and they match
  all three.
- G-01 rot (the stale `test-suite-independence.py` root-climb text) is genuinely closed, and I
  independently re-verified it against FEAT-48's live plan text rather than trusting the prior
  coupling note — see the T-03 row above.
- Cross-feature couplings I spot-checked directly against FEAT-48's plan text (not just the existing
  coupling note): the `--mutation-check "$BIN_DIR"` argument (FEAT-48 D-11/T-06, matches T-05's claim
  exactly), the explicit `test-run-pool.py` path FEAT-48 adds to `integration.detect` that T-05 step 6
  must remove (FEAT-48 T-04, matches), and `root_above`/`resolve_scan_root`/`--scan-dir` (FEAT-48 T-03,
  matches). All held up. I did not re-derive every remaining citation (D-13's file census, the
  `test-run-pool.py` "every case forks" claim) from FEAT-48 source line-by-line; see below.
- c0's five findings are all resolved — see the re-derivation section.

## What I could not evaluate

- `goalcheck_path` does not exist, as stated in the dispatch; this is expected for a pre-signature
  plan and I recorded its absence rather than treating it as satisfied.
- Nothing in this plan has executed: `suite_layout.py`, both new test files, and the rewritten
  `run-unit-tests.sh` don't exist yet. My soundness claims for T-05 (the pool-argument parse, the
  `for s in` timing, the census arithmetic) are hand-traced against the plan's literal text, not
  against a running suite.
- Every cross-feature claim I checked was checked against **FEAT-48's plan text**, not FEAT-48's
  actual code — FEAT-48 hasn't been built either. "Matches FEAT-48" in this note and in the plan
  itself means "matches what FEAT-48's plan currently commits to," which is the strongest evidence
  available pre-build but is not the same claim as reading merged source.
- I did not exhaustively re-verify every one of D-13's/D-14's file-count claims or the "every one of
  `test-run-pool.py`'s cases forks the pool" line against FEAT-48's `T-04` case-by-case; I spot-checked
  the two highest-leverage citations (the mutation-check argument and the root resolver) because those
  are exactly the class of claim that broke once already (G-01) and because a wrong argument there
  is a guaranteed red gate the same way Finding 1 is.

## Explicitly re-derived from c0

- **c0 finding 1** (SC-05 unfalsifiable-second-copy overclaim) — **discharged**. Current SC-05 text
  explicitly withdraws the "any second copy anywhere" claim and replaces it with the bounded,
  instrumented sweep (T-05 step 2b) I checked above.
- **c0 finding 2** (T-02 rename count is a padable lower bound) — **discharged**. T-02's verify no
  longer relies on a bare `-ge 36` count alone; it now asserts a per-file rename record for each
  `tests/integration/test-*.py` basename individually, which a fixture-file rename cannot pad.
- **c0 finding 3** (worker-count fallback has zero verify coverage) — **no longer applies**. That was
  old T-08, entirely FEAT-48's scope now (parallel pool sizing), removed from this plan by D-13.
- **c0 finding 4** (REQ-03 classification gap undisclosed) — **discharged**. BRIEF's Verification gaps
  now carries a full paragraph naming the gap, the cost tradeoff, and the reachable instrument; per
  the dispatch I did not re-litigate the underlying decision (accepted, #979's), only its disclosure,
  which reads honest and complete.
- **c0 finding 5** (T-05 miscounts new no-baseline files by one) — **discharged**. Current text reads
  "the two test files this task adds and the two FEAT-48 adds" — four, correctly enumerated; the old
  "two" undercount is gone.

---

**Compact findings for transcription:**

critical | T-06's negative grep sweep for `UNIT_SCRIPTS`/`INTEGRATION_SCRIPTS`/`check-kinds` is unsatisfiable against T-06's own instruction to preserve `DECISIONS.md`'s "What forced it" paragraph verbatim, plus three more live, unexcluded sources (two currently-injected Expertise files, the moved probe's deliberately-preserved history line, two FEAT-33-era comments in test-factory-integration.py) | T-06 fails its own gate on the first run; the plan cannot reach a green state as specified, and REQ-07/SC-07's exclusion list needs a real decision (widen it, or edit the Expertise files, or reword the preserved prose) before this can ship.
