```yaml
VERDICT: PASS
DIGEST:
  headline: "M1 is genuinely discharged: preDomain's edit branch is byte-identical to cycle 0 (still fail-open on an unparseable patch), but the two facts that made it HIGH — untested, and zero signal anywhere — are both now false, confirmed by my own mutation and an end-to-end script. One should_fix (med): the exact end-to-end claim the commit rests on has no permanent regression test. One low: scanned_count()'s middle assertion vacuously passes on a crash, mitigated by its two siblings."
  severity_max: med
  findings: 2
  must_fix: []
  spec_violations: []
  reviewed: "6d6d1cea..fbaa7fec (fix cycle reviewed as new code: 83282dea..fbaa7fec)"
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "Should 'not blocking unparseable edits' graduate from a code-comment-and-test-comment disclosure into an actual DEC, given the panel that flagged this HIGH never signed off on the fail-open being acceptable — only on it being tested and announced? Not this role's call; routing per O-05.", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/BUG-1030-stale-anchor-write-hazard/notes/review-harness-code-reviewer-c1.md
```

# Review — BUG-1030-stale-anchor-write-hazard — review-c1

Diffed `6d6d1cea..fbaa7fec` (**executed**, `git log --oneline`); HEAD `e024599` adds only the pin
record, confirmed. Reviewed `83282dea..fbaa7fec` as new code per dispatch — **executed**, `git diff
--stat`: 11 files, 686+/9-, of which only two are source/test (`.omp/extensions/harness-hooks.ts`,
`.claude/skills/harness/bin/omp-hooks.test.ts`, `test-validate-feature-json.py`); the rest are
governance notes (feature.json, review_sha, handoff-*, and the four cycle-0 review artifacts, which
this commit merely committed into git — they were already reviewed as content in cycle 0 and are not
re-litigated here). No `[harness:human]` commits in range (**executed**, `git log --format`, zero
hits).

## M1 — is it discharged? YES, on the two facts that made it HIGH.

**The code is unchanged.** `preDomain`'s edit branch (`.omp/extensions/harness-hooks.ts:219-234`,
call site `:684`) is byte-identical, same line numbers, to what cycle 0 reviewed — **executed**, `git
diff 83282dea..fbaa7fec -- .omp/extensions/harness-hooks.ts` touches exactly one hunk, the
`postDomain`/S2 advisory string at `:845-855`, nothing in `preDomain`. An unparseable edit still lands
with **zero domain check** at the PRE gate. That part of M1's finding stands, unchanged, and is now a
disclosed, deliberate decision rather than an oversight (code comment `:846-850`, test comment
`:534-538`) — see the not-blocking judgement below.

**What actually changed, and what it closes:**

