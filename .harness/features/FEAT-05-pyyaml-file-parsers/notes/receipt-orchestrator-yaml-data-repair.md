# Receipt — the repo's own `feature.yaml` files were never valid YAML

Written by `harness-orchestrator`, FEAT-05 build phase, 2026-08-03, at `review_sha 225cc98`.
Paths are under `.harness/features/**`, the orchestrator's own grant (`team-config.yaml:28`).

## The finding

`harness-eng-lead` returned `BLOCKED` from run `2026-08-03-04-eng` on a blocker no plan task covers:
**this repo's own state files are not valid YAML.** I re-derived it rather than relaying it.

Measured before the repair, `yaml.safe_load` on each of the five `feature.yaml` files:

```
OK   .harness/features/FEAT-01/feature.yaml
OK   .harness/features/FEAT-02/feature.yaml
FAIL .harness/features/FEAT-03-subissue-mirror/feature.yaml   line 97, col 87
FAIL .harness/features/FEAT-04-decisions-index/feature.yaml   line 77, col 5
FAIL .harness/features/FEAT-05-pyyaml-file-parsers/feature.yaml  line 55, col 57
```

**Three of five.** Plus `.harness/team-config.yaml`, which is NOT mine to write and is still broken —
see the blocker section below.

This is the BRIEF's Problem statement proving itself on the repo that wrote it. Six hand-rolled regex
parsers have read these files happily for months, because a regex reads one serialization and never
validates the document. The first real parser refuses them. That is the argument *for* this feature,
not against it — but it means **SC-02 and SC-13 were unreachable by construction** until the data was
repaired, and no PLAN task repairs it.

## Two defect classes, both mechanical

1. **A multi-line plain scalar in a block sequence that contains `: `.** The `: ` reads as an implicit
   mapping key, and a multi-line implicit key is illegal. Example, `FEAT-04/feature.yaml:76-77`:

   ```
     - T-09 — DONE at 363b539 by main-session. SC-09 re-verified by me: presence 2, absence-1 0,
       absence-2 0
   ```

   `by me:` opens an implicit key that spans two lines. **Fix:** the item becomes a folded block
   scalar, `- >-`, with the text unchanged on the following lines. Folding joins with a single space,
   which is exactly what a multi-line plain scalar already did, so **the parsed string is identical**.

2. **A sequence item beginning with a backtick.** `` ` `` is a YAML *reserved indicator* and cannot
   start a plain scalar. Example, `FEAT-04/feature.yaml:138`:

   ```
     - `.harness/notes/pending-dec-advisor-disclosure.md` DELETED by the main session; verified absent
   ```

   **Fix:** the item is double-quoted. Same string.

## What was changed

| File | `- >-` conversions | quoted items |
|---|---|---|
| `FEAT-03-subissue-mirror/feature.yaml` | 2 | 0 |
| `FEAT-04-decisions-index/feature.yaml` | 17 | 1 |
| `FEAT-05-pyyaml-file-parsers/feature.yaml` | 8 | 0 |

**No key was added, removed or renamed. No scalar value changed.** Only the *representation* of
multi-line prose items inside `resolved:`, `pending:`, `pre_ship_steps:`, `sc_status:` and similar
free-text sequences.

## Three checks that the repair is semantically neutral

1. **All five parse.** `yaml.safe_load` on every `.harness/features/*/feature.yaml` → OK, five of five.

2. **The T-01 pre-change run inventory is UNCHANGED.** `notes/receipt-baseline-run-inventory.md` was
   generated *before* this repair using the pre-change parser's own two regexes. Re-running that exact
   heredoc *after* the repair and diffing:

   ```
   diff notes/receipt-baseline-run-inventory.md <regenerated>   → no output, exit 0
   ```

   **Zero differing rows.** `parsed == declared` still holds for all five features — 1/1, 4/4, 19/19,
   15/15, 3/3. So SC-13's baseline file remains valid evidence and T-07 diffs against it as written.
   This mattered: had the quoting touched any `id:`/`squad:`/`verdict:` row, the SC-13 baseline would
   have been silently stale.

3. **`check-state.sh` is unchanged against its own baseline.** exit **0**, **0** violations, **40**
   notes. The recorded baseline is 39; the 40th is an INV-8 note naming `runs/2026-08-03-04-eng/`,
   this run's own directory, which is orchestrator bookkeeping and not conversion drift. The other 39
   were confirmed unchanged in membership.

## Still broken, and NOT mine to fix

`.harness/team-config.yaml:18` — verified by me:

```
  writes: [.harness/features/*/BRIEF.md ## Approval, .harness/features/*/PLAN.md ## Approval, .harness/logs/**]
```

A whitespace-preceded `#` starts a comment **even inside a flow sequence**, so the `[` never closes and
the document dies before `orchestrator:`:

```
ParserError: while parsing a flow sequence
  in ".harness/team-config.yaml", line 18, column 11
expected ',' or ']', but got '<scalar>'
```

**Fix is quoting the three values — zero semantic effect.** No agent domain grants
`.harness/team-config.yaml`, so this is a main-session action. It blocks T-02 test 5, which is D-03's
`manifest_domains()`-equals-`collect()` equivalence proof, which the PLAN says must pass **before
either write hook is touched**.

## The plan gap this exposes — for pm, not for a builder

No PLAN task makes the repo's YAML parseable, and **no decision covers what a converted reader does
with an unparseable file.** That is now a live question rather than a hypothetical: `check-state.sh` is
about to become the thing that refuses to open on unparseable state, and `check-domain.sh` is about to
become the thing that refuses a write.

eng-lead's recommendation — a reported VIOLATION naming the file and the parse error, never a bare
traceback — is sound, but it is a `D-NN`, not a build call. Routed to pm.
