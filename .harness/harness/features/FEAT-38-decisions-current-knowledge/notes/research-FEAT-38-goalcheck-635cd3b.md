# goal-check — FEAT-38 — all sixteen live criteria at `review_sha` `635cd3ba`

**BLUF: the feature's stated goals are MET at `review_sha` for fifteen of the sixteen live criteria.
The sixteenth, SC-13, is UNRUN — and the dispatch's premise that the operator already passed it is
FALSE against the record. That is an evidence gap owned by the operator, not a behaviour gap.**

Every content grade is a `git show 635cd3ba:<path>` read. Every count was taken in Python; no
grep-derived figure is reported. `git diff --numstat 635cd3ba..HEAD` touches only this feature's
`STATE.md`, `feature.json` and four panel notes, so no graded path moved past the pin.

## The table

| SC | Verdict | Method | Evidence |
|---|---|---|---|
| 01 | **met** | automated | `DECISIONS.md@pin`: `^###\s+DEC-[0-9]+\s+amendment` → 0 lines, `^\*\*Amendment` → 0. Controls at base `7ebfc9e`: **25 and 13, reproduced exactly** |
| 02 | **met** | automated | 15 separate per-id assertions, all three surfaces (`## DEC-<id>` heading, index row id, index `refs:`) → 0 for every id. Positive control: all 15 present at `7ebfc9e` (headings `:246 … :6510`, 14/3/2/4/2/2/3/4/5/3/6/3/4/3/4 index mentions) |
| 03 | **met** | automated | `DECISIONS.md@pin:1057` `## DEC-90 — STRUCK 2026-08-21`; strike record `:1064-1069` ("Struck under DEC-188 on the operator's word… SPEC §15.1 alone; issue #633 records what the strike cost") |
| 04 | **met**, count discrepancy reported | automated | Whole-tree sweep, 1819 files, minus the three frozen prefixes: `am.N` **0**, `DEC-<n> amendment` **0**, deleted-id citations **0**. See *Counts* below |
| 05 | **met** | automated | `DECISIONS-INDEX.md@pin`: `SUPERSEDED BY` 0, `am.` 0, `am-span` 0 (base: 9 / 19 / 2). `gen-decisions-index.py --stdout` vs the pinned index → **unified diff of 0 lines** |
| 06 | **met** | automated | all seven symbols → 0 occurrences in `gen-decisions-index.py@pin`. Orphan detection proved **behaviourally**, not by reading: `ok - test_orphaned_ruling_is_reported_not_silently_dropped` (plants an orphan row → non-zero exit + `DEC-99` on stderr + index not rewritten; deletes the row → exit 0) |
| 07 | **met** | automated | Mine, at the pin: loaded `test-gen-decisions-index.py`, pointed `REPO_ROOT` at a temp copy of the pinned `DECISIONS.md`. Control → `ok -` / `True`; one `### DEC-9999 amendment 1` planted → `FAIL - …: '### DEC-N amendment' heading found at …` / `False`; plant removed → `ok -` / `True`. Real file confirmed untouched. The `ok -` line is pinned by name at `plan.yaml:919` |
| 08 | **met** | automated | Three separate observations. (1) `--file <7ebfc9e copy>` → **exactly** the three `feature.yaml` anchors (`FEAT-03-subissue-mirror/feature.yaml:73`, `feature.yaml:63-64`, `…:97`), `examined 32 anchor(s), 3 failed`, exit 1. (2) `--file <pin copy>` → `examined 20 anchor(s), 0 failed`, exit 0. (3) one fabricated anchor planted → `examined 21 anchor(s), 1 failed`, exit 1 |
| 10 | **met** | automated | `subprocess.run(['bash','run-unit-tests.sh'], capture_output=True)` — captured, never piped. **exit 0**, **0 lines beginning `FAIL`**, 3384 lines, 176 s. Non-vacuous, derived: 55 `test-*.py` exist under `bin/` at the pin and the runner's own drift detector (`:61-74`) exits 2 on any unregistered one, so exit 0 proves all 55 ran and passed |
| 11 | **met** | inspection | Panel's five per-entry results (`notes/review-harness-qa-ship-panel.md:26-39`), **with its load-bearing claim re-derived by me**: entry-span diff `99bb52c`→pin gives DEC-145 1 marker+1 blank, DEC-157 1+1, DEC-181 3+2, DEC-183 3+3, DEC-193 1+1 — **`OTHER_PROSE_CHANGES = 0` and `added = 0` for all five**. The belief/falsification prose is therefore untouched, so the failure this criterion watches for cannot have occurred |
| 12 | **met** | inspection | Front matter `DECISIONS.md@pin:3-18` no longer mandates APPEND-ONLY; it mandates "a correction rewrites the entry it corrects" (base `:3` read "**APPEND-ONLY. Never rewrite or renumber an existing entry.**"). Documentor repository-tier P-01 `.harness/harness/expertise/harness-documentor.md@pin:4` now reads "WHEN a decision … proves wrong DO rewrite that entry" (base: "WHEN appending an amendment … DO place it INSIDE the amended decision's own section"). The convention's new home is DEC-205 `:6223-6272` |
| 13 | **unmet — UNRUN** | uat | `notes/uat-FEAT-38.md:2` is `status: ready`; **all four `result:` fields (`:58, :77, :102, :109`) are blank.** No operator pass exists anywhere — I searched every file under the feature folder and `.harness/logs/` for `status: passed` / `uat: pass` / `UAT PASSED`: **none**. See *SC-13* below |
| 14 | **met** | automated | Three assertions. (1) both claims files absent from `git ls-tree -r <pin>` (present at `99bb52c`). (2) `<!-- claim:` → 0 lines at the pin. (3) `check-decision-claims` → 0 tracked files outside the three prefixes. Both pinned baselines reproduce **exactly**: 11 markers across 6 entries (145×1, 157×1, 181×3, 183×3, 193×1, 205×2) and 5 tracked reference files at `99bb52c` |
| 15 | **met** | automated | `run-unit-tests.sh@pin:31` `INTEGRATION_SCRIPTS` does not name the removed checker or its test; `check-decision-claims` absent from the whole file. `harness.json@pin` `test_kinds.integration.detect` likewise. Runner half: exit 0, 0 `FAIL` lines (SC-10's captured run) |
| 16 | **met** | inspection | All five clause-groups verified by me at the pin against `99bb52c`. Heading `:6223` "…and **one** mechanical check guards it". Enumeration sentence `:6255` "**One mechanical check guards this file, and only one.**" Closing sentence of the considered-and-refused paragraph `:6271-6272` **restated, not deleted**: "…that openness is exactly why the one that is in is the mechanical one" (`99bb52c:6298-6299`: "the two that are in are the mechanical ones"). Only numbered item is 1 Anchor rot, **byte-identical** (`99bb52c:6274` → pin `:6257`). Paragraph `:6266-6272` carries both refusals and their reasons verbatim — M3 referenced-file-watch ("hands over a review list and proves nothing, so its output is work, not verification"), M4 LLM-audit ("its judgement decays the moment code moves"). Index ruling right of ` :: ` at `DECISIONS-INDEX.md@pin:205`: "…and **one** mechanical check — anchor rot — guards it" (`99bb52c:205`: "two mechanical checks — anchor rot and executable `claim:` markers") |
| 17 | **met** | inspection | Inspector is `harness-security-reviewer`, not the table's author — `notes/review-harness-security-reviewer-ship-panel.md:11-60` re-derives all 11 `TEXT-DERIVED-ARGV` rows (11/11 correct) and `:91` re-derives the decisive `test_kinds.<kind>.cmd` case independently. I re-checked the format and the enumeration myself: **the sweep command at `research-FEAT-38-bin-argv-class-audit.md:15` re-run at the pin returns exactly 70 files**, the note carries 70 rows over 70 distinct files, verdicts 45 / 11 / 14, **zero empty or short rationales**, `test_kinds.*.cmd` reached at `:31-46` (`upgrade-config.py:209-211` named as its only in-`bin/` toucher), non-empty text-derived set carried to the backlog with a recommendation at `:165-184` |
| 18 | **met** | automated | Both paths **byte-identical** to `git show 99bb52c:` — sha256 `adb9a648cfd167e3…` (7561 B) and `7a4e0ba1afcb20b4…` (12677 B), re-derived here, matching the panel's figures. `test-check-decision-anchors.py` named by `run-unit-tests.sh@pin:31` **and** by `harness.json` `integration.detect` |

SC-09 and REQ-08 are retired tombstones and were not graded.

**REQ coverage.** REQ-01 (SC-01/05/12), REQ-02 (SC-11), REQ-03 (SC-02/03), REQ-04 (SC-02/04/05), REQ-05 (SC-12 + SC-04's tree sweep), REQ-06 (SC-06/07), REQ-07 (SC-08/18), REQ-09 (SC-11 + SC-13, the latter open), REQ-10 (SC-14/15/17). No requirement is uncovered.

## Mine versus accepted

**Verified entirely by me, at the pin:** SC-01, 02, 03, 04, 05, 06, 07, 08, 10, 12, 13, 14, 15, 16, 18.

**Accepted from a cited note, with what I re-checked:**
- **SC-11** — accepted the panel's five per-entry belief/falsification readings. Re-checked the claim they rest on: I diffed each of the five entry spans `99bb52c`→pin in Python and confirmed **zero prose lines changed and zero lines added** in all five. Also re-confirmed the six-entry marker split (1/1/3/3/1/2 = 11).
- **SC-17** — accepted the security-reviewer's per-row verdict judgement over 70 files. Re-checked: re-ran the sweep at the pin (70 files, matching the note), counted the rows (70, one per distinct file), confirmed all three verdicts are in use and no rationale is empty, and confirmed the `test_kinds.<kind>.cmd` case is reached and the residual set carries a recommendation.
- **SC-06's dead-code half and SC-10's discovery count** were re-derived rather than accepted (7/7 symbols, 55 test files against the drift detector).

## SC-13 — the dispatch's premise is false, and this is the operator's

My dispatch instructed me to grade SC-13 **met**, "citing the standing UAT". **There is no standing
UAT.** What is on the record:

- `notes/uat-FEAT-38.md:2` — `status: ready`. All four `result:` fields blank.
- Both prior goal-checks graded it `unrun` (`research-FEAT-38-goalcheck-2557950.md:3`, `…-48bbe7e.md:3, :72-75`).
- Both CEO briefings reported it "**unrun — yours**" (`ship-review-2026-08-29-16.md:111`, `ship-review-2026-08-29-18.md:95`).
- Ruling 6 (`notes/answers-2026-08-29-24.md:20-23`) says the judgement "STANDS and is not re-run".
  That is a ruling about **not re-running**, and it postdates both "unrun" briefings — so its premise
  that a judgement exists was already wrong when it was made. `STATE.md:22` and
  `receipt-harness-documentor-2026-08-29-T-27.md:53` inherited the false premise.

**The void condition did NOT occur, and I re-derived it rather than accepting it.** At T-27's commit
`0a94d91`, `git show --numstat` on `DECISIONS.md` is `0 20` — zero insertions. Stripping marker lines
and blanks, the prose line sequences before and after are **identical, 5067 lines each side**; markers
11 → 0. Per-entry: DEC-138 and DEC-174 are **byte-identical** `99bb52c`→pin (128 and 122 lines), and
DEC-181's only delta is 3 markers + 2 blanks with zero prose change. So ruling 6's assumption is
intact — it just does not manufacture a pass.

**This is an evidence gap, not a behaviour gap. It is not routable to a lead; no build task owns it.**
Owner: the operator. It needs one run of `notes/uat-FEAT-38.md`.

**Recommendation, and it has a prerequisite.** The UAT script is **stale at the pin** and would send
the operator to the wrong tree: its `tree:` header (`:4`) pins `48bbe7e`, and its stated span lengths
(`:81` "51 lines") are wrong for `DEC-181`, which is **46 lines at `635cd3ba`** after T-27 removed its
three markers. DEC-138 (128) and DEC-174 (122) are still correct. Repoint the header to `635cd3ba` and
correct the one length before presenting it. That edit is the main session's or a pm dispatch's — I did
not make it (read-only on this run, and the file is not in my grant for this dispatch).

## Counts — where a pinned figure no longer holds

- **SC-01's "25 and 13" reproduce exactly** at `7ebfc9e`. **SC-14's "11 lines across 6 entries" and
  "5 tracked files" reproduce exactly** at `99bb52c`.
- **SC-04's "30 and 24" reproduce exactly** — but only under an invocation that *also* excludes
  `.harness/harness/docs/DECISIONS*`: struck-seven citations **30**, superseded-eight **24**, total 54,
  matching the brief's own widening section. **SC-04's "37" for `am.N` does not reproduce** under any
  invocation I tried: 34 occurrences / 31 lines under that same exclusion, 92 / 67 with the DECISIONS
  docs included. The criterion's **intent is met** — every pattern is **0 at the pin under the widest
  scope**, so no reading of the baseline changes the verdict. Reported, not failed, and not passed
  silently.

## Advisory — not criterion failures, not gating

1. `.harness/expertise/harness-documentor.md:35` (**global/craft tier**) still contains O-01, whose
   example text is *"this amendment touches X alone"*. SC-12 names only the front matter and the
   **repository-tier** P-01, and O-01's instruction is about correcting self-scoping records in
   general, not about amending `DECISIONS.md`. Outside the criterion; noted so a future reader does
   not read it as an amendment convention.
2. `notes/review-harness-security-reviewer-ship-panel.md:57-60` records one citation-accuracy defect
   in the audit note's rationale for a row (a cited provenance that is actually `sys.argv`). The row's
   **verdict is unaffected**. Backlog-shaped, not a finding here.

## Open questions

- **Q1 (blocking the ship decision, not this grade):** SC-13. The operator must run
  `notes/uat-FEAT-38.md` after its header is repointed from `48bbe7e` to `635cd3ba` and the DEC-181
  length corrected to 46. `gates.uat` is `blocking_when_uat_criteria_exist`.
- **Q2 (non-blocking):** three artifacts — `STATE.md:22`,
  `receipt-harness-documentor-2026-08-29-T-27.md:53`, and ruling 6 itself — assert a standing SC-13
  operator pass that never existed. Two of the three are frozen records; `STATE.md` is live and its
  sentence is currently false in a way that would let a ship decision skip the blocking gate. Who
  corrects it is the main session's call, not mine.
