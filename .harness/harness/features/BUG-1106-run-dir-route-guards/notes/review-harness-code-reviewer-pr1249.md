# Review — PR #1249 (BUG-1106-run-dir-route-guards)

Reviewed `main..500000ad` in the worktree at `.claude/worktrees/BUG-1106-run-dir-route-guards`.
Ran both full test suites (`test-check-domain.py`, `test-bash-write-guard.py`) — both exit 0,
every case `ok`, none skipped. No source edits made (read-only role).

## VERDICT: FAIL

One `must_fix`: a confirmed, untested gap in the new Bash-route guard that contradicts the PR's
own stated claim ("refused on every route"). Everything else — the Edit-route content
reconstruction, the state.yaml fail-closed change, the shared-pattern respelling — is sound,
well-tested, and traced clean by hand.

## must_fix

### 1. `_run_artifact_guard` is placed after the DEC-153 worktree carve-out — the new Bash-route protection is inert for any write whose target resolves under `.claude/worktrees/`

`bash-write-guard.sh`'s findings loop (`:754-822`) has an unconditional early `continue` at
line ~765 for any `rel` matching `^\.claude/worktrees/` — **before** `harness_boundary.classify()`
is ever called, and therefore before either `feature_checkout_guard` or the new
`_run_artifact_guard` (called only from the `allow`/`not_a_domain_question` and `shared` branches,
`:813-819`) ever runs. I traced this by hand against the actual source, not the diff summary.

For `feature_checkout_guard` this exemption is correct by construction: its whole question is
"is this feature artifact in the main checkout when it should be in a worktree", so once you're
already inside *some* worktree there's nothing for it to answer (test-bash-write-guard.py itself
pins this as intentional: "DEC-153 pinned: ... the carve-out is blanket and depth-agnostic").

