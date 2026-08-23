# BRIEF audit — FEAT-34 worktree act 3 — contract fidelity vs grilling rulings

**BLUF: FAIL.** Two must-fix gaps, both concrete and both traceable to the operator's own stated
concerns: REQ-02's "exact command" clause has no SC that grades it, and SC-05 — the criterion built
specifically to guard against REQ-06 over-suppressing — does not exercise the short-named-worktree
miss that is the measured failure mode on disk. Every citation checked resolved correctly; no
ruling was dropped; Q1/Q2 genuinely do not entangle REQ-07/08/09 or SC-06/07/08.

## 1. Fidelity to the rulings — all nine `## Settled` bullets carried

Walked item by item against REQ-01..10 and Constraints/Out-of-scope:
- Blocking/exit 2 → REQ-01. Cost accepted → Constraints:103-105. Abandoned-flow out → REQ-06 +
  Out-of-scope:113-114. `Building`-no-worktree inverse out → Out-of-scope:115. Every repo →
  REQ-04. Dirty-still-blocks → REQ-03. Hook automatic/tracked-dir/guard/install (three things
  named before the ruling) → REQ-07/REQ-08/REQ-09 respectively. Gate not replaced by hook → Goal
  ¶2. No agent removes it → Out-of-scope:119-120 + REQ-10. Message names directory actually found
  → REQ-02 (first clause).

Nothing settled is missing. No ruling was silently widened into a bigger commitment than stated.

**Q1/Q2 tested, not assumed.** Q1 (hooks-directory mechanism, one-or-two) — REQ-09/SC-08 are
written at the outcome level ("a named setup step" / "core.hooksPath resolves to the tracked
directory") and neither commits to a single-repo-vs-fleet mechanism, so both readings still pass.
Q2 (hook removes every eligible worktree vs only the triggering one) — REQ-07/SC-06 grade only
"the merged feature's worktree was removed" and never assert anything about *other* eligible
worktrees, so a broader or narrower implementation both satisfy it. Confirmed neutral on both.

## 2. Coverage — REQ-02's second clause is uncovered (must_fix)

10 REQs, 10 SCs, but the trace is 1:1 only through REQ-06/SC-05; REQ-07→SC-06, REQ-08→SC-07,
REQ-09→SC-08, REQ-10→SC-09, and SC-10 is the blanket gate. **REQ-02 has two clauses — "names the
directory it actually found" AND "the exact command that removes it" — and SC-01 (the only SC that
could plausibly cover the plain-refusal case) grades only that a blocking `INV-28` finding
*appears*, never its content.** SC-03 grades message content, but only for the *dirty* variant
(REQ-03's clauses), which is explicitly not the same wording. No SC anywhere asserts that the
refusal names the removing command. This is an omission the operator would be signing blind to:
a refusal that fires but says nothing actionable would pass every SC as written.

REQ-05↔SC-02 checked directly: SC-02's deadlock fixture (working tree `Done`/default `Review` →
no finding; inverse → finding) is exactly REQ-05's HAZARD case from the grilling note
(`check-state.sh:22` reads the working tree by default) and is well-covered.

## 3. REQ-06 suppression risk — SC-05 does not test the operator's actual concern (must_fix)

Verified on disk: `git worktree list --porcelain` shows `FEAT-33` standing; `git ls-tree main
.harness/harness/features/` stops at `FEAT-32` — FEAT-33 has no directory on `main`. REQ-06's
carve-out is live, exactly as BRIEF:9-13 states.

The real risk is the implementation shape REQ-06 invites: any lookup that maps a worktree to a
feature by an exact name/id match will treat a **short-named** worktree for a real `Done` feature
the same as a genuinely abandoned one, because the lookup misses either way. The grilling note's
own last `## Settled` bullet says **four worktrees on disk were short-named** — this is not a
hypothetical, it's the measured shape of operator error this feature exists partly to survive.

