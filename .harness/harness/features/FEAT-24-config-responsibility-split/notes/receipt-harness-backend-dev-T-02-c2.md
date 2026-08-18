# Receipt — harness-backend-dev — FEAT-24 T-02, cycle 2 (MUTATION PROOFS ONLY)

**Headline finding: the suite proves 12 of 13 named defects but is BLIND to a fallback-on-failure
implementation of `product_config` — a mutation that reads a stale checkout when the remote raises
passes 78/78, contradicting the module's own docstring ("There is no fallback to workspace_path
and no default," `factory_config.py:260-261`). This is a fail-open shape: a network fault would
read as a stale local board rather than a loud error.** See F-5.

No production or test code changed. `factory_config.py` and `test-factory-config.py` are
byte-identical to their state at commit `962417a` at the end of this spawn — confirmed in §5.

## 1. Verify block cross-check

Extracted T-02's `verify:` from `plan.yaml` with `yaml.safe_load` to `/tmp/plan_verify.txt`,
wrote the dispatch's verbatim block to `/tmp/dispatch_verify.txt`, and ran an actual `diff`:

```
$ diff /tmp/dispatch_verify.txt /tmp/plan_verify.txt; echo "diffrc=$?"
diffrc=0
```

**IDENTICAL.** No mismatch.

## 2. Baseline

```
$ sha256sum .claude/skills/harness/bin/factory_config.py .claude/skills/harness/bin/test-factory-config.py
ff0fc89ca2cd3b38a3e8917d36cd70b15045e84e89f54bf49518dce73361cb1a  .claude/skills/harness/bin/factory_config.py
a0416a9240106e8e6bfbbbc3306a8d0cdcfd0a2f5366cb071fa336759b75febd  .claude/skills/harness/bin/test-factory-config.py
```

Verify block, run verbatim (`bash /tmp/dispatch_verify.txt`, contents identical to the dispatch's
quoted block per §1):
```
T-02 GREEN
```

Underlying test script's own tail, run separately, same tree:
```
ok    (X) SC-18: that one reader is factory_config.py's load_fleet — no other tool bypasses it

78/78 checks passed.
```
RC=0. Zero `FAIL` lines. **Baseline ok-line count: 78.** All ok-line texts named by the verify
block's `has "..."` checks are present verbatim — the verify block itself mechanically checked
every one of them and returned `T-02 GREEN`, which is stronger evidence than the c1 static
`ast.parse` walk.

## 3. Mutation table

13 mutations. Per mutation: (a) hashed the file before, (b) applied one plausible wrong
implementation, (c) ran the suite, (d) restored via
`git checkout -- .claude/skills/harness/bin/factory_config.py`, (e) confirmed
`git diff --exit-code` rc=0 AND sha256 == `ff0fc89c...` after the restore — done individually for
every row below, not only at the end.

