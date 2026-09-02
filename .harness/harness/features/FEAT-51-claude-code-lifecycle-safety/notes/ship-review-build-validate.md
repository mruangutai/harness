# FEAT-51 Claude Code lifecycle safety — ship review

**The feature is built, validated, merged, and accepted for shipment.** Nine of nine tasks landed,
eleven success criteria are met, SC-10 and SC-12 were withdrawn by explicit operator rulings, and
the review panel is clean at `severity_max: low` with no `must_fix`. The operator withdrew SC-10 on
2026-09-02 rather than represent the OMP pre-flight as Claude Code UAT evidence.

**The validation was worth paying for.** The panel found two high-severity defects at the first
pin, and one of them was a regression in the very protection this feature exists to provide. Both
are fixed and independently re-verified. Detail is §3.

---

## How this briefing was assembled

**No report round was spawned.** I read the run digests off disk rather than pay a squad to
re-narrate files that already exist (DEC-69). The build and validation phases are mine and I ran
them; the plan phase predates me and I took it from my predecessor's own signature briefing rather
than from context.

Assembled from: `runs/2026-09-01-01-eng/digest.md` (T-04) · `runs/2026-09-01-02-eng/digest.md`
(T-08) · `runs/2026-09-01-1-product/digest.md` (T-06) · `runs/2026-09-01-03-validator/digest.md`
(qa gate) · `runs/2026-09-01-05-eng` and `runs/2026-09-01-04-product` (the two qa fix cycles) ·
`runs/2026-09-01-2-simplify-eng/digest.md` (SIMPLIFY) · `runs/2026-09-01-01-product/digest.md`
(goal-check) · `runs/2026-09-01-04-validator` (panel) · `runs/2026-09-01-1-eng` (panel fix) ·
`runs/2026-09-01-05-validator` (panel delta) · `runs/2026-09-01-06-product` (SC-07 and UAT) · and
for the plan phase, `notes/ship-review-plan-signature-c9.md`.

**Everything I state as measured, I measured myself.** Where a claim is a squad's and I did not
re-run it, I say so.

---

## §1 — The decision: ship

On 2026-09-02 the operator explicitly chose to skip the Claude Code-specific UAT and withdraw
SC-10. The OMP pre-flight was not treated as a pass: it cannot exercise the compatibility-host
quarantine branch. The feature therefore ships with live Claude Code parent resumption unverified.

PR #1151 is merged. Record the ship transition.

---

## §2 — What shipped

A third answer for a parent with live children, and a write boundary for an orphaned one.

- **The suspension.** A lead or orchestrator with live children can now end its turn legally by
  returning `VERDICT: SUSPENDED` with an `awaiting` list naming every live child. It exits 0, and
  crucially **the parent's own claim is not released** — a suspension is not a completion. A
  terminal verdict with a live child is still refused at exit 2. `SUSPENDED` is recognised only
  inside `validate-digest.py` `hook_mode` and is deliberately not a member of `VERDICTS`, so no
  member persona and no written digest can carry it.
- **The quarantine.** A governed writer with no live claim for the feature it is writing, while
  some other live claim for that feature exists, is refused at two registered gates and told the
  exact quarantine path to write instead. It is a **write boundary, not a kill**: reads, greps and
  writes to `notes/`, `observations/` and `runs/` are untouched. Quarantined content is inert until
  a resumed parent runs `quarantine.py adopt`; nothing happens on a timer.
- **The CLI.** `quarantine.py list / adopt / discard`, stdlib only, no scheduler and no implicit
  action. `plan.yaml` adoption delegates to `plan-merge.py apply` so the locked union merge and the
  byte-identical approval carry-forward are the merge tool's answer, not a second implementation.
- **The record.** DEC-210, which states the non-coverage as plainly as the coverage.

---

## §3 — What validation caught, and why it mattered

**The panel found two high defects at the first pin. Neither was cosmetic.**

**F-1 was a regression in this feature's own protection.** `validate-digest.py` had narrowed the
live-children refusal from `if _kids:` to `if _kids and _return_verdict in VERDICTS:`. A parent with
a live child and an absent, null or unparseable last message therefore **skipped the refusal
entirely**, had its own claim released, and exited 0 — where the same input exited 2 before this
feature touched the file. That is the interrupted-parent case, which is precisely what FEAT-51 was
built to govern, and no test covered the combination. **We would have shipped a feature that widened
the hole it was written to close.** I verified the premise myself with `git show` at both commits
before spending a cycle on it. Fixed; the refusal is unconditional again and the uncovered
combination now has a permanent regression test proved red against the old binary.

