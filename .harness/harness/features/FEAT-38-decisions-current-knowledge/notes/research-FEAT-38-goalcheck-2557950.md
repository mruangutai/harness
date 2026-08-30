# Goal-check — FEAT-38 at `review_sha` 2557950

**11 of 13 criteria met. SC-04 is `not_met` (carved out, main-session T-14). SC-13 is `unrun` (operator).**
No criterion is `cannot_be_met_as_written`. Every content grade is a `git show 2557950:` read.

Provenance: `git diff 2557950 46206de` touches `feature.json` only; `git diff 2557950 -- <the five
graded source files>` is 0 lines, so a worktree invocation of a checker at HEAD *is* the pinned code.
`git diff 3928c70 2557950 -- .harness/harness/docs/DECISIONS.md` is **0 lines** — the cycle-0
inspection of DECISIONS.md is therefore NOT stale (see SC-11).

Working copies used below: `/tmp/D.md` = `git show 2557950:…/DECISIONS.md`, `/tmp/I.md` = the pinned
index, `/tmp/D0.md` / `/tmp/I0.md` = the same two at `7ebfc9e`.

## Grades

| SC | Grade | Method | Command → observed |
|---|---|---|---|
| 01 | met | automated | `git show 2557950:…/DECISIONS.md \| grep -E '^###\s+DEC-[0-9]+\s+amendment'` → exit 1; same for `^\*\*Amendment` → exit 1. Control at `7ebfc9e`: 25 and 13 matches |
| 02 | met | automated | per id ∈ {19,20,37,67,82,88,92,102,103,104,137,140,186,192,196}: `grep -cE "^## DEC-0*<id>\b" /tmp/D.md` → 0 **and** `grep -cE "DEC-0*<id>\b" /tmp/I.md` → 0. Fifteen separate assertions, no file-global count. Positive control on the same 15 patterns at base: heading=1 each, index 2–14 mentions each |
| 03 | met | automated | `grep -n -E '^## DEC-90' /tmp/D.md` → `1057:## DEC-90 — STRUCK 2026-08-21`; strike record present (`Struck under DEC-188 on the operator's word… bin/expertise-merge.py holds an exclusive lock…`), plus `**DEC-90's number is retired, not reused.**` |
| 04 | **not_met** | automated | see residue list below |
| 05 | met | automated | `grep -F "am." /tmp/I.md` → exit 1; `grep -n "SUPERSEDED BY" /tmp/I.md` → exit 1; `grep -E "am-span" /tmp/I.md` → exit 1. Controls at base: 9 and 20 hits. `gen-decisions-index.py --stdout > /tmp/gen.out; diff -q /tmp/gen.out .harness/harness/docs/DECISIONS-INDEX.md` → exit 0 |
| 06 | met | automated | all seven tokens `grep -c` → 0 in `git show 2557950:…/gen-decisions-index.py`. Orphan detection proved **behaviourally**, not by reading: loaded the pinned module, `build_index(text_with_DEC-90_entry_removed, parse_existing_index(pinned_index))` → returned `None` and printed `ORPHAN: DEC-90 '…' has a ruling in the index but no live heading`. Unmutated control → returned a `list`, stderr empty |
| 07 | met | automated | re-proved at the pin, not inherited: loaded `test-gen-decisions-index.py`, pointed `gdi.DECISIONS_PATH` at a copy of the pinned DECISIONS.md with one `### DEC-999 amendment 1` planted at line 61 → `FAIL - test_no_amendment_construct_survives_in_the_authority: '### DEC-N amendment' heading found at …:[61]`, returns `False`; plant removed → `ok - test_no_amendment_construct_survives_in_the_authority`, returns `True`. Transcript of the original both-runs is also on record at `notes/receipt-harness-backend-dev-2026-08-29-07-eng.md:77-111`, and the `ok -` line is pinned by name in `plan.yaml:800` |
| 08 | met | automated | three separate observations, all mine. (1) `check-decision-anchors.py --file /tmp/D0.md` → `FEAT-03-subissue-mirror/feature.yaml:73`, `feature.yaml:63-64`, `FEAT-03-subissue-mirror/feature.yaml:97`; `examined 32 anchor(s), 3 failed`; exit 1 — **exactly** the three. (2) `--file /tmp/D.md` → `examined 20 anchor(s), 0 failed`, exit 0. (3) one fabricated `` `.claude/skills/harness/bin/no-such-file-xyz.py:12` `` planted → `examined 21 anchor(s), 1 failed`, exit 1 |
| 09 | met | automated | **re-observed at 2557950, not inherited from 3928c70.** Control: `check-decision-claims.py --file /tmp/D.md` → `examined 11 claim(s), 0 failed`, exit 0. Mutation: DEC-181's marker at `DECISIONS.md:4775` expectation `budget is 80 (DEC-181)` → `81` → `DEC-181 — CLAUDE.md gets a line budget of 80: … :: 'budget is 81 (DEC-181)': expected substring … not found in stdout`, `examined 11 claim(s), 1 failed`, exit 1. It names the marker by owning entry and by command |
| 10 | met | automated | `out=$(bash .claude/skills/harness/bin/run-unit-tests.sh 2>&1); ec=$?` — captured, never piped to `tail`. exit=0, `^FAIL` lines = **0**, `^PASS` lines = **1117**, `^ok - ` = 184, 3405 lines total, 175 s. 1117 matches the orchestrator's figure exactly |
| 11 | met | inspection | 5 graded personally (below); 10 inherited and proved not stale |
| 12 | met | inspection | three clauses, all at the pin: front matter `DECISIONS.md:3-13` now reads *"Every entry states current truth, in its own voice… a correction rewrites the entry it corrects"* — the base's `APPEND-ONLY. Never rewrite…` (`7ebfc9e:DECISIONS.md:3-5`) is gone. `.harness/harness/expertise/harness-documentor.md:4-7` P-01 now reads *WHEN a decision … proves wrong DO rewrite that entry in place* (base:4 read *WHEN appending an amendment … DO place it INSIDE*). The convention's new home is stated by `DECISIONS.md:6240` DEC-205 |
| 13 | **unrun** | uat | operator's judgement. Script `notes/uat-FEAT-38.md`, `status: ready`, 115 lines. Its `tree:` line names `b32013c` and says review_sha unpinned — stale metadata only: `git diff b32013c 2557950 -- .harness/harness/docs/DECISIONS.md` is 0 lines, so the entries the operator will read are byte-identical to the pin |

