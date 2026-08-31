# Code review — ship panel — FEAT-38-decisions-current-knowledge

Reviewed at `review_sha` `635cd3baa950e7a48eaad9c3a1990560b61bf7c0`, diff base `7ebfc9eb9cb77939b325f559d64e6b0cbb22d907`,
`99bb52c` used only where the assignment names it (SC-14/SC-16/SC-18 baseline; it is mid-feature, taken
*after* the amendment-fold segments and *before* the claims-deletion segment — confirmed by walking the
commit graph, not assumed). No source edited; HEAD not moved. All counting done in Python against
`git show <sha>:<path>` content, never shell grep, per the stated hazard.

## BLUF

**PASS.** No `must_fix`. SC-17 (mine to own): **met** — 7 of 59 rows re-derived from their actual call
sites plus a full independent reproduction of the 70-file sweep and the 11/45/14 verdict-count
arithmetic; every verdict I checked is correct. SC-16: **met** — DEC-205's three counting sentences and
its full considered-and-refused paragraph verified word-for-word against both sides of the fold, with
`file:line` anchors at `review_sha`. One real, non-blocking finding: 5 of the 6 decision citations this
feature's own diff rewrites in `board_lifecycle.py` point at a successor entry (`DEC-203`) that does not
actually contain the claim attributed to it — exactly the semantic-citation-rot class DEC-205 admits no
gate catches, caught here by a human reading the diff, as designed.

## SC-17 — the argv-class audit (THE ASSIGNMENT)

**Sweep reproduction — reran the verbatim command in Python against `review_sha` content** (not the
working tree): `git grep -lE 'subprocess|shlex|shell=|Popen|os\.system|eval\('` over
`.claude/skills/harness/bin` → **70 files, exact set match** against the table's 70 filenames (zero in
either direction). The command note itself lands on the same set it claims.

**Verdict-count arithmetic** — 11 TEXT-DERIVED-ARGV + 45 FIXED-LITERAL-ARGV + 14 NO-EXECUTION = 70,
cross-checked: the Group A (9) + Group B (2) breakdown sums to 11; the 14 NO-EXECUTION names I extracted
independently match the table; 70 − 11 − 14 = 45 is consistent.

**Rows I re-derived from the actual call site at `review_sha`** — 7 of the 59 mine to own, biased toward
the highest-risk categories named in the dispatch (a `test_kinds` cmd reader, the runner this feature
edits, the frozen anchor file, `shell=True` sites, and the trickiest NO-EXECUTION claims):

| file | table verdict | what I checked | result |
|---|---|---|---|
| `run-unit-tests.sh` | FIXED-LITERAL-ARGV | line 149 `python3 "$BIN_DIR/$s"` (loop over the two literal bash arrays), line 101 `python3 -I - <<'KINDCHECK'` heredoc — both exact at the cited lines; `detect` is only set-compared (lines 108-130), never placed in argv | **correct** |
| `check-decision-anchors.py` | FIXED-LITERAL-ARGV | line 111 `subprocess.run(["git", "ls-files"], ...)` — both elements literal, wrapped in try/except that exits 2 (fail-closed) on failure | **correct** |
| `check-domain.sh` | FIXED-LITERAL-ARGV | line 1478 `_subprocess.run(["git", "-C", _checkout] + _argv, ...)` — `_argv` is one of two literal lists (1476-1477), `_checkout` from the worktree sweep | **correct** |
| `test-run-unit-tests-kinds.py` | FIXED-LITERAL-ARGV | line 47 `subprocess.run(["bash", RUNNER, "--check-kinds"], ...)` — the mutated `detect` value travels via a fixture `harness.json` path in `HARNESS_JSON`, never into this argv | **correct** |
| `gh-close-gate.py` | NO-EXECUTION | zero occurrences of `subprocess`/`os.system`/`eval(`/`Popen` in the whole file; the only enumeration-pattern hit is 7 uses of `shlex.shlex(...)` at line 47 to tokenize a *proposed* command string for an allow/deny decision | **correct** |
| `test-factory-gh.py` | NO-EXECUTION | `subprocess` appears ~100 times as substring but `subprocess.run(` and `subprocess.Popen(` as calls: **zero** hits — all attribute-rebind fakes (`fgh.subprocess.run = fake_run`) | **correct** |
| `test-hooks-install.py` | FIXED-LITERAL-ARGV | all five `shell=True` sites (218, 222, 223, 235, 236) pass `STEP1_CMD`/`STEP2_CMD_SET`/`STEP2_CMD_GET`, module constants at lines 57-59, verbatim strings — nothing parsed reaches them | **correct** |

