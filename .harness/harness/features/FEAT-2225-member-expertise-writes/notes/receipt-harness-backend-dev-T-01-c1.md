# Receipt — harness-backend-dev — FEAT-2225 T-01 (cycle 1)

**BLUF.** `expertise-merge.py` now has `member-ops`, `verify-receipt` and `replay` on the existing ops engine and `harness_merge` lock/atomic core (no second writer, no journal). The literal verify passes: exit 0, 0 FAIL, 549 PASS lines (194 unit + 355 integration), 34 s wall. Fail-first and 17 one-mechanism mutants are recorded below. Guards, merge authorization and T-02/T-03/T-04 files are untouched.

Product checkout: `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2225-member-expertise-writes`, branch `feat/FEAT-2225-member-expertise-writes`.

## Task verify (verbatim command, cross-checked against plan.yaml T-01)

```
python3 tests/unit/test-expertise-ops.py && python3 tests/integration/test-expertise-merge.py
```

Result: exit 0, elapsed 34 s (under 60 s). Closing lines of the output (full output is 549 PASS lines; `grep -c '^FAIL'` = 0):

```
PASS test-expertise-ops.py
PASS test-expertise-merge.py
```

Discovered/executed: unit 194 checks (pre-existing cases plus 12 new case functions: u30, u31, u32, u33, u34, u35, u36, u38, u39, u40, u41, u42); integration 355 checks (pre-existing cases plus 13 new case functions). Counts come from the `check()` tallies the scripts print, not from an empty collection. The new integration cases run on a 4-worker bounded pool so the suite stays under budget (pre-change suite alone was ~19 s; the new git/python subprocess cases add ~39 s serially, ~13 s pooled).

## Fail-first (actual evidence)

RED against the pre-change source (same tests, tool untouched), saved at `/tmp/t01/red-unit.txt`, `/tmp/t01/red-int.txt`:

- Unit: 121 PASS / 12 FAIL, exit 1 — all 12 new cases `FAIL  case_uNN_...: completed without raising` (`AttributeError`: `_next_free_id`, `destination_rel`, `_DestinationReplay`, `active_entries`, `batch_identity`, `member_ops`, `_effect_mismatches` did not exist; `resolve_ops` had no `enforce_caps`).
- Integration: 232 PASS / 63 FAIL, exit 1 — every new `member-ops`/`verify-receipt`/`replay` assertion failed (argparse rejected the subcommands), including `member absent craft: exits 0`, all nine boundary refusals, `strict` empty-list/JSON refusals, `refusal: cap overflow refused with 8` and `receipt failure: ...`. (An earlier run crashed on an unguarded `FileNotFoundError`; I wrapped the new cases in `run_guarded` so a mutant or missing subcommand reads as FAIL, never an aborted suite.)

One-mechanism mutants (copy of the bin dir, one literal changed, `EXPERTISE_MERGE_BIN` pointing at it; pristine source hash `e4c68589a58f` verified unchanged afterwards). Every mutant reddened named checks only, none aborted:

