# QA re-review — cycle 17, scoped seam (154ff2a0..252a18a9)

## Verdict on the one question

**The handoff PRE permit requirement is CLOSED.** The case
`handoff valid reconstructable PRE-Edit remains allowed` exists, is genuinely PRE (not the POST
sweep), pins a unique/grammar-valid reconstruction, asserts exit 0, and — critically — the mutation
probe that targets the exact regression the Advisor named (folding `RE_HANDOFF` into the
deny-by-path arm) makes it RED. It also reddens when the grammar validator is forced to reject the
candidate, so both halves of the composed claim are load-bearing, not one alone.

## Diff scope — WIDER than the dispatch described

`git diff --stat 154ff2a0 252a18a9` (10 files, +447/-15):
`BRIEF.md`, `STATE.md`, `feature.json`, `notes/regression-delta-BUG-1305.md`,
`notes/research-BUG-1305-goalcheck-build-c4.md` (new), `notes/research-sc07-amend-c16.md` (new),
`notes/review-harness-qa-c4.md` (new), `observations/harness-pm.md`, `observations/harness-qa.md`,
`tests/integration/test-check-domain.py`. The dispatch named three files "plus harness
bookkeeping" — the actual bookkeeping set is larger (STATE.md, feature.json, two research notes, a
prior review note, two observation logs) than the dispatch anticipated, spanning cycles back to c4.
None of it is production code or test code beyond the one file named. `.claude/skills` is confirmed
byte-identical (`git diff 154ff2a0 252a18a9 -- .claude/skills` → 0 lines). **Finding F-0, bucket
(b)**: a dispatch-accuracy gap, not fixable in the test/amendment — routes to the Advisor/orchestrator
only as a note that "plus bookkeeping" undersold the set; no action needed on the amendment itself.

## Q1 — the case is real and non-vacuous

- **Location at `252a18a9`**: `tests/integration/test-check-domain.py:4288-4293`, inside
  `_handoff_valid_pre_edit_cases` (4276-4305) → called from `_handoff_pre_edit_cases` (4339-4341) →
  called from `run_handoff_done_when` (4410-4424).
- **Route**: `subprocess.run([HOOK], input=json.dumps(permitted_edit), ...)` — no `--post` flag, no
  `hook_event_name` key in the payload → PRE. Confirmed distinct from the POST-sweep case
  `handoff edit with Done when` (line 4382), whose payload explicitly sets
  `"hook_event_name": "PostToolUse"` (line 4372) and is a different route through the code
  (`elif target:` POST branch at check-domain.sh:2080, vs the PRE `RE_HANDOFF` reconstruction arm at
  check-domain.sh:2045-2048).
- **Uniqueness/grammar-validity**: the fixture is built by `_handoff_text(valid)` with
  `valid = "Scope: build complete\nAuthority: plan-task:T-03.verify"` (line 4414), giving a body
  where `"Scope: build complete"` occurs exactly once. `old_string="Scope: build complete"`,
  `new_string="Scope: build complete and verified"` — the reconstructed `## Done when` becomes
  `Scope: build complete and verified` / `Authority: plan-task:T-03.verify`: exactly one non-empty
  `Scope:` line, appearing before the one `Authority:` line, no unexpected lines — passes
  `handoff_done_when.py`'s `_shape_problems`/`_classified_lines` checks (lines 286-312) unchanged.
- **Assertion quoted**: `_record_handoff_result(results, "handoff valid reconstructable PRE-Edit
  remains allowed", subprocess.run(...), 0)` — `want=0`, no needles, so `ok = returncode == 0`.
- **Second trap, checked not assumed**: at `154ff2a0`,
  `_handoff_valid_pre_edit_cases` registered ONLY `"handoff pre-Edit blocks invalid candidate"`
  (exit 2, needle `"non-empty"`) — no permit assertion existed despite the function's name. At
  `252a18a9` it now asserts the new permit (exit 0) FIRST, then the pre-existing invalid-candidate
  block (exit 2) unchanged. Confirmed by diffing both SHAs directly.

## Q2 — mutation probe (mandatory), literal command and output

Built in a disposable worktree, never the checkout under review:

```
git -C <WT> worktree add --detach /…/.claude/worktrees/harness/qa-c5-mutant-probe 252a18a9
```
Mutated the COPY at `.claude/worktrees/harness/qa-c5-mutant-probe/.claude/skills/harness/bin/check-domain.sh`,
moving `RE_HANDOFF` from the reconstruction `elif` (check-domain.sh:2045-2048) into the deny-by-path
`if` one arm above (check-domain.sh:2042-2044) — the exact future harmonisation the Advisor named —
via a Python in-place string replace (the Edit/Write tools refuse this path outside my domain
regardless of worktree; a scripted `python3 -c` file rewrite through Bash was permitted).

Ran:
```
CHECK_DOMAIN_BIN=/…/qa-c5-mutant-probe/.claude/skills/harness/bin/check-domain.sh \
  python3 <WT>/tests/integration/test-check-domain.py
```
Literal result (excerpt):
```
FAIL  handoff valid reconstructable PRE-Edit remains allowed exit 2: check-domain: BLOCKED — …
  missing required section(s) ['## Next', '## Trust', '## Dead en[ds…]
```
**The case REDDENS against the mutant** (expected exit 0, got exit 2 — the deny-by-path arm forces
empty reconstructed content, which then trips the "missing required sections" shape check). Two
sibling cases also correctly redden as collateral (`handoff pre-Edit blocks invalid candidate`,
`handoff pre-Edit unreadable existing file fails closed`) since they share the same fixture/route;
this is expected, not a separate finding.