SC-05 as written: "...while a sibling `Done` feature in the same fixture does [produce a
finding]." Nothing in SC-05's text requires that sibling's worktree to be short-named — it is
satisfiable with a worktree named exactly for the flow id, which exercises the trivial case
(REQ-06 isn't blanket silence) but never exercises the specific miss the operator is worried
about. A REQ-06 implementation that suppresses on any lookup failure — including a short-named
`Done` worktree — passes SC-05 as drafted. SC-05 needs a fixture where the `Done` sibling's
worktree is short-named to actually prove what its own prose claims.

## 4. Citations — all resolved, one correction confirmed correct

Re-derived at `HEAD` (`3ed95a4`): `check-state.sh:1076` (`worktree list --porcelain`), `:1086`
(`for _rec in _wt_out.split`) through `:1094` (`_entries.append`) — **the BRIEF's `:1086-1094` is
right; the grilling note's `:1083-1090` is stale**, confirming the BRIEF's self-reported
correction. `:1132`/`:1148` match the "no removal guidance / prints `remove <path>`" comment
pair. `SKILL.md:321`/`:325` match the act-3 prose and the exit-0-from-inside fact.
`harness-team` `SKILL.md:90` mentions worktrees, never removal — confirmed. `feature-worktree.py:287`
is the `rev-parse {default_branch}:{rel}` call; `resolve_repo` returns `default_branch` per repo —
confirmed. `run-unit-tests.sh:18` is `INTEGRATION_SCRIPTS=(...)`, `:110-115` is the two `KIND-DRIFT`
branches — confirmed.

Only `harness-orchestrator.md` preloads the bare `harness` skill among all 16 agents (grepped every
agent's `skills:` block). `harness-handoff`, `harness-expertise`, `harness-principles` contain zero
occurrences of "worktree." A sweep of every other skill (`harness-brief`, `harness-init`,
`harness-team`, `harness-verification-rules`) turns up worktree mentions with no removal statement —
so SC-09's claim "15 of 16 fail today" is accurate as its own red proof.

INV-28 as next-free: confirmed — highest active is INV-27 (`:1349`), INV-20 is in use (`:884`),
INV-10 is explicitly retired-and-unreusable (`:1403-1407`). DEC-174 amendment 4's text (read via
the index, opened directly — not the whole file) states the enforcement enumeration verbatim as
`check-domain.sh, bash-write-guard.sh, validate-digest.py, check-state.sh, check-plan-routes.py,
dispatch-guard.sh, and the test file of each` — the BRIEF's Constraints:88-96 enumeration matches
this exactly, including the non-exhaustive framing.

## 5. Fail-open, one level up (secondary, not gating)

REQ-06 states the "absent" case is out of scope. Nothing states what happens when the default
branch's `feature.json` is *present but unreadable* (malformed YAML, a `git rev-parse` error for a
reason other than a missing path). If an implementation folds "any read failure" into REQ-06's
"absent" carve-out, that is a second, unauthorized suppression path indistinguishable from the
first at the interface level. Flagging as `open_question` for the plan round rather than must_fix —
Q1/Q2 already carry precedent for leaving genuinely fog patches to the plan, and this is exactly
that shape.

## Verdict

```yaml
VERDICT: FAIL
DIGEST:
  headline: "REQ-02's exact-command clause is uncovered by any SC, and SC-05 does not exercise the short-named-worktree miss that is REQ-06's real suppression risk — both block signature."
  severity_max: high
  findings: 4
  must_fix:
    - "REQ-02 clause 2 ('the exact command that removes it') has no SC grading message content for the plain (non-dirty) Done refusal — SC-01 only checks that a finding appears, SC-03's content assertions are scoped to the dirty variant only."
    - "SC-05 proves REQ-06 is not blanket silence but does not require the sibling Done feature's worktree to be short-named, so it does not test the operator-flagged risk: a short-named worktree for a real Done feature being suppressed by the same lookup miss that legitimately exempts an abandoned flow. Four such worktrees were measured on disk per the grilling note."
  spec_violations:
    - { kind: omission, path: ".harness/harness/features/FEAT-34-worktree-act3-enforced/BRIEF.md:39-40 (REQ-02)", ref: "REQ-02" }
    - { kind: omission, path: ".harness/harness/features/FEAT-34-worktree-act3-enforced/BRIEF.md:142-145 (SC-05)", ref: "REQ-06" }
  reviewed: "none"
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "Should the BRIEF state what happens when the default branch's feature.json is present but unreadable/malformed, distinct from REQ-06's 'absent' case, so an implementation cannot fold both into one silent skip?", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-34-worktree-act3-enforced/notes/review-harness-code-reviewer-brief-audit-validator.md
```
