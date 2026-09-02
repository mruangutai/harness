# Goal-check c3 — corrected plan vs the operator's stated intent — FEAT-54

## VERDICT

**YES — the plan delivers the operator's stated intent, and segment 1's two edits are correct.**
10/10 grilling `## Settled` lines carried, **0 uncarried**. 5/5 `## Out of scope` lines clean,
**0 re-admissions**. Both ACCEPTED rulings landed; both REJECTED findings' subjects are untouched;
every leave-list item is byte-unchanged. Both approval blocks read `pending`. **Gate verdict: PASS.**

Graded at worktree HEAD `ca43c014` **plus the uncommitted working tree** (segment 1's c3 edits are
not yet committed). Base `git merge-base main HEAD` = `b7956fc4`.

**Method that makes the leave list falsifiable rather than asserted:** `git diff HEAD` over both
files, then a `safe_load` object-diff of every task and decision. The c3 delta is **exactly**:
`plan.yaml` D-10 `because`, T-06 case (g), T-06 tail paragraph, T-09 `verify`+`intent`; `BRIEF.md`
SC-04 only. Object-diff: `changed tasks: [T-06, T-09]`, `changed decisions: [D-10]`,
`panel` identical, `lanes` identical. Everything not in that list is byte-unchanged by construction.

## 1. Settled-line coverage — 0 uncarried

The c2 table (`research-FEAT-54-goalcheck-plan-c2.md:19-28`) mapped all 10. The c3 delta touches
carriers of three lines only, and each keeps a carrier:

| Grilling line | Carrier affected | Still carried |
|---|---|---|
| :15 pointers resolve **when written** | D-10 `because` widened (`plan.yaml:177`) | yes — `choice` byte-identical, REQ-06/SC-15/T-01/T-02/T-06(e1) untouched |
| :16 historical valid / new notes five | SC-04 method changed (`BRIEF.md:89-99`) | yes — SC-04 survives with claim text intact; SC-06, SC-11, D-01, D-08, T-05, T-06(a)(b), T-07, T-11 untouched |
| :18 permanent deterministic gate, benchmark rerun at review | T-09 gained `exclude` (`plan.yaml:688`, `:715-717`) | yes — REQ-10, SC-09, D-04, T-12 untouched; registration scope word-for-word unchanged |

**UNCARRIED: 0.** `## Not yet specified` is `None` (grilling :22), so nothing was silently decided.

## 2. Out-of-scope re-admissions — 0

All five clean, and the delta admits nothing: T-09 stays `locally_run`, absent from `test_matrix`
(asserted `plan.yaml:689`) and from both script arrays (`:690`, T-12(c) `:880-884`); the 60-line cap
and the no-per-section-cap coverage are untouched; no token/latency saving is claimed anywhere.
**VIOLATIONS: 0.**

## 3. The two ACCEPTED rulings — quoted at the artifact

**(a) PF-570b9c87 — real-corpus mtime/byte audit out of the permanent suite. LANDED.**
`plan.yaml:519-531` T-06 (g): *"A CLEAN CORPUS AND NO MUTATION, ON A FIXTURE ROOT: build a fixture
corpus under tempfile.TemporaryDirectory holding TWO compliant notes — one whose repo-relative path
IS in that fixture's harness.json handoff_done_when_baseline and one that is NOT … assert BOTH that
no reported line mentions "Done when" AND that each fixture note is byte-identical and
mtime-identical afterwards. This case NEVER runs a gate over the real repository tree and NEVER
compares the mtime or bytes of a real feature note"*. Tail `:541-543`: *"Every case, (g) included,
builds its own fixture root … No case in this file runs a gate over the real repository tree, and
none compares the mtime or bytes of a real feature note."*
`BRIEF.md:89-99` SC-04: claim text `:89-91` **byte-identical** (the diff's only removed line is the
old `verify: automated        evidence: integration`); now *"Verified at REVIEW TIME, not by a
permanent suite case: at `review_sha` … the reviewer runs `bash …/check-state.sh` and records in the
review record its exit status and that no reported line names `Done when`"*, `verify: inspection`.

**My own independent sweep** (regex over both files for `mtime|byte-identical|real repository|real
corpus|live corpus|real tree|real feature note`), reported as mine, not inherited:

