#!/usr/bin/env python3
"""Unit tests for check-plan-routes.py's pure census functions (FEAT-63 T-03, SC-04) and the
spawn-resource reader the reads lock uses (FEAT-62 SC-04 as taught `Ctx.spawn` by FEAT-63
T-02). The integration suite proves the LOCK through isolated mutants of the whole tree;
this suite proves the FUNCTIONS on in-memory sources -- what counts as a broad catch, what
a ceiling finding says, and which `git:`/`gh:` resource an argv reads as.

Loaded from CHECK_PLAN_ROUTES_BIN when set (mutation testing), else the sibling bin/.
Runnable directly with python3, no pytest.
"""
import ast
import os
import sys
import tempfile

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
BIN_DIR = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
SCRIPT = os.environ.get("CHECK_PLAN_ROUTES_BIN") or os.path.join(BIN_DIR, "check-plan-routes.py")
sys.path.insert(0, BIN_DIR)

failures = []


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'} {name} {'' if cond else detail}".rstrip())
    if not cond:
        failures.append(name)


def cpr():
    import importlib.util
    spec = importlib.util.spec_from_file_location("_census_under_test", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _count(mod, source):
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as fh:
        fh.write(source)
    try:
        return mod._broad_catch_count(fh.name)
    finally:
        os.unlink(fh.name)


def case_broad_catch_count_counts_exactly_the_two_syntaxes():
    """`except Exception` and bare `except:` count; a typed catch, a tuple, and a SUBCLASS of
    Exception do not -- the census is about the catch that hides bugs, not every handler."""
    mod = cpr()
    src = ("try:\n    pass\nexcept Exception:\n    pass\n"
           "try:\n    pass\nexcept:\n    pass\n"
           "try:\n    pass\nexcept OSError:\n    pass\n"
           "try:\n    pass\nexcept (OSError, ValueError):\n    pass\n"
           "try:\n    pass\nexcept RuntimeError as e:\n    pass\n")
    check("census counts except-Exception and bare except, and nothing typed", _count(mod, src) == 2)
    check("census counts a handler NESTED in a function or class",
          _count(mod, "class A:\n    def f(self):\n        try:\n            pass\n        except Exception:\n            pass\n") == 1)
    check("census of a clean file is zero", _count(mod, "x = 1\n") == 0)
    check("a file that does not parse counts as None (its own finding, never a pass)",
          _count(mod, "def (:\n") is None)


def case_broad_catch_finding_compares_a_file_to_its_own_ceiling():
    mod = cpr()
    ceiling = mod.BROAD_CATCH_CEILINGS["harness_boundary.py"]
    check("at the ceiling is clean", mod._broad_catch_finding("bin/harness_boundary.py", "harness_boundary.py", ceiling) is None)
    check("below the ceiling is clean (a reduction never fails the census)",
          mod._broad_catch_finding("bin/harness_boundary.py", "harness_boundary.py", ceiling - 1) is None)
    above = mod._broad_catch_finding("bin/harness_boundary.py", "harness_boundary.py", ceiling + 1)
    check("above the ceiling names the file and BOTH counts",
          above is not None and "bin/harness_boundary.py" in above and str(ceiling + 1) in above
          and f"ceiling {ceiling}" in above, above)
    check("check-state.py's ceiling is zero", mod.BROAD_CATCH_CEILINGS.get("check-state.py", 0) == 0)
    check("a script absent from the allowlist has a zero ceiling",
          mod._broad_catch_finding("bin/new.py", "new.py", 0) is None
          and "ceiling 0" in (mod._broad_catch_finding("bin/new.py", "new.py", 1) or ""))
    unparsed = mod._broad_catch_finding("bin/x.py", "x.py", None)
    check("an unparseable script is its own finding", unparsed is not None and "cannot parse" in unparsed, unparsed)


def case_feat64_wave4_ceilings_are_zero():
    """FEAT-64 (SC-04): the wave-4 libs and tools carry NO allowance -- absent from the table or
    explicitly zero -- and harness_boundary.py's two designed catches are the whole budget."""
    mod = cpr()
    for name in ("factory_decompose.py", "feature_schema.py", "gh_cost_log.py", "handoff_done_when.py",
                 "handoff_policy.py", "harness_yaml.py", "run_identity.py", "worktree_terminal.py",
                 "board-station.py", "check-omp-port.py", "check-plan-routes.py", "check-skill-weight.py",
                 "gh-sync.py", "post-merge-sweep.py", "run-unit-tests.py", "upgrade-config.py"):
        check(f"FEAT-64: {name} has a zero ceiling", mod.BROAD_CATCH_CEILINGS.get(name, 0) == 0,
              repr(mod.BROAD_CATCH_CEILINGS.get(name)))
    check("FEAT-64: harness_boundary.py's ceiling is exactly two",
          mod.BROAD_CATCH_CEILINGS.get("harness_boundary.py") == 2)
    check("FEAT-64: a third harness_boundary.py broad catch is a finding against two",
          "ceiling 2" in (mod._broad_catch_finding("bin/harness_boundary.py", "harness_boundary.py", 3) or ""))


_FEAT65_HOOKS = ("bash-write-guard.py", "branch-create-gate.py", "check-domain.py", "dispatch-guard.py",
                 "feature-record.py", "gh-close-gate.py", "inflight_registry.py", "inject-expertise.py",
                 "merge-gate.py", "plan-sign-gate.py", "validate-digest.py")
_FEAT65_PROLOGUES = ("branch-create-gate.py", "gh-close-gate.py", "merge-gate.py", "plan-sign-gate.py",
                     "run-unit-tests.py")


def case_feat65_hooks_have_no_allowance():
    """FEAT-65 (SC-04): the ceiling table is exactly harness_boundary.py's two designed catches;
    every hook is unlisted, so its ceiling is the default zero and one catch is a finding;
    the live census of all eleven hooks is zero and of harness_boundary.py exactly two."""
    mod = cpr()
    check("FEAT-65: the ceiling table is exactly {harness_boundary.py: 2}",
          mod.BROAD_CATCH_CEILINGS == {"harness_boundary.py": 2}, repr(mod.BROAD_CATCH_CEILINGS))
    for name in _FEAT65_HOOKS:
        finding = mod._broad_catch_finding(f"bin/{name}", name, 1) or ""
        check(f"FEAT-65: one broad catch in {name} is a finding against ceiling 0",
              name in finding and "ceiling 0" in finding and " 1 " in finding, finding)
        live = mod._broad_catch_count(os.path.join(BIN_DIR, name))
        check(f"FEAT-65: {name} carries zero broad catches", live == 0, repr(live))
    check("FEAT-65: harness_boundary.py carries exactly its two designed catches",
          mod._broad_catch_count(os.path.join(BIN_DIR, "harness_boundary.py")) == 2)
    check("FEAT-65: a third harness_boundary.py catch is a finding naming 3 against 2",
          " 3 " in (mod._broad_catch_finding("bin/harness_boundary.py", "harness_boundary.py", 3) or "")
          and "ceiling 2" in (mod._broad_catch_finding("bin/harness_boundary.py", "harness_boundary.py", 3) or ""))


def _prologue_source(path):
    """The `_resolve_root` function's exact source lines, comments included."""
    src = open(path, encoding="utf-8").read()
    node = next(n for n in ast.parse(src).body
                if isinstance(n, ast.FunctionDef) and n.name == "_resolve_root")
    return "\n".join(src.split("\n")[node.lineno - 1:node.end_lineno])


def _prologue_drift(sources):
    """Names of the copies whose text differs from run-unit-tests.py's, in order."""
    reference = sources["run-unit-tests.py"]
    return [name for name, text in sources.items() if text != reference]


def case_feat65_dec234_prologues_are_byte_identical():
    """FEAT-65 (SC-05): the five DEC-234 bootstrap copies are one text, comment and
    `(ModuleNotFoundError, ValueError)` tuple included; an independent mutation of any one
    copy is reported by name."""
    sources = {name: _prologue_source(os.path.join(BIN_DIR, name)) for name in _FEAT65_PROLOGUES}
    check("FEAT-65: the five DEC-234 prologues are byte-identical",
          _prologue_drift(sources) == [], repr(_prologue_drift(sources)))
    check("FEAT-65: the shared prologue catches exactly (ModuleNotFoundError, ValueError)",
          "except (ModuleNotFoundError, ValueError):" in sources["run-unit-tests.py"])
    for name in _FEAT65_PROLOGUES:
        mutated = dict(sources)
        mutated[name] = sources[name].replace("ValueError", "TypeError", 1)
        drift = _prologue_drift(mutated)
        others = [n for n in _FEAT65_PROLOGUES if n != name]
        expected = others if name == "run-unit-tests.py" else [name]
        check(f"FEAT-65: mutating {name}'s prologue alone is reported",
              drift == expected, repr(drift))


def _call(src):
    return next(n for n in ast.walk(ast.parse(src)) if isinstance(n, ast.Call))


def case_spawn_resource_reads_git_and_gh_through_run_and_spawn():
    """The reads lock names the RESOURCE, not the binary: `git show` is git:show, `worktree
    list` is git:worktree-list, `gh auth status` is gh:auth, a `gh api` endpoint is its last
    path segment, and the board module's query is gh:board. Both `subprocess.run` and the
    checker's own `ctx.spawn` are spawn callees (FEAT-63 T-01 moved every read behind spawn)."""
    mod = cpr()
    rows = (
        ('subprocess.run(["git", "-C", root, "show", f"{sha}:{p}"], capture_output=True)', "git:show"),
        ('ctx.spawn(["git", "-C", root, "status", "--porcelain=v1", "-z"], capture_output=True)', "git:status"),
        ('ctx.spawn(["git", "worktree", "list", "--porcelain"], cwd=root)', "git:worktree-list"),
        ('ctx.spawn([gh_bin, "auth", "status"], capture_output=True, text=True, timeout=15)', "gh:auth"),
        ('ctx.spawn([gh_bin, "api", "--paginate", "repos/%s/milestones?state=open" % repo, "-q", ".[].number"])',
         "gh:milestones"),
        ('gb.board_stations_for(board, repo, numbers)', "gh:board"),
        ('subprocess.run([sys.executable, script, root], text=True)', None),
        ('read(path)', None),
    )
    for src, want in rows:
        got = mod._spawn_resource(_call(src))
        check(f"spawn resource of `{src[:48]}` is {want}", got == want, f"got {got!r}")


def main():
    case_broad_catch_count_counts_exactly_the_two_syntaxes()
    case_broad_catch_finding_compares_a_file_to_its_own_ceiling()
    case_feat64_wave4_ceilings_are_zero()
    case_feat65_hooks_have_no_allowance()
    case_feat65_dec234_prologues_are_byte_identical()
    case_spawn_resource_reads_git_and_gh_through_run_and_spawn()
    if failures:
        print(f"\n{len(failures)} FAILURE(S): {failures}")
        return 1
    print("\nALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
