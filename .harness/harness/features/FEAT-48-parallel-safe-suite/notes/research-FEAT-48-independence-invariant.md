# Research — the independence invariant, prototyped and measured

Written at plan time so T-03 does not re-derive the rule set. The scope decisions in
`plan.yaml` T-03 are not preferences: each one is the answer to a measured false-positive
class, and a fourth variant would have been unusable.

## The finding: exactly three files violate, at ten sites

Scanning the three files at `ea6f51f` with the rule set T-03 specifies:

```
test-check-domain.py:1482   open('w')          <- the #1053 partner
test-check-domain.py:1489   open('wb')            (the restore)
test-check-state.py:2112    open('w')          <- .mutant-check-state-t14.sh
test-check-state.py:2114    shutil.copymode
test-check-state.py:2133    os.remove
test-check-state.py:2248    open('w')          <- .mutant-check-state-t10.sh
test-check-state.py:2250    shutil.copymode
test-check-state.py:2269    os.remove
test-feature-worktree.py:584 open('w')         <- .mutant-feature-worktree-behind.py
test-feature-worktree.py:605 os.remove
```

Every one is a true positive, and all three are the same shape: a probe that needs the
script under test to import its siblings, so it puts a mutant next to the original. T-01
and T-02 fix all ten with one helper. Nothing else in the tree — 56 test files at
`ea6f51f` — writes into the live checkout.

## Three rule variants, measured, and why the third is the one

| variant | findings | false positives |
|---|---|---|
| whole-file name taint | 47 | 37 — a function-local `tmp`, `path`, `fdir` in one function tainted the same name everywhere |
| per-scope taint, order-sensitive | 15 | 5 — 4 were `str.replace` on source read from `__file__`, 1 was `os.symlink` where only args[0] is live |
| + Path-typed receiver, + per-sink argument index | **10** | **0** |

The two refinements in the third row are therefore load-bearing, not polish:

- **Method sinks require a syntactically Path-typed receiver.** `src.replace(needle, "")` on
  text read from `__file__` appears in four mutation probes. A scanner that reads it as
  `Path.replace` reports four violations nobody can fix, and the invariant gets deleted.
- **The mutated argument differs per sink.** `os.symlink(live, fixture)` mutates args[1];
  `os.rename` mutates both; `shutil.copy*` mutates args[1]; `os.remove` mutates args[0].
  A uniform args[0] probe reports the sweep fixture's symlink source as a violation.

## Reference implementation

Proven against the tree above. T-03 should still write its cases first, but this is the
scanner it is specifying, so nobody has to re-invent the taint model.

```python
MUT_OS = {"remove", "unlink", "rename", "replace", "rmdir", "truncate", "utime",
          "chmod", "makedirs", "mkdir", "symlink", "link", "rmtree"}
MUT_SHUTIL = {"copy", "copy2", "copyfile", "copytree", "move", "rmtree", "copymode",
              "copystat"}
MUT_PATH = {"write_text", "write_bytes", "touch", "unlink", "rename", "mkdir",
            "replace", "rmdir", "chmod", "symlink_to", "hardlink_to"}

def mentions(node, tainted):
    return any(isinstance(n, ast.Name) and (n.id in tainted or n.id == "__file__")
               for n in ast.walk(node))

def path_typed(node):
    if isinstance(node, ast.Call):
        fn = node.func
        return ((isinstance(fn, ast.Name) and fn.id == "Path")
                or (isinstance(fn, ast.Attribute) and fn.attr == "Path"))
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        return path_typed(node.left) or path_typed(node.right)
    return False

def sink(call, tainted):
    f = call.func
    name = f.id if isinstance(f, ast.Name) else getattr(f, "attr", None)
    mod = f.value.id if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) else None
    args = call.args
    if name == "open":
        mode = args[1].value if len(args) > 1 and isinstance(args[1], ast.Constant) else None
        for k in call.keywords:
            if k.arg == "mode" and isinstance(k.value, ast.Constant):
                mode = k.value.value
        if mode and any(c in str(mode) for c in "wax+") and args and mentions(args[0], tainted):
            return "open(%r)" % mode
        return None
    if mod in ("os", "shutil") and name in (MUT_OS | MUT_SHUTIL):
        if name in ("copy", "copy2", "copyfile", "copytree", "move", "copymode",
                    "copystat", "symlink", "link"):
            probe = args[1:2]
        elif name in ("rename", "replace"):
            probe = args[:2]
        else:
            probe = args[:1]
        if any(mentions(a, tainted) for a in probe):
            return "%s.%s" % (mod, name)
        return None
    if (name in MUT_PATH and isinstance(f, ast.Attribute)
            and mentions(f.value, tainted) and path_typed(f.value)):
        return "Path.%s" % name
    return None
```

Taint: walk the module body in source order, adding every `Assign` target whose value
`mentions` the current set; that set seeds each function scope, and a function's own
bindings (added the same way, in order, including `with ... as` targets) never leave it.

## Every verify block was run against the pre-change tree

A verify that would have passed before the work proves nothing (#979). Measured
2026-08-31 in the FEAT-48 worktree at `ea6f51f`, before any task ran:

| task | exit | the output that makes it discriminating |
|---|---|---|
| T-01 | **1** | `bytes_equal True mtime_equal False crash_case 1 untouched_case 0` — the live module IS written today; the restore hides it from a bytes check but not from mtime |
| T-02 | **1** | `appeared ['.mutant-check-state-t10.sh', '.mutant-check-state-t14.sh', '.mutant-feature-worktree-behind.py']` — the poll sees all three mutants enter the live bin directory |
| T-03 | n/a | the guard does not exist yet; its historical half was proven with the prototype above: 10 findings, 3 files named, injection at `:1482` |
| T-04 | **1** | `test-run-pool.py` absent. Its `--check-kinds` and unknown-kind clauses already pass (exit 0, no PASS/FAIL line; exit 2) and are regression clauses only |
| T-05 | **1** | all four required tokens missing from `DECISIONS.md`; `index_drift False`, so the `--stdout` comparison works and would catch a stale index |

T-02's row is the positive control the whole feature rests on: it is the same technique
that proved the original hazard, and it can be re-run at any time.

Per-file timings taken at the same sha, for the sub-60s budget on those blocks:
`test-check-domain.py` 17.7s, `test-check-state.py` 24.9s, `test-feature-worktree.py` 6.1s.

## Open

- `subprocess` calls are NOT sinks. A test that shells out to `git -C <live tree> checkout`
  would mutate the tree and pass this scan. Deliberately out of scope: no such site exists
  today, and a sink model over argv strings has no precision worth having. If one appears,
  it is grounds to widen the rule, and this paragraph is the record that it was a choice.
