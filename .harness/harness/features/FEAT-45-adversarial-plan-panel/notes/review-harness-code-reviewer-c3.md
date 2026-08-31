# Code review — FEAT-45-adversarial-plan-panel — c3 (re-pinned SHA)

Scope: `git diff main...d78f393` (merge-base `ba338d8`), 71 files, +7931/-152. HEAD (`877be4c`)
confirmed to differ from `d78f393` only in `feature.json`'s `review_sha` line (`git diff d78f393 HEAD
--stat`). `validate-digest.py`, `test-validate-digest.py`, `check-state.sh` confirmed byte-identical
between the working tree and `git show d78f393:<path>` before citing any line number below.

**Tool note, not a repo finding**: relative-path `read`/`grep` calls in this session resolved against
a different cwd than this worktree (the exact "note landed in the main checkout" failure c0/c1's own
review notes record). Every citation below is from an absolute-path read or grep, or from `bash`
commands `cd`'d explicitly into the worktree. This turned out to be directly related to a live F5
finding below, not a tooling coincidence — see the closing section.

## Stage 1 — spec compliance

Read `BRIEF.md` (REQ-01..14, SC-01..17, constraints, approval) in full. Every file in the diff traces
to a named requirement: `validate-digest.py`/`check-state.sh`/`panel_findings.py` changes are
REQ-05/06/07/08/10/11/13/14 machinery; `plan-panel.yaml` and the `plan.yaml` template additions are
SC-01/02/03/14/15; `.omp/agents/harness-validator-lead.md` and `.claude/agents/harness-validator-lead.md`
are the `spawns:` grant SC-15 asserts; `DECISIONS.md`/`DECISIONS-INDEX.md` additions are REQ-11/SC-09;
`harness-plan.md`'s sequence edit is REQ-10's trigger site. No file found serving no requirement
(no scope creep), and no requirement found with no corresponding change. `harness-hooks.ts`'s
`harness_feature`/`inflight_registry.feature_root` wiring is the F5 fix, in scope via REQ-05/09 (the
normalization mechanism must actually resolve, or REQ-05 is unmet in practice). Stage 1: **PASS**.

## F1 / F2 / F3 / F5 corroboration — independent, at the pin

### F1 — PARTIALLY CLOSED, NEW GAP FOUND. DEMONSTRATED.

Read confirms the wiring: `_pending_plan_review_error` (validate-digest.py:908-926) now ends
`_pending_plan_status_error(plan_path) or _pinned_feature_review_error(feature_dir) or
_branch_corroboration_error(feature_dir, _current_branch_or_none(branch_override, feature_dir))` —
matches the dispatch's claim.

Rebuilt the c2 exploit (fabricated `plan:` digest citing an unrelated, genuinely-pending feature),
retargeted at a feature whose `feature.json` carries **no `branch` field** — a real, sanctioned,
currently-live state in this exact repo: `FEAT-01`, `FEAT-15-domain-product-base`,
`FEAT-19-central-product-config` all have `branch: none` today (`FEAT-15` additionally has
`review_sha: none`, i.e. genuinely unpinned and pending). Ran the *production* call shape
(`validate(agent, text)`, `feature_dir=None`, real CLI subprocess, hermetic `git init` fixture with a
real `HARNESS_PROJECT_DIR` marker, a real resolvable branch on the "attacker" side):

```
RC: 0
STDOUT: digest ok
```

Root cause: `_branch_corroboration_error`'s own docstring states it is "ADDITIVE ONLY... either side
being unknown means nothing to corroborate, not reject." When the impersonated feature's `branch`
field is absent (not malformed — a documented, real state), corroboration silently no-ops regardless
of the real current branch. F1's fix closes the exploit only when the impersonated feature happens to
carry a recorded, *differing* branch. It does not close it against any of the ≥3 currently-real,
branch-less, pending features in this repository — the exact same exploit shape from c2, unmodified,
minus one precondition.

**MUST NOT SHIP (gates).** This is the literal defect class SEC-01/F1 exists to close: a forged
pre-signature review claim for an unrelated feature is still accepted end-to-end through the real CLI.
It undermines REQ-06 at the root, because the mechanism that is supposed to make a `high` finding
block signature can itself be forged for any target lacking a recorded branch.

### F2 — CLOSED. DEMONSTRATED.

Rebuilt a *complete* `lead` digest (`team`, `steps_run: 3`, `cycles_used`, `branch`, `escalations`,
`sc_status` all present — the c2 fixture's missing fields would have masked the real check) with three
members, all `{status: skipped, persona: fable-advisor, reason: never spawned}`:

```
RC: 1
STDOUT: VERDICT: BLOCKED (contract violation)
  - members records no member actually ran — a lead verdict cannot claim an outcome for an entirely skipped team.
