# Code-reviewer re-review — FEAT-21, pinned `4a98cc4` — 2026-08-15

**PASS. must_fix: none. The must-fix delivery (D-08's label half) is proven correct and complete
for the traded pattern; both `/simplify` refactors (`gh-sync.py` walk-up, `test-layout-migration.py`
case 20) are semantically equivalent to what they replaced; the one comment-only change in
`check-state.sh` is accurate; all four prior advisories are unchanged or fixed, none regressed; the
skip list's four declines are all defensible.** Everything below is advisory, ranked, none blocking.

Ground-pin confirmed: `HEAD 4a98cc4`, branch `feat/FEAT-21-features-layout-migration` (not `main`).
`git log --oneline ea937b1..4a98cc4` → 10 commits: `d033b9d`, `5c39f8c`, `649b36b`, `3df7002`,
`b1d3925`, `835692a`, `1f717da`, `b517049`, `1c95e81`, `4a98cc4`. None carries a `[harness:human]`
tag — `human_commits_in_scope: []`. Source-bearing set is `d033b9d` + `b1d3925` + `4a98cc4`; the
other seven are orchestrator close-out/bookkeeping, all `.harness/harness/features/FEAT-21*` scoped.

**Dispatch correction, load-bearing:** the "case 20 lifecycle" refactor in `4a98cc4` is in
`.claude/skills/harness/bin/test-layout-migration.py`, not `test-check-plan-routes.py`. Both files
have a case named "20" — `test-check-plan-routes.py`'s `case_20` (source-text scan for root-probe
consistency) was untouched by `4a98cc4` and irrelevant to job B. Reviewed the right one
(`test-layout-migration.py`); flagging the mix-up since it's exactly how a lead could misverify.

## A — must-fix delivery (D-08's label half)

**17 `fpath()` call sites are the complete set for the traded pattern class.** Swept every
`bad.append`/`warn.append` in the file (grep, all lines) and diffed against the pre-migration
shape at `ea937b1`: every site that used to read `f"{feat}/FILE.ext ..."` (a bare-basename path
construction) is now `fpath(feat, 'FILE.ext')`; a repo-wide grep for the literal `{feat}/` or
`{_feat}/` pattern in the file at `4a98cc4` returns zero hits — none escaped conversion. No
feature-only label (the `"{feat}: ..."` colon-separated shape) was wrongly given a path. This
claim is safe for the exact pattern D-08 traded on.

**Residual, narrower gap — four bare-basename labels outside that pattern class, low/advisory,
not part of the signed trade.** `check-state.sh:126, 609, 619, 638` mention a filename in prose
(`"{feat} has STATE.md but no BRIEF.md"`, `"{feat}: ... notes/handoff-{prev}.md ..."` ×2, and
`f"{os.path.basename(fdir)}: has runs/ but no feature.json — ... instantiate it from
.../templates/feature.json"`) without ever qualifying the *directory* — a reader who wants to open
the named file still has to guess which of possibly several `.harness/<repo>/features/<feat>/`
trees it lives under. Line 638 is the sharpest instance: it discards the full `fdir` it is already
holding into `os.path.basename(fdir)` and then tells the operator to "instantiate" a file, without
saying where. None of these four existed in the traded-pattern's `{feat}/FILE` shape pre-migration
either (checked against `ea937b1`), so they are not a broken promise — D-08 never covered them —
but they're the same underlying ambiguity the fix exists to solve, just phrased differently.
Advisory: worth folding into the same `fpath()` treatment on a later pass; does not block this ship.

**`fpath`'s `?` fallback (`check-state.sh:59`) — unreachable on any tree the script can currently
discover, confirmed independently.** Every one of the script's 15 independent feature-discovery
globs uses the shape `.harness/*/features/*`, the same shape `_feat_dirs` is built from — so any
`feat` value the script ever binds already came from a directory `_feat_dirs` also matched. The
fallback fires only via direct/synthetic invocation (`fpath("NOT-REAL", ...)`), never through a
live code path today. This matches QA's independent finding
(`notes/review-harness-qa-2026-08-15-rereview.md` Job 1c) exactly. Info, not blocking, and correctly
scoped by QA into the existing B-1/B-3 "nothing stages a non-migrated tree" backlog framing rather
than as a new row — I agree and file it the same way, not as a new item.

**`_feat_dirs`'s dict-comprehension can silently pick one of two directories under a MIXED
layout** (same basename present at both a legacy and a migrated path simultaneously) — dict
overwrite order is glob-order-dependent, unspecified. Not a new row: `INV-27` already reports
MIXED as a blocking `bad` line before this matters in practice, so the operator is already told to
fix the tree; this is the *mechanism* behind why `B-1` ("nothing stages two repository segments")
matters, not a separate defect. Filed as a dismissal with reason, not a new finding (per my own
P-15) — folded into B-1, no new row.

## B — `/simplify` refactor semantic equivalence

