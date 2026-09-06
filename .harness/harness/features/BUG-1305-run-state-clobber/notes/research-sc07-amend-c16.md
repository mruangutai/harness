# SC-07 amendment — cycle 16, product lane

**BLUF.** Both Advisor-worded replacements are applied verbatim to SC-07 in
`.harness/harness/features/BUG-1305-run-state-clobber/BRIEF.md`, and nothing else in the file
changed. Diff is 10 insertions / 3 deletions in one file, confined to two hunks entirely inside
SC-07: the tail of the `The note also records` paragraph, and the final clause of the
`**It FAILS if any of these holds:**` sentence. The six-pair enumeration, every other criterion,
and `## Approval` are byte-untouched. No code, tests, notes, plan.yaml or STATE.md were touched;
nothing was staged or committed.

Verbatim check is mechanical, not eyeballed: both mandated strings were compared to the file with
whitespace collapsed (`re.sub(r"\s+"," ")`) — the only latitude the dispatch granted — and both
matched (`A True`, `B True`). No dash, quote or backtick substitution.

## Verification results, as measured

**1. `git diff --stat -- BRIEF.md`**

```
 .../harness/features/BUG-1305-run-state-clobber/BRIEF.md    | 13 ++++++++++---
 1 file changed, 10 insertions(+), 3 deletions(-)
```

Consistent with two sentence replacements re-wrapped at ~95 columns (2 lines -> 5, 1 line -> 5);
not a paragraph reflow.

**2. `git diff -- BRIEF.md`** — two hunks, both inside SC-07:

- `@@ -378,8 +378,11 @@` — removes the two lines `the one newly refused write this feature
  knowingly introduces — an owner that rewrites its / checkpoint and drops \`run_uid\` — with the
  test that pins its message.` and adds the five-line two-class replacement.
- `@@ -387,7 +390,11 @@` — removes `that a write permitted at \`c369fb1f\` is now refused other
  than the disclosed dropped-\`run_uid\` one.` and adds the five-line two-disclosed-classes
  replacement ending `\`state.yaml\`, \`digest.md\`, and the handoff note.`

Context lines confirm the six-pair enumeration (`the sixth pair, the witness guard's route
denials …`, `so the denial is scoped to the one filename …`), the `**It FAILS if any of these
holds:**` opening clauses, `verify: inspection` and SC-08 are unchanged. No hunk touches
`## Approval`.

**3. Amended SC-07 — quoted whole** (`BRIEF.md:357-398` at working tree):

```markdown
- **SC-07 (Modes A and B — no protection traded away, and none newly invented):** Graded in two
  directions against `notes/regression-delta-BUG-1305.md`, the artifact the regression task produces.
  **Direction one — nothing removed.** Every refusal asserted by the harness `unit` and `integration`
  suites at `c369fb1f` is still asserted at the pinned review sha, and every assertion removed,
  weakened, or changed in its expected exit code, message or route is enumerated and justified under
  that note's `## Removed or altered assertions` heading. Compared by reading
  `git show c369fb1f:<path>` against `git show REVIEW_SHA:<path>` for every test file under
  `tests/unit/` and `tests/integration/` that this feature touched.
  **Direction two — nothing newly refused.** Each refusing or reporting branch this feature adds is
  paired in that note, under the heading `## Newly refused writes`, with the write it must still
  permit, and the grader COMPARES that note's six named pairs against the suite at the review sha:
  the legacy directory — prior and incoming both carrying no `run_uid` — still accepting an
  equal-run_id update; the resumed owner, carrying its own checkpoint's `run_uid` from a different
  session, still exiting 0, together with BOTH recovering-owner cases of SC-01(d) exiting 0; the
  lead's own-run digest append repair still exiting 0; `check-state.sh` exiting 0 over a fixture
  tree of legacy run directories that carry checkpoints and no witness at all; and the fifth pair,
  T-05's new fail-closed `return 2` in `validate-digest.py`, still exiting 0 over a run directory
  whose `digest.md` exists and is compliant and over the no-root-resolves case that fails open; and
  the sixth pair, the witness guard's route denials in `bash-write-guard.sh` and `check-domain.sh`,
  still permitting — in the same run directory — a Write of `state.yaml` and a Write of `digest.md`
  at exit 0, and leaving a Bash write to an unrelated ordinary file in that directory unaffected,
  so the denial is scoped to the one filename rather than to the directory.
  The note also records
  `check-state.sh`'s exit code and findings over this repository's own `.harness` tree, and states
  the two newly refused write classes this feature knowingly introduces — an owner that rewrites
  its checkpoint and drops `run_uid`; and an Edit of a governed `state.yaml`, `digest.md`, or
  handoff note whose complete candidate cannot be reconstructed from the tool payload (unmatched
  `old_string`, ambiguous `old_string` without `replace_all`, or a path-only payload — ordered by
  the Advisor at cycle 13 in service of SC-01(a)) — each with the test that pins its message.
  **It FAILS if any of these holds:** an assertion present at `c369fb1f` is absent or weakened at the
  review sha and is not enumerated under the first heading; any one of the six permitted-write cases
  is absent from the suite at the review sha or is asserted to exit non-zero; `check-state.sh`
  reports a run directory whose checkpoint and witness agree, or reports any directory carrying no
  witness; either heading is
  absent; the `## Suite results` heading is absent, or records a non-zero exit or any FAIL line for
  either suite; or the note's BLUF states that a refusal holding at `c369fb1f` no longer holds, or
  that a write permitted at `c369fb1f` is now refused other than the two disclosed classes — the
  dropped-`run_uid` checkpoint rewrite, and the reconstruction-`None` Edit of a governed artifact;
  the latter disclosure FAILS in turn if the suite at the review sha does not assert an exit-0
  permit for a uniquely reconstructable, content-valid Edit of each governed class it refuses:
  `state.yaml`, `digest.md`, and the handoff note.
  verify: inspection
```

**4. `git status --porcelain`** — verbatim, taken with the edit in place (this note not yet
written at that point):

```
 M .harness/harness/features/BUG-1305-run-state-clobber/BRIEF.md
 M .harness/harness/features/BUG-1305-run-state-clobber/feature.json
 M tests/integration/test-check-domain.py
```

`test-check-domain.py` is the main session's concurrent DEC-174 work — not mine, not reverted.
`feature.json` is harness run bookkeeping written by the orchestrator, not by me.
`notes/regression-delta-BUG-1305.md` did not appear as modified at the time of measurement; the
main session's edit to it had not landed yet. Nothing staged, nothing committed, HEAD unmoved.

## What the amendment changes downstream

The regression note's `## Newly refused writes` disclosure must now name TWO classes, and the
second carries its own cost: the suite at the review sha must assert an exit-0 permit for a
uniquely reconstructable, content-valid Edit of EACH governed class — `state.yaml`, `digest.md`,
and the handoff note (three permits). A note disclosing the reconstruction-`None` class without
those three permits now FAILS SC-07 on the new clause. That is the load-bearing consequence for
whoever writes or grades the note next.

## Open questions

None blocking. Advisory: SC-07 now presupposes three permit assertions exist in the suite at the
review sha; if they do not, the correct route is a qa/eng fix cycle, not a further amendment.
