# Goal-check delta — BUG-1308 — SC-01..SC-12 at review_sha `5942e34e`

**All twelve criteria are MET at `5942e34e82cf84fd127ff496fdb64202ad647ba6`. The feature's goals are
met at that commit.** No criterion unmet, none undeterminable, none unmeetable as written. Nothing
routed back; no `must_fix`.

**And that sentence is exactly the sentence I wrote at `48d2285b`, where REQ-03 was FALSE.** The
analysis of why is §3, and it is the part of this note that matters. Short form: **REQ-03 has two
clauses and only the first one has a criterion.** No SC-NN states the second.

Every automated criterion was RUN at this pin, not carried forward. Content read with
`git show 5942e34e:<path>` (G-15). `HARNESS_AGENT_TYPE` cleared for every suite invocation (O-01).

## 1. Suite baseline at the pin

| Suite | Command | Exit | `^FAIL ` | Files |
|---|---|---|---|---|
| unit | `.agents/skills/harness/bin/run-unit-tests.sh --kind unit` | 0 | **0** | 28 |
| integration | `.agents/skills/harness/bin/run-unit-tests.sh --kind integration` | 0 | **0** | 46 |

Counted with `grep -c '^FAIL '`, never a tail read (G-08). Named files run directly:
`tests/unit/test-expertise-ops.py` exit 0 / 102 PASS; `tests/integration/test-expertise-merge.py`
exit 0 / 198 PASS / `grep -c '^FAIL'` = 0; `tests/integration/test-gen-decisions-index.py` exit 0.

**Independent probe** (`/tmp/bug1308_probe_c3.py`, outside the tree, temp roots removed;
`--ops` given a FILE PATH throughout): **51/51**. All ten `str.splitlines()` boundary characters —
derived at runtime from `str.splitlines()` itself, `U+000A 000B 000C 000D 001C 001D 001E 0085 2028
2029` — refuse at exit 12 `MALFORMED OPS` in **both** `entry` and `target`, file byte-unchanged, and
the re-parsed section stays at 15. The cycle-2 exploit verbatim (a `replace` at capacity carrying
`U+2028`) now exits 12, is never `APPLIED`, and re-parses at **15, not 16**. A clean replace at
capacity exits 0 / `REPLACED P-07` / 15 entries / P-07 still 7th; a drop exits 0 / `DROPPED P-03` / 14.

## 2. The twelve, at `5942e34e`

| SC | Verdict | Method | Command run | Observed |
|---|---|---|---|---|
| SC-01 | **met** | automated / integration | `python3 tests/integration/test-expertise-merge.py` | case11 ×6: exit 0; `REPLACED P-07`; Patterns still 15; 7th entry line is P-07 and carries the new text |
| SC-02 | **met** | automated / integration | same | case12 ×8: exit 0; `DROPPED G-03`; `- G-03:` absent; G-01/02/04/05 each still present |
| SC-03 | **met** | automated / integration | same | case13 ×7: exit 10; `MISSING TARGET` + `P-99` + `Patterns`; sha256 unchanged; byte-identical; following apply exit 0 |
| SC-04 | **met** | automated / unit+integration | both files | clause table below — all four conditions fixtured |
| SC-05 | **met** | automated / integration | integration | case15 ×3: non-zero exit; sha256 equals pre-invocation; following add-only apply exit 0 |
| SC-06 | **met** | automated / integration | integration | exit 0; case16 re-asserts exit 7 CONFLICT and exit 8 CAP EXCEEDED; `git diff origin/main -- .claude/skills/harness/bin/expertise-merge.py \| grep -c '^-[^-]'` = **0** (pure addition) |
| SC-07 | **met** | automated / unit | `python3 tests/unit/test-expertise-ops.py` | exit 0; u10 feeds the same replacement to `compute_union`: "returns non-empty conflicts" + "merged Patterns still carries OLD text at index 6" |
| SC-08 | **met** | automated / integration | integration | `check-expertise.sh` exit 0 on the replace-produced file (case11), the drop-produced file (case12) and case19 |
| SC-09 | **met** | automated / integration | integration | case17 ×11 — anchor matches once; real SKILL.md clean; copies (a)/(b) redden FIRST direction only, (c) SECOND only |
| SC-10 | **met** | automated / integration | `git show 5942e34e:.harness/harness/docs/DECISIONS-INDEX.md` + `python3 tests/integration/test-gen-decisions-index.py` | `DEC-219` row at `:219`; phrase `replace and drop through the ops subcommand` count = **1**; generator test exit 0 |
| SC-11 | **met** | automated / integration | integration | case18 ×5: **2.04s** hold, neither child exited; both exit 0 after release; census = original 8 + P-09 + P-10; P-07 carries child B's marker |
| SC-12 | **met** | automated / unit+integration | both files | case19 ×7 (file-order `P-02,P-03,P-04,P-05`, marker on P-05 only) + u11 ×7 forward **and** reversed, identical + u12 ×2 |