**`gh-sync.py` walk-up flatten — equivalent, traced by hand and confirmed behaviorally.** Traced
every branch: the `while` condition `(not isfile(_d) and _d != dirname(_d))` reproduces the old
`while True: check; break-if-found; climb-or-break-at-root` loop exactly, including the terminal
case (`_d == dirname(_d)`, filesystem root) — the only difference is one redundant `isfile` re-check
after the loop exits, not a behavior change. Termination condition and fallback reachability are
both unchanged. QA's independent behavioral proof (three staged trees: legacy depth, migrated
depth, un-onboarded) confirms the same conclusion
(`review-harness-qa-2026-08-15-rereview.md` Job 3) — convergent, not just read-through.
Comment fix is accurate: the removed comment claimed the walk-up probes `.harness/harness.json`
while the code always probed `.harness/team-config.yaml`; the new comment names the real probe and
explains `harness.json` is read *after* root resolution, by `load_config`. Cross-checked against
`test-check-plan-routes.py:1098-1194` (`case_20`, a source-text sweep requiring every root-probe in
`bin/*.py`/`*.sh` to name `team-config.yaml`) — the claim that this case enforces the manifest
choice is true, and the suite passes (ran it: exit 0).

**`test-layout-migration.py` case 20 lifecycle — equivalent.** `_parity_tree` (mkdtemp +
try/finally shutil.rmtree(ignore_errors=True), returning a tuple unpacked by a separate
`_parity`) is now one `_parity` using `with tempfile.TemporaryDirectory()`, computing `gate`/`ci`/
`res` inside the `with` block and using them after it closes — safe, since these are plain
str/object values already computed while the dir existed, not open handles. Ran the suite: exit 0,
all "case 20 parity" assertions `ok`, including all five parity scenarios. One low/info
nit, not a finding: `TemporaryDirectory()`'s default cleanup does *not* swallow a removal error the
way `shutil.rmtree(..., ignore_errors=True)` did — a cleanup failure would now raise instead of
being silently ignored. No demonstrated failure scenario at HEAD (suite is green, including the
"unreadable" fixture case), and raising on cleanup failure is fail-loud, which this codebase
generally prefers over fail-silent. Not filing as a finding.

## C — `check-state.sh`'s comment-only change

Confirmed comment-only (`+1/-1` in the diff): `.harness/features/<FEAT>/...` →
`.harness/<repo>/features/<FEAT>/...`. Terminology (`<repo>` for the migrated segment) matches
existing usage elsewhere (`gh-sync.py:730`, `layout_migration.py:6`) — not invented for this
comment. States something true of the code beneath it: the glob it sits above is
`os.path.join(H, "*", "features", "*", "BRIEF.md")`, which literally is
`.harness/<repo>/features/<FEAT>/BRIEF.md`. Correct and complete.

## D — prior advisories, regression check only

1. **`branch-create-gate.sh:77-78`, hardcoded literal `harness` segment — changed, and the change
   is a real latent narrowing, but not news.** The literal moved from `.harness/features/${flow}*`
   (pre-migration: universally correct, since no per-repo segment existed yet) to
   `.harness/harness/features/${flow}*` (post-migration: correct only where the repo's own segment
   happens to be literally "harness"). Behaviorally identical on every tree stageable *today*
   (single segment; `B-1` confirms nothing currently stages a second one), so this is not a live
   break — but the underlying shift from a portable hardcode to a repo-specific one is real. This is
   already recorded, with the correct remedy, as `B-5` in
   `notes/ship-review-2026-08-15.md` ("It should derive it; a bare wildcard is wrong, because
   feature ids are coined per-BRIEF with no cross-repo uniqueness") — my independent read reaches
   the identical conclusion (derive the current repo's own segment from its own `harness.json`,
   neither wildcard nor hardcode). Confirmation of an already-tracked backlog row, not a new finding.
2. **`check-plan-routes.py`, no segment-level readability guard in `discover_plans()` — the gap was
   *created* in this exact range (`d033b9d`, T-04).** Pre-migration there was one directory level
   and it *was* guarded (`try: os.scandir(feats) except OSError: print + exit(2)`). Post-migration
   a new outer level was added (`seg_dirs = sorted(d for d in glob.glob(feats) if os.path.isdir(d))`)
   with no guard at that level — `os.path.isdir()` and `glob.glob()` both swallow `PermissionError`
   silently, so an unreadable segment directory just vanishes from `seg_dirs` with no diagnostic,
   while the per-feature guard one level down (unchanged) still fires correctly. Ruled `med,
   advisory` at the precommit round (`review-harness-code-reviewer-2026-08-14-precommit.md`
   Finding 2) and tracked as `B-4`. Unchanged by `4a98cc4` (not in its diff). Confirmed present,
   correctly still open, not silently dropped.
3. **`gh-sync.py`/`plan.yaml` — walk-up probes `team-config.yaml`, `plan.yaml`'s T-10 text still
   says `harness.json` — unchanged.** `plan.yaml` for FEAT-21 *was* touched in-range (`5c39f8c`,
   9 lines), but only a `status: building` → `status: done` flip plus path-migration edits
   elsewhere in the file; T-10's intent text (lines ~929-934, `"return the first ancestor holding
   .harness/harness.json"`) is untouched, verbatim. Tracked as `B-6` in the ship record ("the
   choice is right ... but no test discriminates, and it deserves a decision record") — still open,
   correctly not this polish pass's job to close.
4. **`.harness/expertise/harness-pm.md` legacy path — fixed, confirmed.** `git log -S` pins the fix
   to `d033b9d` exactly as claimed. Swept all of `.harness/expertise/*.md` for the literal
   `.harness/features/` pattern: zero hits — the fix wasn't a one-line patch that left siblings
   stale.

## E — the `/simplify` skip list

All four declines are defensible; I agree with all four, on evidence rather than deference:

1. **Branch-gate wildcard, skipped** — correct. Matches the reasoning in `B-5` and my own
   independent read of D-01: a bare wildcard here is a genuine false-grant (feature ids are
   per-BRIEF, not cross-repo-unique), so widening to `.harness/*/features/${flow}*` would let a
   same-numbered flow in a different segment validate a branch it doesn't back. The right fix is
   derivation, not wildcarding, and that's correctly deferred to its own change rather than folded
   into a polish pass.
2. **Cross-test runner extraction, skipped** ("standalone-test convention") — consistent with this
   repo's actual convention (every `test-*.py` here is independently runnable with no shared
   harness import), confirmed by running each suite individually above. No objection.
