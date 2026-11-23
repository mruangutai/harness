# Plan sign-off — delegated ruling — FEAT-2452 — 2026-11-23

Authority: the operator's delegation ("start feature D. same rules, defer to fable-advisor"). Ruled by `fable-advisor` (`AdvisorD2Signoff`) at worktree `425c7218`. The full ruling follows verbatim.

# Sign-off ruling — FEAT-2452-gh-one-transport (AdvisorD2Signoff)

## 1. Fidelity to AdvisorD1Grill — **faithful, no drift found**

Verified item by item against the plan text, not the digests' claims:

- **Transport not command logic (Q1):** T-01 `GhResult`/`try_gh`/`launch_gh`, run_gh as raising adapter; T-02 explicitly preserves flows/argv/policies. ✓
- **Enforcement excluded (Q2):** no gate file in any task; DEC-144 keep row; BRIEF BLOCKS DEC-100/144. ✓
- **FACTORY_GH only, GH_SYNC_GH + D-11 deleted (Q3/#893):** I censused the worktree — 19 files carry `GH_SYNC_GH`; all 19 are inside the 29-file task-owned union that T-05's verify mechanically asserts is free of `GH_SYNC_GH` and `\bD-11\b`. The absence clause has a real mechanical check, not just prose. ✓
- **issue://, pr://, run_watch rejected on contract grounds:** D-01 + BRIEF constraint, verbatim the grilling's reasoning. ✓
- **Five fixes, (e) first to cut:** (a)(b)→T-04 with the stricter status-zero/404 classification (an improvement, not drift); (c)→T-02+T-03 with one pinned matcher; (d)→T-02; (e)→T-02 trimmed to the exact create_ref conjunction, two regressions, cut lever spelled in the intent. ✓
- **Policy table in references/github-mirror.md + factory_cli exit-2 fix:** T-05; the verify assertion `'nothing mutated); exit 3' not in cli` correctly targets the exit-2 false claim while preserving the distinct exit-3 lost-race claim (confirmed against factory_cli.py:10-14). ✓
- **#893/#1542/#13 folded**, provenance kept out of the living reference (PF-3cf5ab12). ✓
- **Enforcement ticket a named deliverable:** SC-07, real-issue readback JSON, signed verbatim body. ✓
- **Deadlines recorded non-goal:** BRIEF out-of-scope + `'subprocess deadlines'` asserted in the T-05 verify vocabulary. ✓
- **No verify gap found.** Every SC has a tracing task whose verify can prove it; SC-06's one non-mechanical clause ("no enforcement executor changed in the pinned diff") is handled by condition C4 below.

One realization beyond the grilling's letter, accepted: the label-exists idempotent acceptance in (c). Strict return-code checking without it would turn every pre-existing label into a mirror SKIP — a behavior regression the grilling's "keeping each caller's colours" forbids. Necessary, pinned once, cited verbatim by T-03. The matcher text rests on PM's reading of gh's create.go `[unverified against the live gh binary]` — covered by condition C3.

## 2. OQ-1 (DEC-138 stale clause) — **(b) amend**

Reason: I verified DECISIONS.md:3131-3141 — "gh_bin() live in exactly one place, gh_issues.py … each caller keeps its own runner" is a present-tense factual claim this feature falsifies outright; my grilling's no-amendment ruling carried an explicit escape for wording the change would contradict, and a DECISIONS.md the feature makes literally false fails the honest record regardless of which clause triggers it.

Exact conditions on the amendment:
- Add one DEC-138 **amend** row (replacing only the runner-clause keep row; the best-effort-policy keep row stays keep) and give `.harness/harness/docs/DECISIONS.md` + index regen to **T-05** (post-T-04, so the text matches the code state when written).
- Amendment scope is minimal: rewrite only the "Shared code, and migration scope" implementation sentences (gh_bin location/existence; each-caller-runner) to point at factory_gh as the shared transport with failure policy kept at the caller. The write-only regression guard ("gh-sync imports only internal_id_args/attach_sub_issue_args, no parent_args/blocked_by_args call") and all policy clauses stay untouched. DEC-146 untouched.
- Applied by pm in one more product apply run before signature; plan-merge check exit 0; plan remains `pending` (no APPROVAL-RESET applies). The T-05 verify's `len(owned) == 29` is unaffected (DECISIONS.md is under `.harness/`, excluded from that set) — no verify rewrite needed.

## 3. OQ-3 (lost apply stdout) — **accept the surviving capture; no rerun**

Reason: the receipt's function is recoverable without it — the applied plan.yaml is itself the diffable output, every surviving stdout line is visible at line-start (so no `APPROVAL-RESET:` could hide), `exit=0`/`APPLIED` and the stderr guard block survive, and two later independent plan-merge checks (30 then 31 anchors, 0 failures) validated the resulting file. Rerunning the writer to regenerate a receipt would be re-audit theater.
Required: record this acceptance in the answers note, and **C6** below going forward.

## 4. Approval and rework

**Approved, with the binding conditions below.** **Rework: 2 rounds / 90 minutes** (C's formula: 3 tasks per round, floor 2, 45 min per round; 5 tasks → 2 rounds). The OQ-1 product apply run does not count against rework rounds.

**Conditions (binding):**
- **C1 — DEC-138 amend before signature**, exactly as scoped in §2. Signature waits on its apply run's check exiting 0.
- **C2 — Confinement-first evidence.** For each of T-02/T-03/T-04, `tests/offline_gh_support.py` confinement lands and its red run against the *old* code is captured to `notes/` before any production edit in that task (makes PF-3bfe1e6f's red run auditable on a credentialled host).
- **C3 — Early host tripwire (C-style).** When T-02 is green, Main runs once on the credentialled host `gh label create` for an already-existing label without `--force` (mutates nothing) and confirms stderr matches the pinned conjunction ("label with name" + "already exists"). Mismatch → stop, return to fable-advisor before starting T-03. This is the only live assumption both T-02 and T-03 build on.
- **C4 — Enforcement diff guard.** At the review pin, `git diff --name-only <base>..review_sha` recorded in `notes/` showing no change to branch-create-gate.py, merge-gate.py, check_state/ctx.py, or any GH_BIN site — mechanizing SC-06's inspection clause.
- **C5 — Scope levers.** The (e) cut is pre-sanctioned exactly as pinned (helper, second spelling, or a third regression needed → cut it, record in the ship record, no return required). Any other Settled-item shrink returns to fable-advisor first.
- **C6 — Receipts.** All post-signature writer/task-changing stdout tees to a file under the feature `notes/`, never `/tmp`.
- **C7 — Ordering of remote writes.** The enforcement ticket is created only after signature, verbatim signed body, readback saved; uncertain dispatch → stop and request evidenced adoption (plan already says this; now binding). The live issue-types probe receipt counts only as CAPABILITY PRESENT/ABSENT per T-05; SKIP is not evidence.

Sign as `Mike Ruangutai (delegated to fable-advisor)` once C1 lands.
## C1 clearance (AdvisorD2Signoff, follow-up at worktree c86302c7)

**Yes.** C1 is cleared and the signature may proceed. pm made two additions beyond the ruling's
letter. Both tighten C1's scope rather than widen it, and both are accepted:
- three T-05 verify assertions on the rewritten DEC-138 paragraph: it names factory_gh, has no
  `gh_bin` and no "keeps its own runner", and keeps the write-only guard;
- a DEC-205 citation in T-05's intent.

Condition: C6 means the full writer and check output must be reproduced verbatim in a `notes/`
receipt. Staging in /tmp is acceptable only when the output is reproduced that way. The
orchestrator's check counts through its quoted output, because the write guard blocked it from
teeing. C2–C7 are otherwise binding and unchanged.
