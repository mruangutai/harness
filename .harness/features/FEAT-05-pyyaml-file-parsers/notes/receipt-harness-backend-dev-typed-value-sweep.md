# Receipt — the typed-value sweep (T-08 + T-17) — 2026-08-03

SC-10's single inspection evidence. **One file by design** (T-17): two receipts would let a
reviewer cite whichever half looks better.

Both halves were executed by the **main session**, not `harness-backend-dev`, under DEC-174 — the
harness plans changes to its own enforcement layer but does not execute them through a team run
whose gates are the thing being changed.

## The rule applied

`yaml.safe_load` returns TYPED values where the regexes it replaced returned strings. Every consumer
of a value from `harness_yaml.load_str` / `load_file` / `manifest_domains` is classified by use:

- used as a **path component, identifier, or dict key** → `str()` at the consumer;
- used as a **number** → stays typed (D-08).

## Files (T-08) — the readers

Every consumer of a value from `load_str` / `load_file` / `manifest_domains`, classified by use.
**Recounted at the post-F-02/F-03 state**, because both fixes added parse sites the first version
of this receipt predated — which is exactly why F-05 caught it at 10 rows against a required 14.

| # | file:line | value | use | handling |
|---|---|---|---|---|
| 1 | `check-state.sh:128-129` | any scalar via `val(k)` | identifier / comparison | `str(v)` at the boundary, `None` preserved |
| 2 | `check-state.sh:143` | `entry["id"]` | **path component** — joined into `runs/<id>` | `str(...).strip()` |
| 3 | `check-state.sh:144` | `entry["squad"]` | identifier, compared to `"validator"` | `str(...).strip()` |
| 4 | `check-state.sh:145` | `entry["verdict"]` | identifier, `.upper()`-compared to `"FAIL"` | `str(...).strip()` |
| 5 | `check-state.sh:151` | `cycles_used` | **numeric** | `val()` yields str, `.isdigit()` then `int()` — count stays numeric (D-08) |
| 6 | `check-state.sh:280` (F-02) | `phase` | enum, indexed into `PHASE_ORDER` | `str(...).strip()`, `isinstance` guard |
| 7 | `check-state.sh:344` (F-02) | `status` | enum, compared to `"complete"` | `str(...).strip()` — the quoted-value fail-open |
| 8 | `check-state.sh:348` (F-02) | `cost` | **presence only**, never a number | `"cost" not in sdoc` — no coercion needed |
| 9 | `check-state.sh:359-364` (F-02) | top-level keys | dict-key comparison vs `CHECKPOINT_KEYS` | `str(k)` both sides |
| 10 | `check-state.sh:367` (F-02) | `host` | identifier, membership in `LEADS` | `str(...).strip()` |
| 11 | `check-state.sh:471-475` (F-02) | `github.issues` | mapping presence | `isinstance` guards, no scalar use |
| 12 | `gh-sync.py:220` → `_opt_int` | `milestone`, `parent` | **numeric ids** | `_opt_int` excludes `bool` explicitly — an `int` subclass, so `parent: true` would become `1` |
| 13 | `gh-sync.py` `issues` loop | `T-NN` keys | dict keys, regex-matched | `str(k).strip()` before `re.fullmatch` |
| 14 | `gh-sync.py` `attached` | list entries | identifiers | `str(x).strip()`, list-or-CSV tolerated |
| 15 | `upgrade-config.py:108` | every `name:` at any depth | identifier | `isinstance(n, str)` guard, `.strip()` |
| 16 | `upgrade-config.py:133` | `schema_version` | **numeric** | typed `int` accepted; quoted string coerced; `bool` excluded |

**A real defect this caught, not a hypothetical.** `cycles_used: 6` parses to an `int`, and the
pre-existing line called `cu.isdigit()` on it — `AttributeError`. Demonstrated before the fix.

## Hooks (T-17)

The two scripts where a typed-value surprise **blocks or permits a write** rather than printing a
wrong number.