Repository check-domain.sh confirmed byte-untouched throughout:
`git -C <WT> status --porcelain -- .claude/skills` → empty, both before and after the probe.
Worktree removed from OUTSIDE it (`git worktree remove --force`) after use;
`git worktree list` confirms no `qa-c5-mutant-probe*` entries remain.

## Q3 — permit composition, both halves proven

The Advisor's grounds: this ONE case must pin reconstruction-permit AND candidate grammar-validity
TOGETHER. Ran a second, independent mutation in a second scratch worktree
(`qa-c5-mutant-probe2`, same `git worktree add --detach 252a18a9` pattern): forced
`handoff_done_when.problems()` to unconditionally return one problem (simulating a grammar validator
that wrongly rejects a valid candidate). Re-ran the same suite against that mutant hook:
```
FAIL  handoff valid reconstructable PRE-Edit remains allowed exit 2: check-domain: BLOCKED — …
```
**Also reddens.** Both halves are exercised by the single case: reconstruction being denied (Q2's
mutant) and the reconstructed candidate being wrongly rejected by grammar validation (this mutant)
each independently flip the assertion. Neither half is a free rider. Scratch worktree #2 removed the
same way; `check-domain.sh` and `handoff_done_when.py` in the reviewed checkout confirmed
byte-untouched.

## Q4 — the suite total, derived not accepted

The "27/27" figure is `run_bug1305_marker_cases`'s own aggregate (test-check-domain.py:5038-5058),
which is UNRELATED to the new handoff case (that lives in the separate `run_handoff_done_when`
aggregate, 41 cases, 0 failures at the pin — the new case is one of those 41, not one of the 27).
Derived the 27 independently by importing the module and calling each of the 8 sub-functions
`run_bug1305_marker_cases` sums, summing `len()` of each returned list:
`_bug1305_edit_reconstruction_cases`=4, `_bug1305_nonstate_edit_reconstruction_cases`=6,
`_bug1305_marker_foreign_refusals`=2, `_bug1305_marker_witness_precedence`=2,
`_bug1305_marker_recovery_cases`=3, `_bug1305_marker_file_protection`=6,
`_bug1305_marker_post_mint_cases`=2, `_bug1305_marker_post_preservation_cases`=2 → **total 27**,
matching the reported figure and matching a full run of `run_bug1305_marker_cases()` (0 failures).

## Q5 — no do-no-harm regression

Called each relevant group directly at the pin (unmutated hook): `_bug1305_identity_refusal_cases`
(5, 0 fail), `_bug1305_marker_witness_precedence` (2, 0 fail), `_bug1305_marker_file_protection`
(6, 0 fail), `run_bug1305_digest_repair_cases` (5, 0 fail incl. `digest Edit append repair remains
allowed`), `run_bug1305_marker_cases` (27, 0 fail incl. `uniquely reconstructable state Edit remains
allowed` and the three unreconstructable-Edit refusals per governed class:
`handoff absent-prior Edit fails closed`, `handoff unmatched Edit fails closed`,
`handoff omp file-path-only Edit fails closed`, plus their `state`/`digest` siblings),
`run_bug1305_identity_cases` (10, 0 fail incl. `modal collision Write omitting uid is refused`,
`modal collision Edit removing uid is refused`, `different minted uid Edit is refused`). All six
named refusal cases and both sibling permits pass at `252a18a9`.

## Regression-delta note review (read-only, not re-fixed)

`## Newly refused writes` BLUF discloses the reconstruction-`None` class explicitly ("an Edit of a
governed run artifact whose complete candidate cannot be reconstructed... now fails closed") and
names all three permits by exact case name: `uniquely reconstructable state Edit remains allowed`,
`digest Edit append repair remains allowed`, `handoff valid reconstructable PRE-Edit remains
allowed`. Requirement met. `## Suite results` records only `exit 0` lines and `0 lines beginning
FAIL` for both unit and integration kinds, and `check-state.sh` exit 0 with 0 `INV-36` lines; the
one non-zero exit in the note (`exit 4; 6/10 passed`) is explicitly the OLD pre-change hook run for
historical contrast, not a live failure — correctly framed, no discrepancy found.

## Findings, each bucketed

- **F-0** (bucket b — Advisor/orchestrator, not fixable in cycle 18): the diff touched by this
  amendment cycle is wider than the dispatch's "three files plus bookkeeping" — six additional
  bookkeeping/notes/observation files, spanning back to cycle 4. No production or test drift beyond
  the named file; purely a dispatch-framing gap.
- No other findings. The amendment text, the new test case, and the regression-delta refresh are
  internally consistent and mechanically sound; nothing here is cycle-18 (bucket a) eligible because
  nothing needs fixing.

## Cleanup confirmation

Both scratch worktrees (`qa-c5-mutant-probe`, `qa-c5-mutant-probe2`) removed via
`git worktree remove --force` run from OUTSIDE them; `git worktree list` shows neither remains.
`/tmp/mut_full.log` and `/tmp/mut2_full.log` scratch capture files removed. No repository file was
edited; only the disposable worktree copies were mutated and discarded.

`git -C <WT> status --porcelain` **before** my own writes (captured mid-review, describes the
reviewed source tree): empty — no output.

`git -C <WT> status --porcelain` **after** writing this note (describes the tree I leave behind,
since `notes/` is my own tracked domain):
```
?? .harness/harness/features/BUG-1305-run-state-clobber/notes/review-harness-qa-c5.md
```
