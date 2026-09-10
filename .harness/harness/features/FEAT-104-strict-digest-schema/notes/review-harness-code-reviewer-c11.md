reviewed: origin/main..984bd26b

# Verdict: PASS

BLUF: PF-C10-01 is genuinely closed on the merits. `_missing_required` names the exact absent
required key(s) under a truthful head; the mixed/non-mapping/exception cases all still deny. The
fail-open shape the batch context flagged does NOT exist at this pin: I re-derived (not adopted)
that only `type`, `additionalProperties` and `required` can report `error.path == []` against the
step subschema, and every one of those three either populates `_missing_required`, is caught
independently by the unconditional `_offending` accumulation lines that run before the
`if _schema_errors:` gate, or (non-dict step) both. Q14 and Q15 keep their present-tense ratings.
No new must_fix. `severity_max: low` (carried).

## 1. Census (MEASURED)

`git diff --stat origin/main..984bd26b -- . ':!.harness'`: **18 files, +3203/-19**. All 18 examined;
none skipped. `git diff --numstat 790023f0..984bd26b`: exactly `check-domain.sh` (+26/-8) and
`tests/integration/test-check-domain.py` (+6/-0) outside `.harness/` — confirmed by direct diff
(the hunk is entirely inside `shape_problems`, `:1645-1680`, plus the one new `_undeclared_cases`
case). Working tree `check-domain.sh` is byte-identical to `git show 984bd26b:...` (MEASURED, diff
empty).

## 2. PF-C10-01 closure (REASONED, source read at the pin)

`_missing_required` (`check-domain.sh:~1660-1668`) is `set(_error.validator_value) - set(_error.instance)`
gated on `_error.validator == "required"`. jsonschema only raises a `required` error when at least
one declared required key is absent from the instance, so this set can never be empty when the
branch fires — CONFIRMED, not merely plausible: the subtraction is definitionally the missing set.
The head `"missing required step key."` is truthful and distinct from the pre-existing
`"undeclared step key or evidence shape."` head, which is now gated on `if _offending:` instead of
firing unconditionally.

## 3. Fail-open re-audit (REASONED — MEASURED path blocked, see below)

Read `run-state-schema.json`'s step subschema directly (`:19-58`): declares, at the step's own
level, exactly `type: object`, `required: ["id","status"]`, `additionalProperties: false` — no
`minProperties`/`dependentRequired`/`dependencies`/`if`/`allOf`/`anyOf`/`not`. Every other keyword
(`minimum` on `cycles`/`max_cycles`/`redispatches`, `type` arrays on `seq`, `items` on
`depends_on`/`outputs`, `propertyNames`/`oneOf` under `evidence`) sits under a named property, so a
violation there reports `error.path[0] == <that property name>` — never empty. **CONFIRMS the
batch's claim**: only `type`, `additionalProperties`, `required` can report `path == []` at this
subschema.

Tracing each of the three against `shape_problems`:
- **`required`** → `_missing_required` (verified non-empty per §2). Fires correctly.
- **`additionalProperties`** (extra key) → its `path` is also `[]`, so the `_schema_errors` loop
  adds nothing for it — but `_offending.update(set(_step) - _declared)` runs **unconditionally in
  the per-step `for` loop, before the `if _schema_errors:` gate**, so the extra key is already in
  `_offending` regardless of what the jsonschema error loop does with it. Not fail-open.
- **`type`** (non-dict step) → same empty-path non-contribution from the error loop, but
  `if not isinstance(_step, dict): _offending.add("<step>"); continue` — also unconditional, before
  the gate. Not fail-open. Confirms (b).

(a) **Mixed** (missing `status` + rogue key on the same step): `required` fires →
`_missing_required = {"status"}`; `additionalProperties` fires too but is moot since `_offending`
already holds the rogue key from the unconditional accumulation. `_schema_errors` is non-empty (both
errors are in it), so both `if _missing_required:` and `if _offending:` bodies execute — **both
diagnostics fire**, confirmed by code structure, not merely argued.

(b) Non-mapping step — confirmed above, still refused.

(c) `except Exception` (`:~1678-1685`) wraps the whole `jsonschema`/schema-load/validate block,
independent of the specific violation shape — a broken schema file or missing library still denies
via a **third**, distinct head (`"run-state schema CANNOT be checked; the write is denied."`).
Unchanged by this delta, still fail-closed.

