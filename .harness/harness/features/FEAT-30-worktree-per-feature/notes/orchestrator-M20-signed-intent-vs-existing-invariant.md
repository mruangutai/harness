# M-20. T-01 cannot be implemented as SIGNED without failing an existing invariant test. This needs a ruling.

Found by me independently, by running the integration suite after T-08's registration landed — not
reported up by the run. **This is the most consequential finding of the build phase and it is
blocking**, because T-08's own `verify:` greps for `^FAIL ` and will not pass while it stands.

## The failure

    .claude/skills/harness/bin/run-unit-tests.sh --kind integration
      -> exit 1, scriptPASS=15, scriptFAIL=1
    FAIL test_exactly_one_guarded_import_in_the_tree: unexpected guarded-import file(s)
         outside the allowed set: {'feature-worktree.py'}
    FAIL test-harness-yaml.py

Re-derived the set myself rather than trusting the message:

    guarded_hits : check-domain.sh, feature-worktree.py, feature_schema.py, harness_yaml.py
    allowed      : check-domain.sh, feature_schema.py, harness_yaml.py
    offending    : feature-worktree.py     <- exactly one, and it is T-01's

## Neither side is at fault, which is what makes it a ruling and not a fix

**The member built exactly what the signed plan told it to.** `plan.yaml` T-01 `intent:`, lines 37-39:

> Read the segment string `.claude/worktrees` from `harness_boundary.WORKTREES_SEGMENT` rather than
> spelling it again; **import `harness_boundary` lazily and, if the import fails, exit 2 with a
> message naming the module.**

Delivered at `feature-worktree.py:47-53` — lazy import, `except ImportError`, a message naming the
module, `sys.exit(2)`. Line for line the instruction.

**The test is also right, and it is not a nuisance rule.** `test-harness-yaml.py:309-374` caps the
guarded-import pattern: *"one guarded import per required dependency, each living in the module whose
job IS that dependency's policy."* Its assertion 1 keeps D-12's yaml rule at exact `==` strength;
assertion 2 is the general cap, deliberately a subset (`<=`) so it can admit new legitimate cases.

## Why I cannot resolve it myself

Both available remedies cross a line that is not mine:

| Remedy | Why it is blocked |
|---|---|
| Change `feature-worktree.py` so it holds no guarded import | **Contradicts T-01's signed intent.** An unguarded import exits 1 with a traceback, not `exit 2` with a message naming the module. The intent specifies the exit code and the message. |
| Widen `allowed` in `test-harness-yaml.py` to include `feature-worktree.py` | **Edits a file no task declares.** `test-harness-yaml.py` is in no `files:` list in this plan. DEC-179 makes literal `files:` the routing basis, and an undeclared edit riding a cluster commit is precisely the lineage hole nothing in this repo reconciles. |

An execution-time adjustment is mine; changing what the plan's diff contains is not.

## My recommendation, if the operator wants one

**Widen the `allowed` set.** One line, and it is the better-grounded side:

- **Precedent already covers a first-party guarded import.** `check-domain.sh` sits in `allowed`
  for guarding `import feature_schema` — first-party, exactly like `harness_boundary`. So
  "`harness_boundary` is not an external dependency" does not distinguish this case from an
  already-accepted one. I checked: `check-domain.sh` does currently hold the needle, so the test's
  own comment claiming it holds zero occurrences is itself stale.
- **The test was built to grow this way.** Its comment states assertion 2 *"MUST be a subset (`<=`),
  never `==`"* so new legitimate cases can land without the cap being lost.
- **It costs nothing that matters.** Assertion 1 — the signed D-12 yaml rule — is untouched and keeps
  its exact `==` form, because `feature-worktree.py` imports no yaml.
- The alternative rewrites a signed instruction to satisfy a textual proxy.

**A third option exists and I recommend against it:** satisfy the intent via
`importlib.util.find_spec` plus an explicit `exit 2`, which honours the rule's purpose (no silent
fallback) while not matching its `except ImportError` needle, and touches only T-01's own declared
file. It is in scope and it would go green. I advise against it because it contorts working code to
evade a lint rather than deciding whether the rule should admit this case — and it leaves the next
person to rediscover the same question.

## Status

Reported, not acted on. The build run is still live at T-08; if its member resolves this by editing
`test-harness-yaml.py`, that edit is **undeclared** and I will catch it when I stage by explicit
pathspec — it does not enter a commit without a ruling.

## New fact, measured after the note was written: NOTHING tests the guarded branch

