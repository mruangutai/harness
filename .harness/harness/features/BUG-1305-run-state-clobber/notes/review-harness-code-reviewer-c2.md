# Code review — BUG-1305-run-state-clobber — review-c2 (DELTA) — base `dc0e0313` → head `e77b30ca`

**BLUF: F-04 (the Edit-creates bypass) is CLOSED, measured, not inferred — exit 0 at `dc0e0313`,
exit 2 at `e77b30ca` for both the CREATE case and the previously-unmeasured "ambiguous old_string"
case. No over-match found: the new PRE branch denies by path alone, matches only the exact
`.run-identity.json` basename inside a run directory (case-insensitively, by deliberate existing
convention), and every sibling artifact (`state.yaml`, `digest.md`, an ordinary file) I probed
remains unaffected. The three moved files agree — `RE_RUN_IDENTITY` is a single shared object
imported by both guards, not a second independently-drifting copy. QA-F1/F2/F3 and the SC-09
evidence gap are all CLOSED with anchors below. Mechanical grade over the canonical range
(`merge-base(default branch, e77b30ca)..e77b30ca` = `4b0d04e9..e77b30ca`): exit 0, 50 records,
`code_grade: grade_2` — six pre-existing grade-2 test functions survive (none newly introduced by
this delta, none is a grade-1 or below-bar-3-production blocker), and this delta's own single
changed function (`_bug1305_marker_file_protection`) is grade 3 PASS. `severity_max: none`.
Nothing here requires a 13th cycle.**

All source read via `git -C <worktree> show e77b30ca:<path>` (or `dc0e0313:<path>` for the old
side); the working tree is confirmed code-identical to `e77b30ca` outside `feature.json`
(`git diff e77b30ca HEAD --stat` → only `feature.json`, 2/2 lines). Diff scope independently
confirmed: `git log --oneline dc0e0313..e77b30ca` is exactly four commits — `929d4144` (pin
review_sha, `feature.json` only), `9d5c3bad` (docs: NotebookEdit evidence, `probe-notebookedit`
only), `2728aa20` (the fix: the 3 bin/test files + `BRIEF.md` + `redproof` + `regression-delta`),
`e77b30ca` itself (preserve cycle-11 panel artifacts: `review-*-c1.md`, `receipt-*-c1.md`,
`research-*-c1.md`, `observations/harness-pm.md`, `feature.json` budget bump). The panel-artifact
commit's extra files are pre-existing cycle-1 panel output being committed for persistence, not
new code under review this cycle — matches the Contract's own framing exactly and is not a
discrepancy.

## Q1 — Does the F-04 remedy close the Edit-creates bypass on every route?

**Yes, measured directly, both before and after.** `check-domain.sh:2036-2046` (`e77b30ca`):

```python
if (_tool == "Edit" and target
        and RE_RUN_IDENTITY.match(_norm(target))):
    targets = [(_norm(target), "", _show(target), _claimed_abs(target))]
elif (_tool == "Edit" and target
        and (RE_RUN_DIGEST.match(_norm(target))
             or RE_STATE_YAML.match(_norm(target))
             or RE_HANDOFF.match(_norm(target)))):
    ... _edit_reconstructed_content(...) ...
```

The witness match is now the FIRST branch, checked before `_edit_reconstructed_content` is ever
called for this path — so its `except OSError: return None` → caller `sys.exit(0)` fall-through
(the old bypass) is structurally unreachable for `.run-identity.json`: the branch that used to
reach it no longer matches this path at all. `targets` is built with an empty placeholder content
(`""`) because `shape_problems()`'s `RE_RUN_IDENTITY.match(rel)` branch (`check-domain.sh:1318`)
denies unconditionally on path match alone, never inspecting `content` — confirmed by reading the
function body directly (`shape_problems`, `check-domain.sh:1262-1330`).

**Replay, both pins, extracted via `git archive <sha> -- .claude/skills/harness/bin | tar -x` into
scratch bin roots, invoked through the CURRENT `test-check-domain.py`'s own fixture helpers with
`CHECK_DOMAIN_BIN` pointed at each pin's script** (so the harness's own path/env logic is
exercised, not a hand-rolled shell call):

- CREATE case (path never existed): `_fire_digest_edit(root, identity, "not present",
  '{"run_id": "forged"}')` after `os.unlink(identity)` → **`dc0e0313`: exit 0, stderr `''`.
  `e77b30ca`: exit 2**, stderr `"...this path is the run's write-once identity witness..."`.
