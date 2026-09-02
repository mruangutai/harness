# Plan fix c5 — three panel residues closed, cycle-5 panel transcribed — FEAT-53

**BLUF. All three residue findings landed and the cycle-5 panel is transcribed: `panel.last_run:
2026-09-02-08-validator`, `cycle: 5`, both readers `ran`, 28 findings.** Nothing was left unapplied.
`plan-merge.py` (main checkout) was the only writer; exactly one `set-panel`. `approval:` and BRIEF
`## Approval` are untouched and read pending. One deliberate deviation from the dispatch wording and
one word changed beyond the named clauses — both listed at the bottom.

**Filename note:** the dispatch named `notes/plan-fix-c5-<something>.md`; `check-domain.sh` denied it
(pm's per-feature grant is `notes/research-*.md` / `notes/uat-*.md`), so this is the same artifact
under the permitted name. Not worked around.

## Per-fix status

| Fix | Field | Status | Anchor after the write |
|---|---|---|---|
| 1 | `T-19.intent` | applied | `plan.yaml:1306-1315` |
| 2a | `D-23.choice` | applied | `plan.yaml:168-173` |
| 2b | `C4-04.note` | applied, folded into the single `set-panel` | `panel.findings` `C4-04` |
| 3 | `T-10.intent` | applied | `:751-766` semantics, `:791-794` assertion, `:802-807` fixture |
| 4 | `panel:` | applied, ONE `set-panel` | `plan.yaml` `panel:` |

**FIX 1 is satisfiable, proved not asserted** (`/tmp/feat53c5/probe_t19.py`, real `git`): with `git
init` alone the case FAILS — `status --porcelain` prints `?? BRIEF.md` / `?? a.txt`; with the amended
setup (`add -A`, then `commit`) it prints nothing and `ls-files --error-unmatch` exits 0 → PASSES. The
probe discriminates, so the clause is not merely plausible.

**FIX 3 reading.** Written windowed, forced by REQ-15 at source (`BRIEF.md:56`, "as a count for the
window broken into weekly buckets"). Four pins landed: a bucket counts only ships inside BOTH its ISO
week and the window; the bucket values sum EXACTLY to tile 7's headline for the window, asserted as a
case in its own right; the returned week bounds mark WHICH buckets are partial; a partial bucket with
no in-window ship carries its own verbatim sentence — `"no ship record between
<YYYY-MM-DD>T<HH:MM:SS>Z and <YYYY-MM-DD>T<HH:MM:SS>Z, the part of that week inside the window"` —
while the whole-week sentence stays byte-exact for full buckets. Both take their instants from
`resolve_window`'s bounds, so T-10 still computes no window boundary (one-authority rule intact).

## Invocations — every write, in order

```
plan-merge.py amend --key tasks     --id T-19 --field intent --expect-sha256 271ecd8a…fe02 --value-file /tmp/feat53c5/t19-intent.txt
plan-merge.py amend --key decisions --id D-23 --field choice --expect-sha256 117b3960…530d --value-file /tmp/feat53c5/d23-choice.txt
plan-merge.py amend --key tasks     --id T-10 --field intent --expect-sha256 70c9eb0e…66e1 --value-file /tmp/feat53c5/t10-intent.txt
plan-merge.py set-panel --value-file /tmp/feat53c5/panel.yaml
```
Binary: `/Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py`, `--file`
the worktree `plan.yaml` by absolute path, each preceded by its own `--show` for the hash. No Edit, no
Write, no redirect into plan.yaml.

## Read-back evidence (`/tmp/feat53c5/verify.py`, re-reads the file after the writes)

- `plan.yaml approval: {'status': 'pending', 'approved_by': 'none', 'date': 'none'}`
- `BRIEF ## Approval: ['## Approval', '', 'status: pending', 'approved-by:', 'date:']`
- `last_run: 2026-09-02-08-validator | cycle: 5`; readers `should-not-exist`/`fable-advisor` `ran`,
  `scope`/`harness-code-reviewer` `ran`
- findings **28**, by cycle `{1: 8, 2: 5, 3: 5, 4: 7, 5: 3}`; file panel == supplied value file: True
- cycle-5: `PF-0f13227f5dc23a9e7b0e987fda5dd493` med/should-not-exist → T-10;
  `PF-1b818430804d209162381618314ec9f5` low/should-not-exist → T-19;
  `PF-804ec98d2f26bd12285a095a8809e659` low/scope → D-23 + C4-04. All `resolved`, each note citing
  the amended field by line anchor. The T-10 note records that the lead considered `high` and settled
  on `med`, both ratings on the record in `runs/2026-09-02-08-validator/digest.md`.
- `C4-03` summary still names `DESIGN.md:250` and React Charts (immutable record kept); `C4-04`
  summary untouched, only its `note` corrected (and its stale `D-23` range 163-199 → 163-201).
- 19/19 clause checks `ok`, including "whole-week sentence untouched", "failure branch kept",
  "D-23 fourteen-row set and per-row subjects intact".
- `check-plan-routes.py` on this plan alone: `0 violation(s) across 1 plan(s)`, exit 0.
- BRIEF.md / DESIGN.md mtimes `10:41:17` / `10:46:25` predate the first write of this run
  (plan.yaml `11:30:10`) — neither was opened for writing.

## Deviations and residue (nothing hidden)

1. **`&&` written as "then".** FIX 1 specified `git -C <copy> add -A && git -C <copy> commit -m
   <baseline>`; the clause reads `(git -C <copy> add -A, then git -C <copy> commit -m baseline)`.
   Same two commands, same order; prose form keeps a shell operator out of plan prose.
2. **One word beyond the named clauses in T-10.** "The weekly cases must ALSO fixture **BOTH**
   definitional edges above" became **ALL THREE**, because the fix adds a third named case. Leaving
   "BOTH" would have made the sentence false — the defect class this cycle exists to stop.
3. **`git HEAD` is NOT a baseline in this worktree** — the cycle-4/5 fix passes are uncommitted, and
   HEAD's plan.yaml has no `D-23` at all. The 25 carried findings are value-identical by provenance,
   not by diff: `/tmp/feat53c5/build_panel.py` loaded them from the plan's own parse, asserted 25 in
   and 28 out, and mutated exactly `C4-04.note`; `set-panel` then verified the file reloads as the
   value supplied. Stated this way rather than claiming a diff I cannot produce.
4. **Advisory, NOT applied (out of scope).** Line anchors inside the earlier C4 notes (e.g. `C4-02`'s
   citation of `T-10.intent` lines) may have shifted by this run's amendments; the dispatch requires
   those 25 findings byte-identical apart from `C4-04`'s note, so they stand. Same class as
   repository-expertise B-11/G-05: an anchor rots without asserting anything false.