| Mutant (mechanism) | FAILs | Named checks that went red |
|---|---|---|
| M1 independent-caller check off | 4 | u35 identical/drop independent; `replay independent: two callers ... (identical text not hidden)` |
| M2 PR selection ignores base | 4 | `replay selection: ... earlier distill's receipt ... ignored`, `only the current PR's receipt is read`, supersession `outside this PR` |
| M3 supersession persona/feature/destination scope off | 9 | u38 cross-persona/cross-destination; `another persona cannot retire the batch` |
| M4 check-expertise skipped | 3 | `candidate failing check-expertise refused with 14` + no-applied-batch checks |
| M5 no collision remap | 11 | u32 (all), `replay collision` mapping/survive/write |
| M6 changed/vanished original accepted | 10 | u34 CHANGED/DISAPPEARED; `replay changed main` named-field and DISAPPEARED |
| M7 batch identity unchecked | 2 | tamper fails replay and verify with 15 |
| M8 ambiguous supersession allowed | 4 | u38 ambiguous; `second replacement of the same batch is ambiguous` |
| M9 final-effect compare off | 4 | u41; verify reverted-intermediate and removed-entry mismatches |
| M10 symlink exactness off | 0 first run (my boundary fixture's symlink targets did not match the tail regex) → added legal-looking-tail symlink cases → **3** | `symlink onto another tree's legal-looking .harness/expertise`, `symlinked repository segment with a legal-looking tail`, `nothing landed in the symlink targets` |
| M11 unreceipted-change coverage off | 2 | `receipt failure: replay fails closed on the unreceipted change`, `evidence: Expertise change with no receipt` |
| M12 final cap check skipped | 1 | `replay cap: overflow refuses rather than truncates` |
| M13 first-free becomes max+1 | 7 | u30, u32 mapping, collision hash/mapping/repeat |
| M14 supersession keeps retired batch | 4 | `same persona re-dispatched child replaces the refused batch`, reconstruction file |
| M15 cycle check off | 3 | u38 cycle; `evidence: cyclic supersession` |
| M16 receipt/file agreement check off | 0 first run (no test could disagree) → added u42 → **1** | `u42: receipt/file disagreement refuses the call` |
| M17 originals recorded as null | 24 | batches originals/counts, verify, independent |

Mutant logs: `/tmp/t01/mutants.txt`, `/tmp/t01/mutants2.txt`.

## Behaviors named in the intent — assessed

- **member-ops** (host-bound root, feature, persona, runtime/parent ids, craft or repository tier, ordinary JSON ops): done. `persona`/`state`/unknown op keys are refused by the unchanged engine (exit 12); the low-level `ops` regression for `persona` still refuses. Ops are shape-validated before any lock is taken.
- **Destination**: `destination_rel` builds only `.harness/expertise/<persona>.md` or `.harness/<segment>/expertise/<persona>.md`; segment is a literal token that must be an existing `.harness/<segment>` directory; `resolve_destination` requires `realpath == expected path` (any symlink in the chain refuses, including ones landing on a legal-looking tail) and then `require_expertise_destination`. Refusals exit 9 and write nothing.
- **Delegation / absent files**: parsing, section/id resolution, caps, flock and atomic replace come from `resolve_ops` and `harness_merge.locked_update`; `check-expertise` runs on the computed candidate before landing (exit 14). Absent file gets the canonical title and four sections.
- **Result**: JSON with `before`/`after` per-section counts, outcomes, batch id and receipt path.
- **Receipt**: `notes/expertise-receipt-<sha256 runtime id>.json` under the one `.harness/*/features/<FEAT>` directory; persona, feature, runtime and parent ids; per batch checkout-relative destination, ordered exact ops, original text/absence per op, before/after hashes, `supersedes`, content-derived batch id (timestamp excluded). Repeated calls append ordered batches; identity mismatch on the same runtime id refuses before any write.
- **Persistence and failure**: target persisted first, then receipt through `locked_update`; success is published only after re-reading both and agreeing. Receipt persist failure fails the call (exit 15, target stays written) and verification/replay then fail closed; a refused operation changes no bytes and adds no batch. No journal, pending state or resume path.
- **verify-receipt** (read-only; creates no lock): matches persona, feature, runtime, parent, destination and exact claimed ops (item-level `persona` stripped, required); evaluates the final effect of the runtime's ordered active batches against the file; lists preserved identical adds; reports unreported recorded ops; validates supersession references.
- **replay** (`--root --feature --base [--check]`): reads only this feature's receipts absent from the base tree; rebuilds each file from the base blob; replays active batches in recorded order (`recorded_at_ns`, runtime id, seq); collision adds take the first free positive id (reserved ids excluded) with per-runtime remap of later references; identical adds preserve; replace/drop require the recorded original (CHANGED/DISAPPEARED refuse, already-applied replace is idempotent); independent callers on one entry refuse before the idempotence test; one-base-snapshot per batch via the engine; caps (deferred to the complete candidate) and check-expertise run before any write; all-or-nothing, refused files byte-identical; JSON emits refusals (persona, runtimes, destination, section/id, batches, code, reason), id mappings, base/result/current hashes and `up_to_date`.
- **Supersession**: `--supersedes <batch id>... --base <sha>` on member-ops; references validated (exist in this PR, earlier, same persona/feature/destination, acyclic, single successor); reconstruction = base blob + other active batches, then the new ops; empty withdrawal supported; historical receipts never rewritten; failed replacement retires nothing; active set follows validated references. Another persona, another destination, missing/malformed ids, no `--base`, duplicate successor, cyclic and on-main references are all tested refusals.

## Test coverage map (task intent → case)

absent craft/repository files, boundaries, strict ops → `case_member_absent_files/_destination_boundaries/_strict_ops`; append batches, refusal preserves bytes/no batch, cap overflow → `_batches_append/_refusal_preserves`; receipt persistence failure + fail-closed → `_receipt_failure_fails_closed`, u40, u42; final-effect verification, preserved vs invented → `_verify`, u41; current-PR selection → `case_replay_current_pr_selection`; two worktree adds, collision mapping, repeat replay → `case_replay_collision_and_repeat`; independent replace/drop → `case_replay_independent_callers`; changed-main replace/drop and cap overflow → `case_replay_changed_main_and_cap`; refusal → same-persona re-dispatch → replay success, empty withdrawal, immutability, idempotence, unauthorized/ambiguous → `case_supersession_flow`; tamper/cycle/unreceipted/missing file → `case_replay_evidence_fails_closed`, u38.

## Decisions I made (cheap, reversible)

- Subcommand flags: `--tier craft|repository [--repository SEG]`, `--ops`, `--claimed`, `--supersedes` (repeatable), `--base`; stdout is one JSON object, refusal lines print to stdout like `cmd_ops`.
- New exit codes: 13 replay refusal (JSON `refusals`), 14 candidate failed check-expertise, 15 receipt-evidence failure (missing, mismatched, tampered, unauthorized, ambiguous, cyclic, unreceipted change, bad base).
- Cross-runtime replay order is `recorded_at_ns` then runtime id then seq. A later runtime that edits an entry an earlier runtime added is replayed in that order; if the order is wrong the batch refuses (DISAPPEARED) for member re-judgment, never silently misapplies.
- `replay` also refuses (15) when the checkout changed an Expertise file (vs the merge-base with the base) that no receipt names — the missing-evidence arm of "fails closed at replay/merge".

## For T-04 / the main agent

- Interface T-04 consumes: `member_ops`, `verify_receipt`, `replay_feature` (library) or the three CLI subcommands; `verify-receipt` takes the item list `expertise_update` (each item with `persona`) and optional `--base` to limit receipts to the PR.
- Flock files `*.md.lock` / `*.json.lock` are left beside the files by `harness_merge` as before (`.gitignore` covers `.harness/**/*.lock`).
- Checks I did not run (assignment scope): `code-grade.py --base ... --head HEAD` on the changed Python (new functions were written as small helpers; `_validate_receipt`, `_DestinationReplay._edit_problem` and `replay_feature` are the likeliest to need a grade-2 reason), the full unit/integration suites beyond this verify, any lint/format.
- No plan amendment proposed: intent, files and verify were sufficient as written.

## Principles applied

- Separate Before Serializing Shared State: each runtime caller owns its own receipt file (`expertise-receipt-<sha256 runtime id>.json`) and each persona its own Expertise file, so receipts never share a writer; only the one real shared target (the Expertise file) is serialized, through the existing `harness_merge` lock.
- Make Operations Idempotent: replay rebuilds from the named main blob every time, so a second run converges to the same bytes (`replay repeat`), identical adds preserve and already-applied replaces are no-ops; a crash between target and receipt is handled by fail-closed verification instead of a resume path.