**F-2 was a new unauthenticated cross-feature overwrite route.** `quarantine.py adopt` checked only
the basename and derived its target by directory arithmetic, while the Bash gate recognised the
adopt route only when the path segment was spelled literally `quarantine` — so the orphan predicate
was never consulted. The security reviewer reproduced it end to end: gate exit 0, adopt exit 0,
another feature's canonical `feature.json` overwritten, no live claim required. Fixed on both sides
to one shared realpath-containment rule; the original exploit now exits 2 with the canonical file's
sha256 unchanged, across a nine-row attack matrix, and both legitimate adoptions still succeed.

**The delta re-verification passed on measurements, not inspection** — every closure proved by a
red-on-the-old-binary run. `severity_max: low`, no `must_fix`.

**Three vacuous gates were caught across this feature** — a test that could not go red, a checker
that discovered nothing, and an OMP fixture whose claim was pruned before its assertion ran. The
last of those was SC-07, and it is why SC-07 was graded not-met until a mutation proof showed both
hook-level cases going red with the exemption removed. A green test is a claim, not evidence, and
this feature has now paid for that lesson three times.

---

## §4 — The gate of record, and the one number that is not green

| kind | result |
|---|---|
| `--kind unit` | **exit 0, 519 PASS, 0 FAIL** |
| `--kind integration` | **exit 1, 755 PASS, 7 FAIL** |
| `test-quarantine.py` | exit 0, 35 checks |
| panel | PASS, `severity_max: low`, no `must_fix` |

**The seven are the ones you already ruled on**, and the evidence is worth restating because it is
the sharpest process finding of this feature. All seven are `test-check-plan-routes.py`'s manifest
DEVIATION family. `diff` of main's `team-config.yaml` against the branch's returns **exactly** T-03's
approved route line plus its comment and nothing else; `_manifest_deviation`'s own docstring records
that a route change deviating is *intended*; clearing the one other cause moved 9 FAIL to exactly 7;
and pointing `HARNESS_PROJECT_DIR` at the worktree changes nothing, because the checker resolves
against the **owner** manifest, which is what the hook actually consults.

**So the project's only blocking gate cannot go green on any branch that changes a route in
`team-config.yaml`.** That is gate placement, not this feature. Backlog row B-13.

---

## §5 — Success criteria

Eleven met; SC-10 and SC-12 withdrawn by operator rulings.

| | |
|---|---|
| SC-01 … SC-06 | **met** — suspension accepted, refusals, claim liveness, both gate surfaces, the CLI |
| SC-07 | **met**, after a fix — the OMP fixtures now carry a live supervisor pid and go red when the exemption is removed |
| SC-08, SC-09, SC-11, SC-13 | **met** |
| SC-10 | **withdrawn** by the operator on 2026-09-02; Claude Code live-host conduct remains unverified |
| SC-12 | **withdrawn** by the operator's plan-phase ruling, number left as a deliberate gap |

pm's evidence: `notes/research-FEAT-51-goalcheck-build-c1.md` and
`notes/research-FEAT-51-goalcheck-sc07-c2.md`.

---

## §6 — Proposed backlog

**Anything not listed here dies silently. Strike rows by ID.** Rows B-1 to B-12 carry over from the
signature briefing; B-13 onward are new from build and validation.