| Hit | Kind | Violates the ruling? |
|---|---|---|
| `plan.yaml:519-531` T-06(g) | fixture-root scan + fixture-note mtime/byte identity | no — this is the remedy |
| `plan.yaml:543` T-06 tail | negative assertion | no |
| `plan.yaml:566` T-07 `verify` | runs `check-state.sh` over the real tree | **no — a one-shot task verify, not a permanent suite case.** PF-570b9c87's subject was *"the permanent integration suite"*; T-07's verify runs once when the task lands |
| `plan.yaml:783-803` T-11 `verify` | reads this feature's own real notes | no — no gate run over the corpus, no mtime/byte comparison |
| `plan.yaml:725` T-09 | *"byte-identical"* of two `harness.json` keys | no — not a note, not a scan |
| `plan.yaml:869` T-12(a) *"REGISTERED ON THE REAL TREE"* | reads the real `harness.json` config | no — config, not the handoff corpus; pre-existing `case_1` shape |
| `BRIEF.md:96` SC-04 | the ruling's own rationale | no |
| `plan.yaml:46-49` PF-570b9c87 summary | historical finding text, must not be edited | no |

**Agreement with segment 1:** my list agrees on every entry it named. It **disagrees by addition**
on three sites segment 1's table did not surface — T-07's verify, T-11's verify and T-12(a). I
adjudicate all three as non-violating for the reasons above; none is a permanent suite case scanning
the handoff corpus. No disagreement of verdict.