`_run_artifact_guard`'s rule has nothing to do with which checkout the write lands in — it says
"never write digest.md/state.yaml via Bash, anywhere" (its own docstring: "these two files must
be written through Write or Edit... a route denial is the weakest sufficient rule"). Wiring it in
at the exact same call sites as `feature_checkout_guard`, after the exact same carve-out,
silently narrows that "anywhere" to "anywhere except inside a worktree" — exactly the location
where run artifacts live for the *normal* case (DEC-95: worktree-per-feature). Confirmed this is
not merely a main-checkout vs. worktree distinction that resolves itself per-session: `root` here
is resolved once via `harness_boundary.resolve_root()`/`HARNESS_PROJECT_DIR`, and test fixtures in
this same suite (`test-check-domain.py:3513-3517`, "a session ROOTED in an out-of-place worktree")
show a session's own root need not be the checkout it's writing into. Any Bash write whose
resolved absolute target sits under `<the writer's own resolved root>/.claude/worktrees/...` —
cross-checkout access into a sibling worktree, or any process (main session, an orchestrator, a
misrouted agent) rooted outside the specific worktree holding the run — skips `_run_artifact_guard`
entirely, with **zero test coverage**: `_run_artifact_fixture()` (test-bash-write-guard.py:1031-1035)
places digest.md/state.yaml directly at the fixture root, never inside `.claude/worktrees/`, so
none of the four new `bug1106 Bash route` cases exercise this interaction at all.

This also makes a claim in the commit message inaccurate: "any write into an existing run dir's
digest.md or state.yaml that is not a proven upsert of the current run is now refused **on every
route**" — it is not, for the Bash route, once the target is inside a worktree.

**Mitigating context, so this is scoped correctly:** the *primary*, content-aware defenses (the
Write/Edit routes in check-domain.sh, which are the actual fix for gap (b) and the correctly-built
gap (a) Edit interception) have no such carve-out — `_norm()` resolves worktree-nested targets to
their checkout-relative form regardless of physical location, so those two routes protect run
artifacts everywhere, worktree or not. Only the Bash route's path-only refusal (already the
weakest of the three, by the PR's own admission — "Bash carries no complete incoming payload to
compare") has this scoping hole. That downgrades it from "the whole fix is defeated" to "the
weakest of three layers has a location-dependent hole in exactly the location run artifacts
normally live" — still a real, realistic-case defect (`severity: high`, not `critical`), and it
gates because it is untested and the commit message overstates coverage it doesn't have.

**Recommendation:** call `_run_artifact_guard` ahead of the DEC-153 continue (its rule doesn't
depend on checkout placement, so it doesn't need to wait for `classify()` either), or make the
scoping decision explicit with a comment plus a test that pins the current behavior the way
`test-bash-write-guard.py:679-686` already pins `feature_checkout_guard`'s equivalent exemption —
so a future reader can tell "considered and accepted" from "missed."

## Should-fix / notes (do not gate)

### 2. Two "left untouched" assertions in the new Edit-route tests are vacuous
`run_bug1106_edit_route_cases` (test-check-domain.py:3699, :3720) asserts the on-disk file still
equals its prior content after a refused Edit. `check-domain.sh` never opens the agent's target
path for writing in any code path (grep-verified: the only `open(..., "w")` in the whole file is
the sweep's own internal high-water-mark stamp, `:2035`), and `_fire_edit`/`_fire_digest_edit`
never apply the simulated edit to disk either — so this assertion is true unconditionally,
independent of the hook's exit code. It adds no coverage beyond the adjacent exit-code check.
Not a bug, just decorative; matches the "assertion's subject" pattern from `harness-code-review`
(binds "did our own test harness touch the file", not "did the guard prevent the edit").

### 3. check-domain.sh's local RE_RUN_DIGEST/RE_STATE_YAML could have used an absorbing import instead of a hand-kept duplicate
The stated reason for not importing from `harness_boundary` (the shape phase's import must stay
*absorbing*, never fail-closed, or a broken module blocks the only tier — the main session —
that can repair it) is correct and well precedented elsewhere in this exact file. But the file
*already* demonstrates the safer alternative two functions above: `_root()` (`:128-142`) does
`try: import harness_boundary ... except Exception: return _derived` — an absorbing import with a
hardcoded fallback, not a bare duplicate. The same shape (`try: RE_STATE_YAML =
harness_boundary.RE_STATE_YAML; except Exception: RE_STATE_YAML = re.compile(...)`) would have
kept the single source of truth without weakening the fail-open guarantee. As shipped, the two
copies can only be kept honest by the new `run_bug1106_shared_pattern_consistency` test, which
*is* wired into `run-unit-tests.sh`'s `INTEGRATION_SCRIPTS` (verified) and does run — so this is a
real but low-priority design nit, not a live risk.

## Verified sound

- **`_edit_reconstructed_content`** (check-domain.sh:1813-1839): hand-traced both the
  single-match and `replace_all` branches against `str.count`/`str.replace` semantics — they
  agree (both are literal, non-overlapping, left-to-right). The "ambiguous → return None → allow
  through" fallback is not exploitable as a bypass: if `old_string` occurs zero times, or more
  than once without `replace_all`, Claude Code's own Edit tool refuses to apply the edit at all
  (undocumented from inside this read-only review — I could not invoke the real Edit tool to
  confirm this directly, so flag it `[INFERENCE]`, though it matches the tool's publicly
  documented match-uniqueness contract and the same assumption `approval_guard`'s existing Edit
  branch, two hundred lines above, already relies on for identical reasons). Either way, an
  attacker cannot get *both* an ambiguous match at the guard *and* an applied destructive edit —
  those two outcomes are mutually exclusive by the tool's own contract, not by anything this hook
  enforces.
- **PRE-dispatch control flow** (check-domain.sh:1841-1868): traced the full truth table by hand.
  Write to any path (digest/state or not): unchanged, reaches the same `targets` assignment as
  before. Edit to an unrelated path, or with no target: still exits 0 immediately (unchanged from
  pre-PR — Edit was never processed on this route before). NotebookEdit: still exits 0
  (`_tool != "Write"` catches it in the `elif`, same as before). Edit to digest.md/state.yaml:
  the only newly-reachable branch, and it correctly feeds the same `shape_problems()` the Write
  route already used. No other shape rule (feature.json, CLAUDE.md, handoff, plan.yaml) was
  widened to Edit, matching the PR's stated narrow scope.
- **State.yaml fail-closed change** (check-domain.sh ~:1450-1490): unparseable prior, prior with
  no `run_id`, incoming with no `run_id` against a `run_id`-bearing prior, and the mismatch case
  are all refused; equal-`run_id` upsert and brand-new-file remain allowed. Confirmed against the
  full test run (`state-no-prior-run-id-refused`, `state-no-incoming-run-id-refused`,
  `state-prior-unparseable-refused`, `state-run-id-upsert-allowed`, `state-new-file-allowed` all
  `ok`).
- **harness_boundary.py addition**: minimal, additive, no other call sites touched.
- **Test suites**: both run clean, exit 0, 0 FAIL lines (full output captured this session).
  I could not independently re-run the commit's hand-done RED proof (reverting the Edit
  interception / the `_run_artifact_guard` call and confirming exactly the new cases redden) —
  my tool access is read-only and `bash-write-guard` itself blocks every file mutation from this
  role, including scratch copies under `/tmp`. I substituted a full manual control-flow trace
  (above) in its place, which supports the claim for the Edit-route and state.yaml changes.
  I could not similarly re-derive the Bash-route RED proof by inspection alone without finding
  the DEC-153 gap above, which the by-hand proof described in the commit message would not have
  caught either (a revert-and-rerun proves the code path is reachable somewhere, not that it is
  reachable everywhere the commit message claims).

reviewed: main..500000ad
