# Goal-check — FEAT-38 at `review_sha` 48bbe7e (repin)

**12 of 13 criteria met. SC-13 is `unrun` — `verify: uat`, operator-owned. SC-04, the one criterion
that was `not_met` at `2557950`, is now `met`: all three sweeps are empty at the pin and the
measurement is proved able to report red.** No criterion is `cannot_be_met_as_written`. Every content
grade is a `git show 48bbe7e:` read, never a working-tree read.

Provenance: `git diff --name-only 2557950 48bbe7e -- '*.py' '*.sh'` → **0 files**, so every checker
graded below is byte-identical to the code at the prior pin; the delta is 26 files, +1041/−77 across
six commits. `git diff 48bbe7e HEAD -- .../DECISIONS.md` → 0 lines and the path is clean, so a
worktree invocation of a checker *is* the pinned code and text. Working copies: `/tmp/D48.md`,
`/tmp/I48.md`, `/tmp/gen48.py` = `git show 48bbe7e:<path>`; `/tmp/D0.md` = the same at `7ebfc9e`.

## Grades

| SC | Verdict | Method | Evidence command → observed |
|---|---|---|---|
| 01 | met | automated | `grep -cE '^###\s+DEC-[0-9]+\s+amendment' /tmp/D48.md` → 0, exit 1; `^\*\*Amendment` → 0, exit 1. Control at `7ebfc9e`: **25** and **13** — the same two figures SC-01 names |
| 02 | met | automated | per id ∈ {19,20,37,67,82,88,92,102,103,104,137,140,186,192,196}: `grep -cP "^## DEC-0*<id>(?![0-9])" /tmp/D48.md` → 0 **and** `grep -cP "DEC-0*<id>(?![0-9])" /tmp/I48.md` → 0. Fifteen separate assertions covering headings, index row ids and `refs:` graphs alike (the index pattern is unanchored, so a `refs:` mention would hit) |
| 03 | met | automated | `grep -nE '^## DEC-90' /tmp/D48.md` → `1057:## DEC-90 — STRUCK 2026-08-21`; strike record present and cited live from `DECISIONS-INDEX.md:100` (`refs: DEC-120 DEC-188`) |
| 04 | **met** | automated | three sweeps + positive control — see below |
| 05 | met | automated | `grep -cF "am." /tmp/I48.md` → 0; `SUPERSEDED BY` → 0; `am-span` → 0. `gen-decisions-index.py --stdout > /tmp/gen.out` exit 0, `diff -q /tmp/gen.out /tmp/I48.md` **exit 0** — index is fresh at the pin |
| 06 | met | automated | all seven tokens `grep -c` → 0 in `/tmp/gen48.py`. Orphan detection proved **behaviourally**, not by reading: loaded the pinned module, `build_index(D48_with_DEC-90_span_removed, parse_existing_index(I48))` → returned `None`, stderr `ORPHAN: DEC-90 '…' `. Unmutated control → returned a `list`, stderr empty |
| 07 | met | automated | re-proved at the pin: loaded `test-gen-decisions-index.py`, pointed `gdi.DECISIONS_PATH` at `/tmp/D48_amend.md` (one `### DEC-999 amendment 1` planted at line 61) → `FAIL - test_no_amendment_construct_survives_in_the_authority: '### DEC-N amendment' heading found at …:[61]`, returns `False`; unplanted `/tmp/D48.md` → `ok - test_no_…`, returns `True`. The `ok -` line is pinned by name at `48bbe7e:…/plan.yaml:800` (and `:832`), so it cannot be deleted with the suite green |
| 08 | met | automated | three observations. (1) `check-decision-anchors.py --file /tmp/D0.md` → the **exact** three `feature.yaml` anchors (`FEAT-03-subissue-mirror/feature.yaml:73`, `feature.yaml:63-64`, `…:97`), `examined 32 anchor(s), 3 failed`, exit 1. (2) `--file /tmp/D48.md` → `examined 20 anchor(s), 0 failed`, exit 0. (3) one fabricated `` `…/bin/no-such-file-xyz.py:12` `` planted → `examined 21 anchor(s), 1 failed`, exit 1 |
| 09 | met | automated | control: `check-decision-claims.py --file /tmp/D48.md` → `examined 11 claim(s), 0 failed`, exit 0. Mutation: DEC-181's `budget is 80 (DEC-181)` → `81` (marker at `/tmp/D48.md:4775`) → `DEC-181 — CLAUDE.md gets a line budget of 80: … expected substring 'budget is 81 (DEC-181)' not found in stdout`, `examined 11 claim(s), 1 failed`, exit 1 — names the marker by owning entry and by command |
| 10 | met | automated | **not re-run** (dispatch: already re-established GREEN). `notes/qa-2026-08-29-11-validator.md` measured the pin `48bbe7e` directly: exit 0, `fail: 0`, `kind_drift: 0`, full 1002 / unit 417 / integration 585, `matrix_ok: true`, both feature checkers still discovering (`examined 20 anchor(s)` / `11 claim(s)`, known-positive probe at `7ebfc9e` → 32/3). Sibling `notes/qa-2026-08-29-11-validator-c2.md` measured the same pin (via worktree HEAD `04d333d`, non-source delta) **and** a read-only `2557950` archive, allocating the whole 115-line `PASS` gap to a `^PASS` vs `^PASS ` regex convention across three unchanged scripts — 0 `FAIL` at both trees |
| 11 | met | inspection | staleness resolved explicitly — see below |
| 12 | met | inspection | three clauses, all at the pin. Front matter `48bbe7e:DECISIONS.md:3-13` now reads *"Every entry states current truth, in its own voice… a correction rewrites the entry it corrects"*; the base's *"APPEND-ONLY. Never rewrite or renumber"* (`7ebfc9e:DECISIONS.md:3-5`) is gone. `48bbe7e:.harness/harness/expertise/harness-documentor.md:4-8` P-01 now reads *WHEN a decision … proves wrong DO rewrite that entry in place* (base:4 read *WHEN appending an amendment … DO place it INSIDE*). The convention's new home is stated by `48bbe7e:DECISIONS.md:6240` — DEC-205 |
| 13 | **unrun** | uat | operator's judgement, not mine to grade — see below |

