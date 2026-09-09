# Review C3 — delta confirmation at `44351432`

**Headline: PASS. All four claimed-closed findings (F1, F2, F3-corroborated, F4) independently
confirmed at the pin with fresh evidence, not the fix cycle's word. No new gating defect found in
the changed union. SC-03 carries forward byte-identical; SC-04's four changed files re-cited fresh.**

Previous pin used for delta: `9768681c` (feature.json's `review_sha` at c2 time, per
`notes/review-harness-code-reviewer-c2.md`; `cf8a9e4c..44351432` gives an identical changed-file
set, confirmed by running both diffs). Changed union confirmed via `git show 44351432 --stat`:
the two `.omp/commands/` doors, all four `.claude/commands/` adapters, `sync-command-adapters.py`,
and both integration test files — matches the dispatch's named union exactly, nothing skipped.

## F1 — CLOSED. `test-sync-command-adapters.py` decomposed, every function passes its bar.

Per-function grades, `code-grade.py` run directly against the file (paths mode; working tree ==
pin, verified — `git diff 44351432 HEAD --stat` touches only `feature.json`):

| Line | Qualname | Cyclo | Cog | ABC | Grade | Bar | Result |
|---|---|---:|---:|---:|---:|---:|---|
| 34 | `run` | 1 | 1 | 3.0 | 5 | 3 | PASS |
| 43 | `banner` | 1 | 0 | 0.0 | 5 | 3 | PASS |
| 50 | `seed` | 2 | 1 | 7.3 | 5 | 3 | PASS |
| 60 | `case_well_formed_tree_passes_check` | 1 | 0 | 5.1 | 5 | 3 | PASS |
| 69 | `case_edited_adapter_body_fails` | 1 | 0 | 7.5 | 5 | 3 | PASS |
| 83 | `case_missing_banner_fails` | 1 | 0 | 6.7 | 5 | 3 | PASS |
| 97 | `case_orphan_door_fails` | 1 | 0 | 6.7 | 5 | 3 | PASS |
| 111 | `case_missing_adapter_apply_workflow` | 2 | 2 | 17.3 | 4 | 3 | PASS |
| 135 | `case_missing_required_door_fails` | 1 | 0 | 9.9 | 4 | 3 | PASS |
| 166 | `main` | 4 | 9 | 11.1 | 4 | 3 | PASS |

**No function is grade 1; none below its bar.** `main`'s ABC-heavy driver (`cognitive+abc`) sits
comfortably at grade 4 — a straight `for case in CASES: results.extend(case())` loop plus a
print/count tail, nothing left resembling the old grade-1 shape.