I checked whether the `exit 2` the intent mandates is actually asserted anywhere.
`test-feature-worktree.py` contains exactly one `returncode == 2` assertion, at `:492`, and it is for
an **undeclared `--repo`** (`case_undeclared_repo`), not for a failed `harness_boundary` import.
Grepping the suite for `harness_boundary` finds only fixture uses of `WORKTREES_SEGMENT` at `:33`,
`:162`, `:172`, `:181`.

**So the guarded branch is required by the intent's letter and asserted by nothing.** It is also
unreachable in practice: `harness_boundary` is a sibling module in the same `bin/` directory as the
CLI.

This shifts the balance between the two remedies, and I am revising the recommendation accordingly:

- **Option B (remove the guard from `feature-worktree.py`) breaks NO test**, touches only T-01's own
  declared file, and is therefore fully in plan scope. Its only cost is departing from the intent's
  literal wording. An unguarded `ImportError` still names the module — in a traceback — but exits 1
  rather than 2.
- **Option A (widen `allowed` in `test-harness-yaml.py`)** remains better-grounded on the merits and
  is precedented, but it edits a file no task declares.

**Revised recommendation: Option A on the merits, Option B if the operator wants this closed without
touching an undeclared file.** Both need a ruling because both alter something signed — A alters the
plan's effective diff, B alters what a signed intent mandates. Neither is an execution-time
adjustment, which is the whole reason this is a note and not a fix dispatch.

The one thing I would NOT do is treat exit 2 as load-bearing without evidence. If the operator judges
the clean exit worth keeping, Option A is the answer; if the wording was incidental, Option B costs
less. That judgement is the actual question, and it is one line either way.

## One ruling closes it completely — verified, nothing else is hiding

Ran `test-harness-yaml.py` alone from the repository root: **exit 1 with exactly ONE failing
assertion** and 18 `ok` lines.

    FAIL test_exactly_one_guarded_import_in_the_tree: unexpected guarded-import file(s)
         outside the allowed set: {'feature-worktree.py'}

No second failure sits behind it, so whichever remedy the operator picks restores the suite to green
in one line. `--kind unit` is exit 0 and unaffected throughout.

## Corroborated independently by the run itself

T-08 returned `verdict: FAIL` with the note *"registrations correct, integration PASS 90 to 198;
verify red on out-of-scope test-harness-yaml.py"* — the same conclusion I reached by measurement,
arrived at separately. **And the run did NOT make the undeclared edit**: the tree outside the feature
directory holds only `run-unit-tests.sh` and `harness.json` modified, plus the four new files. The
squad correctly refused to fix a file the plan does not give it.

That is the right behaviour and worth recording as such: the cheap wrong move was available and was
not taken.

## Consequence for the phase

T-10's `verify:` ends with both `run-unit-tests.sh --kind unit` and `--kind integration` gated on
exit 0, so **T-10 will FAIL for this same inherited reason regardless of its own quality.** T-10 must
therefore be graded on its own merits — its red proof and its concurrency assertions — separately
from the inherited redness.

And because `gates.qa_gate` is **blocking** and the matrix cannot pass with a red integration suite,
this also means: no qa gate pass, no simplify, and **no commit** until the ruling. The work stays in
the tree.

## T-10 graded on its OWN merits — independently measured by me, and it is strong

Because T-10's `verify:` gates on both suites being green, it will FAIL for the inherited reason
above no matter how good it is. So I measured its substance separately, running its suite myself
while no member process was active:

    python3 .claude/skills/harness/bin/test-feature-worktree.py
    exit=0   PASS=89   FAIL=0

    PASS  SC-01b case A: all four concurrent committers succeed against their own worktree
    PASS  SC-01b case A: all six pairwise write windows genuinely overlapped under contention
    PASS  SC-01b case A: assert_commit_isolation holds across four concurrently-committed worktrees
    PASS  SC-01b case A: no branch outside the four expected ones advanced (repoA main, repoB master unchanged)
    PASS  SC-01b case A: FEAT-90 working directory is clean after concurrent commits
    PASS  SC-01b case A: FEAT-90 HEAD still names its own branch after concurrent commits
    PASS  SC-01b case B: the successful committers' write windows genuinely overlapped
    PASS  SC-01b case B: the shared-checkout collision was detected

Why this is criterion-faithful rather than merely green:

- **Six** pairwise overlaps is exactly C(4,2) — per pair, not an aggregate, which is what SC-01b's
  *"asserts their write windows actually overlapped"* requires. A serialised fixture cannot pass it.
- The *"NO other branch advancing"* clause is asserted explicitly, naming `repoA main` and
  `repoB master`.
- The fixture uses TWO repositories with deliberately DIFFERENT default branches (`main` and
  `master`), so a hard-coded default branch would be caught.