**No mislabeled verdict found in this sample.** SC-17: **met.**

## SC-16 — DEC-205's count and its considered-and-refused paragraph

Anchored on content (`What was considered and refused`), not line numbers, since both sides moved.

- **Heading**, `DECISIONS.md:6223` (review_sha): *"...and **one mechanical check** guards it"* — was
  *"...and **two mechanical checks** guard it"* at `99bb52c`. Corrected.
- **Enumeration-intro sentence**, `:6255`: *"**One mechanical check** guards this file, and only
  one."* — was *"**Two mechanical checks** guard this file, and only two."* Corrected.
- **Closing sentence of the considered-and-refused paragraph**, `:6270-6272`: *"Neither becomes cheap
  merely because **the one check** above is open rather than closed — that openness is exactly why
  **the one that is in is the mechanical one**."* — was *"...because **the two checks** above are open
  ... why **the two that are in are the mechanical ones**."* Corrected, singular/plural grammar
  adjusted, not just the numeral.
- **Item 2 ("Executable claims") is fully removed**, not left describing a re-run claim or command
  grammar — only item 1 ("Anchor rot") remains.
- **Rule 1 (anchor rot) text is byte-identical** between `99bb52c` and `review_sha` — diffed directly,
  zero difference.
- **Full paragraph, quoted both sides** (`DECISIONS.md:6266-6272` at review_sha):
  > **What was considered and refused, recorded so a future scan does not re-suggest it.** A
  > **referenced-file watch** (M3) — flagging every entry whose cited files changed — was declined: it
  > hands over a review list and proves nothing, so its output is work, not verification. A **periodic
  > LLM audit of design claims** (M4) was declined as a gate: its judgement decays the moment code
  > moves, so it is worth running once as a sweep and worthless standing as a check. Neither becomes
  > cheap merely because the one check above is open rather than closed — that openness is exactly why
  > the one that is in is the mechanical one.

  Identical at `99bb52c` except the final clause's numeral/plurality, quoted above. Both refusals (M3,
  M4) and their stated reasons survive unchanged. Nothing in it still asserts the deleted marker
  mechanism — confirmed the two `<!-- claim: ... -->` markers that sat immediately below this paragraph
  at `99bb52c` are gone entirely at `review_sha`.
- **`DECISIONS-INDEX.md` row** — index line 205 both sides: `99bb52c`'s ruling half read *"...and
  **two mechanical checks** — anchor rot and executable `claim:` markers — guard it."*; `review_sha`'s
  reads *"...and **one mechanical check** — anchor rot — guards it."* Names one check, no marker
  mechanism. Correct.
- **DEC-205 gains no positive guidance about what an entry does instead** (Contract 4) — confirmed, the
  removed item 2 leaves no replacement text.

**SC-16: met**, all four `file:line` comparisons verified directly, not inherited.

## Spec compliance — the automated criteria I re-derived myself (not trusted from the gate record)

All measured fresh in Python against `git show <sha>:<path>` content at `review_sha` unless noted:

- **SC-01**: zero lines matching `^###\s+DEC-[0-9]+\s+amendment` and zero matching `^\*\*Amendment` — **met**.
- **SC-02**: all 15 deleted ids (19,20,37,67,82,88,92,102,103,104,137,140,186,192,196) — zero `## DEC-<id>`
  headings, zero appearances (row id or `refs:`) in `DECISIONS-INDEX.md`, checked per-id — **met**.
