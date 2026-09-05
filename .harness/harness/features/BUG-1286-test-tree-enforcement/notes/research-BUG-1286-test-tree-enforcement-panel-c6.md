# Cycle-6 plan-panel digest — verbatim durable copy

Source: `runs/2026-09-04-20-validator/digest.md` (gitignored). Copied here unchanged so the record
survives. This file is the transcription source for plan.yaml's cycle-6 `panel:` mapping.

Path note: the dispatch named `notes/review-plan-panel-c6.md`; `check-domain.sh` denies `review-*`
to harness-pm (it is the validator lead's path), so this copy lives under pm's own
`notes/research-<FEAT>-*.md` grant, as the cycle-4 transcription note did.

---

```yaml
VERDICT: FAIL
DIGEST:
  headline: Both readers independently defeated case 11's new partition rule at the same root cause - it decides EXCUSED and synthesises representatives lexically, segment-wise, while the repository's only mechanical detect consumer matches full paths with fnmatch where * crosses / - so the panel FAILS with one high finding that returns to the operator; everything else probed (one-fence identity, amendment collateral, traceability, DAG, 85/9/0) held under independent re-measurement.
  team: plan-panel
  steps_run: 2
  cycles_used: 0
  members:
    - { step: should-not-exist, persona: fable-advisor, verdict: PASS, headline: "Case 11 pins segment-wise glob semantics the repo's own fnmatch consumer does not use; keep the runtime-derived assertion, but its partition and its excused-cardinality pin both need work", files_touched: [] }
    - { step: scope, persona: harness-code-reviewer, verdict: FAIL, headline: "Case 11's literal-prefix check does not normalize .., so tests/../evil/** substituted for tests/unit/** stays GREEN end to end; two lower findings; all other probes clean", files_touched: [".harness/harness/features/BUG-1286-test-tree-enforcement/notes/review-harness-code-reviewer-planpanel-c6.md"] }
  severity_max: high
  must_fix: [
    "F-01 (scope, high): case 11's EXCUSED test is an unnormalized lexical prefix compare, so a directory-only detect glob whose text begins tests/ but escapes the tree is excused rather than rogue. Remedy: normalize the literal prefix and reject any .. component before the tests/ comparison.",
    "F-02 (should-not-exist, med): case 11's partition and its final-segment-only synthesis assume wildcards do not cross /, but code_grade._is_test_path matches detect with fnmatch over full relative paths. Remedy: state the governing matcher semantics in D-01/REQ-09/SC-19 and assert no unit.detect glob carries a wildcard in a non-final segment."
  ]
  files_touched: [".harness/harness/features/BUG-1286-test-tree-enforcement/notes/review-harness-code-reviewer-planpanel-c6.md", ".harness/harness/features/BUG-1286-test-tree-enforcement/runs/2026-09-04-20-validator/state.yaml", ".harness/harness/features/BUG-1286-test-tree-enforcement/runs/2026-09-04-20-validator/digest.md"]
  branch: none
  open_questions:
    - { id: Q1, question: "Which matcher semantics does REQ-09's word 'counts' denote? The only mechanical consumer of test_kinds.unit.detect is code_grade._is_test_path (code_grade.py:466-471), fnmatch over the full relative path, where * crosses /. Under it today's unmutated **/test_*.py already counts any file under a tracked test_*-named directory outside tests/ (basename innocent, so the guard structurally cannot refuse it), which falsifies REQ-09's absolute wording while SC-19 stays green. Narrowing a signed requirement, or accepting the residual, is the operator's - not pm's and not this panel's.", blocking: true }
    - { id: Q2, question: "F-01 is rated high by scope. The lead assessed its MECHANISM as real and reproduced (the prefix compare is genuinely unnormalized) but its STATED consequence as not reproducible today: tests/../evil/** matches no git-tracked path under fnmatch, and should-not-exist independently traced the same escape and called it vacuous. Both ratings are carried unreassigned. The operator decides whether the high rating stands as a latent-defect rating or is discharged by the normalization edit; no agent may accept a high finding's risk.", blocking: true }
  escalations: []
  expertise_update: []
  sc_status: []
  adequacy_notes:
    - "Neither reader could grade SC-02 (test-first red proof) or SC-12/SC-13 (graded at review_sha). They are ungradable at plan phase by construction, not gaps the panel missed, and no review_sha can be pinned before the Building-to-Review seam."
    - "Both readers produced falsification evidence, so neither clean result is a shallow pass: between them they traced eleven distinct unit.detect mutants mechanically through the rule as written and recorded RED or GREEN for each, re-derived today's four globs from the live harness.json and templates/harness.json, and re-measured the census to TOTAL 85 / OUTSIDE 9 / VIOLATIONS 0 independently."
    - "The panel graded TEXT. Nothing here is evidence about code; no code exists. Every GREEN or RED reported is a trace of the specified algorithm, not an execution of it."
    - "The lead verified the decisive fact itself rather than adjudicating between the readers on their word: grep over bin/ and hooks/ returns exactly one path-matching consumer of test_kinds.*.detect (code_grade._is_test_path; code-grade.py and validate-digest.py both route through the same classify()). If a future consumer normalizes or shell-expands detect, F-01's dismissed consequence becomes live - the dismissal is contingent on that census, not permanent."
    - "No reader could establish whether a tracked test_*-named DIRECTORY outside tests/ will ever exist; both measured zero today. F-02 is therefore latent, and its severity reflects a hole that opens on someone else's future commit."
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1286-test-tree-enforcement/.harness/harness/features/BUG-1286-test-tree-enforcement/runs/2026-09-04-20-validator/digest.md
```

# plan-panel cycle 6 — BUG-1286-test-tree-enforcement

**Not PASS. One high finding is present and returns to the operator; no agent may accept its risk.**
`severity_max: high`, `must_fix` non-empty → the panel gate FAILS. The remedies are plan-text edits
inside pm's authority except the one requirement question at Q1, which is the operator's.

Tip graded: committed plan-phase artifacts at `a185a41c` plus the uncommitted amendment on top.
No `review_sha`; none can be pinned at plan phase.

## Readers

| reader | persona | status |
|---|---|---|
| `should-not-exist` | `fable-advisor` | **ran** — returned a valid single-key `findings` block first pass, no `on_fail` |
| `scope` | `harness-code-reviewer` | **ran** — note at `notes/review-harness-code-reviewer-planpanel-c6.md` |

Neither reader was skipped. Both returns parsed on the first attempt, so `cycles_used: 0`.

## Surviving findings — reader's own severity, never reassigned

Ranked by what has to happen next, not by severity alone. F-01 and F-02 are ONE root cause with two
symptoms and must be fixed in one edit; fixing either alone leaves the other open.

**F-01 · high · `scope`** — *Case 11's literal-prefix check does not normalize `..`, so a clean
one-for-one substitution stays GREEN.* Substituting `tests/../evil/**` for `tests/unit/**` in both
`.harness/harness.json` and `templates/harness.json` traces as: segments `["tests","..","evil","**"]`
→ first wildcard segment `**` → literal prefix `tests/../evil` → `.startswith("tests/")` is True →
**EXCUSED**. Rogue set empty, excused count still 1, all three basename globs still synthesise and
pass. GREEN end to end. Consequence: a directory-only glob rooted outside `tests/**` passes the very
assertion GAP-1's fix was written to prevent. Scope also raises a symlink variant of the same
unnormalized compare.

**F-02 · med · `should-not-exist`** — *Case 11 assumes segment-wise glob semantics; the repository's
only mechanical `detect` matcher does not use them.* `code_grade._is_test_path`
(`code_grade.py:466-471`) is `fnmatch.fnmatch(relative, pattern)` over the **full relative path**,
where `*` crosses `/`. Adding `**/fixtures/*/test_*.py` classifies BASENAME (final segment
`test_*.py`, `strip("*?")` non-empty), synthesises `.harness/tools/fixtures/*/test_x.py` because
substitution touches the final segment only, and `is_test_shaped` accepts it → **GREEN** — while
under `fnmatch` that glob counts `.harness/fixtures/a/test_env/run.py`, whose basename the guard can
never refuse. No mutation is even required: today's own `**/test_*.py` `fnmatch`-matches
`.harness/tools/test_data/gen.py`, so REQ-09's absolute wording is already falsified while SC-19
stays green. Latent — zero such tracked files today.

**F-03 · med · `scope`** and **F-04 · low · `should-not-exist`** — *the same defect, two ratings,
both carried.* The "exactly one of today's globs is EXCUSED" side-assertion is a hardcoded
cardinality — a partial literal copy of the value the case elsewhere forbids copying. A legitimate
future `tests/`-rooted directory glob (`tests/e2e/**`, or folding `tests/integration/**` in) takes
the count to 2 and reddens the case with no invariant broken, and the paragraph's remedy text covers
only the rogue and not-test-shaped firings while a blanket *"NEVER to delete, narrow or skip this
assertion"* sits beside it. That is the trained-to-delete channel this amendment exists to close,
reopened through the side-assertion. `should-not-exist` supplies the cheaper reformulation: assert
the BASENAME bucket is non-empty, which serves the stated purpose and pins no cardinality.

**F-05 · low · `scope`** and **F-06 · low · `should-not-exist`** — *the same defect, both at low.*
SC-12 quotes `note carries {n} fenced blocks, expected exactly 1` as refusing **both** the zero-block
and the two-or-more case, but T-03 specifies a distinct zero message, `note carries no fenced block:
{path}`. SC-12 is `verify: inspection`, so an inspector taking the quoted string literally sees a
correct implementation emit a string SC-12 never names — a review-time dispute manufactured by the
spec. `should-not-exist` adds a secondary nit: *"Exit 2 is reserved for this refusal"* is
over-claimed, since argparse exits 2 on its own usage errors; no gate branches on the distinction.

**F-07 · info · `should-not-exist`** — keep verdict on case 11 and on the runtime-derived assertion
itself. The maintenance surface earns its weight: the snapshot alternative it replaced already
decayed once, and that decay was the cycle-4 med.

## Cross-references

- **F-01 + F-02 are one root cause.** Case 11 decides EXCUSED and synthesises representatives by
  pure lexical, segment-wise string work; the consumer matches full paths with `fnmatch`. Under
  `fnmatch`, F-02 is the live-capable symptom and F-01 is inert; under any normalizing or
  shell-expanding consumer, F-01 becomes live. Both readers reached the same rule from opposite
  ends without seeing each other's work.
- **F-03 + F-04**: one defect, two readers, med and low. Not averaged; both stand.
- **F-05 + F-06**: one defect, two readers, both low. The panel's only fully-agreed finding.

## Assessed and dismissed, with reasons

- **F-01's stated consequence — "makes qa's kind map count every file under `evil/`" — dismissed as
  stated, by lead measurement.** `grep` over `bin/` and `hooks/` returns exactly one consumer that
  matches `test_kinds.*.detect` against paths: `code_grade._is_test_path`, `fnmatch` over the full
  relative path (`code-grade.py` and `validate-digest.py` both route through the same `classify()`).
  Git-tracked paths never carry `..` and nothing normalizes the pattern, so `tests/../evil/**`
  matches nothing. `should-not-exist` traced the identical escape (`tests/../docs/**`) and
  independently called it *"GREEN but vacuous"*. **The finding's mechanism stands and its severity is
  scope's and is not reassigned** — the plan should not ship a prefix test that is wrong on its face.
- **The symlink variant — dismissed on the same evidence.** Git records a symlink as a blob, so no
  tracked path carries a `tests/<link>/` prefix and `fnmatch` compares literally.
- **`harness.json` moved or renamed as a wrong-reason RED — dismissed by both readers
  independently.** It crashes the pre-existing `repo_cfg` load that six existing assertions already
  depend on, so the cause is unambiguous and is inherited infrastructure risk, not new to case 11.
- **Eight further mutants traced RED for the right reason, so not findings**: `**/fixtures/*/x_test.py`
  (no final-segment wildcard → directory-only, empty prefix → ROGUE); `**/*.{test,spec}.*` and
  `**/*_[ts]est.*` (braces and classes survive `strip("*?")`; representatives not test-shaped);
  `**/test_*`, `**/*test*.*`, `**/?test?.py` (the fixed `x` token cannot forge `_test.`, `.test.` or
  a source extension); `detect` empty and `detect` `"|"` (empty prefix → ROGUE); `detect` absent
  (KeyError naming the key — loud).

## Falsification evidence — why the clean results are credible

Anchors re-measured live and all matching: `test-suite-layout.py:100-103`, `:104-105`, `:136-139`;
`suite-census.py:24` is exactly the find-all fence pattern T-03 describes; `run-unit-tests.sh:47` is
the single `run_pool.py --mutation-check "$BIN_DIR"` SC-15 cites; `suite_layout.py:20-33` is the two
existing clauses. Census independently re-measured: TOTAL 85 / OUTSIDE 9 / VIOLATIONS 0, dispositions
1 documented exception (`.ts`) + 8 probe records (7 `.md`, 1 `.jsonl`). Amendment collateral intact:
case 11 plants no file by its own text, so SC-06's one-element exact-equality list is untouched, and
`test_rogue.py` collides with neither agnostic shape. REQ-01..REQ-09 each traced by at least one
task; no orphan REQ, no phantom trace; REQ-09's only grader is SC-19. `depends_on` is a real
topological order. Verify non-vacuity checked: T-03/T-04 invoke a `tree-audit` subcommand that does
not exist today (only `verdict-lines`, `migration`, `residue`, `children` are registered), so both
fail non-vacuously; T-05's stated precondition reproduces at 0 hits. T-03's `--against` combination
rule is total — fence-count ≠ 1 → exit 2 unconditionally, else row-difference or violation → 1, else
0 — and exit 2 is reachable and distinguishable from exit 1.

## Fix order

1. **Answer Q1 first** — it decides both remedies' shape.
2. **One edit to T-01 case 11 + SC-19**: normalize the literal prefix and reject any `..` component
   before the `tests/` compare (F-01); assert no `unit.detect` glob carries a wildcard in a
   non-final segment, and name the governing matcher semantics in D-01/REQ-09 (F-02); replace the
   excused-cardinality pin with a BASENAME-bucket-non-empty assertion and give the remaining firing
   modes a sanctioned remedy sentence (F-03/F-04). All three live in the same paragraph.
3. **SC-12**: quote both of T-03's messages, or say "refused by name per T-03's two messages"
   (F-05/F-06). Independent and trivial.

Off-the-table items were respected: no reader re-argued D-05, D-01's two-group vocabulary, the
closed cycle-3/cycle-4 findings, or the two engineering-tier rejections. `scope` checked D-05's
*description* against the live consumer file for a new inaccuracy and found none.