**Method note (contract-required disclosure):** I attempted to MEASURE this with a live
`jsonschema.Draft202012Validator.iter_errors` probe (constructing the nine violation shapes above
and printing `.path`) in a `mktemp -d` scratch directory, reading only `run-state-schema.json`
(read-only). `bash-write-guard` refused the redirect used to write the scratch script and the probe
output (`BLOCKED — harness-code-reviewer is READ-ONLY and this command writes files (redirect)`).
Per dispatch instruction this is reported, not worked around. The above is REASONED from source and
from jsonschema's documented `ValidationError.path` semantics (path is relative to the *validated
instance*, i.e. each step; whole-instance-level keywords — `type`, `required`,
`additionalProperties` — report at that instance's own root, path `()`; every other keyword here
sits under a named property and reports `path[0]` equal to that property).

**Verdict: CONFIRM** the closure is sound; **REFUTE** the batch's hypothetical fail-open — it does
not exist at this pin, by source enumeration of the only three empty-path-capable keywords.

## 4. Discriminating test (REASONED)

`_state("2").replace("    status: pending\n", "")` removes only the step's `status:` line (the
top-level `status: running` line has no 4-space indent, so it survives the exact-string replace),
leaving `{"id": "s1"}` — a genuine `required` violation for `status`. Assertion:
`returncode==2 and "missing required step key" in stderr and "status" in stderr`. Only the new
`if _missing_required:` branch (`:~1663-1668`) emits the literal `"missing required step key"`
substring anywhere in the file (grep-verified, single hit); the `except Exception` route's head is a
different sentence entirely and its body never contains that phrase, and the `_offending` branch's
head/body also never contain it. **The case can and does report RED discriminately** — it is the
correct positive control for PF-C10-01, and pre-fix code (single unconditional head, empty `_names`
join) would have failed both `in stderr` clauses, as `qa`'s own prior analysis (`STATE.md`,
`qa-2026-09-10-15.md:46-53`) already reasoned identically. Independent convergence, not adopted.

## 5. SC-08 step seam re-grade (MEASURED — grep)

`grep -rn 'missing required step key\|undeclared step key'` across `.claude/skills/harness/bin/`:
`"missing required step key"` has **exactly one producer** (`check-domain.sh:1663`).
`"undeclared step key"` (substring inside `"undeclared step key or evidence shape."`) has **two
producers**: `check-domain.sh:1671` (write-time) and `check-state.sh:1526` (at-rest sweep) — this is
the pre-existing CF drift (§7), unaffected by this delta. For the SC-08 discriminating clause itself
(the `strict` fixture, `rogue_step_key` only, no missing-required violation), the new head cannot
fire — that fixture's step has both `id` and `status` present, so `_missing_required` stays empty
and only the unchanged `_offending` branch runs. **The seam is still uniquely pinned** to its
intended producer; the new second head does not weaken the existing four-clause conjunction because
the two heads are mutually exclusive per-fixture in every case this suite exercises. c10's MET/
EXECUTABLE grading and its thin-symbol citation (Q13/Q5, `plan.yaml:460-462`, a decided plan
reading) stands — not reopened.

## 6. Q14 / Q15

- **Q14 — present-tense: low, unchanged.** Still reachable (a `type` error on a *declared* field,
  e.g. `cycles: not-an-int`, still lands in `_offending` via `_path[0]` and prints under the
  "undeclared step key or evidence shape" head, which tells the author to move a *declared* key
  under `evidence` — wrong advice, though the denial itself is correct and the key is named
  truthfully). Moves only if a fourth head is added distinguishing "invalid value on a declared
  field" from "undeclared key". Not this delta's job; PF-C10-01's fix touched only the
  `required`-vs-everything-else split, not this orthogonal one.
- **Q15 — present-tense: none reachable / latent design risk, unchanged.** No `minProperties`/
  `dependentRequired`/`dependencies` exists in the schema today (verified §3); the branch keys on
  the validator *name* rather than the structural cause (`path == []`), so a future schema author
  adding such a keyword at step level would silently fall into neither bucket. This is not a present
  defect and I am not proposing hardening against a keyword the schema doesn't declare, per
  instruction — it moves only when such a keyword is actually added.

## 7. Prior-finding dispositions

- **PF-C10-01** — CLOSED, confirmed above (§2-3).
- **F-104C10-01** (info, substring-anywhere assertions) — CARRIED, unchanged. Applies identically to
  the new `missing` case (`missing.returncode==2 and ... in stderr and ... in stderr` is the same
  whole-buffer style); not worsened, not newly gating.
