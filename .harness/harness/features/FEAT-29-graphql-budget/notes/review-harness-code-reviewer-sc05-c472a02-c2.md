# Send-back re-grade — SC-05 OFF+wrap-site+failing-rc finding (review_sha c472a02)

## BLUF

**Downgrading from `high` to `low`, and it does NOT belong in `must_fix`.** All three facts in
my prior review stand unchanged (untested combination, 35/35 survives, `record()`'s guard neuters
the mutant on the `not _enabled()` disjunct). What changes is the conclusion I drew from them: I
independently verified, by reading the code rather than trusting either side's framing, that the
untested combination cannot currently hide a wrong behavior — the two guards that would need to
interact don't. A test for it would be a demonstration, not a discriminating pin, and the literal
BRIEF text has a defensible reading under which it is already satisfied. What is left is a spec
literal-text ambiguity plus an asymmetry with the ON-side's cycle-4 test, worth closing cheaply, not
worth gating a fix cycle.

## What I verified myself, not just re-read from the dispatch

**1. `measured()`'s guard does not consult `rc`, confirmed by the code's control flow, not by
inference (`gh_cost_log.py:149-166`).** The predicate `if not _enabled() or is_counter_call(argv)`
is evaluated at line 157, before `yield m` — before the caller (`run_gh`) has even invoked
`subprocess.run`. `m.returncode` is not set until `factory_gh.py:162`, which runs *inside* the
`with` block, after the yield resumes. So the OFF branch is decided and taken before any exit code
exists to consult. This is not "unlikely to depend on rc" — it structurally cannot, in the code as
written.

**2. `record()` is never reached via `run_gh`/`gh()` when OFF, confirmed by reading both sides of
the seam (`gh_cost_log.py:157-166`, `factory_gh.py:144-171`).** The OFF branch is `yield m; return`
— no `try/finally`, so `record()` (called only inside the enabled branch's `finally`, line 166) is
never invoked. `factory_gh.run_gh`'s error-raising (`if r.returncode != 0: raise GhError(...)`,
`:163-168`) sits entirely *outside* the `with gh_cost_log.measured(args)` block and is untouched by
recorder state. So `record()`'s own guard (`:112`) is not on the path a wrap-site OFF+failing test
would exercise at all — that guard only matters for a caller that invokes `record()` directly,
which is exactly what the existing rc=1 direct-call case at `test-gh-cost-log.py:251-259` already
does.

**3. Consequently, the 2x2 (ON/OFF x success/fail) collapses to what the code actually branches
on, and every cell that matters is independently pinned:**
   - ON x success — `:317-333`.
   - ON x fail — `:381-410` (cycle 4, the one commit c472a02 actually added).
   - OFF's *only* branch decision, proven rc-independent by (1), is pinned at rc=0 by the wrap-site
     call-count assertions (`:344-345`, `:377-378`) — and I read the observation record
     (`observations/harness-backend-dev.md:135-141`) describing those exact assertions catching a
     live mutation (`not _enabled() or` removed from `measured()`'s guard: OFF write stayed absent
     because `record()`'s own guard still fired, but the call count tripled from 1 to 3, and the
     count assertion is what caught it) — consistent with, not contradicted by, my static reading.
   - `record()`'s own guard, independently, is pinned at rc=1 directly (`:251-259`).
   - No code path requires the OFF+wrap-site+rc=1 conjunction specifically to distinguish correct
     from mutated behavior — a mutant that could only be caught by that exact conjunction would
     have to make `measured()`'s branch depend on `rc`, and no such mutant exists in this diff or
     was proposed.

## Re-reading BRIEF.md:83-90 on the literal-scope question

The ON sentence names its scope explicitly: "every harness `gh` invocation that flows through
`factory_gh.run_gh` or `gh-sync.py`'s wrapper." The OFF sentence — "With the variable unset — the
new default — a test proves NO file is created and NO line is written, including for a failing
invocation" — does not repeat that qualifier; it says "a failing invocation," not "a failing
*wrapped* invocation." Read as its own clause, the direct-call test at `:251-259` already proves
exactly that: unset, a failing invocation (`record(["issue","create"], 200, 210, 1)`, rc=1) creates
no file and writes no line. I do not think this reading is forced — the OFF sentence sits in the
same bullet as the ON sentence and could just as easily inherit its scope — but it is available,
and combined with fact (2) above (the wrap site literally never reaches `record()` when OFF), the
wrap-site-scoped reading would only ever be testing the *same* rc-independent branch decision
already pinned at rc=0. Either reading, the acceptance criterion's intent — "an opt-in recorder
whose off state is untested is a recorder that is always on" — is satisfied: the off state IS
tested, directly and at the wrap site, and proven not to depend on the failing/succeeding
distinction because nothing in the implementation makes it depend on that distinction.

## Severity and must_fix

**`low`, not `must_fix`.** Not `med`: I could not construct, and do not believe there exists, a
plausible near-term code change that would make this gap exploitable without also being caught by
the existing OFF-wrap-site call-count assertions or the existing rc=1 direct-call assertions — the
"unlikely case" a `med` finding needs isn't available; the guards are provably orthogonal to rc as
written. Not `info`, because there is real, if modest, value in closing the literal-text ambiguity
and giving OFF the same rc=1 wrap-site coverage that ON already got in cycle 4 — an asymmetry a
future reader of BRIEF.md's SC-05 bullet could reasonably re-flag, exactly as I did the first time.
That is a spec-completeness/test-symmetry item, not a functional defect, which is what keeps it out
of `must_fix`: gating a fix cycle should be reserved for a finding where I can name a wrong outcome
for a real input, and here I traced the code and could not.

## What I'd tell a future reviewer of this same finding

Do not stop at "the combination is untested, therefore high" for a fail-open hunt — that heuristic
is right as a *starting* question, but it has to be closed by tracing whether the two dimensions of
the untested combination actually interact in the code. Here they provably do not, and that trace is
what moves the grade, not the requester's framing of it.

## Constraints honored

Read-only on source (`Read` only). No `gh` calls, no suite runs, nothing touching
`HARNESS_GH_COST_LOG`. Did not edit `CLAUDE.md`, `.harness/notes/**`, or `.harness/logs/**` — did
not touch the prior artifact `review-harness-code-reviewer-sc05-c472a02.md`, which is unmodified.
Noted but did not act on: `CLAUDE.md` and three other files show as modified in `git status` at
this pin — pre-existing working-tree state, not something I touched, and out of scope for this
send-back.