| # | Target | Mutation (before → after) | Reddened case(s) | Total red | Surviving ok | Restore |
|---|---|---|---|---|---|---|
| 1 | `_STATION_KEYS` drop `backlog` | `("backlog","ready","building","review","done")` → `("ready","building","review","done")` | 5×`accepts...` (all five, collateral — F-1) + `rejects...missing backlog` (key-specific) + `(6)/(28b) coerces digit string` (collateral) = 7 named FAILs, then module crash | 7 FAIL + 46 ok = 53 lines printed, module then crashed (F-2) | 46 | diffrc=0, sha256 match |
| 2 | `_STATION_KEYS` drop `review` (distinct key) | same tuple, drop `review` instead | 5×`accepts...` (collateral) + `rejects...missing review` (key-specific) + `(6)/(28b)` (collateral) = 7, then crash | 7 FAIL + 46 ok = 53 lines, crashed (F-2) | 46 | diffrc=0, sha256 match |
| 3 | `key_base = where` → `key_base = f"{where}.board"` (revert old bug) | `key_base = where` → `key_base = f"{where}.board"` | `owner missing`, `number not an int`, `station_field missing`, `stations missing`, `stations key set wrong`, `a station value is empty` — 6 cases. Pinned pair (`github.board.owner` present / `github.board.board` absent) reddened as required | 6 | 72 | diffrc=0, sha256 match |
| 4 | `load_fleet` board rejection | the `if "board" in entry: raise FleetError(...)` block → `pass` | `load_fleet rejects a repos entry carrying a board key` | 1 | 77 | diffrc=0, sha256 match |
| 5a | fallback-on-failure (as literally instructed) | on `GhError`, read `workspace_path(fleet, repo_name)/.harness/harness.json` if present, else re-raise (correctly wired to the real checkout path this time) | **none — did not redden. This is F-5, the headline finding.** | 0 | 78 | diffrc=0, sha256 match |
| 5b | no-fallback / consult-checkout-first (a different property than 5a — see note below the table) | if a checkout file exists at `workspace_path`, read it INSTEAD of the remote (unconditionally, not only on failure) | `product_config never falls back to a checkout` | 1 | 77 | diffrc=0, sha256 match |
| 6 | no-checkout (corrupt returned value instead of raising — see F-3 for why a literal "require checkout" raise is unusable) | after successful remote parse: if no checkout file exists at a **real** (on-disk) workspace_root dir, force `doc["github"]["board"]["number"] = 999` | `product_config reads the remote at default_branch with no checkout on disk` + 3 collateral (`number not an int` raise case, `board_for resolves through product_config`, `product_config memoisation: a failing read is not cached...`) | 4 | 74 | diffrc=0, sha256 match |
| 7a | memo caches failures too | on `GhError`, stash a fake success doc into `_product_config_memo` before raising | `product_config memoisation: a failing read is not cached and the next call succeeds` | 1 | 77 | diffrc=0, sha256 match |
| 7b | memo disabled entirely | `if memo_key in _product_config_memo:` → `if False and memo_key in _product_config_memo:` | `product_config memoises a successful read: a second board_for makes no second remote read` | 1 | 77 | diffrc=0, sha256 match |
| 8a | number coercion widened to accept float | added `elif isinstance(number, float): coerced = int(number)` before the digit-string branch | `board_for raises naming the file and the key: number not an int` | 1 | 77 | diffrc=0, sha256 match |
| 8b | number coercion narrowed to reject digit string | `elif isinstance(number, str) and number.strip().isdigit():` → `elif False and isinstance(...)` | `(6)/(28b) validate_board coerces a digit string number to an int` | 1 | 77 | diffrc=0, sha256 match |
| 9a | remote-failure message drops ref from `next_step` only | `f"...at {ref}: {e}"` → `f"...: {e}"`, `human_path` untouched | **none — did not redden (F-4)** | 0 | 78 | diffrc=0, sha256 match |
| 9b | remote-failure message drops ref from `human_path` only | `human_path = f"{repo_name}@{ref}:..."` → `f"{repo_name}:..."`, `next_step` untouched | **none — did not redden (F-4)** | 0 | 78 | diffrc=0, sha256 match |
| 9c | remote-failure message drops ref from **both** slots | both changes from 9a+9b applied together | `product_config raises naming repo, path and ref when the remote read fails` | 1 | 77 | diffrc=0, sha256 match |

Mutations 5a and 5b are different properties even though both touch the checkout-consulting code,
and the table keeps them distinct rather than merging them under one "no-fallback" label:

- **5a** answers "does the suite catch a remote-failure-then-fallback-to-checkout
  implementation?" — the property the docstring states ("no fallback ... no default") and the
  property the dispatch's item description names ("Make it fall back to a checkout read when the
  remote read raises"). **It does not catch it.**
- **5b**, which is what the `product_config never falls back to a checkout` case's own fixture
  (`test-factory-config.py:513-526`) actually exercises, answers a narrower question: "when the
  remote SUCCEEDS and a checkout also exists with different data, does the remote win?" That case
  reddened cleanly. But its fixture never makes the remote fail, so it says nothing about the
  failure-path property in 5a.

An earlier, differently-wired attempt at 5a (using `os.getcwd()`-derived paths that could never
resolve to a real file) also produced 78/78 and was discarded as inconclusive rather than
reported — 5a above is the correctly-wired repeat of that same mutation, and its 78/78 is the real
result, not an artifact of a broken mutation.

## 4. Findings

**F-5 (mutation 5a — the fallback-on-failure gap, headline).** No fixture in
`test-factory-config.py` exercises "the remote read raises AND a checkout exists on disk." Case
(ii) (`product_config raises naming repo, path and ref when the remote read fails`,
`test-factory-config.py:486-511`) uses `good_fleet_dict()`'s default
`workspace_root=/tmp/does-not-need-to-exist/factories` — no checkout is ever present, so a
fallback-on-failure implementation finds nothing there either, falls through to the original
raise, and passes. Case (iii) (`product_config never falls back to a checkout`,
`test-factory-config.py:513-526`) does put a checkout on disk, but its remote read **succeeds**,
so the `except GhError` branch this mutation targets never executes. The two fixtures cover
disjoint halves of the 2×2 (remote fails / checkout absent) and (remote succeeds / checkout
present) — the (remote fails / checkout present) cell that the docstring's "no fallback" claim is
actually about is untested. This is a fail-open shape per this codebase's own review history: a
network fault, with this mutation applied, would silently read a possibly-stale local board
instead of raising the loud `FleetError` the docstring promises.

