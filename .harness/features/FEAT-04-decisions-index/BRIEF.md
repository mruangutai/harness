# BRIEF — FEAT-04 Decisions index

## Problem

`docs/harness/DECISIONS.md` is 4,413 lines and the only way to be correct about a ruling is to read
it whole — `CLAUDE.md:43` says so in as many words. FEAT-03 measured the cost: 137 cache-read tokens
per output token, `eng-lead` the single most expensive agent at $16 while spawning no members,
because reviewing correctly meant reading the authority. This feature's own plan phase then spent
~$114 of a $120 budget the same way. The file compounds — eleven decisions were appended on
2026-07-31 alone — so the toll rises every week, and the alternative to paying it is an agent
guessing at 169 rulings from memory.

## Goal

`DECISIONS.md` stops being read whole. An agent that must be correct about decisions reads a bounded
index and greps the two or three entries that bear on its task. The full file stays the authority,
and `check-docs.sh` keeps harvesting stale markers from it. Scope is that one file.

## Requirements

- REQ-01: An agent can determine which decision entries bear on its task from a single bounded file,
  without opening the authority.
- REQ-02: Every top-level decision in the authority is represented in the index, so recall is
  complete — no decision is silently absent.
- REQ-03: The index states, in its own text, that a row is an open-or-skip filter and never the rule
  itself, and that backfilled rulings are second-hand paraphrase.
- REQ-04: The index's mechanical content (location anchor, topic tags, reference graph, supersession
  status) stays current as decisions are appended, without a human re-deriving it.
- REQ-05: Hand-written content in the index survives regeneration, attributed to the same decision.
- REQ-06: The project's entry-point instruction points at the index, and no agent-facing surface
  instructs reading the authority whole.
- REQ-07: The reading discipline — citations are a floor, and the four go-broad triggers — reaches
  every deployed project, not only this repo.
- REQ-08: The propagation checker's coverage is unchanged: it harvests the same pattern set and still
  flags a real stale claim, including one in the new index.
- REQ-09: A newly recorded decision carries its own ruling, written by its author in the same commit;
  paraphrase stops at the backfill.

## Success Criteria

- SC-01: `docs/harness/DECISIONS-INDEX.md` carries exactly one row per **live** `^## DEC-NN` heading
  in the authority — live meaning outside a code fence — counted at run time rather than against a
  frozen number. That is **169** at `f723194`, not the 170 a bare `grep -c` reports; PLAN D-04 has the
  measurement and why the difference matters.
  verify: automated      evidence: unit
- SC-02: No row is left unwritten. **(MF-3) Two halves, because bare absence is not a criterion
  (DEC-169):** *absence* — zero occurrences of the `RULING PENDING` sentinel in the committed index;
  *presence* — every `^- DEC-` row carries at least **20 non-whitespace characters of hand-written
  ruling prose**, measured on the segment after ` :: ` **once PLAN T-02's strip rule has removed the
  generator-owned trailing content** (all `— SUPERSEDED BY DEC-NN` clauses and any `<!-- ok-stale -->`).
  Absence alone is satisfied by deleting the sentinel and writing nothing, which is the hole; and a
  floor measured on the raw segment is the same hole one layer down — `DEC-19`'s row carries two
  supersession clauses (~44 characters of generator text) and would clear a naive 20-character floor
  with no prose at all. This is asserted at ship state by T-01 test 5; it does not change the backfill burn-down
  counts in PLAN T-04..T-07 (`grep -c 'RULING PENDING'` → 81, 54, 31, 0), which stand as written.
  verify: automated      evidence: unit
- SC-03: The index's own header carries the open-or-skip framing, anchored by the stable token
  `<!-- index-contract v1 -->`, and the header is generator-emitted so it cannot be edited away by a
  regeneration.
  verify: automated      evidence: unit
- SC-04: Regenerating over an index holding N hand-written rulings preserves all N against the same
  DEC number, including a ruling that carries an inline `<!-- ok-stale -->` marker, and including the
  case where a new decision was appended to the authority mid-file.
  **(MF-4) What "byte-identical" means, precisely:** the hand-written *ruling prose* is byte-identical.
  The `<!-- ok-stale -->` marker survives but is re-emitted last, and `— SUPERSEDED BY DEC-NN` clauses
  are recomputed each run — those two are generator-owned, so a row carrying either is byte-identical
  only after normalisation to PLAN T-02's canonical order. Stating it this way is what keeps SC-04 from
  over-claiming against a merge that legitimately rewrites clause order.
  **(MF-5) Plus the orphan case, as a fourth named case:** a preserved ruling whose DEC number has no
  live heading in the authority makes the generator exit non-zero naming that number and write nothing —
  never a silent drop. Asserted in both directions (orphan present → non-zero; orphan removed → exit 0).
  verify: automated      evidence: unit