**(b) PF-918326 — `exclude` on the new kind. LANDED, and the value is right.**
`plan.yaml:688` verify: `assert k['exclude']=='.claude/worktrees/**', k`.
`plan.yaml:715-717` intent: *"The entry also carries "exclude": ".claude/worktrees/**", exactly the
value omp_session_accessor carries: all 8 existing kinds declare exclude"*.
**Verified at the config, not from the plan** — `.harness/harness.json` `test_kinds` parsed:
`omp_session_accessor.exclude == '.claude/worktrees/**'` exactly, and all 8 kinds declare `exclude`.
The plan's stated convention is true at source.

## 4. The two REJECTED findings' subjects — unchanged

| Ruling | Subjects | Verdict |
|---|---|---|
| 3 — no-per-section-cap coverage KEPT | SC-14 `BRIEF.md:170-176`; T-03(h) `plan.yaml:363-366`; T-06(h) `plan.yaml:532-539` | **unchanged** — none appears in the diff; T-06's only hunks are (g) and the tail |
| 4 — typed grammar is a STABLE CONTRACT | D-01 `:143-145`, D-10 `choice` `:176`, REQ-06 `BRIEF.md:35-39`, SC-15 `:177-184`, T-01, T-02, T-06(e1)/(e2) `plan.yaml:506-516`, T-07 | **unchanged** — object-diff shows D-10 `choice` identical and T-01/T-02/T-07 identical |

**D-10's `because` carries the record clause and nothing mechanistic.** The new text is a strict
suffix of the old (`old.because` is a prefix of `new.because`, verified programmatically): the
`PF-bd92960a` STABLE-CONTRACT clause, the Q3 confirmation (*"grammar validation IS part of the
persisted shape validation"*), and its own self-limit — *"This clause is a record of the ruling and
adds no mechanism, no task, no criterion and no grammar-versioning machinery, which stays out of
scope"*. Corroborated: `grammar-version|versioned contract` matches 3 lines in `plan.yaml`, all
record text (D-10 `because`; PF-bd92960a's summary and disposition), **0** in `BRIEF.md`. Task and
decision counts unchanged, so no task, criterion, requirement or machinery followed the ruling.

## 5. Leave list — per item

`T-09 probe behaviour and scope`: word-stream diff of T-09's `intent` is **purely additive** (31
added tokens, the `exclude` clause; zero removed). The scope sentence's line-wrapping bytes moved
because the clause was inserted before it — an unavoidable consequence of ruling 2, not a change of
content. Every other item: **unchanged**, proven by the diff being confined to the five hunks above.

SC-14 ✔ · T-03(h) ✔ · T-06(h) ✔ · D-04 ✔ · T-09 probe behaviour/scope ✔ (word-identical) · T-12 ✔ ·
SC-09 ✔ · D-01 ✔ · D-10 `choice` ✔ · REQ-06 ✔ · SC-15 ✔ · T-01 ✔ · T-02 ✔ · T-06 (e1)/(e2) ✔ ·
T-07 ✔ · REQ-07 ✔ · D-08 ✔ · REQ-08 ✔ · SC-05 ✔ · REQ-01..05 ✔ · SC-01 ✔ · SC-02 ✔ · SC-03 ✔ ·
SC-12 ✔ · SC-13 ✔.

## 6. Id sets and approval

`safe_load`: tasks exactly `T-01..T-12`; decisions exactly `D-01..D-08, D-10`; `BRIEF.md` 10 REQ and
15 SC (unchanged); verify tally 10 automated / 4 inspection / 1 uat (SC-04 moved automated→inspection,
the only shift). `approval: {status: pending}` (`plan.yaml:3-4`) and `BRIEF.md:194-196` `status:
pending`. **Both pending.** `check-plan-routes.py <plan>` exits **0**, 0 violations; the 8 DEVIATION
lines are the expected DEC-174 carve-out output.

## 7. The c2 goal-check's conclusions, one by one, under c3

| c2 conclusion | Holds? |
|---|---|
| §1a 10/10 settled carried, 0 uncarried | **holds** (re-derived above) |
| §1b nothing silently decided | **holds** |
| §1c no contradiction with the 4 verified facts | **holds** — untouched by the delta |
| §2 0 out-of-scope violations | **holds** |
| §3 the three rulings delivered | **holds**, and now extended by two more |
| §3 adjudication: T-06(g) really did scan the real corpus (the pre-check was wrong to call it dangling) | **holds and is now superseded** — that text is what c3 replaced |
| §4a REQ traceability | **holds** |
| §4b SC gradability 15/15 | **holds, restated** — SC-04's falsifier is unchanged ("a reported line naming Done when"); its method moved to `inspection` and is now reachable, because the criterion names the recorded observation rather than an unrecorded terminal run. It joins SC-07/SC-08/SC-11, which already grade at `review_sha` by inspection |
| §4b evidence kinds resolve, none rests on a null kind | **holds** — one fewer `integration` criterion, no new kind |
| §4c `depends_on` acyclic | **holds** — no `depends_on` changed |
| §4d no cross-task verify conflict | **holds** — T-06's verify is unchanged; (g) is expected GREEN before and after, consistent with `plan.yaml:546-549` |
| §4e no dangling references | **holds** |
| §5 every cited anchor live | **holds** — no anchor was edited; `omp_session_accessor.exclude` re-verified today at source |
| F-01 PF-4205e7e2 `disposition: open` | **stale** — now reads `ACCEPTED by the operator … implemented as decision D-10` (`plan.yaml:29-32`). Not `resolved`/`resolved_by` in schema form; the `panel:` key is out of scope this run |
| F-02 the ruling is nowhere in `approval.rulings` | **still holds** — `approval:` is `status: pending` and nothing else. Main-session write |
| F-03 REQ-09 uncarried for `check-domain.sh`'s normative comment | **resolved** — T-04 `plan.yaml:408-423` now names both prose sites by content |
| F-04 T-04 double-reports a missing section | **still holds**, advisory (`plan.yaml:399-400` + `:401-404`) |
| F-05 `research-FEAT-54-planrevision-c2.md:66` stale on `FEAT-52` | **still holds**, advisory, outside my write scope |
| F-06 three panel findings open | **partly stale** — PF-570b9c87 and PF-918326 are now ruled and implemented, but their `disposition:` still reads `open - no operator ruling exists`, as does PF-d0ea19ff's and PF-bd92960a's. Expected: `panel:` transcription is a later run |

## Open questions

- **Q1 (non-blocking):** SC-04 says the reviewer records the run "in the review record" without
  pinning a path. The reviewer's own `notes/review-<self>-*.md` is the established home; naming it
  would remove the only ambiguity left in an otherwise reachable inspection criterion.
- **Q2 (non-blocking):** F-02 — does the operator want the batched rulings recorded in
  `approval.rulings` before signing? Main-session write only.
- **Q3 (non-blocking):** the four `panel.findings` dispositions still read `open` for findings the
  operator has now ruled. Out of scope here by dispatch; it must land before signature or the
  operator reads four unaddressed findings at the gate.
