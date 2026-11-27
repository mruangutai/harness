# Signature answers — FEAT-2488-plan-merge-atomicity — 2026-11-23

Ruled by fable-advisor (AdvisorE2Signoff) under the operator's delegated approval ("start feature E. same parameters as feature D, defer to Advisor"). Signed as `Mike Ruangutai (delegated to fable-advisor)`.

**Rework ruling (DEC-226, C1): 2 rounds / 90 minutes.**

Decision: approved. Conditions C1–C6 are binding at build, and no pre-signature amendment is required. Q1: sign, because the advisor read the three cycle-2 repairs itself. Q2: accept both (b) and (c). Q3 and Q4 go to backlog.

## Full ruling (verbatim)

# Sign-off ruling — FEAT-2488-plan-merge-atomicity (AdvisorE2Signoff)

## Authority

The operator's delegation ("start feature E. same parameters as feature D, defer to Advisor"), exercised against my own grill ruling `.harness/notes/grilling-plan-merge-atomicity-e-2026-11-23.md` and D's sign-off shape (`FEAT-2452 answers-2026-11-23-signoff.md`). Everything below was verified in the worktree at HEAD `8c969b8b`, whose product tree is byte-identical to the pin `2491336e` (`git diff --stat 2491336e..HEAD` excluding `.harness/` is empty — so the SC-04/SC-05 baselines and the lanes `resolved_at` all describe the tree the build starts from).

## Gap

The orchestrator's ESCALATE leaves four open questions, of which only Q1 is structural: the scope reader's loop is spent and the three cycle-2 repairs were applied by pm but re-read by nobody. I performed that read myself, at full depth (raw task text, not digests), and verified the repairs' premises at source.

## Fidelity to the grill — faithful; two realizations beyond the letter, both accepted

