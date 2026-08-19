# Distillation receipt — harness-backend-dev — run 2026-08-19-12-eng

## Base file confirmed

Read `.harness/expertise/harness-backend-dev.md` from disk before writing — byte-identical to the
injected `SubagentStart` block (both showed 15/15 Patterns, 9 Gotchas, 0 Outcomes, 0 Open, 83
lines). No truncation/wipe risk detected this run.

## Section counts — before / after

| Section | Before | After |
|---|---|---|
| Patterns | 15 (at cap) | 15 (at cap, 2 replaced) |
| Gotchas | 9 | 15 (at cap) |
| Outcomes | 0 | 0 |
| Open | 0 | 0 |

File: 83 → 103 lines (cap 150).

**Revised after an advisor pass, before this receipt was finalized**: the first draft under-shipped
two things the advisor caught and I verified against my own material — see the two added ops
below (G-14, G-15) and the open_question. Both are now reflected in the counts and the ops block
in this final version; nothing here is retracted, only added.

## Ops applied

```yaml
expertise_update:
  - op: replace
    target: P-04
    section: Patterns
    entry: "WHEN a test case's call could raise under a mutation DO wrap it in try/except and compare against a sentinel, never call it bare — an unguarded raise crashes the whole suite, silently skipping every later case, and the surviving output still looks like a clean partial pass."
    why: "Recurred at least 4 times this feature (T-01 c1 mutation 5, T-02 c1's advisor-caught fixture guards, T-02 c2's F-2/F-3 partial-suite-death findings, fix-c2's observation) — a more general, more evidenced lesson than P-04's single narrow review-gate-binding scenario, which fired once."
  - op: replace
    target: P-05
    section: Patterns
    entry: "WHEN a function mutates its argument in place and also returns it DO never assert `fixture == result` as the proof of correctness — compare against an independent, distinctively-valued oracle instead. Comparing the fixture to itself cannot redden for any implementation, including one that silently drops a required field."
    why: "My own T-02 c1 receipt: five `accepts` cases compared a mutated-in-place board to itself (x == x), unable to redden for any non-raising implementation including one dropping a required station key. General, reusable coding-shape gotcha; the old P-05 (finding phrased as gap not fix) is narrower and review-specific, single occurrence."
  - op: add
    section: Gotchas
    entry: "WHEN a fake HTTP double models a call by argv TEXT DO also assert its METHOD — list membership like `any(x in a for a in argv)` is blind to structure, so a correct call form and a broken one forcing the wrong verb can both satisfy it."
    why: "Own artifact (fix-c1's -f-vs-query-form fix, and the REUSE-angle receipt's Finding 1 on the two fake-gh doubles) — corroborates the lead-relayed run-7 candidate describing the identical mechanism."
  - op: add
    section: Gotchas
    entry: "WHEN an assertion searches a tool's stdout for a failure message DO first confirm which stream the tool actually writes it to — a check written against stdout is permanently blind to a message the tool writes to stderr, and its pass/fail is unrelated to what the tool actually does."
    why: "Lead-relayed candidate (mechanism 2 of 3), general and reusable; not independently measured by me this feature."
  - op: add
    section: Gotchas
    entry: "WHEN an assertion slices a string between two marker substrings DO confirm both markers exist in the target first — if neither is present, the slice is silently empty and any search or comparison run over it can vacuously pass without inspecting real content."
    why: "Lead-relayed candidate (mechanism 3 of 3), general and reusable; not independently measured by me this feature."
  - op: add
    section: Gotchas
    entry: "WHEN restoring a mutation probe mid-cycle, nothing committed yet, DO NOT use `git checkout -- <path>` as the restore step — it resets to HEAD, the pre-fix defect state, not the prior cycle's fix, and can silently revert still-live work. Restore by hand and re-verify the hash instead."
    why: "Own observations log + confirmed again in fix-c5 cycle 2 (git checkout -- would have reverted cycle-1's still-live fix to the pre-cycle-1 defect text); recurred twice this feature, general to any uncommitted mutation-testing workflow."
  - op: add
    section: Gotchas
    entry: "WHEN a contract states a negative invariant over two conditions (no fallback on remote failure AND a local copy present) DO enumerate the 2x2 and name the untested cell — two fixtures covering disjoint cells leave it untested, and the code fails open under a matching mutation."
    why: "Own artifact, this feature's single strongest finding (T-02 c2 receipt, F-5): two fixtures covered (remote fails / no checkout) and (remote succeeds / checkout present), leaving (remote fails / checkout present) untested — a fallback-on-failure mutation passed 78/78 against the module's own no-fallback docstring. This is exactly this codebase's named failure mode (fail-open) and was missing from my first draft; added after an advisor pass caught the gap."
  - op: add
    section: Gotchas
    entry: "WHEN a test double returns a payload DO shape it like the real wire response — encoding, line wrapping, envelope — not a synthetic clean value; a synthetic fixture leaves the decode path untested, so a real response differing in form ships as a live, unguarded defect."
    why: "Completes lead-relay candidate 1, which named TWO blind spots (HTTP method AND response shape); my first draft's G-10 kept only the method half across three word-count trims and silently dropped the shape half. Own artifact for the shape half: fix-c2's line-wrapped-base64 RED-then-GREEN fix (the fake double returned synthetic unwrapped base64; GitHub's real contents endpoint wraps it), plus fix-c2's own Q1 noting two more call sites still feeding synthetic-clean payloads."
```

