# EFFICIENCY receipt — FEAT-26 plan surface — 2026-08-18

## What I read and measured

- `plan.yaml` (686 lines), `BRIEF.md` (127 lines), full text.
- `.claude/skills/harness/bin/check-state.sh` lines 850-1000 — read INV-21's block (858-891) and
  INV-24's block (893-995) in full to answer the dispatch's specific question.
- Timed `python3 .claude/skills/harness/bin/test-gh-sync.py`: **7.145s wall** (2.24s user, 1.26s
  sys), all 3 boundary-step tasks (T-02/T-03/T-04) run this whole suite as `verify:`.
- Timed a full `bash .claude/skills/harness/bin/check-state.sh` run on the current tree:
  **10.546s wall**.
- Counted `.harness/harness/features/*/feature.json`: **27 files** today.
- Measured `harness_yaml.load_file()` cost on all 27 files, 3 passes vs 1: **12.9ms for 3 passes,
  ~4.3ms per pass** (python3 timing script, in-process).

## Findings

### 1. INV-28 adds a third independent glob+parse pass where two already exist

**File/line:** `.claude/skills/harness/bin/check-state.sh:893-903` (INV-24's block, opening
`for fy in glob.glob(os.path.join(H, "*", "features", "*", "feature.json")): ... harness_yaml.load_file(fy)`)
and `plan.yaml:420-423` (T-05's intent: "Model it on the INV-21 block - the per-feature glob loop
over the feature.json files... place it after INV-24's block").

**The measurement asked for:** are the loops already N passes? Yes — read both blocks in full.
INV-21 (`check-state.sh:863-891`) runs its own `glob.glob(...features*/feature.json)` +
`harness_yaml.load_file(fy)` per feature. INV-24 (`check-state.sh:902-903` onward) runs a second,
independent `glob.glob(...)` + `harness_yaml.load_file(fy)` over the identical fileset immediately
below it. T-05's intent explicitly instructs a **third** independent glob+parse loop, "modeled on
INV-21," positioned right after INV-24's block ends — i.e., right after INV-24 has already opened
and parsed every `feature.json` in scope.

**Concrete cost, measured honestly:** on today's 27 features, one glob+parse pass costs ~4.3ms
in-process; a third pass over the same fileset costs the same again — a few milliseconds, not a
build-breaking cost today. `check-state.sh` is CLAUDE.md's own mandated per-commit gate
(the closest thing this repo has to a hot path), and this is a structural 2-becomes-3 pattern on a
file count that only grows, so the honest framing is: cheap today, and it is redundant work a
shared loop body would not do at all, on a script every commit is told to run.

**Alternative:** fold INV-28's checks into INV-24's existing loop body (it already holds a parsed
`fdoc` for every feature per iteration) rather than opening a new glob and a new
`harness_yaml.load_file(fy)` call per feature. INV-28's own logic (status == "Done", `pr` is int)
reads the same document INV-24 already parsed; only the `github.sync` gate and the two check
conditions differ, and both can live inside one shared iteration with a shared parse.

**Rank:** worth a build cycle to fix — the fix is cheap (fold the loop body) and the plan's own
intent-writer already says "model it on INV-21" without noticing INV-24 sits immediately above and
already opens the same files.

## What I deliberately did NOT flag

- **T-02/T-03/T-04 full-suite `verify:` runs (7.1s each).** Measured, not a fraction of a second,
  but the dispatch names this as the deliberate-boundary-hedge case and the skill charter says the
  same explicitly ("deliberate full-suite runs at boundary steps are not waste — they are the
  evidence the boundary exists"). Each subsequent task's suite run also includes the prior tasks'
  new cases, which is the intended growth of one shared suite, not duplicated work.
- **T-06's verify (23 `json.load` calls, one per feature).** BRIEF.md SC-08 (`BRIEF.md:78-81`)
  requires the assertion be made "one feature id at a time" and says explicitly "a count or a
  whole-file search does not satisfy this." The per-file open is what SC-08 forces, not
  over-engineering — this is the "redundancy that is a deliberate verification hedge" case named
  in my dispatch, and I did not flag it.
- **T-06's eleven `record-pr` invocations (one gh query per feature, on 7 of the 11).** Each is a
  distinct branch with no shareable query shape, this runs once at backfill signature time (not a
  hot path — CLAUDE.md's per-commit gate is `check-state.sh`, not this), and it deliberately reuses
  the mechanism T-03 built rather than a hand-rolled batch query, which the intent states as a goal
  ("using the mechanism T-03 built rather than by editing the files by hand"). Not flagged.
- **D-01..D-08.** Read all eight; none restates another or is undead. Not an efficiency-angle
  finding regardless.

## OUT-OF-CHARTER

None found.

```yaml
VERDICT: PASS
DIGEST:
  headline: one finding — INV-28 (T-05) would add a third independent glob+parse pass over every feature.json where INV-24's loop, immediately above it, already parses the same fileset
  change_type: config
  applied: []
  suite: n/a
  task: none
  open_questions: []
  files_touched: [.harness/harness/features/FEAT-26-pr-linkage-recorded/notes/receipt-harness-dev-ops-2026-08-18-2-efficiency.md]
  expertise_update: []
artifact: .harness/harness/features/FEAT-26-pr-linkage-recorded/notes/receipt-harness-dev-ops-2026-08-18-2-efficiency.md
```
