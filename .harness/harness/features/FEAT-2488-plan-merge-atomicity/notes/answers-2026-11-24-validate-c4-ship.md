# Final ruling after validate c4 (ESCALATE) — FEAT-2488 — 2026-11-24

Ruled by fable-advisor (AdvisorE7Final) under the operator's delegated approval.

**Disposition: SHIP at 45f16cfa.**
- C1 and S1 are not gating instances of either class, and descope remedies neither. Both go to backlog (BL-1, BL-2).
- Backlog BL-1..BL-6.
- The eight-item disclosure list goes in the ship record.
- No ledger correction is needed.
- Distill runs.

## Full ruling (verbatim)

The core refuses my direct apply (no governed identity in this session), so the fable-advisor distill rows below go into the dispatch list with the others, spelled out verbatim for the lead to apply.

---

# Ruling — FEAT-2488 validate c5 ESCALATE (pin 45f16cfa)

Issued under the operator's delegated approval (DEC-174, main-session-direct). I re-read every cited site in W: `guards.py:254-348` (`_STDIO_FAULTS` tuple, `_emit`, `_relay_after_commit` running `relay_changed_state_feedback` inside `_emit("stderr", …)`), `harness_boundary.py:489-515` (`subprocess.run(text=True)` with no encoding at :501-502, catch `(OSError, SubprocessError)` at :503), `check-domain.py:2604-2629` (`RE_PAIR_JOURNAL` anchored `…)$` on the final component), plan.yaml:355 (claim (7) verbatim), and the c0/c2/c3/c4-departures rulings. I ran my own grep: **no** `warn_default_encoding`, `PYTHONWARNINGS`, `EncodingWarning`, or `-W error` anywhere in `.claude`, `.omp`, `.github`, or `tests` — the lead's claim verified independently. All runtime measurements remain the readers'; I executed nothing.

## C1 — not a gating instance of the stdio class. Backlog.

**Authority.** The c3 fix brief's own class contract: *"after commit, no **state of stdout/stderr** may change the exit code, double-apply the write, or misroute output"* — with the tuple rationale ruling raises from outside the stream-fault family a caller contract breach. Plus the c4-departures precedent I signed: a pre-existing member of the relay family in an unchanged surface "is **not** a new instance and does not gate."

**Gap.** Under `-X warn_default_encoding -W error::EncodingWarning`, `harness_boundary.py:501`'s `subprocess.run(text=True)` raises EncodingWarning outside both `_STDIO_FAULTS` and harness_boundary's own `(OSError, SubprocessError)`; the verb exits 1 after both files land, no receipts.

**Ruling.** In C1 both streams are *healthy* — no stdout/stderr state is involved. The raise is a subprocess-spawn fault under an opt-in interpreter configuration no harness surface sets (verified empty grep), originating at a line unchanged from base, in the same relay as the ruled OQ-3 backlog class. At base the identical trigger produced rc 2 **with a torn pair**; the pin's rc 1 with both files landed and the journal removed is strictly less harmful — the feature *improved* this path. This is a new member of the already-ruled unguarded-relay family, not of the stdio-state class. Reconciled severity: **med**. Backlog, folded into the OQ-3 ticket (OQ-2's question: yes).

**Constraints.** The backlog ticket must (a) add `encoding="utf-8"` (or equivalent) at `harness_boundary.py:501` alongside the c2 `_emit`-import remedy, (b) add a regression test running the relay under `-W error::EncodingWarning`, and (c) measure amend idempotency on retry after a post-commit rc 1 — the one consequence the digest flags as unmeasured `[unverified]`.

## S1 — not a gating instance of the journal class. Backlog.