## Candidates accepted / rejected, with source tags

1. **Lead-relay candidate 1** (fake-gh argv-text-not-method/shape, run-7 digest + fix cycle
   record) — **ACCEPTED IN FULL** as two new Gotchas, not one. `source: lead-relay`, corroborated
   by my own artifacts. The candidate names TWO blind spots — HTTP method AND response shape — and
   my first draft only kept the method half (fix-c1's Fix 1: the `-f`/query-string form bug and
   its tightened assertion; the REUSE-angle receipt's Finding 1 on the two fake-gh doubles). The
   response-shape half is separately RED-proven in fix-c2 (the fake double returned synthetic
   unwrapped base64; GitHub's real endpoint line-wraps it) — added as its own entry after an
   advisor pass caught the omission.

2. **Lead-relay candidate 2** (three unfalsifiable assertions, three mechanisms) — **partially
   accepted**. `source: lead-relay`, not independently measured by me this feature.
   - Mechanism 1 (fixture value equals the literal the implementation might hardcode) —
     **REJECTED as a new entry**: already covered by P-01 (pick a value absent from every
     compared fixed prose, reuse it). Adding it again would be a near-duplicate.
   - Mechanism 2 (stdout/stderr channel mismatch) — **ACCEPTED** as new Gotcha. General,
     reusable, distinct mechanism.
   - Mechanism 3 (slice markers absent, slice empty, search runs over nothing) — **ACCEPTED**
     as new Gotcha. General, reusable, distinct mechanism.

3. **My own T-02 c1 receipt** (five `accepts` cases were `x == x` because `validate_board`
   mutates its argument in place and returns it) — **ACCEPTED**, entered by replacing P-05.
   `source: own-artifact`. Self-caught before return, root cause fully diagnosed (mutate-in-place +
   no independent oracle), and the failure mode (a comparison that cannot redden for ANY
   non-raising implementation) generalizes cleanly to any function with the same shape in any
   repository.

4. **My own T-02 c2 receipt, F-5** (the fallback-on-failure coverage gap: two fixtures covering
   disjoint cells of a 2x2 left "remote fails AND checkout present" untested, so a fallback
   mutation passed 78/78 against the module's own no-fallback docstring) — **ACCEPTED**, entered
   as a new Gotcha. `source: own-artifact`. Not one of the three candidates named in the dispatch —
   surfaced by an advisor pass that checked my draft against the receipt material and found this,
   my own headline finding of the whole feature and this codebase's own named failure mode
   (fail-open), absent from the file. Confirmed against P-01..P-15/G-01..G-13 before adding: no
   existing entry covers condition-combination coverage, only value-distinctness (P-08) or
   value-collision (P-01) — genuinely new ground, not a near-duplicate.

## Rejected observations (not entered)

- **The orchestrator's commit landing ahead of the member's own return** (fix-c2 observation,
  confirmed again in a later run) — rejected as repository/process-specific to this harness's own
  commit-ownership model ("the pen is the orchestrator's"), not a craft lesson generalizable to an
  arbitrary repository. No repository-tier file exists here to hold it (`.harness/harness/expertise/`
  is absent, and this agent's `domain:` in `team-config.yaml` names no such path) — raised as Q1 in
  the DIGEST's `open_questions` instead of invented a home for it.
- **D-06 five-key-stations blast radius differing per tool** (claim vs. decompose vs. land) —
  rejected: narrates one migration's specifics rather than stating a durable rule; fails the "true
  in a repository never seen" test.
- **`validate=False` tripping the auto-mode Bash classifier** — rejected: describes this specific
  agent-harness's sandbox behavior, not a target-codebase fact or a general engineering rule.

## Layer

All accepted entries are craft (`.harness/expertise/harness-backend-dev.md`). No candidate this
run turned on a path, file, decision or invariant specific to exactly one repository, so nothing
was routed to a repository-tier file, and none was created (none exists here; the domain manifest
names no such path for this agent).

## `check-expertise.sh` — raw final output

```
OK   /Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-backend-dev.md
```

File is 103 of 150 lines. (Four word-count-cap round-trips were needed to fit G-14 under 50
words — recorded here because this eyeballing-vs-checker gap recurred four times in this same
session, consistent with the general lesson to run the checker before finalizing wording, not
after.)