- **SC-03**: `## DEC-90 — STRUCK` and its strike record present — **met**.
- **SC-04**: swept every tracked file outside `.harness/harness/features/`, `.harness/notes/`,
  `.harness/logs/` for `am\.\d+`, `DEC-\d+\s+amendment` (same-line only — a naive cross-line variant of
  my own sweep false-hit on DEC-205's own prose narrating *"the former DEC-145 amendment 3"*, which is
  legitimate history-in-current-truth, not a live construct; re-run per-line, zero hits) and the 15
  deleted ids — **met**.
- **SC-05**: zero `SUPERSEDED BY`, zero `am.` span tokens, zero `am-span` header text in
  `DECISIONS-INDEX.md`; `gen-decisions-index.py --stdout` piped through Python and diffed byte-for-byte
  against the checked-in index — **identical, exit 0** — **met**.
- **SC-06**: all seven named symbols (`AMEND_HEADING_RE`, `AMEND_BOLD_RE`, `SUPERSESSION_VERB_RE`,
  `BODY_SUPERSESSION_RE`, `compute_amendments`, `format_amendment_span`,
  `compute_supersession_target`) absent from `gen-decisions-index.py`; orphan detection present and
  read (lines 175-190) and its refs-graph filter (`compute_refs`, `if n == own_num or n not in
  live_nums: continue`) confirmed to implement DEC-205's issue-686 clause — verified `DEC-161` (the
  motivating example) appears in neither a live heading nor the regenerated index's `refs:` graph —
  **met**.
- **SC-07**: ran `test-gen-decisions-index.py` read-only — 11/11 cases print `ok -`, including
  `test_no_amendment_construct_survives_in_the_authority`; the `ok -` line is named literally in the
  source, matching "cannot be deleted with the suite still green." An independently-recorded live
  mutation proof for this exact case (planted `\n### DEC-99 amendment 1\n`, monkeypatched `REPO_ROOT`,
  called the function directly, observed False then True) exists in the frozen
  `notes/review-harness-qa-c0.md` and predates the SIMPLIFY apply; I additionally confirmed the
  SIMPLIFY apply (the `parse_decisions` 3-tuple → 2-tuple narrowing) touches nothing this case reads and
  the case still passes post-apply — **met**.
- **SC-08**: ran `check-decision-anchors.py --file <(...)` (process substitution, no file write) three
  ways myself: against `base_sha` content → `examined 32 anchor(s), 3 failed`, exactly the three
  `feature.yaml` anchors; against `review_sha` content → `examined 20 anchor(s), 0 failed`, exit 0;
  against `review_sha` content plus one fabricated anchor appended in-memory → `examined 21 anchor(s), 1
  failed`, exit 1 — all three reproduced live — **met**.
- **SC-10**: ran the full `run-unit-tests.sh` myself — **exit 0, zero lines starting `FAIL`**, 55/55
  registered `test-*.py` scripts present in the bin dir and named in the union of both arrays (drift
  detector's own precondition independently confirmed clean) — **met**.
- **SC-12**: front matter no longer contains "APPEND-ONLY"; `harness-documentor.md` P-01 rewritten from
  "WHEN appending an amendment... DO place it INSIDE the amended decision's own section" to "WHEN a
  decision proves wrong DO rewrite that entry in place... keep the falsified claim inside it as one
  undated clause" — states the new convention in the same breath it retires the old one — **met**.
- **SC-14**: `check-decision-claims.py` / `test-check-decision-claims.py` absent from `git ls-tree -r`;
  zero `<!-- claim:` lines in `DECISIONS.md`; zero tracked files outside the three excluded dirs
  containing the string `check-decision-claims` — all three assertions run independently — **met**.
- **SC-15**: `.harness/harness.json`'s `integration.detect` contains no `check-decision-claims` and does
  contain `test-check-decision-anchors.py`; simulated the runner's own KIND-DRIFT set-comparison in
  Python against the live 27-unit/28-integration arrays and the live `detect` string — **zero
  discrepancies either direction** — **met**.
- **SC-18**: `check-decision-anchors.py` / `test-check-decision-anchors.py` at `review_sha` hashed
  `sha256` and compared byte-for-byte against `99bb52c` — **identical**, hashes match the two given in
  the dispatch exactly; both names present in `run-unit-tests.sh`'s `INTEGRATION_SCRIPTS` and in
  `harness.json`'s `integration.detect` — **met**. Not re-reported per Contract 2 (the stale-docstring
  gap is already on the backlog).

