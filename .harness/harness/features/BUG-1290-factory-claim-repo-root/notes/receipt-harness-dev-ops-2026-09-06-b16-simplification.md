# Receipt — harness-dev-ops — SIMPLIFICATION angle — BUG-1290 B-16

**BLUF:** near-empty pass. One finding, backlog-only (a docstring overclaim that makes the
existing outer `try/except` a necessary guard rather than redundant machinery). Every other
angle-specific probe the dispatch asked for came back negative — I ruled each out explicitly
below rather than manufacturing a finding.

## Finding 1 — `_5b_property_holds`'s totality docstring overclaims; the outer `try/except` around it is a necessary guard, not redundant machinery

- **File/line:** `tests/unit/test-factory-claim.py:1208-1223` (docstring + body), consumed at
  `:1227-1231` (5b) and `:1317-1321` (5g).
- **Summary:** the docstring claims the predicate is "Total over any (code, out, err) … so it
  never raises," but `payload.get("issue")` at line 1220 assumes `json.loads(out)` returned a
  `dict`. If `out` is valid JSON that decodes to a non-dict (e.g. a list, string, number, bool,
  `null`), `.get` raises `AttributeError`, which the `except (json.JSONDecodeError, TypeError)`
  clause at line 1217 does not catch.
- **Concrete cost:** the claim is false in general, even though `run_main`'s real CLI output
  never produces non-dict JSON today, so it is not reachable in practice. The cost is only if a
  later reader trusts the docstring and treats the surrounding `try/except Exception` (1227,
  1317) as belt-and-braces worth deleting — that would convert a future genuinely-unreachable
  edge case into an uncaught crash that aborts the file mid-run and silences every later `check()`
  call (the exact failure mode the file's `5a`-block comment at line 1156 says this pattern
  exists to avoid).
- **Alternative:** either narrow the docstring's claim to the shapes this file's `run_main`
  actually produces, or widen the except tuple to `(json.JSONDecodeError, TypeError,
  AttributeError)` so the claim is literally true. Not applying this myself — read-only pass.
- **Verdict:** backlog row, `blocking: false`. Not reachable today; not worth a rework cycle at
  the ship gate.

## Ruled out (no finding)

- **Four conjuncts in `_5b_property_holds`'s return** (`issue==952`, `"951" in err`,
  `"unresolvable blocker" in err`, `"no plan could be read" not in err`): checked pairwise for
  logical implication. None is redundant — each guards a distinct mutant the file's own comments
  name: `issue==952` guards wrong-issue resolution; `"951" in err` guards kaya's blocker going
  unreported; `"unresolvable blocker" in err` guards the *reason* being right; `"no plan could be
  read" not in err` guards against cross-segment plan-cache bleed producing 5c's no-plan reason
  instead of 5b's. No assertion here is a candidate even for a backlog row.
- **5g's mutant swap (`saved_blocker_cache` / `try` / `finally`)**: the file already uses this
  exact save-restore-in-`finally` idiom for monkeypatching module state (`run_main`'s
  `saved_gh`/`saved_features_root`/`saved_product_config` at lines 411-445). Proposing
  `unittest.mock.patch.object` here would add a second monkeypatch convention beside an
  established one for no anchoring benefit, and `unittest.mock` is not currently imported. Ruled
  out per shared-context: this pattern is anchoring semantics, not complexity added by this diff.
- **Comments narrating the change**: the two new prose blocks (lines 1185-1187, 1299-1303) read
  as present-tense design statements ("the scenario builder and predicate below are SHARED with
  5g," "this defends 5b's cache-bleed proof: it reddens if…") rather than diff narration ("we
  changed X to Y"). No instance found of a comment stating history instead of the present fact.

## Not touched
Nothing modified; this receipt is the only write.
