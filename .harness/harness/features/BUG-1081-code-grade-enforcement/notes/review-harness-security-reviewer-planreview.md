# Security threat-model — BUG-1081 code-grade enforcement (plan review)

Scope: BRIEF.md + plan.yaml under this feature directory. This is an enforcement-boundary change to
`validate-digest.py` (DEC-174 carve-out). Read-only review, no edits, no tests run.

## Verdict

**PASS.** No high/critical findings. Two `med` findings on evidentiary rigor — both should be closed
before/while T-01/T-02 execute, but neither is a demonstrated bypass in the plan as written, and both
are inside main-session-direct's control to fix without a plan re-signature.

## What the plan gets right (checked against the false-pass checklist)

- **Base/head separation (D-02, SC-05):** the mechanical range is `merge-base(default branch,
  review_sha)..review_sha`, both boundaries repository-derived; the digest's own `reviewed` base is
  discarded and only its head is bound (must resolve to `review_sha`). This mirrors the SEC-01
  wave-4 hardening already in `validate-digest.py:637-682` (`_derived_reviewed_python_change`) and
  correctly generalizes it to `pass`/`fail`/`grade_2` rather than only `n_a`.
- **Fail-closed on grading failure (D-05, SC-04, REQ-03):** the intent text explicitly requires
  catching grader/repository exceptions inside the validation boundary and converting them to a named
  contract violation, never a traceback or a silent accept. This is the correct place to catch it:
  `hook_mode()` (`validate-digest.py:1437-1620`) wraps its call to `validate()` in
  `except Exception: return 0` — "fail open, loudly, on our own bug" (DEC-127's own precedent, same
  file). If the new grading call is allowed to raise *out of* `validate()`, that outer handler will
  silently accept the digest, exactly inverting REQ-03. The plan's own wording ("Catch grader and
  repository errors **at this boundary**") places the catch on the correct side of that line.
- **DEC-174 library/gate split (D-03, T-01 vs T-02 lanes):** moving classification/bar logic into an
  importable module consumed by both `code-grade.py` and `validate-digest.py`, with only the
  validator itself and its test on the main-session-direct lane, matches DEC-174's own stated carve-out
  ("a module a gate imports is not itself a gate... a squad may write the library") almost verbatim.
  Not a new hole — `code_grade.py` is *already* team-lane today; this plan does not newly delegate
  trust that wasn't already delegated, it only makes the validator a consumer of it.
- **Branch/artifact corroboration untouched:** `code_grade_bound_to_review` already runs
  unconditionally for `pass`/`fail`/`grade_2`/`n_a` (existing code, `:950-998`) and the plan does not
  touch it; the new mechanical check rides on the same `feature_dir`/`review_sha` resolution path
  (`resolve_review_sha` → `_resolve_feature_dir` → artifact-line derivation → branch corroboration),
  so it inherits the existing cross-feature/branch-spoof protections rather than opening an
  independent, uncorroborated lookup.
- **n_a boundary (D-04, SC-03):** correctly bidirectional — a digest claiming `n_a` when Python did
  change is rejected (existing rule), and a digest claiming a graded value (`pass`/`fail`/`grade_2`)
  when the canonical range is degenerate or touches no Python is also rejected, since the classifier
  is explicitly barred from deciding `n_a` itself (T-01 intent: "It does not decide `n_a`").

## Findings

### F1 (med) — The core false-pass fixture is not pinned to the real `--hook` exit-code path with automated evidence

**Evidence:** T-02's intent paragraph requires "at least one assertion must exercise `--hook`'s exact
rejection exit code so a crash cannot masquerade as a refusal," but the sentence sits at the end of a
fixture list whose neighboring clause is the grader-exception fixture, and the only SC that names
"the real validator entry path" generally is **SC-10, `verify: inspection`** — not automated. SC-01
(the fixture that reproduces the named defect itself: blocking function + `code_grade: pass`) is
`verify: automated, evidence: integration` but does not itself specify it must run through
`hook_mode()`'s JSON-stdin surface rather than a direct `validate()` call.