No criterion's stated evidence failed to establish it once re-derived.

## Code quality — the rest of the changed surface

**`run-unit-tests.sh`** — read in full. The MISCONFIGURED drift detector sweeps `test-*.py` under
`BIN_DIR` with no `nullglob`; an empty directory would leave the literal glob pattern as the loop
variable, fail the membership check, and **exit 2 loudly** rather than silently pass — this is the
inverse of a fail-open gate, by design. The KIND-DRIFT python block treats a missing/unparseable
`harness.json` or a non-string `detect` as `sys.exit(2)`, propagated by the outer bash as `exit 2` —
also loud, never a skip. Both are exactly what their own comments claim, verified by reading the
branches, not by reading the comments. **Looked, nothing to report.**

**`check-decision-claims.py` + `test-check-decision-claims.py`** — deleted, confirmed absent from
`git ls-tree`, from both `run-unit-tests.sh` arrays, and from `harness.json`'s detect field (SC-14/15
above). **Looked, nothing to report** (the deletion is the point of T-24; nothing survives to review).

**`gen-decisions-index.py` + `test-gen-decisions-index.py`** — the SIMPLIFY apply (3-tuple →
2-tuple `parse_decisions` return, drop the unread `"title"` key) has exactly one call site
(`build_index`, line 171), confirmed via search — no second destructuring site left assuming three
values, no dangling reference to `"title"`. Orphan detection and the refs-graph filter both still
function (SC-06 above, behaviourally proved, not just grepped for). **Looked, nothing to report.**

**`check-decision-anchors.py` + `test-check-decision-anchors.py`** — frozen, byte-identical (SC-18).
Not re-reviewed for content per Contract 2.

**`.harness/harness.json`** — the one-entry T-25 change is correct and symmetric with the runner
(SC-15). Relative to the merge-base (before this feature branch started), the claims checker was never
present in `detect` at all — it was added and removed within this same feature's own history — so the
diff against `base_sha` shows only `test-check-decision-anchors.py` being **added**, which is exactly
right.

**`board_lifecycle.py`** — diffstat is 6 comment/docstring hunks only (`DEC-186`→`DEC-203` ×3,
`DEC-192`→`DEC-203` ×3), no code change. One of the six (line 433, the case-sensitivity claim) is
content-accurate: DEC-203 item 6 does state "case sensitive, byte for byte." **The other five are not:**

- **Finding [low, non-blocking]** — `board_lifecycle.py:104,151,949` all attribute "GhError propagates
  as exit 4, never conflated with 0 or 1 — the inverse of gh-sync.py's mirror posture" to `DEC-203`.
  I read `DEC-203`'s full ~17.5k-char entry (`DECISIONS.md:5982-6222`) end to end in Python: it never
  contains the strings "exit 4", "GhError", "mirror posture" or "inverse" anywhere. I also read
  `DEC-186`'s full pre-strike body at `base_sha` (12.4k chars): same result, zero matches. **This
  citation was never true of `DEC-186` either** — it is a pre-existing miscitation this feature's
  citation-repointing swap (successor-map: `DEC-186`→`DEC-203`) mechanically carried forward rather than
  corrected. Failure scenario: a future reader who opens `DEC-203` to understand why the audit uses
  exit 4 for a `GhError` finds no such rule there and has to re-derive it from the code alone — exactly
  the semantic-citation-rot class `DEC-205` documents as now undetectable by any gate.
