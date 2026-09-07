# EFFICIENCY angle — BUG-148 gate-record-correction

**EFFICIENCY: no finding.**

## BLUF

Both realistic entry points reach the corrected mechanism in one read; the read-only freshness
check (`gen-decisions-index.py --stdout | diff -`) exits 0 clean. Compute-cost is out of scope for
this angle and is declared inapplicable below, not padded into a finding.

## Compute-cost — inapplicable

This diff is prose only: two docs passages rewritten in place plus a generator-produced index
regeneration. No hot path, no loop, no repeated I/O is introduced or changed. Per the skill's
"Measure before flagging," there is nothing here for the compute-cost half of EFFICIENCY to
measure — stated plainly, not manufactured as a finding.

## (a) Reader-cost trace — two entry points

1. **`DECISIONS-INDEX.md` → DEC-174 row (`gen-decisions-index.py`:177, anchor `@4302`).** The row's
   own ruling text is unchanged and is about a different facet of DEC-174 (harness never executing
   changes to its own hooks/validators/gate scripts) — it does not itself mention
   `gen-decisions-index.py --check`, so it cannot mislead about that claim. Following the anchor
   lands the reader at the DEC-174 heading in `DECISIONS.md`, and the corrected evidence sentence
   (`DECISIONS.md:4305-4318`) sits inside that same entry, a few lines below the anchor. One hop,
   answered: the corrected text states plainly that `--check` was never a supported mode, names the
   pre-`ffbdbfa1` fallthrough-to-write behavior, and gives the read-only replacement command
   verbatim. No second hop required.
2. **FEAT-05 `STATE.md`, landing near line 13.** The corrected passage is the passage itself — no
   indirection. It states "Three gates green," names the fourth entry as no gate at all, gives the
   same mechanism in the same terms as DEC-174 (required by plan D-05 ruling 3, not a duplication
   defect per the shared contract), and ends with the same read-only command. A reader who reaches
   for `--check` here is answered in the same paragraph they're already reading.

Neither entry point forces a second hop to learn what to use instead.

## (b) Generated index as a data artifact

- Diff scope confirmed: `DECISIONS-INDEX.md`'s only changes are per-row `@NNN` anchors for every
  entry from DEC-175 onward (DEC-174's own anchor `@4302` is unchanged — the edited passage sits
  after that anchor, within the same entry, so the anchor itself doesn't move). No row's tag list,
  refs, or ruling text changed.
- Anchor arithmetic checks out by hand: `DECISIONS.md`'s hunk is 2 lines removed / 10 added, net
  +8; DEC-175's anchor moves `@4424` → `@4432`, exactly +8. Every subsequent row shifts by the same
  constant.
- Read-only freshness check, run exactly as specified, writes nothing:
  ```
  python3 .agents/skills/harness/bin/gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md
  EXIT:0
  ```
  Empty diff, exit 0 — the committed index is NOT stale against the committed `DECISIONS.md`. No
  finding here.

## Invariants preserved

No alternative is proposed, so no invariant-list phrase is touched and there is no net line-count
effect on `DECISIONS.md` to report.

## Checks performed (for the zero-finding record)

- Read `harness-simplify` SKILL.md `## EFFICIENCY` section in full.
- Read plan.yaml `decisions:` D-01/D-04/D-05 and T-01/T-02 `intent:` (binding: same mechanism, same
  terms, cross-record repetition required, `--stdout | diff -` form required in both records).
- Read the full diff for all three product paths (no elisions left unread via `artifact://624`).
- Traced both reader entry points named in the dispatch against the actual corrected text.
- Confirmed DEC-174's index row text itself, independent of the diff, to check it doesn't mislead.
- Ran the read-only freshness command myself; reported its exit status and (empty) output above.

## Product paths touched by this run

None. `git status --porcelain` on this worktree shows only this receipt.