| # | file:line | value | use | handling |
|---|---|---|---|---|
| 17 | `check-domain.sh:134` → `:212,:215` | every glob from `manifest_domains` | **regex source** — reaches `re.escape`/`re.compile` | `str()` at the SOURCE, `harness_yaml.py:130,142` |
| 18 | `bash-write-guard.sh:287` → `:318-319` | same | same, via its own `glob_to_re` | same source coercion |
| 19 | `check-domain.sh:306` → `:315-316` | top-level keys of a parsed `state.yaml` | **dict-key comparison** vs `ALLOWED` | `str(k)` on BOTH sides |

**19 consumer sites, all classified.** The count is the complete output of
`grep -n 'harness_yaml\.\(load_str\|load_file\|manifest_domains\)'` over `bin/`, expanded to
each value the parse feeds.

### Regression 1 — a non-`str` glob reaching `re.escape`

Handled at the **source** rather than at each consumer: `manifest_domains` coerces with
`str(entry["path"])` at `harness_yaml.py:130` (own domain) and `:142` (shared). Both hooks therefore
receive `str` unconditionally, and neither can raise inside `re.compile`.

Coercing once at the producer is deliberate. Two consumers in two files, each with its own
`glob_to_re`, is exactly the divergence D-03 exists to remove — a coercion added at one consumer and
forgotten at the other is the same class of bug wearing a smaller hat.

**Why it matters here specifically:** a raise inside a fail-closed hook is not a wrong answer, it is
`exit 1`. And `exit 1` is NON-blocking (DEC-100), so the write would proceed with enforcement
silently off — a fail-open produced by a crash.

### Regression 2 — a YAML-truthy top-level key vs `ALLOWED`

`check-domain.sh:315-316`. YAML 1.1 resolves `on`, `off`, `yes`, `no`, `true`, `false` to booleans
and `01` to an int, so a parsed key is **not necessarily a string**. Verified:

```
load_str("on: 1\nno: 2\nrun_id: r1\n") -> keys [(True, 'bool'), (False, 'bool'), ('run_id', 'str')]
```

Two failures without coercion: a real key reported as unknown, and — with a bool key **beside** a
string key — `sorted()` over the mixed set raises `TypeError`, which is the `exit 1` fail-open above.

Covered by `test-check-domain.py`'s `a YAML-truthy key (on:) beside a string key denies cleanly, no
raise`, proven **RED against a deliberately un-coerced copy** (9/11) and green on the real hook
(11/11).

**The fixture needs TWO unknown keys, and that is not incidental.** A first draft used `on:` alone.
Its unknown set is the single element `{True}`, which sorts fine — so the test passed against the
un-coerced copy and proved nothing. Recorded because the fix (assert against a reverted copy) is
what exposed it, and the same trap has now appeared three times in this feature.

### Beyond the plan's two regressions

The denial message was also made actionable (DEC-100b). Naming the offending key as `True` when the
author typed `on:` is technically "named in the message" and practically useless — the reader cannot
find `True` in their file. The denial now adds:

```
NOTE — True (bool) came from an UNQUOTED key that YAML resolved to a non-string:
`on`/`off`/`yes`/`no`/`true`/`false` become booleans and `01` becomes an int (YAML 1.1).
Quote the key to keep it a string.
```

## Verification

- `run-unit-tests.sh` exit 0, 12 suites (T-04's mandated `test-upgrade-config.py` now exists — it
  never did, which is how F-03's NameError shipped).
- The T-17 assertion is discriminating in both directions, shown above.
- No consumer of a parsed value anywhere in `bin/` is left un-classified: 19 rows, recounted at the
  post-F-02/F-03 state.
- **F-05, the panel's own finding about this file, is why the recount happened.** T-17's verify
  requires >= 14 rows and the first version had 10 — it was written before F-02 and F-03 added parse
  sites, and a receipt that stops being true is worse than an absent one, because SC-10 rests on it.
