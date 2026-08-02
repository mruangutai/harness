# PLAN — FEAT-04 Decisions index

**BLUF.** One new stdlib generator, one new test file, one new 190-line index, four line-range-bounded backfill
batches dispatched **one at a time** (`## Ordering`), and two edits that no agent domain covers. The only real logic is
preservation-by-DEC-number and it gets three named tests. `check-docs.sh` is **not modified** — the
index enters its scan scope as an ordinary file and pays for residual hits with per-row markers, so
the central absence assertion cannot be satisfied by weakening the gate.

Baseline pinned at `f723194`, recorded in `feature.yaml` under `baseline:` — cited, not re-derived.

## Decisions

- **D-01: `docs/harness/DECISIONS-INDEX.md` is a scanned file and stays one. `check-docs.sh` is not
  touched.** Verified at source: `check-docs.sh:81-95` globs `docs/harness/**/*.md` and the only
  exclusions are basename `DECISIONS.md` and any path containing `/runs/`. So the index lands inside
  the scanner. Residual hits are paid per row with an inline `<!-- ok-stale -->`, added only to rows
  the checker actually flags — not blanket-applied.
  *Rejected — adding the index to the exclusion filter.* One line, and superficially principled: the
  index paraphrases rulings much as the registry quotes stale wording. But it costs coverage on ~165
  rows to buy silence on a handful, and this feature's central constraint is an absence assertion
  (SC-07: exit 0, 45 patterns) which a gutted checker satisfies just as well — the exact mechanism
  DEC-169 documents. *Rejected — blanket `<!-- ok-stale -->` on every row.* ~169 lines of noise for
  a result functionally identical to the exclusion, only harder to see.
  Two facts make the targeted version cheap: `check-docs.sh:136-137` skips any line containing
  `superseded`, `no longer`, `corrected`, `inverted`, `an earlier` or `was wrong`, so every
  `— SUPERSEDED BY DEC-NN` row auto-skips; and per `feature.yaml baseline`, exactly 1 of 169 DEC
  *titles* would be flagged. D-03 and D-07 keep rulings in the same low-risk register.
  **What that title figure does and does not bound:** it counts *titles*, which D-03 omits from rows,
  so the population this decision prices is the 169 hand-written rulings — a population no measurement
  bounds until T-08 records `grep -c 'ok-stale'`, which is why the trigger below is a threshold rather
  than a prediction.
  **Escalation trigger, not a silent workaround:** if T-08 finds more than 20 flagged rows, that is
  evidence the residual is materially larger than this decision assumes — T-08 stops and returns
  `ESCALATE` rather than adding 60 markers.
  **The residual is confirmed, not theoretical — it tripped inside this feature's own planning
  artifacts before a single index row existed.** Quoting one superseded phrase owned by `## DEC-120`
  into SC-08 and the A-4 row produced two real STALE hits, because the scan covers `.harness/**/*.md`
  (everything outside `/runs/`) and not only `docs/`; both were cleared by the same per-line
  `<!-- ok-stale -->` escape this decision prices per row, which therefore demonstrably works outside
  `docs/` too. Whoever writes rulings should expect the same trip anywhere they quote retired wording.
- **D-02: amendments fold into the parent decision's row; they get no rows of their own.** The parent
  row carries an `am.1-am.N` span in its mechanical segment, and the ruling states the decision *as
  currently amended*. Rationale: a row is an open-or-skip filter, and `DEC-138 am.7` is not
  independently actionable — if any amendment matters you open the parent entry anyway. One row per
  decision also keeps grep recall intact, since the amendment span sits on the same physical line the
  topic tags do. *Trade-off accepted:* an amendment whose subject differs sharply from its parent's
  is findable only via the parent's tags.
  **(MF-1) The `am.N` form this decision originally built on does not exist in the authority.** Run
  02 measured `DEC-[0-9]+ am\.[0-9]` at **0** occurrences. The authority carries **two** real forms,
  and both are in scope — an extraction rule that silently ignores the second would be a new instance
  of the defect MF-1 names:
  1. **Heading form**, 9 of them (`feature.yaml baseline: amendment_headings: 9`):
     `### DEC-NNN amendment` or `### DEC-NNN amendment N`, at `:3217 :3264 :3285 :3300 :3308 :3327
     :4244 :4271 :4299`. Keyed by the **captured** DEC number, never by physical position — measured
     instance: `### DEC-137 amendment 2` at `:3327` sits inside DEC-138's body region, so a positional
     rule would misattribute it (A-5). An unnumbered `amendment` is **am.1**. Measured result:
     DEC-137 → `am.1-am.2`, DEC-138 → `am.1-am.7`.
  2. **Inline bold form**, 2 of them (`amendments_inline: 2`): `**Amendment (same day):**` at `:3530`
     and `**Amendment 2 (2026-07-29) …**` at `:3536`. These carry **no DEC number**, so they are the
     one case keyed **positionally** — attributed to the enclosing `^## DEC-` heading, measured as
     DEC-145 (`:3493`, next heading `:3553`). Unnumbered = am.1, so DEC-145 → `am.1-am.2`.
  **Precedence and contiguity, stated rather than assumed:** if one decision ever carries both forms,
  the heading form's captured numbers win and inline forms are numbered after the highest heading
  number. If the numbers for one decision are non-contiguous, the generator emits the enumerated list
  (`am.1,am.3`) rather than a span that hides the gap. Neither case exists at `f723194`; both are
  specified so the gap is visible if it appears.
- **D-03: verbatim titles are omitted from rows; the ruling replaces them.** The settled position is
  that titles are insufficient — a title says a decision *exists* about a topic, not what it ruled,
  which is most of the cost being removed. Carrying both would duplicate the row's purpose. Not
  chosen to dodge the one known title flag; under D-01 that flag would have cost one marker, which is
  affordable. *Trade-off accepted:* title-only keywords absent from the ruling are recovered by the
  controlled-vocabulary tags (D-05), not by substring match on the title.