**Authority.** My c3 journal-class contract ("the discovery set equals the producer set") and its explicit pricing: *"an unreadable **real** journal still wedges every write in the directory until reconciled — that is the designed crash-recovery posture."* Plus the c2 Bash-porosity backlog ruling (perimeter porosity predating the feature's enforcement posture goes to backlog, D precedent).

**Gap.** `RE_PAIR_JOURNAL` (check-domain.py:2611-2613) matches only paths *ending* in a journal name, so a governed Write below `plan.yaml.harness-merge.journal/` implicitly creates a directory at the real slot; every pair write then refuses at exit 5 until one `rmdir`. Source inspection only; nobody executed the governed route `[unverified at runtime]`.

**Ruling.** S1 does not touch discovery — remedy (b)'s invariant stands closed by construction, and a directory at the real slot refusing at exit 5 is the fail-closed behavior I ruled *designed*. What S1 adds is a second route into a state already reachable via the backlogged Bash route (`mkdir` at the slot), with identical blast radius: availability-only, one-command recovery, no integrity or confidentiality consequence. It is also a general check-domain property — implicit parents are never judged for *any* denied name — which makes it perimeter porosity, the exact class c2 sent to backlog, not a journal-class instance. Reconciled severity: **med**. Backlog, grouped with Bash-route porosity.

**Constraints.** The ticket's remedy is to judge every ancestor component a Write would implicitly create (or deny Writes carrying a denied name as a non-final component), with a planted-Write test; the unexecuted governed route gets executed there, not here.

## Is descope a remedy? No — for either. The lead is right.

The terminal condition's descope clause was written *for gating instances of the named classes*; applied to these findings it is incoherent on its own terms:
- The stdio descope (revert to base print-only) does not touch `harness_boundary.py:501`, **restores base's torn-pair rc 2** under C1's exact trigger — strictly worse — and re-opens the four stdio members round 4 closed (None-misroute, closed, broken-pipe, exit-flush).
- No journal descope exists because remedy (b) "leaves no residue to descope" (my own words); reverting it would re-open MF-12 while leaving check-domain's final-component property exactly where it is.

Since neither finding is a gating instance of either class, the descope clause is **not triggered**; the governing rule is the standing one from c2: a non-member / pre-existing-family finding goes to backlog under the D precedent. The condition's silence on non-members is a defect in my c3 drafting, not in the feature — that goes to distill, below.

## Disposition: **SHIP**

MF-11 and MF-12 are closed as defined, measured by the lenses that raised them (c4 probe rc 0 both verbs; N-1 wedge 6/6; foreign-name trace; QA's own mutants killed); unit 68/68 and integration 95/95 with PYTHONUNBUFFERED stripped under DEC-255 receipts; SC-01..07 met; C4 untouched, signature stands.

**Backlog rows (exact):**

| id | item | sev | remedy |
|---|---|---|---|
| BL-1 | Post-commit relay hardening, `harness_boundary.py` (merges c2 OQ-3 + C1): unguarded relay at `feature_json_write.py:227` reached by sign/revoke-approval (`approval.py:535/:581`); `encoding="utf-8"` at `harness_boundary.py:501`; route through `guards._emit` once importable without a second convention; regression test under `-W error::EncodingWarning`; measure amend retry idempotency after post-commit rc 1. **File with corrected wording**: drop "outside T-01's and T-02's files" (T-02's files include `feature_json_write.py#write_feature_json`); the relay *line* is unchanged from base, which is the fact that carries the ruling. | med | one tested edit per site |
| BL-2 | check-domain implicit-parent creation (S1), grouped with the c2 Bash-route porosity and the T-09 13 Edit/NotebookEdit note: judge ancestor components a Write would implicitly create; execute the governed-route test below `plan.yaml.harness-merge.journal/`. | med | gate widening + test |
| BL-3 | Regression lock: `_die` refusal under None/broken stderr (QA G-1; pin correct, 8f948c52 blob regresses). | low | one test |
| BL-4 | Add QA's five joint stdio states to `_STDIO_MATRIX` (probed green, 42/42 — lock them in). | low | tests only |
| BL-5 | Standing, unchanged: linked-worktree hardlink detection; `RE_PAIR_JOURNAL` `$`→`\Z`; FEAT-63 census loophole (BaseException/tuple handlers uncounted); Q3 apply/load_plan verify asymmetry; Q4 mission-less intake; c1 security advisories (case-insensitive alias, unescaped filenames). | — | as ruled c0/c2/c3 |
| BL-6 | SC-07 preservation discrimination (baseline lock only): add one mutate-and-observe-red demonstration. | low | one test |

**Ship-record disclosure list (accepted risk, ruled across c0..c4, not backlog work):**
1. MF-9 residue: fd 1 closed *after* interpreter startup → exit 120 after landing, both verbs, base parity (re-measured at c5; priced at c2/c3).
2. c0 outcome-space sliver: exception classes outside the enumerated tuples traceback with the journal left on disk; disk stays safe-by-journal (rolls forward), confined to MemoryError-grade anomalies.
3. C1 residue until BL-1 lands: under opt-in warnings-as-errors the relay exits 1 post-commit — strictly better than base's torn pair at rc 2.
4. S1 residue until BL-2 lands: availability-only wedge at exit 5, one `rmdir` recovery, governed reachability source-inspection only `[unverified at runtime]`.
5. D1 APFS semantics: the ledger pins the *name*, not the listed spelling; an APFS case-variant read is not a contradiction of the amended intent.
6. EPIPE mid-write unreachable because receipts < 3.1 KB `[INFERENCE, QA's]`.
7. Amendments trail: T-02 amendment (7) (c2 era); c4 T-01 amendment (discovery = `JOURNAL_PAIR[0] + JOURNAL_SUFFIX`; verify + `test-check-domain-approval.py`, closing G-04); rework records 3/120 → 4/150, both by set-rework on advisor ruling.
8. Departures: D1 path-lookup discovery (approved as more faithful to the ledgered invariant, no ledger entry); D2 refusals through `_emit` (inside the brief); deletion of `case_reversed_primary_refuses_before_any_lock` (the c4 amendment supersedes c1 amendment (5)'s refusal clause; lock-order guarantee holds by inertness, pinned at `test-harness-merge-journal.py:610-622`).

**Ledger truth check: no correction needed.** Claim (7) (plan.yaml:355, read verbatim) scopes "the verb still exits 0" to stdout states — "if stdout cannot take them (closed: ValueError; broken pipe: OSError)" — and those are measured true at the pin (c4 probe, QA matrix). Its final sentence, "No **write** after a commit can turn a landed amendment into a traceback," also reads true: C1's traceback originates in a subprocess *spawn*, not a write, and only under an interpreter config the claim never spoke to. Its "(OSError, ValueError)" tuple mention is now incomplete (the pin adds AttributeError) — incomplete, not false; disclosure 7 covers it. T-01's amended intent reads true under the D1 ruling. The one false-reading sentence anywhere ("outside T-01's and T-02's files") lives in `notes/answers-2026-11-24-c4-departures.md:48` — notes, not the signed ledger — and is corrected at BL-1 filing.

## Distill: yes, run it

Dispatch distill runs for (verbatim lesson per persona):
- **fable-advisor (craft)** — the core refused my direct apply (no governed identity this session), so apply these two for me: **(P1)** a FINAL-round terminal condition must define each class by contract, pre-rule the disposition of *non-member* findings (default: severity-reconciled backlog under the D precedent), and prescribe descope only where descope verifiably remedies that class — c5's escalation existed only because my c3 condition was silent on non-members and its descope remedied neither finding. **(P2)** a class-closure round must carry an adjacency-sweep obligation one boundary beyond the stated contract — the cascade (one member per round, rounds 1–4, same as Feature D) ended only when the c3 brief enumerated the class exhaustively.
- **harness-orchestrator** — carrying reader highs by name with the lead's reconciliation alongside (P-04) and routing FINAL+FAIL per G-06 produced a decidable escalation; keep that shape. Brief class *contracts*, never instance lists.
- **harness-qa / harness-pm** — both called the classes closed while measuring only inside the stated contracts; closure verification needs one probe beyond the contract boundary before "closed" is said.
- **harness-code-reviewer / harness-security-reviewer** — probing outside the stated class contracts is what found both adjacent members (P-06); retain as pattern, including the discipline of routing them to the terminal ruling instead of demanding round 5.
- **round-4 builder persona** — "fix the class, then sweep neighbors in the same round"; the exhaustive c3 matrix is the template.

**Net:** SHIP at 45f16cfa under option (a), with BL-1..BL-6 filed as above, the eight-item disclosure list in the ship record, no ledger correction, and distill dispatched for the six personas named — my two craft rows included verbatim since the direct apply was refused.