## SC-04 — re-measured at the pin, with a reachability proof

Scope, all three sweeps: `48bbe7e -- . ':(exclude).harness/harness/features/*'
':(exclude).harness/notes/*' ':(exclude).harness/logs/*'`.

1. `git grep -nE 'DEC-[0-9]+ amendment'` → **empty, exit 1** (0 sites; was 0 at `2557950` too).
2. `git grep -nE 'am\.[0-9]+'` → **empty, exit 1**. Was **13** sites in 8 files at `2557950`,
   including the bare `am.2` at `.claude/skills/harness/SKILL.md:203` that a `DEC-N am.N`-shaped
   pattern cannot see. This unanchored pattern would still see it.
3. Deleted-id citations, `git grep -nP "DEC-0*<id>(?![0-9])"` run **once per id for all fifteen** ids
   (19, 20, 37, 67, 82, 88, 92, 102, 103, 104, 137, 140, 186, 192, 196) → **exit 1, 0 hits, fifteen
   for fifteen.** Was 5 sites over 3 ids (19, 102 ×3, 192) at `2557950`; the other **twelve** ids were
   already clean there. *(The prior goal-check called that "Ten of the fifteen" over a twelve-id list:
   15 − 3 = 12. The list was right, the word wrong. My own count at this pin is 15/15 clean.)*

**Positive control — the measurement can report red.** Same command, same scope, same pattern shape,
against ids that survive this feature:

- `DEC-188` → **exit 0, 26 hits**, e.g. `.claude/skills/harness-brief/SKILL.md:52`,
  `.claude/skills/harness/bin/check-domain.sh:523`, `bin/gen-decisions-index.py:205`.
