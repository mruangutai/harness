# Receipt — the verified `team-config.yaml:18` fix, and D-03's equivalence proven ahead of it

Written by `harness-orchestrator`, FEAT-05 build phase, 2026-08-03, at `review_sha 225cc98`.

`.harness/team-config.yaml` is **MAIN-SESSION's file** and I have not touched it. This receipt exists so
the main session applies a form that is already proven safe rather than one that is merely plausible —
the lead's stated concern was that quoting the line changes raw text the two hooks currently line-scan,
and that a wrong edit wedges every agent write mid-build. That concern is answerable with measurement,
so I measured it.

## The exact line to apply

Line 18, currently:

```
  writes: [.harness/features/*/BRIEF.md ## Approval, .harness/features/*/PLAN.md ## Approval, .harness/logs/**]
```

Replace with — one line, three double-quoted elements, nothing else changed:

```
  writes: [".harness/features/*/BRIEF.md ## Approval", ".harness/features/*/PLAN.md ## Approval", ".harness/logs/**"]
```

## Five checks, all run against a candidate copy, none against the live file

1. **It parses, and the values are the intended three.** `yaml.safe_load` on the candidate returns

   ```
   main_session.writes = ['.harness/features/*/BRIEF.md ## Approval',
                          '.harness/features/*/PLAN.md ## Approval',
                          '.harness/logs/**']
   ```

   The `## Approval` suffixes survive intact — they were the thing being eaten as a comment, and they
   are load-bearing (they are how the manifest says main-session writes *a section*, not a whole file).
   All nine top-level keys are now reachable: `schema_version`, `cli_min_version`, `main_session`,
   `orchestrator`, `paths`, `universal_rules`, `shared`, `teams`, `leads`. Before the fix the document
   died at line 23, so **everything from `orchestrator:` onward was unreachable** — which is why one
   quoting error on a `main_session` line took out the entire manifest.

2. **The lead's wedge concern does not apply to this line, and I checked rather than reasoned.**
   `grep -n 'main_session' check-domain.sh bash-write-guard.sh` returns **nothing**. Neither hook reads
   the `main_session:` block at all — `collect()` keys off `name:` entries and the `shared:` marker, and
   `main_session` has neither. So line 18 is not on either hook's scan path.

3. **The pre-change line-scan sees an identical manifest before and after.** 16 `name:` entries, 16
   `path:` entries, 16 `read: true` entries — **identical**, both files.

4. **Both hook suites still pass on the unchanged live manifest**, establishing the baseline the fix must
   not move: `test-check-domain.py` **11/11**, `test-bash-write-guard.py` **30/30**.

5. **D-03's equivalence is PROVEN — the test that is currently red will go green.** This is the
   substantive result. T-02 test 5 asserts `manifest_domains()` equals the pre-change `collect()`. I ran
   the comparison directly, extracting `collect()`'s logic verbatim from `check-domain.sh:107-125`:

   - **OLD** `collect()` against the **ORIGINAL** (unquoted) file, versus
   - **NEW** `harness_yaml.manifest_domains()` against the **CANDIDATE** (quoted) file,
   - for **every** `name:` in the manifest — **19 agent names**.

   Result: **0 mismatches.** Both `mine` and `shared` match set-for-set for all 19. Every returned glob
   satisfies `isinstance(g, str)` (D-08's coercion holding).

   So there is **no residual design risk in D-03**. The one red test in the tree is red for exactly one
   reason — an unparseable manifest — and the moment line 18 is quoted it passes. The main session is not
   applying a speculative fix and then hoping; the outcome is already measured.

## Why this line broke, in one sentence worth keeping

A whitespace-preceded `#` opens a comment **even inside a `[...]` flow sequence**, so the `[` never
closes, and PyYAML reports the failure at the *next* structural token — five lines later, at
`orchestrator:` on line 23. The error location is nowhere near the defect. That is the general shape of
this whole class, and it is why six regex readers never noticed: they never had to close the bracket.

## The gate the corpus now needs — my recommendation, the user's call

The lead is right that a repair alone is insufficient. **Four files were invalid and one of them,
`FEAT-05/feature.yaml`, was written today** — so this is live, ongoing production of invalid YAML by
agents, not historical debt. Without a gate the next run reintroduces it.

**Recommendation:** the cheapest sufficient gate is a new `test-*.py` under
`.claude/skills/harness/bin/` that walks every `.harness/**/*.yaml` and asserts each one
`safe_load`s — inside the existing `unit` runner, so it is already covered by the gate the plan uses,
and it needs no new mechanism, no hook, and no `harness.json` change. It also self-hosts the feature's
own thesis: the corpus is validated by a real parser or the suite goes red.

That is a **new task and plausibly a BRIEF amendment**, and this feature is already at 2.0x budget. It
is not mine to add to a signed plan — routed to pm, and to the user.
