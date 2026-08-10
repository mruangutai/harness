# Goal-check `goalcheck2` — scoped re-grade of SC-13, SC-18, SC-19 (harness-pm)

> Filed here, not at the dispatched path. `check-domain.sh` blocked
> `notes/receipt-harness-pm-goalcheck2.md` for harness-pm; my grant covers
> `.harness/features/*/notes/research-*.md`. Raised as Q1 in the DIGEST.

**All three grade `met`.** Every clause the prior goal-check named unbound now carries at least one
assertion of the criterion's own declared method, and I proved each binding non-vacuous by mutating
a scratchpad copy of the production module and watching that specific check go red. One residual is
named and does not change a verdict: SC-19's `os.path.isdir` half is vacuous, but its sibling
assertion binds the same clause.

Graded at working tree over `b89c00ad` (the factory files are untracked; nothing in the tree was
changed by this run). Baseline re-run by me, not inherited: `test-factory-claim.py` 77/77,
`test-factory-config.py` 56/56, `test-factory-integration.py` 97/97, all exit 0.

## Declared methods — derived from BRIEF.md, not from eng's rows

| SC | `verify:` | `evidence:` | BRIEF.md line |
|---|---|---|---|
| SC-13 | automated | unit | 250 |
| SC-18 | automated | unit | 177 |
| SC-19 | automated | integration | 184 |

`harness.json` `test_kinds.integration` is **active** with `cmd: run-unit-tests.sh --kind integration`
and a `detect` glob that names `test-factory-integration.py` explicitly. SC-19 does not rest on a
null runner; there is no verification-gap residual here.

## The mutants — tree untouched

Method: `.claude/skills/harness/bin/*.py` copied to a scratchpad dir; the test files resolve their
own `BIN_DIR`/`_BIN_DIR` from `__file__` / `fc.__file__`, so a copy under `/private/tmp` scans and
executes only the copy. Every mutation was applied to the copy of the **production** module.
(One pre-existing failure in the scratchpad copy of `test-factory-config.py` — `(21) the returned
root still has a readable probe file` — is an artefact of running outside the checkout and is
present at the scratchpad's own baseline. In the tree it passes.)

| SC | Mutant on the copy | Result |
|---|---|---|
| SC-13(b) | `factory_claim.py:277` reason text replaced by the create-ref reason text, so two reasons differ **only** by the embedded issue number (901 vs 904) | both SC-13(b) checks RED, 2/77 failing |
| SC-18 | `factory_land.py` `_main`: `harness_yaml.load_file(args.fleet)` added | both SC-18 checks RED |
| SC-18 | `factory_land.py` module scope: `harness_yaml.load_file(factory_config.FLEET_PATH)` at import time | both SC-18 checks RED |
| SC-19 (i) | `factory_decompose.py:353` boards at `building` instead of the fleet's `ready` | `(F) decompose: both board items boarded at the fleet's declared ready station` RED |
| SC-19 (ii) | `factory_land.py:60` push removed | `(F) land: recorded git commands include a push` RED, and **only** that check — 1/97 failing |
| SC-19 (iii) | `factory_workspace.py:134` `_checkout_issue_branch(...)` removed | `(F) workspace: recorded git commands include a checkout` RED — **while `(F) workspace: the payload path is an actual directory on disk` stayed GREEN** |

## SC-13 — met

Clause (a) was already bound before this cycle (prior goal-check's own row). Clause (b)'s resting
condition — no two skip reasons read alike — is bound at `test-factory-claim.py:724-729`, with the
fixture guards at `:717` (exactly seven skip lines fired) and `:719` (they are issues 901..907) that
stop the check passing on an under-fired fixture.

**The trap is genuinely avoided.** `_normalize_reason` (`:672-675`) strips `#\d+` and `issue-\d+`
before comparison, and the `skip #N` prefix is already removed by the em-dash capture at `:715`. I
printed the seven normalised reasons from the scratchpad copy: **no digit survives normalisation in
any of them** — the only remaining variable token is a `T-NN` task id, and the bonus check at
`:736-740` normalises those too and is green. So there is no residual bare number that could make
two identical phrases read as distinct. The mutant above confirms it empirically.

## SC-18 — met

Exclusivity is bound at `test-factory-config.py:448-459` over `_find_fleet_reads` (`:344-395`),
which enumerates `open(` / `harness_yaml.load_file(` **call sites** by AST across module scope and
every function/async-function scope, pruned at nested `def` boundaries by `_scope_body_walk`
(`:328-341`). It returns exactly one hit and asserts it is `factory_config.py`'s `load_fleet`.

**The argparse-help trap is avoided by construction and by observation.** `fleet.yaml` appears as a
bare help string at `factory_land.py:43` and `factory_workspace.py:110` at HEAD, and the enumeration
is green with those present — a help string is not the first argument of an `open`/`load_file` call,
so it cannot be a hit. Both bypass mutants above go red, which is what rules out a check that merely
counts to one for unrelated reasons.

**Anchor question the dispatch asked me to settle: not drift, two different things.** `:43`/`:110`
are the argparse `--fleet` help strings (the trap). The prior goal-check's `factory_land.py:59` and
`factory_workspace.py:117` are the `factory_config.workspace_path(fleet, args.repo)` call sites (the
shared-derivation clause). I re-derived all four at HEAD; every one is correct and they name
different lines because they are about different claims.

The residual `assert2-eng` named in its Q2 (a cross-scope alias whose name does not contain "fleet")
stands, and I am not counting it against the clause — it is a deliberately obscure bypass, not an
accidental one, and it is a sub-case of a narrowing the operator accepted.

## SC-19 — met, with one named vacuous assertion

- **(i) decompose boards them at `ready`** — bound at `:644-649`, read from GH_STATE before claim
  runs, against the fleet's own declared `ready_option` rather than a hard-coded string. Mutant red.
- **(ii) land pushes that branch** — bound at `:737-744` against the recorded git argv. Mutant red,
  and surgically so: 1 of 97.
- **(iii) workspace produces a checkout** — bound at `:704-708` against a recorded
  `checkout <branch>` in the git log. Mutant red.

**The extra trap the dispatch flagged is real, and it does not sink the clause.** Case F pre-creates
`<workspace_root>/widget/.git` at `:676`, and `factory_config.workspace_path` derives the checkout
path as `<workspace_root>/widget` for `REPO = "acme/widget"`. So the `os.path.isdir` assertion at
`:691-692` is asserting the fixture's own `makedirs`: under a `factory_workspace.py` that produces
no checkout at all, it stayed **green**. It is vacuous: it passes under a null-checkout mutant.

Clause (iii) is nevertheless closed, because its sibling assertion at `:704-708` is a genuine
binding of the same clause and went red under exactly that mutant. The operator's rule is
zero-assertions-per-clause, not zero-vacuous-assertions — one binding assertion closes it. The
residual worth someone's attention later: either drop the `isdir` check or move the fixture's
`makedirs` to a sibling directory so it binds too.

## Out of scope, untouched

SC-06 and the other sixteen criteria were not re-graded. No test and no production file in the tree
was changed; nothing staged, nothing committed.
