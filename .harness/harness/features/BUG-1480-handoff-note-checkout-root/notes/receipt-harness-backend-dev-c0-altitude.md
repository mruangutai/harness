# ALTITUDE angle — BUG-1480 (c0)

**BLUF:** The T-02 fix sits at the right layer and its test proves behaviour, not mechanism —
both `leave`. But the same defect class the BRIEF names (a worktree-relative `rel` joined against
the MAIN `root` and handed to a filesystem-walking consumer) is already present, unfixed, and
self-documented as an accepted residual one branch away, in the `RE_FEATURE_JSON` schema-lookup at
`check-domain.sh:1472-1474` — one live adjacent finding, `briefing-row`, `defer` per DEC-174.
**ZERO edits applied — DEC-174 suspends the apply step for this whole feature; every finding below
is recorded with disposition `defer` regardless of severity.**

## Q1 — Is the fix at the right layer?

`_checkout_root` (check-domain.sh:1151-1162) is a thin, same-layer sibling of `_norm`
(check-domain.sh:1114-1149) that re-exposes the checkout-root half of
`harness_boundary.checkout_relative`'s pair — the half `_norm` already computes and discards
(BRIEF `## Problem`). It is consumed at exactly one call site, `check-domain.sh:1761-1762`.

Pushing the answer DOWN into `harness_boundary` is not warranted: the entry point already exists
there (`checkout_relative`, harness_boundary.py:115-148) — nothing new needs to be added to that
module, only exposed one layer up. Pushing it UP into `handoff_done_when` (having `problems()`
resolve its own root from the note's absolute path) would mean threading an `absolute_path`
parameter through `handoff_done_when.problems` → `_resolve_all` (handoff_done_when.py:359-361) →
`_read_target`/`_feature_dir` (handoff_done_when.py:51-54, 78-79) — a second file's public contract
widened for one caller's need, when that module already takes an explicit `root` argument, i.e. it
already delegates "which root" to its caller. `check-domain.sh` supplying the correct root at its
own call site is the caller doing exactly the job that contract assigns it.

D-03's constraint (`_norm`'s string contract must not change; 15 call sites, see the REUSE receipt's
recount) rules out the alternative of widening `_norm` itself, which is the only layer move that
would have been actually cheaper than the sibling-helper shape. Verdict: right layer. **leave.**

## Q2 — Problem or symptom?

BRIEF `## Problem` names the general defect precisely: "`_norm`... discards `_ck[0]`" and "every
consumer that needs it must re-derive it" is the shape of the risk, even though the BRIEF's own
prose is scoped to the one handoff call site. T-02's fix resolves the ONE call site the BRIEF and
D-01/D-03 scope to (correctly — D-01 requires a standalone, minimal-scope PR). But the general
defect — a worktree-relative `rel` (from `_norm`, checkout-stripped per `checkout_relative`'s
contract) joined against the always-MAIN `root` and handed to a consumer that reads the
filesystem — is not unique to the handoff branch. See Q4: it is present, live, and already
self-documented as an accepted residual in the `RE_FEATURE_JSON` branch a few hundred lines away.
So: this fix patches the symptom at the one site the plan scoped to (correct, given D-01), while the
general defect the BRIEF describes survives untouched elsewhere in the same file. Evidenced, not
vibes — see Q4's file:line. This is not a criticism of T-02's scope; it is the literal answer to
"problem or symptom" against the general framing the BRIEF itself uses.

## Q3 — Does the test group prove behaviour or mechanism?

Read `_handoff_worktree_cases` (test-check-domain.py:4401-4440, diff hunk `@@ -4398,6 +4398,47 @@`).
All three assertion rows go through `_invoke_handoff(root, target, content)`, which drives the real
hook as a subprocess (crosses the interface) and asserts only on the process's exit code and, for
the refusal rows, case-insensitive substring needles against stderr (`_record_handoff_result`,
test-check-domain.py:4132-4137). No row references `_checkout_root` by name, imports
`check-domain.sh` internals, or asserts an implementation detail. The needle for the third row is
explicitly the checkout-relative trailing fragment, not the absolute worktree path, and the T-01
intent (plan.yaml:149-157) records why in the same terms this angle cares about: an absolute-path
needle would break under `checkout_relative`'s realpath normalisation, i.e. the test was written
*not* to couple to one resolution mechanism.

Would every row stay green under the Q1 alternative (root resolved inside `handoff_done_when`
instead of at the call site)? Yes — the observable contract (exit code + stderr substring) is
identical either way; the test exercises "does a worktree-only note's pointer resolve", not "does
`_checkout_root` get called". That is a point in the tests' favour, stated plainly. **leave.**

## Q4 — Adjacent breakage the same root cause leaves open

