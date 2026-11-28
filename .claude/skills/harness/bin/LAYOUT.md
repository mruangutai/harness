# bin/ layout

How a `bin/` script splits into an entry and a package. What a script does lives in its docstring;
where a split lands and how its modules are named is the Layout section of the
harness-codebase-design skill, which this file does not restate.

| Entry | Package |
|---|---|
| `check-state.py` | `check_state/` |
| `feature-record.py` | `feature_record/` |
| (none, shared domain) | `github/` |
| `plan-merge.py` | `plan_merge/` |

- **Naming.** The entry keeps its hyphenated name and path, because callers, hooks and tests invoke
  it by path. The package takes the entry's importable underscore name, and its `__init__.py` is
  empty.
- **The entry.** It keeps its module docstring and its bootstrap, puts its own directory on
  `sys.path`, and imports from the package what it dispatches: `plan-merge.py` imports its `cmd_`
  functions from `plan_merge` modules. The entry parses and dispatches; the logic lives in the
  package.
- **Flat modules.** A flat `bin/` module that serves one package's domain moves into that package.
  Only a cross-cutting module that stands alone stays flat, such as `harness_boundary.py`.
- **Shared domains.** When several modules serve one domain that many entries use, they live in one
  package named for the domain, such as `github/`. The package has an empty `__init__.py` and no
  entry. Never use flat siblings that share a prefix. Prefix groups that predate this rule and have
  not moved yet: `digest_*`, `factory_*` and `handoff_*`.