### Clause-by-clause for the multi-clause criteria (P-04, P-05)

**SC-04**, four conditions, each with its own assertions — never a file-global grep:
duplicate id in file → case14(b) exit 11 + `AMBIGUOUS TARGET` + `P-04` + section + reason + sha256;
two ops on one target → case14(c) same five, id `P-01`; `section` **absent** → u13 across four verbs
+ case20(a) through the CLI; `section` **empty** → u13 + case20(b). The trailing gloss (sha256
unchanged across the refusal, following `apply --entries` exit 0) binds to case20 and is asserted.

**SC-12** composition: the two-op case is asserted at the CLI forward (case19) and at the resolver
forward **and reversed** with an explicit "forward and reversed produce identical merged Patterns";
second shape (two drops) is u12 with its own sequence `[P-02,P-03,P-05]`.

## 3. Why twelve green criteria did not see the VL-05 hole — the confrontation

At `48d2285b` I graded all twelve **met** and every one of those verdicts was **true**. The commands
were right, the evidence was right, the clause-by-clause discipline was applied. And REQ-03 was
false at that commit. That is the uncomfortable fact this section exists to explain, and the
explanation is not "the grading was sloppy".

### The requirement, and where its two clauses went

> **REQ-03**: "Section caps are preserved: *a replace at capacity succeeds and leaves the section the
> same size*; **no operation can leave a section over its cap**."

Two clauses. Trace each to a criterion:

- **Clause 1** → **SC-01**: *"With `Patterns` holding 15 entries, a proposal replacing `P-07` exits 0
  … the file still holds 15 `Patterns` entries."* Covered — **existentially**. SC-01 grades ONE
  proposal, with ONE benign fixture, whose text the author chose.
- **Clause 2** → **nothing.** No SC-NN in the BRIEF quantifies over operations or over input text.
  The nearest neighbour is **SC-06**, whose cap clause is *"including exit 7 CONFLICT and exit 8 CAP
  EXCEEDED"* — a **regression** clause on the pre-existing add-only `apply --entries` path, which
  says nothing about the new `ops` path at all.

Clause 2 is a **universal negative over all operations and all inputs**. It is the clause an attacker
falsifies. It was never turned into a criterion.

### The mechanism that broke was outside every criterion's surface

Sharper still. The defect lived in `_reject_multiline` — the shape gate deciding whether an
`entry`/`target` value may be written verbatim by `render`. Which criterion grades that gate?

**Exactly one criterion mentions exit 12 `MALFORMED OPS` at all: SC-04.** Its clause reads:

> *"an op with `section` absent, and one with it empty, each refuse at exit 12 with `MALFORMED OPS`
> naming the offending key **`section`** and the op's index"*

It is explicitly and exclusively scoped to one key. **The words `entry` and `target` do not appear in
any exit-12 clause of any of the twelve criteria.** So the function whose line alphabet was wrong sat
entirely outside the graded surface. A goal-check grading all twelve criteria correctly, with perfect
method, cannot reach it. The hole was invisible **by construction**, not by oversight.

### The classification

**(b) — a criterion is missing entirely.** Not (a), and I want to be precise about why not: calling
SC-01 "under-specified" would be wrong. SC-01 never claimed universality; it is a happy-path
existence criterion and it was correctly met both times. Nothing about a two-character newline
alphabet appears in any criterion, because **no criterion talks about the newline alphabet at all** —
there was no narrow quantifier to widen. The missing thing is REQ-03 clause 2 as a criterion.

**(c) contributes, in the requirement-to-criterion mapping — and it is mine.** REQ-03's two clauses
were traced as one unit to SC-01. A REQ-coverage pass that split multi-clause requirements the way
P-04 already tells me to split multi-clause *criteria* would have shown clause 2 with no SC against
it. I apply clause-splitting to SCs when grading and did not apply it to REQs when tracing. That is
the specific procedural failure, and it is a pm failure, not a qa or panel one.

