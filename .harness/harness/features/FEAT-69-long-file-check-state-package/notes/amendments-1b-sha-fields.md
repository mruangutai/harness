# FEAT-69 — amendment 1b (DEC-174 main-session-direct): the two SHA-only field edits, ledgered

The T-01 `intent` and T-04 `verify` fields were corrected with `plan-merge.py amend` (baseline `e6f8493b` → `a726bad8`, amendment 1). That verb rewrites the field but writes no ledger entry, and INV-40 refused the first clean-pin full-table run for exactly that ("the signed text was edited outside the ledger"). `record-amendments` was tried with the digest below and crashed in `_item_range` (IndexError) on these multi-line block-scalar fields — a plan-merge defect for the backlog, not in this feature's scope — so the two amendments are ledgered with `feature-record.py judgement --kind amendment --decision T-01.intent | T-04.verify` (the entry shape INV-40 reads), and the fields re-applied through `amend`. The was/now record of each field:

```yaml
VERDICT: PASS
DIGEST:
  amendments:
  - task: T-01
    field: intent
    was: 'Work only in the assigned FEAT-69 worktree. Use the grilling map at e6f8493b without re-deriving it: check-state.py is 5,058 lines; bootstrap is lines 1-118 with root = sys.argv[1] at line 96 as the bootstrap-end sentinel; class Ctx is lines 467-878; invariant bodies are lines 880-4563; INVARIANTS is lines 4599-4750; RETIRED is line 4754; runner logic is lines 4759-5058. The baseline code-grade record is 287 functions: 114 at grade 5, 169 at grade 4, two at grade 3, and two at grade 2. The only below-bar functions are _inv41_invocation at 2, _unquoted_hash_digit at 2, _quoted_scalar_closed at 3, and inv_49 at 3; improve those in the modules where they land while preserving observable behavior.


      Keep check-state.py as the existing hyphenated forked entry and thin it to roughly 150 lines without introducing a file-length gate. Preserve bootstrap root resolution, argv shape, bin-on-sys.path behavior, process exit semantics, and the root = sys.argv[1] sentinel. Add importable check_state/__init__.py. Keep Ctx whole in ctx.py, including parse-once caches, seed findings, spawn boundary, path helpers, and shared context primitives. Put the exact baseline table and all row-selection discretion in table.py; it alone imports every family and owns INVARIANTS in the baseline''s exact order. Put row selection, repo and feature passes, collation, reporting, and CLI dispatch behind runner.py. check-state.py never selects families. Family modules never import or know the runner and expose no per-family entry points.


      Move invariant bodies and their private helpers by the settled declared-read ownership, with no omissions or extra families: plan.py owns INV-35/3/4/5/34/32/44; feature_record.py owns INV-1/2/6/7/8/12/18/22/23/33 and ledger INV-39/40/43/47 with collate_feat59; run_state.py owns INV-15/16/36/46; seams.py owns INV-17; brief.py owns INV-38/41/49 and the INV-38..41 helpers currently at lines 332-466; worktrees.py owns INV-25/27/29/31; board.py owns INV-13/21/24/26/28/30/37; host.py owns INV-19/42/45/48. Retain the accepted judgment placements INV-1/2 in feature_record.py and INV-27/31 in worktrees.py. Families export inv_NN(ctx[, feat]) returning the existing bad and warn shape; preserve the ledger collation shape.


      Preserve every invariant''s behavior, exact message text, severity, table and finding order, short-circuit, accumulator seeding, feature iteration, retired-number behavior, and return/exit shape. Move existing comments byte-for-byte with their code. Preserve all four load-bearing INV-32 markers: the era BEGIN/END comments at baseline lines 1380/1384 travel with INV-32 in plan.py, and the table-row BEGIN/END comments at baseline lines 4605/4610 travel with that row in table.py. Make no rename beyond what the package forces. Do not change plan-merge.py, validate-digest.py, check-domain.py, gh-sync.py, any unrelated long file, any message, any severity, any invariant order, or any navigation-family .get site.

      '
    now: 'Work only in the assigned FEAT-69 worktree. Use the grilling map at a726bad8 without re-deriving it: check-state.py is 5,058 lines; bootstrap is lines 1-118 with root = sys.argv[1] at line 96 as the bootstrap-end sentinel; class Ctx is lines 467-878; invariant bodies are lines 880-4563; INVARIANTS is lines 4599-4750; RETIRED is line 4754; runner logic is lines 4759-5058. The baseline code-grade record is 287 functions: 114 at grade 5, 169 at grade 4, two at grade 3, and two at grade 2. The only below-bar functions are _inv41_invocation at 2, _unquoted_hash_digit at 2, _quoted_scalar_closed at 3, and inv_49 at 3; improve those in the modules where they land while preserving observable behavior.


      Keep check-state.py as the existing hyphenated forked entry and thin it to roughly 150 lines without introducing a file-length gate. Preserve bootstrap root resolution, argv shape, bin-on-sys.path behavior, process exit semantics, and the root = sys.argv[1] sentinel. Add importable check_state/__init__.py. Keep Ctx whole in ctx.py, including parse-once caches, seed findings, spawn boundary, path helpers, and shared context primitives. Put the exact baseline table and all row-selection discretion in table.py; it alone imports every family and owns INVARIANTS in the baseline''s exact order. Put row selection, repo and feature passes, collation, reporting, and CLI dispatch behind runner.py. check-state.py never selects families. Family modules never import or know the runner and expose no per-family entry points.


      Move invariant bodies and their private helpers by the settled declared-read ownership, with no omissions or extra families: plan.py owns INV-35/3/4/5/34/32/44; feature_record.py owns INV-1/2/6/7/8/12/18/22/23/33 and ledger INV-39/40/43/47 with collate_feat59; run_state.py owns INV-15/16/36/46; seams.py owns INV-17; brief.py owns INV-38/41/49 and the INV-38..41 helpers currently at lines 332-466; worktrees.py owns INV-25/27/29/31; board.py owns INV-13/21/24/26/28/30/37; host.py owns INV-19/42/45/48. Retain the accepted judgment placements INV-1/2 in feature_record.py and INV-27/31 in worktrees.py. Families export inv_NN(ctx[, feat]) returning the existing bad and warn shape; preserve the ledger collation shape.


      Preserve every invariant''s behavior, exact message text, severity, table and finding order, short-circuit, accumulator seeding, feature iteration, retired-number behavior, and return/exit shape. Move existing comments byte-for-byte with their code. Preserve all four load-bearing INV-32 markers: the era BEGIN/END comments at baseline lines 1380/1384 travel with INV-32 in plan.py, and the table-row BEGIN/END comments at baseline lines 4605/4610 travel with that row in table.py. Make no rename beyond what the package forces. Do not change plan-merge.py, validate-digest.py, check-domain.py, gh-sync.py, any unrelated long file, any message, any severity, any invariant order, or any navigation-family .get site.

      '
    reason: 'amendment 1: the baseline SHA is a726bad8 (e6f8493b predates INV-49); the field''s only change is that SHA'
  - task: T-04
    field: verify
    was: 'python3 -c ''import re,subprocess; rel=".harness/harness/features/FEAT-69-long-file-check-state-package/notes/clean-pin-byte-receipts.generated.md"; receipt_commit=subprocess.check_output(["git","log","-1","--format=%H","HEAD","--",rel],text=True).strip(); assert receipt_commit,"receipt commit not found"; text=subprocess.check_output(["git","show",f"{receipt_commit}:{rel}"],text=True); pins=re.findall(r"(?m)^implementation_pin: ([0-9a-f]{40})$",text); assert len(pins)==1,pins; pin=pins[0]; assert pin!=receipt_commit,"receipt commit must postdate implementation pin"; subprocess.run(["git","merge-base","--is-ancestor",pin,receipt_commit],check=True); subprocess.run(["python3",".harness/harness/features/FEAT-69-long-file-check-state-package/notes/receipt-scripts/feat69-cleanpin.py",pin,"e6f8493b"],check=True)''

      '
    now: 'python3 -c ''import re,subprocess; rel=".harness/harness/features/FEAT-69-long-file-check-state-package/notes/clean-pin-byte-receipts.generated.md"; receipt_commit=subprocess.check_output(["git","log","-1","--format=%H","HEAD","--",rel],text=True).strip(); assert receipt_commit,"receipt commit not found"; text=subprocess.check_output(["git","show",f"{receipt_commit}:{rel}"],text=True); pins=re.findall(r"(?m)^implementation_pin: ([0-9a-f]{40})$",text); assert len(pins)==1,pins; pin=pins[0]; assert pin!=receipt_commit,"receipt commit must postdate implementation pin"; subprocess.run(["git","merge-base","--is-ancestor",pin,receipt_commit],check=True); subprocess.run(["python3",".harness/harness/features/FEAT-69-long-file-check-state-package/notes/receipt-scripts/feat69-cleanpin.py",pin,"a726bad8"],check=True)''

      '
    reason: 'amendment 1: the baseline SHA is a726bad8 (e6f8493b predates INV-49); the field''s only change is that SHA'
```
