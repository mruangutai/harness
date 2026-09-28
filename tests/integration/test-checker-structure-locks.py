#!/usr/bin/env python3
"""Checker-structure locks that live in check-plan-routes.py but police bin/ as a whole.

FEAT-61 T-05 (station and loader locks), FEAT-62 T-02 (module-body, reads, authority and
--changed posture locks), FEAT-63 T-03 and FEAT-64 T-03 (broad-catch census). Each lock is
proven RED on an isolated mutant of a COPY of the tree and silent on the tree as shipped.

Split out of test-check-plan-routes.py so the test pool runs these whole-tree scans beside
the routing cases rather than behind them; none of them reads a plan.
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
import os
import shutil
import subprocess
import sys
import tempfile

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
BIN_DIR = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
SCRIPT = os.environ.get("CHECK_PLAN_ROUTES_BIN") or os.path.join(
    BIN_DIR, "check-plan-routes.py")
REPO_ROOT = os.path.abspath(os.path.join(BIN_DIR, "..", "..", "..", ".."))


def cpr():
    """The module UNDER TEST, loaded from SCRIPT — never from the repo copy.

    SCRIPT honours CHECK_PLAN_ROUTES_BIN, so during mutation testing the two are
    DIFFERENT FILES. An earlier case in this suite read the repo copy while the override
    pointed at a mutant and therefore reported ok against the broken build; anything here
    that needs a production constant must come through this function.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location("_cpr_under_test", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


failures = []


def run(*args, cwd=None, project_dir=None, script=None):
    """Invoke the checker. `project_dir` sets the root override; None UNSETS it.

    Unsetting is not cosmetic (case 19). Under a hook-invoked suite run the variable
    IS set to the repo, at which point a wrong-directory test would pass through the
    env var and prove nothing about the from-__file__ derivation it exists to check.

    BOTH NAMES, SET AND UNSET TOGETHER (FEAT-42 T-13). The checker now resolves through
    harness_boundary.resolve_root, which reads HARNESS_PROJECT_DIR and no other name, while
    the reverted sha-3952814 copy read HARNESS first and the host-owned name second. Clearing
    only one leaves the other set by whatever invoked this suite, and case 19's whole point is
    that NOTHING is set.
    """
    _OVERRIDES = ("CLAUDE_PROJECT_DIR", "HARNESS_PROJECT_DIR")
    env = {k: v for k, v in os.environ.items() if k not in _OVERRIDES}
    if project_dir is not None:
        for _k in _OVERRIDES:
            env[_k] = project_dir
    return subprocess.run(
        [sys.executable, script or SCRIPT, *args],
        cwd=cwd or REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
    )


def check(name, cond, detail=""):
    if cond:
        print(f"PASS {name}")
    else:
        print(f"FAIL {name} {detail}")
        failures.append(name)


def _consolidation_findings_for_tree(mutate=None):
    """Run `consolidation_findings` over a COPY of bin/ so a mutant never touches the live
    tree. `mutate(bin_dir)` edits the copy; None runs the tree as shipped."""
    with tempfile.TemporaryDirectory() as td:
        copy_bin = os.path.join(td, ".claude", "skills", "harness", "bin")
        shutil.copytree(BIN_DIR, copy_bin, ignore=shutil.ignore_patterns("__pycache__"))
        # FEAT-62's authority audit reads the decisions index and is LOUD without it — a bin/
        # copy alone is not a tree the audit can pass, so the index rides along.
        index_rel = os.path.join(".harness", "harness", "docs", "DECISIONS-INDEX.md")
        os.makedirs(os.path.dirname(os.path.join(td, index_rel)))
        shutil.copy(os.path.join(REPO_ROOT, index_rel), os.path.join(td, index_rel))
        if mutate is not None:
            mutate(copy_bin)
        return cpr().consolidation_findings(td)


def _append_to_gh_board(bin_dir, source):
    with open(os.path.join(bin_dir, "gh_board.py"), "a", encoding="utf-8") as stream:
        stream.write(source)


def _append_station_literal_mutant(bin_dir):
    # A predicate that respells the active bucket instead of calling is_active.
    _append_to_gh_board(bin_dir, '\n\ndef _mutant_is_live(station):\n'
                        '    return station in ("plan", "ready", "building", "review")\n')


def _append_drifted_bucket_mutant(bin_dir):
    # Validate c1 CR-01: a copied active bucket that has ALREADY drifted — `review` omitted.
    # A feature in review is classified inactive by this predicate, and an exact-set lock
    # never sees it. Also the finished bucket drifted to two names, assigned not compared.
    _append_to_gh_board(bin_dir, '\n\ndef _mutant_is_live(station):\n'
                        '    return station in ("plan", "ready", "building")\n'
                        '\n\n_MUTANT_OVER = frozenset({"done", "abandoned"})\n')


def _append_work_started_control(bin_dir):
    # D-11 negative control: the historical one-off spans both buckets and is NOT a respelling.
    _append_to_gh_board(bin_dir, '\n\ndef _control_work_started(statuses):\n'
                        '    return not set(statuses).isdisjoint({"building", "review", "done"})\n'
                        '\n\ndef _control_columns():\n'
                        '    return [k.capitalize() for k in ("ready", "building", "review")]\n')


def _append_second_loader_mutant(bin_dir):
    _append_to_gh_board(bin_dir, '\n\ndef _mutant_load(path):\n'
                        '    import importlib.util\n'
                        '    spec = importlib.util.spec_from_file_location("m", path)\n'
                        '    return spec\n')


def _mutant_findings(mutate, symbol, respelled):
    """Findings from a mutant, plus whether exactly one names `symbol` and `respelled`."""
    findings = _consolidation_findings_for_tree(mutate)
    own = [f for f in findings if symbol in f and respelled in f]
    return findings, len(findings) == len(own) and bool(own)


def case_feat61_station_lock():
    """FEAT-61 T-05 / SC-07, lock 1: the station lock passes on the shipped tree, fails on a
    bucket copied whole AND on one that has already drifted to a subset (validate c1 CR-01),
    and stays silent on the D-11 negative control — `_work_started`'s cross-bucket trio and a
    `for` over station keys.
    """
    clean = _consolidation_findings_for_tree()
    check("feat61_lock_clean_tree_has_no_findings", clean == [], "\n".join(clean))
    station, ok = _mutant_findings(_append_station_literal_mutant, "gh_board.py::_mutant_is_live",
                                   "respells factory_config.ACTIVE_STATIONS")
    check("feat61_lock_station_literal_mutant_fails_for_its_own_finding", ok, "\n".join(station))
    drifted = _consolidation_findings_for_tree(_append_drifted_bucket_mutant)
    check("feat61_lock_drifted_bucket_mutant_fails_for_both_partial_buckets",
          len(drifted) == 2
          and "gh_board.py::_mutant_is_live" in drifted[0]
          and "respells factory_config.ACTIVE_STATIONS" in drifted[0]
          and "gh_board.py::<module>" in drifted[1]
          and "respells factory_config.FINISHED_STATIONS" in drifted[1],
          "\n".join(drifted))
    control = _consolidation_findings_for_tree(_append_work_started_control)
    check("feat61_lock_d11_cross_bucket_predicate_and_key_iteration_are_not_flagged",
          control == [], "\n".join(control))


def case_feat61_loader_lock():
    """FEAT-61 T-05 / SC-07, lock 2: a second spec_from_file_location under bin/ fails for its
    own finding only, and the CLI reports the shipped tree clean at exit 0."""
    loader, ok = _mutant_findings(_append_second_loader_mutant, "gh_board.py::_mutant_load",
                                  "second spec_from_file_location")
    check("feat61_lock_second_loader_mutant_fails_for_its_own_finding", ok, "\n".join(loader))
    r = run("--consolidation-audit")
    check("feat61_lock_cli_reports_clean_and_exits_0",
          r.returncode == 0 and r.stdout.strip().endswith("0 consolidation finding(s) under bin/"),
          f"exit {r.returncode}: {r.stdout[-300:]!r} {r.stderr[-200:]!r}")


# ---------------------------------------------------------------------------------------------
# FEAT-62 T-02: the three checker-structure locks and the --changed posture scan, each proven
# RED on an isolated mutant of the tree and silent on the tree as shipped. Mutants edit a COPY
# that carries bin/, the decisions index, the workflows and the hooks — the four surfaces the
# FEAT-62 rules read — so no case touches the live tree.
_FEAT62_TREE_RELS = (
    os.path.join(".harness", "harness", "docs", "DECISIONS-INDEX.md"),
)
_FEAT62_TREE_DIRS = (
    os.path.join(".github", "workflows"),
    os.path.join(".claude", "skills", "harness", "hooks"),
)


def _feat62_findings_for_tree(mutate=None):
    """`feat62_findings` over a COPY of the surfaces it reads; `mutate(root)` edits the copy."""
    with tempfile.TemporaryDirectory() as td:
        copy_bin = os.path.join(td, ".claude", "skills", "harness", "bin")
        shutil.copytree(BIN_DIR, copy_bin, ignore=shutil.ignore_patterns("__pycache__"))
        for rel in _FEAT62_TREE_RELS:
            os.makedirs(os.path.dirname(os.path.join(td, rel)), exist_ok=True)
            shutil.copy(os.path.join(REPO_ROOT, rel), os.path.join(td, rel))
        for rel in _FEAT62_TREE_DIRS:
            shutil.copytree(os.path.join(REPO_ROOT, rel), os.path.join(td, rel))
        if mutate is not None:
            mutate(td)
        return cpr().feat62_findings(td)


def _checker_path(root, module=None):
    """The entry, or the check_state/<module>.py package file (FEAT-69)."""
    bin_dir = os.path.join(root, ".claude", "skills", "harness", "bin")
    return os.path.join(bin_dir, "check-state.py") if module is None else os.path.join(bin_dir, "check_state", module + ".py")


def _checker_files(root):
    """The entry then every package file, in name order (FEAT-69)."""
    package = os.path.join(root, ".claude", "skills", "harness", "bin", "check_state")
    return [_checker_path(root)] + sorted(os.path.join(package, n) for n in os.listdir(package) if n.endswith(".py"))


def _owning_checker_file(root, needle):
    """FEAT-69: the ONE checker source file whose text carries `needle` — a mutant edits the
    file that owns its anchor, wherever the split put it."""
    owners = [p for p in _checker_files(root) if needle in open(p, encoding="utf-8").read()]
    assert len(owners) == 1, f"mutant anchor {needle!r} owned by {len(owners)} file(s): {owners}"
    return owners[0]


def _edit_checker(root, old, new, count=1):
    path = _owning_checker_file(root, old)
    with open(path, encoding="utf-8") as stream:
        source = stream.read()
    assert source.count(old) >= count, f"mutant anchor {old!r} not found"
    with open(path, "w", encoding="utf-8") as stream:
        stream.write(source.replace(old, new, count))


def _append_checker(root, source, module=None):
    with open(_checker_path(root, module), "a", encoding="utf-8") as stream:
        stream.write(source)


def _only_finding(findings, *needles):
    own = [f for f in findings if all(n in f for n in needles)]
    return bool(own) and len(own) == len(findings)


_TABLE_HEAD = "\nINVARIANTS = ("

# Module-scope shapes injected before the table so the mutant still runs: (name, statement,
# the finding it must produce and nothing else).
_MODULE_BODY_MUTANTS = (
    ("loop", 'for _p in glob.glob(os.path.join(H, "*", "features", "*", "plan.yaml")):\n'
             '    if read(_p) is None:\n        pass\n', ("<module>", "for block at module scope")),
    ("conditional", 'if not os.path.isfile(os.path.join(H, "glossary.md")):\n    pass\n',
     ("conditional at module scope",)),
    # `except OSError`, not `except Exception`: the FEAT-63 broad-catch census would fire on the
    # latter too, and this mutant isolates the module-body rule.
    ("try", 'try:\n    _x = subprocess.run(["git", "status"], capture_output=True)\n'
            'except OSError:\n    _x = None\n', ("try block at module scope",)),
    ("read", '_early = read(os.path.join(H, "harness.json"))\n', ("reads the tree at module scope", "read")),
)


def _inject_before_table(statement):
    return lambda root: _edit_checker(root, _TABLE_HEAD, "\n" + statement + _TABLE_HEAD)


def case_feat62_module_body_lock():
    """SC-03: module-scope invariant execution is refused; the shipped tree passes."""
    clean = _feat62_findings_for_tree()
    check("feat62_clean_tree_has_no_findings", clean == [], "\n".join(clean))
    for name, statement, needles in _MODULE_BODY_MUTANTS:
        f = _feat62_findings_for_tree(_inject_before_table(statement))
        check(f"feat62_module_body_{name}_mutant_fails_for_its_own_finding",
              _only_finding(f, *needles), "\n".join(f))
    # Same family: an invariant body re-parsing a source the context already holds.
    def reparse(root):
        _edit_checker(root, "def inv_2(ctx, feat):\n    \"\"\"",
                      "def inv_2(ctx, feat):\n    _again = artifact_accessors.load_plan(ctx.path(feat, 'plan.yaml'))\n    \"\"\"")
    f = _feat62_findings_for_tree(reparse)
    # The reparse also OPENS plan.yaml undeclared, so the reads lock fires too — both are true.
    check("feat62_reparse_mutant_fails_for_its_own_finding",
          any(all(n in x for n in ("inv_2", "re-parses a runner-shared source", "load_plan")) for x in f)
          and all("inv_2" in x or "INV-2 " in x for x in f), "\n".join(f))


_INV19_HEAD = "def inv_19(ctx):\n"
_INV19_READS = '("path:.harness/glossary.md",)'
_PEEK = "    _peek = read(os.path.join(ctx.H, 'team-config.yaml'))\n"

# An undeclared input opened by INV-19's own body: (name, first statement, its finding).
_UNDECLARED_MUTANTS = (
    ("file", _PEEK, ("opens 'team-config.yaml'", "declares no path: read")),
    ("git", "    subprocess.run(['git', 'status'], capture_output=True)\n", ("reads git:status", "declares no git:status read")),
    ("gh", "    _gh_bin = 'gh'\n    subprocess.run([_gh_bin, 'auth', 'status'], capture_output=True)\n",
     ("reads gh:auth", "declares no gh:auth read")),
)

# A row whose declaration names the right BINARY but the wrong RESOURCE (GC-02): the lock
# matches the operation/endpoint, so a false declaration is a finding, not a pass.
_MISDECLARED_MUTANTS = (
    ("gh_board", '"gh:auth", "gh:board"', '"gh:auth"', ("INV-26", "reads gh:board", "declares no gh:board read")),
    ("gh_endpoint", '"gh:auth", "gh:milestones"', '"gh:auth", "gh:issues"',
     ("INV-30", "reads gh:milestones", "declares no gh:milestones read")),
    ("git_op", '"git:show", "git:log"', '"git:status", "git:log"', ("INV-33", "reads git:show", "declares no git:show read")),
)


def _misdeclared_resource_checks():
    for name, before, after, needles in _MISDECLARED_MUTANTS:
        f = _feat62_findings_for_tree(lambda root: _edit_checker(root, before, after))
        check(f"feat62_reads_misdeclared_{name}_resource_fails", _only_finding(f, *needles), "\n".join(f))


def _inv19_prefixed(statement):
    return lambda root: _edit_checker(root, _INV19_HEAD, _INV19_HEAD + statement)


def case_feat62_reads_lock():
    """SC-04: an input a function opens without declaring it — a file, a git spawn, a gh
    spawn — fails for its own finding; a declared one is silent."""
    for name, statement, needles in _UNDECLARED_MUTANTS:
        f = _feat62_findings_for_tree(_inv19_prefixed(statement))
        check(f"feat62_reads_undeclared_{name}_mutant_fails", _only_finding(f, "INV-19", *needles), "\n".join(f))
    _misdeclared_resource_checks()
    # Reached through a HELPER, not the row's own function: the lock walks the call graph.
    def via_helper(root):
        _append_checker(root, "\n\ndef _inv19_probe(ctx):\n    return read(os.path.join(ctx.H, 'team-config.yaml'))\n", "host")
        _edit_checker(root, _INV19_HEAD, _INV19_HEAD + "    _inv19_probe(ctx)\n")
    f = _feat62_findings_for_tree(via_helper)
    check("feat62_reads_lock_follows_helpers", _only_finding(f, "INV-19", "opens 'team-config.yaml'"), "\n".join(f))
    # And the negative control: the same read, DECLARED, is silent.
    def declared(root):
        _edit_checker(root, _INV19_HEAD, _INV19_HEAD + _PEEK)
        _edit_checker(root, _INV19_READS, '("path:.harness/glossary.md", "path:.harness/team-config.yaml")')
    f = _feat62_findings_for_tree(declared)
    check("feat62_reads_declared_input_is_silent", f == [], "\n".join(f))
    f = _feat62_findings_for_tree(lambda root: _edit_checker(root, _INV19_READS, '("glossary.md",)'))
    # An unprefixed declaration covers nothing, so the file it meant to declare is ALSO reported.
    check("feat62_reads_unprefixed_declaration_fails",
          any(all(n in x for n in ("INV-19", "not path:/git:/gh:")) for x in f)
          and all("INV-19" in x for x in f), "\n".join(f))


def case_feat62_authority_audit():
    """SC-05: a missing or STRUCK authority fails; every live row resolves."""
    def missing(root):
        _edit_checker(root, '"the domain\'s ubiquitous language is recorded (a note)", "DEC-162"',
                      '"the domain\'s ubiquitous language is recorded (a note)", "DEC-9999"')
    f = _feat62_findings_for_tree(missing)
    check("feat62_authority_missing_decision_fails",
          _only_finding(f, "INV-19", "DEC-9999", "does not resolve"), "\n".join(f))
    def struck(root):
        _edit_checker(root, '"the domain\'s ubiquitous language is recorded (a note)", "DEC-162"',
                      '"the domain\'s ubiquitous language is recorded (a note)", "DEC-90"')
    f = _feat62_findings_for_tree(struck)
    check("feat62_authority_struck_decision_fails",
          _only_finding(f, "INV-19", "DEC-90", "STRUCK", "DEC-188"), "\n".join(f))
    # Striking a decision the table stands on reddens the rows that cite it — the DEC-188
    # mechanism — proven by striking DEC-162 in the COPY's index.
    def strike_in_index(root):
        path = os.path.join(root, ".harness", "harness", "docs", "DECISIONS-INDEX.md")
        with open(path, encoding="utf-8") as stream:
            text = stream.read()
        line = next(l for l in text.splitlines() if l.startswith("- DEC-162 "))
        head, _, ruling = line.partition(" :: ")
        with open(path, "w", encoding="utf-8") as stream:
            stream.write(text.replace(line, f"{head} :: STRUCK 2026-09-21 under DEC-188 — {ruling}"))
    f = _feat62_findings_for_tree(strike_in_index)
    check("feat62_authority_striking_a_cited_decision_reddens_its_rows",
          _only_finding(f, "INV-19", "DEC-162", "STRUCK"), "\n".join(f))
    def no_index(root):
        os.remove(os.path.join(root, ".harness", "harness", "docs", "DECISIONS-INDEX.md"))
    f = _feat62_findings_for_tree(no_index)
    check("feat62_authority_unreadable_index_is_loud_not_silent",
          _only_finding(f, "CANNOT RUN", "DECISIONS-INDEX.md"), "\n".join(f))


def case_feat62_changed_posture():
    """SC-06: a workflow or hook invoking check-state.py --changed fails; the live tree has none
    and CI still runs the full checker."""
    def workflow(root):
        with open(os.path.join(root, ".github", "workflows", "tests.yml"), "a", encoding="utf-8") as stream:
            stream.write("\n      - run: python3 .claude/skills/harness/bin/check-state.py --changed\n")
    f = _feat62_findings_for_tree(workflow)
    check("feat62_posture_workflow_mutant_fails",
          _only_finding(f, "workflows/tests.yml", "--changed", "edit-loop verb"), "\n".join(f))
    def hook(root):
        with open(os.path.join(root, ".claude", "skills", "harness", "hooks", "post-merge"), "a",
                  encoding="utf-8") as stream:
            stream.write('\npython3 "$HARNESS_BIN/check-state.py" --changed\n')
    f = _feat62_findings_for_tree(hook)
    check("feat62_posture_hook_mutant_fails",
          _only_finding(f, "hooks/post-merge", "--changed"), "\n".join(f))
    with open(os.path.join(REPO_ROOT, ".github", "workflows", "tests.yml"), encoding="utf-8") as stream:
        wf = stream.read()
    check("feat62_posture_ci_runs_the_full_checker",
          "check-state.py" in wf and "--changed" not in wf, wf[:200])
    r = run("--consolidation-audit")
    check("feat62_cli_reports_clean_and_exits_0",
          r.returncode == 0 and r.stdout.strip().endswith("0 consolidation finding(s) under bin/"),
          f"exit {r.returncode}: {r.stdout[-300:]!r} {r.stderr[-200:]!r}")




# ------------------------------------------------------------------- FEAT-63 T-03 ---

def _bin_path(root, name):
    return os.path.join(root, ".claude", "skills", "harness", "bin", name)


def _append_bin(root, name, source):
    with open(_bin_path(root, name), "a", encoding="utf-8") as stream:
        stream.write(source)


def case_feat63_reparse_lock_covers_both_json_loaders():
    """SC-05: a checker re-parse of feature.json or harness.json inside an invariant is a
    shared-source-reparse finding, like load_plan's; the shipped tree is clean."""
    for loader, arg in (("load_feature_json", "ctx.path(feat, 'feature.json')"),
                        ("load_harness_json", "os.path.join(ctx.H, 'harness.json')")):
        def reparse(root, loader=loader, arg=arg):
            _edit_checker(root, "def inv_2(ctx, feat):\n    \"\"\"",
                          f"def inv_2(ctx, feat):\n    _again = artifact_accessors.{loader}({arg})\n    \"\"\"")
        f = _feat62_findings_for_tree(reparse)
        check(f"feat63_reparse_{loader}_mutant_fails_for_its_own_finding",
              any(all(n in x for n in ("inv_2", "re-parses a runner-shared source", loader)) for x in f)
              and all("inv_2" in x or "INV-2 " in x for x in f), "\n".join(f))


_BROAD_CATCH = "\n\ndef _feat63_mutant():\n    try:\n        pass\n    except Exception:\n        pass\n"
_BARE_CATCH = "\n\ndef _feat63_mutant():\n    try:\n        pass\n    except:\n        pass\n"


def _reduce_one_broad_catch(root):
    # FEAT-65: harness_boundary.py is the only script with an allowance left to reduce.
    path = _bin_path(root, "harness_boundary.py")
    src = open(path, encoding="utf-8").read()
    assert "except Exception" in src
    open(path, "w", encoding="utf-8").write(src.replace("except Exception", "except OSError", 1))


def _feat63_checker_ceiling_checks():
    """check-state.py's ceiling is zero: both syntaxes, each its own mutant, one finding each."""
    for name, source in (("except_exception", _BROAD_CATCH), ("bare_except", _BARE_CATCH)):
        f = _feat62_findings_for_tree(lambda root, s=source: _append_checker(root, s))
        check(f"feat63_census_checker_{name}_mutant_is_one_finding_naming_check_state",
              len(f) == 1 and "check-state.py" in f[0] and "broad catch" in f[0] and "ceiling 0" in f[0]
              and "1 " in f[0], "\n".join(f))


def _feat63_frozen_ceiling_checks():
    """The one script with an allowance (harness_boundary.py, FEAT-65): +1 fails naming THAT
    file and both counts; -1 is clean; allowance never transfers; an unlisted script — every
    hook is one now — has a zero ceiling."""
    f = _feat62_findings_for_tree(lambda root: _append_bin(root, "harness_boundary.py", _BROAD_CATCH))
    check("feat63_census_frozen_script_plus_one_is_one_finding_naming_it",
          len(f) == 1 and "harness_boundary.py" in f[0] and "check-state.py" not in f[0]
          and " 3 " in f[0] and "ceiling 2" in f[0], "\n".join(f))
    f = _feat62_findings_for_tree(_reduce_one_broad_catch)
    check("feat63_census_frozen_script_minus_one_is_clean", f == [], "\n".join(f))
    f = _feat62_findings_for_tree(lambda root: (_reduce_one_broad_catch(root),
                                                _append_bin(root, "gh-sync.py", _BROAD_CATCH)))
    check("feat63_census_allowance_never_transfers_between_files",
          len(f) == 1 and "gh-sync.py" in f[0], "\n".join(f))
    def newcomer(root):
        with open(_bin_path(root, "brand_new_helper.py"), "w", encoding="utf-8") as s:
            s.write("import os\n" + _BROAD_CATCH)
    f = _feat62_findings_for_tree(newcomer)
    check("feat63_census_unlisted_script_has_a_zero_ceiling",
          len(f) == 1 and "brand_new_helper.py" in f[0] and "ceiling 0" in f[0], "\n".join(f))


def _feat65_hook_ceiling_checks():
    """Every hook is unlisted now: one broad catch in any of them is a finding against zero."""
    f = _feat62_findings_for_tree(lambda root: _append_bin(root, "check-domain.py", _BROAD_CATCH))
    check("feat65_census_a_hook_plus_one_is_one_finding_against_ceiling_0",
          len(f) == 1 and "check-domain.py" in f[0] and " 1 " in f[0] and "ceiling 0" in f[0],
          "\n".join(f))


def case_feat63_broad_catch_census():
    """SC-04: ONE AST census over every bin script -- check-state.py at zero, every other
    script frozen at its recorded count; the shipped tree is clean."""
    clean = _feat62_findings_for_tree()
    check("feat63_census_clean_tree_has_no_findings", clean == [], "\n".join(clean))
    _feat63_checker_ceiling_checks()
    _feat63_frozen_ceiling_checks()
    _feat65_hook_ceiling_checks()


_FEAT64_ZEROED = ("factory_decompose.py", "feature_schema.py", "gh_cost_log.py", "handoff_done_when.py",
                  "handoff_policy.py", "harness_yaml.py", "run_identity.py", "worktree_terminal.py",
                  "board-station.py", "check-omp-port.py", "check-plan-routes.py", "check-skill-weight.py",
                  "gh-sync.py", "post-merge-sweep.py", "run-unit-tests.py", "upgrade-config.py")


def _feat64_ceiling_checks(mod):
    for name in _FEAT64_ZEROED:
        check(f"feat64_ceiling_{name}_is_zero", mod.BROAD_CATCH_CEILINGS.get(name, 0) == 0,
              f"ceiling {mod.BROAD_CATCH_CEILINGS.get(name)!r}")
    check("feat64_ceiling_harness_boundary_is_exactly_two",
          mod.BROAD_CATCH_CEILINGS.get("harness_boundary.py") == 2,
          f"ceiling {mod.BROAD_CATCH_CEILINGS.get('harness_boundary.py')!r}")


def _feat64_zero_ceiling_mutant_checks():
    """One new catch of either syntax in a lib and in a tool: one finding, naming that file,
    `1` against `ceiling 0`."""
    for family, name in (("lib", "handoff_policy.py"), ("tool", "gh-sync.py")):
        for syntax, source in (("except_exception", _BROAD_CATCH), ("bare_except", _BARE_CATCH)):
            f = _feat62_findings_for_tree(lambda root, n=name, s=source: _append_bin(root, n, s))
            check(f"feat64_census_{family}_{syntax}_mutant_is_one_finding_naming_{name}",
                  len(f) == 1 and name in f[0] and "broad catch" in f[0] and "ceiling 0" in f[0]
                  and " 1 " in f[0], "\n".join(f))


def case_feat64_broad_catch_census_wave4():
    """SC-04: the sixteen FEAT-64 files sit at a ZERO ceiling; harness_boundary.py's two designed
    catches hold at exactly two, so a third fails against two; a reduction elsewhere is clean."""
    _feat64_ceiling_checks(cpr())
    _feat64_zero_ceiling_mutant_checks()
    f = _feat62_findings_for_tree(lambda root: _append_bin(root, "harness_boundary.py", _BROAD_CATCH))
    check("feat64_census_third_harness_boundary_catch_fails_against_two",
          len(f) == 1 and "harness_boundary.py" in f[0] and "3 " in f[0] and "ceiling 2" in f[0],
          "\n".join(f))
    f = _feat62_findings_for_tree(_reduce_one_broad_catch)
    check("feat64_census_reduction_mutant_is_clean", f == [], "\n".join(f))


# ------------------------------------------------------------------- FEAT-69 T-02 ---
# The lock over the check_state/ PACKAGE: one function table across the entry and every
# package file, one transitive walk that follows `from check_state.<m> import` bindings and
# `ctx.<method>` calls, the four FEAT-62 rules over every file, the reads-family rule, and a
# zero broad-catch ceiling for every package file. Each mutant fails for ITS OWN finding.

_FEAT69_PACKAGE = ("__init__.py", "ctx.py", "table.py", "runner.py", "plan.py", "feature_record.py",
                   "run_state.py", "seams.py", "brief.py", "worktrees.py", "board.py", "host.py")
_INV47_HEAD = "def inv_47(ctx, feat):\n"


def _feat69_package_body_checks():
    """A module-body violation in a PACKAGE file (not the entry) is a finding naming that file."""
    f = _feat62_findings_for_tree(lambda root: _append_checker(
        root, "\nfor _p in glob.glob(os.path.join('x', 'plan.yaml')):\n    pass\n", "board"))
    check("feat69_module_body_rule_covers_a_package_file",
          _only_finding(f, "check_state/board.py::<module>", "for block at module scope"), "\n".join(f))


def _feat69_cross_module_checks():
    """An undeclared read reached ONLY through an imported helper (feature_record.inv_47 ->
    feature_record._note_verdict -> run_state._inv15_digest_verdict, two helpers deep, across a
    module boundary) is a finding on the row; a git spawn placed there is one too."""
    def deep_read(root):
        _edit_checker(root, "def _inv15_digest_verdict(",
                      "def _inv15_digest_verdict(*_a, **_k):\n    open('secret.yaml')\n"
                      "    return _inv15_digest_verdict_real(*_a, **_k)\n\n\ndef _inv15_digest_verdict_real(")
    f = _feat62_findings_for_tree(deep_read)
    check("feat69_reads_lock_follows_an_imported_helper_two_calls_deep",
          any(all(n in x for n in ("INV-47", "opens 'secret.yaml'")) for x in f)
          and all("opens 'secret.yaml'" in x for x in f), "\n".join(f))
    def deep_spawn(root):
        _edit_checker(root, "def _inv15_digest_verdict(",
                      "def _inv15_digest_verdict(*_a, **_k):\n    subprocess.run(['git', 'status'])\n"
                      "    return _inv15_digest_verdict_real(*_a, **_k)\n\n\ndef _inv15_digest_verdict_real(")
    f = _feat62_findings_for_tree(deep_spawn)
    check("feat69_reads_lock_sees_a_spawn_two_helpers_deep_across_modules",
          any(all(n in x for n in ("INV-47", "reads git:status")) for x in f)
          and all("reads git:status" in x for x in f), "\n".join(f))
    _feat69_ctx_method_check()


def _feat69_ctx_method_check():
    """A ctx METHOD reached through `ctx.<m>(...)` from a family module: the walk crosses into ctx.py."""
    def ctx_method(root):
        _edit_checker(root, "    def station(self, feat):\n",
                      "    def station(self, feat):\n        self.spawn(['gh', 'auth', 'status'])\n")
    f = _feat62_findings_for_tree(ctx_method)
    check("feat69_reads_lock_walks_into_ctx_methods_from_a_family",
          bool(f) and all("reads gh:auth" in x for x in f), "\n".join(f))


def _feat69_family_checks():
    """A row whose function is DEFINED outside the family its reads name fails; an import
    alias and an assignment alias are not definitions; a row no family claims fails."""
    def moved(root):
        _edit_checker(root, "from check_state.host import ", "from check_state.board import inv_19\nfrom check_state.host import ")
        _edit_checker(root, "inv_19, ", "")
        _append_checker(root, "\n\ndef inv_19(ctx):\n    return [], []\n", "board")
    f = _feat62_findings_for_tree(moved)
    check("feat69_row_defined_outside_its_family_fails",
          _only_finding(f, "INV-19", "defined in check_state/board.py", "check_state/host.py"), "\n".join(f))
    def alias(root):
        _edit_checker(root, "inv_19, ", "")
        _append_checker(root, "\ninv_19 = inv_42\n", "table")
    f = _feat62_findings_for_tree(alias)
    check("feat69_assignment_alias_is_not_a_definition",
          _only_finding(f, "INV-19", "not a function defined in the package"), "\n".join(f))
    def unclaimed(root):
        _edit_checker(root, 'Inv("INV-19", inv_19,', 'Inv("INV-99", inv_19,')
    f = _feat62_findings_for_tree(unclaimed)
    check("feat69_row_no_family_claims_fails",
          _only_finding(f, "INV-99", "belongs to no family"), "\n".join(f))


def _feat69_census_checks():
    """The broad-catch census enumerates the entry and the complete package (deterministic), and
    a catch injected into the entry or into a family module is one finding naming that file."""
    scanned = {name for _abs, name in cpr().broad_catch_census_paths(REPO_ROOT)}
    expected = {"check-state.py", *(os.path.join("check_state", n) for n in _FEAT69_PACKAGE)}
    check("feat69_census_scans_entry_and_every_package_file", expected <= scanned,
          f"missing {sorted(expected - scanned)}")
    f = _feat62_findings_for_tree(lambda root: _append_checker(root, _BROAD_CATCH))
    check("feat69_census_entry_broad_catch_is_one_finding_naming_check_state",
          len(f) == 1 and "bin/check-state.py" in f[0] and "ceiling 0" in f[0], "\n".join(f))
    f = _feat62_findings_for_tree(lambda root: _append_checker(root, _BROAD_CATCH, "plan"))
    check("feat69_census_family_broad_catch_is_one_finding_naming_the_module",
          len(f) == 1 and "check_state/plan.py" in f[0] and "ceiling 0" in f[0], "\n".join(f))


def case_feat69_package_lock():
    """FEAT-69 SC-03: the FEAT-62 lock walks the check_state/ package as one tree; the shipped
    package is clean; every mutant fails for its own finding."""
    clean = _feat62_findings_for_tree()
    check("feat69_clean_package_has_no_findings", clean == [], "\n".join(clean))
    _feat69_package_body_checks()
    _feat69_cross_module_checks()
    _feat69_family_checks()
    _feat69_census_checks()


CASES = (
    case_feat61_station_lock,
    case_feat61_loader_lock,
    case_feat62_module_body_lock,
    case_feat62_reads_lock,
    case_feat62_authority_audit,
    case_feat62_changed_posture,
    case_feat63_reparse_lock_covers_both_json_loaders,
    case_feat63_broad_catch_census,
    case_feat64_broad_catch_census_wave4,
    case_feat69_package_lock,
)


def main():
    for case in CASES:
        case()
    if failures:
        print(f"\n{len(failures)} FAILURE(S): {failures}")
        sys.exit(1)
    print("\nALL PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
