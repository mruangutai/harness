# Security plan review — FEAT-22 docs-layout-migration — S-03 planpanel

Pin: `0f12f14` (confirmed `git rev-parse HEAD` == plan.yaml's `lanes.resolved_at`). Read-only; no source
touched. All four checks measured against the live tree, not inferred from the plan's prose.

## CHECK 1 — D-01's wildcard grant

Measured with `harness_boundary.matches()` directly against pattern `.harness/*/docs/**`:

| probe | matches |
|---|---|
| `.harness/harness/docs/SPEC.md` (intended) | True |
| `.harness/expertise/docs/x.md` | **True** |
| `.harness/logs/docs/x.md` | **True** |
| `.harness/notes/docs/x.md` | **True** |
| `.harness/factory/docs/fleet-notes.md` | **True** |
| `.harness/expertise/harness-documentor.md` (a real grant/Expertise file) | False |
| `.harness/team-config.yaml` | False |
| `.harness/harness/features/FEAT-1/docs/x.md` | False |
| `.harness/docs/x.md` (no middle segment) | False |

`*` is confirmed single-segment (`glob_to_re`: `*` → `[^/]*`, never crosses `/`; `**` → `.*`, crosses).
So the grant reaches `.harness/<any-one-segment>/docs/**` for whatever segment exists — not only
`harness`. At 0f12f14 the segments under `.harness/` are `harness, logs, notes, expertise, factory`
(measured via `ls -la .harness/`). None of them currently holds a `docs/` subdirectory except the
migration destination, so **today this is dormant** — but it is a real latent grant: were anyone to
later create `.harness/factory/docs/` or `.harness/expertise/docs/`, harness-documentor gains write
there with no further decision, purely as a side effect of this plan's pattern choice.

It does **not** reach `.harness/team-config.yaml`, any grant file, gate script, Expertise file, or
feature state — those aren't nested under a `<segment>/docs/` shape, so 1(b)'s specific worry (grants,
gates, expertise, feature state) is measured clear.

1(c) symmetry claim — verified TRUE, not merely asserted. `.harness/*/features/**` is not a one-off:
FEAT-21's plan.yaml (`:115-123`) documents it as an intentional multi-repository-segment mechanism
("Grants, globs and regexes take a WILDCARD repository segment… never a hardcoded harness segment…
team-config.yaml is one global file (issue 346), so a hardcoded segment grows a line per repository").
`check-domain.sh`/`check-plan-routes.py`/`check-state.sh` all anchor that segment with `[^/]+`
(single-segment, matching `matches()`'s behavior) — so the docs grant inherits an *already-signed*
risk shape rather than introducing a new one. The precedent carries no narrowing D-01 omits.

1(d) — measured directly: `check-domain.sh --resolve docs/harness/SPEC.md` (pre-move, live tree)
returns exactly `harness-documentor`, and the destination pre-move returns `NOBODY` — confirming no
other role currently resolves for the docs surface, so nothing is orphaned by the move, and T-02's
intent explicitly retains the existing `docs/**` entry.

**Finding (low, not must_fix):** the wildcard grant is a real, measured widening of reach beyond the
literal `.harness/harness/docs/**`, to any future `<segment>/docs/**` under `.harness/`. It is
currently inert (no such directory exists) and is the same accepted shape as FEAT-21's features grant,
so it is not a new class of risk this plan introduces — but it's worth a one-line acknowledgment in the
plan or in `HARNESS_CONTROL_PLANE`'s comment (which already documents an analogous "closed list,
accepted risk" tradeoff at `harness_boundary.py:84-88`) rather than left silent.

## CHECK 2 — D-02's redundancy claim

Verified line-by-line against `harness_boundary.py`:
- `is_control_plane_target` (`:217-229`): `is_control_plane_glob(rel)` is checked FIRST and returns
  True for any `rel` whose first segment is `.harness` — which `.harness/harness/docs/...` always is,
  post-move, independent of `HARNESS_CONTROL_PLANE`'s contents. Confirmed.
- `classify`'s deny-advertise filter (`:339-344`): `is_control_plane_glob(g)` alone already admits any
  glob starting with `.harness`/`.claude` before the `HARNESS_CONTROL_PLANE`-driven `any(...)` clause
  is even needed. Confirmed.

Consumer completeness — grepped the full repo (`.py`/`.sh`) for `HARNESS_CONTROL_PLANE`: exactly two
executable consumers exist, `harness_boundary.py:229` and `:343`. The only other hits are
`layout_fixtures.py:54-55` (a string-literal fixture for the *detector*, not a runtime consumer) and
`layout_migration.py:38` (a docstring reference). **The amendment's "two consumers, redundant in both"
claim is accurate and complete** — no third consumer exists that the amendment would misstate.

Necessity check: `layout_migration.py:99-101`'s migrated-row regex for `harness_boundary.py` is
`\.harness/[^/"]+/docs/\*\*`, i.e. it requires that literal shape to appear *somewhere* in the file. If
the entry were deleted outright the file would match neither the legacy nor migrated form and go
CANNOT_VERIFY — confirming D-02's stated reason for keeping it is real, not decorative.

No finding. This is a verified-true claim in a document the operator will sign (DEC-189 amendment).

Also verified the benign-side-effect clause (T-08, plan.yaml :943-944): "docs/** was advertised partly
via the old entry and is still advertised via docs/PRINCIPLES.md, so the deny message loses nothing."
Measured directly: `matches('docs/PRINCIPLES.md','docs/**')` = True (still advertised),
`matches('docs/harness','docs/**')` = True (was advertised via the old entry too, pre-existing),
`matches('.harness/*/docs','docs/**')` = False (not advertised via the migrated spelling). All three
match the amendment's claim — it is TRUE as written, so this clause is also safe for the operator to
sign.

## CHECK 3 — the symlink-escape example at :111

3(a) Climb arithmetic, counted from repo root:
- Old: `docs/harness/<link>/agents/x.md` — link's containing dir is `docs/harness/` (2 segments). From
  there `../../` = 2 climbs reaches root, `+.claude` lands in `.claude/`. Two-deep, two climbs — matches
  the plan's claim.
- New: `.harness/harness/docs/<link>/agents/x.md` — containing dir `.harness/harness/docs/` (3
  segments). `../../../` = 3 climbs reaches root. Three-deep, three climbs — matches the plan's claim.
  Both directions verified correct.

3(b) — **this is documentation only; nothing executable depends on the climb count.** Read the actual
fixture at `test-check-domain.py:801-826` (pre-move, current pin): it builds the escape via
`os.symlink(os.path.join(esc_root, ".claude"), os.path.join(esc_root, "docs", "harness", "esc"))` — an
**absolute** symlink target, not a relative `../../`-style chain. The prose at `harness_boundary.py:111`
is an illustrative relative-path example; the real test fixture encodes no climb count at all and is
therefore depth-agnostic. Moving the fixture to `.harness/harness/docs/esc` (T-05) cannot desynchronize
from the doc example because there is no shared numeric dependency to desynchronize — confirmed by
reading the fixture, not assumed. The escape still functions post-move for the reason in 3(c).

3(c) — `classify()` calls `_abs_target = real(abs_target)` (`os.path.realpath`) as its very first step,
**before** `select_base` and before any glob match. Resolution happens once, up front, against the
fully-resolved real target — this is depth-independent and link-style-independent (relative or
absolute). The move from a 2-segment to a 3-segment base changes nothing about *when* or *how*
symlinks are resolved; realpath handles either uniformly. `check-domain.sh`/`bash-write-guard.sh` both
call the same shared `classify()` (grepped: both import `harness_boundary` and call `.classify(`), so
this holds for both PreToolUse routes, not just one.

No finding — assessed and dismissed. Recording this so a later reviewer doesn't re-raise it: the
climb-count rewrite is prose-only, the actual control (`real()` before matching) is unaffected by the
migration's added directory segment.

## CHECK 4 — mid-cluster exposure

Between T-02 (grant + physical move) and T-03 (list rewrite), does the guard grant *more* than
intended? Traced through `is_control_plane_target`: because it short-circuits on
`is_control_plane_glob(rel)` — true for any `.harness`-prefixed target — `.harness/harness/docs/**`
is already recognized as a control-plane target **the instant T-02's grant and move land**, independent
of `HARNESS_CONTROL_PLANE`'s (still-stale) list contents. So there is no window where the guard is
*weaker* than the final intended state; if anything T-03 only closes a cosmetic/detector-satisfaction
gap (Check 2), not a functional one. This directly follows from Check 2's finding — the combination
(D-01 grant timing × D-02 redundancy) closes cleanly rather than opening a gap, worth recording since
neither task's own scope states it explicitly (P-10 in this role's Expertise).

The other direction (a path remaining writable that should not be) is the pre-move status quo,
unchanged: between T-02 and T-03, `docs/harness/**` stays listed in `HARNESS_CONTROL_PLANE` (stale,
not yet rewritten) and stays reachable via harness-documentor's retained `docs/**` grant — exactly
today's behavior, both endpoints already signed, nothing new opened by the half-applied state.

Concurrent-agent exposure: D-03 dispatches no squad for this feature, so no team agent process is
spawned during the window. Checked for a genuinely concurrent *other* feature: `git worktree list`
shows only the main checkout registered (no other worktrees active at review time), and the harness's
own convention (`.claude/worktrees/<id>/`, README.md's "a dirty tree deadlocks the next run") isolates
concurrently-running features' team members into their own worktree checkouts, which read their own
copy of `team-config.yaml` off their own filesystem, not the main checkout's live in-progress edits.
The main session itself is exempt from the write guard entirely (`team-config.yaml:15`: no
`agent_type` → `check-domain` exits 0), which is what lets D-03's plan work as `main-session-direct` at
all. I could not fully rule out a *hypothetical* second main-session-direct flow running concurrently
on the same non-worktree checkout — this residual is **precondition-absent** (no such second flow
exists at review time, and the single-operator model makes it unlikely), not an active gap. Flagging
per G-11 rather than treating it as unmitigated.

## Scope fences respected

Did not re-litigate Q6/Q7/Q8, issue #369, the two-segment fixture row, FEAT-21's filed set, r7's
signature, Q2, or MF-4. Did not touch the 35-file survivor partition or the detector's migrated regexes
(code-reviewer's lane) or the test-suite class sweep (qa's lane) beyond what was needed to verify the
symlink fixture's actual mechanism in Check 3.

## Verdict

No must-fix. The DEC-189 amendment text (D-02/T-08) is verified TRUE and complete against source — the
operator can sign it as accurate. The wildcard grant (Check 1) is a real, measured, currently-dormant
widening consistent with an already-accepted design pattern (FEAT-21) — recorded as a low finding, not
blocking. The symlink-escape rewrite (Check 3) is prose-only and does not touch the actual control
mechanism. The mid-cluster window (Check 4) does not widen effective write access at any point,
verified by tracing the short-circuit that makes T-03's edit non-functional (redundant) from the moment
T-02 lands.
