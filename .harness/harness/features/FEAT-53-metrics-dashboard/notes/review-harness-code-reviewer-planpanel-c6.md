# Plan-panel c6 — scope read — amended T-05 — e6b93643

Read at `e6b93643` in the FEAT-53 worktree (`git rev-parse HEAD` confirmed). Diff scope confirmed
against `1745ca83..e6b93643`: only `plan.yaml` (top `status`, `approval:`, T-05's title/verify/intent)
and `STATE.md` changed. `BRIEF.md`, `DESIGN.md`, `feature.json` untouched — so no SC/REQ changed
meaning, and T-05's `traces: [REQ-11, REQ-12]` is unchanged from before the amendment.

## Stage 1 — spec compliance (DESIGN.md:532-545 gap closure)

- **(a) TBL-1/TBL-2/TBL-3 — MET.** `plan.yaml:375-376` names all three tables by id with "their pinned
  group and row semantics"; verify (`:366`) greps for all three tokens.
- **(b) S-5 unattributed-bucket state — MET.** `plan.yaml:383-384` ("S-5 demonstrates unattributed
  commits as their named bucket treatment"); verify greps `S-5`.
- **(c) C-3 keyboard/focus — MET as intent, but see finding F-3 below.** `plan.yaml:385-387` names
  focus-stop order, the 2px/2px text-token ring, and per-transition focus landing (drill/Back/theme/
  disclosure) — covers DESIGN C-3 clauses 1-3 explicitly; clause 4 (chart `aria-hidden` + adjacent
  table in tab order) is covered by "Charts are aria-hidden and their adjacent real tables carry the
  values." All four C-3 clauses are named in intent. Unlike (a)/(b)/(d), **no token in C-3 is
  machine-checked** — see F-3.
- **(d) Seventh tile / 3×3 grid — MET.** `plan.yaml:374-376` ("DESIGN C-1's fixed 3x3 grid of seven
  tiles ... tile 7 ... LAST and full-width on row 3"); verify greps `3x3`.
- **(e) Never rendered by anyone — PARTIALLY MET: instructed, not gated.** Intent (`:389-393`)
  instructs launching the prototype in a real browser in both themes and capturing the observed
  result in README.md. But `verify:` (`:363-366`) is `npm ci && npm run build && <token grep>` —
  none of which proves a browser ever opened or that README.md carries an observation record (the
  grep would pass on a README that merely repeats the design-spec vocabulary as prose). The
  browser-observation half of the gap DESIGN.md:539-542 documents remains **honour-system**: nothing
  in the mechanically-checked `verify:` can distinguish "rendered and observed" from "instructed to
  render, wasn't." This is the same failure C-4's own text warns about ("prose is the medium it
  hides in," DESIGN.md ~line 521) — see F-2, which is this same gap restated as a plan-quality issue.

No REQ/SC changed meaning; the amendment closes (a)/(b)/(d) as machine-checked requirements and (c)
as an intent-level requirement with no machine check of its own.

## Stage 2 — plan quality

### F-1 · `npm ci` cannot succeed on a clean checkout of the committed tree — **high, must_fix**

`plan.yaml:355-361` files T-05 to `.gitignore`, and that file (`notes/prototypes/FEAT-53/.gitignore`)
reads `node_modules/`, `dist/`, `.smoke/`, `package-lock.json`. `git cat-file -e
e6b93643:.../FEAT-53/package-lock.json` confirms the lockfile is **absent from the pinned commit's
tree** (`git ls-files` over that directory lists no `package-lock.json`). `npm ci` hard-requires an
existing lockfile matching `package.json` and fails immediately without one — it is not an install
fallback the way `npm install` is.

The verify block (`plan.yaml:363-366`) was **newly added by this amendment** — the pre-amendment T-05
verify was a pure `python3` grep with no `npm` step at all, so this is a defect the amendment
introduces, not a carried-over one. Sibling task T-04 shows the plan author already knows the fix:
`plan.yaml:290-296` lists `package-lock.json` in `files:` and its intent (`~line 327`) explicitly says
"Run npm install in that directory and COMMIT the resulting `package-lock.json`." T-05 does neither:
`package-lock.json` is absent from its `files:` list (`:355-361`) and its `.gitignore` — which T-05
itself owns and could edit — actively excludes it.

Failure scenario: harness-visual-designer executes T-05 against the files: list as written, builds
the prototype, and either never notices the ignore rule (verify passes locally because the working
tree already carries a stray, untracked `package-lock.json` predating this session — confirmed present
on disk at 1 day old vs. 17h for the other prototype files, i.e. leftover from earlier local work) or
commits everything the list names and nothing else. Either way the committed tree at the task's own
completion has no tracked lockfile. A fresh reviewer, CI, or the next panel cycle re-running T-05's
own literal `verify:` against a clean clone of the resulting commit hits `npm ci` failing at the first
step — the task can never mechanically re-verify itself on a clean checkout, undermining the very
thing adding `npm ci` was meant to prove (that the prototype builds from what's actually committed).

### F-2 · The python3 token check is presence-only and defeatable by prose, not rendering — **med**

`plan.yaml:366` concatenates every `.html/.md/.js/.jsx/.ts/.tsx/.json/.css` file under the prototype
directory (this now includes `README.md`, which T-05's own intent requires to carry the
browser-observation writeup) and greps for the literal tokens `S-1..S-5, TBL-1..TBL-3, 30d, 90d, 3x3`.
A README that documents "observed S-1 through S-5, TBL-1 through TBL-3, 30d/90d/all, in the 3x3 grid"
in prose satisfies every one of these literals without any component in `src/` rendering a single one
of them correctly — or, for that matter, existing. This is not a hypothetical the reviewer invented:
DESIGN.md's own C-4 preamble (~line 521) exists specifically because "prose is the medium [the
failure] hides in," and this verify clause is exactly a prose-shaped hiding place for the same
failure it is meant to catch. Given who executes the task — harness-visual-designer, dispatched with
explicit, detailed build-and-observe instructions — a deliberately gamed README is unlikely; the
realistic risk is not malice but the honest gap in (e) above: an executor who runs out of cycle budget
mid-build, writes the intended-state README first (a natural drafting order), and never gets back to
actually wiring one of the five states — the grep still passes. Rated `med`, not `high`, because the
plan does not rely on this check alone: DESIGN.md is explicit that a human/panel browser inspection is
the real gate (STATE.md: "the amended plan requires a fresh adversarial panel read"), so a gamed or
merely-aspirational README is still catchable downstream — just not by this task's own `verify:`.

### F-3 · C-3 keyboard/focus is named in intent but carries zero tokens in verify — **low**

Unlike (a), (b) and (d), DESIGN C-3's keyboard/focus contract (`plan.yaml:385-387`) has no
corresponding literal in the `verify:` grep list. An executor who implements every other clause and
skips C-3 entirely produces an artifact whose `verify:` still passes clean. This is consistent with
DESIGN's own position that keyboard/focus is inspection-only (SC-15, no automated `ui` runner), so it
is not a defect unique to this amendment, but it does mean T-05's own gate carries no signal at all
for the one DESIGN clause (C-3) that is hardest to eyeball quickly in a panel read — worth naming so
the next panel specifically inspects C-3 in the built artifact rather than trusting T-05's green verify.

### F-4 · D-23's B-25 subject and finding C4-07 both describe a remedy the amendment has superseded — **med**

`plan.yaml:186-189` (D-23.choice, B-25's recorded subject) and `plan.yaml:2106-2117` (finding C4-07,
disposition `backlog`) both state that T-05 "wants one clause recording the six-tile artifact as
accepted under DEC-5's closure" — i.e., the accepted remedy was to *keep* the stale six-tile 3×2
prototype and add one sentence documenting that the divergence from the 3×3/seven-tile contract is
accepted. That premise is now false: the amended T-05 does not keep the six-tile artifact and does not
add an acceptance clause — it replaces the prototype outright with a build that closes the 3×3/
seven-tile gap directly (Stage 1(d) above, MET). The backlog item's very reason for existing (a known,
accepted, permanent divergence) has been closed by different means than the accepted remedy describes.

Concrete failure scenario: D-23 is the single carrier "a filer at ship does not have to reconstruct
[the accepted backlog set] from a briefing" (`plan.yaml:190-198`) — if this plan proceeds to ship with
D-23 untouched, the ship step files a GitHub issue for B-25 asking someone to add "one clause recording
the six-tile artifact as accepted," describing an artifact and a disposition that no longer exist once
T-05 has run. The issue would be actively wrong, not merely stale, and nothing in the diff or in any
task corrects it. **No task owns this correction** — D-23/C4-07 are plan-level records with no lane
grant reachable by any team task, and no plan-cycle task touches them. This needs either a
main-session/orchestrator edit to D-23 and C4-07 (mark C4-07 `resolved_by: T-05`, correct B-25's
subject to reflect the rebuild) or an explicit operator ruling that the correction waits for the next
signature pass. It is in scope per this panel's brief (the amendment falsified a CLOSED item's recorded
subject) and is not a re-litigation of D-23's underlying backlog-filing mechanism, which stays accepted.

### F-5 · DESIGN.md:532-545's "Status of the committed prototype" goes stale once T-05 lands — **low**

The same falsification applies to DESIGN.md itself. Lines 532-545 describe the *current* (pre-T-05)
committed prototype as lacking TBL-1..3, S-5, C-3 and the seventh tile, and as never rendered by
anyone — explicitly framed as "read this before waiving the gate." Once T-05 executes, every one of
those clauses becomes false of the artifact at that path. No lane row grants any team agent write
access to `DESIGN.md` (checked `plan.yaml:1-33`; the lanes list has no `DESIGN.md` surface at all), and
no task's `files:` list includes it, so nothing in this plan updates it. This is lower severity than
F-4 because DESIGN.md's own contract clauses (C-1..C-4) are untouched and remain authoritative — only
the descriptive "status" paragraph rots — but a future reader deciding whether to waive the prototype
gate (the paragraph's own stated purpose) would be told the opposite of the post-T-05 truth.

## Ordering, ownership, approval — no findings

- **Lane/ownership:** `notes/prototypes/**` is granted to `harness-visual-designer` (`plan.yaml:23-25`),
  matching T-05's `execution_agent`. Correct.
- **`depends_on: []` is correct.** T-05's `package.json` pins its own, independent dependency set
  (`@astryxdesign/core 0.5.2`, its own React/TanStack Router versions) unrelated to T-04's client
  package under `.claude/skills/harness/bin/dashboard/client/**`; nothing in T-05 consumes a T-04
  output.
- **Downstream consumer T-13** (`plan.yaml:1034-1057`) depends on `[T-01, T-04, T-05, T-18]` and is
  built "against the prototype from T-05" — a design/behavioral reference, not a code import (T-13's
  own `files:` are fresh `.tsx` under the client tree). The amendment **fixes**, rather than creates, a
  prior mismatch: pre-amendment T-05 pointed T-13 at a stale six-tile reference; post-amendment T-05
  gives T-13 a reference that actually matches what DESIGN commits T-13 to build. No ordering finding.
- **Approval reset is correct per DEC-75** (`.harness/harness/docs/DECISIONS.md:851-867`): the
  prototype and the plan are one bundled signature, and T-05's rewrite is a material change to the
  prototype half of that signature, so resetting `approval.status` to `pending` (`plan.yaml:6-9`) is
  the required action, not an overcautious one. STATE.md's account of the reset (STATE.md:9-16) matches
  DEC-75's reasoning correctly.
- **`feature.json` is consistent** — it carries no approval-mirroring field to go stale (`review_sha:
  "none"`, no ship yet); nothing there contradicts the reset.
- **`panel:` block** (`plan.yaml:1767+`) still shows `last_run: 2026-09-02-08-validator`, `cycle: 5` —
  this is expected, not stale: this very c6 panel run is the mechanism that updates it. No inconsistency
  to report.

## Verdict basis

`must_fix` = [F-1]. `severity_max` = high (F-1). Findings F-2 through F-5 are notes, not gates — they
do not individually block, but F-4 in particular should be closed before ship (not necessarily before
this signature) since it will otherwise produce a false GitHub issue.
