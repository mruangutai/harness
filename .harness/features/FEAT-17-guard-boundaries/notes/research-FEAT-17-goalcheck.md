# Goal-check — FEAT-17 guard boundaries — GC-01

**BLUF. Eight of ten criteria are met on their own declared method. SC-07 is NOT met — one of its
three clauses has no assertion in either test file. SC-09 is SUPERSEDED by the removal receipt: its
letter cannot be satisfied without falsifying the record, and its two checkable sub-claims both hold
today.** Nothing is owed in guard code. What is owed is one paired assertion (SC-07) and one
operator ruling on SC-09's text.

## Tree, stated exactly

At entry, HEAD was `b6f2c8005a3c4cbe7c356839ba9bdcd04f4f6383` on branch
`feat/FEAT-17-guard-boundaries`. Two departures from the dispatch's assertion, both reported rather
than assumed away:

1. The tree was **not** clean. `git status --porcelain` showed one modified file,
   `.harness/features/FEAT-17-guard-boundaries/feature.json`, whose entire diff is
   `review_sha: "none" -> "b6f2c80"` — the operator's own pin, uncommitted. I did not touch it.
2. **HEAD moved mid-run**, to `2e02cfcb07a6b4928aacb89294ba1dfc2a380432`. `git diff --stat b6f2c80
   HEAD` is one added file, `.harness/notes/grilling-central-product-config-2026-08-12.md` (+101),
   unrelated to this feature.

No guard, test, plan or BRIEF file differs between the two commits, so every verdict below holds at
`b6f2c80` and at `2e02cfc` alike. The SC-07 diff was taken against explicit SHAs.

## Run evidence (`evidence: integration`)

`bash .claude/skills/harness/bin/run-unit-tests.sh --kind integration` — **runner exit 0**, all 12
`INTEGRATION_SCRIPTS` reported `PASS`. `--kind unit` would not have executed any of the three
(`run-unit-tests.sh:17-18`). The three suites executed, by their own summary lines:
`test-check-domain.py` — `8/8 worktree-boundary cases passed`, plus `30/30 post-mode`, `14/14 hook`;
`test-bash-write-guard.py` — `22/22 worktree-boundary cases passed`;
`test-check-state.py` — `PASS`, with cases `(u.1)`–`(u.6)` each printed `ok`.

## Verdicts, with the assertion that settles each

- **SC-01 met.** `test-check-domain.py:1512-1516` — Write into `<sib>/allowed/x.txt` exits 2 and
  stderr contains `.claude/worktrees`; paired allow `:1520-1522` (root's own `.harness/allowed/`
  write exits 0). Fixture is hand-built `.git` pointer files, no `git` invoked (`:1486-1500`).
- **SC-02 met.** `test-bash-write-guard.py:333-336` forbidden, `:340-342` paired allow, same fixture
  (`_worktree_fixture`, `:296-309`).
- **SC-03 met, both routes.** Write: forbidden `test-check-domain.py:1529-1531`, both wording halves
  on that same stderr `:1542-1544`, paired allow from a legitimate-worktree root `:1547-1549`. Bash:
  forbidden `test-bash-write-guard.py:346-349`, wording `:358-361`, paired allow `:372-374`. Targets
  are control-plane and in-domain for that root, so they exit 0 without the rule — discriminating.
- **SC-04 met.** `test-bash-write-guard.py:482-521` — absolute-outside, `-b`-before-destination and
  relative all expect 2; `git worktree add <root>/.claude/worktrees/FEAT-99 HEAD`, `git status
  --porcelain`, `git worktree list`, `git commit -m x` all expect 0. Relativity is asserted by
  wording too (`:527-529`).
- **SC-05 met.** `test-bash-write-guard.py:243-259` — manifest grants `src/**` AND
  `.harness/allowed/**`; `src/main.py` expects 2 on Bash and Write, `.harness/allowed/x.txt` expects
  0 on both. The `src/**` grant is what makes the refusal about the control-plane rule and not about
  a missing grant.
- **SC-06 met.** `test-bash-write-guard.py:412-470` — isolated `bin/`, root pinned INSIDE
  `<root>/.claude/worktrees/wt`, baseline `(0,0)` asserted `:447`, constant mutated by name `:452`,
  `__pycache__` dropped `:462`, and `after == (2,2)` asserted on BOTH routes `:467-470`.