**Failure scenario:** T-02 lands with SC-01 proven only against `validate()`'s return value, and the
one `--hook`-exit-code assertion required by the loose prose is satisfied solely by the grader-exception
fixture (SC-04). `hook_mode()` carries extra pass-through branches ahead of the `validate()` call
(`agent_type` checks, `stop_hook_active`, the inflight-registry release/roll-up block) that the direct
`validate()` tests never exercise; a future edit to that surrounding code could reintroduce exactly the
gap DEC-127 was written to close — this same file, previously green at the `validate()` level while
`--hook` had zero coverage on the code path that actually gates real dispatches (DEC-127, "the fourth
time this project has learned that a green suite exercising the wrong surface is indistinguishable from
no suite").

**Required correction:** Add (or amend SC-01) so the primary bypass fixture — not only the crash
fixture — is asserted through the literal `--hook` JSON-stdin path with the exact exit code checked,
`verify: automated`, not folded into SC-10's inspection-only claim.

### F2 (med) — D-07's stated safeguard ("mutation evidence") for the grading library is not traceable anywhere in the repo record

**Evidence:** D-07 justifies not building a second grading implementation on the grounds that
"semantic correctness of the one grading implementation remains protected by its contract tests and
mutation evidence." `DECISIONS.md` and `DECISIONS-INDEX.md` have no entry for `code_grade`/`code-grade`
grading logic or `FEAT-43`, and `test-code-grade.py` / `test-code-grade-cli.py` contain no reference to
mutation testing. Mutation testing *is* an established, recorded practice in this repo for
enforcement-adjacent logic (`DECISIONS.md:4764-4768`: "six mutants were run against `check-state.sh`
and six against `check-domain.sh`," with the one survivor named and justified) — so the vocabulary is
real, but no matching record exists for the grading module this feature is about to make authoritative.

**Failure scenario:** This feature converts `code_grade.py`'s classification from advisory (a human
runs the CLI, reads it, self-reports) to the *sole* enforcement authority — SC-01 through SC-08 all
assume the classification seam's answer is ground truth and gate purely on digest/expected agreement.
A latent logic defect in `gated_set()`/the bar thresholds (wrong grade-2/blocking precedence, an
off-by-one bar, a missed AST node type) would now produce a systematically wrong "expected" value that
every comparison in T-02 would treat as correct, with only an ordinary (non-adversarial) unit suite as
protection — the exact class of risk mutation testing exists to catch, and the exact class this repo
already pays for elsewhere in the enforcement layer.

**Required correction:** Either cite where the mutation evidence for `gated_set()`/bar classification
already lives (if it exists under a different feature this plan didn't cross-reference), or add
mutation evidence for the classification/bar logic as an explicit T-01 deliverable before D-07's
premise is relied on to justify skipping a second implementation.

## Not findings (assessed and dismissed)

- Team-lane `code_grade.py` becoming the enforcement gate's sole source of truth: covered by DEC-174's
  own library-vs-gate carve-out language; not new exposure introduced by this plan (P-12/DEC-174).
- Cross-feature `artifact:`/branch spoofing of `feature_dir`: pre-existing SEC-01 wave 2–3 protection,
  unmodified by this plan, reused by the new mechanical check via the same resolution path.
- Default-branch drift changing the derived merge-base between review time and validation time: the
  degenerate-range check (`review_sha` already an ancestor of default → refuse, not accept) keeps this
  failure mode fail-closed in the direction that matters (narrows to nothing → refusal, never a silent
  empty-diff accept).

## threat_model

| boundary | STRIDE | mitigated |
|---|---|---|
| digest `code_grade` claim vs. repository-computed classification | Tampering | true (D-01/SC-01-03, contingent on F1) |
| digest `reviewed` base/head vs. repository-derived canonical range | Tampering | true (D-02/SC-05) |
| grading-seam exception vs. `hook_mode`'s own fail-open-on-bug handler | Denial of Service / Tampering | true in plan text, contingent on implementation catching inside `validate()` (D-05/SC-04) |
| team-lane grading library correctness vs. main-session-direct validator trust | Tampering | false — no mutation/adversarial evidence found (F2) |
| cross-feature artifact/branch binding | Spoofing | true — pre-existing SEC-01/DEC-174, unmodified |