## SC-04 — the residue T-14 must clear

**18 sites in 13 files.** `DEC-<n> amendment` prose: **0 occurrences** (`git grep -nE 'DEC-[0-9]+ amendment' 2557950 -- . ':(exclude).harness/harness/features/*' ':(exclude).harness/notes/*' ':(exclude).harness/logs/*'` → empty).

`am.N` — 13 occurrences, command `git grep -nE 'am\.[0-9]+' 2557950 -- <same exclusions>`:

| file:line | token |
|---|---|
| `.claude/commands/harness.md:95` | DEC-138 am.4 |
| `.claude/skills/harness-brief/SKILL.md:53` | DEC-138 am.7 |
| `.claude/skills/harness-init/SKILL.md:103` | DEC-171 am.1 |
| `.claude/skills/harness-wayfinding/SKILL.md:35` | DEC-138 am.6 |
| `.claude/skills/harness/SKILL.md:132` | DEC-157 am.1 |
| `.claude/skills/harness/SKILL.md:203` | bare `am.2` (no DEC prefix — a plain `DEC-N am.N` sweep misses it) |
| `.claude/skills/harness/SKILL.md:284` | DEC-138 am.4 |
| `.claude/skills/harness/references/github-mirror.md:23` | DEC-138 am.6 |
| `.claude/skills/harness/references/github-mirror.md:40` | DEC-138 am.7 |
| `.claude/skills/harness/references/github-mirror.md:44` | DEC-138 am.4 |
| `.claude/skills/harness/templates/gitignore.snippet:8` | DEC-171 am.1 |
| `.gitignore:9` | DEC-171 am.1 |
| `.harness/factory/fleet.yaml:10` | DEC-174 am.1 |

Deleted-id citations — 5 occurrences, command `git grep -nP "DEC-0*<id>(?![0-9])" 2557950 -- <same exclusions>` run per id:

| file:line | id |
|---|---|
| `.claude/skills/harness/references/debug-mission.md:21` | DEC-19 |
| `.claude/agents/harness-orchestrator.md:46` | DEC-102 |
| `.claude/skills/harness-team/SKILL.md:15` | DEC-102 |
| `.omp/agents/harness-orchestrator.md:49` | DEC-102 |
| `.claude/skills/harness/SKILL.md:246` | DEC-192 |

Ten of the fifteen deleted ids (20, 37, 67, 82, 88, 92, 103, 104, 137, 140, 186, 196) have **zero** live
citations. The dispatch's estimate of ~10 am.N and ~4 id sites is **13 and 5** — re-measured, not repeated.

**Tooling warning for whoever executes T-14:** `git grep -E 'DEC-103\b'` returns **nothing** — git's ERE
has no `\b`. Use `-P` (as above) or `git grep -n DEC-103` unanchored. A `-E … \b` sweep reports the tree
clean while five citations stand. Likewise spell every path `.claude/…`, never `.agents/…`.