- SC-05: Running the generator at ship state changes nothing:
  `.claude/skills/harness/bin/gen-decisions-index.py && git diff --exit-code
  docs/harness/DECISIONS-INDEX.md` → exit 0. Catches marker-stripping and mechanical drift together.
  verify: inspection
- SC-06: The checker's coverage of the index is proven in permanent regression form: in a temporary
  project tree, a declared stale pattern planted into `DECISIONS-INDEX.md` **without** a marker makes
  `check-docs.sh` exit 1 naming the owning DEC, and the same line **with** `<!-- ok-stale -->` exits
  0. The presence half of REQ-08 — asserting exit 0 alone would be satisfied by a gutted checker
  (DEC-169).
  verify: automated      evidence: unit
- SC-07: At ship state `.claude/skills/harness/bin/check-docs.sh` exits 0 and prints
  `checked 45 superseded pattern(s)`. The pattern count is pinned; the file count is not, because it
  becomes 91 the moment the index lands.
  verify: inspection
- SC-08: The live discriminating receipt, run in this repo. **(A-4) The plant is pinned, because an
  unpinned one passes vacuously** — a phrase landing on a line that carries any of `check-docs.sh`'s six
  narration keywords (`:136-137`), or into `DECISIONS.md`, or under a `/runs/` path, exits 0 and reads as
  a clean revert. Pinned: append the phrase **`all 15 agents`** <!-- ok-stale --> — declared stale at
  `docs/harness/DECISIONS.md:2479`, owned by `## DEC-120` at `:2473`, and measured absent, unescaped, from every
  scanned file at `f723194` — as a new line at the end of **`docs/harness/SPEC.md`**, phrased so the line
  contains none of `superseded`, `no longer`, `corrected`, `inverted`, `an earlier`, `was wrong` and no
  `ok-stale` marker. The two citations added since — here and in the A-4 row of `PLAN.md` — each carry
  `<!-- ok-stale -->` on the phrase's own physical line and are skipped at `check-docs.sh:133` before any
  pattern is matched, so the plant is the only unescaped occurrence. Then `check-docs.sh` exits 1 with
  **exactly one** stale statement, attributing it to `DEC-120`; revert; `git status
  --porcelain docs/harness/SPEC.md` is empty. **The reviewer cites the landing `file:line`**, both exit
  codes and the attribution line — a receipt without the landing line does not distinguish a real hit
  from a vacuous one. `check-docs.sh --audit` (`:97-122`) is the cheaper standing liveness check to cite
  beside this: SC-06 proves the code path in a hermetic tree with a *fabricated* marker, which is not the
  same as proving this repo's 45 real patterns are live.
  verify: inspection
- SC-09: `CLAUDE.md` points at the index and nothing in the agent-facing surface set instructs a
  whole read. Bounded to a named set and a named grep pair, run from the repo root:
  - presence: `grep -n 'DECISIONS-INDEX.md' CLAUDE.md` → at least one hit, at the pointer line
    (currently 0 hits — discriminating).
  - absence — **(A-2) widened from the single literal, which any re-wording of the same instruction
    would have walked past.** Over the surface set `CLAUDE.md .claude/skills .claude/agents
    .harness/expertise`, both of these → **0 hits**:
    1. `grep -rniE '(read|consult|review|check)[^.]{0,40}DECISIONS\.md' <set> | grep -viE
       '(never|not)[[:space:]][^.]{0,20}(read|whole)'` — **discriminating**: measured at `f723194` it
       returns exactly **1**, `CLAUDE.md:43`. The `grep -v` is required so T-09's own replacement text
       ("…is never read whole") does not self-trip the criterion; the matching constraint is written into
       PLAN T-09's task text so the doer can satisfy it without seeing this SC.
    2. `grep -rniE 'DECISIONS\.md[^.]{0,30}(whole|in full|end to end|cover to cover)' <set>` — a
       **standing guard, not a discriminating check**: it returns 0 today, so passing it proves nothing
       about this change. Recorded as such rather than presented as a receipt.
    `[^.]` rather than `[^.\n]` — grep is line-based, so excluding the period alone is what stops a match
    crossing a sentence boundary, and the bracketed `\n` risks excluding the letter `n` on a
    non-GNU grep. `DECISIONS\.md` cannot match `DECISIONS-INDEX.md`, so the new pointer is free.
    `.harness/expertise/**` is in the set because a `SubagentStart` hook injects it into every spawn,
    which makes it as agent-facing as a skill. Measured at `f723194` its two `DECISIONS.md` mentions
    (`harness-documentor.md:7,16`) match neither pattern — their verbs are "appending" and "declare" —
    so including the path costs nothing today and closes the hole tomorrow.
  verify: inspection
