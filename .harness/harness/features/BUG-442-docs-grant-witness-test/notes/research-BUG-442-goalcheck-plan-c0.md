# Goal-check — BUG-442 drafted plan vs the operator's stated intent (c0)

**Does this plan deliver the operator's stated intent?**

**yes** — all three clauses of the acceptance sentence have a named owner, and every literal T-01
puts in the doer's hands was checked against the real manifest and is correct.

Graded against `notes/intake-BUG-442.md` (issue #442 + the verbatim acceptance sentence). BRIEF.md was
read as evidence only. Nothing on disk changed but this note.

## A. Coverage — VERDICT: complete, no unowned clause

| acceptance clause | owner | evidence |
|---|---|---|
| (a) load through the repointable `MANIFEST_PATH`, not hand-copied literals | REQ-01, SC-01, T-01 §3 | T-01 §3 calls the helper on module-level `MANIFEST_PATH`; `test-harness-yaml.py:29-32` is the override chain, `:32` the only consumer |
| (b) exhaustive over all 16 personas | REQ-04, SC-02, T-01 §1 `DOCS_GRANT_CENSUS` + §3a | per-persona assert mandated, "never one aggregate comparison … never a count" (plan.yaml:98-100) |
| (b) future **addition** on any persona is caught | REQ-02, SC-03, T-01 M1 | M1 measured below |
| (b) future **removal** is caught | REQ-03, SC-04, T-01 M2 | M2 measured below |
| the intake's shrinking-domain trap (intake:73-83) | REQ-04, SC-05, D-01, T-01 M3 | M3 measured below |

A 17th persona arriving with a docs grant is also caught — as census drift by §3a, not silently.

## B. T-01's literals — VERDICT: all four claims hold, verified not assumed

Ran T-01's *specified* helper verbatim against `.harness/team-config.yaml` (walk + `hy.manifest_domains`,
docs by exact slash-segment):

- **Census.** Walk yields **16** names; symmetric difference against T-01's typed 16-name list is
  `set()` — exact match. Sources: `orchestrator:` `name:` at `team-config.yaml:41`, 12 `members[]`
  names (`:103,125,139,168,180,194,207,220,244,267,278,289`), 3 `leads[]` (`:303,312,321`). The three
  `lead: { name: … }` refs (`:93,159,242`) dedupe into `leads:`. Every `name:` key in the file holds a
  `harness-*` persona; `team-name:` is a different key, so the walk collects no team names.
- **`EXPECTED_DOCS_GRANTS`.** Both halves true. Measured docs-grant map is exactly
  `{'harness-documentor': ['.harness/*/docs/**', 'docs/**']}` — the two globs at `:143-144`, and no
  other persona holds a docs-segment path (`docs` appears elsewhere only in prose comments `:141`,
  `:147`). The `{ path: ".", read: true }` rows do not surface: `harness_yaml.py:408` filters on
  `not entry.get("read")`, and `"."` carries no `docs` segment either way.
- **M1's insertion point.** Holds. `      - name: harness-qa` is `:244` (6 spaces); the first
  `        domain:` after it is `:248` (8 spaces); qa's entries are at **10 spaces** (`:249`), exactly
  as T-01 states. Inserting the 10-space row after `:248` parses and yields
  `harness-qa -> ['docs/**']`.
- **M3's premise.** Holds. `- name: harness-ui-reviewer` occurs **once** in the file (`:289`);
  `:294-297` mention the persona only inside path values, never after `name:`. The replace is
  non-vacuous and the walk drops to **15**. M3 is not vacuous.

## C. Proportionality — VERDICT: right-sized

One file, one task, three decisions for a one-file additive test change. The bulk of T-01 is D-03's
in-suite mutation controls, and they are load-bearing, not padding: the grant is correct today, so a
witness written without them can never be observed to fail — the exact defect #442 names. The three
mutants map 1:1 onto SC-03/04/05, so there is nothing to drop. No production change, no second task,
`harness_yaml.py` and the manifest explicitly read-only.

## D. Verifiability — VERDICT: every SC can report RED; SC-07 is legitimate

Measured on the pre-change tree (subprocess with `HARNESS_PROJECT_DIR` at a temp root holding a
mutated manifest):

- clean copy → `rc=0`, 22 `ok`, 0 `FAIL`. D-03's anti-false-red leg holds; repointing perturbs
  nothing else, confirming the orchestrator's `REPO_ROOT`-feeds-only-`MANIFEST_PATH` fact
  (`:29-32`, sole consumer `:32`).
- **M1 → `rc=0` today.** The bug, reproduced: a docs grant on qa lands green. Only the new witness
  can catch it.
- **M2 → `rc=1` today**, but via `FAIL test_manifest_domains_matches_the_regex_walk_on_the_real_manifest`.
  So a returncode-only assertion for SC-04 would have been non-discriminating — passing on the
  pre-change tree. T-01 (plan.yaml:128-130) already requires the *witness's own* `FAIL` line, which
  is what makes SC-04 falsifiable. Correct as drafted.
- Output shapes match `main()` (`test-harness-yaml.py:892-904`): `ok   <name>` (three spaces),
  `FAIL <name>: <msg>`, `sys.exit(1)` — so T-01's substring assertions and the four `^ok   …$` greps
  in `verify:` all match real output. Suite wall time 0.15s, so the 4-invocation `verify:` is far
  inside 60s.
- **SC-07 is legitimate.** `<review_sha>` is a placeholder resolved when review pins it; the base
  `6d969ed3` exists (`git cat-file -t` → `commit`). A criterion graded later at a SHA that will
  exist, not an ungradeable one. Both clauses are artifact-readable, which is what `inspection`
  grades.
- `integration` has a live runner and `tests/integration/**` matches the changed file.

## E. The admitted residual — VERDICT: admitting it is the right call

BRIEF.md:80-84 concedes the census walk and the grant lookup share one loader, so a parser bug hiding
a *newly added* persona hides it from both. This leaves **no** acceptance clause unmet: the sentence
is about a docs grant being added to or removed from a persona, and both are caught; a loader that
hides a persona is a `harness_yaml.py` defect, and production changes there are excluded by the
intake (intake:91). Closing it would need a second, parser-independent reading — which is a new
witness for a different subject, i.e. scope the operator did not ask for. Stated in the BRIEF where
the user signs, which is the correct disposition.

## Advisory (non-blocking, no gate)

- `verify:` hard-codes the absolute worktree path four times (plan.yaml:41-44). Consequence: anyone
  re-running that literal string after the worktree is removed gets `No such file or directory` — a
  red for a path reason, not a code reason. Harmless at build time (qa runs inside the worktree);
  worth knowing before the string is quoted anywhere else.

## Open questions

None blocking. Approval remains pending; nothing here needs the operator before the plan panel reads it.