- **SC-07 NOT MET — one clause of three has no assertion.**
  - Met: no pre-existing case's expected exit code changed VALUE. Diffed `52ee5db..b6f2c80` (base =
    `git merge-base main HEAD`) over both test files. Five retargets, all value-preserving:
    `docs/a.md -> docs/harness/a.md` in three cases keeping `0` and in `rm docs/a.md; rm src/main.py`
    keeping `2`; `allowed/x.txt -> .harness/allowed/x.txt` in `run_t14`'s allow half keeping `0`. The
    only other change to an expectation list is the ADDITION of `("src/main.py", 2)`. No case was
    deleted.
  - Met: paired refusal — `<root>/src/main.py` exits 2 despite the `src/**` grant
    (`test-bash-write-guard.py:249-259`).
  - **Not met:** "a write to `<root>/.claude/worktrees/wt/.harness/allowed/x.txt` … from OUTSIDE that
    worktree exits 0 on both routes" is asserted **nowhere**. Every `.claude/worktrees` occurrence in
    both files is either a refusal, a creation case, or a session rooted INSIDE the worktree
    (`test-check-domain.py:1498,1547`; `test-bash-write-guard.py:306,372,426-431`). SC-06's own
    baseline pins the root inside, by design, so it cannot stand in. No task in `plan.yaml` ever
    instructed this assertion. **The behaviour itself is correct** — I probed it directly and both
    routes exit 0 — so what is owed is a test, not a fix. A probe is not `automated` evidence.
- **SC-08 met.** `test-check-state.py:1193-1268` — repo A silent `(u.1)`; repo B's sibling line is a
  `VIOLATION` `(u.2)` and DOES carry `git worktree remove` `(u.3)`; repo C's own-root line is a
  `VIOLATION` `(u.4)`, its legitimate `.claude/worktrees/legit` line is absent `(u.5)`, and the
  own-root line names `.claude/worktrees` and does NOT say `git worktree remove` `(u.6)`. One
  substitution, and it is a strengthening: SC-08's "exits non-zero" is asserted as the line's
  `VIOLATION` prefix instead, because the fixture is red for other reasons and the exit code does not
  discriminate. `check-state.sh:1079` (`sys.exit(1 if bad else 0)`) makes the prefix imply exit 1.
- **SC-09 SUPERSEDED — see below.**
- **SC-10 met.** Forbidden half on both routes, each naming the module:
  `test-check-domain.py:1573-1575`, `test-bash-write-guard.py:391-393`. Paired allow: with the module
  absent AND the manifest removed, DEC-101 still prints `enforcement OFF` at exit 0
  (`test-check-domain.py:1584-1586`); the cited non-regressing case survives at
  `test-check-domain.py:172-174`.

## SC-09, ruled explicitly

**Its letter fails.** `notes/worktree-list-before.md` and `notes/worktree-list-after.md` do not exist
and were never committed on any branch (`git log --all --diff-filter=A -- '*worktree-list-*'` returns
nothing). Its paired negative — the FEAT-13 worktree still listed after — is unsatisfiable: `git
worktree list` now returns one entry, the main checkout, so no `.claude/worktrees/` entry survives.

**Its intent holds, and is proven today.** T-06's `verify:` block, carried verbatim from
`plan.yaml` (byte-identical to the dispatch text; I diffed the `safe_load`ed scalar against it),
**exits 0 / prints `OK`**: no out-of-place worktree is present, `archive/worktree-r6` exists and
resolves to `52d8334` which `git merge-base --is-ancestor` confirms is NOT an ancestor of `main`, and
the receipt names `LATE`, the tag, and `sweep`.

I rule **superseded**, not `not_met`, because the substitute evidence was produced under ruling R-01
(`plan.yaml:9-40`), signed by the operator, and because the only technique that could satisfy the
letter — writing the before-capture now from memory — is falsification of the record. **Nobody
manufactures the missing captures, and I did not.** Doing so would place the exact defect this
feature exists to remove inside the feature that removes it. The two checkable sub-claims are
reported above on their own and both hold; the unprovable half is the before/after comparison and the
targeted-vs-sweep control, and the receipt says so in its own voice
(`notes/worktree-removal-receipt-2026-08-12.md:29-37`).

I did not edit BRIEF.md. SC-09's text still asserts two files that do not exist; that contradiction
stands in the signed artifact and only the operator can resolve it.

## Owed

1. **must_fix (SC-07):** add one paired-allow assertion — a session rooted at `<root>` writing to
   `<root>/.claude/worktrees/wt/.harness/allowed/x.txt`, expecting 0 on both routes — to
   `test-check-domain.py`'s and `test-bash-write-guard.py`'s worktree fixtures. No guard change.
2. **Operator's call (SC-09):** amend SC-09's text to cite the receipt, or accept `superseded` on the
   record. Not mine to edit.
3. **Backlog, unchanged from the BRIEF:** both guard suites match `harness.json`'s `unit` detect glob
   yet sit in `INTEGRATION_SCRIPTS`, so `--kind unit` never runs them.
