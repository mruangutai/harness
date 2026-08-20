# Receipt — harness-backend-dev — distillation — FEAT-29-graphql-budget

## Inputs read
- Observations log (18 entries, T-01 through T-04 plus fix cycles) — read in full, my primary source.
- Receipts: T-01 (not separately quoted, referenced via observations), T-02-c1, T-03-c4, T-04
  (referenced via observations), sc05-c1 — read the four cited plus T-04's own observation entries.
- `harness-distill/SKILL.md` — read first per dispatch.
- Both Expertise files, in full, before writing (read-modify-write; DEC-125).

## Entry counts, before -> after

| File | Section | Before | After |
|---|---|---|---|
| craft (`.harness/expertise/harness-backend-dev.md`) | Patterns | 15/15 | 15/15 |
| craft | Gotchas | 15/15 | 15/15 |
| craft | Outcomes | 1/10 | 3/10 |
| craft | Open | 0/5 | 0/5 |
| craft | **file lines** | 109 | 119 (cap 150) |
| repository (`.harness/harness/expertise/harness-backend-dev.md`) | Patterns | 0/15 | 0/15 |
| repository | Gotchas | 1/15 | 2/15 |
| repository | Outcomes | 0/10 | 0/10 |
| repository | Open | 0/5 | 0/5 |
| repository | **file lines** | 12 | 16 (cap 40) |

Both sections at cap (Patterns, Gotchas in craft) took entries only by **displacement** — no net
growth in those two sections; new material entered by `replace` (rewriting an existing ID) or
`merge` (broadening an existing ID to absorb a related new idea), never plain `add`, per the caps.

## `expertise_update` — ops applied

```yaml
expertise_update:
  - op: replace
    target: P-01
    section: Patterns
    entry: "assert the exact expected value (never a weaker existence/type check) for an
      exception VALUE slot or numeric/sentinel field — a weaker check can pass under the same
      mutant that breaks the real contract"
    why: "broadened P-01 to absorb relayed candidate 1 (rc==1 vs `is not None` under the same
      mutant) without growing the section"
  - op: replace
    target: P-07
    section: Patterns
    entry: "predicted redness is required; an unpredicted redness is a FAIL unless it is a
      pre-existing check already coupled to the same path, verified not assumed"
    why: "own observation (T-03 second pass, SC-05 mutation): 5 checks reddened not 4, and the
      extra one was legitimately coupled, not a fix failure — nuances P-07's blanket rule"
  - op: replace
    target: P-10
    section: Patterns
    entry: "mutate the DATA a discriminator check depends on, not a GUARD shared by every caller,
      to scope mutation blast radius"
    why: "own observation (T-04 cycle 3): mutating the shared detection guard detonated ~30
      unrelated fixtures; mutating the marker/data list scoped it to exactly 2. Displaced the
      original P-10 (verify-grep section-scoping) as the weaker, narrower entry"
  - op: replace
    target: P-11
    section: Patterns
    entry: "a coverage-hole fix on already-correct production code is proven by mutation-testing
      the EXISTING code, not a RED/GREEN cycle on new production code"
    why: "own observation (T-03 fix cycle 3): the Iron Law governs production-code order and
      there was none to add for a test-only fix. Displaced the original P-11 (read-cited-line
      workflow tip) as narrower"
  - op: merge
    target: G-01
    section: Gotchas
    entry: "zero hits/zero red checks (coverage sweep OR mutation) is inconclusive, not proof of
      absence — a fixture may spell the condition differently, or an upstream contract may already
      foreclose the input shape"
    why: "own observation (T-02): a mutation to a defensive `or {}` guard produced zero red checks
      because the upstream function already normalized the input away — broadens G-01's existing
      coverage-sweep-only framing to the same principle under mutation testing"
  - op: replace
    target: G-07
    section: Gotchas
    entry: "only a clean, named-check FAIL across a mutation run is valid proof — a script that
      ABORTS instead proves nothing about the target check, report it separately, never as evidence"
    why: "relayed candidate 2 (sc05-c1): one mutation produced a clean FAIL in one script and a
      full abort in another; only the clean run counts. Displaced original G-07 (a narrow
      grep-startswith workaround) as weaker"
  - op: replace
    target: G-12
    section: Gotchas
    entry: "a dispatch/brief claim that an artifact is absent, or its framing of 'the gap', is a
      snapshot not a lock — verify against the live tree before acting, especially on a re-dispatch"
    why: "own observations (T-03 fix cycle 3 second dispatch: a stale absent-receipt claim
      collided with a concurrent sibling run; sc05-c1: the dispatcher's framing of the gap was
      stale relative to HEAD). Displaced original G-12 (marker-slicing) as narrower"
  - op: merge
    target: G-15
    section: Gotchas
    entry: "a test double's payload AND spare/second queued result must match the real wire shape
      AND real outcome class (success vs failure) — a spare failure can misroute a call down the
      wrong except branch, masking the check"
    why: "own observation (T-04 cycle 3): a spare failing Result routed the target call's error
      through a different except branch, producing a message that didn't contain the asserted
      headline, so only the sibling check reddened. Broadens existing G-15 (payload shape) to
      cover outcome class"
  - op: merge
    target: G-16
    section: Gotchas
    entry: "for a stated count or 'zero FAIL lines', re-run the count and confirm it rose by the
      expected delta — a silent zero-FAIL false green looks identical to a genuine pass otherwise"
    why: "broadened existing G-16 (re-run before writing) with relayed candidate 3 (check-count
      rose 32->35, not just a bare zero-FAIL claim) — same principle, sharper evidence"
  - op: add
    target: none
    section: Outcomes
    entry: "O-02: a complete, spec-like dispatch/intent is itself a red flag for the Iron Law —
      the more finished it reads, the stronger the pull to transcribe it into production code
      first. Write the test first regardless"
    why: "own observation (T-03): caught myself writing full production code before a test,
      triggered by a spec-like intent block, even with the Iron Law fully in context"
  - op: add
    target: none
    section: Outcomes
    entry: "O-03: a scope-changing amendment can retroactively resolve a prior open_question
      without anyone touching the file it named — re-check outstanding questions against the new
      scope before re-raising them"
    why: "own observation: a default-OFF amendment resolved a real-checkout-write open_question
      as a side effect of the scope change itself"
  - op: add
    target: none
    section: Gotchas
    layer: repository
    entry: "G-02: with HARNESS_GH_COST_LOG default-on, check whether
      factory_config.harness_root()'s CLAUDE_PROJECT_DIR fallback routes pre-existing
      unit/integration tests into the real .harness/logs/ when CLAUDE_PROJECT_DIR is unset"
    why: "own observation (T-03): reproduced twice live — two pre-existing test files wrote a
      real gh-cost-<date>.jsonl into the actual checkout, not a tmp root, because of this exact
      fallback. Repository-tier per the dispatch's own example of this checkout's specifics"
```