Not (c)-as-grading-method and not (c)-as-evidence-selection: no command I ran was wrong, and no
better evidence for the twelve criteria as written existed.

### The compounding failure worth naming

The **cycle-1 panel had already found this exact class** — VL-01, an `entry`/`target` rendered
verbatim past a cap check that counts only parsed entries. The fix landed. **No criterion was added,
because BRIEF is approval-gated and nobody proposed one.** So the cycle-2 goal-check re-graded twelve
criteria, none of which mention the surface a panel had just holed, and returned green — and the
cycle-2 panel then found the same class again at a wider alphabet. A landed panel finding does not
create a criterion, so consecutive goal-checks stay blind to the same surface. Raised as Q1.

**What did catch it, both times: the panel, behaviourally.** Per P-13, the twelve criteria collapse
to a small number of independent methods; the adversarial-input method was not among them.

## 4. Emergent criterion — RECOMMENDED TO THE OPERATOR, NOT ADOPTED

**I have not touched BRIEF.md.** Adopting this is the operator's call.

> **SC-13 (proposed) (REQ-03, cap-preservation under adversarial text):** No `ops` operation can
> leave a section over its cap, whatever text an op carries. For every character `str.splitlines()`
> treats as a line boundary — the set derived at test time **from `str.splitlines()` itself, never a
> hardcoded character list** — an `ops` proposal whose `entry` or whose `target` embeds that
> character exits 12 with `MALFORMED OPS`, the file's sha256 is unchanged, and the file re-parsed by
> `parse_expertise` holds no section with more entries than its `CAPS` value. The at-capacity
> variant is exercised explicitly: the same proposal against a section already holding its cap
> re-parses at exactly the cap, never cap+1.
> **verify: automated        evidence: unit, integration**

**New vs covered: NEW.** Read strictly, no existing SC implies it — SC-01 is existential over one
benign fixture, SC-04's exit-12 clause is scoped to the key `section`, SC-06's `exit 8 CAP EXCEEDED`
is a regression clause on the add-only path. **It would grade `met` at `5942e34e`** (case21 including
its cap-bypass and cross-section assertions, case22, u17, u18, plus my 51/51 probe), so adopting it
changes no verdict today. Its whole value is that the surface becomes *graded* rather than
*incidentally covered* — the next regression on it would be caught by the goal-check, not by a panel.

The self-derivation clause is load-bearing and is why I propose this wording rather than a character
list: an enumerated alphabet is the very shape that failed, and `_reject_multiline` was
deliberately fixed by deferring to the parser's own splitter rather than by enumerating (see its
docstring at `expertise-merge.py:170-188` at the pin).

## 5. Unmet criteria, and non-gating findings

**Unmet: none.** No owning task id, no code-vs-tests routing required.

Non-gating, none blocking the ship (one cycle remains):

| # | Finding | Class | Nature |
|---|---|---|---|
| N-1 | `_reject_multiline` keeps the narrower `"\n" in value or "\r" in value` branch above the `splitlines()` check; its own docstring says it "never fires on its own". Dead code that invites a future reader to believe the alphabet is two characters. | advisory | chore |
| N-2 | No criterion covers REQ-03 clause 2 (§3). Remedy is the operator adopting SC-13, not a code or test change — the tests already exist. | advisory | enhancement |
| N-3 | Pre-existing, already backlogged, restated only so it is not re-raised: SPEC §5.3 apply-side citation drift, `EXPERTISE_MERGE_BIN` override, `cmd_ops` traceback on a missing `--ops` path. | backlog | bug/chore |

## 6. Proof nothing was changed

`git status --porcelain` at the end of grading — the single entry is this artifact:

```
?? .harness/harness/features/BUG-1308-expertise-replace-drop/notes/research-BUG-1308-expertise-replace-drop-goalcheck-sc-c3.md
```

HEAD unmoved at `14a22b7c`. No commit, no formatter, no linter. BRIEF.md, plan.yaml, STATE.md,
feature.json untouched; the c2 note untouched; no `notes/review-*.md` touched. Probe lived under
`$TMPDIR` and its temp roots were removed.

## 7. Open questions

- **Q1 (non-blocking, harness process):** when a panel finding falsifies a REQ and the fix lands, no
  step turns that finding into a criterion, so the next goal-check grades the same twelve criteria
  and is blind to the same surface. Observed twice on this feature (VL-01 → VL-05). For the harness
  owner: should a REQ-falsifying panel finding require a proposed SC alongside the fix?