- **D-04: the row set is defined by fence-guarded parsing, and there are 169 live decisions, not
  170.** The baseline's "170 top-level DECs" is a `grep -c '^## DEC-'` artifact. Measured: `## DEC-83`
  matches at lines 1001 and 1583, and **line 1583 is inside a code fence** — an illustration of the
  heading format, not a live declaration. Once the fence toggle runs (`check-docs.sh:41-48` — the
  toggle at `:44-46` **plus** the `if infence: continue` skip at `:47-48`; the range is cited whole
  because a doer copying the narrower range gets the toggle without the skip, A-1), every DEC number
  is unique and the live count is 169. Consequences, all load-bearing:
  the generator emits 169 rows; SC-01 counts distinct numbers *after* fence-stripping; and any test
  computing an expected count with a raw `re.findall` gets 170 and fails for a reason unrelated to the
  generator (T-01 test 1 pins this).
  The generator still keys rows by DEC number and **asserts uniqueness after fence-stripping, exiting
  non-zero with the colliding number if that ever breaks** — a real duplicate would make
  preservation-by-DEC-number ambiguous, which is the one thing this feature must get right, so the
  invariant is enforced rather than assumed. No `dup:` annotation is emitted; today there is nothing
  to annotate.
- **D-05: topic tags come from a controlled vocabulary hard-coded in the generator**, matched as
  lowercase substrings against the decision's body, up to four tags by hit count, ties alphabetical.
  *Rejected — free-form keyword extraction or an LLM pass.* Neither is deterministic, so neither is
  regenerable without churn, and a tag set that shifts on every run makes `git diff` useless as the
  record of what changed (SC-05 would never hold). A fixed vocabulary is testable and its gaps are
  visible.
- **D-06: the ~169-row backfill is four line-range-bounded batches, dispatched one at a time — never
  concurrently.** (MF-6: the earlier phrasing named four spawns with no ordering, which read as an
  invitation to parallel dispatch. They are four *sequential* dispatches; no boundary moved.) A single
  spawn
  reading all 4,413 lines is precisely the cost pattern this feature exists to remove: cache-read
  cost scales with context size times turns, so one large context is superlinearly more expensive
  than four bounded ones for the same total lines. Ranges are line-balanced (~1,100 lines each), not
  count-balanced, because lines are what cost money. Boundaries are pinned in T-04..T-07 from
  measured heading line numbers. See `## Ordering` below: T-03..T-08 all mutate one file and are
  strictly serial.
- **D-07: rulings are written affirmatively — present tense, what the rule *is*, never a description
  of what it replaced — and are at most 30 words.** Load-bearing for D-01: a ruling that paraphrases
  what a superseding decision
  overturned will reach for the old wording and trip the checker. "Skills live flat one level under
  `.claude/skills/`" is in register; a sentence describing the arrangement that preceded it is not.
  The 30-word bound is mechanical, not advisory: count only the text right of ` :: `, excluding any
  generated `— SUPERSEDED BY DEC-NN` suffix and excluding any `<!-- ok-stale -->` marker.
- **D-08: this feature declares no new `<!-- stale: ... -->` marker.** The disciplined instinct is to
  declare one for the whole-read wording T-09 removes, so its return is caught forever. But every
  marker moves the emitted pattern count, and the pinned baseline this feature must hold is 45. SC-09's
  named grep pair carries the enforcement instead. Raised as Q1, non-blocking — if the user wants the
  marker, the SC re-pins to 46 and this decision reverses cheaply.

## Tasks

### T-01 — tests for the generator, written first

owner: harness-backend-dev · change_type: logic · traces: REQ-04, REQ-05, REQ-08

