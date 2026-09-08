# Code Review — BUG-148-gate-record-correction — cycle 0 (harness-code-reviewer)

**PASS.** All four inspection criteria met, both prose-quality reads clean, DECISIONS-INDEX
regeneration confirmed anchors-only. Zero findings after a real read. This is a docs-only diff;
no Python changed in the review range (`code-grade.py` over `merge-base(origin/main, 87e6033)..87e6033`
prints `PASSING: 0`, no graded functions), so fail-open/silent-failure hunting has no code surface
here — noted, not skipped.

## Stage 1 — spec compliance

Diffed `41c16c736e3cc4b2b331757081c90a24f2ba977d..87e60330104e63b2efa366852a5e514f8eb73b36` per file
(never `..HEAD`, never `merge-base origin/main HEAD`).

**SC-01 — MET.** `git show 87e6033:.harness/harness/docs/DECISIONS.md`, region between `## DEC-174 `
and `## DEC-175 ` headings. "Every gate was green" absent (checked as a literal substring across the
whole region, whitespace-normalized). Read each clause separately, not by one file-global grep:
- (a) unsupported-mode fact: present — "was no gate at all: `--check` was never a supported mode."
- (b) pre-`ffbdbfa1` write-path fall-through: present — "Before argv validation landed at commit
  `ffbdbfa1` (2026-08-05, …), `main()` read `stdout_mode = "--stdout" in sys.argv[1:]`, so an
  unrecognized `--check` fell through to the WRITE path: the run regenerated `DECISIONS-INDEX.md`
  in place and exited 0"
- (c) exit 0 could not prove drift: present — "…so it could not prove index drift one way or the
  other."
- (d) `--stdout | diff` read-only form: present, exact contiguous string — "The read-only form is
  `gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md`."
All four clauses read in the region as committed at the pin; none is a line-wrap artifact.

**SC-02 — MET.** `git show 87e6033:.../FEAT-05-pyyaml-file-parsers/STATE.md`. "All four gates
green" replaced by "**Three gates green:**" — no longer claims four including `--check` 0. Each
clause checked separately:
- (a) unsupported mode: "was no gate at all — `--check` was never a supported mode"
- (b) fall-through: "before argv validation landed at `ffbdbfa1` (2026-08-05) an unrecognized
  argument fell through to the WRITE path"
- (c) could not prove drift: "that exit 0 was a regeneration of `DECISIONS-INDEX.md` that
  overwrites exactly the drift a check would have reported; it could not prove index drift."
