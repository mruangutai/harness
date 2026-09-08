# SIMPLIFICATION angle — FEAT-56 simplify pass

**BLUF: clean.** `findings: []`. The diff (`4b5dbb23..HEAD`) does not add unnecessary
complexity. The 15-case test file is mostly distinct behaviour with three legitimate
same-path parameter rows (backlog-only, per the hard constraint — none applicable here
anyway since removing them is a coverage judgement already made by qa). No
implementation-pinning assertions. One dead conjunct in `_check_product_configs`'s
final guard, judged worth keeping. No narrating comments in `bin/**`/`tests/**`.

## 1. The 15 `check()` cases in `tests/unit/test-fleet-product-config.py`, per-case verdict

| # | case (as printed) | verdict |
|---|---|---|
| 1 | (a) two declared repos, both succeed -> every entry ok, ok count 2, unreachable 0 | BEHAVIOUR |
| 2 | (a)/(d) len(report) equals len(fleet['repos']) | BEHAVIOUR (establishes the length invariant) |
| 3 | (b) the FIRST entry, asserted individually, is not ok and names repo and ref | BEHAVIOUR (mixed success/failure path) |
| 4 | (b) the SECOND entry, asserted individually, is ok with an empty detail | BEHAVIOUR (proves per-entry isolation: a sibling failure doesn't corrupt the ok entry) |
| 5 | (b)/(d) len(report) equals len(fleet['repos']) | SAME-PATH PARAMETER ROW (re-asserts #2's fact, only the fixture scenario differs) |
| 6 | (c) invalid JSON content -> entry not ok, detail names the invalid-JSON failure | BEHAVIOUR (distinct failure mode: JSON-parse error vs. GhError in case b) |
| 7 | (c)/(d) len(report) equals len(fleet['repos']) | SAME-PATH PARAMETER ROW (re-asserts #2's fact again) |
| 8 | every entry carries exactly repo/ref/path/ok/detail, path is _PRODUCT_CONFIG_PATH | BEHAVIOUR (schema/contract check) |
| 9 | product_config_report preserves fleet['repos'] declaration order | BEHAVIOUR (ordering guarantee, distinct axis) |
| 10 | (e) --check-product-configs exits 2 (EXIT_REFUSED) under a failing stub | BEHAVIOUR (CLI exit-code contract) |
| 11 | (e) stdout under failure parses as ONE JSON payload with declared/ok/unreachable/members | BEHAVIOUR (establishes the payload-shape assertion pattern, failure counts) |
| 12 | (e) exactly one stderr line is written for the one unreachable member | BEHAVIOUR (fail-log side effect, non-zero case) |
| 13 | (e) --check-product-configs returns without SystemExit under an all-succeeding stub | BEHAVIOUR (opposite branch of #10: return vs. exit) |
| 14 | (e) stdout under success parses as ONE JSON payload with declared/ok/unreachable/members | SAME-PATH PARAMETER ROW (repeats #11's shape-assertion pattern; only the count values 2/2/0 vs 2/1/1 differ) |
| 15 | (e) no stderr line is written when nothing is unreachable | BEHAVIOUR (complements #12 with the zero-emission branch — proves the fail-log loop skips ok entries rather than merely trusting it) |

12 distinct behaviours, 3 same-path parameter rows (#5, #7, #14). Per the pass's hard
constraint, parameter-row status alone is never an apply — it's a coverage-adequacy call
qa already made — so these are recorded, not fixed. None pin implementation (see §2), so
none are even backlog-eligible under the "pins implementation" carve-out.

## 2. Implementation-pinning assertions — none found

Checked every compound condition for a conjunct that pins a field copy, a default, exact
source text, an internal call count, or the memo dict by name (`test-fleet-product-config.py`
lines 132-240). `clear_product_config_memo()` is the only memo touch anywhere in the file —
the sanctioned reset, not a reach-in. The one attribute-vs-attribute comparison,
`m["path"] == fc._PRODUCT_CONFIG_PATH` (line ~186), compares the report's threaded field
against the *same constant `product_config` itself reads with* — it verifies wiring
(the field a consumer reads reflects what was actually fetched), not an incidental literal.
Not a finding.

## 3. `_check_product_configs`'s final guard — `factory_config.py` (post-diff line ~471)

```
if unreachable_count or len(report) != len(fleet["repos"]):
    sys.exit(factory_cli.EXIT_REFUSED)
```

`unreachable_count = len(report) - ok_count`, and `product_config_report` unconditionally
appends exactly one entry per `fleet["repos"]` entry in its `for` loop (no early return, no
filter, no swallowed non-`FleetError` exception per its own docstring) — so `len(report) ==
len(fleet["repos"])` always holds today, and the second conjunct is **unreachable given the
current implementation**.

**Verdict: LEAVE, not dead weight.** Cost of keeping it is one cheap `len()` comparison; the
guard is documented intent (the function's own docstring names "or the report came up short
of the declared count" as part of its contract), and it is real insurance against a future
edit to `product_config_report` that filters or short-circuits the loop — the kind of
regression a reviewer skimming a diff to that function could plausibly miss, and this guard
would catch it for free at zero added test cost. This is a judgement call, not a lint; I am
not filing it as a finding.

## 4. Comments narrating the change vs. stating a present fact

Checked every `bin/**`/`tests/**` diff hunk (`check-domain.sh`, `check-instruction-paths.py`,
`check-state.sh`, `gh-sync.py`, `layout_migration.py`, `post-merge-sweep.sh`,
`upgrade-config.py`, and the four integration test files, plus the new
`test-fleet-product-config.py`). Every changed line rephrases a *present* claim about the
control plane vs. a fleet member ("this control-plane clone", "for a fleet member, that file
lives in the member's own repository") — none read "this used to be X" or "after FEAT-56 we
now...". The `FEAT-56`/`T-04` citations in the new test file's module docstring and
`clear_product_config_memo()`'s docstring follow the same provenance-citation convention
already used throughout this file (`FEAT-41 T-01`, `FEAT-24 T-02 item 6`, `FEAT-42`) — not
narration, and pre-existing style. No findings.

## Findings

`[]` — none. All four checks above came up clean; §3 is a documented judgement (LEAVE), not
a fix.
