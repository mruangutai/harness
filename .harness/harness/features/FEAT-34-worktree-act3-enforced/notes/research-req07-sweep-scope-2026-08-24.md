# REQ-07 sweep scope — shape 3: genuinely undecided at plan time

**BLUF.** REQ-07 neither reaches nor excludes served repositories. The brief says so in its own
words, and no signed decision has closed the question since. This is **shape 3**: it needs a new
operator-signed `D-11`, drafted below. My recommendation inside that draft is **harness-checkout-only
for this feature** — leave it, record it, ship — because the cross-repository sweep is not a
one-word change and INV-29 still refuses. `D-01`'s recorded `because` is **partly false as written**
and needs one clause corrected; that correction is separate from, and independent of, the unsigned
Amendment 3 / SC-16 item.

## The requirement text, quoted

`BRIEF.md:73-74` — **REQ-07**:
> When a merge lands the default branch locally and a feature it carries reads `Done`, that
> feature's worktree is removed without anyone running a command.

No repository quantifier. Compare `BRIEF.md:62-63` — **REQ-04**:
> The refusal covers **every** repository's worktrees under `WORKTREES_SEGMENT`, with no
> per-repository exception to remember or later remove.

REQ-04 quantifies over repositories explicitly and REQ-07 does not. That contrast is deliberate,
and the brief states it outright at `BRIEF.md:236-239` (Q1, the operator's, non-blocking):
> Whether the harness and a fleet repository share one mechanism or need two is undecided, and
> REQ-07 through REQ-09 are written to be satisfied by either.

That sentence settles the interpretation question. REQ-07's repository scope is **open by design**,
so no reading of it can be called the defect.

## Why the scope was never closed afterwards

- `D-08` says it "resolves the brief's Q1" — but only Q1's *directory* half (where the tracked hooks
  directory lives). The "one mechanism or two, for a fleet repository" half is untouched.
- `D-10` created `classify_all` for REQ-04 and edited T-01, T-02, T-03, T-05, T-06, T-07.
  **T-04 is absent** (`notes/research-plan-fix-req04.md:84-91`). Nobody weighed the sweep's
  repository dimension; it was inherited, not chosen.

## Why the fix is not `classify` → `classify_all`, and this bounds severity

Three measured obstacles, all beyond the one-word swap:

1. **The trigger does not exist in a served repo.** The shim resolves its root from its own file
   location (`.claude/skills/harness/hooks/post-merge:20-21`), and harness-init states the harness
   is not copied into a product repository (`harness-init/SKILL.md:8`). Measured: no
   `.claude/skills/harness/hooks` directory exists under any checkout in
   `/Users/molchairuangutai/GitHub/harness-factories/`. A merge landing in kaya-ai fires no harness
   hook at all. Cross-repo removal would only ever happen opportunistically, on the next *harness*
   merge.
2. **The landed feature directory would not resolve.** `post-merge-sweep.sh:163` builds
   `main_checkout_root/.harness/<repo_segment>/features/<id>`. Measured: the harness checkout's
   `.harness/` holds `harness/` and `factory/` only — no `kaya-ai/`; kaya-ai's features live in
   kaya-ai's own checkout. Every served-repo record would hit the `:164` SKIP path.
3. **`gh-sync.py ship` (D-03) would need pointing at the other repository's state store**, which
   `_handle_record` has no parameter for.

So the qa finding, taken literally, would be a green-looking swap that changes no behaviour. The
`med` ranking is right; I would not raise it.

## Does `D-01`'s rationale still stand as written? No — one clause is false.

`plan.yaml:88` records:
> Sweeping all makes the hook compute the SAME predicate as INV-29, so the hook and the invariant
> can never disagree about what is eligible.

Since `D-10`, `check-state.sh:1237` calls `classify_all` and `post-merge-sweep.sh:234` calls
`classify`. They **do** disagree, on the repository dimension. The clause was true when signed and
is now partly falsified by a later signed decision. D-01's other two grounds — post-merge receives
only the squash flag, and one pull can land several merges — are untouched and still carry the
decision.

**This is a correction, not a DEC-188 strike.** DEC-188 (`DECISIONS-INDEX.md:206`) governs a
decision the tree *flatly contradicts*; D-01's choice is still correct, only its stated reason
overreaches. But there is no propagation checker, so nothing will ever detect this sentence — the
operator has to amend it deliberately.

## Draft `D-11`, for the operator to sign — verbatim wording

```
- id: D-11
  choice: The post-merge sweep is HARNESS-CHECKOUT-ONLY for this feature. post-merge-sweep.sh
    keeps calling worktree_terminal.classify(root); it does not call classify_all. REQ-07 is
    read as scoped to the checkout whose merge fired the hook. A served repository's terminal
    worktree stays reported-not-removed, by INV-29, until a future feature gives fleet repos
    their own trigger. This resolves the fleet half of the brief's Q1, which D-08 left open.
  because: three facts measured at 4c7b650 make classify_all at the sweep a no-op rather than a
    fix. First, no served checkout carries .claude/skills/harness/hooks, and the shim resolves
    its root from its own file location, so a merge in a served repository fires no harness hook
    and REQ-07's own trigger never occurs there. Second, post-merge-sweep.sh:163 resolves the
    landed feature directory under the harness main checkout, while a served repository's feature
    directories live in that repository's own .harness/<repo>/features, so every served-repo
    record would take the :164 SKIP. Third, D-03's gh-sync.py ship invocation has no parameter
    for a second repository's state store. The accepted cost, named rather than argued away: the
    hook and INV-29 now compute DIFFERENT predicates on the repository dimension, which is exactly
    what D-01's because said must never happen. That asymmetry is deliberate here and is safe only
    because it errs toward inaction - INV-29 still refuses at exit 2 on a served repository's
    terminal worktree, so nothing ships silently wrong; the checkout merely waits for a manual
    removal. A test asserting the narrower scope is required so the asymmetry is pinned rather
    than latent.
  dec: none
```

**Companion correction to `D-01`'s `because` (operator's edit, one clause):** replace
> Sweeping all makes the hook compute the SAME predicate as INV-29, so the hook and the invariant
> can never disagree about what is eligible.

with
> Sweeping all makes the hook compute the same predicate as INV-29 WITHIN one checkout. D-10 later
> gave INV-29 a cross-repository entry point (classify_all) that the sweep does not call, so the
> two agree on which worktrees of this checkout are eligible and differ on which repositories are
> in view - see D-11.

## Routing

- **Not eng.** No code fix is warranted unless the operator signs D-11 the other way.
- **Test-only follow-up, if D-11 is signed as drafted:** `test-post-merge-sweep.py` has no
  fleet/second-repository case. Add one asserting the sweep leaves a served repository's terminal
  worktree standing *and* that INV-29 reports it — the pairing is what makes the narrowing
  intentional rather than a gap. Fixture shape already exists at
  `test-worktree-terminal.py:337-406`.
- **Independent of Amendment 3 / SC-16.** Deliberately not folded in, so the operator can accept or
  refuse the two separately.

## Open questions

- Q1 (blocking on this item only): does the operator sign D-11 as harness-only, or direct the
  cross-repository sweep as its own feature? Nothing else in FEAT-34 waits on the answer.