- Ambiguous-`old_string` case (file exists, `old_string` does not match its content — the second
  fall-through `_edit_reconstructed_content` had, via `count == 0 → return None`): same command
  against the still-present file → **`dc0e0313`: exit 0, stderr `''`. `e77b30ca`: exit 2**, same
  message.

This is the SAME defeat class the `except OSError` gap was, and the new branch closes it too — the
Contract only asked about the CREATE case, but the fix's mechanism (deny before reconstruction, at
all) closes both, and I measured both to be sure the fix isn't narrower than it looks.

Routes: **Edit — closed** (above). **Write — was already closed pre-fix** (unconditional `targets`
build in the `else` branch, unaffected by this delta's diff) and I did not need to re-measure it;
c1's review already proved it live and this delta does not touch that branch.
**Bash — unaffected, still closed**: `bash-write-guard.sh`'s `_run_artifact_guard`
(`RE_RUN_IDENTITY.match(rel)` → `deny(...)`) is untouched logically in this delta — the diff there
is comment/message wording only (adds the issue #1376 cross-reference), confirmed by reading the
full diff hunk; no control-flow line changed.

No residual ordering/early-return/matcher-scope path remains: I traced every `elif` in the
`if not _post:` chain and the new first branch is unconditional on `RE_RUN_IDENTITY.match` alone —
nothing upstream of it can short-circuit past it for a matching path (the branch immediately
follows entry into the `not _post` block).

## Q2 — Does denying by path over-match anything legitimate?

**No over-match found**, checked by direct probe, not by reading the pattern alone:

- `RE_RUN_IDENTITY = re.compile(r"^\.harness/[^/]+/features/[^/]+/runs/[^/]+/" +
  re.escape(_RUN_IDENTITY_MARKER) + r"$", re.IGNORECASE)` (`harness_boundary.py:43-46`), where
  `_RUN_IDENTITY_MARKER = run_identity.MARKER_NAME = ".run-identity.json"` — fully anchored
  (`^...$`), and the marker segment is `re.escape`'d literal text, not a wildcard. It cannot match
  a different basename by construction.
- Probed live against `e77b30ca`: a `state.yaml` sibling first-landing Write in the same run
  directory → exit 0 (unaffected). An ordinary file (`notes.txt`) Edit in the same run directory →
  exit 0 (unaffected). A `digest.md` sibling Write beside a present witness → exit 0 (this is also
  QA-F1's new regression case, see Q4).
- Alt-case basename (`.RUN-IDENTITY.JSON`) → exit 2, refused. This IS a match, by design: every
  pattern in this file is deliberately case-insensitive (comment at `check-domain.sh:~1233`,
  "EVERY PATTERN IS CASE-INSENSITIVE, AND THAT CLOSES F-04" — a DIFFERENT, earlier F-04 about a
  `Plan.yaml` case-bypass on a case-insensitive filesystem). Not a new over-match introduced by
  this delta; it is the codebase's existing, consistent convention applied to a pattern that
  already carried it (`RE_RUN_IDENTITY` picked up `re.IGNORECASE` before this delta — the flag is
  unchanged in the diff).
- No darwin-specific new risk: the same case-fold applies on a case-sensitive filesystem too
  (denies `.RUN-IDENTITY.JSON` there as well, per the file's own stated rationale — a name nobody
  legitimately writes, refused loudly rather than silently bypassed).

## Q3 — Do the three moved files agree?

**Yes, and more strongly than the sibling `RE_STATE_YAML`/`RE_RUN_DIGEST` patterns do.**
`bash-write-guard.sh`'s `_run_artifact_guard` reads `harness_boundary.RE_RUN_IDENTITY` directly
(no independent respelling); `check-domain.sh` imports the SAME object as
`_shape_boundary.RE_RUN_IDENTITY` (`check-domain.sh:1187`, `try: import harness_boundary as
_shape_boundary; RE_RUN_IDENTITY = _shape_boundary.RE_RUN_IDENTITY`). One compiled regex, two
importers — unlike `RE_STATE_YAML`/`RE_RUN_DIGEST`, which ARE independently spelled in
`check-domain.sh` for the documented reason that the shape-phase import must stay absorbing
(comment at `check-domain.sh:1169-1174`), with a byte-for-byte string-equality test guarding
against drift. `RE_RUN_IDENTITY` needs no such test because there is nothing to drift.

`test-check-domain.py`'s new/changed assertions bind the actual mechanism, not a decoration:
`"unmatched Edit of existing witness is refused"` and `"Edit creating false witness is refused"`
both assert `returncode == 2 and "identity witness" in stderr` — I confirmed both go red at
`dc0e0313` (exit 0, empty stderr) and green at `e77b30ca` via my own replay above, so these are not
vacuous against the old pin; they are exactly the discriminating cases the fix addresses.

## Q4 — Was any earlier must_fix only partly closed, and is there any new undisclosed refusal?

| Item | Status | Anchor |
|---|---|---|
| F-04 (Edit-creates bypass) | **CLOSED** | `check-domain.sh:2036-2046` (new branch order) + my own replay above (exit 0→2, both the CREATE and ambiguous-`old_string` cases) |
| QA-F1 (SC-13 missing digest-Write-beside-witness case) | **CLOSED** | `test-check-domain.py` diff, `run_bug1305_digest_repair_cases`: new case `"digest Write append remains allowed beside identity witness"`, `response.returncode == 0` |
| QA-F2 (redproof missing `## SC-13` section) | **CLOSED** | `notes/redproof-BUG-1305.md` diff: new `## SC-13` section with verbatim command + output for both the Bash-route pinned-vs-live replay and the F-04 Edit replay (`15/17 → 17/17`) |
| QA-F3 (SC-01(c) Edit half weaker than Write sibling) | **CLOSED** | `test-check-domain.py` diff, `_bug1305_identity_refusal_cases`: `"modal collision Edit removing uid is refused"` now asserts `"run identity" in edit.stderr and "field disagreement" not in edit.stderr`, matching its Write sibling's assertion shape exactly |
| SC-09 evidence note (wrong-tree capture) | **CLOSED** | `notes/regression-delta-BUG-1305.md` diff: now states "From the control-plane root `/Users/.../harness`, ... exit 0 ... a search of the verbatim output found 0 `INV-36` lines" — names the root explicitly, unlike the prior unattributed sentence |
| SC-11 probe falsifiability (F-02, c1) | **CLOSED** (bonus, not asked but in scope per the 7-file list) | `notes/probe-notebookedit-BUG-1305.md` diff: now carries the verbatim `omp --help` command and its full tool-inventory output for both the `route_reachable` and `guard_fires` lines |

**New refusal beyond the disclosed one:** none found. The only disclosed new refusal (owner
rewrites its checkpoint from scratch and drops `run_uid`) is unrelated to this delta's files. My
own Q2 probe (state.yaml sibling, ordinary file, digest.md beside witness) is the direct check for
an undisclosed REQ-07-direction-two violation and it came back clean.

## Mechanical grade

The reviewed range for `code_grade` is repository-derived, not reviewer-chosen: it is
`merge-base(default branch, e77b30ca)..e77b30ca`, resolved here to `4b0d04e9..e77b30ca`.

```
$ python3 .claude/skills/harness/bin/code-grade.py --base 4b0d04e974244fc3766267e1ebe9d444b27c7df8 --head e77b30cab2221bd09bbc9b91b986b253fc941f7f
```

50 records, exit 0. `_bug1305_marker_file_protection` (`tests/integration/test-check-domain.py:4834`,
this delta's ONLY touched function, cyc 6 / cog 5 / abc 21.8) is grade 3, bar 3, **PASS**. Six
pre-existing grade-2 TEST functions survive, none touched by this delta's own diff (`dc0e0313` →
`e77b30ca`), each carrying a written reason (reused from c1's independent re-grading, since these
are the same pre-existing records, unaffected by cycle-11's fix):

| Function | File:line | Cyc/Cog/ABC | Reason grade 2 is acceptable |
|---|---|---|---|
| `_write_while_sweep_reads_fifo` | `test-check-domain.py:1044` | 8/16/23.8, driver cognitive | Pre-existing BUG-1304-era race-condition fixture (many sequential setup/assert steps), not BUG-1305's own code and not touched by this delta. |
| `run_bug1305_digest_repair_cases` | `test-check-domain.py:3878` | 4/5/37.3, driver abc | ABC-driven fixture/assert accumulator (five sequential digest-repair scenarios, one more than c1 counted since this delta added the digest-Write-beside-witness case per QA-F1); splitting would fragment the shared `prior`/`artifact` fixture across functions for no readability gain. |
| `_bug1305_identity_refusal_cases` | `test-check-domain.py:4995` | 13/5/31.0, driver cyc+abc | Five refusal-case constructions plus assertions, same fixture-per-case shape as its siblings; cyclomatic rose slightly from c1's 11 to 13 because QA-F3 added two conjuncts to one assertion, not a new branch in production code. |
| `case_bug1305_run_identity_invariant` | `test-check-state.py:4560` | 12/7/35.3, driver cyc+abc | Six fixture-tree constructions (X/V/Y/Z/L/W) plus two full-run assertions; already grade 2 pre-refactor (c1) and unaffected by this delta. |
| `case_uid_mint_and_injection` | `test-run-identity.py:64` | 5/4/38.7, driver abc | ABC-driven: mint-shape, injection-preserves, no-replace, no-newline and missing-file behaviours of one primitive tested together, matching this file's case-per-topic convention. |
| `case_seed_conflict_guards` | `test-run-identity.py:86` | 6/4/26.1, driver abc | Run-id-first guard, squad guard, and two born-null cases are one coherent topic (the write-once seed's null-tolerance), per T-01's own instruction to build the marker through `record_seed`. |

All six are TEST code (bar 3, not production bar 4); grade 2 never blocks the build once reasoned,
and none is newly introduced or worsened by this cycle's own diff — I confirmed this by comparing
each cyc/cog/abc triple against c1's independently-run numbers at the earlier head and finding no
functions that dropped a grade band that weren't already at grade 2 there. `code_grade: grade_2`.

## Findings

None at `low` or above. Two `info`-level observations, both **rulable at ship, no code required**:

- **info** — the empty-string placeholder content (`""`) built for the new `RE_RUN_IDENTITY` Edit
  branch is never read by `shape_problems()`'s witness check (it denies on path alone), so the
  placeholder is inert. A future maintainer skimming the tuple shape might wonder why content is
  blank here when every other branch reconstructs real content. A one-line comment noting "content
  is unused for this match — the witness denies by path alone" would preempt that question. Not a
  correctness issue; nothing behaves differently either way.
- **info** — the panel-artifact commit `e77b30ca` bundles unrelated files (four `-c1.md` review
  notes, a receipt, a research note, an observations file) into the same commit as the review
  pin. This is intentional per the Contract ("preserved panel artifacts and the budget record")
  and not a defect, but a future delta reviewer diffing `dc0e0313..e77b30ca` naively (as I did on
  first pass) will see 15 changed files and must independently reconstruct that only 7 are
  in-scope, exactly as I had to. Worth a one-line pointer in whichever note hands off the next
  pin, saying explicitly "N of the M changed files are panel-artifact housekeeping, not code."

`severity_max: none`. `must_fix: []`.

## What my verdict does NOT license

A reader must not infer from this PASS that the Edit route is now fully equivalent in strength to
Write for every protected pattern (`RE_RUN_DIGEST`/`RE_STATE_YAML`/`RE_HANDOFF` still go through
`_edit_reconstructed_content` and its `except OSError: return None` fall-through — that fall-through
is BENIGN for those three patterns only because an absent prior is legitimately unprotected there,
per c1's own F-04 analysis, and this delta did not touch that reasoning or re-verify it). Nor should
this PASS be read as clearing the SEC-01 directory-level-removal residual (`#1376`, unchanged,
explicitly out of scope this cycle) or as certifying the Bash-route end-to-end PostToolUse delivery
path (explicitly disclosed as unmeasured, unrelated to this delta). Nor does `code_grade: grade_2`
mean this delta introduced any new grade-2 debt — every gated grade-2 record here predates this
delta's own diff; the one function this delta actually touched (`_bug1305_marker_file_protection`)
is grade 3 PASS on its own bar. This review is scoped to the 7-file delta named in the Contract; it
says nothing new about the rest of the feature that c1 already covered.

## Repository state

```
$ git -C /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1305-run-state-clobber status --porcelain
 M .harness/harness/features/BUG-1305-run-state-clobber/observations/harness-pm.md
?? .harness/harness/features/BUG-1305-run-state-clobber/notes/research-BUG-1305-goalcheck-build-c2.md
?? .harness/harness/features/BUG-1305-run-state-clobber/notes/review-harness-qa-c2.md
?? .harness/harness/features/BUG-1305-run-state-clobber/notes/review-harness-security-reviewer-c2.md
```

(Captured before I added my own note; these three are concurrent peer panel members' outputs —
`pm`, `qa`, `security-reviewer` — not mine. I wrote and touched nothing else.)
