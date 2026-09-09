# QA measurement note — B-16 panel, pin c488218e

**BLUF: `must_fix: []`.** Pin fidelity holds, all three contract arms reproduce exactly as
specified, 5g reddens for the right reason (an UNRESOLVABLE BLOCKER read off kaya's map, not an
exception/no_plan/JSON-decode artifact), and order dependence on fixture list order is a
non-issue — the candidate sort is by issue number, not board_item insertion order. One genuine
co-vacuity hole exists but requires editing the shared assertion helper itself, which the dispatch
correctly distinguishes from a fixture-level hole; it is a labelled backlog note, not a gate.

## 1. Pin fidelity
`git -C <worktree> show c488218e:tests/unit/test-factory-claim.py` is byte-identical to the working
file (`diff -q` empty, 1327 lines both sides). The other three reviewers' worktree read is sound.

## 2. Three contract arms (measured in a disposable `git worktree add` at c488218e, never the
assigned worktree; `env -u HARNESS_AGENT_TYPE` on every run)
- **Intact:** `125/125 checks passed.` — 5b `ok`, 5g `ok`.
- **Drop harness's `depends_on=["T-99"]`** (`task_dict("T-77", depends_on=["T-99"])` →
  `task_dict("T-77")`): `124/125`, only failure is **5g FAIL**; 5b stays `ok`. Matches spec exactly.
- **Empty harness's issue map** (`{"T-99": 954}` → `{}`): `124/125`, only failure is **5b FAIL**;
  5g stays `ok`. Matches spec exactly.

## 3. Right reason (CONFIRMED)
5g's actual `(code, out, err)` under the mutant, captured directly:
```
(1, '', 'factory: claim: skip #951 — issue #951 depends_on T-88, ... (unresolvable blocker)\n'
        'factory: claim: skip #952 — issue #952 depends_on T-99, ... (unresolvable blocker)\n'
        'factory: claim: no claimable work\n')
```
Harness's #952 is refused as an **unresolvable-blocker skip**, same message shape as #951, naming
T-99 — not an exception (`5g`'s own `except` branch never fires), not `no_plan` (message absent),
not a JSON-decode short-circuit (stdout is legitimately empty because nothing claimed, not malformed).
Root cause confirmed by code reading `_BlockerCache.issue_number`: the mutant canonicalizes on the
*first* `(feature)` seen; that lookup resolves against kaya's map, which has no `T-99` entry, so
harness's own valid dependency is reported unresolvable — precisely the cache-bleed 5b/5g exist to
catch.

## 4. Order dependence (CONFIRMED — not an issue)
Swapped `board_item` list order (harness first, kaya second) in `_run_5b_scenario`: **identical**
`(code, out, err)` triple, 5b/5g outcomes unchanged. Reason (read from
`factory_claim.py:314-327`): candidates are sorted by `(issue_number, repo_index)` before
processing, not by board-item/fleet insertion order — 951 always precedes 952 regardless of the
fixture's list order. **5g's redness does not depend on incidental fixture ordering**; it depends
on the issue-number values themselves (951 < 952), which are declared adjacent to the property they
encode and are not "incidental."

## 5. Co-vacuity hunt
- **(a) Add `T-99: 954` to kaya's own issue map** — CONFIRMED as predicted: 5g goes **RED**
  (`124/125`, only 5g fails; 5b stays ok). The mutant then resolves harness's T-99 via kaya's map
  too (now present), reproducing the real per-repo outcome — mutant genuinely changes nothing
  observable. **Detected, not a hole.**
- **(b) Weaken `_5b_property_holds` to `payload.get("issue") == 952` only** (drop both `err`
  conjuncts) — CONFIRMED as predicted: **both 5b and 5g stay green**, `125/125`. This is a real
  co-vacuity hole: the predicate is shared, so one edit to it silently defeats kaya's half of the
  proof (that #951 is refused for the *unresolvable-T-88* reason, not something else) in both
  cases at once.
  - **Classification: requires an edit to the ASSERTION ITSELF** (the shared predicate function),
    not an innocent fixture/production edit. Every test is vulnerable to its own assertion being
    weakened; this is that same class, not a distinct gating defect. The one thing worth flagging
    beyond "every test has this exposure": because the predicate is *shared* between 5b and 5g, one
    such edit silently defeats twice the coverage a single-case predicate would — a larger blast
    radius than the generic case. **Backlog, `enhancement`**, non-gating: consider an assertion-level
    self-test (a case that flips the predicate's own conjuncts and confirms redness) if the panel
    wants defense-in-depth against edits to shared verification helpers specifically.
- **(c) `except Exception` leak probe** — CONFIRMED no leak: forced a `RuntimeError` immediately
  after `claim._BlockerCache = _FeatureOnlyIssueMapCache`, before the inner `try`. The `finally`
  still restored `claim._BlockerCache` (`POST-FINALLY-BLOCKERCACHE-IS-MUTANT: False`), and the
  outer `except` cleanly reported `FAIL BUG-1290 5g ... RuntimeError('INJECTED-FAULT')` — no case
  after it ran under the mutant. The `try/finally` genuinely covers every raise path reachable after
  the assignment; there is no gap between assignment and the inner `try`.
  - Note (non-gating, `chore`): 5g is the last case in the file, so even a hypothetical future leak
    would be harmless today — but nothing pins that position. A case appended after 5g in a later
    edit would inherit any latent leak with no test currently positioned to catch it. Worth a
    one-line comment if the panel wants it pinned; not a defect today since the measured leak
    surface is empty.

## Findings summary
- `must_fix: []`.
- Backlog: (1) `enhancement` — shared-predicate blast radius (5.b above); (2) `chore` — 5g's
  last-position dependency is undocumented, not unsafe (5.c above).

## Scope discipline
All work in a disposable `git worktree add <tmp-path> c488218e` (never the assigned worktree) plus
in-memory string edits written to `/tmp/arm-*.py` and copied into that disposable worktree only;
every mutation was `git checkout --`-restored immediately after its measurement
(`git status --porcelain` clean after each). Assigned worktree, `plan.yaml`, and every production
file are untouched. No commit, no push, no merge.