Create `.claude/skills/harness/bin/test-gen-decisions-index.py` — `python3` stdlib only, plain
`assert` + a `main()` returning exit 0/1, matching the shape of the existing
`.claude/skills/harness/bin/test-check-state.py`. **Six** tests (five, plus MF-5's orphan test), these
names:

1. `test_row_per_distinct_dec_matches_authority` — run the generator against the real
   `docs/harness/DECISIONS.md`; assert the row count equals the number of distinct DEC numbers,
   computed in the test rather than hard-coded so the assertion survives the next appended decision.
   **The test must build its expected set through the same fence toggle the generator uses, not a raw
   `re.findall(r'^## (DEC-\d+)', text, re.M)`** — measured, the raw regex yields 170 and the
   fence-guarded parse yields 169, because `## DEC-83` at line 1583 sits inside a code fence (D-04).
   A raw-regex expectation fails here for a reason that has nothing to do with the generator. Assert
   both numbers explicitly — expected 169, and 170 for the raw count — so the divergence is documented
   by the test rather than rediscovered.
2. `test_preserves_hand_written_rulings_by_dec_number` — build a synthetic authority in a
   `tempfile.TemporaryDirectory()` with 5 decisions, and an index whose 5 rows carry distinct
   hand-written rulings. Append a 6th decision **between** existing ones, regenerate, and assert:
   all 5 original rulings are present byte-identical, each still on the row for its original DEC
   number, and the new decision's row carries the `RULING PENDING` sentinel. This is the only real
   logic in the feature and this is its test.
3. `test_preserves_inline_ok_stale_marker_on_a_row` — same fixture, one ruling carrying
   `<!-- ok-stale -->`; assert the regenerated row is byte-identical including the marker. Without
   this, the first regeneration after T-08 silently strips the markers and the checker goes red with
   nothing having caught it.
4. `test_checker_flags_planted_stale_phrase_in_index` — build a temp project tree containing
   `docs/harness/DECISIONS.md` (one `## DEC-01` heading declaring a single
   `<!-- stale: "fabricated placeholder phrase" -->`) and `docs/harness/DECISIONS-INDEX.md` with one
   row whose ruling contains that phrase. `subprocess.run` the repo's `check-docs.sh` with
   `CLAUDE_PROJECT_DIR` set to the temp tree; assert exit 1 and that stdout contains both the index
   path and `DEC-01`. Then rewrite the same row with `<!-- ok-stale -->` appended and assert exit 0.
   The temp tree **must** contain `docs/harness/DECISIONS.md` or the script exits 1 on "not found"
   and the test passes for the wrong reason.
5. `test_committed_index_is_complete_and_within_budget` — on the committed
   `docs/harness/DECISIONS-INDEX.md`: `<!-- index-contract v1 -->` present, at most 260 lines, zero
   `RULING PENDING` occurrences, **and** — the presence half MF-3 requires — every `^- DEC-` row has
   **at least 20 non-whitespace characters of hand-written prose** in the segment after ` :: `,
   measured **after applying this task's own strip rule** (drop all trailing `— SUPERSEDED BY DEC-\d+`
   clauses and any `<!-- ok-stale -->`, per T-02's merge bullets). Measuring the raw segment reopens the
   hole: `DEC-19` is targeted by DEC-84 and DEC-85, so its row carries ~44 characters of
   generator-written clause text and would clear a naive floor with zero prose. Bare absence of the
   sentinel
   is satisfiable by deleting it and writing nothing (`- DEC-42 @498 [] refs:  :: ` would pass SC-01
   and an absence-only SC-02 together), which is DEC-169's failure mode; the length floor is what makes
   the criterion mean "written", not "not-sentinel".
   **(MF-2) The skip predicate is file-absence ONLY.** If `docs/harness/DECISIONS-INDEX.md` does not
   exist, print `SKIP test_committed_index_is_complete_and_within_budget` and return pass. If the file
   exists and carries the sentinel, or carries a short ruling, the test **FAILS** — it does not skip.
   The earlier "absent **or** still carries the sentinel" predicate swallowed the exact state REQ-09
   exists to catch: post-ship, the sentinel state would have skipped and passed, leaving REQ-09 with no
   mechanical teeth. The consequence is deliberate and is stated in `## Ordering`: between T-03 and
   T-07 the unit gate is red on this test, and T-03..T-06 do not invoke the runner. T-02's verify
   (index absent → the SKIP line) and T-07's verify (complete → no SKIP line) both still hold.
   **(A-5) The failure message names its remedy**, because post-ship it fires inside unrelated
   features: `FAIL … <n> row(s) unwritten in docs/harness/DECISIONS-INDEX.md — a decision was appended
   without its ruling. Run .claude/skills/harness/bin/gen-decisions-index.py and write the ruling after
   ' :: ' on each listed row, in this commit (REQ-09).` List the offending DEC numbers.
6. `test_orphaned_ruling_is_reported_not_silently_dropped` — MF-5. In a `tempfile.TemporaryDirectory()`,
   build an authority of 3 decisions and an index whose 4 rows include a hand-written ruling for a
   `DEC-` number **not present** in the authority (deleted or renumbered upstream). Assert the generator
   **exits non-zero** and names that DEC number on stderr, and that it does **not** rewrite the file.
   Then delete the orphan row and assert the same fixture exits 0 — both directions, so the check
   cannot pass by always failing. A silently dropped hand-written ruling is the one failure that makes
   the whole index untrustworthy, so it is a hard error rather than a warning.

Then, as a numbered step of this task and not a footnote: **edit
`.claude/skills/harness/bin/run-unit-tests.sh` and add `"test-gen-decisions-index.py"` to the
`SCRIPTS` array.** The runner's drift detector (`run-unit-tests.sh`, the `MISCONFIGURED` branch)
exits 2 on any `test-*.py` under `bin/` absent from that list, so skipping this step makes the whole
unit gate exit 2 rather than running.

verify: `CLAUDE_PROJECT_DIR=$(pwd) .claude/skills/harness/bin/run-unit-tests.sh; echo $?` → output
contains `FAIL test-gen-decisions-index.py` and no `MISCONFIGURED` line, and the exit code is 1 — the
red state. Exit 2 means the SCRIPTS edit was missed; exit 0 means the tests are not testing anything.

### T-02 — the generator

owner: harness-backend-dev · change_type: logic · traces: REQ-01, REQ-02, REQ-03, REQ-04, REQ-05, REQ-09

Create `.claude/skills/harness/bin/gen-decisions-index.py`, executable, `python3` stdlib only,
`cd`-ing to `CLAUDE_PROJECT_DIR` or cwd exactly as `check-docs.sh:26` does.

Reads `docs/harness/DECISIONS.md`, writes `docs/harness/DECISIONS-INDEX.md` in place. Flags: no args
= write in place; `--stdout` = write to stdout, touch nothing. **(A-5) `--check` is dropped** — it had
no caller and no test, and giving it one (a `check-state.sh` INV) is a task this feature did not scope.
SC-05's `generator && git diff --exit-code` is the same assertion with a real caller.

Parsing:

- Toggle on lines whose `lstrip()` starts with ``` and skip fenced content — the same guard as
  `check-docs.sh:41-48` (the toggle is `:44-46`, the `if infence: continue` skip is `:47-48`; copy the
  whole range, A-1). A heading or marker shown inside a fence is documentation of the format, not
  a live declaration. **(A-1, accepted) Fenced lines are dropped BEFORE all extraction**, not only
  before heading detection — headings, amendments, the reference graph and tag scoring all see the
  de-fenced body. Concrete instance this fixes: `## DEC-83` inside the fence at `:1582-1586` would
  otherwise inject a spurious `DEC-83` into the enclosing decision's reference graph.
- Headings: `^##\s+(DEC-(\d+))\b`. A decision's body runs from its heading to the line before the
  next `^## ` heading, or EOF.
- Key = the zero-padded DEC number. After fence-stripping, numbers are unique (D-04); the generator
  **asserts that** and exits non-zero naming the collision rather than silently merging two entries
  into one row, because a collision would make ruling-preservation ambiguous. No `dup:` annotation is
  emitted — there is nothing to annotate at `f723194`.
- Amendments — **(MF-1)** two patterns, per D-02. The form `DEC-(\d+)\s+am\.(\d+)` **does not exist in
  the authority** (0 occurrences) and is not used.
  1. `^###\s+DEC-(\d+)\s+amendment(?:\s+(\d+))?\b` — keyed by the **captured** group 1, never by the
     enclosing heading. Group 2 absent ⇒ number 1.
  2. `^\*\*Amendment(?:\s+(\d+))?\b` — no DEC number to capture, so keyed **positionally** to the
     enclosing `^## DEC-` heading. Group 1 absent ⇒ number 1. If a decision carried both forms, the
     heading form's numbers win and inline ones continue past the highest heading number.
  Emit a contiguous span as `am.1-am.N`, a single amendment as `am.1`, and a **non-contiguous** set as
  the enumerated list `am.1,am.3` — never a span that hides a gap. Measured at `f723194`: DEC-137
  `am.1-am.2`, DEC-138 `am.1-am.7`, DEC-145 `am.1-am.2`.
- Reference graph: every `DEC-\d+` occurrence in the body except the owner's own number, deduped,
  sorted numerically, emitted space-separated.
- Supersession — **(MF-4a)** case-insensitive matching over the whole title is wrong and was measured
  wrong. For each decision, take the title line's **em-dash trailing segment** and match
  `—\s*(SUPERSEDES|CORRECTS|INVERTS)\s+(DEC-\d+...)` **UPPERCASE only**. Take targets from that
  **first clause only, stopping at the first comma.** Each named target's row gains a trailing
  `— SUPERSEDED BY DEC-<owner>`.
  Why uppercase-and-first-clause, both halves load-bearing against measured rows: `DECISIONS.md:1001`
  is `## DEC-83 — Nesting default is 3, not off — CORRECTS DEC-82, and DEC-82 corrected DEC-39`. A
  greedy multi-target read marks DEC-39 as `SUPERSEDED BY DEC-83`, which is **false** — the second
  clause names its own subject. Stopping at the comma yields the one true target, DEC-82. Uppercase
  anchoring alone also drops DEC-83's lowercase `corrected` tail, DEC-81's `corrections` (`:968`) and
  DEC-146's `inverted` (`:3553`) for free, leaving exactly the 9 real cases the baseline counts.
- Tags: module-level `TOPIC_VOCAB: dict[str, tuple[str, ...]]` per D-05. Seed vocabulary — `org`,
  `cost`, `gates`, `tests`, `tdd`, `skills`, `hooks`, `domain`, `github`, `expertise`, `docs`, `map`,
  `orchestrator`, `dispatch`, `digest`, `approval`, `security`, `deploy`, `state`, `brief`, `plan`,
  `qa`, `worktree`, `budget` — each mapping to a tuple of lowercase substrings.
  **(A-3, accepted — pinned literally, because any single choice satisfies SC-05 so the idempotency
  gate cannot catch a divergence between implementers):** score a tag as
  `sum(body_lower.count(sub) for sub in TOPIC_VOCAB[tag])` — total occurrences, not distinct substrings
  hit — then select and emit in the order `sorted(tags, key=lambda t: (-score[t], t))[:4]`. Omit
  zero-score tags. The **title line is part of the body** under this task's own body definition, which
  is what makes D-03's "tags recover title-only keywords" true.

Row format — **one physical line per decision**, which is what makes the six-keyword auto-skip work
per row and what structurally caps ruling length (SC-11). Fabricated example, deliberately not a real
ruling:

```
- DEC-42 @498 [gates,tests] refs: DEC-07 DEC-19 :: Placeholder — one affirmative sentence.
```

Everything left of ` :: ` is generated; everything right of it is hand-written and preserved.

Merge on regeneration: if the index exists, parse each existing row as
`^- (DEC-\d+) .*? :: (.*)$`. Group 2 holds three kinds of content — the hand-written ruling prose, any
inline `<!-- ok-stale -->`, and any `— SUPERSEDED BY DEC-NN` clauses the previous run emitted. Only the
first is preserved verbatim; the other two are **generator-recomputed**, so they are stripped and
re-emitted in a canonical order. Precisely:

- **(MF-4b) Strip ALL trailing clauses, not a singular one, and in any order they appear.** From the
  end of group 2, repeatedly remove `\s*—\s*SUPERSEDED BY DEC-\d+\s*$` and `\s*<!--\s*ok-stale\s*-->\s*$`
  until neither matches; remember whether an `ok-stale` marker was seen. Measured reason the singular
  form breaks: `DEC-19` is targeted by **both** DEC-84 (`:1036`, CORRECTS) and DEC-85 (`:1047`, INVERTS),
  so its row carries two clauses. Stripping one and re-appending two grows the row on **every**
  regeneration, and SC-05's `git diff --exit-code` then never holds.
- **(MF-4) Canonical emission order, so the merge is idempotent and normalizing:**
  `<ruling prose> [— SUPERSEDED BY DEC-a] [— SUPERSEDED BY DEC-b] … [<!-- ok-stale -->]` — supersession
  clauses first, ascending by target-owner DEC number, then the `ok-stale` marker **last**, exactly once
  if it was present. A row that arrives in any other order (a human appended the marker before the
  clause) is rewritten into this order on the next run and is stable from then on. Position is
  immaterial to `check-docs.sh:133`, which skips any line containing `ok-stale` — so pinning the order
  costs nothing and buys idempotency.
- A DEC with no prior row gets `⚠ RULING PENDING`.
- **(MF-5) Orphan detection — a preserved key with no live DEC is a hard error, never a silent drop.**
  After parsing both files, any DEC number that has a row (with non-sentinel ruling text) but **no live
  heading** in the authority means a decision was deleted or renumbered upstream and a hand-written
  ruling is about to vanish. The generator writes nothing, prints
  `ORPHAN: <DEC-NN …> has a ruling in the index but no live heading in docs/harness/DECISIONS.md` to
  stderr, and **exits non-zero**. T-01 test 6 covers both directions.

Header — generator-emitted, so REQ-03's framing cannot be edited away and SC-03 holds for free:

```
<!-- index-contract v1 -->
<!-- GENERATED except the text after ` :: ` on each row.
     Regenerate: .claude/skills/harness/bin/gen-decisions-index.py -->

# DECISIONS — index

**A row is an open-or-skip filter, never the rule itself.** Its only job is to answer "do I open this
entry?" Never act on a ruling here: open `docs/harness/DECISIONS.md` at the `@line` anchor and read
the entry. Rows written during the one-time backfill are second-hand paraphrase.

**Never read the authority whole (DEC-150).** Grep this index, then open the two or three entries that
bear on your task. Decisions cited in a dispatch are a floor, not a ceiling.

**Adding a decision:** its author writes its ruling here, in the same commit that appends the entry.

Row: `- DEC-NN @<line> [tags] refs: <graph> :: <ruling>`.
A row ending `— SUPERSEDED BY DEC-NN` is one you must not act on.
```

verify: `CLAUDE_PROJECT_DIR=$(pwd) .claude/skills/harness/bin/run-unit-tests.sh; echo $?` → exit 0,
output contains `PASS test-gen-decisions-index.py`, contains
`SKIP test_committed_index_is_complete_and_within_budget` (the index does not exist yet), and contains
no `MISCONFIGURED` line. The unit gate is green from this task onward; the one unrun assertion is
named in the output rather than left to inference.

### T-03 — first generation: all rows, no rulings

owner: harness-documentor · change_type: docs · traces: REQ-02, REQ-03

Run `.claude/skills/harness/bin/gen-decisions-index.py` to create
`docs/harness/DECISIONS-INDEX.md` from scratch. Commit it with the header and 169 rows, every ruling
the `RULING PENDING` sentinel. Do not hand-edit a single row in this task — its whole purpose is to
prove the generated half stands alone before any paraphrase enters. Do not open
`docs/harness/DECISIONS.md` for this task; the generator reads it.

verify: `grep -c '^- DEC-' docs/harness/DECISIONS-INDEX.md` → `169`, and
`grep -c 'RULING PENDING' docs/harness/DECISIONS-INDEX.md` → `169`.

### T-04 — backfill batch 1 of 4: `DEC-01` … `DEC-88`

owner: harness-documentor · change_type: docs · traces: REQ-01, REQ-05

Read **only** lines 1–1099 of `docs/harness/DECISIONS.md` — `sed -n '1,1099p'`. Boundary measured:
`## DEC-89` begins at line 1100. Write one affirmative present-tense ruling per D-07 into the text
right of ` :: ` on each of the 88 rows for `DEC-01` … `DEC-88`, replacing the sentinel. One sentence,
one physical line, stating what the rule is. Do not edit anything left of ` :: `. Do not open any
other part of the authority — reading past the range is the cost pattern D-06 exists to prevent.

verify: `grep -c 'RULING PENDING' docs/harness/DECISIONS-INDEX.md` → `81`.

### T-05 — backfill batch 2 of 4: `DEC-89` … `DEC-115`

owner: harness-documentor · change_type: docs · traces: REQ-01, REQ-05

As T-04, over `sed -n '1100,2238p' docs/harness/DECISIONS.md` (`## DEC-116` begins at 2239), for the
27 rows `DEC-89` … `DEC-115`.

verify: `grep -c 'RULING PENDING' docs/harness/DECISIONS-INDEX.md` → `54`.

### T-06 — backfill batch 3 of 4: `DEC-116` … `DEC-138`

owner: harness-documentor · change_type: docs · traces: REQ-01, REQ-05

As T-04, over `sed -n '2239,3342p' docs/harness/DECISIONS.md` (`## DEC-139` begins at 3343), for the
23 rows `DEC-116` … `DEC-138`.

**(MF-1) Correction to this task's earlier note, which was false as written.** It said "`DEC-138`
carries the amendment span" — with the dead `am.N` regex no span existed at all, and "the" implied it
was the only one (DEC-137 and DEC-145 also carry amendments, per D-02). What is true and measured:
`DEC-138` carries `am.1-am.7`, and **three of its seven amendment headings sit outside this task's
range** — `:4244`, `:4271`, `:4299`. Per D-02 the ruling states the decision *as currently amended*, so
writing DEC-138's ruling from `2239,3342p` alone would state it as amended through am.4 while claiming
otherwise, and the burn-down verify (31) would not catch it.

Therefore this task takes **one bounded extra read** — `sed -n '4244,4375p' docs/harness/DECISIONS.md`,
**132 lines against this task's ~1,104-line main range** — before writing DEC-138's ruling. The range is
contiguous rather than a set of narrow per-heading windows because each amendment's operative text has to
arrive whole: run 05 measured am.6's operative rule as the provenance blockquote at `:4278-4279`, which
sits well below its own heading, and a ruling written from truncated text claims "as currently amended"
without being it — the defect MF-1's fix exists to remove. The extra read stays bounded and D-06's cost
argument holds at 132 lines. Do not widen the main
range; the boundaries are correct and are not moved. Conversely, ignore `### DEC-137 amendment 2` at
`:3327`: it sits physically inside DEC-138's body region but is keyed by its **captured** number to
DEC-137, which belongs to T-06's range as a row but whose amendment text is DEC-137's, not DEC-138's
(A-5). DEC-138's tags and reference graph will absorb that amendment's words — inherent to the file's
layout, accepted, not fought.

verify: `grep -c 'RULING PENDING' docs/harness/DECISIONS-INDEX.md` → `31`.

### T-07 — backfill batch 4 of 4: `DEC-139` … `DEC-169`

owner: harness-documentor · change_type: docs · traces: REQ-01, REQ-05

As T-04, over `sed -n '3343,4413p' docs/harness/DECISIONS.md`, for the 31 rows `DEC-139` …
`DEC-169`.

Two amendment facts inside this range, per D-02, so they are not mis-assigned: the amendment headings
at `:4244 :4271 :4299` are **DEC-138's** (am.5-am.7) and DEC-138's row belongs to T-06, not to you —
leave it alone. **Where DEC-168's own body ends — 132 of the 155 lines in its body region belong to
another decision:** `## DEC-168` is at `:4221` and its own prose ends at `:4243`; `:4244-4375` is that
DEC-138 amendment text sitting inside DEC-168's body region, and the next `^## ` heading, DEC-169, is at
`:4376`. **Write DEC-168's ruling from `:4221-4243` only.** This is human misattribution — a wrong
ruling — and is a different case from the generator artifact T-06 accepts, where the cost is one
unnecessary open. No boundary moves: `3343,4413p` stands.
The two inline `**Amendment …**` paragraphs at `:3530` and `:3536` carry no DEC number
and are keyed positionally to the enclosing heading, **DEC-145** (`:3493`), whose row is yours: state it
as amended through am.2.

verify: `grep -c 'RULING PENDING' docs/harness/DECISIONS-INDEX.md` → `0`, and
`CLAUDE_PROJECT_DIR=$(pwd) .claude/skills/harness/bin/run-unit-tests.sh` → exit 0 with
`PASS test-gen-decisions-index.py` **and no `SKIP` line in the output** — test 5 now has a complete
index to assert against, and the absent skip line is the proof it actually ran.

### T-08 — residual marker pass, then idempotency

owner: harness-documentor · change_type: docs · traces: REQ-08, D-01

1. Run `.claude/skills/harness/bin/check-docs.sh`. For each `STALE docs/harness/DECISIONS-INDEX.md:N`
   line it prints, append ` <!-- ok-stale -->` to the end of that row — a per-row escape, never a
   blanket one, and never a change to `check-docs.sh`. **(MF-4) The marker goes LAST on the row, after
   any `— SUPERSEDED BY DEC-NN` clause** — T-02's canonical order. Put it before a clause and step 4's
   regeneration rewrites the row, which shows up as SC-05's `git diff --exit-code` failing rather than
   as anything obviously wrong here.
2. **If more than 20 rows are flagged, stop and return `ESCALATE`** — the residual is materially larger
   than D-01 assumes and the exclusion-filter alternative deserves a second look with real numbers. Do not add the markers.
3. Rewrite any flagged ruling that is describing what a decision replaced rather than what it rules
   (D-07); prefer rewriting to marking, since a marked row is a row the checker no longer watches.
4. Re-run the generator to confirm the markers survive the merge path (SC-04's third test covers this
   in permanent form).

verify: `.claude/skills/harness/bin/check-docs.sh; echo $?` → exit 0, output contains
`checked 45 superseded pattern(s)`; then
`.claude/skills/harness/bin/gen-decisions-index.py && git diff --exit-code
docs/harness/DECISIONS-INDEX.md; echo $?` → 0. `grep -c 'ok-stale' docs/harness/DECISIONS-INDEX.md`
is recorded in the DIGEST as the measured residual.

### T-09 — repoint the entry-point instruction

owner: **main-session** — no agent domain covers `CLAUDE.md`; see the routing note below ·
change_type: docs · traces: REQ-06

Edit `/Users/molchairuangutai/GitHub/harness/CLAUDE.md`:

- Line 43's opening clause is the whole-read instruction — it tells the reader to read the authority
  before changing any harness doc. Read it at source rather than from this plan, which deliberately
  does not reproduce the wording (D-08's Q1 would make that phrase a declared stale pattern, and this
  file is itself scanned: `check-docs.sh:92` keeps `.harness` feature docs in scope). Replace it with
  an instruction naming `docs/harness/DECISIONS-INDEX.md` as what to read, then
  grepping and opening the two or three entries it names, and stating plainly that the authority is
  not read whole (DEC-150). Keep the sentence about `check-docs.sh` and its registry — that is still
  true and unrelated.
- Line 36's design-docs table row gains `DECISIONS-INDEX.md` beside `DECISIONS.md`, marked as the
  index and the entry point.

**Drafting constraint on your replacement text — binding, and stated here because the doer cannot see
SC-09.** SC-09's widened absence grep (below, and in BRIEF SC-09) matches
`(read|consult|review|check)` within 40 characters of `DECISIONS.md`. Your own new sentence trips it if
it names the authority path in the same sentence as a reading verb. Two rules, satisfy both:

1. **The authority path `docs/harness/DECISIONS.md` appears only in a negated construction, on the same
   physical LINE as its negation.** `grep` is line-based and this file is hard-wrapped, so a sentence
   that satisfies the rule but wraps between the negation and the path leaves the absence grep at 1 hit
   — the criterion would then self-trip on the very edit meant to clear it. The line carrying the path
   must itself carry `never` or `not` within 20 characters of `read`/`whole` (e.g. "…is never read
   whole"); do not let the wrap separate them. The SC's absence grep excludes lines matching
   `(never|not)[[:space:]][^.]{0,20}(read|whole)` for exactly this reason.
2. Prefer naming `docs/harness/DECISIONS-INDEX.md` as the thing to read. `DECISIONS\.md` in the pattern
   cannot match `DECISIONS-INDEX.md`, so the positive instruction is free of the constraint.
3. **The retained `check-docs.sh` registry sentence keeps the bare filename `DECISIONS.md`, not the full
   path, and keeps it clear of a reading verb.** Rendered as "…its registry is
   `docs/harness/DECISIONS.md`", the span from "checker" to the path is ~37 characters with no
   intervening period and pattern 1 matches text you were told to preserve. Today's line 45 already
   writes the bare filename on its own line; keep it that way.

verify: `grep -n 'DECISIONS-INDEX.md' CLAUDE.md` → at least 2 hits (0 at `f723194` — discriminating);
and the widened absence pair from SC-09, over `CLAUDE.md .claude/skills .claude/agents
.harness/expertise`, → 0 hits each. Measured at `f723194` the first absence grep returns exactly 1
(`CLAUDE.md:43`), so it is discriminating; the second returns 0 and is a standing guard, not a
discriminating check. The surface set includes `.harness/expertise/**` because a `SubagentStart` hook
injects it into every spawn — see SC-09.

### T-10 — ship the discipline where it travels

owner: **main-session** — no agent domain covers `.claude/skills/harness-handoff/SKILL.md` ·
change_type: docs · traces: REQ-07

Add a short section to `.claude/skills/harness-handoff/SKILL.md` (73 lines today; keep the addition
under ~15). It carries the **universal** discipline only, no repo-specific path — verified in the
grilling that `deploy.sh` ships skills, agents, commands and templates and never `CLAUDE.md`, that
`harness-init` writes no `CLAUDE.md` either, and that kaya's copy of this skill is byte-identical, so
this is the surface that reaches every deployed project on the next `deploy.sh --apply`. Content:

- Decisions cited in a dispatch are a **floor, never a ceiling** — the same framing the qa gate uses
  for the test matrix. A cited list means *at minimum these*.
- Never read an authority file whole; read its index and open what bears on your task.
- The four go-broad triggers, numbered `(1)`…`(4)` so SC-10's count is checkable: (1) a cited
  decision references an uncited one — with a dense reference graph this is the common case, so
  following it is a lookup, not a judgement call; (2) you are about to judge something the citations
  do not cover; (3) your own Expertise implies a rule they omit; (4) "surely this was decided
  already" fires.

verify: `grep -c '^\s*[0-9])\|([1-4])' .claude/skills/harness-handoff/SKILL.md` → at least 4, and
`grep -n 'floor' .claude/skills/harness-handoff/SKILL.md` → at least 1 hit (0 at `f723194` — both
discriminating).

## Ordering — MF-6, and the orchestrator needs both halves

**T-03 … T-08 are strictly serial on one file.** All six mutate `docs/harness/DECISIONS-INDEX.md`, and
their verify counts are cumulative by construction (169 → 81 → 54 → 31 → 0 → marker pass). Four
concurrent documentors lose each other's writes and every burn-down count becomes meaningless. D-06's
four batches are a **cost** device, not a concurrency device — dispatch them one at a time, each
completing before the next opens. No `depends_on` field is introduced (FEAT-03's PLAN has none either);
this paragraph is the ordering contract.

**The unit gate is deliberately red between T-03 and T-07.** MF-2's fix makes T-01 test 5 FAIL rather
than skip when the index exists carrying `RULING PENDING` — which is exactly the state T-03 creates and
T-04..T-06 burn down. T-03..T-06 are `change_type: docs` (`test_matrix` `always: []`) and **do not
invoke the runner**, so nothing observes the red window; T-07's verify is the first invocation after
T-02's and it requires exit 0 with no `SKIP` line. Do not "fix" the red window by re-softening test 5:
that predicate is the whole of REQ-09's mechanical teeth.

## Routing note the orchestrator needs

T-09 and T-10 have **no agent owner**. `.harness/team-config.yaml` grants `docs/**` to
`harness-documentor` and `.claude/skills/harness/bin/**` to `harness-backend-dev` and
`harness-dev-ops`; nothing grants `CLAUDE.md` or `.claude/skills/harness-<rule>/SKILL.md`, and
`.claude/agents/**` is deliberately unowned. This is the same wall FEAT-03 hit at its SC-13. **SC-09
and SC-10 cannot go green until the main session acts** — plan the segment order so that is not
discovered at the goal-check.

## REQ-09 has mechanical teeth, and they create a cross-feature coupling

REQ-09 ("a new decision carries its own ruling") is not carried by header prose alone. A decision
appended without an index row regenerates as `RULING PENDING`, which **fails** T-01 test 5, which
reddens the unit gate. That is stronger enforcement than SC-03's presence check and it is deliberate.

**(MF-2) This narrative and T-01 test 5 now agree, and previously did not.** Test 5's earlier skip
predicate ("absent **or** still carries the sentinel") made that same sentinel state SKIP-and-pass,
so this paragraph's claim was false and REQ-09 had no mechanical teeth at all. Test 5 now skips on
**file absence only**; a sentinel-bearing or short-ruling row FAILS. The same fix also covers the
MF-3 case — a row whose sentinel was deleted and replaced with nothing fails the 20-character ruling
floor, so "not sentinel" cannot pass for "written". The price is the red window recorded in
`## Ordering`, which is the honest cost of the teeth.

**The consequence the orchestrator needs:** after this ships, any feature that appends a decision to
`docs/harness/DECISIONS.md` must run the generator and write the new row's ruling **in the same
commit**, or the unit gate fails. That is a new standing obligation on every future feature, not a
FEAT-04 detail.

## Glossary — deliberately not updated

`harness-spec-driven` makes `.harness/codebase/glossary.md` pm's to keep sharp when a feature pins
vocabulary, and this one pins two terms: a **ruling** (the one-sentence paraphrase of what a decision
decided) and an **open-or-skip filter** (a pointer whose only job is to answer "do I open the source?"
and which is never acted on directly). The file **does not exist** at `f723194` (`ls` → no such file),
no agent domain grants it, and the skill's own guidance is that an empty glossary is worse than an
absent one. Creating it to hold two entries is not warranted here; both terms are defined in the
index's generator-emitted header, which every reader of the index sees. Recorded so a reviewer does
not read the omission as an oversight.

## Test matrix note

Per `.harness/harness.json` `test_matrix`, `change_type: docs` is `always: []` — most tasks here
require no tests by the matrix, correctly. `change_type: logic` is `always: [unit]`, so T-01 and T-02
carry the entire automated burden of the feature, which is why the six test names are specified here
rather than left to the implementer.

## Run 02 fix cycle — MF-1..MF-6 and A-1..A-5, each answered by id

Every entry below is landed in the artifact text at the sites named; this table is the map, not the fix.

| id | Landed where | What changed |
|---|---|---|
| **MF-1** | D-02 (rewritten), T-02 amendments bullet, T-06's corrected note, T-07's note | The `am.N` form does not exist (0 occurrences). Both real forms specified: `### DEC-NNN amendment[ N]` keyed by **captured** number, and the two inline `**Amendment …**` paragraphs keyed **positionally** to DEC-145. Precedence, contiguity and the non-contiguous emission all ruled on. T-06's false "DEC-138 carries the amendment span" replaced with the measured `am.1-am.7` plus one bounded contiguous extra read, defined in T-06. |
| **MF-2** | T-01 test 5, `## Ordering`, `## REQ-09 has mechanical teeth` | Skip predicate is **file-absence only**; sentinel present = FAIL. Both former sites now say the same thing, and the red-gate window the fix creates is stated where the orchestrator sees it. |
| **MF-3** | BRIEF SC-02 (presence half), T-01 test 5 | SC-02 gains "every row's ruling is ≥20 non-whitespace characters" beside the absence half. The burn-down counts at T-04..T-07 are `grep -c 'RULING PENDING'` on the committed index and are untouched — 169 → 81 → 54 → 31 → 0 still holds, since the floor is asserted by test 5 at ship, not by the burn-down. |
| **MF-4** | T-02 supersession bullet, T-02 merge bullets, T-08 step 1, BRIEF SC-04 | (a) UPPERCASE-verb anchor in the em-dash trailing segment, targets from the first clause only, stop at the first comma — DEC-83's `:1001` title no longer marks DEC-39. (b) Strip **ALL** trailing clauses in any order, since DEC-19 carries two (DEC-84 `:1036`, DEC-85 `:1047`); canonical re-emission is clauses ascending, then `<!-- ok-stale -->` **last**. |
| **MF-5** | T-02 merge (orphan detection), T-01 **test 6** of six, BRIEF SC-04 | A preserved ruling whose DEC has no live heading is a hard error: nothing written, orphan named on stderr, non-zero exit. Named as a sixth test beside SC-04's three cases, asserted in both directions. |
| **MF-6** | D-06's wording, `## Ordering` | The bare four-spawns phrasing is gone — D-06 now reads "four line-range-bounded batches, dispatched one at a time — never concurrently", and `## Ordering` states T-03..T-08 are strictly serial on one file. No boundary moved. |
| **A-1** | **Accepted.** T-02 fence bullet + D-04's citation | Fenced lines dropped before **all** extraction, not just heading detection. Both citations of `check-docs.sh:41-46` widened to `:41-48`, because the toggle is `:44-46` and the `if infence: continue` skip is `:47-48` — a doer copying the old range got the toggle without the skip. |
| **A-2** | **Accepted and landed, not deferred.** BRIEF SC-09 + T-09 | SC-09's absence half replaced with the widened pair; the drafting constraint (authority path only in a negated construction) is written into **T-09's task text**, since the doer cannot see the SC. |
| **A-3** | **Accepted.** T-02 tags bullet | Score is `sum(body_lower.count(sub))`, selection is `sorted(tags, key=lambda t: (-score[t], t))[:4]`, emitted in that order. The title line is explicitly part of the body. |
| **A-4** | **Accepted.** BRIEF SC-08 | The plant is pinned: the phrase `all 15 agents` <!-- ok-stale --> (declared at `DECISIONS.md:2479`, owned by `## DEC-120` at `:2473`) into `docs/harness/SPEC.md`, on a line carrying none of the six narration keywords. Reviewer cites the landing `file:line` and both exit codes. `check-docs.sh --audit` (`:97-122`) cited beside it as the cheaper standing liveness check. |
| **A-5** | **Accepted in all three parts.** T-02 flags, T-01 test 5, D-02 + T-06 | `--check` **dropped** — no caller, and giving it a `check-state.sh` INV consumer is a task this feature did not scope; SC-05 is the same assertion with a real caller. Test 5's failure message names its remedy verbatim. Keying amendments by captured number is adopted; DEC-138's tags absorbing DEC-137's amendment text is recorded as inherent and not fought. |

Nothing on the LEAVE LIST was re-opened: D-01, D-04, D-06's four boundaries, T-01's runner description,
T-09/T-10's `owner: main-session`, and the SC-06/SC-08 pairing stand as approved-for-review. No
`D-NN`/`T-NN`/`SC-NN` id was renumbered.

## Approval

status: approved
approved-by: Mike Ruangutai
date: 2026-08-02
note: Q0 accepted — T-09 (CLAUDE.md:43) and T-10 (harness-handoff) are main-session
pre-ship steps, same arrangement as FEAT-03 SC-13. Also accepted: Q4, the unit gate is
deliberately red between T-03 and T-07 by design.