1. **"Uncovered by any test" — now false, mutation-confirmed.** I copied the real module to a scratch
   file outside the worktree (`/tmp/bug1030-scratch/omp-mutated/harness-hooks.ts`, DEC-174), neutered
   *only* `preDomain`'s edit branch (`if (false && toolName === "edit")`, `postDomain` untouched), and
   ran the three new `tool_call` cases against it directly through `registerHarnessHooks` (**executed**,
   `bun run mutation-test.ts`): the two positive-path cases ("a hashline edit is gated BEFORE it
   lands", "every file of a multi-section edit is gated") both redden — `pre.length` goes from 1 to 0
   and the multi-file path list goes from `["a/one.json","b/two.yaml"]` to `[]`. The third case ("a
   non-string patch reaches no pre-write gate") stays green, correctly, since it asserts the documented
   fail-open and doesn't depend on `preDomain` running. **This is an exact match to the commit's own
   claim** ("neutering the PRE branch now reddens 2 tests"). The two reddening cases bind real
   behaviour: they assert `pre[0].payload.tool_input` equals `{ file_path: path }` exactly (`toEqual`,
   not a substring or membership check) and `tool_name === "Edit"`, with no `--post` in args — a
   regression that silently dropped a path, added an extra field, or reused the POST args shape would
   redden them too.
2. **"Zero signal anywhere" — now false, confirmed end-to-end, not just per-hook.** I wrote a second
   scratch script that fires `tool_call` then `tool_result` on the *same* unparseable edit payload
   through the real (unmutated) module (**executed**, `bun run e2e-check.ts`): `tool_call` returns
   `undefined` (no block) and spawns zero `check-domain.sh` calls; `tool_result` on the identical input
   returns `{ content: [{ text: "...neither the pre-write nor the post-write shape check ran on any
   file..." }] }`, no `isError` key. This corroborates the commit message's "MEASURED... S2 DOES fire on
   the same edit, so the operator is told once" — cycle 0's "zero signal anywhere" was true of the
   pre-gate in isolation and is false end-to-end, exactly as claimed. I verified this independently at
   source rather than taking the commit message's word for it.

**Net severity call.** The panel's HIGH rating combined three things: wrong-in-a-realistic-case
behaviour, zero test coverage, and zero signal. Behaviour is unchanged (still fail-open on unparseable
edits), but it is now a structurally-defensible position, not an oversight: `extractEditPaths` failing
means no file was identified, and there is no target to hand `check-domain.sh` — blocking *every*
shape-unreadable edit outright would be a fail-closed policy change with its own cost (refusing
legitimate edits whose patch text happens not to match the two regexes), which is exactly the kind of
enforcement-semantics change DEC-174 reserves for a real decision, not a silent side-effect of a bug
fix. Coverage and signal — the two things a code reviewer can gate on independent of that policy
question — are both closed, measured. I am not re-raising M1 as a must_fix. The unresolved policy
question is Q1 above, correctly routed as a question rather than decided unilaterally by me.

## Per-assertion analysis of the three new `tool_call` cases

| Test | What it binds | Verified how |
|---|---|---|
| "a hashline edit is gated BEFORE it lands" | `preDomain`'s edit branch reaches `check-domain.sh` exactly once, with the exact extracted path, `tool_name: "Edit"`, and no `--post` — the PRE/blocking route's happy path, previously completely unexercised | Mutation: reddens when `preDomain`'s edit branch is neutered (**executed**) |
| "every file of a multi-section edit is gated before it lands" | Same route, multi-path extraction, order preserved | Mutation: reddens (**executed**) |
| "a non-string patch reaches no pre-write gate and does not block the edit" | The *current, disclosed* fail-open: zero `check-domain.sh` calls of either kind, `blocked` undefined | Does NOT redden under the PRE mutation (**executed**, correctly — it isn't testing PRE's happy path) — it pins the fail-open as a known, regression-guarded state: if a future change accidentally started blocking here, or accidentally started calling `check-domain.sh` with a fabricated path, this test would catch either |

None of the three overclaims what it binds. This is a real, discriminating fix to the coverage half of
M1, not a coverage-shaped decoration.

## `scanned_count()` — does it bind what it claims?

**Mostly, with one asymmetric residual.** `test-validate-feature-json.py:26-41`, regex `r"—\s*(\d+)\s*
file\(s\)"` against `validate-feature-json.py:52-53`'s literal `print(f"scanning ... — {len(paths)}
file(s)", file=sys.stderr)` — the em-dash and spacing match exactly (**executed**, ran the real suite:
`ALL PASS`, including all three `scanned_count`-based checks against this repository's actual 41
`feature.json` files, which is the exact count that broke the old substring check).

- **Absent/garbled stderr** (e.g. an unhandled exception before the print — `harness_boundary.
  resolve_root`'s `strict=True` path raises `ValueError` if neither `HARNESS_PROJECT_DIR` nor the
  script-derived root carries `team-config.yaml`): `scanned_count` returns `None`.
- For the two `== 1` assertions (`case_migrated_depth`, and the second half of `case_root_resolves`),
  `None == 1` is `False` → the check **fails loudly**. Fail-closed, correct.
- For the middle assertion (`case_root_resolves`'s first check, `scanned_count(r.stderr) != 1`),
  `None != 1` is `True` → the check **passes vacuously**. This is a genuine fail-open: a crash or a
  future rewording of the "scanning..." line that broke `scanned_count` universally would silently
  satisfy this one assertion while correctly reddening its two siblings in the same file.
- **Reachability, checked, not assumed:** in this test's own fixture, the `ValueError` path cannot
  fire — `resolve_root`'s fallback (`derived`, computed from the script's own on-disk location) always
  carries `team-config.yaml` in any context where this test suite itself can run, since the suite is
  testing this checkout's own tooling. A universal wording regression, if it happened, would still be
  caught by the two `==1` siblings in the same file. **Severity: low, not the "fourth" assertion the
  dispatch asked me to find** — it doesn't let a real regression through undetected given its
  neighbours, unlike the three assertions already found in this effort, each of which was the *only*
  guard for the property it claimed. Named because the fix's own docstring claims "parsing the integer
  makes the criterion the thing the name claims it is," and for this one assertion that claim overstates
  by one edge case.

## The fourth-assertion hunt: searched, none found that meets the bar

Searched the full fix-cycle diff (`omp-hooks.test.ts`'s 52 new/changed lines, `test-validate-
feature-json.py`'s 27) plus the tests each new assertion depends on transitively (`fixture()`/`start()`
in `omp-hooks.test.ts`; `discover_paths()` and `harness_boundary.resolve_root` for the Python side) for
an assertion whose name claims more than it checks. Specifically checked and ruled out:

- Both new `pre.length`/`tool_input`/`tool_name` assertions use `toEqual`/`toBe`, not `.includes()` or
  membership — no adjacency or exhaustiveness gap (Expertise G-11/G-13 shape). Mutation-confirmed
  discriminating.
- No collision risk in `scanned_count`'s regex: grepped the whole `bin/` tree for other `"file(s)"`
  producers (**executed**) — `validate-feature-json.py:53` is the only one; nothing else could feed a
  false match into the same stderr stream.
- The `!= 1` asymmetry above is real but mitigated by siblings (documented, not silently passed over
  per Expertise P-15).
- `cycle` → `cycles_used` (DEC-154): not reviewable from this diff — `runs/**` is gitignored
  (**executed**, `git check-ignore -v`), so this rename touches no tracked file and isn't part of
  `base..review_sha`. Read directly at source: the current run's top-level key is `cycles_used: 0`,
  the whitelisted INV-16 key (**executed**, grepped `check-state.sh`'s `KNOWN` set). Correct as far as
  it's checkable; not a code-review target since it's ephemeral, untracked run state.

**One genuine gap, reported as should_fix rather than a fourth "assertion that lied":** the end-to-end
claim itself — that firing `tool_call` then `tool_result` on the *same* unparseable edit produces the
S2 notice — has **no permanent test**. Both halves are tested in isolation (three new `tool_call`
cases; one existing `tool_result`/S2 case), but nothing in the shipped suite drives both hooks in
sequence on one input and asserts the composed outcome. I only know it holds because I wrote that
script myself, outside the checked-in suite. If a future refactor decoupled the two `extractEditPaths`
call sites (e.g., made S2 conditional on state `preDomain` sets), nothing would catch the regression
until the next incident. **Alternative:** one more `test()` in the same describe block, driving
`tool_call` then `tool_result` on an identical unparseable payload and asserting `(a)` zero
`check-domain.sh` calls total, `(b)` the returned `tool_result` content contains the "neither...nor"
text — pinning the exact claim the commit's justification rests on.

## Stage 1 — spec compliance

No BRIEF/plan.yaml (confirmed again, `handoff-plan.md` unchanged from cycle 0). Spec surrogate is the
analysis note + `handoff-build.md`; the fix cycle's own commit message is its most specific
self-description, checked against source above (M1 section) and matches. No scope creep: every
touched file is either the PRE-gate fix's test coverage, the `scanned_count` fix (an incidental defect
found while chasing what looked like an environmental failure — disclosed as such in the commit
message, not smuggled in), or governance/notes commits. No omission found beyond the one already
flagged (Q1's policy question, correctly left open rather than decided).

## What I did not find a defect in

`postDomain`'s branch, `runPolicy`, `firstBlock`, and every other function in the file are
byte-identical to `83282dea` (**executed**, `git diff` shows exactly the one hunk). The `_dabsentT02`
and case_22/realpath residuals from cycle 0 are untouched by this diff and out of this cycle's scope
per dispatch.
