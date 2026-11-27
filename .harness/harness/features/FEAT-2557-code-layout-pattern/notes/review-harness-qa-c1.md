# QA gate — FEAT-2557 · run r-20261127-1-validate-validator · cycle 1

**BLUF: PASS. `matrix_ok: true`, `suite: n/a`, `kinds: []`.** T-01's change_type `docs` requires
no test kind at the pin, so no runner was run and no receipt was written (none invented).
`fail_first: []` is legitimate: every SC (SC-01..SC-06) is `verify: inspection`. The T-01 verify
re-ran green at the pin; its guards are non-vacuous, with six low-severity weaknesses below
(report only, none gating).

## Matrix at the pin

- Repository: harness (unbound Harness feature, reviewed in the repo holding it).
- Commit: `5c600680e7f46af124fa3281392fa7b25623e982` (the worktree's `feature.json` `review_sha`;
  the blob at the pin itself reads `"none"`, as a commit cannot carry its own SHA).
- Blob: `git show 5c600680…:.harness/harness.json` → `test_matrix.docs = {"always": []}`, no `when:`.
- Started tasks: T-01 only, `change_type: docs` (plan.yaml at the pin). No predicate exists to evaluate.
- Required kinds: **none**. Active kinds not required: `unit`, `integration`, `typecheck`. These were
  deliberately not run, and no `runs/r-20261127-1-validate-validator/qa/manifest-*.json` was written.
  Running an unrequired suite only to report `pass` is forbidden.
- Diff from merge base `cf7b422b2e55ae4c9129a8009e240b56c6e25035`: the five prose files plus the
  feature dir. No hook, gate, validator, schema, test or config file, so no added requirement is warranted.

## fail_first

Empty. The BRIEF at the pin marks each SC-01..SC-06 with exactly one `verify: inspection` line, so
there is no `verify: automated` SC. The BRIEF's `## Verification gaps` says so explicitly.

## Assurance: T-01 verify (not a matrix kind)

I ran it verbatim, extracted from plan.yaml at the pin, in the managed pin
(`pinned-checkout.py add … --persona harness-qa`, HEAD = 5c600680, clean,
`env -u HARNESS_AGENT_TYPE`). Result: `LAYOUT-SKILL-AGENTS-DEC-OK`, exit 0. Anchors were 25/0
failed, and test-gen-decisions-index.py passed 12/12. The pin was removed on return.

Positive injection: each guard was piped a known-bad string on stdin, where exit 0 means caught.
- size/grade `grep -Eqiw 'lines|size|grade|graded'` catches `max 400 lines`, `keep size small`,
  `grade B`, `graded at C` and `grade-bar`. The pinned LAYOUT.md is clean (exit 1).
- section/provenance `'^#{1,6} +A split|FEAT-|DEC-174'` catches `## A split`, `### A split`,
  `FEAT-69` and `DEC-174`. The pinned file is clean.
- language-neutral `'bin/|\.py|__init__|LAYOUT'` catches `bin/check`, `foo.py`, `__init__` and
  `LAYOUT.md`. The extracted Layout section is 17 lines, non-empty and clean.
- Section extractions are non-empty: Applying it 20 lines, Project map 12, Conventions 7, DEC-259 49.
- Scope check (last lines) is non-vacuous. At the pin it enumerated exactly the five files, and `want`
  is a fixed non-empty set, so an empty diff fails the equality.

### Findings (all T-01, severity low, non-gating)

1. **substance — delete-first guard is vacuous after commit.** `git diff --quiet HEAD -- …/delete-first.md`
   compares the tree with HEAD. At the pin, `git diff --quiet HEAD -- AGENTS.md` exits 0 even though
   AGENTS.md differs from base (`git diff --quiet cf7b422b HEAD -- AGENTS.md` exits 1).
   Failure scenario: a committed edit to delete-first.md passes this line. It is still caught,
   because the terminal scope check (base..tree) would print SCOPE DRIFT. The line is redundant, not
   load-bearing. delete-first is unchanged vs base (exit 0).
2. **substance — size/grade guard misses inflections.** `-w` does not match `sizes rot`,
   `line count 300` or `line-count`. Failure scenario: LAYOUT.md gains "sizes rot", the plan intent's
   own phrase, or "keep under a 300 line count", and the verify stays green, admitting the size rule
   SC-03 forbids. Inspection still covers it.
3. **form — "A split" heading guard is case-sensitive and needs a space.** `## A Split` and
   `##A split` escape. Failure scenario: a re-titled "A Split" section ships green.
4. **form — the "exactly once" check counts lines, not occurrences.** `grep -c` admits two LAYOUT.md
   paths on one line. At the pin the true count is 1 (`grep -o … | wc -l`).
5. **form — the DEC-259 extraction runs to EOF** (`awk '/^## DEC-259 — /{f=1} f'`). It holds only
   while DEC-259 is the last entry, which it is at the pin (line 8758). A later DEC-260 could supply
   the required tokens.
6. **proportionality — the language-neutral guard covers only the letter of SC-01** (`bin/`, `.py`,
   `__init__`). `.PY` and other-language paths escape. This is acceptable for a one-shot build check.

## Coverage gaps

None against the matrix. Phase 1 (BRIEF and plan only) expected no automated test: the change is
prose-only `docs`, and every criterion is inspection, graded by the reader lanes rather than QA.

## Principles applied

- harness-verification-rules (skill): I read the matrix from the pinned `harness.json` blob and
  reported `kinds: []` rather than running unrequired suites, so the floor came from config and not
  from convenience.
