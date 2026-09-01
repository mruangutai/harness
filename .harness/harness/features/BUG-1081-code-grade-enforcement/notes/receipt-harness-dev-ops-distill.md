# Distillation receipt — harness-dev-ops — BUG-1081-code-grade-enforcement

**Read `harness-distill/SKILL.md` first.** Read both existing Expertise files from disk before
writing (shown in dispatch context; confirmed unchanged on disk before any edit).

## Candidates judged

**1. EFFICIENCY relay (R-3: 6 redundant `git rev-parse --verify`, ~59ms/13% of 467ms, correctly
NOT applied — a three-function refactor of the enforcement path at the last step before the review
pin).** ACCEPTED, craft layer. The durable rule is the disposition, not the measurement: a real,
measured cost does not by itself justify a refactor when the scope and location risk (enforcement
path, near a pin) outweigh the gain. Folded into **P-07** via `replace` — P-07 already covered
"measure directly instead of trusting framing"; the new text keeps that and adds the
weigh-scope-against-gain step, same length, no new section slot needed.

**2. ALTITUDE relay (R-4: six refusal conditions duplicated in SKILL.md/validate-digest.py/
DECISIONS.md, recommendation `leave` because two locations are structurally exempt and the third
has a real partial compensating test).** ACCEPTED, craft layer (the rule generalizes: check for
structural exemption before flagging duplication as a defect; the specific files are the example,
not the point). Patterns was already at the 15-entry cap, so this entered by **displacing P-13**
(fixture-snapshot-regeneration) — judged weaker: P-13 covers one narrow QA-fixture scenario,
whereas the accepted rule applies to any duplication-flagging review (code review, simplify,
altitude passes generally), which is the more broadly reusable judgment call.

**3. Self-derived — repo tier.** Both R-3's and R-4's underlying findings are settled, assessed,
backlogged residuals specific to this repository's `validate-digest.py`/`code_grade.py`. Recorded
as repo-tier Gotchas (**G-11**, **G-12**) so a future dev-ops reader on THIS repo doesn't re-measure
or re-flag them as fresh findings — the craft-layer rules above are the general judgment; these are
the concrete "already settled here" facts.