- (d) `--stdout | diff` form: "Use `gen-decisions-index.py --stdout | diff -
  .harness/harness/docs/DECISIONS-INDEX.md`."
- (e) correction date 2026-09-06: "**Corrected 2026-09-06 under BUG-148:**"
All five present.

**SC-03 — MET.** `git diff -U5 41c16c7..87e6033 -- .harness/harness/docs/DECISIONS.md` shows
exactly one hunk, `@@ -4303,12 +4303,20 @@`, whose only `+`/`-` lines are the evidence sentence
(two old lines replaced by ten new ones). Read the surrounding region at both endpoints in full:
the DEC-174 heading, the three-bullet defect list ("four `.harness` YAML files…", "…normative
refusal template…", "…could not report a did-nothing state…"), the "Self-hosting caught none of
these" paragraph, and the carve-out table are byte-identical at base and pin — none appears as a
diff line, confirmed by direct comparison of both full regions, not inference from the hunk
header alone.

**SC-05 — MET.** `git diff --name-only 41c16c7..87e6033` lists 23 paths. Two are the docs product
files (`DECISIONS.md`, `DECISIONS-INDEX.md`), one is `FEAT-05-pyyaml-file-parsers/STATE.md`, and
the remaining 20 are all under `.harness/harness/features/BUG-148-gate-record-correction/**` (this
feature's own BRIEF/STATE/feature.json/plan.yaml/notes/observations). No `BUG-440-…` or
`FEAT-55-…` path appears — the dead-end contamination from `merge-base origin/main HEAD` (`8bdc2477`)
that the BRIEF warns about is correctly absent because SC-05 uses `41c16c7`, not that merge-base.

Cross-checked against qa's own note (`notes/qa-BUG-148-2026-09-06.md`): it reads the diff at an
earlier, ancestor commit `f60d5d27` (17 paths, confirmed `git merge-base --is-ancestor f60d5d27
87e6033` → true) rather than the pin. Verified this does not stale the SC-04 evidence: `git diff
--stat f60d5d27..87e6033 -- DECISIONS.md DECISIONS-INDEX.md STATE.md` is empty — the three product
files are byte-identical between qa's commit and the pin, so qa's integration-test run (`ok` on
both named tests) still applies unchanged at `87e6033`. Not a finding; recorded so the next reader
doesn't have to re-derive it.

REQ-04 cross-check: DEC-174's ruling paragraph ("A change to the enforcement layer is made
**directly**…"), its carve-out table, and the naming of the three genuinely-green gates
(`run-unit-tests.sh`, `check-docs.sh`, `check-state.sh`) are unchanged at the pin versus base —
confirmed by direct comparison of the full DEC-174 region text, not the hunk alone.

## Stage 2 — prose quality on a governing record

**DEC-174 ruling support, unweakened.** The corrected evidence paragraph still leads into "Those
three real gates were green while:" and the existing three-bullet defect list, unchanged. The
ruling itself ("A change to the enforcement layer is made directly…") sits later in the same
region and is untouched. If anything the corrected version is a *stronger* argument for DEC-174's
point than the original: it is now on record that even the three gates that genuinely ran caught
none of the listed defects, rather than resting on a fourth gate that never ran at all. No
weakening, no rewrite of the ruling.

**FEAT-05 passage reads as correction, not apology.** "**Corrected 2026-09-06 under BUG-148:**" is
inline, factual, present-tense-of-the-record register — it states what was wrong and why, in the
same paragraph as the surviving true claims ("Three gates green… Every `.harness/**/*.yaml`
parses."), not as a footnote or an appended dated sub-section. No hedging, no "we apologize" or
"in hindsight" language. Matches BRIEF's REQ-01/D-05-ruling-1 intent (in-place rewrite, DEC-174's
treatment, no new section) — consistent with the 7-heading count at the pin being unchanged from
base (verified: `grep -c '^## '` on both files at both commits = 7).

**Side-by-side same-terms read (D-05 ruling 3 — binds T-02 to T-01's mechanism, no automated check
exists for this, so this read is the only evidence).** Placed both mechanism clauses next to each
other:

| clause | T-01 (DECISIONS.md) | T-02 (STATE.md) |
|---|---|---|
| unsupported mode | "was no gate at all: `--check` was never a supported mode." | "was no gate at all — `--check` was never a supported mode," |
| fall-through | "an unrecognized `--check` fell through to the WRITE path" | "an unrecognized argument fell through to the WRITE path" |
| regeneration / could-not-prove-drift | "the run regenerated `DECISIONS-INDEX.md` in place and exited 0, and a regeneration overwrites exactly the drift a check would have reported, so it could not prove index drift one way or the other." | "that exit 0 was a regeneration of `DECISIONS-INDEX.md` that overwrites exactly the drift a check would have reported; it could not prove index drift." |

All three clauses are present in both, in matching order, and the third clause shares the
identical load-bearing phrase "overwrites exactly the drift a check would have reported" verbatim
in both records. Neither text drops the fall-through or the regeneration (the narrower mechanism
D-05/T-02's intent explicitly forbids) — both keep all three facts. Same mechanism, same terms.
Holds.

**DECISIONS-INDEX.md — anchors-only, confirmed by direct comparison, not assertion.**
`git diff --stat` shows 42/42 (all rows from DEC-175 to the file's tail, one `@line` shift of +8
matching DEC-174's paragraph growing by 8 lines). Ran:
`diff <(git show 41c16c7:…INDEX.md | sed -E 's/@[0-9]+/@X/') <(git show 87e6033:…INDEX.md | sed -E 's/@[0-9]+/@X/')`
→ empty diff, i.e. **byte-identical once the `@NNN` anchors are normalized out.** No row's TEXT
moved; only the per-row source anchors shifted. Anchors-only holds, established mechanically, not
by spot-check.

**code_grade.** Ran `code-grade.py --base "$(git merge-base origin/main 87e6033)" --head 87e6033`:
output `PASSING: 0`, no graded records, exit 0 — no changed Python function in that
repository-derived range. `code_grade: n_a` is correct per protocol (no changed Python path).

## Findings

None. Zero findings after reading every clause of SC-01/SC-02 separately, diffing the full
DECISIONS.md and STATE.md regions at both endpoints, and mechanically confirming the
DECISIONS-INDEX.md regeneration is anchors-only. No scope creep, no omission, no value mismatch,
no fail-open branch (no code changed), no silent-failure path, no shallow-module or seam concern
(no module boundary in this diff — pure prose).

## Dead ends re-confirmed, not re-opened

- `--stdout | diff` read-only form stays in both records (D-05 ruling 2 / PF-54450f537e28244ae73d9c0e48ae4efe) — confirmed present verbatim in both.
- FEAT-05 STATE.md's 170-line/7-heading pre-existing shape violation — left as found, heading count verified unchanged (7) at both commits.
- The date asymmetry (FEAT-05 names 2026-09-06, DEC-174 does not) — REQ-01 requires it only of FEAT-05; not re-raised.
- `git merge-base origin/main HEAD` not used as SC-03/SC-05 baseline; used only for the code-grade range per the tool's own protocol, which is a distinct, independent computation from the spec-compliance diff base.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Docs-only correction meets all four inspection SCs; both records state the same mechanism in the same terms; DECISIONS-INDEX regeneration confirmed anchors-only; zero findings."
  severity_max: none
  findings: 0
  must_fix: []
  spec_violations: []
  code_grade: n_a
  reviewed: "41c16c736e3cc4b2b331757081c90a24f2ba977d..87e60330104e63b2efa366852a5e514f8eb73b36"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-148-gate-record-correction/.harness/harness/features/BUG-148-gate-record-correction/notes/review-harness-code-reviewer-c0.md
```