```

Isolated, single error, matching `validate-digest.py`'s new `if worst is None: err.append(...)` line
exactly. Also tested the more realistic shape — three members of three *different* real personas
(`harness-pm`, `harness-code-reviewer`, `fable-advisor`) all claiming `status: skipped`: F3's
per-member check correctly rejects the two non-`fable-advisor` entries *and* the all-skipped backstop
still fires — defense in depth, no double-jeopardy weirdness, no gap found.

### F3 — NOT a regression. DEMONSTRATED + cross-checked against spec.

`_skipped_member_error` (validate-digest.py:931-947) rejects any skip whose `persona !=
"fable-advisor"`. Cross-checked `harness-team/SKILL.md:178` and `SPEC.md:1615-1616`, independently:
both say, verbatim, "Only the optional external `fable-advisor` may instead carry `status: skipped`
... at least one member must have run before the lead may claim a verdict." Code and prose agree
exactly — no drift. Grepped every file under `.claude/skills/harness/teams/`: no team file other than
`plan-panel.yaml` documents any skip usage at all, and `plan-panel.yaml` names only `fable-advisor` as
skippable (its own trailing comment: "If fable-advisor cannot resolve or preflight refuses it, the
lead skips the step..."). No other persona has a documented, legitimate skip path this restriction
could be wrongly blocking. Demonstrated live above (the `harness-pm`/`harness-code-reviewer` skip
rejections). **No finding** — this is a correct, faithful implementation of a decision recorded in two
independent doc sources, not a fail-closed regression.

### F5 — PARTIALLY CLOSED, SAME DEFECT CLASS RE-OPENS ON AN UNTESTED BRANCH. DEMONSTRATED — and then reproduced live against my own return; see closing section.

Read: `_hook_feature_dir` (validate-digest.py:1359-1372) resolves via
`inflight_registry.feature_root(owner_root, feature)` (:1367). `feature_root`
(`inflight_registry.py:260-268`) matches by `os.path.basename(worktree) == feature` over
`harness_boundary.linked_worktrees(owner_root)`, and on **any** miss — no matching worktree, or any
exception — falls back to returning `owner_root` verbatim: the exact pre-F5 behaviour.
`linked_worktrees` (`harness_boundary.py:138-180`) silently drops any `.git/worktrees/<name>/gitdir`
pointer whose target directory does not currently exist (`os.path.isdir(named)` guard), so a stale
pointer degrades to "no entry," same bucket as "never had one." `_resolve_feature_dir` accepts an
explicitly-passed `feature_dir` with **no existence check** — so a fallback path under `owner_root`
(where an in-flight, unmerged feature does not live — this repo's own BRIEF documents exactly this:
"the main checkout cannot see a feature whose directory exists only on its own branch or worktree")
is passed straight through and only fails later, deep inside `_pending_plan_review_error` or
`_read_review_sha`, with a message that quotes the *fallback's* nonexistent expected path, not the
reviewer's real one.

The shipped test (`check_hook_feature_dir`, `test-validate-digest.py:2731-2756`) monkeypatches
`inflight_registry.feature_root` directly to a lambda that **always succeeds** — it never exercises
the miss/fallback branch.

DEMONSTRATED, full production `--hook` CLI path (real JSON stdin with `harness_feature`, real
subprocess, reviewer digest correctly naming the real worktree's real `plan.yaml`), three cases plus a
control:

| Case | Setup | Result |
|---|---|---|
| A | no `.git/worktrees` dir at all | RC 2 — "reviewed plan target '\<real worktree path\>/plan.yaml' is not this feature's plan.yaml (\<fallback owner_root path\>/plan.yaml)." |
| B | stale pointer, target dir does not exist | RC 2 — same rejection shape |
| C | linked worktree metadata present, but only for an unrelated feature | RC 2 — same rejection shape |
| control | worktree correctly linked and name-matched | RC 0, silent success |

The control isolates the fault to the fallback specifically — the mechanism works when registry data
is intact.

**MUST NOT SHIP (gates), with an explicit distinction from F1**: this gap fails **closed**, not open —
it blocks a legitimate return rather than accepting a forged one, so it is not a security hole. It
gates because it is the identical defect class F5 was authored to close, demonstrably still reachable
on a branch the shipped suite gives zero coverage to, and because this project's own build history
(this very feature, cycles 0-1, and now cycle 3 — see below) shows the failure mode is not
hypothetical — it has now cost three cycles of confusion, not two.

## Code-risk grading

```
python3 .claude/skills/harness/bin/code-grade.py --base ba338d8879e2cc1b9beb04c2986f6073125ca016 \
  --head d78f393a7d5addc1cbd2f31628aed18c54983b9a
