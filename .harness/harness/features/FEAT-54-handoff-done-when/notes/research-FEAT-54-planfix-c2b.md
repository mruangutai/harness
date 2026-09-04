# Plan fix c2b — goal-check F-03 closed — FEAT-54

## BLUF

**F-03 is closed.** T-04's intent now instructs the doer to bring `check-domain.sh`'s own prose into
the five-section contract — both live four-section claims named by CONTENT, not line number — and
BRIEF SC-08 is widened so a surviving four-section claim anywhere in either gate script (comments and
user-facing messages included) is caught rather than assumed. REQ-09's "no live document **or gate**"
clause is now carried by a graded criterion. Only T-04 moved in `plan.yaml`; nothing else changed.

Read/written at worktree `FEAT-54-handoff-done-when`. F-01 remains open by design (the `panel:`
mapping is rewritten wholesale by the c2 panel transcription); F-02, F-04, F-05, F-06 untouched.

**Cycle 2 (2026-09-02):** SC-08 as landed in cycle 1 was ungradeable — it quantified over dated
historical prose in `check-state.sh` that rule 15 protects. It has been rewritten in place with a
mechanical historical exemption; Q1 is CLOSED. Nothing else moved and `plan.yaml` was not touched.

## What changed

### 1. `plan.yaml` task T-04 — `intent` only

One new bullet plus a conflict-resolution paragraph, inserted after the cap clause:

- **(i)** the normative `DEC-159:` comment immediately above the `RE_HANDOFF` branch, which today
  says the note is working memory for a successor with "four fixed sections", must state FIVE and
  name `## Done when`.
- **(ii)** the 60-line whole-file cap's refusal message, which today enumerates the note as
  "intent, trust, dead ends and a working set", must enumerate five and name `## Done when`.
- Both located **by content, never by line number** (they move).
- **The interaction is resolved in the text.** The pre-existing clause "keep the 60-line whole-file
  cap and its message unchanged" is left byte-identical, and the new paragraph states explicitly
  that it bounds the cap's VALUE (60) and the absence of any per-section cap — it does **not** freeze
  the message's four-section enumeration, and satisfying either clause by violating the other is a
  failed task. Without that sentence a doer could green the cap clause by leaving claim (ii) standing.

Every other clause of T-04's intent is byte-identical (required-heading list and its "four
sections"→"five sections" wording change, the sibling-module import with `resolve=True`, the cap
value and no-per-section-cap rule, the import-failure-is-a-REFUSAL paragraph, the
do-not-edit-test-check-domain.py paragraph). `traces`, `files`, `verify`, `depends_on`,
`execution_mode`, `execution_reason` untouched.

**Amend mechanics.** `plan-merge.py amend --key tasks --id T-04 --field intent`,
`--expect-sha256 d82074601b44babf3b6709fe938c5f0aec67617462e06dd3a0df62e4b079717b` (the value read
before the write), value from `/tmp/feat54_t04_intent.txt`. Reported
`AMENDED tasks:T-04.intent`. Post-amend field sha256:
`d5e1ec5463117297df21390d3c43121ad9b200ccb983cfccfbd5b8d5932527f8`.

### 2. `BRIEF.md` SC-08 — widened in place, no renumbering, `verify: inspection` kept

**SUPERSEDED by "Cycle 2" below.** The text quoted in this section is cycle 1's SC-08; it was
ungradeable and has been rewritten. Read the cycle-2 section for the criterion now on disk.

```
- SC-08: Read at `review_sha` (`git show <review_sha>:<path>`), no four-section assertion survives
  in `.claude/skills/harness/templates/HANDOFF.md`, `.claude/skills/harness/SKILL.md`, the DEC
  record, or ANYWHERE in `check-domain.sh` or `check-state.sh` — required-section lists, heading
  constants, normative comments AND user-facing refusal or cap messages alike; each states five and
  names `## Done when`. Falsified by: any line in either gate script enumerating four sections, or
  any cap or refusal message listing intent, trust, dead ends and a working set without
  `## Done when`.
  verify: inspection