**F-1 (mutations 1, 2 — `_STATION_KEYS`).** Dropping any one key from the 5-key set does not
redden "exactly one case naming that key." The five `validate_board accepts the five-key stations
map: <k>` cases are not independently pinned per key: each supplies a full 5-key stations dict, so
dropping *any* key from `_STATION_KEYS` breaks the set-equality check for all five `accepts` cases
at once (collateral, not key-specific). Only the `rejects a stations map missing <k>` cases are
genuinely key-specific — mutation 1 (drop `backlog`) reddened `missing backlog` only among the
`rejects` group; mutation 2 (drop `review`) reddened `missing review` only. Reported as measured
fact; no verdict rendered on how an earlier receipt characterised this.

**F-2 (mutations 1, 2 — partial suite death).** Both `_STATION_KEYS` mutations print 53 of 78
lines (46 `ok` + 7 `FAIL`, correctly including the two targeted cases) and then crash on an
uncaught `FleetError` inside `test-factory-config.py`'s "board_for resolves through
product_config" fixture (`_b1 = fc.board_for(...)` at line 464, no `try/except`, unlike every
`board_for_raise_case` call). The remaining 25 of 78 cases — everything after line 464, including
all of the `product_config` no-checkout/no-fallback/memoisation cases, the `--show` cases and the
sanity/SC-18 cases — never get a chance to run under either of these two mutations. This is not
the zero-ok-line pathology the dispatch warns about (both targeted cases print their FAIL line
correctly before the crash), but it does mean these two mutations cannot serve as evidence for
anything past line 464 — those properties are separately covered by mutations 5b–9c.

**F-3 (mutation 6 — a literal "require a checkout" raise crashes the suite; not the reported
mutation).** Tried first, as a straight `raise FleetError(...)` when no checkout exists on a real
workspace_root: 45 `ok` + 8 `FAIL` = 53 lines print (crashing in the same line-464 region as
mutations 1/2, for the same unguarded-fixture reason). A second, narrower attempt scoped the same
raise to `os.path.isdir(workspace_root)` only: 54 `ok` + 0 `FAIL` = 54 lines print, then the
module dies specifically at `test-factory-config.py:480` (`_result = fc.board_for(fleet, _repo)`
in the "no checkout on disk" fixture itself, also unguarded). Neither straight-raise variant is in
the mutation table because neither produces a named FAIL line — both are module deaths, which per
the dispatch's hard rule are not proof. The table's mutation 6 is a working substitute (corrupt
the returned board number instead of raising) that reddens the named case cleanly, at the cost of
testing a different (and more contrived) wrong-implementation shape than "requires a checkout."

**F-4 (mutations 9a, 9b — the ref assertion checks a redundant slot, not two independent prose
sites).** The case `product_config raises naming repo, path and ref when the remote read fails`
asserts `("mruangutai/harness" in _msg and ".harness/harness.json" in _msg and "trunk-xyzzy" in
_msg)`. Removing `ref` from `next_step`'s prose alone (9a) does not redden it, because `ref` is
still embedded in `human_path` (the FleetError `value` slot, always present in `str(exc)` via
`factory_cli.body`). Removing it from `human_path` alone (9b) does not redden it either, for the
mirror reason. Only removing `ref` from both locations (9c) reddens the case. The assertion
currently proves "ref appears somewhere in the message" via two independent code paths that both
happen to carry it today — it does not prove either specific slot names the ref, and a refactor
that dropped ref from one slot while leaving it in the other would pass silently.

No other mutation in the table (3, 4, 5b, 6, 7a, 7b, 8a, 8b, 9c) failed to redden its target case.

## 5. Closing confirmation

```
$ sha256sum .claude/skills/harness/bin/factory_config.py .claude/skills/harness/bin/test-factory-config.py
ff0fc89ca2cd3b38a3e8917d36cd70b15045e84e89f54bf49518dce73361cb1a  .claude/skills/harness/bin/factory_config.py
a0416a9240106e8e6bfbbbc3306a8d0cdcfd0a2f5366cb071fa336759b75febd  .claude/skills/harness/bin/test-factory-config.py
$ git status --short .claude/skills/harness/bin/factory_config.py .claude/skills/harness/bin/test-factory-config.py
(no output)
```

Both hashes match the baseline in §2. Final literal re-run of T-02's verify (the exact block
quoted in the dispatch, cross-checked against `plan.yaml` in §1):

```
T-02 GREEN
```

## Q3 carried forward, unanswered

c1's Q3 (the `"fleet key invalid"` `what`-slot wording recommendation for `validate_board`'s five
raise sites) is untouched by this spawn — it was a recommendation for the author of the
`factory_config.py` write, which has already landed at `962417a` using the original wording. Not
this spawn's decision to make or remake.