## Sourcing, counted separately

- From my own observations log: P-07 (refine), P-10, P-11, G-01 (merge), G-12, G-15 (merge), O-02,
  O-03, repository G-02 — **9 accepted entries**.
- From the lead's 3 relayed candidates: P-01 (merge), G-07, G-16 (merge) — **all 3 accepted**.

## Rejected candidates, with reason

1. **Own observation (T-04, repeated G-13 mistake live)** — rejected. The existing G-13 already
   states the rule; a single live repetition of a known gotcha is not a new rule, it is an
   instance. Adding it would violate the "no instance lists" guidance.
2. **Own observation (T-02, fixture isolation came "for free")** — rejected. Confirms the existing
   T-01-derived practice worked; no new rule, a success story not a WHEN/DO.
3. **Own observation (T-04 cycle 1-2, scoped standalone probe for shared-helper blast radius)** —
   rejected as a separate entry. Overlaps with the accepted P-10 (mutate data not guard); the
   scoped-probe workaround is the fallback for cases P-10's rule doesn't fully resolve, and adding
   both would be two entries about one root cause at a capped section.
4. **Own observation (T-03, self-inflicted P-04 case: read_lines() needed crash-proofing)** —
   rejected. Already covered by existing P-04 (wrap raising calls in try/except); this is an
   instance, not a new rule.
5. **Own observation (T-03 fix cycle 3, stale file-read tool signal contradicted by fresh hash)** —
   rejected. Reinforces existing P-09/G-13 (verify via hash, not tool signal); no new rule.
6. **Own observation (T-03 fix cycle 3, call-count assertion catches masking between two separate
   guards)** — rejected as a distinct entry. This is an instance of existing G-14's already-general
   "enumerate the matrix, name the untested cell" rule, discovered by applying it; not a new rule.

## `check-expertise.sh` results

- `.harness/expertise/harness-backend-dev.md`: **OK**. One pre-existing advisory (G-08 names
  `team-config` — flagged as a repository-layer candidate) predates this distillation and was not
  touched; left as-is, not a violation.
- `.harness/harness/expertise/harness-backend-dev.md`: **OK**.

## open_questions
None raised this cycle — no harness defect surfaced during distillation itself.
