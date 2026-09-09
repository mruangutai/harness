# Receipt — T-07 doc sweep + central-onboarding decision — harness-documentor

**T-07 is done and its verify block exits 0.** The documentation surface now describes onboarding as
fleet registration plus one product-resident file, and the model is recorded as **DEC-220**. One
pre-existing gate failure, not mine, is called out below and needs a decision above me.

## The new decision

**DEC-220 — Onboarding is fleet registration plus one product-resident file**, appended at EOF of
`.harness/harness/docs/DECISIONS.md` (now @6985). Number **computed from the file at HEAD**, not
assumed:

```
$ grep -n '^## DEC-' .harness/harness/docs/DECISIONS.md | tail -1
6952:## DEC-219 — Replace and drop are a second subcommand, `ops`, taking the contract's op objects as JSON
```

`main` and `origin/main` also top out at DEC-219, so 220 is free on the integration branch too
(P-02 check — a branch-local ceiling can lag). Body follows the file's four-part shape
(`Chose/Over/Because/Record`) and carries the ordering rule: the config lands *before* the fleet
entry, because the reverse has no symptom but an unattributed `FleetError`.

**Appending at EOF kept every existing `@line` anchor stable** — `check-decision-anchors.py` examined
33 anchors before and after, 0 failed.

## One anchor per file (for SC-04's reviewer)

Anchored on content, since line numbers shift (P-04):

| File | Anchor |
|---|---|
| `DECISIONS.md` | `## DEC-220 — Onboarding is fleet registration plus one product-resident file` @6985 |
| `DECISIONS-INDEX.md` | `- DEC-220 @6985 … :: The central onboarding model:` @220 — ruling hand-written, survives regeneration |
| `SPEC.md` | `**Onboarding a repository is three things, in order (DEC-220):**` @441; routing rows @145, @152; templates @457; interview step 3 @464 |
| `BUILD.md` | `Exactly one file is copied into the repository` @393; table row @389; five-entries claim @104; task 18 clause @784 |
| `org.html` | `/harness-init · control plane only` @286 |
| `README.md` | `lands its harness.json on its own default branch` @192 |
| `.harness/README.md` | `A fleet member gets no such directory` @8; owner rows @17–18; onboarding condition @83 |

## Verify — exits 0

The block ran **verbatim from the worktree root**, with the `gen-decisions-index.py --stdout | diff`
conjunct run *after* regeneration as the intent warns. `VERIFY EXIT: 0`.

Baseline before any edit was **exit 1**, and per-clause: the index-phrase, BUILD `default branch`,
both READMEs and `org.html` clauses all failed, and the three forbidden literals were all present.
So every clause reflects real work, not a pre-landed change (G-03).

Two clauses are *negative* greps on SPEC.md, so the mandated prose had to be written **around** the
struck literals rather than near them (P-06): row @145 reads "the repository is not onboarded — have
the user run", which does not match the forbidden `project not onboarded — tell the user to run`.

`git status --porcelain` names only my seven files plus
`.harness/harness/features/.../plan.yaml`, whose sole diff is the lead's `status: ready → building`
flip for T-07 — **present at dispatch, not mine**. The run dir is gitignored
(`.harness/features/*/runs/**`). `git diff --stat` on `org.html`: 1 insertion, 1 deletion, confined
to the one owner cell; class `owner o-you` and markup untouched.

## Pre-existing gate failure — NOT mine, needs a decision

`check-instruction-paths.py` **exits 1, and did so before I touched anything** — identical 4
violations, same files, same lines:

```
VIOLATION .claude/agents/harness-dev-ops.md:54,56: unanchored instruction path
VIOLATION .omp/agents/harness-dev-ops.md:55,57: unanchored instruction path
```

Committed at HEAD by **T-06 (`8a66cab2`)**; working-tree diff for both files is empty. They are
outside T-07's seven files, so I did not touch them. The acceptance criterion supposed my new prose
would introduce instruction paths — it cannot: the checker scans only `.omp/agents`,
`.claude/agents`, `.claude/skills` SKILLs, `references/` and `templates/`
(`check-instruction-paths.py:48-52`). **`docs/` and `README.md` are not scanned at all**, so none of
my seven files is in its scan set. This will fail the QA gate until someone with the grant fixes
those two lines.

## Three edits beyond the enumerated spots

Present-tense claims that DEC-220 falsifies, inside files I own; left standing they would contradict
the decision landing in the same commit (P-16):

- `SPEC.md` @441-452 — the paragraph said onboarding is "one edit" and "nothing is installed into
  it". Both false now; restated as the three things, naming the one file.
- `BUILD.md` @377 — "run **inside a target project**" → "in the control-plane clone".
- `BUILD.md` @104 — kept the five-entries claim, named the clone as its subject per intent 4a.

`SPEC.md` @424 "The harness is never copied into a product repository" was **left alone**: it is a
claim about the machinery and skills, still true, and @452 now names the one config file.

## Notes for the record

- The intent said "five settings entries"; BUILD carries **two different counts** — @104 "all five
  entries" (the 0a prerequisites) and @399 "six artifacts"/@401 "ALL SIX entries" (settings.json
  keys). Different subjects, both internally consistent, so I changed neither count.
- Task 18's shipped record (@784) was **amended by appended clause only**; its spec text is
  unrewritten, per intent 4c.
- Pre-migration `.harness/features/<FEAT>/` spellings in SPEC.md left as-is — layout drift, another
  feature's work, per the intent's scope discipline.