Checked item by item against the plan text: scope (atomicity + DEC-199 compliance + fsync docstring + the 5 dead lines + `base_doc` tidy — all present, nothing more); all six non-goals verbatim in the BRIEF; all five SC seeds carried (SC-05's base count of 8 `check()` calls re-counted myself at `test-plan-merge.py:4663-4690,4724-4774` — 8 exactly); every task and all three lane rows main-session-direct with the DEC-174 import chain cited; plan-first ordering kept with the ledger-first reversal history preserved (verified live at `amendments.py:175-184`); lock order plan.yaml.lock → feature.json.lock, and I verified the two approval-path claims it rests on: the rework write (`approval.py:313`) lands **before** `_locked_plan_update` at `:335`, and the `signed_task_hashes` write nests inside the plan transform (`approval.py:321-331`) — so the documented order is true of every live path. No DEC amended; `decisions_affected` is keep-only, including the DEC-230 row the c1 panel added.

The two realizations beyond my grill's letter:

1. **`approval.py#_write_brief_signature` moved onto a public `harness_merge.replace_bytes`.** My grill's SC-02 zero-hit predicate was scoped from two helpers and missed this third `mkstemp`/`os.replace` site (verified: `approval.py:407,411`). The seed as I wrote it is unsatisfiable without this move; it adds no transactionality (the non-goal holds). Accepted — this is the same shape as D's label-exists realization: necessary, pinned once, ruled in by the scope reader.
2. **Recovery widened from "every acquirer of the plan lock" to every `locked_update` naming a journal member.** Justified by a real gap my grill did not name: gh-sync/factory/rework all write feature.json through `locked_update` without ever touching the plan lock, and one such write between crash and recovery would turn roll-forward into a false DIVERGED. Accepted.

## Ruling — **Approved.** Sign as delegated; conditions C1–C6 below

**No condition requires a plan amendment before signature.** D's C1 existed because the feature falsified DECISIONS.md; nothing here falsifies any DEC (all rows are keep, and I verified the two DEC-199/229 clauses become literally true rather than needing rewording). C2 below resolves the one textual conflict I found in the builder's favor at build time — the verify already forces the correct outcome mechanically.

**Rework ruling (DEC-226, recorded here as the one ruling): 2 rounds / 90 minutes**, the delegated D parameters, per my grill's Q6. Expect 1 round — two tasks, one core module plus one package. The recording of this ruling at signature does not count against the rounds.

**Conditions (binding):**

- **C1 — Rework recording.** The signature answers note carries this ruling's 2 rounds / 90 minutes verbatim, satisfying the goalcheck's OQ-1; `sign-approval` is run so the `REWORK` receipt lands in feature.json (the plumbing exists — `approval.py:313-316`).
- **C2 — approval.py docstring.** T-02 item 6 says "No other approval change", but `_write_brief_signature`'s docstring (`approval.py:402`) carries the literal string `os.replace`, which T-02's verify and SC-02 mechanically forbid in any `plan_merge` module. Ruled now so the builder doesn't stall on the contradiction: rewording that docstring (e.g. "through harness_merge.replace_bytes") **is** in scope of item 6; "no other change" means no behavioral change.
- **C3 — Red receipts before production edits** (already task text; now binding as D's C2 was): `red-t01-journal-unit.txt` and `red-t02-plan-merge-base.txt` captured before any production edit in their tasks; red-t02 run in the detached base worktree with (g) passing — that run is SC-04's baseline and SC-01's "both failure reports differing" evidence.
- **C4 — Forbidden-surface diff guard.** At the review pin, `git diff --name-only 2491336e..<review_sha>` recorded in `notes/`, showing no change to `check-plan-routes.py`, `test-check-plan-routes.py`, any `check_state/` module, or `union.py` — mechanizing the BRIEF's "Left alone" constraints. (`canonical-reader-classification.json` appearing is expected: T-01's one row.)
- **C5 — Scope levers.** Message/name wording inside the pinned shapes is the builder's. Any new journal surface — a schema field, a third outcome class, an added fsync, a second recovery entry point — or any Settled-item shrink returns to fable-advisor first. The one pre-sanctioned adjustment: if the canonical-reader audit reports a different category for `_read_journal`, classify exactly what it reports (already in T-01's text).
- **C6 — Receipts.** All post-signature writer/test stdout that a task names tees to the feature `notes/`, never `/tmp` alone (D's C6, including its follow-up clarification: /tmp staging is acceptable only when reproduced verbatim in a `notes/` receipt).

## Q1 — Sign with the three unread c2 repairs: **yes, sign.** No further scope read

I am the read nobody did, and I read the repaired task text raw, not the dispositions. All three repairs are sound, and I verified their factual premises:

- **Replay classification (PF-cc9533d1):** the outcome space is now total. Every failure after a member `replace_bytes` or the journal unlink is `JournalPending(replay=True)` (T-01 §6); every failure before any member write propagates plainly and is truthfully reported as "nothing was written" (`guards._resolve_plan` item 3's reasoning — "which is true because T-01 raises every failure after a member write as JournalPending" — is correct by construction). I walked the DIVERGED/UNREADABLE/LOCKED/absent-member edges and the four interleaving cases (i)–(iv); each converges or refuses deterministically.
- **Case (i) seam (PF-484f97f2):** premise verified — base `harness_merge.py:141-172` has no `replace_bytes` and renames via module-level `os.replace`, so the destination-filtered `os.replace` wrapper is one seam present in both trees, and the reached-the-seam check before grading makes the base red behavioral, not a setup crash.
- **Membership recheck + duplicate refusal (PF-ebc96c4b):** closes the J1→J2 discovery race correctly (interleaving (iv)), and the pairwise-distinct rule in `_read_journal` turns the P,P self-flock timeout into an exit-5 refusal — verified `acquire` raises LOCKED as `MergeRefusal(6)` so the "never LOCKED" unit assertion is the right discriminator.

The orchestrator's trend-read is right: the c2 findings were races in spelled-out mechanism, repaired as acceptance behaviors with red-provable cases. Buying another code-reviewer cycle would re-derive what this ruling just verified.

## Q2 — (a) ruled above (2/90, C1). (b) **accept the SC-04 narrowing.** (c) **accept the dropped fsync**

**(b)** The narrowing is provably safe, not merely tolerable: `result["reset"] = False` at `amend.py:163` is the **only** assignment to that key in the module (verified by grep — two `result[` hits, both that line and the dict literal), so `if result.get("reset")` at `:301` can never fire and APPROVAL-RESET can never print on any amend path today. The removed code is unreachable for stdout for *every* case, so two exact-stdout locks (one ledgered, one unledgered — the two shapes that exist) plus SC-07's eleven unedited suites carry the grill's "every existing green case" intent. Widening would mean capturing stdout baselines for every amend case to protect against a change the dead-code proof already excludes — ritual, not information.

**(c)** Fail-closed and consistent with the feature's stated durability boundary. The member renames themselves are un-fsync'd (`replace_bytes` deliberately has none), so OS-crash durability was never in the guarantee — the BRIEF's Verification gaps says so. A crash-resurrected journal meets members at after (no-op replay) or diverged (exit-5 refusal, journal kept, images preserved in `after_b64` for hand reconciliation). Requiring the fsync plus a third outcome class would add mechanism solely for a scenario the feature explicitly does not warrant — exactly the over-specification spiral the c2 cycle was escaping.

## Q3 — apply/load_plan verify asymmetry: **backlog, own issue; not E**

Verified real: `harness_yaml.py:335-364` — `_looks_runnable` doesn't recognize `env -u VAR …`, the refusal fires in `load_plan` gated on `approval.status == "pending"`, and apply writes without running that shape check, leaving the plan unloadable until amend repairs it. It is a genuine write/read validator asymmetry in the plan-merge toolchain, but it is outside E's grilled scope (nothing in the atomicity cluster touches `harness_yaml` or apply's splice validation), and pulling it in at signature is scope creep. File it with pm's observation attached (`observations/harness-pm.md` already states the fix direction: validate the verify shape before writing, or teach `_looks_runnable` the `env` prefix — the backlog grill picks).

## Q4 — Mission-less grilling note refusal at intake: **backlog, low priority; not E**

The instruction-level door already exists — the harness SKILL mandates returning BLOCKED when an intake lacks a `## Mission` block, and `feature-record.py set-mission` is the write path. Mechanizing the refusal is cheap hardening of a rule already in force, below Q3 in consequence (Q3 left a plan unloadable; Q4's failure mode is an instruction a lead could miss). Backlog it; do not attach it to E.

## Plan defects found (beyond the escalation's list)

1. **T-02 item 6 vs. its own verify** — the `approval.py:402` docstring conflict, resolved by C2. The only defect that could have stalled the build.
2. **Minor diagnostic misnomer, noted not gated:** a plain pre-member-write `Exception` escaping `recover_journals` inside `locked_pair_update`'s initial recovery maps, via T-02 item 2's final clause, to "the ledger write to \<feature_json\> failed" — the failing operation was an older journal's recovery, not this call's ledger write. The load-bearing line ("nothing was written.") stays true, so this is a wording wart; the builder may tighten the message under C5's wording latitude, no return needed.
3. Nothing else. Anchors spot-verified (`plan-merge.py:103` exit-5 contract line, `_amend_fixture`/`_PENDING_PLAN`/`_sign`/`_load_owner` all present, `run_pool.py` and `--canonical-reader-audit` exist, `harness_merge.py` is in the audit inventory, T-02's `10 <= len(mods)` holds at 11 modules). The digest's E-02 (goalcheck missing from the panel roster) is already moot — `plan.yaml` records four readers including goalcheck.

[unverified]: the two `fcntl` lock-semantics claims I reasoned through (flock across distinct descriptors in one process, and the no-journal-can-appear-while-plan-lock-held invariant protecting sign-approval's nested write) rest on reading the design, not executing it; T-02's fixtures all run `_sign` under the new recovery code, so the build's own verify exercises the latter end-to-end.

## Constraints

Sign as `Mike Ruangutai (delegated to fable-advisor)`; plan stays byte-identical at signature (no APPROVAL-RESET applies — no pre-signature amendment is required). C1 lands in the signature answers note in the same action. C2–C6 are held at build and checkable from the receipts they each name.