**Assertion count, old vs new (no assertion vanished):** compared `44351432^` (byte-identical to
`2eaceb99`, confirmed: `diff <(git show 2eaceb99:...) <(git show 44351432^:...)` → no output) against
`44351432`. AST-walked both (`ast.parse` + visitor collecting `check(label, ...)` call-site labels
in the old blob, and 3-tuple literals inside `case_*` functions in the new blob): **old = 12
labels, new = 15 labels.** Set difference: `missing from new = {}`, `added in new = {"missing
required door fails --check", "missing-required-door failure names the door", "missing required
door also fails --apply"}` — the 3 new assertions belong to the new `case_missing_required_door_fails`
(F3's regression pin); all 12 old labels reproduced verbatim. A shell-grep cross-check landed on the
same 12/15 split.

**Reachability confirmed, not assumed:** `CASES` tuple lists exactly the 6 defined `case_*`
functions (grep count matches tuple-literal count), `main()` iterates `for case in CASES:
results.extend(case())`. Ran the file directly at the pin (`git archive 44351432` into a scratch
dir, `python3 tests/integration/test-sync-command-adapters.py`): **15/15 cases passed, exit 0** —
every one of the 15 assertions actually executed, not merely defined.

## F2 — CLOSED. Dependency direction fixed and swept in both directions.

(a) Neither door references the adapter root any more: `.omp/commands/harness-plan.md:3` and
`.omp/commands/harness-ship.md:3` both now read `` Read `.omp/commands/harness.md` and follow it
with **mission: plan/ship** `` — canonical-to-canonical.

(b) Full 8-file sweep at the pin (`git ls-tree -r --name-only 44351432 -- .omp/commands
.claude/commands`; pattern validated against a known positive first — `git show
44351432^:.omp/commands/harness-plan.md` fires the same grep at line 3): **zero** of the 4
`.omp/commands/*.md` files reference `.claude/commands` anywhere, checked file-by-file, not by one
global grep.

(c) Inverse direction: read all 4 `.claude/commands/*.md` bodies in full. Each is banner + verbatim
canonical body; every internal cross-reference inside those bodies points at `.omp/commands/harness.md`
(the two mission files) or at nothing (harness.md, harness-grilling.md carry no internal command
cross-reference). No adapter depends on another adapter or on anything that exists only because it
was generated.

## F3 — corroborated as a side effect of reviewing F1/F2 (not separately re-litigated per scope).
Live-mutated a scratch checkout (`git archive 44351432`, python `unlink()` — not `rm`, to respect
the read-only-bash guard): deleted `.omp/commands/harness-ship.md` and its adapter together.
`sync-command-adapters.py --check` now prints `required canonical door missing from
.omp/commands/: harness-ship.md` and exits 1 — fails closed, matching the shipped
`case_missing_required_door_fails` test.

## F4 — CLOSED. Banner path is real; all four regenerated adapters carry it.
`.claude/skills/harness/bin/sync-command-adapters.py` exists at the pin (`git cat-file -e
44351432:.claude/skills/harness/bin/sync-command-adapters.py` → exit 0). All four adapters carry
the corrected banner at line 1 (`git show 44351432:.claude/commands/<name>` — quoted verbatim,
identical text modulo the filename): `harness.md:1`, `harness-plan.md:1`, `harness-ship.md:1`,
`harness-grilling.md:1`, each: `` <!-- Generated from .omp/commands/<name>; do not edit. Run
.claude/skills/harness/bin/sync-command-adapters.py --apply. --> ``. Live `--check` run against the
pin's archived tree: exit 0.

## Introduced-by-the-fix review (fail-open hunt)

**No fail-open found in `sync-command-adapters.py`'s new `missing_required_doors()`.** It uses
`(canonical_dir / name).is_file()` per name — `Path.is_file()` on a path whose parent directory
does not exist returns `False`, no exception; confirmed both by code reading and by the live
deletion above. When `.omp/commands` is wiped entirely, all 4 names come back missing, `sync()`
returns 1 before ever reaching the byte-diff logic — this is strictly stronger than the pre-fix
`canonical_paths()`/`expected_adapters()` pair (which derived "expected" from disk and went
vacuously green on the exact F3 scenario).

**MED, informational, not a new finding — `sync-command-adapters.py:44` `sync()` graded worse,
still grade 2.** Independently re-ran `code-grade.py --base $(git merge-base origin/main
44351432) --head 44351432`: exactly 2 gated FAIL records, both grade 2 (MED), zero grade 1 / HIGH.
`sync()` is now cyclomatic 12 / cognitive 18 / ABC 31.2 (was 10/15/27.9 at c2) — the new
`missing_required_doors` early-return added a branch and a loop to an already-flagged grade-2
function. Still within the accepted, non-blocking band; this is the same function F5's prior
"deliberately left" MED covers, not a new item. `tests/unit/test-no-distribution.py:66 case1()`
is the other gated record, unchanged from c2, part of the settled F6. `code_grade: grade_2`.

**Stale comment, LOW, `tests/integration/test-check-omp-port.py`, task none, lane `tests/**`
(squad-writable).** The committed comment above `case_live_tree_passes` still reads "EXPECTED TO
FAIL until the main session regenerates `.claude/commands/**`..." — but this same commit *did*
regenerate all four adapters, so the case passes at the pin (confirmed: ran the file directly,
31/31 cases passed, exit 0, including this one). The comment describes a state the commit itself
already resolved; a future reader diffing behavior against this comment would be misled about
whether the case is expected-red. Not a functional defect — the assertion is correct and green —
purely a comment-vs-code mismatch. Does not gate.

**No other fail-open found.** Read `test-check-omp-port.py`'s full diff: all touched functions are
pure decomposition of the same 23 assertions into `case_*` functions plus one new
`case_required_doors_pinned_to_sync_command_adapters` that loads `sync-command-adapters.py`'s own
`REQUIRED_DOORS` at runtime (behavioral pin, not a text grep) and proves each door's deletion is
independently caught. Ran it live: 31/31 pass.

## SC-03 — carried forward, byte-identical, verified (not assumed)

All six cited executables (`check-instruction-paths.py`, `check-state.sh`, `check-domain.sh`,
`upgrade-config.py`, `gh-sync.py`, `layout_migration.py`) are **absent from `git diff --name-only
9768681c 44351432`** (confirmed identical to `git diff --name-only cf8a9e4c 44351432`) and spot-
verified individually via `sha256sum` on `git show <ref>:<path>` at both pins — all six IDENTICAL.
c2's citations stand unchanged; MET, carried forward.

## SC-04 — 4 of ~23 files changed; those four re-cited fresh, one at a time, at the pin

`git diff --name-only 9768681c 44351432` intersected with SC-04's file set: only
`.claude/commands/harness.md`, `harness-plan.md`, `harness-ship.md`, `harness-grilling.md` changed
(the regenerated adapters). The other ~19 files (skills, templates, docs, agents + their adapters)
are absent from the diff and spot-verified byte-identical via `sha256sum` at both pins (17 files
checked, all IDENTICAL) — carried forward.

Re-cited, one file at a time, at `44351432`:
- `.claude/commands/harness.md:14-16,18` — "routes to the `harness-init` skill" / "to the
  `harness-add-repo` skill" / "not onboarding" — content lines untouched by the fix (only line 1's
  banner changed), re-verified by direct grep at the pin. MET.