**4. Status-capture step (verbatim `git status --porcelain -- .claude/skills/` empty, no source
touched).** REJECTED as a new entry — already fully covered by existing craft **P-05** ("capture
git status unfiltered... re-check against the opening snapshot"). Nothing sharper to add.

**5. The four design tests applied to `classify` (deletion/interface/adapter/lifetime).** REJECTED
as a new dev-ops entry — this methodology belongs to `harness-codebase-design` (a shared skill, not
persona-specific craft I originated), and adding it here would duplicate doctrine that already
lives at the right altitude.

## Ops applied

| Op | Target | Section | File | Why |
|---|---|---|---|---|
| replace | P-07 | Patterns | craft | fold "weigh scope/risk before recommending apply" into the existing measure-before-trusting-framing rule |
| replace | P-13 | Patterns | craft | displaced by broader duplication-exemption-check rule (candidate 2) |
| add | G-11 | Gotchas | repository | settled fact: redundant rev-parse re-verification chain, already assessed, don't re-flag |
| add | G-12 | Gotchas | repository | settled fact: six-refusal-condition triple-duplication, already assessed, don't re-flag |

**Tool mechanics:** `expertise-merge.py apply` is additive-union only (confirmed live per this
repo's established precedent — same-id-different-text is `CONFLICT`/exit 7, applies nothing). Ran
it first against the craft file with P-07/P-13 replacement text to get the exit-7 confirmation
(file byte-unchanged), then resolved with a single targeted `edit` confined to those two lines only
— never a whole-file write, per DEC-125. The repo-tier G-11/G-12 additions had room under cap, so
`expertise-merge.py apply` succeeded directly: `ADDED G-11`, `ADDED G-12`, exit 0.

## Counts

**Craft** (`.harness/expertise/harness-dev-ops.md`) — BEFORE: Patterns 15/15, Gotchas 15/15,
Outcomes 0/10, Open 0/5. AFTER: Patterns 15/15 (P-07, P-13 content replaced, same count), Gotchas
15/15 (unchanged), Outcomes 0/10, Open 0/5.

**Repository** (`.harness/harness/expertise/harness-dev-ops.md`) — BEFORE: Patterns 1/15, Gotchas
9/15 (G-01,02,04,05,06,07,08,09,10), Outcomes 0/10, Open 0/5. AFTER: Patterns 1/15 (unchanged),
Gotchas 11/15 (+G-11, +G-12), Outcomes 0/10, Open 0/5.

`check-expertise.sh` NOT run (per contract — orchestrator runs it once over the whole corpus). No
source file touched, no commit, no suite run.

## G-11 re-judgment (repair, appended post-hoc — original distillation above is unchanged)

The lead flagged two problems with G-11 as originally written: (1) it recalled a specific
measurement (~59ms/13% of 467ms) from a closed run — the instant anyone threads the resolved OIDs
through the enforcement path, that number goes false, and the entry is injected at every future
dev-ops spawn with nothing to catch the drift; (2) "not a fresh finding" reads as a standing
instruction to suppress a still-open backlog row, which is the opposite of what an efficiency
reader needs.

**Old text:** "WHEN reviewing validate-digest.py's code-grade enforcement path DO expect
review_sha and base_oid to be re-resolved via redundant git rev-parse --verify calls (~59ms/13% of
a 467ms review) — already measured and deliberately left unrefactored as a chore, not a fresh
finding."

**New text (kept, not dropped):** "WHEN reviewing validate-digest.py's code-grade enforcement path
DO check whether review_sha/base_oid are still each re-resolved via separate git rev-parse
--verify calls instead of a single shared resolution, and re-measure the cost yourself — do not
treat any prior number here as current, it rots at the first refactor."

**Reason kept, not dropped:** the underlying structural fact — two separate identifiers each going
through their own `git rev-parse --verify` on this path — is durable and still worth flagging to a
future reader; only the numeric measurement and the suppression framing were the false/rotting
parts. Stripping those two and replacing them with an instruction to re-measure lets the entry
survive the refactor it describes instead of lying about it. Applied by a targeted `Edit` confined
to the single G-11 line in the repository file (no merge-tool replace/drop verb exists, confirmed
in `expertise-merge.py`'s `compute_union`). Re-read after edit: repository file still has no
duplicate ids, 11/15 Gotchas, 17 lines total — both budgets intact.

```yaml
VERDICT: PASS
DIGEST:
  headline: two relayed candidates accepted (P-07/P-13 replaced in craft), two self-derived facts added to repository Gotchas (G-11/G-12); one relay-adjacent item rejected as already covered, one rejected as out-of-persona doctrine
  task: none
  open_questions: []
  files_touched:
    - .harness/expertise/harness-dev-ops.md
    - .harness/harness/expertise/harness-dev-ops.md
  expertise_update:
    - { op: replace, target: P-07, section: Patterns, file: craft, entry: "WHEN a dispatch frames a cost as negligible or settled DO measure it directly and report the number even against the framing; then weigh refactor scope and risk against that measured gain before recommending apply — a real, small, measured cost near a pin can still be the wrong trade." }
    - { op: replace, target: P-13, section: Patterns, file: craft, entry: "WHEN duplicated prose or logic spans multiple artifacts DO check each location for a structural exemption — no code access, a frozen record, or a test tying wording to code — before recommending a fix; duplication isn't a defect once propagation is already blocked." }
    - { op: add, target: G-11, section: Gotchas, file: repository, entry: "WHEN reviewing validate-digest.py's code-grade enforcement path DO expect review_sha and base_oid to be re-resolved via redundant git rev-parse --verify calls (~59ms/13% of a 467ms review) — already measured and deliberately left unrefactored as a chore, not a fresh finding." }
    - { op: add, target: G-12, section: Gotchas, file: repository, entry: "WHEN reviewing the six code-grade refusal conditions duplicated in harness-code-review/SKILL.md, validate-digest.py, and DECISIONS.md DO treat it as an accepted residual, not a fresh finding — test-validate-digest.py's N_A_REFUSAL_SUBSTRINGS table already ties refusal wording to code." }
artifact: .harness/harness/features/BUG-1081-code-grade-enforcement/notes/receipt-harness-dev-ops-distill.md
```