- The predicate asserts per tree: exact five-sha ordering since base, plus for every OTHER tree both
  a foreign-file check and `merge-base --is-ancestor` for foreign shas — the latter catching a foreign
  commit even if its file were later deleted.
- Case B's detection is real, not assumed.

**What I could NOT verify:** the neutered red proof. Every red proof in this plan begins by copying
`bin/` to a temp directory, and the write guard blocks the orchestrator's `cp` there as out-of-domain.
That half rests on the member's reported output, which is exactly why the dispatch demanded the actual
command text.

**Conclusion: T-10's FAIL is inherited, not earned.** Its own deliverable is the strongest evidence
in this build.

## A SECOND plan-text defect, same root cause: T-10's `verify:` is unrunnable as written

T-10's member disclosed a required deviation, and I verified its premise independently by
inspection.

**The defect.** T-10's signed `verify:` copies a single file:

    cp .claude/skills/harness/bin/test-feature-worktree.py "$T/t.py"

But `test-feature-worktree.py:35` is a bare top-level `import harness_boundary`, and the file
contains **no** `sys.path` manipulation at all (grepped: zero hits). So a single-file copy cannot
import its sibling and dies with `ModuleNotFoundError` at import time, **before any assertion runs,
with zero neutering involved.** The verify is broken on the pristine file.

**The member's fix was the right one and it was disclosed, not silent.** It re-expressed the copy
step as `cp -R` of the whole `bin/` directory — which is exactly what T-06's `verify:` already does
for a materially identical red-proof shape — and changed nothing the verify *asserts*: the signature
lookup, the neutering, the RC check, the marker grep and the three trailing commands are untouched.
Matching an already-working sibling pattern rather than inventing one is the correct instinct.

**Why this matters beyond this run:** `plan.yaml`'s recorded `verify:` for T-10 still contains the
broken single-file copy. Anyone who re-verifies T-10 literally — a reviewer, a successor
orchestrator, CI — gets a spurious failure that looks like a T-10 defect and is not. **It needs a
one-line correction in the plan (`cp -R` the directory), which is pm's edit, not mine.**

## Both plan-text defects trace to ONE decision

This is the coherent finding underneath both:

- **T-01 imports a sibling module, `harness_boundary`.** That was required by its intent (do not
  spell the segment twice) and it is good design.
- Consequence 1: the *guarded* form of that import trips `test-harness-yaml.py`'s anti-fallback cap
  (M-20 above).
- Consequence 2: the *sibling* nature of that import breaks any red proof that copies one file
  instead of the directory (this section).

Neither consequence was anticipated when the plan was signed, and neither is a builder error. One
design choice, two collisions with existing machinery — which is the honest characterisation to put
in front of the operator, rather than two unrelated incidents.

## Q2 from the build digest is SETTLED — the lead could not run the check, I could

The lead reported an unsettled contradiction: `cp -R .claude/skills/harness/bin "$T/bin"` — the FIRST
LINE of T-02's, T-03's, T-04's, T-05's and T-06's verify blocks — was green for one spawn and denied
for another, and it holds no shell so it could not discriminate. I hit the same denial myself, so
here is the answer with four consistent data points.

**Both halves of the puzzle are true.**

1. The guard really does NOT expand shell variables. When it denied me it printed the literal
   `cp targets $T/bin, outside your domain` — it read the unexpanded `$T/bin` as a repository-relative
   path, which is out of domain. That part of the lead's hypothesis is correct.
2. But that check is never REACHED by some callers, and that is what explains the contradiction.
   `bash-write-guard.sh:49-57`, in order:

       agent = d.get("agent_type") or ""
       if not agent:                     sys.exit(0)     # no agent_type at all
       if agent == "harness-dev-ops":    sys.exit(0)     # the DEC-85 exemption

**The four data points, all consistent:**

| Who ran it | agent_type | Outcome | Why |
|---|---|---|---|
| T-02's spawn | `harness-dev-ops` | green | exempt at `:56-57` |
| T-06's spawn | `harness-backend-dev` | DENIED | not exempt, reaches the unexpanded-path check |
| me | `harness-orchestrator` | DENIED | same |
| the operator | none (main session) | green | exits at `:50-52` |

So the discriminator is **WHO ran it, not WHAT was run.** The lead's two observations were both
accurate reports of different personas.

**The consequence that matters, and it is reassuring:** T-03, T-04 and T-05 are the operator's, run
from the main session, which carries **no `agent_type`** and therefore exits at `:50-52` before any
path check. **Those three verify blocks will run literally as written, with no re-expression needed.**
The denial is an agent-lane artifact and does not reach layer 0.

It also means Q4's concern is narrower than stated: T-06's re-expression was forced by the guard's
non-expansion for a non-exempt persona, not by anything wrong with the plan's text.