- **F-104C10-02** (info, thin step-seam symbol vs. digest seam's three Python identifiers) — CARRIED,
  unchanged. The message text this citation targets is untouched by the delta.
- **CF-2** (severity contested: qa med / code info / c9 lead low — `check-state.sh:1590` discards
  `_host`, passes literal `"lead"`) — CARRIED, unchanged; `check-state.sh` is byte-identical since
  790023f0. My rating stays **info**: correct today by construction and pinned by
  `_t01_adequacy_failures`'s bidirectional case; only a *future* edit substituting `_host` would
  reopen it, and nothing in this delta touches that call site.
- **CF-3** (low — `abff2a84` FEAT-56 root-commit status flip, untracked by any REQ/D) — CARRIED,
  unchanged; still present in `origin/main..984bd26b`, still outside SC-13's four-file scope, still
  benign.
- **Q7** (5 spellings of the strict-schema-version predicate across `check-domain.sh`/
  `check-state.sh`) — CARRIED, unchanged; neither file's `_valid_version`/predicate logic is touched
  by this delta (confirmed by the numstat in §1 — only `shape_problems`'s tail changed).
- **F1/F2/F3** — F1 and F3 remain CLOSED (unaffected code, per c10). F2's DECLINED disposition
  STANDS — `check-state.sh` topology (the `validate("lead", ...)` call site) is unchanged.
- **`_no_parser` bootstrap early return** — CARRIED. Pre-existing, sits above both FEAT-104 blocks in
  source order, unaffected by this delta (the touched lines are inside the already-`_no_parser`-
  gated `state.yaml` branch's tail, not the guard itself). No new information.
- **DEC-85 Bash-write bypass** — CARRIED. Standing, acknowledged, out of scope; unaffected.
- **Stale comment at `check-domain.sh:1646-1647`** — CONFIRMED STALE (info, non-gating). Read at the
  pin: `"# Type/value failures on declared fields may not be captured by the vocabulary comparisons
  above; name their nearest field."` sits directly above the new `_missing_required` block it does
  NOT describe (that block names the *exact* absent key, not "the nearest field") — it accurately
  describes only the second half of the same loop (the `_path[0]` → `_offending` fallback). A future
  reader skimming only the comment would misunderstand what the `required` branch does. Concrete
  scenario: someone extending the `required` handling later, trusting the comment's "name their
  nearest field" framing, could reintroduce the PF-C10-01 shape by conflating the two mechanisms.
  Worth a one-line comment split; not blocking.

## 8. Code grade (MEASURED)

`code-grade.py --base $(git merge-base origin/main 984bd26b) --head 984bd26b`: **42 functions
graded, 0 SEVERITY lines, 0 RESULT: FAIL**. `_undeclared_cases` itself (the delta's own touched
function): cyclomatic 7, cognitive 2, ABC 17.3 → **grade 4**, PASS (bar 3, test code). No shell
functions are graded (tool limitation, pre-existing). `code_grade: pass`.

```yaml
VERDICT: PASS
DIGEST:
  headline: PF-C10-01 is genuinely closed; the hypothesized fail-open re-audit REFUTES a gap at this pin — only type/additionalProperties/required can report empty error.path, and all three are handled.
  severity_max: low
  findings: 6
  must_fix: []
  spec_violations: []
  code_grade: pass
  reviewed: "origin/main..984bd26b"
  human_commits_in_scope: []
  open_questions:
    - { id: Q14, question: "A type/range failure on a declared step key (e.g. cycles: not-an-int) still prints under the 'undeclared step key or evidence shape' head, advising the author to move a declared key under evidence — cosmetically wrong, denial still correct.", blocking: false }
    - { id: Q15, question: "shape_problems keys the required-vs-offending split on validator NAME ('required') not on the structural cause (empty error.path); a future minProperties/dependentRequired keyword at step level would satisfy neither bucket and emit no denial. No such keyword exists today; latent only.", blocking: false }
    - { id: Q-scratch-guard, question: "bash-write-guard refused even a mktemp -d scratch probe reading only run-state-schema.json read-only and writing only /tmp — confirming the read-only grant extends past tracked files. Reported per instruction, not worked around; no action needed unless a future reviewer needs live jsonschema execution.", blocking: false }
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-104-strict-digest-schema/.harness/harness/features/FEAT-104-strict-digest-schema/notes/review-harness-code-reviewer-c11.md
```