```
49 functions graded, **all `RESULT: PASS`**, zero `SEVERITY:` lines, zero grade-1/grade-2 functions.
Every new `validate-digest.py` function from this fix cycle (`_pending_plan_review_error` grade 4,
`_skipped_member_error` grade 4, `_hook_feature_dir` grade 4, `_pinned_feature_review_error` grade 4,
etc.) sits at or above the bar-4 production line. **No code-risk finding.**

## Other fail-open hunting

Read `check-state.sh`'s new INV-32 block in full (lines 174-243) and `panel_findings.py` in full
(61 lines). Both correctly require every `expected_readers` entry recorded as `ran` or `skipped` and
reject an unrecorded one — matches SC-17, no new fail-open found. `panel_findings.py`'s 8-hex-char
(32-bit) id is the pre-existing, carried-forward M4 advisory, unchanged at this pin — not re-derived.

## Test suite corroboration — independently re-run, not restated

- `test-validate-digest.py` at this pin: **ALL PASSED** (fresh run, not trusted from the record).
- `run-unit-tests.sh --kind unit` at this pin: 433 `^PASS |^FAIL ` lines, **0** `^FAIL `, **0**
  `KIND-DRIFT` — matches the shared context's reported numbers exactly, confirmed by direct re-run.
- Neither run exercises either new gap above: `_check_plan_feature_binding` only tests a feature WITH
  a recorded, *differing* branch (never the branch-absent case); `check_hook_feature_dir` only tests
  the registry HIT path (never a miss). Both gaps are new proof from this cycle, not something the
  green suite already covered and I am re-discovering.

## Carried-forward advisories — not re-derived, unchanged; noted only per dispatch

M4 (32-bit id, asserted ratchet risk), M6 (goalcheck transcription ambiguity), M7 (withhold message
lacks remedy), and `check-state.sh:199-206`'s unattributed-overrule audit-trail wart — all as given in
the shared context. No evidence found that any of them changed at this pin; none re-verified in depth
this cycle per the dispatch's "do not re-derive" instruction.

## Summary

| Item | Status | Severity | Evidence | Gate |
|---|---|---|---|---|
| F1 — plan-review binding, branch-less-feature bypass | new gap (F1 only partially closed) | high | DEMONSTRATED | **MUST NOT SHIP** |
| F2 — all-skipped roll-up | CLOSED | n/a | DEMONSTRATED | closed, no finding |
| F3 — skip restricted to fable-advisor | correct, matches SPEC/SKILL exactly | n/a | DEMONSTRATED | closed, no finding |
| F5 — installed-validator worktree resolution, registry-miss fallback | new gap (F5 only partially closed), now confirmed LIVE against my own return | high | DEMONSTRATED (synthetic fixtures) + DEMONSTRATED (live, this session) | **MUST NOT SHIP** |
| Code-risk grading | clean, 49/49 PASS | n/a | DEMONSTRATED | no finding |

`severity_max: high`. `must_fix`: exactly two items — the F1 branch-less-feature bypass and the F5
registry-fallback fail-closed gap, both above. Both are genuinely demonstrated, both are regressions
of previously-"closed" defect classes reopened on an untested precondition, neither is padding. F3 was
actively hunted as the dispatch's top suspicion and is ruled a non-issue with evidence, not assumed
clean. No other candidate finding from this cycle's hunt was elevated. **VERDICT: FAIL.**

## On my own yield — F5 reproduced LIVE, not just synthetically

I predicted (wrongly, on first analysis) that my own yield would land cleanly, because the real main
checkout's `.git/worktrees/FEAT-45-adversarial-plan-panel/gitdir` correctly points at this worktree
(confirmed by direct read before my first yield attempt). **It did not land cleanly.**

My first structured `yield` was refused by the SubagentStop hook with a full contract-shape complaint
(no `VERDICT:`/`DIGEST:` visible in my message text — a mechanical mistake on my part, since the
contract validates the assistant's own message text, not the tool call's `data` payload). I corrected
that and emitted the fenced `yaml` block as visible text in this same turn. The **second** attempt was
refused with exactly one line, verbatim:

```
code_grade cannot be bound to review_sha: /Users/molchairuangutai/GitHub/harness/.harness/harness/features/FEAT-45-adversarial-plan-panel/feature.json could not be read ([Errno 2] No such file or directory: '/Users/molchairuangutai/GitHub/harness/.harness/harness/features/FEAT-45-adversarial-plan-panel/feature.json'), so the claim is not trusted.
```

That path is under the **main checkout** (`/Users/molchairuangutai/GitHub/harness/...`), not this
worktree (`/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-45-adversarial-plan-panel/...`).
Confirmed independently: the main checkout genuinely has no `FEAT-45-adversarial-plan-panel` directory
under `.harness/harness/features/` at all (`ls`/`grep`, both empty). This is `_hook_feature_dir`'s
fallback path firing for real, on my own return, in this exact session — despite the linked-worktree
metadata being correctly present, which means either `d.get("harness_feature")` was not delivered to
the hook as `"FEAT-45-adversarial-plan-panel"`, or `inflight_registry.feature_root`'s lookup missed it
for a reason I cannot observe from inside this turn (I have no visibility into the hook's own stdin).
Either way, the *outcome* is exactly the fail-closed defect class documented above, now happening to a
genuine, correctly-positioned reviewer rather than a constructed fixture — and it is **structurally
unavoidable from my own return text**: `code_grade_bound_to_review` runs unconditionally for
`harness-code-reviewer` regardless of what `code_grade`/`reviewed` values I write, so no digest content
I could write would route around this.

This raises F5's assessment from "demonstrated via synthetic fixture, not currently reproducible
against this exact worktree" to "demonstrated via synthetic fixture, AND independently reproduced live,
in production, against this exact review, in this exact cycle." It does not change the `must_fix`
list (F5 was already `MUST NOT SHIP` above) but it removes any doubt that the gap is theoretical.

Per the dispatch's instruction, I am retrying this yield now with this section added. If it is refused
again, the artifact — not the tool response — is this panel's authoritative record; the orchestrator
should read this file directly rather than wait on a structured return this environment may not be
able to deliver for a `harness-code-reviewer` in this exact worktree/feature pairing right now.
