# Plan-panel cycle 1 — scope reader (harness-code-reviewer) — FEAT-50-run-artifact-integrity

**BLUF: PASS with one `med` finding worth the operator's attention before signature, one `low`
anchor nit, and both cycle-0 `high` findings CLOSED on verified evidence.** Traceability is exact
(REQ-01..09 union, no orphan, no phantom trace), `depends_on` is acyclic and its one asymmetry is
harmless, and every anchor I re-measured at 5d12e68 — some 20+ line citations across
`check-domain.sh`, `bash-write-guard.sh`, `validate-digest.py`, `check-state.sh`,
`feature-worktree.py`, `test-validate-digest.py`, `run-unit-tests.sh` — was accurate to the byte
except one. This is an unusually well-grounded amendment.

## Findings

### F1 — `med` — T-03's checkout-binding placement misses a verdict shape T-09's does not

`lands_on`: T-03, T-09, D-10, REQ-03, REQ-08

**Summary:** T-03 places the new worktree-binding check only inside `domain_check()`'s `allow`
and `shared` branches; `harness_boundary.classify` returns a *third*, structurally earlier outcome
— `not_a_domain_question` — via its own dedicated `return` at check-domain.sh (before `rel =
_verdict["rel"]` and the `allow` branch), so a write landing on that outcome never reaches T-03's
check. T-09 narrows `bash-write-guard.sh:747`'s `if verdict["outcome"] in ("allow",
"not_a_domain_question"): continue` — a **single** statement covering both outcomes — so, taken
literally, T-09's check *does* fire on `not_a_domain_question`. The two "route-complete" fixes are
not actually symmetric in what verdict shapes they intercept, even though D-10 states they use
"the SAME seam... no second derivation."

**Consequence, and how discovered:** I reproduced `not_a_domain_question` directly against
today's unmodified `harness_boundary.classify` (`.claude/skills/harness/bin/harness_boundary.py`):
a session whose resolved `root` is a registered worktree, writing a target that names the SAME
feature's path but lives in a *different* checkout tree (e.g. the main checkout, or vice versa),
classifies as `not_a_domain_question` rather than `allow` — because `select_base` cannot place a
target outside the root's own tree without a base relationship it recognizes. I confirmed this
both via direct `classify()` calls and via a live `check-domain.sh` subprocess (exit 0, no denial,
today). If a governed agent's session `root` can ever differ from the checkout its own target
tree lives under in this shape — which is exactly the geometry a worktree-rooted agent
mistakenly constructing a main-checkout path would produce, the precise failure mode #1057
describes — the tool route's fix (T-03) silently permits the write while the Bash route's fix
(T-09) would deny the identical write. Neither T-03's own `verify:` (which only ever sets
`HARNESS_PROJECT_DIR` to the main checkout) nor T-05's documented cases (`feature-checkout-main`,
`-inside`, `-absent`, all built on the same root=main pattern) exercise a `not_a_domain_question`
outcome at all, so this gap would not be caught by anything in the plan as written.

**What I could not settle:** whether a governed subagent's resolved `root` ever actually *is* the
worktree itself in this harness's real dispatch (as opposed to always inheriting the outer
session's own root, typically main, with only the *target path* varying into a worktree) — that
determines whether this is a live reachability gap or an inert corner case. `resolve_root`'s own
docstring ("HARNESS_PROJECT_DIR ... always names the session project root") reads as consistent
with either. I did not find code that settles it either way within my scope. Recommend: before
relying on T-03/T-05 as proof of route-completion, either (a) add a `not_a_domain_question` case
to T-05 mirroring case 1 with `root` set to a worktree and target aimed at the sibling main
checkout, or (b) get an explicit statement from whoever owns subagent dispatch about whether a
governed agent's `HARNESS_PROJECT_DIR` can differ from the top-level session's.

### F2 — `low` — D-11's line citation is off by one

`lands_on`: D-11

**Summary:** D-11's `because:` cites `validate-digest.py:1414` for `cands = ([path] if
os.path.isabs(path) else [os.path.join(_root_or_none() or "", path)])`. Re-measured at 5d12e68:
that assignment is at **line 1413**; line 1414 is `found = next((p for p in cands if
os.path.isfile(p)), None)`. The substance of D-11's claim is correct and I verified it directly —
this is a one-line anchor drift, not a wrong description.

**Consequence:** trivial — a reader jumping to the exact line lands one line low. No task or `SC`
depends on this citation being byte-exact (unlike, say, T-02's or T-04's citations, which I
independently re-measured and found exact).

## Cycle-0 findings — disposition

Both `high` findings that were mine (`scope`) are **CLOSED**, on evidence, not on the plan's own
say-so:

- **`PF-3d9ac1d0…`** (Bash route unbound). CLOSED. Re-confirmed `bash-write-guard.sh:747` reads
  exactly as the ruling cites; T-09's intent narrows that continue with a concrete branch
  structure (feature-id-from-path, `worktree_for_feature`, containment via `checkout_relative`,
  message naming both target and worktree), T-10 adds a reachability-proof case
  (`bash-feature-checkout-red`) and the short-form clause (`bash-feature-checkout-short`) that was
  the original finding's own emphasis. SC-18/SC-19 grade it. (See F1 above for a *narrower*,
  newly-found gap in the *sibling* fix, T-03 — not a reopening of this finding, which was
  specifically about the Bash route having no binding at all; it now has one.)
- **`PF-964d6356…`** (obsolete exit-0 test expectation). CLOSED. Re-measured
  `test-validate-digest.py:738-739` — the exact case text the ruling cites is still present
  unmodified; T-02 step 5 names it verbatim and instructs deletion (not rewrite, with a stated
  reason), T-02's `verify:` adds the `grep -cF ... -eq 0` control, and SC-17 grades the removal at
  `<review_sha>` independent of the task instruction.

The three findings that were `should-not-exist`'s (T-06 Write-only caveat, T-03's
then-unreachable allow branch, D-07's fixed-path mutant collision) are not mine to grade or close;
I note only that D-07's mutant idiom (unique-per-process, dot-prefixed, `finally`-removed) now
appears uniformly across every red-proof case in T-02/T-05/T-10/T-12, which reads as addressing
that finding's shape, but the disposition call belongs to that reader.

## What I checked and found NOT to be defects (recording so it is not re-litigated)

- **Traceability.** `traces:` across T-01..T-12 unions to exactly REQ-01..REQ-09 — no orphan REQ,
  no phantom trace (verified by direct extraction, not by trusting the plan's own claim).
- **`depends_on` asymmetry** (T-01/T-11 and T-02/T-12 share files with no edge; T-04→T-03 has
  one for the same reason). Harmless: all of T-01, T-02, T-03, T-04, T-11, T-12 are
  `main-session-direct`, i.e. executed serially by the single main session — there is no
  concurrent-write hazard an edge would prevent that isn't already prevented by there being only
  one actor. The T-04→T-03 edge is extra caution, not evidence the other pairs are an oversight.
- **Route-completeness of `lanes:`.** Every task `files:` entry has a matching `lanes:` row (12 of
  12); the two extra rows (`check-state.sh`, `test-check-state.py`) are declared-but-unedited with
  a stated reason (SC-08/SC-11 read them) — not orphans.
  `resolved_at: 75daa3b` with the two `bash-write-guard.sh` rows separately dated `5d12e68` is
  honest disclosure, not a stale pin — I re-ran `--resolve` on both files at HEAD and got the
  cited grant.
- **A third governed write route.** `.claude/settings.json`'s `PreToolUse` registers exactly
  `Write|Edit → check-domain.sh` and `Bash → bash-write-guard.sh` (plus `Task|Agent →
  dispatch-guard.sh`, not a write route). `check-domain.sh` itself already branches on
  `tool_input.get("notebook_path")`, so `NotebookEdit` (matched by the `Edit` pattern) is already
  routed through the SAME `domain_check()` T-03 amends — not a fourth, unbound surface. I found no
  registered hook or sweep outside T-03/T-09's reach for a `.harness/*/features/*/` target.
- **D-03 vs. D-11.** Confirmed `check-domain.sh` reads `harness_feature` nowhere today (0
  matches) — consistent with D-03's ban and with T-03's own instruction not to introduce that
  read. Confirmed `validate-digest.py` already reads `d.get("harness_feature")` at exactly
  `:1514` and passes it to `_hook_feature_dir` at exactly `:1598-1599`, both PRE-existing, both
  unrelated to check-domain.sh's PreToolUse route. The two decisions govern different hooks on
  different routes; they do not disagree.
- **SC-11's positive control and five-row enumeration.** Ran `check-state.sh` live: 37 VIOLATION
  rows, exactly 5 name FEAT-50, and they are exactly the five SC-11 lists (BRIEF not approved,
  `review_sha` unpinned, three DEC-156 digest contract failures). Confirmed `.gitignore:7`
  excludes `runs/**`, so rows 3-5 are structurally absent at the landing checkout regardless of
  whether the authoring leads ever re-emit — SC-11's own "graded from the checkout the feature
  LANDS in" framing is the right resolution, not a hand-wave.
  Ran SC-11's exact evidence command: positive control passes, `rc=1` today as expected
  (externally blocked, per D-09) — the command does not silently pass on a broken run.
- **SC-13's count.** Ran `check-plan-routes.py` on the live plan: exactly 9 DEVIATION lines
  (T-01,02,03,04,05,09,10,11,12), 0 violations — matches SC-13 exactly.
- **T-07/SC-14 heading match, DEC-207 highest-in-use.** Both confirmed against the live
  `DECISIONS.md`.
- **T-08's UNIT/INTEGRATION kind claims.** `test-harness-boundary.py` is in `UNIT_SCRIPTS`;
  `test-inflight-registry.py`, `test-validate-digest.py`, `test-bash-write-guard.py`,
  `test-check-domain.py` are all in `INTEGRATION_SCRIPTS` — confirmed by direct extraction, not
  assumed.

## Anchors re-measured and found exact (not just F2's exception)

`check-domain.sh` :833, :835-841, :843-848, :872, :980-1047 (RE_STATE_YAML/SHAPE_PATTERNS),
:1367-1370, :1376-1381, :1505, :1546; `bash-write-guard.sh` :703, :706, :714, :744, :747, :758-761;
`validate-digest.py` :1343-1357 (`_root_or_none`), :1359-1372 (`_hook_feature_dir`), :1514,
:1598-1599; `check-state.sh` :176-179, :1868-1871; `test-validate-digest.py` :730, :735-739,
:750-769; `feature-worktree.py` ~234-248.

## Open questions

- `{ id: Q1, question: "Can a governed agent's resolved HARNESS_PROJECT_DIR/root ever differ from the top-level session's own checkout (i.e., can it literally equal a feature worktree) for a Task-tool-dispatched subagent, or does root always inherit the outer session's checkout regardless of which worktree a target path names? This determines whether F1 is a live reachability gap or an inert corner case.", blocking: false }`