Per the dispatch, SC-04 is carved out and **not routed** — its owner is the main session under T-14
(`execution_mode: main-session-direct`, all 13 paths `NOBODY` from `check-domain.sh --resolve`).

## SC-11 — the five I graded, and the ten I inherited

Staleness: `git diff 3928c70 2557950 -- .harness/harness/docs/DECISIONS.md` → **0 lines**. The 10 entries
sampled by the cycle-0 code reviewer (`notes/review-harness-code-reviewer-c0.md:11-28` — DEC-11, 138, 142,
158, 171, 174, 181, 189, 193, 194) were graded against byte-identical text. Inherited, not re-run.

The five remaining, each `git show 7ebfc9e:` beside `git show 2557950:`. All **met**.

- **DEC-145** (base:3494 → pin:3201, 78→53 lines). Prior belief *"prefer merge over add"* rewarded
  appending case histories, and the three root causes, survive verbatim. am.1 survives as *"A third
  boundary joins decision-versus-observation: a harness defect is a bug report, not a learning"* with
  both original examples. am.2 survives as *"Distillation is a three-party pipeline, not diffusion"*
  including rejection-as-outcome, displacement-never-merge and the staleness-audit yield; its
  falsifying measurement survives as *"9 of 15 Expertise files failed it again within a day"* under
  **"Deploying the checker is the control; authoring discipline is not."** **am.3 is dropped entirely** —
  it was annotated MOOTED at base and its subject (ship-refresh) no longer exists; BRIEF's own
  Verification-gaps section records the operator accepting that loss on 2026-08-20, and DEC-205 restates
  it. Not a fold defect; flagged so it is not rediscovered as one.
- **DEC-149** (base:3624 → pin:3306). Prior belief — `deepen` as a live between-features mission —
  survives as *"A third import, the `deepen` mission, was tried and retired."* Falsification survives:
  *"read the codebase map, and the map tier was removed after 35 features never built one — leaving the
  mission nothing to scan."* The glossary's move to `.harness/glossary.md` is stated as current truth.
- **DEC-152** (base:3733 → pin:3406, 42→22). Prior belief survives as *"The three domain leads are NOT
  in the `high` tier, and putting them there because they assess what their members return has been
  tried and reversed"*; falsification survives as *"a lead routes and consolidates, holds no shell and
  reads no diff itself"* + *"The `high` tier is four agents, not seven."* Dropped: the `b4659cd`
  measurement command and the "nothing detected it" provenance. That is provenance, not the
  falsification, and the census is now directly checkable — inside SC-11's bar.
- **DEC-157** (base:3898 → pin:3551). am.1 survives as *"Runs are counted too, informationally — INV-22"*;
  the prior belief that counting rework alone sufficed is stated and falsified in the same clause —
  *"with first-pass runs contributing zero, FEAT-03 ran 19 times against a 6-cycle count and tripped
  nothing."* Both load-bearing properties (FLOOR; unresolvable budget REPORTED) survive with their
  FEAT-07 and `harness.kaya-ai.json` evidence.
- **DEC-183** (base:5548 → pin:4907). am.1's two reasons are folded into the body as current truth, with
  reason 2 still marked load-bearing. Crucially for REQ-02, the refused alternative survives —
  *"A LIGHTER guard is not the answer either… a pure predicate over `yaml.safe_load` … was worked up in
  full, planned, and then ABANDONED on that reasoning"* — so it cannot be re-proposed. The unmeasured
  residue (ruleset / required workflow / pinned ref) and the four repaired citations both survive.

## The eng lead's E1, judged

`DECISIONS.md:6286-6288` states the claim checker's safety boundary as *"the checker refuses any command
whose first word is not `git` or `grep`, and never invokes a shell."* **No criterion is falsified by it.**
The sentence is true — `ALLOWED_FIRST_TOKENS = {"git", "grep"}` and `shell=False` both hold, and the
adjacent claim marker at `:6290` asserts the first mechanically. It is an understatement of six enforced
rules, not a false statement, and no SC asserts exhaustiveness of that prose. **Advisory, not gating:** a
reader who takes it as the whole boundary would under-model rules 2–6 (git global-option ban, subcommand
allowlist, `-O` ban, neutralized `GIT_CONFIG_*`, grep file/device ban). Worth one sentence in a later
edit; it does not justify spending the last cycle.

## Open questions

- Q1 (non-blocking): six stray untracked entries sit in the worktree root — `100644`, `2`,
  `1788036665430977000`, and two 40-hex names, plus `.harness/notes/grilling-…-2026-08-24.md`. They
  predate this segment and are not mine. Likely debris from a `git show`/`git hash-object` invocation
  that lost its redirect target. Harmless to the pin; someone should sweep them before the PR.
