# Two-layer approval guard — Q1 amend

**Both layers are in the plan, and layer 1's specified rule had to change shape, not just placement.**
The dispatch's layer-1 rule — deny an Edit payload containing a `status:` key at exactly two spaces —
closes ONE of the three attack shapes and misses the other two, including the accidental `replace_all`
shape it was introduced to close. It was replaced with an exact substring test that closes all three.

All counts re-derived in `.claude/worktrees/harness/FEAT-32` at **6bb7d82** unless stated.

## The corpus discriminator holds — every number in the dispatch confirmed

- **23** tracked `plan.yaml` (`git ls-files '*plan.yaml'`). `^  status: ` appears **exactly once in
  all 23**, and is the approval block's in all 23. In 22 the line above is literally `approval:`; the
  23rd is `.claude/skills/harness/templates/plan.yaml` at line 27, where `approval:` sits three lines
  above with two comment lines between.
- `^    status: ` is every task's, 1–17 per file. FEAT-32's own is 17, matching its 17 tasks.
- Exactly **two** `status:` lines at any other indent — `FEAT-14-feature-json-schema/plan.yaml:1154`
  (10 spaces) and `FEAT-32-concurrent-write-merge/plan.yaml:647` (11 spaces). Both are prose inside a
  task `intent:`, not YAML keys. Neither is a counter-example; both are accounted for in the plan.
- FEAT-32's approval block is lines **4–7**: `approval:` / two-space `status: pending` /
  `approved_by:` / `date:`. `approved_by:` occurs exactly **once** in the whole file.

## Why the dispatch's layer-1 rule was insufficient

Measured against FEAT-32's real approval block. `re.MULTILINE ^  status:` versus "payload occurs as a
substring inside the on-disk approval block's byte range":

| payload | indent rule | substring rule |
|---|---|---|
| targeted, two-space `status: pending` | DENIES | DENIES |
| mid-line-start, `status: pending\n  approved_by:` (first line at zero indent) | **ALLOWS** | DENIES |
| accidental, `status: pending` + `replace_all` (**18** matches, one is the signature) | **ALLOWS** | DENIES |
| a task's four-space `status: pending` | allows | allows |
| task-body chunk `change_type: logic\n    status: pending` | allows | allows |

The third row is the finding that matters: the dispatch named the accidental `replace_all` shape as a
must-close, and its own rule does not fire on it, because that payload contains no two-space line
start at all. **The mid-line evasion was therefore CLOSED, and so was a third shape the dispatch had
not identified.**

Layer 1 is now two limbs: **limb A** (`old_string` occurs as a substring of the on-disk fragment's
byte range — exact, indentation-independent, no reconstruction) and **limb B** (`new_string`
introduces the fragment's key at column zero or a child key at the indent read *from disk*). Only
limb B depends on the convention; the shipped comment says so and names limb A as the part that
survives a reformatting.

## The non-conflict is real, but its reason is not the one in the dispatch

`check-domain.sh:1039`'s refusal to reconstruct `old_string`/`new_string` sits in the **POST** branch,
and `old_string`/`new_string` appear **nowhere else in the file** — the PRE path has never inspected an
Edit payload. DEC-180 (`DECISIONS.md:5105`) explains why: a SHAPE verdict needs the whole *resulting*
file to count lines, so PRE would have to reconstruct. Neither limb reconstructs anything, so the
refusal stands.

Two consequences worth more than the non-conflict itself:

1. **DEC-180 fixes `_domain_phase = _governed and not _post` (`:294`), so the approval guard cannot
   exist post-hoc at all.** There is no fallback detection of a flipped signature. Layer 1 must be
   PRE, and this is the first Edit-payload inspection in the file — recorded in D-10 as a deliberate
   extension of DEC-180's boundary, not an oversight.
2. **The PRE tool-name short-circuit at `:1032` must NOT be touched.** An Edit already reaches the
   domain phase (entered `:316`; nothing between `:276` and `:316` exits on tool name); `:1032` gates
   only the SHAPE targets list. T-14's existing placement was already correct.

Residual accepted, not solved: limb A reads the block at check time, so there is a TOCTOU window,
bounded by the main session being the sole entitled writer and plan-merge.py locking every other route.

## Layer 2 forced a restructure of an existing test case

T-03 gains step **7b**: parse both sides, refuse **exit 8** when the proposal's `approval:` mapping
loads differently from the base's, applying nothing. Exit 8 rather than 7 because the remedies differ —
a conflict is reconcilable, "you are not the signer" is not — and the tool does not exist yet, so this
is the cheapest moment to pick the interface.

**Case 3 could not survive unchanged.** It graded `PRESERVE_BASE_BYTES` by applying a proposal claiming
`status: approved`; under 7b that now exits 8 and never reaches assembly. It was re-based on a
proposal whose approval is **loaded-equal but textually different** (reflowed, requoted, comment
dropped), which is *more* discriminating: `safe_dump` still destroys the comment and the quoting, and
the case now simultaneously proves 7b compares parsed values rather than text. SC-03's wording already
permitted this, so it needed no change. New case 10 carries the `status: approved` payload, with the
red proof asserting **the base file byte-identical and T-15 ABSENT** — a result-only assertion about
the approval block would pass with the refusal off, because step 7 carries the base bytes forward
either way.

## Baselines now in the plan

- `test-check-domain.py` at 6bb7d82, `CLAUDE_PROJECT_DIR` = worktree root: **exit 0, 167 lines
  beginning `ok`** (193 lines total). T-14's verify now asserts `>= 167` as a floor.
- `test-dispatch-guard.py` exits **2** — Python's no-such-file. Untracked and absent at this sha;
  **T-07 creates it**. Recorded beside the baseline a reader would establish, so it is not filed as a
  broken test.
- Q5: the 3 `ERROR` lines at 62f861c are recorded in T-10, next to the verify someone would be
  tempted to make them gate. **Not re-derived** — a different sha, and the integration suite depends
  on files T-03/T-07 have not built.

## Open

- **Q1 (non-blocking):** layer 1 denies any Edit whose `old_string` is a substring of the four-line
  approval block — `date:` alone, for instance. Conservative in the safe direction and the remedy is
  cheap (add context, or use plan-merge.py), but it is a real false-positive class and the build may
  meet it.
