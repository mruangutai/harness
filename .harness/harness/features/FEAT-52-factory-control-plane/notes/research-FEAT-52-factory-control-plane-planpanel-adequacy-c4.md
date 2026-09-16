# Adequacy judgement — BRIEF SC-11 second half — FEAT-52, cycle 4

**Verdict: NOT a second instance of S1. SC-11's direction clause IS covered for S2 and S3; its
read-at-sha clause is covered NOWHERE, and that is a separate, lower-severity gap.** The lead's
framing (same shape as S1) does not survive reading T-02's rule set: S1's hole and SC-11's subject
are opposite directions, and only one of them is unenforced.

SC-11's second half asserts two things at once (BRIEF.md:163-165):
(a) S2 and S3 each separately show their feature-directory paths written under
`<HARNESS_FEATURE_TREE_ROOT>/`; (b) that is read via `git show <review_sha>:<path>`.

## (a) Direction — covered, and by a mechanism S1 does not touch

T-02 gives the checker two conjoined rules (plan.yaml:166-182): rule 1 flags any
`^\.(harness|claude|agents|omp)/` token in a span or fence **not** preceded by either anchor; rule 2
flags a span beginning `<HARNESS_CONTROL_PLANE_ROOT>/.harness/<seg>/features/`. For a
feature-directory path the two leave exactly one survivor — the feature-tree anchor. So a clean lint
run over a file **is** a per-file direction proof for every WRITE path in it.

S1's asymmetry is the mirror case: a control-plane READ wrongly anchored to the feature tree passes
rule 1 and is outside rule 2's `/features/` predicate. That direction has no rule. SC-11's second
half is about WRITEs. Different direction, different coverage.

Per-locus:

| locus | line | (a) asserts direction, or mere token presence? | (b) reads |
|---|---|---|---|
| T-04 verify, lint over 6 paths incl. S2 | plan.yaml:351 | direction, via rules 1+2 — but S2 is bundled in one invocation, not an isolated one | working tree |
| T-04 verify, python one-liner | plan.yaml:353 | token presence only — `'HARNESS_FEATURE_TREE_ROOT' in open(f).read()`, satisfied by the token anywhere in the file | working tree (`open`) |
| T-08 verify, lint over S3 alone | plan.yaml:595 | direction, and genuinely per-site — S3 is the sole argument | working tree |
| T-08 verify, python one-liner | plan.yaml:596 | token presence only — a `need` list of 6 literals; the receipt path itself is not among them | working tree (`open`) |
| T-12 verify, whole-scope run | plan.yaml:830-831 | direction, but scope-wide, not per-site | working tree |

The residual on (a) is narrow and not the lead's: no locus asserts the feature-directory path is
**present**. The lint is vacuously clean over a file from which the path was deleted, and the
presence one-liners check the placeholder token, not the path. T-08:596 is the closest and still
misses the receipt path.

## (b) Read at the reviewed sha — no carrier at all

`git show`, `git -C` and `git cat-file` appear **zero** times in plan.yaml (grepped whole file).
`review_sha` appears three times, all prose: D-06's rationale (plan.yaml:67), T-04's intent
(plan.yaml:365), T-11's intent (plan.yaml:804). Every check above reads the working tree; T-12's
intent says so in as many words (plan.yaml:864). A working-tree read passes for a deliverable that
was never committed — which is precisely what SC-11 wrote `git show` to exclude. SC-04 carries the
identical clause (BRIEF.md:117-118) and is already the S1 finding's second half, so one remedy
serves both.

## What this is worth

Not a `high`, and not a new panel finding — no reader raised it, and inventing reader provenance
would corrupt the record the operator signs. It is one adequacy item for the batched review, under
pm attribution: **SC-11's and SC-04's `git show <review_sha>:<path>` clause is unimplementable as
the plan stands, in every task, and SC-11 will therefore grade `partial` at goal-check even on a
perfect build.**

## Open questions for the operator's batched review

- Q1 (non-blocking, same fork as digest Q2): close (b) by adding `git show <review_sha>:<path> |`
  to the per-site assertions, or narrow SC-04/SC-11 to a working-tree read and record the weakening.
  Either is a plan change; neither is a fix a pre-signature dispatch may make (DEC-176).
- Q2 (non-blocking): give S2 and S3 a positive-control assertion that their feature-directory path
  exists, so the lint's silence over a deleted path cannot read as proof.