- **Finding [low, non-blocking]** — `board_lifecycle.py:447,488` both attribute "`Abandoned` gets no
  board column" to `DEC-203`. Same method: `DEC-203`'s full body never mentions "Abandoned." I found
  the actual source of that exact claim — *"`Abandoned` is not a station and has no writer"* — living in
  `DEC-138` (`DECISIONS.md:2972`, within `DEC-138`'s span starting `:2925`), a decision this feature
  itself folds and rewrites (one of SC-11's 15). I also read `DEC-192`'s full pre-strike body (3.3k
  chars): it never mentions "Abandoned" either. Same pre-existing-miscitation shape as above, and the
  better successor (`DEC-138`) was sitting in the very file this feature was editing throughout.

Both findings are **non-blocking** (`low`): the code's runtime behaviour is unaffected in every case —
this is a citation-accuracy gap in comments/docstrings, not a functional defect, and the underlying
miscitation pre-dates this feature. I report rather than fold into `must_fix` because REQ-04's literal
text ("no ... citation to a decision id that has no entry") is satisfied — `DEC-203` exists — so this
does not violate the letter of any REQ/SC I can find; it violates the citation-repointing's evident
intent. Recommendation: fold `board_lifecycle.py:104,151,949` to cite the entry that actually documents
the audit's exit-4 posture (not found under any live DEC during this review — worth a follow-up grep
for "control-plane" or "audit posture" wording, or simply state the rule inline without a citation),
and `:447,488` to `DEC-138` instead of `DEC-203`. Not a decision question — this is a pure citation
correction with no plan/scope implication, but I did not verify a search of the WHOLE document for the
exit-4 rule's true home, so I'm not asserting there is no correct id at all, only that `DEC-203` is not
it.

**`check-domain.sh`** — one comment hunk, `"DEC-171 am.1's logic"` → `"DEC-171's logic"`. Verified: the
FAIL-CLOSED-on-missing-PyYAML rule this comment describes is present in `DEC-171`'s live body
(`DECISIONS.md:4139-4142`, *"`check-domain.sh` and `bash-write-guard.sh` fail CLOSED on a missing
PyYAML"*) — content-accurate. **Looked, nothing to report.**

**`.github/workflows/tests.yml`** — two comment hunks. `"DEC-171 am.1"` → `"DEC-171"` (same PyYAML rule,
same file, content confirmed as above). `"a plan.yaml \`status:\` enum under DEC-192"` → `"...under
DEC-203"`: at first read this looked like a second miscitation (DEC-192/DEC-203 govern the
*feature*-level board station field, not a *task*-level `status:` enum) — but `test-check-plan-routes.py`'s
own `case_25` (unrelated file, not touched by this diff) titles itself in its own docstring *"(25)
DEC-203 board truth: a task's status..."* — so the comment's citation matches what the test it describes
already, independently, cites. Not a defect. **Looked, nothing to report** beyond the above.

## Full changed-surface census (explicit per-area verdict, per the no-pre-emptive-skips instruction)

| area | verdict |
|---|---|
| `run-unit-tests.sh` | reviewed, clean |
| `check-decision-claims.py` + test (deleted) | confirmed fully absent, three ways |
| `gen-decisions-index.py` + test | reviewed, clean, SIMPLIFY apply verified non-dangling |
| `check-decision-anchors.py` + test (frozen) | byte-identical confirmed, not re-reviewed per Contract 2 |
| `.harness/harness.json` | reviewed, symmetric with runner, clean |
| `board_lifecycle.py` | reviewed — **2 low findings** (citation accuracy, non-blocking) |
| `check-domain.sh` | reviewed, clean |
| `.github/workflows/tests.yml` | reviewed, clean |
| `DECISIONS.md` / `DECISIONS-INDEX.md` | reviewed for SC-01–SC-06, SC-08, SC-12, SC-14, SC-16, clean |

## What I did not check

SC-11 (per-entry pre/post-fold read-back) is `verify: inspection` and not in my assigned automated-SC
list; I did not re-grade it — it belongs to whoever the panel assigns it to. I did not exhaustively
re-derive all 59 of the FIXED-LITERAL-ARGV/NO-EXECUTION rows, per the dispatch's own "need not re-derive
all 59." The 52 rows I did not individually re-check remain as recorded in the audit note.