- SC-10: `.claude/skills/harness-handoff/SKILL.md` carries the discipline: the floor-not-ceiling
  framing and all four go-broad triggers, numbered. `grep -c` on the four trigger markers → 4;
  `grep -n 'floor'` → at least one hit (currently 0 for both — discriminating).
  verify: inspection
- SC-11: The index is bounded on two axes. **Structurally:** at most 260 lines, one physical line per
  decision row. **Per ruling:** at most **30 words** — counting only the text right of ` :: `,
  excluding any generated `— SUPERSEDED BY DEC-NN` suffix and excluding any `<!-- ok-stale -->`
  marker.
  verify: automated      evidence: unit

  **Amended 2026-08-02 on a user decision. This OVERRIDES a prior deliberate closure and needs the
  user's re-signature.** The wording signed on 2026-08-02 closed the grilling's open item
  **"does the ruling need a length cap"** on the structural cap alone, saying so explicitly:
  "the structural cap on ruling length … without adding a character-count rule" <!-- ok-stale -->
  That grilling item is hereby **reopened and answered yes, at 30 words** — the user's decision adds
  exactly the per-ruling length rule the signed sentence said was deliberately *not* being added, so
  the old rationale is now false, not merely narrower. Measured at `ce2cd17`: 82 of 169 rows exceed
  the cap (max 165 words), so this is remedial work on the shipped index, not a no-op tightening.
- SC-12: `.claude/skills/harness/bin/run-unit-tests.sh` exits 0, prints
  `PASS test-gen-decisions-index.py`, and prints no `MISCONFIGURED` line — the generator's tests are
  registered in the explicit script list rather than tripping the drift detector.
  verify: automated      evidence: unit

## Post-ship outcome measure — not a blocking SC

The grilling's headline measurable is the **next self-hosted feature's** cache-read-per-output ratio
dropping materially from the 137x measured on FEAT-03. It cannot be observed at this feature's ship
and is routable to no lead, so it is recorded here rather than as an SC. Whoever runs the next
feature reads it off `cost-report.py` and compares. The same run is the trigger for lowering
`per_feature_usd` from 120 in `harness.json`.

## Verification gaps — DEC-163

Read from `.harness/harness.json`: only `test_kinds.unit` has a `cmd`
(`.claude/skills/harness/bin/run-unit-tests.sh`). `functional`, `integration`, `component`, `ui`,
`eval` and `typecheck` are all `cmd: null`, so an SC resting on them would resolve to a soft skip and
could never be met. Every `automated` SC above therefore pins to `unit`.

- `eval` has no runner: the behavioural claim this feature actually rests on — that an agent given
  the index *greps it* instead of reading the authority whole — is LLM behaviour and is **not
  proven** by anything shipped here. It is carried by the post-ship cache-read measure above, and by
  nothing else. This is the largest unproven claim in the feature and the user should read it as one.
- No test kind covers `check-docs.sh` itself; it is a project gate, not a runner. SC-07 and SC-08
  therefore rest on `inspection` receipts, and SC-06 converts the part that *can* be automated (the
  checker's behaviour on a planted phrase) into a `unit` test so the DEC-169 presence assertion is
  permanent rather than a one-time reviewer note.
- `functional` and `integration` have no runner but the feature touches no service or DB path, so
  nothing is routed around here.

## Constraints

- Files-only, `python3` stdlib, no new dependency (`CLAUDE.md`).
- `check-docs.sh` must stay exit 0 at **45** emitted patterns. Never 48 (raw `<!-- stale:` lines; 3
  are dropped by the checker's `len(s) < 4` guard), never 49 (the grilling's arithmetic, which is
  wrong), and never the file count.
- The index never edits `docs/harness/DECISIONS.md`. Superseded entries stay where they are and are
  marked in the index only.
- The feature id is immutable (DEC-133).

## Out of scope — each is its own feature, and a task here would be a scope leak

- The archive split (moving superseded text to `DECISIONS-ARCHIVE.md`). The index delivers its whole
  value without moving a line.
- Per-project decision records via `harness-init`, including anything about kaya's backfill.
- `docs/harness/SPEC.md` and `docs/harness/BUILD.md`. The destination is scoped to one file.
- Lowering `per_feature_usd`; it needs the post-ship measure first.

## Approval

status: approved
approved-by: Mike Ruangutai
date: 2026-08-02
note: BRIEF only. PLAN remains pending — Q0 (T-09/T-10 executable by no agent) is unanswered.
