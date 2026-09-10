# Answers — FEAT-58-corpus-outside-worktree — operator review, cycle 5

One batched pass. Answer the questions in the order below rather than by number: **Q6 first, because
it dissolves Q1.**

## Q6 — STRIKE the hardlink half. SC-15, N-11 PART 4 and PART 5 (a)(b) come out.

This is scope you added on your own ruling, and you were right to flag it for striking rather than
bury it. Strike it.

The reasoning, which is not about cost:

- **A hardlink alias is not the mistake class the guard exists to stop.** The write guard earns its
  place against fumbles — the typo that wrote to `/Users/…/GitHum/x` (#1635) is the realistic shape.
  Creating a hardlink to a corpus file and writing through it is deliberate evasion by an agent that
  already holds Bash, and the Bash route has its own guard.
- **Path-based guards are defeated by hardlinks universally.** Nothing about that is specific to the
  corpus. Fixing it inside FEAT-58 puts a general weakness at the wrong altitude and implies the
  rest of the guard surface is hardlink-safe, which it is not.
- **Decisively: the remedy's own failure mode is the defect it was added to prevent.** VL-01 shows
  the scan fail-opening on exactly the class SC-15 exists to close. A control whose failure mode is
  the harm is worse than no control, because it also buys false confidence.

D-2 is still delivered: a governed write to a path under the corpus symlink is refused, and that is
the requirement. Record the strike with this reasoning so it is not re-proposed, and file the
hardlink-alias weakness as its own ticket against the guard surface generally — not against this
feature.

## Q1 — VL-01 — DISSOLVED by Q6, not remedied

No fifth `test-corpus-denials.py` case, no error conversion, no `_hardlink_plan` change. The code the
finding is against no longer exists in the plan.

For the record, both premises check out and I verified them rather than taking them on the panel's
word: `check-domain.sh:14` states verbatim *"Only exit 2 blocks — exit 1 is a NON-blocking error and
the write proceeds"*, so a bare `raise` in that file is a fail-open. That is a genuine finding and
the panel was right to raise it at high. It is being removed rather than fixed because the whole
half is coming out.

## Q2 — VL-02 — APPLY the named remedy, with one addition: the skip is ANNOUNCED, never silent

`.github/workflows/tests.yml:50` is `actions/checkout@v4` with no `fetch-depth`, verified — a depth-1
shallow clone. Extend SELF-SCOPE to skip when `git cat-file -e` fails for either endpoint.

Two conditions, and the first is the point:

- **The skip prints its reason and names the endpoint that could not resolve.** A check that
  silently does not run in the environment where it is most likely to be relied upon is the
  fail-open pattern this entire feature exists to remove. Skipping is acceptable; skipping quietly
  is not.
- **The authoritative run is recorded once, locally, in a full clone**, as the nothing-altered
  evidence. That check is a one-time whole-feature assertion, not a per-PR gate, so its natural home
  was never CI.

Rejected alternative, recorded so it is not revisited: setting `fetch-depth: 0` on the `integration`
job. It would make the clauses resolvable, but it changes the CI runner's behaviour to suit a check —
and SC-12 asserts the runner is unchanged. Bending the thing you are measuring to fit the
measurement is the wrong direction.

Good catch on the severity reconciliation. One reader flagged its premise unverified, the lead
verified it and moved severity **upward** — a shallow-clone default reddening every PR in the
repository, `enforce_admins` true, including this feature's own. That is the panel working, and both
upward reconciliations being recorded by name with reasons is what makes them trustworthy.

## Q3 — VL-03 — APPLY the named remedy

Strike the `# corpus-scope: owner-root` marker from N-06 PART 2, and quantify **both** N-12
assertions over DETECTED sites only.

Same unmeetable-census shape as GC-01, which was just fixed — a criterion quantifying over a
population that the detector cannot see is unmeetable by construction, and it reds with no
authorised fix. Never quantify over a marked set when a detected set is available; the marker is
bookkeeping that has to be maintained by hand and will drift the first time someone adds a site.

## Q4 — F-10..F-13 / VL-05..VL-08 — FOLD ALL FOUR into the same fix pass

No deferrals by name, and **no acceptance recorded in `approval.rulings` for VL-08.** Fix it. If the
fix is genuinely unavailable rather than merely awkward, come back with that specific reason and I
will rule then — I am not signing a blanket acceptance of a finding I have not seen stated.

Recording them as honestly still open rather than quietly closing them was correct.

## Q5 — VL-07 — the DoD sentence is WRONG and I am amending it. The guard is right.

The guard's `_ID_RE` scope is correct: it no-ops on any basename that is not a feature id, so `qa-*`
probe trees are untouched. My sentence in the DoD note — *"A QA probe worktree now gets stripped
automatically without QA knowing"* — was wrong, and it was wrong in the direction that matters,
because it claimed coverage the design does not deliver.

Amended in the note at source, with the reason: **a disposable probe tree should carry a faithful
full checkout.** A perturbation proof runs against the tree as it really is; stripping it would make
the probe measure something other than the thing being probed. So the scope guard is not a gap, it
is correct behaviour, and the note now says so.

What survives from that paragraph is the part that was never about QA: `post-checkout` fires
whoever creates the worktree, so the mechanism does not depend on anyone following a rule. The claim
about probe trees specifically is withdrawn.

No residual to record in D-10 or N-02 — there is no residual once the sentence is right.

## Q7 — VL-09 — ORDER a post-fix goal-check. The panel's source verification is not a substitute.

Run it. Different lens, different question: the panel checks whether findings are answered in the
artifact; the goal-check asks whether the plan still serves the operator's stated intent. Source
verification that two remedies landed does not answer the second.

**On the error itself:** you told the panel the goal-check had been re-run and was clean when the fix
had landed after the grade. Recording it unsoftened, in the same digest, rather than quietly
ordering another run, is the behaviour I want — it changed what I would have been signing. Noted and
closed; no further account needed.

## Not in scope, restated because the run keeps finding them

Nothing filed as a harness defect is to be fixed inside FEAT-58: #1595, #1596, #1597, #1598, #1630,
#1631, #1635, #1636, #1637, plus the hardlink-alias weakness from Q6 once filed.

## What happens next

Apply Q2, Q3, Q4 and Q6, re-run the goal-check per Q7, re-run the panel on the artifact that will
actually go to signature, and present again.

Expect the task and criteria counts to **fall** — Q6 removes a criterion and two task parts, and Q1
adds nothing. Coverage may not regress except where Q6 removes it deliberately. The ledger stands at
42 rows; report the new figure and account for every removal by name.

Two things I noted and am not asking you to change. The on-demand index at **0.0023 s** rather than
the 1.2 s my own question assumed — that is the second time a measurement has corrected an
assumption of mine in this feature, and it is why the plan asks for measurements rather than
estimates. And ruling the scan-site **class** in at nine sites rather than the four I named was
right: I gave class-based reasoning, and excluding two sites the plan can now see would have made the
census red on day one, which is exactly what Q2's answer rejected.

The signature is mine and has not been given.
