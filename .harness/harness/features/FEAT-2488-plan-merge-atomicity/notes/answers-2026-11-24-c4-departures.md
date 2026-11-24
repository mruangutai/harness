# Rulings on the round-4 departures — FEAT-2488 — 2026-11-24

Ruled by fable-advisor (AdvisorE6Dev) under the operator's delegated approval.

- D1, path lookup: approved as more faithful to the ledgered invariant. No further ledger entry is needed.
- D2, refusals through `_emit`: inside the stdio-class brief.
- The `feature_json_write.py:227` relay stays the c2 OQ-3 backlog item and is not a new instance; the citable wording is below.
- Deleting case_reversed_primary_refuses_before_any_lock is confirmed correct.

## Full ruling (verbatim)

All sources read and verified in W at commit 9ca2855b (c4 build committed; receipts in `notes/fix-c4-build/`). Four rulings follow, each Authority / Gap / Ruling / Constraints. Issued under the operator's delegated approval (DEC-174, main-session-direct).

---

# Ruling — FEAT-2488 pre-validate c4, departures D1/D2 and the relay gap

## D1 — path lookup instead of the literal listdir filter: **approved; it preserves the invariant; no further ledger entry**

**Authority.** My c3 ruling OQ-2 and the ledgered c4 amendment to T-01 intent. The ledgered text (verified in plan.yaml's T-01 amendment trail) says: *"journal discovery is JOURNAL_PAIR[0] + JOURNAL_SUFFIX (plan.yaml.harness-merge.journal) only … so the discovery set equals the producer set."* The listdir-equality filter was my fix-brief's **mechanism**, not ledgered text.

**Gap.** On a case-folding filesystem (this Mac, APFS), the producer's own `os.replace` onto a pre-existing case variant leaves the producer's journal listed under the variant's spelling. The literal spelling filter then excludes the producer's own file: a pending REAL pair goes silently unrecovered. Measured, not argued: `mf12-mutant-listdir-filter.txt` shows the literal filter mutated in fails exactly the pending-pair-rolls-forward check (1/202), and `case_the_producers_name_as_the_filesystem_resolves_it` is red at HEAD.

**Ruling.** The path lookup (`harness_merge.py:413-427`: `os.lstat` of the ONE name `_JOURNAL_NAME`, `[]` on FileNotFoundError) is the **more faithful** implementation of the ledgered invariant, because "the producer set" is defined by what the producer's `os.replace` targets — which is filesystem name resolution, not byte spelling. On a case-sensitive filesystem the two mechanisms are extensionally identical and a case variant stays foreign and inert. On a case-folding filesystem the variant entry **is** the producer's file, and only the path lookup finds it; the literal filter violates the invariant there. The builder deviated from my brief's letter to deliver my ruling's claim — the same logic under which MF-9 needed no amendment at c2.

**No further ledger entry.** The amended intent reads true as written: discovery looks up exactly `JOURNAL_PAIR[0] + JOURNAL_SUFFIX` and nothing else; "a foreign-named `*.harness-merge.journal` is never read" also reads true, because on a case-folding filesystem a case variant of the real name is **not foreign-named** — the filesystem deems the names equal, and the entry occupies the real journal's one slot. For the final validate: do not count the APFS case-variant read as a contradiction of the amendment; the name, not the listed spelling, is what the ledger pins. The distinction is documented at the code itself (`_journals_naming` docstring, verified) and evidenced by the mutant receipt; that record suffices.

**Constraints (all verified met).** `_journal_names` keeps unreadable-names-every-file (`:402-410` — fail-closed on the REAL journal intact); the check-domain two-name denial is untouched and **does** case-fold (`RE_PAIR_JOURNAL` compiled `re.IGNORECASE`, `check-domain.py:2611-2613`), so the variant spelling is denied on the governed route as the builder claimed; the hardlink-scan `names` tuple is exact-case, which is inside the already-backlogged linked-worktree/hardlink item and made moot by (b)'s inertness — no change required.

## D2 — refusals through `_emit`: **inside the stdio-class brief**

**Authority.** The c3 fix brief's own contract line: *"after commit, no state of stdout/stderr may change the exit code … One total emission path in guards.py; no second convention."*

**Gap.** None — this is the brief's text applied, not a departure. A refusal can be a **post-commit** emission: amend/record-amendments report JournalPending as exit 2 through `_die` after the journal is published. At HEAD-before-c4, a broken stderr turned that ledgered exit 2 into a traceback's exit 1 — exactly "a state of stderr changes the exit code," the class, not a new one. And leaving `_die` on raw `print` while receipts/notes/relay go through `_emit` would have been a second emission convention in the same module, which the brief forbids in so many words.

**Ruling.** In scope. The pre-commit refusals folded in (`_resolve_plan:87`, `_legal_stations:138`, `_refuse_illegal_station:150`) ride along under "no second convention"; for them the change is strictly behavior-preserving on a working stderr (byte-identical messages, same codes — `_emit` never raises, `sys.exit(code)` unconditional at `guards.py:369-370`, verified) and strictly better on a broken one (the contractual exit code survives instead of rc 1). amend.py/amendments.py untouched because everything they emit already routes through these helpers — consistent with one path, verified by the builder's `rg` census.

**Constraints.** Byte-identity on working streams is the standing obligation; it is asserted by the matrix's working/working row and SC-04 (2488/g) green. Nothing further.

## The gap — `feature_json_write.py:227` direct relay: **stays backlog; not a new instance under the no-return-clause terms**

**Authority.** My own c2 ruling OQ-3 (AdvisorE4Esc, `answers-2026-11-24-validate-c2.md`), which named **this exact call site** — "write_feature_json's unguarded relay … pre-existing at base, low severity, outside both signed tasks. Backlog" — and my c3 terminal condition, whose "another gating instance" clause governs what the final validate may count.

**Ruling.** Backlog stands; no new facts exist to re-open it. Verified: `feature_json_write.py:227` still calls `harness_boundary.relay_changed_state_feedback(resolved)` bare, reached by sign-approval and revoke-approval (`approval.py:535`, `:581`); the line is unchanged from base. Ruling it in would widen a final round onto a file outside both signed tasks' `files:` (another ledgered amendment) to fix something I already ruled out of round 3 for the same reason — consistency binds me as it did at c2.

**Wording for the final validate to cite verbatim:**

> The stderr-None misroute and unguarded-relay behavior reachable through `feature_json_write.py:227` (sign-approval / revoke-approval, `approval.py:535/:581`) is the **OQ-3 backlog item ruled at c2**, pre-existing at base 2491336e and outside T-01's and T-02's files. Under the round-4 terminal condition ("another **gating instance** of either class means descope"), a pre-existing, previously-ruled member of the stdio class in an UNCHANGED surface is **not** a new instance and does not gate. The backlog remedy remains c2's: make `_emit` importable where `feature_json_write` can reach it without a second convention; the import happens in the backlog item.

**Constraints.** The backlog ticket should now reference `_emit` by name (it exists; c2's note said "MF-9's helper", which `_emit` superseded). A recurrence would gate only if a **changed** surface of this feature introduced a new member — c3's return-clause logic, now expired.

## The deleted test `case_reversed_primary_refuses_before_any_lock`: **deletion confirmed correct**

The refusal it asserted — a `feature.json.harness-merge.journal` refused UNREADABLE before any lock — is the c1 amendment-(5) semantics that remedy (b) **replaces**: that name is now foreign, never read, so the refusal is unreachable by construction (`_recover_journal`'s pre-lock name refusal removed; `_journals_naming` hands over one name only — both verified at source). Keeping the test would pin semantics the ledger no longer claims. For the final validate: the c4 amendment supersedes c1 amendment (5)'s "refused before any lock" clause for non-primary-named journals — the surviving ledgered truth is that **the reversed lock order is unreachable**, now by inertness rather than by refusal; amendments read in order and the c4 text names what it replaces ("replacing item 5's suffix-wide discovery"), so no reconciling amendment is needed.

The lock-order guarantee did move, verified at `tests/unit/test-harness-merge-journal.py:610-622`: the foreign-file matrix asserts each route "takes only its own locks in the one order" with an exact `taken == locks` comparison, the well-formed reversed journal is one of the three planted foreign files (×18 route cases, green in `mf12-green.txt` 202/202), and `_recover_journal`'s docstring carries the structural form of the claim ("no journal can take feature.json.lock before plan.yaml.lock").

---

**Net:** both departures approved as faithful-to-ruling mechanism choices, the gap stays backlog with citable wording, the deletion is correct. Nothing here amends the ledger further; the final validate may proceed against the c4 receipts as they stand. **[unverified]:** the APFS `os.replace` case-variant behavior and all runtime measurements are the builder's receipts, which I corroborated at the named sources and the mutant transcript; I executed nothing, per read-only terms.