Grepped every `os.path.join(root, ...)` in check-domain.sh (7 non-comment hits) and every consumer
of `_norm`/`_resolved_rel`/`_hardlink_plan` output. Traced each for "does it join a possibly
worktree-relative rel against the MAIN root and hand the result to something that touches disk":

- `_resolved_rel` (check-domain.sh:1866-1893) and the plan-checker's `_cands` (check-domain.sh:
  248-252): both compute a STRING used only for pattern matching (`RE_PLAN_YAML.match`, domain-name
  matching) — never opened, never joined again for I/O. No defect.
- `_hardlink_plan` (check-domain.sh:1896-1921): globs `root/.harness/*/features/*/plan.yaml` and
  compares inode identity to the RAW `path` (via `os.stat(_claimed_abs(path))`, not a rel+root
  join). It scans only the main checkout's plans, so a hardlink whose true `plan.yaml` lives only in
  a worktree cannot be discovered — a real gap in kind, but not the rel/root MISMATCH pattern Q4
  asks for (it never joins a worktree-relative string against the main root); noting it, not
  flagging it as this pass's finding.
- `feature_checkout_guard` (check-domain.sh:737-763): compares `checkout_relative(target_path)[0]`
  against `worktree_for_feature(...)` directly — checkout identity, never a rel+root join. No
  defect.

- **`check-domain.sh:1472-1474` — a live instance of the exact defect class, unfixed.**
  `feature_schema.problems_for_text(content, display or rel, for_path=os.path.join(root, rel) if
  root else rel)` inside the `RE_FEATURE_JSON` branch of `shape_problems` (check-domain.sh:
  1398-1523). `rel` here is the SAME `_norm`-derived, checkout-STRIPPED string the handoff branch
  used pre-fix (confirmed by tracing every `shape_problems` call site — check-domain.sh:2058, 2087,
  2092, 2103-2104, 2232 — `rel` is always `_norm(target)` or an equally checkout-relative
  `_resolved_rel`/`_hardlink_plan` result; `checkout_relative` itself, harness_boundary.py:115-148,
  returns the relpath AGAINST THE CHECKOUT, never carrying the worktree segment). The adjacent
  comment (check-domain.sh:1459-1462) asserts the opposite — "`rel` already carries the worktree
  prefix... so joining it with `root` gives the real absolute path" — which is not what `_norm`'s
  code does. `feature_schema.problems_for_text` walks UP from `for_path` to find the nearest
  `feature-schema.json`; for a feature living only in a worktree, `os.path.join(root, rel)` builds a
  path rooted in the wrong tree, so the walk finds the MAIN checkout's schema (or the module
  default), never the worktree's own. The comment's own "Measured live 2026-08-23" paragraph
  (check-domain.sh:1464-1468) reports exactly this symptom — a schema key declared only in the
  worktree's `feature-schema.json` was not honoured — and frames it as an accepted residual ("a
  feature that ADDS a schema key could not write data using it until it merged") rather than a bug,
  but it is the identical rel/root mismatch this feature exists to fix, one branch away.
  - **concrete cost:** every `feature.json` write for a feature planned only in an unmerged worktree
    is schema-checked against the wrong checkout's `feature-schema.json` — silently passing a write
    the worktree's own (newer) schema would refuse, or refusing one the worktree's schema would
    accept.
  - **one-line remedy:** reuse this diff's own `_checkout_root(absolute_path)` in place of `root` at
    line 1474 — `for_path=os.path.join(_checkout_root(absolute_path), rel) if absolute_path else
    rel` — the exact helper this feature already built, applied to a second call site.
  - **severity:** med — real, silent, and matches BRIEF's failure shape (a defect DEC-159/schema
    validation cannot see across a worktree boundary), but bounded to feature.json schema checks and
    already partially mitigated by the module-default fallback, not a full failure to validate.
  - **disposition: defer** (DEC-174: `.claude/skills/harness/bin/**` is enforcement-layer, this
    pass's apply is suspended for the whole feature; this finding is also out of BUG-1480's signed
    scope — D-01 pins this PR to the ONE handoff defect, and RE_FEATURE_JSON is a different branch,
    a different bug). **briefing-row.**

No other consumer in check-domain.sh joins a worktree-relative rel against the main root for
filesystem access. **One finding.**

## Settled, not re-litigated

D-01 (standalone PR), D-02, the mandatory `try/except Exception` + fallback-to-`root` shape, the
trailing-fragment needle, the vacuity-control row's green-both-ways behaviour — none flagged. The
prior three angles' receipts (`receipt-harness-backend-dev-c0-{reuse,simplification}.md`,
`receipt-harness-dev-ops-c0-efficiency.md`) were read and are not duplicated here.