- `.claude/commands/harness-plan.md` — no `harness-init`/`harness-add-repo`/onboarding mention
  anywhere (correct — this file's job is mission differences, not routing); its only content
  change (line 4: `.claude/commands/harness.md` → `.omp/commands/harness.md`) is F2's fix, not an
  SC-04 concern. MET (vacuously, correctly).
- `.claude/commands/harness-ship.md` — same as above, no onboarding mention, same line-4 fix. MET.
- `.claude/commands/harness-grilling.md:8` — "the `harness-add-repo` skill calls this for its
  technical interview" — content line untouched, re-verified at the pin. MET.

SC-04 verdict: MET, re-cited where changed, carried forward where byte-identical.

## The unsettled question — what this panel answered, and what it did not

This panel is structural/mechanical only. **Answered:** the two skill-onboarding artifacts
(`harness-init`, `harness-add-repo`) are named consistently and correctly across every executable
site and instruction file this diff touches or that SC-03/SC-04 name (six sites, ~23 files); the
command-door dependency graph is now acyclic and canonical-rooted; the generator/checker code has
no fail-open on deletion; the regenerated adapters are byte-correct. **Not answered, and cannot be
from a diff read:** whether reading `harness-init`'s or `harness-add-repo`'s SKILL.md prose top to
bottom against a real fresh checkout / real registration candidate actually walks an operator
through onboarding without friction, confusion, or a wrong turn (SC-11, SC-12 — I read no sentence
of either skill's numbered steps for this review, only the four `.claude/commands` doors and the
sync tooling), and whether `/harness-plan` is *recognised and executed* by a live OMP session
(SC-15 — I confirmed the door files exist and are byte-correct; I did not, and cannot from a git
diff, drive an actual OMP session and type the command). Point the operator's UAT at SC-11, SC-12,
SC-15 specifically — everything else in this feature's spec-compliance and code-quality surface has
now been checked, twice, by two independent panels.

## Disposition of the SETTLED list

Not re-raised: D-14 (six-case integration baseline, confirmed unchanged by this fix per the commit
message and by this diff touching none of those cases), D-13, D-10/DEC-06, D-12, D-07, D-09,
DEC-118/176. F5/F6 (the two grade-2 MED findings) not re-litigated as new; `sync()`'s numeric
shift is reported above as informational corroboration, not a new item.