- `DEC-90` → **exit 0, 6 hits**, e.g. `DECISIONS-INDEX.md:100`, `DECISIONS.md:1057`.
- Regex-and-traversal control for sweep 2: the identical `am\.[0-9]+` command at `7ebfc9e` returns
  hits across 20+ files (`.claude/commands/harness.md`, `.gitignore`, `.github/workflows/tests.yml`, …).

So the empty results above are an empty tree, not a search that traversed nothing (the `.agents/**`
symlink trap) and not `git grep -E`'s missing `\b` (the second trap) — `-P` with `(?![0-9])` is used
throughout.

## SC-11 — inherited coverage, and why it carries

`git diff 2557950 48bbe7e -- .harness/harness/docs/DECISIONS.md` → **0 lines. Byte-identical.**
The repin therefore cannot have moved a single one of the 15 rewritten entries. The inherited
coverage stands unchanged and is **not** re-derived: 10 entries (DEC-11, 138, 142, 158, 171, 174,
181, 189, 193, 194) sampled per entry by the cycle-0 code reviewer at
`notes/review-harness-code-reviewer-c0.md:11-28`, and 5 (DEC-145, 149, 152, 157, 183) graded per
entry with base-versus-pin pointers at `notes/research-FEAT-38-goalcheck-2557950.md:80-111`.
15/15 covered, each with a file pointer and both required survivals named. `DEC-145 am.3` is
dropped by the operator's 2026-08-20 acceptance recorded in BRIEF `## Verification gaps`, not by a
fold defect.

## SC-13 — `unrun`, and a separate accuracy finding on the script

**Verdict: `unrun`. Operator-owned. Not met, not waived, not self-passed.** `notes/uat-FEAT-38.md`
is `status: ready`, 115 lines, three steps U-01/U-02/U-03 on exactly the folded DEC-138, DEC-174 and
DEC-181 the criterion names.

**Accuracy at the pin — substantively correct, one stale metadata line.**

- Every entry it asks for is present at `48bbe7e`: `## DEC-138` @2925, `## DEC-174` @4268,
  `## DEC-181` @4769. Its extractions are anchored on `## DEC-NNN` headings, never line numbers, and
  its `span`/`amds` helpers run clean.
- Its three pre-fold line counts are exact: DEC-138 **107**, DEC-174 **214**, DEC-181 **47** at
  `7ebfc9e` (pinned forms 128 / 122 / 51). Both cited receipts resolve at `48bbe7e`.
- It reads the working-tree `$D`; `git diff 48bbe7e HEAD -- DECISIONS.md` is 0 lines and the path is
  clean, so that read *is* the pinned text.
- **The one defect:** line 4 still says *graded at `review_sha` **2557950***. That is now the stale
  pin. Its substance survives — `DECISIONS.md` is byte-identical from `b32013c` through `2557950` to
  `48bbe7e` — so the operator will read exactly the reviewed text. **A one-line metadata fix, not a
  re-authoring; the script does not need to be regenerated.** Not mine to edit under a goal-check
  dispatch.

## Recommendations, not criteria

- No emergent criterion is asserted. The eng lead's E1 (the claim checker's safety boundary stated at
  `DECISIONS.md:6286-6288` as *"first word is not `git` or `grep`, and never invokes a shell"*) remains
  an **understatement of six enforced rules, not a false statement**; no SC asserts exhaustiveness of
  that prose, so it falsifies nothing. Advisory for a later edit, as at the prior pin.
- The UAT script's stale `review_sha` line (above) is the only actionable follow-up I found, and it
  does not gate anything.

## Open questions

- Q1 (non-blocking): the UAT script's `tree:` line names the superseded pin `2557950`. Should the
  main session correct it to `48bbe7e` before handing the script to the operator? Reversible,
  one line, but only a tier with a user channel should touch a script the operator is about to run.
- Q2 (closed, recorded for the record): the prior goal-check's Q1 reported six stray untracked
  entries in the worktree root. `git status --porcelain` at this pin shows them **gone** — only
  `feature.json` (modified, the review-pin's) and four untracked `notes/` artifacts remain. Swept;
  no action.
