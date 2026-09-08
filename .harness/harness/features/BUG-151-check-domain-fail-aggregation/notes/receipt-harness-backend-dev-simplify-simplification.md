# SIMPLIFY / simplification — BUG-151 (harness-backend-dev)

## Examined
- `tests/integration/test-check-domain.py` diff `6d969ed3..fffc62d9` (149 lines), plus
  surrounding region: `_AggTee` (5185-5202), `_aggregation_verdict` (5204-5212),
  `run_bug151_selfcheck_cases` (5213-5241), `main()` (5244-5288).
- Pre-change comment at `6d969ed3` (`git show 6d969ed3:...`, lines 5207-5210) vs its
  replacement at 5269-5274, clause by clause.
- `plan.yaml` T-02 (lines 139-221) for the decisions that bound what counts as
  "simpler": D-01 (agreement-of-zeroness), D-02 (discovery), and the explicit step-5/
  step-6 instruction to special-case the CASES loop rather than fold it into discovery.
- All 24 `def run_*` definitions, confirming file order == globals() insertion order
  (no conditional defs, no redefinitions) — the discovery-loop comment's "in
  definition order" clause is literally true.

## Finding

1. **file**: `tests/integration/test-check-domain.py`
   **line**: 5239
   **summary**: `detail = str(verdict)[:120] if verdict is not None else "None"` is a
   no-op ternary — both branches always produce the same string.
   **cost**: `str(None)` is already the four-character string `"None"`, and slicing it
   `[:120]` leaves it unchanged, so the `if verdict is not None else "None"` guard is
   dead: for every possible `verdict` the expression evaluates identically to plain
   `str(verdict)[:120]`. It adds one more branch a reader has to hand-trace (and
   confirm is a no-op) inside `run_bug151_selfcheck_cases`, for zero behavioral
   difference — a pure complexity cost with no offsetting benefit. Confirmed by
   inspection, not by mutation: this is diagnostic-string formatting inside the
   self-check's failure path, not part of `_aggregation_verdict`'s predicate or the
   safeguard's ability to fire, so simplifying it carries no risk to D-01/D-02.
   **alternative**: `detail = str(verdict)[:120]`
   **backlog_only**: true — this line sits inside `run_bug151_selfcheck_cases`, which
   is part of the deliverable safeguard-under-test apparatus; per the assignment's
   restated hard boundary this pass runs after the qa gate, so this is a backlog row,
   not an apply.

## Candidates considered and rejected

- **Fold the CASES loop into discovery as a `run_cases()` function**, removing the
  near-duplicate tee/verdict stanza at 5248-5267 that mirrors 5278-5284. Rejected:
  plan.yaml T-02 step 5 explicitly directs "Apply the same capture and the same
  verdict to the CASES loop" as a construct separate from block discovery, and the
  task's own `verify:` asserts `len(blocks)==24` — folding CASES in would make it 25
  and contradict a pinned, tested count. The duplication is the anchored shape, not
  incidental duplication.
- **The discovery-loop comment (5269-5274) narrates the change ("DISCOVERED, never
  hand-maintained")**. Checked each clause against the code beneath it for truth
  (T-02's own instruction to remove a *false* prior claim): "in definition order" —
  true, verified against all 24 `def run_*` sites, none conditional or redefined;
  "runs under the same live-tee capture and the same `_aggregation_verdict`
  safeguard as the CASES loop above" — true, matches 5248-5267 structurally; "a trip
  alone fails the suite even when every block's own total was 0" — true, matches
  `return fails + len(problems)`. Every clause is true of the code beneath it, and
  the tense is present-invariant ("is discovered"), not a diff narrative ("was
  changed from … to …"), matching the file's existing comment convention (e.g. the
  D-01/D-09 style call-outs elsewhere in this file). Not a finding.
- **`D-01` is reused in this same file (line 5145, pre-existing, BUG-1305) for an
  unrelated decision ("forbids session-keyed ownership") while the new comments use
  `D-01` for "agreement-of-zeroness."** A future reader grepping "D-01" in this file
  gets two unrelated meanings. Rejected as a finding against *this* diff:
  short-id reuse across unrelated features without a feature-qualifying prefix is an
  established, repo-wide convention already present before this change (`D-02`,
  `D-09` are each reused for different topics elsewhere in the same file too) — this
  diff follows the existing convention rather than introducing a new one. Flagging
  the convention itself is out of scope for a 149-line diff.
- **`not block_name.startswith("run_") or not callable(block_fn)`** — De Morgan's
  dual of `not (startswith and callable)`. Same cost either way; not a simplification.
- **Two-phase `problems` accumulation** (`cases_verdict` appended once, then
  `block_verdict` appended per discovered block) reads as duplicated control flow.
  Rejected: CASES is structurally not a `run_*` block (see above), so there is no
  single loop this could collapse into without also refolding CASES, which is
  out of bounds per plan.yaml step 5.
- **Docstring of `_aggregation_verdict` (5204-5206) and the discovery-loop comment
  (5269-5274) both restate the zeroness rule.** Considered as "duplicate assertion of
  one fact through two spellings." Rejected: one documents the function at its
  definition, the other documents the call site's shared contract with the CASES
  loop above it — ordinary two-site documentation, not a redundant code assertion.

## Verdict basis
One genuine, low-risk, backlog-only finding. No proposal reduces the safeguard's
ability to fire, reintroduces a hand-written block enumeration, or touches D-01/D-02.
Working tree unmodified except this artifact.