```

The old scope was "`check-domain.sh`'s required-section list" and "`check-state.sh`'s handoff heading
constants" — exactly the two places T-04/T-07 already edit, so the criterion was satisfiable while a
comment and a refusal message still taught four sections. The new falsifier names the concrete
surviving line shapes.

## Proof collected

- **Only T-04 moved.** Per-id sha256 of `yaml.safe_dump(entry, sort_keys=True)` over all 12 tasks and
  9 decisions, before vs after: the diff is one line, `tasks/T-04`
  `b1f0b507…` → `5337192877…`. All other 20 ids byte-identical.
- **Field re-read from disk** via `amend --show`: the new clause and the resolution paragraph are
  present; the preserved clauses are intact.
- **`check-plan-routes.py <plan>` → `0 violation(s) across 1 plan(s)`, exit 0.** The 8 `DEVIATION`
  lines are the pre-existing DEC-174 carve-outs (advisory, non-gating).
- **Plan still well-formed:** `harness_yaml.load_plan` gives 12 tasks T-01..T-12, 9 decisions
  D-01..D-08 + D-10, `status: plan`, `approval.status: pending`.
- **No collateral files:** `git status --porcelain` shows only the pre-existing FEAT-52→FEAT-54
  rename metadata (which carries `plan.yaml` and `BRIEF.md` as modified-renamed), the two untracked
  c2 notes, the product-lead observations file, and this note.

## What the repair could not reach

- **F-01** (`panel.findings` PF-4205e7e2… `disposition: open`) is out of scope here by the dispatch:
  the whole `panel:` mapping is re-transcribed after the panel reruns. It is still blocking for
  signature.
- **F-04** (T-04 double-reports the missing section: the required-heading list and the module both
  name it) is advisory and was NOT fixed — the dispatch scoped this cycle to F-03, and de-duplicating
  the message would change a clause I was told to keep byte-identical. Whoever runs the next fix
  cycle should decide it.
- **`check-state.sh:1188` / `:1201-1204`** four-section-flavoured comments: **RESOLVED in cycle 2,
  Q1 CLOSED.** Cycle 1 raised them as Q1 because SC-08 as widened then quantified over ANY
  four-section assertion in `check-state.sh` and so the grader would meet them. The ruling: they
  are dated historical measurement and incident narrative that rule 15 protects, so SC-08 — not
  the record — was amended to exempt them mechanically. See the cycle-2 section.
- Neither approval block was touched; both remain `pending`.

## Cycle 2 — SC-08 made gradeable; Q1 CLOSED

**The ruling (product lead, implemented not re-litigated).** The two four-section mentions in
`check-state.sh` — `:1188` "All 74 carry the four headings and are within the cap" and `:1203`
"a note carrying all four headings and nothing under any of them passed" — are DATED HISTORICAL
MEASUREMENT and incident narrative, each anchored to a past sha and a past feature, not statements
of the live contract. PRINCIPLES rule 15 forbids rewriting the record to look better, so they
STAY, and no task orders them edited. The defect was therefore in the SENTENCE, not the code
(P-06): cycle 1's SC-08 quantified over ANY four-section assertion anywhere in either gate, so
those two lines falsified it and the criterion was ungradeable — at review it could only be waved
off (defeating it) or discharged by a record edit. SC-08 now carries a mechanical exemption a
reviewer applies without judgement.

**Q1 is closed.** Q2 (F-04, T-04's double-report of the missing section) stays advisory and out of
scope, unchanged.

### SC-08 as landed, verbatim (BRIEF.md:106-124)

```
- SC-08: Read at `review_sha` (`git show <review_sha>:<path>`), no assertion about the CURRENT
  contract survives as four sections in `.claude/skills/harness/templates/HANDOFF.md`,
  `.claude/skills/harness/SKILL.md`, the DEC record, or ANYWHERE in `check-domain.sh` or
  `check-state.sh` — required-section lists, heading constants, normative comments AND user-facing
  refusal or cap messages alike; each states five and names `## Done when`.
  EXEMPT, and to be left byte-identical: a comment that reports a PAST MEASUREMENT or a past
  incident rather than the live contract, identified mechanically by BOTH naming a specific past
  commit sha or a past feature id AND reporting what was observed at that point — a count taken
  then, or the behaviour of the code as it stood then. PRINCIPLES rule 15 forbids rewriting the
  record, so such a line is not a defect and no task orders it edited. The
  two known exempt sites, named by content because line numbers move, both in `check-state.sh`:
  the FEAT-31 74-note migration measurement ("Measured at cf51dce ... All 74 carry the four
  headings and are within the cap") and the INV-17 empty-body-check narrative (FEAT-31 T-10, "a
  note carrying all four headings and nothing under any of them passed").
  Falsified by: any line, or any comment wrapped across lines, in either gate script that states
  the CURRENT contract as four sections — a required-heading list, a heading constant, a normative
  comment above a branch, or a refusal or cap message enumerating intent, trust, dead ends and a
  working set without `## Done when`. A line meeting the exemption test above is NOT a falsifier.
  verify: inspection
```

Everything cycle 1 gained is kept byte-for-byte in substance: read at `review_sha` via
`git show`, the five-file scope including ANYWHERE in both gate scripts, the enumeration of what
counts (required-section lists, heading constants, normative comments AND user-facing refusal or
cap messages), "each states five and names `## Done when`", and `verify: inspection`. Two things
are added: the subject is narrowed to claims about the CURRENT contract with the exemption test
spelled out, and the falsifier now reads "any line, or any comment wrapped across lines" — needed
because the live `check-domain.sh` DEC-159 claim wraps ("four fixed" on `:1512`, "sections" on
`:1513`), so a line-only falsifier would have missed the very site F-03 was raised about.

### Proof — the new falsifier applied to both gates at HEAD

Gates unmodified this cycle (`git diff --name-only -- check-domain.sh check-state.sh` empty), so
the working tree IS HEAD for them. Candidate sites, from
`git grep -nE 'four (fixed )?sections|four headings|intent, trust|"## Next", "## Trust"'`:

| site | file:line | live contract? | names past sha / feature id + observed? | verdict |
|---|---|---|---|---|
| A | `check-state.sh:1188` | no — reports a migration count | yes: `cf51dce`, `FEAT-31`, "74 notes match" (`:1184-1191`) | **EXEMPT, not flagged** |
| B | `check-state.sh:1203` | no — narrates the pre-change behaviour | yes: `FEAT-31 T-10` (`:1200`), "Until now it could not be ... passed" | **EXEMPT, not flagged** |
| C | `check-domain.sh:1512-1513` | yes — normative `DEC-159:` comment above the `RE_HANDOFF` branch, "four fixed / sections" | no past sha, no feature id anywhere in `:1511-1525` (only `DEC-160`, a decision id) | **FLAGGED** |
| D | `check-domain.sh:1517-1518` | yes — the 60-line cap's user-facing message, "It is intent, trust, dead ends and a working set" | no | **FLAGGED** |
| E | `check-domain.sh:1519` | yes — `required = ["## Next", "## Trust", "## Dead ends", "## Working set"]` | no | **FLAGGED** |
| F | `check-domain.sh:1523` | yes — refusal message "the four sections are the contract" | no | **FLAGGED** |

So the criterion still catches exactly what F-03 was raised about — C and D, the two sites T-04's
amended intent orders fixed, plus the required-list/refusal pair E and F that T-04 already
covered — while A and B, which no task touches and rule 15 protects, are exempt by a written test
rather than by a reviewer's judgement. No live-contract site in either gate satisfies the
exemption test (checked: neither `DEC-156` at `:1525` nor `DEC-160` at `:1514` is a feature id or
a commit sha, and neither sits inside a four-section claim).

### Document integrity

- Criteria: **15 before, 15 after** — `SC-01 … SC-15` contiguous, none added, none removed, no
  renumbering; 15 `verify:` lines, one per criterion. (HEAD's pre-rename copy carries 14; SC-15
  landed in an earlier uncommitted cycle, so the before/after baseline is the pre-edit working
  tree, not HEAD.)
- `## Approval` → `status: pending`, `approved-by:` and `date:` empty. Untouched.
- `git status --porcelain` from the worktree root: **no newly modified file.** The 12 `RM` rows are
  the pre-existing FEAT-52→FEAT-54 rename (BRIEF.md among them, now also content-modified;
  `plan.yaml` unchanged this cycle — `plan-merge.py` was NOT run at all), plus the four
  pre-existing untracked notes/observations files, this note among them.
- `plan.yaml`, every gate script, `STATE.md`, `feature.json`, `panel:` and `approval:` untouched.
- Edits confined to the SC-08 block: four hunks, every one inside `BRIEF.md:106-124`. Nothing
  above SC-07's `verify: inspection` line or below SC-09's opening line was addressed. The verbatim
  quote above was extracted from the file with `sed -n '106,124p'` and diffed against the fence in
  this note — diff empty.
- Also written this cycle, as the expertise skill mandates: `observations/harness-pm.md`, one
  appended bullet via `observations-merge.py apply` (18 prior bullets reported PRESERVED).
