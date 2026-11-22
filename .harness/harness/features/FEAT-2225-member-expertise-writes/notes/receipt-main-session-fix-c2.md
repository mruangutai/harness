# Receipt — main session — FEAT-2225 validate c2 fix segment (F2; main-session-direct, DEC-174)

**BLUF.** F2 is closed at close time. `verify-receipt` no longer treats the feature's own HEAD as an
authorized starting state. An unreceipted edit that is committed before a receipted application is
now refused (exit 15) at live yield and at durable close-run, for both member and lead lineage.
Handoff: `notes/handoff-validate-c2.md` seq-7. Panel digest: `runs/r-20261121-7-validate-c2-validator/digest.md`.

## T-01 half: `expertise-merge.py`

One resolver, `authorized_base`, chooses the anchor commit:
- No `--base`: `merge-base(HEAD, <default branch>)`, where the default branch is the first of
  `refs/remotes/origin/HEAD`, `refs/remotes/origin/main` and `refs/heads/main` that resolves.
- With `--base`: `merge-base(--base, HEAD)`. This is the same commit when the PR already contains the
  base. When main has moved past the fork, it is the fork point, where the receipted writes actually
  begin. Anchoring on the raw base blob would refuse the legitimate supersession-with-`--base` control.
- Nothing resolves, or there is no shared history: exit 15 `NO AUTHORIZED BASE`, fail closed.
- The write chain must reach that commit's blob of the destination, or "absent" if the file is not
  there. HEAD is never an anchor.

Red-first: `notes/red-first-fix-c2-core.md`. Against the c1 core, unit u44 and 5 integration checks
failed: committed G-01 tamper for member and lead, each with and without `--base`, plus no-base.
QA mutant N2 (unchained-active-batch guard removed) now fails exactly the new discriminating check;
before, it left the suites green.

## T-04 half: `validate-digest.py`

`_verify_receipt` passes no `--base` and relies on the core's single resolver. A second resolver in
validate-digest (its existing `_default_branch_or_none` reads only origin/HEAD) could disagree with
the core. The base comes from git, never from a digest field. Regression group
`run_member_expertise_committed_tamper_cases`: live member yield, live lead yield, durable CLI and
close-run are all refused. Red 0/4 against the c1 core, then 4/4. Fixtures now publish to a local bare
origin so the default branch resolves. No existing assertion changed. Red-first:
`notes/red-first-fix-c2-digest.md`.

## Remaining boundary (stated)

A checkout whose HEAD *is* the default branch anchors on itself. That is the main checkout, never the
`chore/distill-*` or feature branch a distill PR merges from, so no close path reaches it.
