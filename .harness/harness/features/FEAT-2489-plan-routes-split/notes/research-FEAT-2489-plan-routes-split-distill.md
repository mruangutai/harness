# pm distill disposition — FEAT-2489-plan-routes-split — 2026-11-24

**BLUF:** C7 is settled from the source. `plan-merge apply` no longer exits 7 on a changed task or decision field, so repository P-04 was replaced and P-08 dropped. G-07's panel claim still holds for `apply` and was refreshed. I applied two craft ops (P-14, G-18) and four repository ops (P-04, P-08 drop, G-07, O-02). I ran no builds or suites and reviewed no diff.

## C7 — evidence (control-plane `.agents/skills/harness/bin/plan_merge/`)

- `union.py _carry_base_items`: if a proposal item differs from the base item with the same id, `_replace_fields` replaces it field by field, prints a REPLACED line and exits 0. The code comment says: "This was exit 7 CONFLICT". `UNION_KEYS = ("tasks", "decisions")`.
- `union.py _merge_key` → `_merge_plain_key`: any key other than approval, tasks or decisions raises `MergeRefusal(7, "CONFLICT: top-level key ... carries two different values")`. `panel` is one of these keys, so G-07's claim that apply exits 7 on panel still holds.
- `amend.py`: `--reason` is required for a signed task's intent, files or verify, and the change is recorded as an amendment judgement. `check_state/feature_record.py` INV-40 (d) reports an unrecorded change to signed text.
- `plan-merge.py --help`: set-panel "keeps the bytes of every unchanged finding". G-07's old claim that "safe_dump re-emits/wrapping moves" is therefore stale. record-panel is the sanctioned writer (DEC-229).

## Candidates

|#|Candidate|Disposition|
|---|---|---|
|1|C7: repository P-04/P-08 say apply exits 7 on any changed value|**Applied.** P-04 replaced with the correct rule: apply replaces fields, and only a plain top-level key exits 7; signed fields go through `amend --reason`. P-08 dropped and its amend guidance absorbed into P-04. G-07 replaced: record-panel is the writer; apply's exit 7 on panel is confirmed; the stale safe_dump clause is removed.|
|2|record-panel replaced readers wholesale and wrote reason 'none'|**Rejected.** This is the tool defect itself, already filed as #2525 and excluded from Expertise. The only remaining lesson is "diff panel.readers after record-panel". That is a workaround that becomes wrong once the defect is fixed, so it fails the six-spawns test.|
|3|Refactor contract from the move's guarantee + per-file census|**Applied as replace of craft P-14.** The old P-14 said to "permit only enumerated, bounded divergences", which is the shape that failed in this feature through three cycles. The new P-14 keeps the baseline receipts and states the contract from the move's guarantee, backed by a census taken before signature. P-18 covers payload validity fields and P-19 covers probes one boundary past a class; both are separate situations and were kept.|

## Log bullets (observations/harness-pm.md)

|Bullet|Disposition|
|---|---|
|1 AST identity + same-tree CLI diff; verify lines count toward the 50-line task budget|**Rejected.** The panel refused the AST checker as overbuild (PF-293c), so the evidence points against it. The budget point is already covered by repository G-03.|
|2 Sparse worktree tests must use feature_corpus.corpus_path|**Rejected.** It is an implementation detail for the engineers who write the tests, not a pm planning rule.|
|3 Splitting an entry file breaks fake-bin copies and mutation overrides|**Rejected.** A one-off. Craft P-07 already says to enumerate every gate that reads the changed surfaces.|
|4 apply now replaces fields (stale repository claim)|**Applied** as candidate 1.|
|5 A git archive of the base is a runnable matched tree|**Applied** as repository O-02 (add).|
|6 Probe files in an archive bin give a non-clean state|**Rejected.** A detail of one feature's measurement.|
|7 Closed delta list must include diagnostics that format a rewritten field|**Rejected.** Subsumed by the new P-14: the difference-list approach is what failed.|
|8 HEAD/BLOB-prefix receipt binding is unbound|**Applied** as craft G-18 (replace). It displaces the installed-runtime provenance entry, which comes up for pm far less often than receipt-binding verifies.|
|9 Admitted-difference class stated by printed locator|**Rejected.** Subsumed by the new P-14. Stating the class by locator was the second failed list shape.|
|10 Relocation map derived from the inventory misses moved symbols|**Rejected.** Covered by craft P-03: re-base a set derived from the material under grading onto the declared contract.|
|11 record-panel readers / reason 'none'|**Rejected** as candidate 2. The defect is #2525.|

## Counts (from tool results)

- Craft `.harness/expertise/harness-pm.md`: before P15 G15 O10 Open0; after P15 G15 O10 Open0. Batch `64d4da6bcbd2fb03b4556802d8f6122b5e34d8fea0ea7907fef96c87e4bf1aed`.
- Repository `.harness/harness/expertise/harness-pm.md`: before P13 G15 O1 Open0; after P12 G15 O2 Open0. Batch `a04ac66d6ac13127fdad146ba185a9df6391c69cd01d5d0023659b465a7e7dda`.
- Receipt: `notes/expertise-receipt-441ffe8709286efc1f5fba120ecc0a3a3ccb42f95ebd7564682a6ea1d5ef3f4a.json`.
