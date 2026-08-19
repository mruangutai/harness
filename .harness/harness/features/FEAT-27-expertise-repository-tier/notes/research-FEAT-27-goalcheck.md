# Goal-check — FEAT-27 expertise repository tier — graded at 9b929de

**All eleven criteria met.** Every one graded by its own declared method, at `HEAD == 9b929de`
with `git diff --stat` empty over every graded surface. I agree with qa's verdict on all eleven and
disagree with none, but nine of the eleven rest on a measurement I took myself rather than on qa's.
Both suites green under my own run (`unit` rc=0, `integration` rc=0, zero `^FAIL ` lines) — recorded
as context, never as evidence for a criterion.

## Independence, labelled

Three proofs are mine and were not run by qa: the **pre-change hook** re-run (SC-01, SC-09), the
**budget-collapse mutant** on `check-expertise.sh` (SC-05), and my own reconstruction of SC-03's
thirty-two assertions from T-04's commit diff rather than from T-04's `verify:` block. Two are
re-derivations of qa's method with my own hands on the command (SC-11's guard mutant, SC-02's
sixteen resolves). Only SC-06 rests substantially on re-running cases qa ran.

## Per criterion

| SC | Verdict | Method actually used | Evidence |
|---|---|---|---|
| 01 | met | automated, independent | `case1` asserts the segment-named header + `REPO BODY TEXT` (`test-inject-expertise.py:88-101`); I ran the whole suite against `ada8e99`'s hook — **case1 FAILS there**, 12/19. Plus production: the real hook on the real tree emitted `## Your Expertise — harness repository (repository tier)` with the migrated body |
| 02 | met | automated, independent | Sixteen separate `check-domain.sh --resolve` calls on `.harness/harness/expertise/<agent>.md`, agents derived from `team-config.yaml` (orchestrator + 3 leads + 12 members). Sixteen outputs, each exactly the agent's own name, rc 0 — `harness-frontend-dev` included, which holds a grant with no craft file. Negative control: a bogus name resolved `NOBODY`. Baseline at `ada8e99` derived at source: zero `.harness/*/expertise/` grants existed |
| 03 | met | inspection (declared), independent | Thirty-two assertions, one per entry per direction, built from the removed-lines of `532806c` rather than from the plan. Eleven movers: body **verbatim** in the destination and absent from craft. Five stayers: present in craft, absent from the repository tier (pm has no repository file at all). 0 failures |
| 04 | met | automated, independent | `run_extra case1` both directions + 10 token classes; and I observed the real advisory format, which names file, line, entry id and quoted token: `.harness/expertise/harness-backend-dev.md:75: G-08 names 'team-config' …`, rc 0 |
| 05 | met | automated, independent (mutation) | `case5`/`case6` pass at HEAD; against a scratchpad copy with `REPO_LINE_BUDGET = 40` → `150` (one-line diff shown), **exactly those two cases FAIL**, 20/22. The split is enforced by path, not by one constant |
| 06 | met | automated, re-run | `case3` (no tier → rc 0, the string `repository` absent from the context entirely) + `case5a`/`case5b` (missing / unparseable payload → rc 0, stderr empty). `case3` also fails against the pre-change hook, so it is not vacuous |
| 07 | met | automated, independent | I ran `check-expertise.sh` over each tier: **fifteen** craft files each named `OK`, rc 0 (six `ADVISORY` lines, by design); **six** repository files each named `OK`, rc 0. Each file named individually, not a bare directory exit code |
| 08 | met | inspection (declared), independent | Four files, one at a time. `SPEC.md:812,959` and `harness-distill/SKILL.md:45-46` use the prose placeholder; `harness-curate/SKILL.md:19-21,43-45` uses the literal glob inside runnable commands — exactly the admissible split. Zero hits of `expertise/<repo>` or `**/expertise` in any of the four. **One judgement call, stated:** `.harness/README.md:18-19` renders both paths relative (`expertise/<agent>.md`, `<repo>/expertise/<agent>.md`) because that table is rooted at `.harness/` — a third *rendering*, but not either named forbidden form, and it resolves correctly in the document's own coordinates |
| 09 | met | automated, independent | `case7a` asserts `[TRUNCATED at 40 lines` and the absence of 150; it **FAILS against the pre-change hook**, so it discriminates |
| 10 | met | automated, independent (production) | Real hook, real tree, `harness-documentor`: precedence stated once in words, positioned before the repository header; the segment-name warning present; `authoritative on conflict` absent; headers label scope only; stderr 0 bytes |
| 11 | met | automated, mutation-proven by me | Scratchpad copy with line 69 `[ -r "$f" ] || continue` deleted (diff shows exactly `69d68`). Suite run against the mutant: **18/19, `case13` the sole FAIL**, `checks=[True,True,True,False,False]`, stderr carrying `No such file or directory` and `[: : integer expected`. Mutation applied, case ran, case reddened |

## The two qa judgements I was asked to test

**SC-02 stays `met`, and qa's warning is right about a different thing.** The criterion's text is a
statement about what `--resolve` prints today; I ran it sixteen times and it prints it. That is an
automated, discriminating measurement — remove a grant and it reddens. What is *not* true is the
declared `evidence: integration`: `test-check-domain.py` carries zero repository-tier cases (its only
expertise cases are craft, `:36-37` and `:51-52`; `:656-660` is a synthetic fixture root). So the
feature's core new grant is **correct today and pinned by nothing tomorrow**. That is a coverage gap,
not an unmet criterion — an SC grades the delivered state, not the regression suite. It is the first
follow-up I would fund (qa's Q4), and it does not overturn my E1 ruling.

**SC-08's inspection is compliance, not a shortfall.** `verify: inspection` is the criterion's own
declared method. "Two of four files rest on inspection alone" describes the method working as
written. A standing grep for the forbidden third form across all four would still be cheap insurance
and is worth a follow-up, but its absence takes nothing off SC-08.

## The goal, beyond the criteria

**Closed.** The BRIEF's problem was sixteen agents taught a rule they could not execute: all sixteen
can now write their repository file (sixteen resolves), and a real spawn against the real tree
receives a labelled repository block — I watched it happen, not a fixture. **DC-3 now stands on
something**: eleven repository-specific entries live in the tier and are injected, so "agents carry
kaya's expertise" has a working mechanism rather than a documented one.

**Two things the criteria do not cover, and neither is a delivery gap.** E1 gap (b), the suffix
rule's traversal case, still has zero discriminating coverage — no SC reaches it. And qa's six-item
census of assertions that cannot redden sits entirely outside every SC's text. Both are
regression-pinning debt on a shipped-correct tree.

## Open questions

- Q1 (carried from qa, blocking, not mine to settle): whether `plan.yaml` was re-signed after T-07
  was added. Nothing in this goal-check bears on it either way.
- Q2 (mine, non-blocking): SC-02's declared `evidence: integration` names a suite with no case for
  it. The criterion is met; the declaration is aspirational. Worth one standing case looping the
  sixteen agents before the next manifest edit.
