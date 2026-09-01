# Review — harness-code-reviewer (plan-panel, scope reader) — FEAT-50-run-artifact-integrity

**Bound to:** `plan:.harness/harness/features/FEAT-50-run-artifact-integrity/plan.yaml` (no `review_sha`, DEC-207).

**BLUF: FAIL.** Two of the seven mechanical/routing checks the goal-check and two fix rounds already
verified are sound (REQ tracing, `depends_on` topology, no orphan REQs — confirmed, no findings). But
the "reaches every route / survives its own predecessor" hunt turns up four real gaps the prior two
rounds missed, two of them `high`: (1) T-02 adds new cases to `test-validate-digest.py` without
touching a **pre-existing conflicting case** the new D-01 logic directly contradicts — the file will
not pass its own `verify:` as specified; (2) T-03's worktree-binding narrows `check-domain.sh` only —
its documented twin `bash-write-guard.sh` keeps today's unbound behavior, and that file's own header
comment proves this exact bypass shape (`perl -pi` routing around a Write-side denial) already
happened once in this repo's history (DEC-151); (3) a **blocking** open question from two prior
review rounds — whether the platform can legitimately hand `validate-digest.py` an empty
`last_assistant_message` on a tool-only final turn — never made it into `BRIEF.md`'s `Verification
gaps` or `plan.yaml`; the operator signs without seeing it; (4) D-05's literal-prefix comparison is
plausibly narrower than the "revise within one run" case it names as protected.

## Findings

### F-PP1 · high · T-01, T-02, D-01
`test-validate-digest.py:738-739` already carries `hook_case("pass-through: empty
last_assistant_message passes with a stated reason", "harness-qa", "", 0, mentions="no final
message")` — the literal payload `{"agent_type": "harness-qa", "last_assistant_message": ""}`
expecting **exit 0**. Under T-01's new discrimination (a present, empty-after-`.strip()` string is
the *persona's* violation → exit 2), this exact payload now belongs in state 2 and must exit 2. T-02's
intent ("Add FOUR cases…") never mentions this case; nothing in the plan instructs updating or
removing it. T-02's own `verify:` runs `python3 .claude/skills/harness/bin/test-validate-digest.py`
first — the whole file, this case included — so the task as specified cannot pass its own gate.
Consequence: whoever executes T-02 (main-session-direct, no independent second review of the fix)
must invent, unreviewed, how to resolve the contradiction — silently deleting a labeled "deliberate
pass-through (DEC-122)" case, changing its wording, or something else — and the plan gives no
guidance on which. Verified: line numbers checked directly against
`.claude/skills/harness/bin/test-validate-digest.py`; no prior round (goal-check or either fix round)
mentions this case.

### F-PP2 · high · T-03, D-03, D-04, REQ-03
T-03's worktree-binding check is added only to `check-domain.sh`'s `domain_check()` (allow branch
`:835-841`, shared branch `:843-848` — anchors verified against source, exact). Governed-agent Bash
writes take a **separate** code path: `bash-write-guard.sh` calls its own
`harness_boundary.classify(ap, root, mine, shared, "bash-write-guard")` (`bash-write-guard.sh:720`)
with its own allow/shared handling, and T-03's `files:` list names only `check-domain.sh` — the new
narrowing is never threaded there. `bash-write-guard.sh`'s own header states the exact bypass shape
this leaves open: *"Field incident: qa, denied a source edit by check-domain, made the same edit via
`perl -pi` from Bash"* (DEC-151) — the codebase already has one proven instance of an agent routing
around a Write-side denial through Bash. A governed agent denied by T-03's new refusal on `Write` can
`cat > <main-checkout-path>` or `perl -pi` the same feature artifact and bash-write-guard's domain
check allows it exactly as before, because the worktree-binding narrowing lives nowhere on that route.
REQ-03's text carries no tool qualifier ("A governed agent's write of a feature artifact lands in the
checkout…") — unlike REQ-04, which explicitly and honestly scopes itself to `Write`. No SC tests the
Bash route (SC-03/SC-04 fire `tool_name: Write` only), and no `Verification gaps` bullet discloses it,
though the file directly above (`check-domain.sh`'s own recent history, referenced from
`bash-write-guard.sh:306-309`, *"Two guards, one rule, and I changed one of them"*) shows this project's
own convention is to disclose exactly this kind of twin-guard divergence when it is deliberate. Here
it reads as unconsidered, not disclosed-and-accepted.

### F-PP3 · med · T-01, D-01, D-02
A **blocking** open question was raised in the eng review segment and carried unchanged into the
product segment (`runs/2026-08-31-1-product/digest.md` "Open questions riding up… Q1, blocking":
*"Whether the host's `SubagentStop` payload can set `last_assistant_message` to an empty string on a
tool-only final turn. D-01's exit-2 direction rests on the answer being no; not answerable inside this
repository."*) and repeated in `notes/research-2026-08-31-review-application.md:76-78`. Neither
`BRIEF.md` nor `plan.yaml` mentions it — confirmed by grep, zero hits for the discriminating phrases in
either file. If the answer is yes, T-01 will exit 2 and re-prompt a persona for a platform artifact,
not a contract violation — exactly the confusion D-02 exists to prevent, just pointed at the persona
instead of the platform. Blast radius is bounded by the pre-existing `stop_hook_active` passthrough
(one spurious re-prompt, not a permanent wedge), which is why this is `med` and not `high`, but a
question two review tiers marked blocking should not have evaporated by the time the operator is
asked to sign.

### F-PP4 · med · T-04, T-05, D-05
D-05's rule is a literal byte-for-byte prefix test: "unless the existing text is a prefix of the
payload." `harness-team/SKILL.md:207-208` establishes that a lead writes `digest.md` **once**, after
`status: complete`, so the "revising own digest within one run" case D-05 names as the legitimate
exemption is most plausibly a validation-triggered retry: `validate-digest.py`'s own file check
(DEC-156) or the in-message `SubagentStop` check rejects a malformed first attempt (e.g. a missing
`members:` or `open_questions:` key, both of which sit mid-block in the DIGEST schema, not at the
file's tail) and the lead re-`Write`s a corrected `digest.md`. A structural fix to a mid-block field is
not a suffix-only extension of the rejected text, so the corrected write is not a literal prefix
continuation and T-04 refuses it — telling the lead, wrongly, to "write this run's digest into a run
directory of its own," which is not the actual problem. T-05's own `digest-append` case (case 6) only
exercises a payload that "begins with the existing text verbatim and adds more" — pure suffix append —
so this shape is untested in either direction. I cannot confirm from this repository alone that a
real validation-retry ever inserts a mid-block fix rather than appending (as with F-PP3's Q1, this
needs platform/agent-behavior knowledge outside the repo), so `med` rather than `high`.

## Not re-raised
Checked and dismissed as already closed by the two prior rounds / goal-check, with anchors verified
directly against source at the cited lines: F-03 (T-03 re-anchored to `:835-841`/`:843-848`, no
`NameError`), F-04 (disclosed in `Verification gaps`), F-05 (per-pid mutant names present at D-07,
T-02 case 4, T-05 case 7), F-06 (shared branch now covered), F-08 (T-05 cases 5-7 specify no
`agent_type`), F-11 (all three `targets` sites — `:1369`, `:1381`, `:1505` — correctly named).

## Not findings
- Orphan `REQ` ids: none — all 7 REQ trace to at least one task, all `traces:` resolve to real REQs.
- `depends_on` topology: valid DAG (`T-08→T-03→T-04→T-05`, `T-01→T-02`, `T-07` closes over all eight);
  no cycle, no forward reference.
- No `verify:` block asserts something a predecessor task's own change deletes.

```yaml
VERDICT: FAIL
DIGEST:
  headline: >-
    Two high findings the prior two rounds missed: T-02's own verify cannot pass against a
    pre-existing conflicting test case, and T-03's worktree binding never reaches bash-write-guard.sh
    — the exact Bash-bypass shape this repo already fixed once for a different check (DEC-151).
  severity_max: high
  findings: 4
  must_fix:
    - "F-PP1 (T-01/T-02, D-01): test-validate-digest.py:738-739's pre-existing pass-through case contradicts the new discrimination and is not addressed by any task; T-02 cannot pass its own verify as specified."
    - "F-PP2 (T-03, D-03/D-04, REQ-03): the worktree-binding narrowing is added to check-domain.sh only; bash-write-guard.sh's separate classify() call keeps today's unbound behavior for Bash writes, undisclosed."
  spec_violations:
    - { kind: omission, path: .claude/skills/harness/bin/test-validate-digest.py, ref: D-01 }
    - { kind: omission, path: .claude/skills/harness/bin/bash-write-guard.sh, ref: REQ-03 }
  reviewed: "plan:.harness/harness/features/FEAT-50-run-artifact-integrity/plan.yaml"
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "Can the SubagentStop payload legitimately carry an empty last_assistant_message on a tool-only final turn? (Inherited blocking question from two prior review segments, never carried into BRIEF.md or plan.yaml — see F-PP3.)", blocking: true }
    - { id: Q2, question: "Does a validation-triggered digest retry ever produce a non-suffix (mid-block) revision, or is it always append-only in practice? (F-PP4 — cannot confirm from this repo alone.)", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-50-run-artifact-integrity/notes/review-harness-code-reviewer-planpanel-c0.md
```