| ID | nature | item |
|---|---|---|
| B-1 | enhancement | Gate the generic Bash write route to canonical feature artifacts. The hole D-19 admits and DEC-210 states plainly: `cp`/`cat`/`tee`/`mv`/`sed -i`/`python3 -c` inside the writer's own domain passes all three PreToolUse gates. Measured, exit 0 on all three. |
| B-2 | bug | `plan-merge.py` could not give a plan an `approval:` mapping. **You fixed this as this feature's prerequisite — strike this row.** |
| B-3 | chore | T-08 couples three permanent suite tests to DEC-210's prose, so rewriting that entry reds the enforcement-layer suite through a DEC-174 lane. |
| B-4 | chore | The one-run Claude Code host spike `PF-e380f685c0697fb709ff29f65af0cf24`: does the host re-enter a parent that returned exit 0 from its Stop hook with a live child claim, with nobody touching it? **pm's recommendation, and mine: run this BEFORE the ship decision.** Nine tasks rest on that assumption, the UAT does not answer it — the UAT measures operator-driven resumption — and this spike is cheaper than the UAT and strictly more falsifying. |
| B-5 | bug | `harness-code-reviewer` could not terminally yield on a plan-phase dispatch: `validate-digest.py` refused `code_grade: n_a` and refused it omitted. Did not recur this phase once the pin existed. |
| B-6 | bug | `plan-merge.py`'s `UNION_KEYS` is `("tasks", "decisions")` only, so `lanes` and `panel` cannot be amended incrementally. Possibly closed by `BUG-1128-plan-amend-verb`. |
| B-7 | bug | `check-domain.sh` denies `harness-pm` a `Write` at `notes/plan-proposal-*.yaml`, so the sanctioned tool is refused for the one write route `plan.yaml` has — and `python3` reaches it anyway. |
| B-8 | bug | `bash-write-guard.sh` reads a `>=` inside Python source as a redirect and refuses the command. |
| B-9 | bug | `check-plan-routes.py` never reads `lanes.rows`, so a surface missing from that block is ungated. |
| B-10 | chore | A lead digest missing `artifact:` is written and accepted by its own run; only `check-state.sh` catches it later. |
| B-11 | chore | `panel.findings`' `reader` enum has no word for a lead's fan-in finding. |
| B-12 | chore | INV-29 red on `.claude/worktrees/harness/BUG-1129-validate-handoff-sweep` — another effort's dirty terminal worktree. Untouched by me. |
| **B-13** | **bug** | **The only blocking gate is unsatisfiable pre-merge for any `team-config.yaml` route change.** Six `test-check-plan-routes.py` cases run fixture plans against the LIVE checkout, so a branch that legitimately adds a route reddens them until merge. Move those cases onto an isolated fixture root. §4. |
| **B-14** | **bug** | **A repo-relative editor write resolved against the MAIN checkout instead of the dispatched worktree — twice, independently, in this one feature.** Both succeeded silently because the two copies were byte-identical; one was caught only because a generator then wrote no row. Both cleaned. Plausibly `BUG-1030-stale-anchor-write-hazard`'s territory. An absolute-path-plus-check-both-trees mitigation in the dispatch held for every run after I added it. |
| **B-15** | **chore** | The orphan-refusal MESSAGE is hand-written twice — `check-domain.sh:1695-1702` and `plan-sign-gate.py:400-414`, character-identical middle sentence — while the predicate is correctly single-homed. `plan-sign-gate.py`'s own header states the one-refusal-text rule the same file breaks 350 lines later. |
| **B-16** | **chore** | `test-quarantine.py` hardcodes the four canonical basenames, so a fifth `CANONICAL_ARTIFACTS` entry would go silently uncovered. The reader's proposed fix was refused because deriving both sides from one source weakens what it pins; the additive fix is an equality assertion. |
| **B-17** | **bug** | `test-check-domain.py`'s "a CRASHING schema module DENIES the write" case fails whenever the hook is fired from a copied bin dir, with or without a mutation — so `CHECK_DOMAIN_BIN` is an unreliable seam for future mutation proofs. |
| **B-18** | **chore** | A lead cannot correct its own `digest.md` in place, so a digest failing the validator's file-side check can only be fixed by opening a second run directory and leaving a superseded copy behind. Two directories exist for the SIMPLIFY cycle for this reason. |
| **B-19** | **chore** | `#551`'s orchestrator-inferring-run-verdicts-from-disk consequence is now the ONLY unclosed one, and no entry owns closing it. Accepted residual or backlog? |
| **B-20** | **chore** | `quarantines()` in `plan-sign-gate.py` worsened inside its already-failing complexity band (cyclomatic 14→15, cognitive 27→28, ABC 35.0→36.2). Crosses no bar and does not gate — invisible one delta at a time, which is the point of recording it. |
| **B-21** | **chore** | Test-first compliance is **structurally unauditable** for the six `main-session-direct` tasks: that lane writes no receipt and each task landed as one commit, so commit order cannot show test-before-code. Absence of evidence, not evidence of absence — but the gate cannot tell them apart. Does the lane need a recorded-RED convention? |

---

## §7 — Budget, honestly

`cycles_used: 13` of `max_total_cycles: 20`. Four cycles were spent on rework and every one bought
something: the qa gate's two remediable findings, and the panel's two high defects.

**`len(runs)` is 26 against `max_total_runs` of 20, and I am naming the crossing rather than burying
it.** It is informational and it never stops a branch. My read: the runs earn their place. The last
five closed a named defect measured at source, two of them found gates that could not report red,
and one found a regression that would have shipped. The count also **under-reports** — the six
main-session-direct segments are not runs and never appear in `runs:`, so the real total is higher
and the ratio is not comparable to a squad-only feature.
