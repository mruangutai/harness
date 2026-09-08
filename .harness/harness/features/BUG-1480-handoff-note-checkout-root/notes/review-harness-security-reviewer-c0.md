# Security review — BUG-1480-handoff-note-checkout-root — review_sha 4de92e75

**Verdict: no must_fix. severity_max = info.** The new `_checkout_root` helper does not widen
what any caller can write; it only changes which checkout's `plan.yaml`/`BRIEF.md` a handoff
note's `Authority:` pointer is validated against, and it is only reachable, for governed
(agent) writes, on paths `domain_check()` has already placed inside a checkout the calling
agent is legitimately bound to. One low-severity residual noted, not gating.

## Census (both files read in full at 4de92e75)

- `.claude/skills/harness/bin/check-domain.sh` — `_checkout_root` (new, after `_norm`,
  measured at this sha immediately following `_norm`'s closing `return rel`) and its one
  call site inside `shape_problems`'s `RE_HANDOFF` branch (measured: the
  `handoff_done_when.problems(...)` call, ~30 lines below `_checkout_root`'s definition).
- `tests/integration/test-check-domain.py` — `_handoff_worktree_cases` (new) and its call
  from `run_handoff_done_when`.
- `.claude/skills/harness/bin/harness_boundary.py` — read for `checkout_relative`,
  `worktree_owner`, `real`, `classify` (unchanged by this diff, but load-bearing for every
  answer below).
- `.claude/skills/harness/bin/handoff_done_when.py` — read for `problems`, `_read_target`,
  `_resolve_*`, `_satisfied_*` (unchanged by this diff).

## 1. Boundary widening

`_checkout_root(absolute_path)` calls `harness_boundary.checkout_relative`, which itself
calls `worktree_owner` and **discards** the `legitimate` flag (`checkout_relative` at
`harness_boundary.py:145`: `checkout_dir, owner_root, _legitimate = owner` — underscored,
unused). In isolation that makes `_checkout_root` willing to hand back the checkout of ANY
`.git` pointer it can walk up to, legitimate placement or not.

That isolation doesn't hold at the only call site that matters. `_checkout_root` is invoked
from inside `shape_problems`, which runs strictly **after** `domain_check()`
(`check-domain.sh:1002-1003`, `if _run_domain and not _no_parser: domain_check()`, ahead of
"THE SHAPE PHASE" comment at `check-domain.sh:1005`). For a governed agent
(`_domain_phase = _governed and not _post`, `check-domain.sh:328`), `domain_check()` calls
`harness_boundary.classify(...)` and hard-refuses (`sys.exit(2)`) an `out_of_place_worktree`
(worktree not under `WORKTREES_SEGMENT`, `check-domain.sh:921-937`) or a `wrong_checkout`
(same repo, different checkout than the session's own, `check-domain.sh:939-949`) verdict
*before* `shape_problems` ever runs. On the `allow`/`shared` outcomes it additionally calls
`claim_checkout_guard(_claimed_abs(target))` (`check-domain.sh:966-967, 972-973`), which binds
the destination to the agent's own live worktree claims (`claim_checkout_guard` at
`check-domain.sh:770`, backed by `harness_boundary.claim_worktrees`). So by the time
`_checkout_root` runs for a governed write, `absolute_path` has already been proven to sit
inside either the main checkout or a legitimately-placed worktree the calling agent is bound
to — the same set `checkout_relative`'s legitimacy check would have produced, just enforced
one layer up. A governed agent cannot steer `_checkout_root` to a checkout it isn't already
authorized to write into, because it can't reach `shape_problems` with such a path at all.

For the **main session** (`_run_domain` false, `domain_check()` skipped entirely), no new
exposure either: the main session is exempt from domain gating by design
(`harness_boundary.py:562-565`, "The main session is exempt BY THE MECHANISM") and is already
fully trusted with the whole tree.

Net: what changes is *which* `plan.yaml`/`BRIEF.md` a note's `Authority:` pointer resolves
against (the worktree's own copy instead of the main checkout's), never *whether* the write
itself is authorized. That's REQ-01/REQ-02's stated intent and the whole point of BUG-1480.

## 2. Containment (split-root / TOCTOU shape)

`_checkout_root(absolute_path)` is computed exactly **once** per `shape_problems` call and
threaded through as the single `root` argument of the diff's one call site
(`check-domain.sh`, `handoff_done_when.problems(rel, content, _checkout_root(absolute_path),
resolve=True)`). Inside `handoff_done_when.py`, that one value flows unchanged through
`_resolve_all` → `_feature_dir(rel_path, root)` (`handoff_done_when.py:53-55`) and every
`_resolve_plan`/`_resolve_brief`/`_resolve_finding`/`_resolve_approval`/`_satisfied_plan`/
`_satisfied_approval` call (`handoff_done_when.py:117-267`), all of which pass the same
`root` into `_read_target(target, root)` (`handoff_done_when.py:78-87`), whose
`resolved.relative_to(root)` containment check (`handoff_done_when.py:85`) is compared
against that identical value. There is no second, independent re-derivation anywhere in this
call chain — the containment decision and every read it gates use the same resolved root.
No split-root inconsistency.

(`rel_path`/`rel` also derive from the identical `_claimed_abs(target)` input as
`absolute_path` — `_norm` at `check-domain.sh:1141,1144` and `_checkout_root` at
`check-domain.sh` both call `_hb.checkout_relative(_claimed_abs(path))` on the same absolute
path — so `rel` and the chosen `root` can't describe two different files either.)

## 3. Fail-open direction (REQ-03)

`_checkout_root`'s `except Exception: pass` falls back to `root` (the session/main root).
Grading the direction:

- **The common failure mode is safe.** `_checkout_root`'s try body is structurally identical
  to `_norm`'s (`check-domain.sh`, both: `_hb.checkout_relative(_claimed_abs(path))`, then
  compare `_hb.real(_ck[0]) != _hb.real(root)`), called on the *same* absolute path, moments
  apart, within one synchronous hook invocation. `_norm(target)` already ran earlier to
  produce `rel` (`targets = [(_norm(target), ...)]`), and `rel` must match `RE_HANDOFF`
  (`^\.harness/[^/]+/features/[^/]+/notes/handoff-...\.md$`, `check-domain.sh:1189-1190`,
  worktree-prefix already stripped) for this code path to run at all. If `_norm`'s identical
  computation had failed or returned a not-actually-stripped path, `rel` would carry the
  worktree prefix and never match `RE_HANDOFF`, so `_checkout_root` is simply never called.
  So the only way `_checkout_root` throws where `_norm` didn't is a filesystem change to the
  `.git`/worktree pointer files *between* the two calls — a narrow TOCTOU window, not an
  attacker-steerable input.
- **When it does trip, the fallback is usually MORE restrictive, matching the bug this
  feature fixes**: falling back to the main root means `_feature_dir` looks for
  `plan.yaml`/`BRIEF.md` under the main checkout, which for a feature that only exists in the
  worktree raises `ValueError` in `_read_target` (file doesn't resolve) → `_resolve_plan`/
  `_resolve_brief` reports an unresolved-pointer problem → the note is refused. That's a
  false refusal (the original bug), never a false pass.
- **Narrow low-severity residual**: if the main checkout *also* independently carries a
  `.harness/.../features/<feat>/plan.yaml` (or `BRIEF.md`) at the identical relative path,
  with content that diverges from the worktree's own copy — e.g. a stale pre-worktree
  version — then falling back to `root` on the rare TOCTOU trip could validate an
  `Authority:` pointer against that stale main-tree file instead of the worktree's current
  one, which is not guaranteed to be strictly more restrictive. This requires both the rare
  race window from the point above *and* independent plan/brief content drift between two
  checkouts of the same feature — I did not find a way for the write's own author to
  manufacture the favorable half of that (raw `Write`/`Edit` to `plan.yaml` is refused by a
  separate, pre-existing route check, `_plan_route`/`_reached_plan`,
  `check-domain.sh:1913-1928`). Rating **low**, recorded rather than gating (P-17/O-04:
  irreversibility here is bounded — a false-pass only lets a handoff note *claim* an
  authority pointer resolves; it doesn't itself authorize any write).

## 4. Test filesystem footprint

`_handoff_worktree_cases` (`tests/integration/test-check-domain.py`) runs entirely inside
`run_handoff_done_when`'s `with tempfile.TemporaryDirectory() as root:` block
(`test-check-domain.py:4453` down to `_handoff_worktree_cases(results, root)` at the end of
that block). `make_linked_worktree(root, wt_path, wt_id)`
(`test-check-domain.py:138-157`) writes both pointer-pair halves — `wt_path/.git` and
`root/.git/worktrees/<id>/gitdir` — and both destinations are joined from the `root`/`wt_path`
arguments the caller supplies, which in this test are both under the `TemporaryDirectory`.
`fire()`/`_invoke_handoff` shell out to the hook with `env=_env(root)`
(`test-check-domain.py:159-161`), which scopes `HARNESS_PROJECT_DIR` to the same temp root.
No write lands outside the temp directory.

## Threat model

| boundary | STRIDE | mitigated | note |
|---|---|---|---|
| governed-agent write target vs. domain grant | Elevation of privilege | true | `domain_check()`/`classify()` gate runs before `shape_problems`; `_checkout_root` is unreachable outside an already-authorized, already-claim-bound checkout |
| handoff-note Authority-pointer resolution root | Tampering | true | single `root` value threaded through the whole `handoff_done_when` call chain; no split-root read |
| `_checkout_root` exception fallback direction | Tampering | low/precondition-absent | fails toward the main root, which is normally *more* restrictive; a stale-main-tree-content scenario could flip that, but reaching the fallback at all needs a same-invocation TOCTOU that `_norm`'s identical prior call already forecloses in the common case |
| test fixture worktree writes | n/a (test-only) | true | confirmed confined to `TemporaryDirectory` |

## Known non-gating residuals (not re-derived, per briefing)

- `RE_FEATURE_JSON` schema lookup (near old check-domain.sh line ~1472) has a pre-existing,
  out-of-diff rel/root mismatch — not this diff's defect.
- REQ-06's containment narrowing has no executable test row; graded by SC-07 inspection only.

```yaml
VERDICT: PASS
DIGEST:
  headline: "_checkout_root only re-scopes handoff-note content validation to an already-authorized checkout; no write-authorization widening, no split-root containment gap, fail-open direction is safe in the reachable case with one low, non-blocking residual."
  in_scope: true
  scope_reason: "Diff changes the trust root a PreToolUse write-authorization-adjacent gate (check-domain.sh) uses to validate handoff-note Authority: pointers — squarely a boundary-widening question even without network/secret/user-input surface."
  severity_max: low
  findings: 1
  must_fix: []
  threat_model:
    - { boundary: "governed-agent write target vs. domain grant", stride: "E", mitigated: true }
    - { boundary: "handoff-note Authority-pointer resolution root", stride: "T", mitigated: true }
    - { boundary: "_checkout_root exception fallback direction", stride: "T", mitigated: false }
    - { boundary: "test fixture worktree writes", stride: "n/a", mitigated: true }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1480-handoff-note-checkout-root/.harness/harness/features/BUG-1480-handoff-note-checkout-root/notes/review-harness-security-reviewer-c0.md
```
