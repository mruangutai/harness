# Plan-panel c0 — scope reader — BUG-1480

**BLUF: the plan is spec-sound and the fix is correctly traced through the source at every point I
checked. One genuine traceability gap (REQ-06 is orphaned in `plan.yaml`'s `traces:`) and one
already-flagged rot risk (stale numeric anchors in `BRIEF.md`'s Constraints) are worth a line-edit
before signature; neither changes what ships.** No scope creep, no missing task, no bad `depends_on`
order, no `verify:` asserting something a predecessor deletes.

## The five questions

**1. `_checkout_root` correctness across the four cases, named callers.**
Confirmed correct. There is exactly one call site of `shape_problems` — the loop at
`check-domain.sh:2255-2257` — fed by five `targets`-construction sites, and **all five pass a real,
non-`None` `absolute_path`**, never a literal `None`: the Edit-identity-witness branch
(`:2044`, `_claimed_abs(target)`), the Edit-reconstructed-content branch (`:2073`,
`_claimed_abs(target)`), the PRE Write branch (`:2077-2078`, `_claimed_abs(target)`), the POST-with-
target branch (`:2095`, `_claimed_abs(target)`), and the Bash sweep's `targets.append` (`:2218`,
the glob-matched `_p`). `absolute_path is None` is reachable only through the parameter's own
default and is not exercised by any caller in this file or by any test (`grep` for
`shape_problems(` in `tests/integration/test-check-domain.py` returns nothing) — the helper's
`if not path: return root` guard is correct defensive code for an unreached case, not evidence of a
live path I could exercise. For the three reachable cases: main-checkout path →
`harness_boundary.worktree_owner` walks up to the main repo's `.git` **directory** and returns
`(main_root, main_root, True)`, so `real(_ck[0]) == real(root)` and the helper falls through to
`root` — correct. Worktree path (as built by `make_linked_worktree`, `.git` **file**) → returns
`(wt_root, main_root, legitimate)`, `real(_ck[0]) != real(root)` → helper returns `_ck[0]` = the
worktree root — correct. Path outside every checkout (e.g. `/tmp/x`) → `worktree_owner` walks to the
filesystem root, returns `None`, `checkout_relative` returns `None` → helper falls through to `root`
— matches `_norm`'s own fallback to a base-relative `rel` in the same case, so the pairing holds.

**2. `rel`/root coherence.** Holds in every case, and not coincidentally: `_norm(target)` and
`_checkout_root(absolute_path)` are called on the **same underlying `target`/`_p`** at every one of
the five sites above (`_rel = _norm(target)`, `_absolute = _claimed_abs(target)` land in the same
tuple), and both functions apply the byte-identical guard
`_ck is not None and _hb.real(_ck[0]) != _hb.real(root)` against a call to the same
`harness_boundary.checkout_relative`. When the guard is true, `_norm` returns `_ck[1]`
(`relpath(abs, _ck[0])`) and the helper returns `_ck[0]` — a path and its own base, by
construction. When the guard is false (main checkout, outside-every-checkout, or an absorbed
exception), `_norm` returns the base-relative `rel` computed against `root` and the helper returns
`root` — again a path and its own base. I found no route where `_norm` takes one branch of that
guard and `_checkout_root` takes the other.

**3. T-01's fixture is genuinely worktree-only.** `make_linked_worktree` (`:138-155`) writes both
sides of the pointer pair (worktree-side `.git` file, owner-side `.git/worktrees/<id>/gitdir`), which
is exactly what `worktree_owner` needs to resolve `checkout_relative` to the worktree rather than
`None`. `_env(root)` sets `HARNESS_PROJECT_DIR=root` (main), and `resolve_root` only honors that
override when `<root>/.harness/team-config.yaml` exists — T-01's fixture writes that file at the main
`root` via `_handoff_done_when_fixture`, never inside `wt_path`, and the task text repeats the
fixture's own docstring reason ("callers root their session at `root`... NO team-config.yaml inside
the worktree"). So the session stays rooted at main while the target file resolves to the worktree —
precisely the defect's shape.

**4. Row 3 (`brief-sc:SC-99`) is genuinely red pre-fix, green post-fix.** Traced `_read_target`
(`handoff_done_when.py:78-87`) and `_resolve_brief` (`:132-139`). Pre-fix, `root` passed to
`problems()` is the main checkout, so `feature_dir = main_root / ".harness/harness/features/
BUG-1480-wt-fixture"` does not exist; `Path.resolve(strict=True)` raises, caught and re-raised as
`ValueError("cannot resolve target: ...")`, and `_unresolved` (`:112-113`) formats
`f"...unresolved in {target}: {detail}"` with `target = feature_dir / "BRIEF.md"` — a **main-root**
path, which does not contain `"BUG-1480-wt"`. The first needle (`"SC-99"`) DOES match pre-fix,
because `{pointer!r}` (`'brief-sc:SC-99'`) is embedded in the same message — confirming the plan's own
stated reason row 2's `("T-99",)`-only needle would be insufficient here and row 3 needs the second,
path-shaped needle. Post-fix, `_checkout_root` resolves to the worktree root (a realpath, so possibly
`/private/var/...`), and `target`'s string ends in exactly
`.../BUG-1480-wt/.harness/harness/features/BUG-1480-wt-fixture/BRIEF.md` — both needles now match.
Exit code is 2 in both cases (SC-99 is absent from the fixture BRIEF.md either way), so only the
needle pair — not the exit code — discriminates red from green, which is exactly what T-01 claims.

**5. Any SC green with T-02 reverted?** Yes, three, and all three are intentional, not vacuity bugs:
SC-02 (pre-existing handoff cases) is unaffected by T-02 by design — REQ-02 asks for *no change* to
main-checkout behaviour, so it being true both before and after is the criterion working as stated.
SC-03's `"unresolvable pointer refused"` row is explicitly documented in `BRIEF.md` itself as "the
vacuity control" that is "green BOTH before and after the fix" — the plan names this, so it is not a
fresh gap. SC-05 (`_norm`'s contract and call sites unchanged) is also trivially true pre-T-02 since
nothing has been touched yet — it is a scope constraint on the diff, not a proof the fix works, and
the BRIEF frames it that way. None of SC-01, SC-04, SC-06, SC-07 stay green with T-02 reverted: SC-01
needs row 1 green (red pre-fix, confirmed at Q4); SC-04/SC-06/SC-07 all cite code or history that
does not exist without T-02.

## Findings

- **REQ-06 has no task tracing to it (`med`).** `plan.yaml`'s `T-01.traces` is
  `[REQ-01, REQ-04, REQ-05]` and `T-02.traces` is `[REQ-01, REQ-02, REQ-03, REQ-04]` — REQ-06 (the
  containment-bound requirement added by the F-06 remedy, graded by SC-07) appears in no task's
  `traces:` list at all, even though T-02's own code change is exactly what SC-07's `verify:
  inspection` cites (`_checkout_root`'s `root` fallback feeding `_read_target`'s
  `relative_to(root)` bound). A reviewer using `traces:` as the Stage-1 accountability trail — the
  check this dispatch exists to run — would find REQ-06 unserved by any task and either wrongly flag
  an omission or wrongly assume it needs a task nobody wrote. Remedy: add `REQ-06` to `T-02.traces`;
  no code or verify change needed, since the behaviour is already there.
- **`BRIEF.md`'s `## Constraints` BLOCKS entry still carries the pre-fix numeric line anchors for
  `_norm`'s call sites (`low`).** `:1906`, `:1912`, `:2042-2048`, `:2073`, `:2077`, `:2089-2090` — the
  same anchors SC-05 itself replaced with by-name citations for the stated reason (T-02's ~14-line
  insertion after `:1149` shifts everything below it). Verified these numbers are accurate at HEAD
  today (the PRE-branch `_norm` calls do fall inside `:2042-2078`, and `_resolved_rel`/`_plan_route`
  are confirmed at `:1906`/`:1912`), so nothing is wrong yet — but the moment T-02 lands, a reviewer
  reading Constraints (rather than SC-05) and citing these numbers lands on unrelated code. Already
  recorded as an open, unapplied item in `research-BUG-1480-remedies-applied-c0.md`; repeating it here
  because it is a live spec trap for whoever signs next. Remedy: swap the same six line numbers for
  the same by-name citations SC-05 already uses.

## Open questions

- None blocking. Both findings are one-line artifact edits the pm owns; neither touches code, task
  count, or approval status.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Plan is spec-sound and every source-grounded claim in T-01/T-02 checks out; REQ-06 is untraced in plan.yaml and BRIEF's Constraints still carries anchors SC-05 already fixed elsewhere."
  severity_max: med
  findings: 2
  must_fix: []
  spec_violations:
    - { kind: omission, path: .harness/harness/features/BUG-1480-handoff-note-checkout-root/plan.yaml, ref: REQ-06 }
  code_grade: "n_a"
  reviewed: "plan:/Users/molchairuangutai/GitHub/harness/.harness/harness/features/BUG-1480-handoff-note-checkout-root/plan.yaml"
  human_commits_in_scope: []
  open_questions: []
  files_touched: ["/Users/molchairuangutai/GitHub/harness/.harness/harness/features/BUG-1480-handoff-note-checkout-root/notes/review-harness-code-reviewer-planpanel-c0.md"]
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.harness/harness/features/BUG-1480-handoff-note-checkout-root/notes/review-harness-code-reviewer-planpanel-c0.md
```
