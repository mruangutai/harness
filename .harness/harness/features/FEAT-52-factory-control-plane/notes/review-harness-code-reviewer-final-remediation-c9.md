# Code Review — FEAT-52-factory-control-plane — final remediation re-review (post remediation-c9)

`review_sha: 49df4bee`, diffed against `merge-base(origin/main, 49df4bee) = 06bd60c8e3185a166723dfc7bfec860e2bdc88f7`
(same base the remediation-c9 review used). `5bc0b297` (`[harness:human] repin FEAT-52 review SHA`)
sits on top of `49df4bee` and only rewrites `feature.json`'s `review_sha` field — confirmed by
`git show 5bc0b297 --stat`, no other path — so it carries no implementation and is not reviewed.
Eleven commits landed between the remediation-c9 pin (`ff4ca877`) and this one
(`9fe48588` repin .. `49df4bee`); every claim below is grounded via `git show <sha>:<path>`, targeted
`git diff ff4ca877..49df4bee -- <path>` reads, and live execution of every affected unit/integration
suite plus `code-grade.py` at the checked-out tree (byte-identical to the pin for every file cited).

## BLUF

**PASS.** Both `must_fix` items from remediation-c9 are genuinely closed. **F1** (AmbiguousWorktree
silently collapsing to the control-plane root) — `dispatch-guard.sh:171-183` now calls
`hb.worktree_for_feature` directly and catches `hb.AmbiguousWorktree` with its own `except` clause,
positioned before the generic `except Exception` fallthrough, printing the candidates and exiting 2;
the standalone CLI (`inflight_registry.py feature-root`) does the same and is live-tested
(`test-inflight-registry.py::_ambiguous_feature_root_case`, passes). **F2** (`code_grade: fail`) —
reran `code-grade.py --base 06bd60c8..49df4bee`: 38 graded functions, **zero** grade-1 or grade-2
records, zero `SEVERITY` lines; every function named in remediation-c9's F2 table
(`check-instruction-paths.py:scope/violations`, `inflight_registry.py:main`,
`test-check-instruction-paths.py:main`, `test-anchor-directions.py:main`,
`test-inflight-registry.py:main`) was split into smaller helpers and now grades 3-5, all passing bar.

One real, non-blocking gap carried forward and one new one found:

- **New (MED, non-blocking):** T-09's own intent was amended in this remediation window
  (`plan.yaml` diff in `7a6185a4`) to add a fifth required case — "AMBIGUITY REFUSED: two ambiguous
  matching worktrees cause exit 2 with stderr naming the candidates" — to `test-dispatch-guard.py`'s
  `case_17`. It was never written: `grep -i ambiguous .../test-dispatch-guard.py` = 0 hits, and I
  read `case_17_shell_less_persona_requires_matching_feature_root` in full (lines 461-497) — it has
  five sub-checks (REFUSED / ALLOWED / bash-discrimination / MISMATCH REFUSED x2), no ambiguity case.
  T-09 is `status: done`. The dispatch-guard.sh code itself is correct on inspection (verified
  except-clause ordering, message content, and that the comparison branch lives in the `else` of a
  `try/except/else` so it never runs on a swallowed exception) — this is a coverage gap, not a live
  defect, and not part of the signed BRIEF's SC-13 (whose four named cases are all present and
  passing). Not `must_fix`: the practical failure surface is closed at its source, because the
  orchestrator's own emit path (`inflight_registry.py feature-root`, SC-14) already refuses loudly
  (exit 1, no stdout) on ambiguity, so a malformed dispatch built from that refusal never reaches
  dispatch-guard.sh with a bogus root — it reaches it with `HARNESS-FEATURE-TREE-ROOT` simply
  absent, which the tested REFUSED case already catches. Still, the gate's own new branch has no
  test holding it against a future edit; recommend closing before the next remediation cycle rather
  than folding into a routine follow-up. (Aside: T-09's intent header still says "FOUR NEW CASES"
  while listing five bullets after the amendment — a leftover of the same edit, harmless but worth
  fixing alongside.)
- **Carried (MED, non-blocking, unaddressed since remediation-c9's F3):** SC-12's RED case
  (`test-inject-expertise.py:239 case4d`) still asserts only the `HARNESS_PATH_DRIFT: 1 unanchored
  path(s)` count line, never the `<file>:<line>` detail line
  (`inject-expertise.sh`'s `sed -n 's/^VIOLATION \([^:]*:[0-9]*\):.*/  \1/p'` output) that SC-12
  also names. Confirmed unchanged: this diff touches no lines in `test-inject-expertise.py` at all
  (absent from the 8-file `git diff --stat ff4ca877..49df4bee`). Not re-escalating past MED — same
  reasoning as remediation-c9: the extraction is traced correct by hand, only the regression-catch
  is missing.

## Re-verified from remediation-c9's own scope

- SC-04, SC-05, SC-07, SC-09, SC-10 (literal CLI text), SC-11, SC-14, SC-15 were MET at
  remediation-c9 and untouched by this diff's file set (`git diff --stat` above) except where noted;
  re-confirmed live: `test-check-instruction-paths.py` (15/15), `test-anchor-directions.py` (7/7,
  including the reviewed-sha whole-scope row), `test-inject-expertise.py` (21/21),
  `test-inflight-registry.py` (125/125), `test-dispatch-guard.py` (48/48) all pass at the pin.
- SC-07 (no widened write permission): `.harness/team-config.yaml` absent from
  `git diff --stat 06bd60c8..49df4bee` entirely (zero-line diff, unchanged). The sixteen
  `.omp/agents/*.md` diffs land at lines 30-42 and 88-106 in the three shell-less lead files —
  confirmed by hunk headers — nowhere near each file's `tools:` frontmatter block at lines 3-8.
- `feature_root()` (`inflight_registry.py:265-271`) — the shared Python function used by
  `reconcile` and by `validate-digest.py`'s three call sites — is **byte-identical** to before
  remediation-c9 and still swallows `AmbiguousWorktree` behind `except Exception: return
  owner_root`. This is correct and required, not a regression: FEAT-50's own committed assertion
  (`plan.yaml:1201`, `assert ir.feature_root(d, 'FEAT-X-thing') == d, 'ambiguity must fall back to
  owner_root'`) pins that exact fallback for its own consumers. The remediation fixed the two
  call sites that matter for FEAT-52's write-anchor guarantee (dispatch-guard.sh's own comparison,
  and the CLI verb `inflight_registry.py feature-root` the orchestrator's emit duty runs) by
  calling `harness_boundary.worktree_for_feature` directly instead of routing through
  `feature_root()`, rather than changing the shared function's contract — the correct-direction fix
  per this codebase's own "propagate `AmbiguousWorktree` to the caller, don't convert it" framing
  (plan.yaml:756-758, pre- and post-amendment).

## Verdict

**PASS.** `must_fix = []`, `severity_max = med`. Both findings above are advisory: real, worth a
follow-up commit, neither reproduces a live defect nor violates a signed BRIEF success criterion.
Recommend a small follow-up task (not blocking ship) that adds the AMBIGUITY REFUSED case to
`test-dispatch-guard.py::case_17` and the `<file>:<line>` assertion to
`test-inject-expertise.py::case4d`, together with fixing T-09's stale "FOUR NEW CASES" header.
