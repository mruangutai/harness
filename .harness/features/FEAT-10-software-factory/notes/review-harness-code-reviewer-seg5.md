# Review — FEAT-10 seg5 — plan-vs-contract spec compliance (pre-build)

Stage 1 only (per dispatch; stage 2 is n/a — no code exists yet). No SHA exists: `DESIGN.md`,
`plan.yaml` and `BRIEF.md` are all untracked (`git status --short` confirms `??` on all three) — this
reviews the working-tree bytes directly, there is no committed version to diverge from.

## Per-row verdict — DESIGN.md:96-104 point-of-no-return table

| Tool | DESIGN.md row | Verdict | Basis |
|---|---|---|---|
| `factory_config` | none — mutates nothing | **correct** | `plan.yaml:313` — no writes anywhere in T-02 |
| `factory_decompose` | first successful `create_issue` | **WRONG** | see below |
| `factory_claim` | `create_ref` returning `True` | **correct** | `plan.yaml:640-710`; steps 1-4 and 5a are reads only; research note confirms a refused `create_ref` mutates nothing (HTTP 422, measured) |
| `factory_workspace` | the clone; local-only, disposable | **correct, loosely worded** | `plan.yaml:812-814` — step 3 is clone-OR-fetch+reset; the existing-checkout branch mutates without cloning. The stated *guarantee* (never touches GitHub, everything local/disposable) still holds on both branches, so this is imprecise wording, not a false promise — unlike the decompose row below |
| `factory_land` | the successful push in step 3 | **correct** | `plan.yaml:905-910` — steps 1-2 make zero calls of any kind before the guard |

### factory_decompose — the row is false, not imprecise

Stated PONR: "the first successful `create_issue`" (DESIGN.md:101). T-04's own steps put a real
GitHub mutation earlier:

- Step 5 (`plan.yaml:529-531`) calls `ensure_labels` **once, before any issue is created**, ensuring
  `factory:claimed` among other labels. The certain-mutation evidence: `plan.yaml:536-537` states
  "GitHub definitely rejects an issue CREATE naming an undefined label, and a fresh repository ships
  `bug` but not `harness`." On a fresh target repo the `harness`, `feature:<FEAT>` and
  `factory:claimed` labels **do not exist yet**, so `ensure_labels` unambiguously creates them —
  a certain GitHub-side write before the stated PONR, independent of what `--force` does on a
  label that already exists. (`plan.yaml:395-396` separately calls `--force` "idempotent for a
  label that already exists" — that claim is about re-runs against an already-labelled repo, not
  about the first run against a fresh one, and does not rescue the first-run case.)
- T-04's own intent text concedes the ordering and then reasons past it anyway: "The first mutation
  is `ensure_labels` in step 5, which is idempotent by `--force`. The point of no return is the
  first successful `create_issue`" (`plan.yaml:571`). Idempotency is a recovery property;
  DESIGN.md:85's promise is "**zero** mutating calls," not "zero non-idempotent" ones.
  `factory_land`'s own row applies the opposite standard: its push is also idempotent on re-run
  (`plan.yaml:908`) and still counts as the PONR.
- The consequence is concrete: `plan.yaml:599` mandates a test where `create_issue` raises
  `KeyError` and the tool exits 2 having created zero issues. On that exact path `ensure_labels`
  already ran and wrote to GitHub. **SC-14's own wording is correctly plural** — "each refusal path
  ... asserted over the full recorded call list rather than over one call" (BRIEF.md:145-146). The
  defect is not SC-14's phrasing; it is that T-04's operationalisation of it (`plan.yaml:593`,
  "every exit-2 path before the first `create_issue` ... zero mutating calls") silently narrows
  "every exit-2 path" to the four pre-step-5 paths enumerated at `plan.yaml:569-570` and never
  states the step-5-then-`create_issue`-raises path, which it must cover to be true to SC-14 and
  which cannot pass zero-mutating as written. That distinction matters to whoever fixes this: SC-14
  itself stays as written, the plan text (`plan.yaml:568-575,593`) is what moves. This is the DEC-169
  shape — a verify clause that reads as covering "every path" while actually covering a subset (my
  P-01/P-04 pattern).
- The fix is forced, not a style choice: `ensure_labels` cannot move after the first `create_issue`
  (per `plan.yaml:536-537` above, GitHub rejects the create first). The row's PONR must become
  "the `ensure_labels` call in step 5," and DESIGN.md:101's "what exit 2 can leave" column needs
  "labels created in the target repo" added.

**must_fix.**

## Loop control-flow (T-05 step 5, `plan.yaml:676-710`)