3. **Accumulate-loop reshape, skipped** — under-specified in the commit body (no diff was proposed,
   so there's nothing concrete to evaluate), but a skip has no downside to evaluate against. No
   objection.
4. **`_feat_dirs` glob reuse, skipped** ("cosmetic churn on panel-reviewed code") — the sound reason
   is that `B-2` records nothing pins `fpath`'s delivery half with a discriminating test yet; a
   silent reshape of the same glob logic that feeds it would be invisible if it broke something,
   unlike case 20's refactor (which had a fresh discriminating mutant re-run as its safety net,
   explicitly recorded: "still dies ... revert byte-identical"). The skip list drew the line exactly
   where re-verification exists versus where it doesn't. Correct call.

## Scope creep

`spec_violations: []`. 638 files touched in the full range, 567 of them pure `R100` renames; the
72 non-rename files are all accounted for by the four commits' stated purposes (the T-02..T-10
migration surfaces D-02 names, plus FEAT-21's own accumulating notes/bookkeeping). One rider already
on record and not mine to re-litigate: `B-13` notes three untracked FEAT-20 review files rode into
`d033b9d`'s 617-file commit, "harmless, recorded rather than repaired." No new rider found outside
that.

## Findings summary

| # | Finding | Severity | Blocks ship? |
|---|---|---|---|
| 1 | Four bare-basename labels (`check-state.sh:126,609,619,638`) outside D-08's traded pattern still don't resolve to an openable path | low | advisory only |
| 2 | `fpath()`'s `?` fallback is unreachable on any tree the script currently discovers | info | advisory only |
| 3 | `_feat_dirs` dict-overwrite is unspecified under a MIXED layout, but `INV-27` already blocks that state first | info | advisory only, folded into B-1 |
| 4 | `branch-create-gate.sh`'s hardcoded segment narrowed from universally-correct to repo-specific | low | advisory only, already tracked as B-5 |
| 5 | `check-plan-routes.py`'s segment-level readability guard gap was newly created by this range's migration | med | advisory only, already tracked as B-4, unchanged since precommit |
| 6 | `gh-sync.py`/`plan.yaml` T-10 text vs. actual probe (`team-config.yaml`) still not reconciled | low | advisory only, already tracked as B-6 |

No must-fix. Stage 1 (spec compliance) holds: the D-08 label-half delivery is real and correctly
scoped, no requirement is missing a corresponding change, no scope creep found. Stage 2 (quality):
both `/simplify` refactors are semantically equivalent to what they replaced, verified by hand-trace
and by running the actual test suites (not narrated) — `test-layout-migration.py`,
`test-check-plan-routes.py`, `check-state.sh` itself, and all 26 `test-*.py` suites in
`.claude/skills/harness/bin/` all exit 0 at `4a98cc4`.

```yaml
VERDICT: PASS
DIGEST:
  headline: "D-08's label half is delivered and complete for its traded pattern; both /simplify refactors are semantically equivalent to what they replaced; all four prior advisories are unchanged, already-tracked, or fixed-and-confirmed; nothing here blocks ship."
  severity_max: low
  findings: 6
  must_fix: []
  spec_violations: []
  reviewed: "ea937b1..4a98cc4"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-21-features-layout-migration/notes/review-harness-code-reviewer-2026-08-15-rereview.md
```
