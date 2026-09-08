# SIMPLIFICATION angle — BUG-1480 — c0

**BLUF: zero findings. `_checkout_root` and its call site are already minimal; the reachability question resolves to UNREACHABLE, and that is the correct defensive shape, not dead code worth a DEC-174 edit.**

## Reachability of `_checkout_root`'s `if not path: return root` guard

`grep -n "shape_problems(" check-domain.sh` (excluding docstring/comment mentions at 1262, 1509, 1833/1841) finds exactly **one** call site: `check-domain.sh:2270-2271`, inside `for _rel, _text, _disp, _absolute in targets: _problems.extend(shape_problems(_rel, _text, display=_disp, absolute_path=_absolute))`. There is no other caller and no default-argument path — `shape_problems`'s `absolute_path=None` default is never exercised because every element of `targets` is a 4-tuple that always supplies the 4th slot positionally as `_absolute`.

Traced every place a `targets` tuple is built (its 4th element becomes `_absolute` → `absolute_path` → the argument passed into `_checkout_root`):

| Site | Branch | 4th element | Can it be falsy? |
|---|---|---|---|
| `check-domain.sh:2058` | PRE, Edit on run-identity path | `_claimed_abs(target)` | No — guarded by `and target` at :2056 |
| `check-domain.sh:2087` | PRE, Edit on digest/state-yaml/handoff path | `_claimed_abs(target)` | No — guarded by `and target` at :2059 |
| `check-domain.sh:2092` | PRE, Write | `_claimed_abs(target)` | No — reached only when `_tool == "Write" and target` (the `elif _tool != "Write" or not target: sys.exit(0)` at :2088 has already exited otherwise) |
| `check-domain.sh:2109` | POST, named file | `_claimed_abs(target)` | No — reached only inside `elif target:` at :2094 |
| `check-domain.sh:2232` | POST, Bash sweep (no named file) | `_p` from `_glob.glob(_pat)` | No — glob only yields paths to files that exist on disk |

`_claimed_abs` (check-domain.sh:334-351) also can't collapse a truthy `target` to a falsy return: `os.path.isabs(path)` is `False` for a non-empty relative string, and the join branch `os.path.join(root, path)` stays non-empty for any truthy `path`.

**Conclusion: the `if not path: return root` guard in `_checkout_root` is UNREACHABLE from the sole production call site**, on every one of the five ways a `targets` tuple gets built.

**Disposition: `defer`** (not `apply`). This is not the kind of dead code SIMPLIFICATION exists to trim: it is the same defensive shape `_norm` uses one function above it (both wrap the `harness_boundary` import in `try/except Exception`, both fall back to a safe default), and `_checkout_root:1151-1162`'s docstring states the deliberate design intent — "Absorb failures to keep shape non-gating." A guard that is unreachable *today*, from *this* call site, on a small pure helper that a future caller could reasonably invoke with an empty/None path, is exactly the kind of defensive shape the settled fallback-to-`root` anchor (check-domain.sh:1137-1139) calls for. Removing it would save one `if`/`return` pair at the cost of turning a currently-safe helper into one that raises or misbehaves the day a second caller (with a real empty-path possibility) is added — a net negative trade for a gate script whose stated first priority is "must never gain a fail-closed dependency." Not worth a DEC-174 edit.

## Other findings

None. Diff is minimal: `_checkout_root` (check-domain.sh:1151-1162, 12 lines) mirrors `_norm`'s existing `try/except`+`is not None`+`real(...) != real(...)` shape exactly, with no redundant conjunct — both the not-None check and the real-path inequality check are independently load-bearing (the first guards against `checkout_relative` returning nothing, the second distinguishes "same as root" from "a different checkout"). The one-line docstring states a present fact, not a narration of the change. The single changed call-site line (check-domain.sh:1761-1762) is a one-token argument swap (`root` → `_checkout_root(absolute_path)`), nothing to simplify.

Test addition (`_handoff_worktree_cases`, test-check-domain.py:4401-4440): checked each of the four rows against its stated distinct purpose — fixture precondition (main root lacks the feature dir), accepting row (T-03 pointer resolves), vacuity control (unresolvable pointer red both pre- and post-fix), and BRIEF.md-provenance row (SC-99 pointer refused, with the worktree-relative path fragment asserted in the failure detail). No row restates another's assertion; no dead reference to a removed shape; no narrating comment.

## Settled, not re-litigated
D-01 (standalone PR), D-03 (sibling-helper shape), the mandatory `try/except Exception` + fallback-to-`root`, the trailing-fragment needle, and the vacuity-control row's green-both-ways behavior — none flagged.