1. **Every branch continues or terminates deliberately; nothing strands remaining candidates
   incorrectly.** Skips (5a not-open/claimed/assigned, 5b `create_ref` False in poll mode) loop to
   the next candidate. Self-ownership success and a winning `create_ref` deliberately end the run
   (that's the point). A `create_ref` that *raises* `GhError` deliberately stops the loop rather than
   skipping (`plan.yaml:769-771`) — intentional, to keep an auth failure from being silently walked
   past as a string of ordinary skips. No fail-open shape found here.

2. **The two exit-1 causes are correctly distinct in the code as specified, but only one is locked
   by a test.** Step 4's empty-candidate-list path calls `nothing_to_do("claim", "no work
   available")`; step 5c's exhaustion path calls `nothing_to_do("claim", "no claimable work")` —
   different literal strings at the two call sites, so an operator reading stderr genuinely can
   tell them apart as specified. The gap: the test enumeration for the exhaustion case
   (`plan.yaml:756-758`, "exits 1 with a payload-free stdout and ZERO mutating calls") never
   asserts the string "no claimable work" the way the empty-column case does assert "no work
   available" on stderr (`plan.yaml:774`). Nothing stops an implementer from wiring 5c's call to the
   wrong literal and still passing every listed case. `med`, should-fix, not a contract violation
   since the *specified* behavior is correct — only the verify enumeration is loose (my P-01
   pattern: a case label describes coverage the assertion doesn't measure).

3. **Exit 3 is correctly confined to `--issue` mode.** `create_ref` returning `False` only reaches
   `factory_cli.lost_race` (exit 3) in the `--issue` branch (`plan.yaml:701-706`); poll mode routes
   the same `False` to a skip. Since `--issue` mode also collapses the candidate set to the single
   named item (step 3, `plan.yaml:656-660`), there's no queue behind it to strand. Confirmed correct.

## Silent-empty class — fourth instance

Checked every fleet-string-vs-GitHub-string comparison in T-05 per the dispatch's ask. Did not find
a clean fourth beyond the three already named (station option, repo URL-vs-slug, the wedge).
Repo-name case-sensitivity was a candidate but is speculative and unmeasured (nothing in
`research-FEAT-10-claim-atomicity.md` addresses it, GitHub returns canonical case) — not reporting
it as a finding, only naming that it was considered and dropped.

Checked the adjacent question of whether `factory_land`/`factory_decompose` validate their station
option names the way T-05 does (T-05 validates all three up front; T-04/T-07 don't). Traced into
`project_field_set` (T-03, `plan.yaml:448-451`): it resolves the field and option ids first and
**raises `GhError` naming the field or option when either is absent** — so an unknown option name in
`factory_land`/`factory_decompose` exits 2 loudly, not the zero-items-exit-0 shape. This matches
DESIGN.md's own "what exit 2 can leave" column for `factory_land` ("a pull request with the station
not yet moved"). Verified, not a defect.

## T-04 resume ambiguity — new finding

Step 4 (`plan.yaml:526`): "A recorded task is already published: skip it entirely, creating
nothing," without saying whether "recorded" keys on presence in `issues` or requires both `issues`
and `items`. The plan separately mandates a partial state can exist: `plan.yaml:585` requires the
issue number be written even when the subsequent board-add raises `GhError`. If "recorded" is
read as "present in `issues`" (the natural reading, since that's what step 4 is protecting against
re-creating), a task that hit that exact partial state is skipped **forever** on every re-run — the
issue exists with labels and body, but its board item is never added, and `factory_claim` (which
only ever polls the board) can never see it. No stderr line, no error, nothing — the work is
silently orphaned. DESIGN.md:101's recovery text only promises non-duplication ("re-run ... nothing
is duplicated"), so this isn't a contract violation, but it's an unflagged gap in exactly the class
this segment was spawned to hunt. No test case in T-04's list exercises "re-run after a board-add
failure completes the board add." Escalated to must_fix: permanently orphaned work with zero
operator signal is blocking-grade for a document about to be implemented literally, and the fix is
one clause plus a test case.

## must_fix

1. `factory_decompose`'s PONR row (DESIGN.md:101) is false — `ensure_labels` (T-04 step 5,
   `plan.yaml:529-531,536-537,571`) certainly mutates GitHub (creates undefined labels on a fresh
   repo) before the stated PONR. `plan.yaml:593`'s test enumeration silently narrows "every exit-2
   path" and cannot cover the step-5-then-`create_issue`-raises path without failing. SC-14 itself
   (BRIEF.md:145-146) is correctly worded and does not need to change. Fix: change the row's PONR
   to "the `ensure_labels` call in step 5," update the "what exit 2 can leave" column, and rewrite
   `plan.yaml:568-575`'s POINT OF NO RETURN paragraph and the `plan.yaml:593` verify clause to
   match.
2. T-04 step 4's resume semantics (`plan.yaml:526`) are ambiguous in the one word that decides
   whether a partially-published task (issue created, board add failed) is retried or silently
   orphaned forever. Fix: state explicitly that resume re-attempts the board add when `issues` has
   an entry but `items` does not, and add a test case for it.

Both are cheap, mechanical fixes to plan text — not a design rework — but they're false or
ambiguous guarantees under a human signature, which is what gates this stage.
