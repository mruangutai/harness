#!/usr/bin/env python3
"""Tests for the root resolver in harness_boundary.py (FEAT-42 T-01).

Covers MARKER and the three resolver functions:
  root_from_script  -- pure path arithmetic, zero filesystem access, zero env reads.
  resolve_root       -- reads HARNESS_PROJECT_DIR only, falls through to the derived root.
  root_above         -- the only one of the three permitted to see a cwd, walking up from it.

Fixtures are written under tempfile.mkdtemp() so no repo state is touched. Loaded via
importlib from BIN, honouring HARNESS_BOUNDARY_BIN so mutation testing can point this
suite at a different copy than the one it's run alongside (see test-check-plan-routes.py
cpr()).

Runnable directly with python3, no pytest.
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
import inflight_registry
import os
import json
import shutil
import sys
import tempfile
import time

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
BIN_DIR = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
SCRIPT = os.environ.get("HARNESS_BOUNDARY_BIN") or os.path.join(
    BIN_DIR, "harness_boundary.py")

failures = []


def check(name, cond, detail=""):
    if cond:
        print(f"PASS {name}")
    else:
        print(f"FAIL {name} {detail}")
        failures.append(name)


def hb():
    """The module UNDER TEST, loaded from SCRIPT — never a plain import.

    SCRIPT honours HARNESS_BOUNDARY_BIN so mutation testing can point this suite at a
    mutant copy distinct from the file sitting beside it.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location("_hb_under_test", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def write_marker(root):
    os.makedirs(os.path.join(root, ".harness"), exist_ok=True)
    with open(os.path.join(root, ".harness", "team-config.yaml"), "w") as fh:
        fh.write("teams: []\n")


# ============================== marker_constant ==============================

def case_marker_constant():
    mod = hb()
    check("marker_constant_exact_value",
          mod.MARKER == os.path.join(".harness", "team-config.yaml"),
          f"MARKER is {mod.MARKER!r}")


# ============================== root_from_script ==============================

def case_root_from_script():
    mod = hb()
    tmp = tempfile.mkdtemp()
    try:
        # four levels below tmp: tmp/a/b/c/bin
        bin_dir = os.path.join(tmp, "a", "b", "c", "bin")
        os.makedirs(bin_dir)
        got = mod.root_from_script(bin_dir)
        check("root_from_script_four_levels_up_no_marker", got == tmp,
              f"expected {tmp!r}, got {got!r}")

        write_marker(tmp)
        got2 = mod.root_from_script(bin_dir)
        check("root_from_script_unchanged_when_marker_exists", got2 == tmp,
              f"expected {tmp!r} (unchanged by marker presence), got {got2!r}; "
              "root_from_script must do ZERO filesystem checks")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ============================== resolve_root_strict ==============================

def case_resolve_root_strict():
    mod = hb()
    tmp_override = tempfile.mkdtemp()
    tmp_derived = tempfile.mkdtemp()
    old_env = os.environ.get("HARNESS_PROJECT_DIR")
    try:
        bin_dir = os.path.join(tmp_derived, "a", "b", "c", "bin")
        os.makedirs(bin_dir)

        # 1. override carries MARKER: honoured.
        write_marker(tmp_override)
        os.environ["HARNESS_PROJECT_DIR"] = tmp_override
        got = mod.resolve_root(bin_dir, strict=True)
        check("resolve_root_strict_override_with_marker_honoured",
              got == tmp_override, f"expected {tmp_override!r}, got {got!r}")

        # 2. override does NOT carry MARKER: discarded, falls through to derived root
        #    (which DOES carry MARKER here), discard reported on stderr.
        bare_override = tempfile.mkdtemp()
        write_marker(tmp_derived)
        os.environ["HARNESS_PROJECT_DIR"] = bare_override
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            got2 = mod.resolve_root(bin_dir, strict=True)
        check("resolve_root_strict_bad_override_falls_through_to_derived",
              got2 == tmp_derived, f"expected {tmp_derived!r}, got {got2!r}")
        stderr_out = buf.getvalue()
        check("resolve_root_strict_bad_override_reported_on_stderr",
              bare_override in stderr_out and tmp_derived in stderr_out,
              f"stderr did not name both candidates: {stderr_out!r}")
        shutil.rmtree(bare_override, ignore_errors=True)

        # 3. neither carries MARKER: raises ValueError naming both candidates.
        no_marker_override = tempfile.mkdtemp()
        no_marker_derived_bin = os.path.join(tempfile.mkdtemp(), "x", "y", "z", "bin")
        os.makedirs(no_marker_derived_bin)
        no_marker_derived_root = os.path.abspath(
            os.path.join(no_marker_derived_bin, "..", "..", "..", ".."))
        os.environ["HARNESS_PROJECT_DIR"] = no_marker_override
        raised = None
        try:
            mod.resolve_root(no_marker_derived_bin, strict=True)
        except ValueError as e:
            raised = e
        check("resolve_root_strict_neither_carries_marker_raises",
              raised is not None
              and no_marker_override in str(raised)
              and no_marker_derived_root in str(raised),
              f"expected ValueError naming both candidates, got {raised!r}")
        shutil.rmtree(no_marker_override, ignore_errors=True)
    finally:
        if old_env is None:
            os.environ.pop("HARNESS_PROJECT_DIR", None)
        else:
            os.environ["HARNESS_PROJECT_DIR"] = old_env
        shutil.rmtree(tmp_override, ignore_errors=True)
        shutil.rmtree(tmp_derived, ignore_errors=True)


# ==================== resolve_root_override_normalises_relative ====================

def case_resolve_root_override_normalises_relative():
    """A marker-carrying override must resolve to the SAME absolute path whether it
    is spelled absolute or relative — resolve_root's other return path already goes
    through os.path.abspath via root_from_script, so a bare relative override is the
    one path that used to return non-normalised (e.g. '.')."""
    mod = hb()
    tmp_override = tempfile.mkdtemp()
    tmp_derived = tempfile.mkdtemp()
    old_env = os.environ.get("HARNESS_PROJECT_DIR")
    old_cwd = os.getcwd()
    try:
        write_marker(tmp_override)
        bin_dir = os.path.join(tmp_derived, "a", "b", "c", "bin")
        os.makedirs(bin_dir)

        os.environ["HARNESS_PROJECT_DIR"] = tmp_override
        absolute_got = mod.resolve_root(bin_dir, strict=True)

        parent = os.path.dirname(tmp_override)
        rel = os.path.relpath(tmp_override, parent)
        os.chdir(parent)
        os.environ["HARNESS_PROJECT_DIR"] = rel
        relative_got = mod.resolve_root(bin_dir, strict=True)

        # realpath, not just abspath, on both sides for the comparison: on macOS
        # os.getcwd() after os.chdir() resolves /tmp's symlink to /private/tmp, so a
        # literal-string compare against mkdtemp()'s unresolved path would fail on an
        # OS artifact unrelated to resolve_root's own normalisation, which is what
        # this case exists to check.
        check("resolve_root_override_relative_normalises_to_same_absolute_path",
              os.path.realpath(relative_got) == os.path.realpath(absolute_got)
              and os.path.isabs(relative_got),
              f"absolute override -> {absolute_got!r}, relative override -> {relative_got!r}")
    finally:
        os.chdir(old_cwd)
        if old_env is None:
            os.environ.pop("HARNESS_PROJECT_DIR", None)
        else:
            os.environ["HARNESS_PROJECT_DIR"] = old_env
        shutil.rmtree(tmp_override, ignore_errors=True)
        shutil.rmtree(tmp_derived, ignore_errors=True)


# ============================== root_above ==============================

def case_root_above():
    mod = hb()
    tmp = tempfile.mkdtemp()
    try:
        write_marker(tmp)
        start = os.path.join(tmp, "sub1", "sub2", "sub3")
        os.makedirs(start)
        got = mod.root_above(start)
        check("root_above_finds_marker_walking_up", got == tmp,
              f"expected {tmp!r}, got {got!r}")

        # a start point below a directory NAMED .harness that has NO team-config.yaml
        # must NOT return it, and must keep walking to the real marker-carrying root
        # above it -- the $HOME/.harness fail-open this function exists to close.
        bare_harness_dir = os.path.join(tmp, "sub1", ".harness")
        os.makedirs(bare_harness_dir, exist_ok=True)
        start2 = os.path.join(bare_harness_dir, "deep")
        os.makedirs(start2)
        got2 = mod.root_above(start2)
        check("root_above_bare_dot_harness_does_not_satisfy", got2 == tmp,
              f"expected the real marker root {tmp!r} (walking past the bare "
              f".harness dir), got {got2!r}")

        # nothing above -> None
        tmp_no_marker = tempfile.mkdtemp()
        start3 = os.path.join(tmp_no_marker, "x", "y", "z")
        os.makedirs(start3)
        got3 = mod.root_above(start3)
        check("root_above_nothing_above_returns_none", got3 is None,
              f"expected None, got {got3!r}")
        shutil.rmtree(tmp_no_marker, ignore_errors=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def make_worktree(mod, owner_root, name):
    """A linked-worktree fixture: `<owner_root>/wt/<name>` as the checkout, wired to
    `owner_root` with the two-sided gitdir pointer pair -- the worktree's own `.git`
    FILE naming the owner's `.git/worktrees/<name>` entry, and that entry's `gitdir`
    file naming the worktree's `.git` back -- which is the on-disk shape `git worktree
    add` leaves and the one `linked_worktrees` reads. Returns the realpath-resolved
    checkout dir, exactly what `linked_worktrees`/`worktree_for_feature` return.
    """
    path = os.path.join(owner_root, "wt", name)
    entry = os.path.join(owner_root, ".git", "worktrees", name)
    os.makedirs(path)
    os.makedirs(entry)
    with open(os.path.join(path, ".git"), "w") as fh:
        fh.write("gitdir: %s\n" % entry)
    with open(os.path.join(entry, "gitdir"), "w") as fh:
        fh.write("%s\n" % os.path.join(path, ".git"))
    return mod.real(path)


def write_claims(root, claims):
    path = os.path.join(root, inflight_registry.REGISTRY_REL)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump({"schema_version": inflight_registry.SCHEMA_VERSION,
                   "claims": claims}, handle)
    return path


def live_claim(agent, feature):
    return {
        "agent": agent,
        "dispatcher": "harness-orchestrator",
        "cwd": "/fixture",
        "feature": feature,
        "runtime": "omp",
        "supervisor_pid": os.getpid(),
        "started_at": time.time(),
    }


# ============================== worktree_for_feature ==============================

def case_worktree_for_feature():
    mod = hb()

    tmp = tempfile.mkdtemp()
    try:
        short = make_worktree(mod, tmp, "FEAT-X")

        check("worktree_for_feature_exact_basename_match",
              mod.worktree_for_feature(tmp, "FEAT-X") == short,
              f"expected {short!r}, got {mod.worktree_for_feature(tmp, 'FEAT-X')!r}")

        check("worktree_for_feature_short_form_prefix_match",
              mod.worktree_for_feature(tmp, "FEAT-X-thing") == short,
              f"expected {short!r}")

        check("worktree_for_feature_unrelated_id_returns_none",
              mod.worktree_for_feature(tmp, "FEAT-Y-other") is None,
              "expected None for an id no worktree prefixes")

        # Look the LONGER id up against the SHORTER basename: FEAT-XY must NOT match
        # a FEAT-X worktree. Under the correct "equal, or prefix + hyphen" rule this
        # is None (neither an exact match nor a FEAT-X-<rest> match). Under the
        # boundary-less bug `feature_id.startswith(basename)` (dropping the "-"),
        # "FEAT-XY".startswith("FEAT-X") is True and it would wrongly return short.
        check("worktree_for_feature_hyphen_boundary_not_crossed",
              mod.worktree_for_feature(tmp, "FEAT-XY") is None,
              "a FEAT-X worktree must not match a FEAT-XY lookup")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    tmp2 = tempfile.mkdtemp()
    try:
        make_worktree(mod, tmp2, "FEAT-X")
        make_worktree(mod, tmp2, "FEAT")
        raised = None
        try:
            mod.worktree_for_feature(tmp2, "FEAT-X-thing")
        except mod.AmbiguousWorktree as e:
            raised = e
        check("worktree_for_feature_two_candidates_raises_ambiguous",
              raised is not None and "FEAT, FEAT-X" in str(raised),
              f"expected AmbiguousWorktree naming both FEAT and FEAT-X, got {raised!r}")
    finally:
        shutil.rmtree(tmp2, ignore_errors=True)

    tmp3 = tempfile.mkdtemp()
    try:
        raised3 = None
        result3 = "unset"
        try:
            result3 = mod.worktree_for_feature(tmp3, "FEAT-X")
        except Exception as e:
            raised3 = e
        check("worktree_for_feature_no_worktrees_dir_returns_none",
              raised3 is None and result3 is None,
              f"expected None with no raise when .git/worktrees is absent, "
              f"got result={result3!r} raised={raised3!r}")
    finally:
        shutil.rmtree(tmp3, ignore_errors=True)


# ============================== FEAT-61 T-01: checkout predicate ==============================

def _raises(fn, exc_type):
    """The exception `fn()` raises when it is an `exc_type`, else None."""
    try:
        fn()
    except exc_type as e:
        return e
    return None


def _fake_checker(root, script):
    """A stand-in check-state.py at the derived checkout: the adapter must find it by the
    written path alone, so the fixture is a whole (marker + checker) tree under /tmp."""
    write_marker(root)
    bin_dir = os.path.join(root, ".claude", "skills", "harness", "bin")
    os.makedirs(bin_dir, exist_ok=True)
    with open(os.path.join(bin_dir, "check-state.py"), "w") as fh:
        fh.write(script)


_PROBE_CHECKER = (
    "import os, sys\n"
    "sys.stdout.write('FAIL INV-3 something\\n')\n"
    "sys.stderr.write('warn row\\n')\n"
    "sys.stdout.write(f'argv={sys.argv[1:]} cwd={os.getcwd()} "
    "env={os.environ.get(\"HARNESS_PROJECT_DIR\")!r} "
    "nested={os.environ.get(\"HARNESS_CHANGED_FEEDBACK\")!r}\\n')\n"
    "sys.exit(1)")


def _changed_state_root_checks(mod, tmp):
    plan = os.path.join(tmp, ".harness", "harness", "features", "FEAT-7-x", "plan.yaml")
    flat = os.path.join(tmp, ".harness", "features", "BUG-7-x", "feature.json")
    check("changed_state_root: canonical repo-tier plan.yaml derives the checkout",
          mod.changed_state_root(plan) == tmp, mod.changed_state_root(plan))
    check("changed_state_root: canonical flat feature.json derives the checkout",
          mod.changed_state_root(flat) == tmp, mod.changed_state_root(flat))
    for other in (os.path.join(tmp, "scratch", "plan.yaml"),
                  os.path.join(tmp, ".harness", "harness", "features", "notes", "plan.yaml"),
                  os.path.join(tmp, ".harness", "harness", "features", "FEAT-7-x", "BRIEF.md")):
        check(f"changed_state_root: {os.path.relpath(other, tmp)} derives NO checkout",
              mod.changed_state_root(other) is None, mod.changed_state_root(other))
    return plan


def _with_env(key, value, fn):
    os.environ[key] = value
    try:
        return fn()
    finally:
        del os.environ[key]


def _changed_state_spawn_checks(mod, tmp, elsewhere, plan):
    """The spawn itself: which checker, in which cwd, with which environment."""
    _fake_checker(tmp, _PROBE_CHECKER)
    rows = _with_env("HARNESS_PROJECT_DIR", elsewhere, lambda: mod.changed_state_feedback(plan))
    check("feedback forwards BOTH streams' rows from the derived checkout's checker",
          "FAIL INV-3 something" in rows and "warn row" in rows, rows)
    detail = [r for r in rows if r.startswith("argv=")]
    check("the checker is spawned with --changed, in the derived checkout, WITHOUT the "
          "session's HARNESS_PROJECT_DIR, and marked nested",
          len(detail) == 1 and "argv=['--changed']" in detail[0]
          and f"cwd={os.path.realpath(tmp)}" in os.path.realpath(detail[0].split(" env=")[0])
          and "env=None" in detail[0] and "nested='1'" in detail[0], detail)


def case_changed_state_feedback():
    """FEAT-62 T-03: the feedback loop derives its checkout from the WRITTEN PATH, spawns that
    checkout's own checker with --changed, and hands back whatever the checker said."""
    mod = hb()
    tmp, elsewhere = tempfile.mkdtemp(), tempfile.mkdtemp()
    try:
        plan = _changed_state_root_checks(mod, tmp)
        # No checker at the derived checkout: silent, whatever the environment says.
        _fake_checker(elsewhere, "import sys; sys.stdout.write('WRONG TREE\\n')")
        silent = _with_env("HARNESS_PROJECT_DIR", elsewhere, lambda: mod.changed_state_feedback(plan))
        check("feedback is silent when the derived checkout carries no checker, even with "
              "HARNESS_PROJECT_DIR pointing at one (PF-e27f2ac2)", silent == [], silent)
        _changed_state_spawn_checks(mod, tmp, elsewhere, plan)
        nested = _with_env("HARNESS_CHANGED_FEEDBACK", "1", lambda: mod.changed_state_feedback(plan))
        check("a writer inside a feedback run never re-enters the loop", nested == [], nested)
        _fake_checker(tmp, "")
        check("a clean --changed run (no output) yields no rows",
              mod.changed_state_feedback(plan) == [], mod.changed_state_feedback(plan))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        shutil.rmtree(elsewhere, ignore_errors=True)

def case_feature_artifact_checkout_mismatch():
    """The ONE checkout question both write routes ask (check-domain's tool route and
    bash-write-guard's Bash route). It decides; the adapters refuse in their own voice."""
    mod = hb()
    tmp = tempfile.mkdtemp()
    try:
        wt = make_worktree(mod, tmp, "FEAT-X")
        rel = ".harness/harness/features/FEAT-X-thing/BRIEF.md"
        other = ".harness/harness/features/FEAT-Y-other/BRIEF.md"
        check("checkout_mismatch_non_feature_path_is_none",
              mod.feature_artifact_checkout_mismatch(tmp, "docs/README.md", os.path.join(tmp, "docs/README.md")) is None)
        check("checkout_mismatch_no_worktree_for_feature_is_none",
              mod.feature_artifact_checkout_mismatch(tmp, other, os.path.join(tmp, other)) is None)
        check("checkout_mismatch_correct_checkout_is_none",
              mod.feature_artifact_checkout_mismatch(tmp, rel, os.path.join(wt, rel)) is None)
        got = mod.feature_artifact_checkout_mismatch(tmp, rel, os.path.join(tmp, rel))
        check("checkout_mismatch_wrong_checkout_names_feature_and_expected_worktree",
              got == ("FEAT-X-thing", wt), f"got {got!r}")
        check("feature_artifact_id_extracts_the_feature_segment",
              mod.feature_artifact_id(rel) == "FEAT-X-thing"
              and mod.feature_artifact_id("tests/x.py") is None)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def case_feature_artifact_checkout_mismatch_ambiguous():
    mod = hb()
    tmp = tempfile.mkdtemp()
    try:
        make_worktree(mod, tmp, "FEAT-X")
        make_worktree(mod, tmp, "FEAT")
        raised = _raises(lambda: mod.feature_artifact_checkout_mismatch(
            tmp, ".harness/harness/features/FEAT-X-thing/BRIEF.md", os.path.join(tmp, "x")),
            mod.AmbiguousWorktree)
        check("checkout_mismatch_lets_ambiguous_worktree_reach_the_adapter",
              raised is not None and "FEAT, FEAT-X" in str(raised), f"got {raised!r}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ============================== FEAT-61 T-01: load_repo_module ==============================

def _script(tmp, name, body):
    path = os.path.join(tmp, name)
    with open(path, "w") as fh:
        fh.write(body)
    return path


def case_load_repo_module_registration():
    """The sole spec_from_file_location in bin/. Six hand-written copies disagreed on
    sys.modules registration; this one owns the decision."""
    mod = hb()
    tmp = tempfile.mkdtemp()
    try:
        good = _script(tmp, "good-script.py",
                       "import sys\nVALUE = 7\nSEEN = 'fixture_reg' in sys.modules\n")
        loaded = mod.load_repo_module("fixture_unreg", good)
        check("load_repo_module_executes_and_returns_the_module",
              getattr(loaded, "VALUE", None) == 7)
        check("load_repo_module_default_does_not_register",
              "fixture_unreg" not in sys.modules)
        registered = mod.load_repo_module("fixture_reg", good, register=True)
        check("load_repo_module_register_true_is_visible_during_exec",
              getattr(registered, "SEEN", None) is True,
              "dataclasses resolve their module by name DURING exec — registration must precede it")
        check("load_repo_module_register_true_stays_registered_after_exec",
              sys.modules.get("fixture_reg") is registered)
        del sys.modules["fixture_reg"]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _repo_module_error(mod, fn):
    """The RepoModuleError `fn` raises, or the foreign exception it let through, or None."""
    try:
        fn()
    except mod.RepoModuleError as error:
        return error
    except BaseException as other:  # the test wants to SEE a wrong type, not die on it
        return other
    return None


def _check_wrapped(mod, name, fn, cause_type, module_name, path):
    """One load failure: it reaches the caller as RepoModuleError carrying the module name, the
    path and the original exception, both as structured data and as the chained cause."""
    error = _repo_module_error(mod, fn)
    check(f"load_repo_module_{name}_is_RepoModuleError",
          isinstance(error, mod.RepoModuleError), f"got {error!r}")
    if not isinstance(error, mod.RepoModuleError):
        return
    check(f"load_repo_module_{name}_carries_name_path_and_cause",
          error.module_name == module_name and error.path == path
          and isinstance(error.cause, cause_type) and error.__cause__ is error.cause,
          f"name={error.module_name!r} path={error.path!r} cause={error.cause!r}")
    check(f"load_repo_module_{name}_renders_the_original_type_and_text",
          type(error.cause).__name__ in str(error) and str(error.cause) in str(error), str(error))


def _check_process_control_passes_through(mod, tmp):
    """Process control is NOT a load failure: it propagates unchanged, and the registration
    made for the attempt is still undone."""
    for name, stmt, kind in (("keyboard_interrupt", "raise KeyboardInterrupt()", KeyboardInterrupt),
                             ("system_exit", "raise SystemExit(3)", SystemExit)):
        script = _script(tmp, f"{name}.py", stmt + "\n")
        got = _repo_module_error(mod, lambda: mod.load_repo_module(f"fixture_{name}", script, register=True))
        check(f"load_repo_module_{name}_propagates_unchanged", type(got) is kind, f"got {got!r}")
        check(f"load_repo_module_{name}_still_undoes_its_registration", f"fixture_{name}" not in sys.modules)


def _check_registration_restored(mod, bad):
    sentinel = object()
    sys.modules["fixture_preexisting"] = sentinel
    _repo_module_error(mod, lambda: mod.load_repo_module("fixture_preexisting", bad, register=True))
    check("load_repo_module_exec_failure_restores_a_prior_registration",
          sys.modules.get("fixture_preexisting") is sentinel)
    del sys.modules["fixture_preexisting"]


def _check_by_name_and_call(mod):
    """By NAME: the ordinary import, with the same one type for a failure. A CALL into a
    sibling: its own exceptions become RepoModuleError, process control does not."""
    check("load_repo_module_by_name_imports_through_sys_path",
          mod.load_repo_module("json") is __import__("json"))
    _check_wrapped(mod, "by_name_absent", lambda: mod.load_repo_module("no_such_module_fixture_63"),
                   ImportError, "no_such_module_fixture_63", None)
    import types
    sib = types.ModuleType("fixture_sibling"); sib.__file__ = "/x/fixture_sibling.py"
    sib.boom = lambda: (_ for _ in ()).throw(KeyError("k")); sib.quit = lambda: (_ for _ in ()).throw(SystemExit(4))
    sib.fine = lambda a, b=1: a + b
    _check_wrapped(mod, "call_failure", lambda: mod.call_repo_module(sib, "boom"),
                   KeyError, "fixture_sibling", "/x/fixture_sibling.py")
    check("call_repo_module_passes_process_control_through",
          type(_repo_module_error(mod, lambda: mod.call_repo_module(sib, "quit"))) is SystemExit)
    check("call_repo_module_returns_the_result", mod.call_repo_module(sib, "fine", 2, b=3) == 5)


def case_load_repo_module_failures():
    """FEAT-63 T-01 (D-02): every Exception raised while loading a repo module -- spec creation,
    the loader's own I/O, registered or unregistered execution -- reaches the caller as ONE
    typed RepoModuleError; process-control signals pass through untouched; a failed
    registered exec undoes only its own registration."""
    mod = hb()
    tmp = tempfile.mkdtemp()
    try:
        bad = _script(tmp, "bad-script.py", "raise RuntimeError('boom at import')\n")
        absent = os.path.join(tmp, "absent.py")
        wrapped = (
            ("registered_exec_failure", lambda: mod.load_repo_module("fixture_bad", bad, register=True),
             RuntimeError, "fixture_bad", bad),
            ("unregistered_exec_failure", lambda: mod.load_repo_module("fixture_bad2", bad),
             RuntimeError, "fixture_bad2", bad),
            ("missing_file", lambda: mod.load_repo_module("fixture_missing", absent),
             FileNotFoundError, "fixture_missing", absent),
            ("no_loader", lambda: mod.load_repo_module("fixture_dir", tmp), ImportError, "fixture_dir", tmp),
        )
        for row in wrapped:
            _check_wrapped(mod, *row)
        check("load_repo_module_exec_failure_removes_only_its_own_registration",
              "fixture_bad" not in sys.modules)
        _check_registration_restored(mod, bad)
        _check_process_control_passes_through(mod, tmp)
        ok = _script(tmp, "ok.py", "VALUE = 7\n")
        check("load_repo_module_success_is_unchanged", mod.load_repo_module("fixture_ok", ok).VALUE == 7)
        _check_by_name_and_call(mod)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

# ============================== BUG-1304 claim set ==============================

def _bug1304_unreadable(mod, owner, agent, destination):
    try:
        mod.claim_worktrees(owner, agent, destination)
    except inflight_registry.UnreadableRegistry as error:
        return error
    return None


def case_bug1304_short_claim():
    mod = hb()
    agent = "harness-backend-dev"
    owner = tempfile.mkdtemp()
    try:
        short = make_worktree(mod, owner, "FEAT-32")
        write_claims(short, [live_claim(agent, "FEAT-32-concurrent-write-merge")])
        got = mod.claim_worktrees(owner, agent, owner)
        check("bug1304: short-form worktree prefix contributes to S",
              got == [short], f"expected {[short]!r}, got {got!r}")
    finally:
        shutil.rmtree(owner, ignore_errors=True)


def case_bug1304_owner_claim():
    mod = hb()
    agent = "harness-backend-dev"
    owner = tempfile.mkdtemp()
    try:
        linked = make_worktree(mod, owner, "FEAT-40")
        write_claims(owner, [live_claim(agent, "FEAT-40-harness-writes-done")])
        got = mod.claim_worktrees(owner, agent, owner)
        check("bug1304: owner-root registry claim resolves by its feature",
              got == [linked], f"expected {[linked]!r}, got {got!r}")
    finally:
        shutil.rmtree(owner, ignore_errors=True)


def case_bug1304_unresolved_and_empty_claims():
    mod = hb()
    agent = "harness-backend-dev"
    owner = tempfile.mkdtemp()
    try:
        write_claims(owner, [live_claim(agent, "FEAT-404-missing")])
        check("bug1304: unresolved feature contributes no worktree",
              mod.claim_worktrees(owner, agent, owner) == [])
    finally:
        shutil.rmtree(owner, ignore_errors=True)
    owner = tempfile.mkdtemp()
    try:
        check("bug1304: no claims yields an empty set",
              mod.claim_worktrees(owner, agent, owner) == [])
    finally:
        shutil.rmtree(owner, ignore_errors=True)


def case_bug1304_multiple_claims():
    mod = hb()
    agent = "harness-backend-dev"
    owner = tempfile.mkdtemp()
    try:
        first = make_worktree(mod, owner, "FEAT-31")
        second = make_worktree(mod, owner, "FEAT-32")
        write_claims(owner, [
            live_claim(agent, "FEAT-31-orchestrator-context-watch"),
            live_claim(agent, "FEAT-32-concurrent-write-merge"),
        ])
        check("bug1304: claims in two features yield both worktrees",
              mod.claim_worktrees(owner, agent, owner) == sorted([first, second]))
    finally:
        shutil.rmtree(owner, ignore_errors=True)

def case_runtime_lineage_filters_claim_worktrees():
    mod = hb()
    agent = "harness-backend-dev"
    owner = tempfile.mkdtemp()
    try:
        first = make_worktree(mod, owner, "FEAT-31")
        make_worktree(mod, owner, "FEAT-32")
        first_claim = live_claim(agent, "FEAT-31-orchestrator-context-watch")
        first_claim.update({"agent_id": "BackendOne", "parent_agent_id": "LeadOne"})
        second_claim = live_claim(agent, "FEAT-32-concurrent-write-merge")
        second_claim.update({"agent_id": "BackendTwo", "parent_agent_id": "LeadTwo"})
        write_claims(owner, [first_claim, second_claim])
        got = mod.claim_worktrees(
            owner,
            agent,
            owner,
            agent_id="BackendOne",
            parent_agent_id="LeadOne",
        )
        check("runtime lineage selects only the exact child's worktree",
              got == [first], f"expected {[first]!r}, got {got!r}")
        sibling = mod.claim_worktrees(
            owner,
            agent,
            owner,
            agent_id="BackendOne",
            parent_agent_id="LeadTwo",
        )
        check("runtime lineage rejects a sibling parent's claim",
              sibling == [], f"expected [], got {sibling!r}")
    finally:
        shutil.rmtree(owner, ignore_errors=True)



def case_bug1304_ambiguous_claim():
    mod = hb()
    agent = "harness-backend-dev"
    owner = tempfile.mkdtemp()
    try:
        make_worktree(mod, owner, "FEAT")
        make_worktree(mod, owner, "FEAT-X")
        write_claims(owner, [live_claim(agent, "FEAT-X-thing")])
        raised = None
        try:
            mod.claim_worktrees(owner, agent, owner)
        except mod.AmbiguousWorktree as error:
            raised = error
        check("bug1304: ambiguous feature worktrees propagate",
              raised is not None and "FEAT, FEAT-X" in str(raised), repr(raised))
    finally:
        shutil.rmtree(owner, ignore_errors=True)


def _bug1304_check_owner_unreadable(mod, owner, linked, agent,
                                    owner_registry, outside):
    with open(owner_registry, "w", encoding="utf-8") as handle:
        handle.write("{")
    write_claims(linked, [live_claim(agent, "FEAT-50-run-artifact-integrity")])
    raised = _bug1304_unreadable(mod, owner, agent, outside)
    check("bug1304: unreadable owner registry also refuses",
          raised is not None and owner_registry in str(raised), repr(raised))

    got = mod.claim_worktrees(owner, agent, os.path.join(linked, "inside"))
    check("bug1304: proven destination is allowed with unrelated unreadable registry",
          got == [linked], f"expected {[linked]!r}, got {got!r}")


def case_bug1304_unreadable_claims():
    mod = hb()
    agent = "harness-backend-dev"
    owner = tempfile.mkdtemp()
    try:
        linked = make_worktree(mod, owner, "FEAT-50")
        owner_registry = write_claims(
            owner, [live_claim(agent, "FEAT-50-run-artifact-integrity")])
        linked_registry = write_claims(linked, [])
        with open(linked_registry, "w", encoding="utf-8") as handle:
            handle.write("{")
        outside = os.path.join(owner, "outside")
        raised = _bug1304_unreadable(mod, owner, agent, outside)
        check("bug1304: unreadable linked registry refuses an outside destination",
              raised is not None and linked_registry in str(raised), repr(raised))

        _bug1304_check_owner_unreadable(
            mod, owner, linked, agent, owner_registry, outside)
    finally:
        shutil.rmtree(owner, ignore_errors=True)


def case_bug1304_refusal_text():
    mod = hb()
    agent = "harness-backend-dev"
    members = ["/tmp/wt-a", "/tmp/wt-b"]
    destination = "/tmp/main/.harness/file"
    refusal = mod.claim_set_refusal(agent, members, destination)
    check("bug1304: refusal names every claim worktree and destination home",
          all(value in refusal for value in members)
          and destination in refusal and "/tmp/main" in refusal,
          refusal)
    check("bug1304: refusal never advises removing a worktree",
          "remove the worktree" not in refusal.lower(), refusal)
    expertise_refusal = mod.claim_set_refusal(
        agent, members, "/tmp/main/.harness/expertise/harness-backend-dev.md")
    check("bug1304: expertise refusal names the sanctioned merge CLI",
          "expertise-merge.py apply" in expertise_refusal
          and "remove the worktree" not in expertise_refusal.lower(),
          expertise_refusal)


def case_bug1304_claim_set():
    case_bug1304_short_claim()
    case_bug1304_owner_claim()
    case_bug1304_unresolved_and_empty_claims()
    case_bug1304_multiple_claims()
    case_runtime_lineage_filters_claim_worktrees()
    case_bug1304_ambiguous_claim()
    case_bug1304_unreadable_claims()
    case_bug1304_refusal_text()


def run_case(fn):
    """Run one case, tolerating a crash so one broken case does not silently skip
    every later one (an unguarded raise would abort main() and leave the rest
    unreported)."""
    try:
        fn()
    except Exception as e:
        check(f"{fn.__name__}_did_not_crash", False, f"raised {e!r}")


def case_real_keeps_one_namespace_when_unresolvable():
    """FEAT-41 HIGH-3, cycle 4. `real()` must return a path in the SAME namespace whether or not
    the input resolves, because every caller COMPARES its output against another `real()` result.

    MF-2 made `real()` total by falling back to `abspath` on an unresolvable input. That stopped
    the fail-open crash, but it returns an UNRESOLVED path -- and when the checkout root is
    reached through a symlink, `real(root)` is fully resolved while `real(target)` is not. The two
    no longer share a prefix, so `select_base`/`inside` classify an in-base target as
    `not_a_domain_question` and `bash-write-guard.py` exits 0 with empty stderr.

    MEASURED on a symlinked root before the fix:
        real('/tmp/h3/link')                    -> /private/tmp/h3/actual
        real('/tmp/h3/link/sub/<unresolvable>')  -> /tmp/h3/link/sub/<unresolvable>
        target.startswith(root)                  -> False

    THE PERMIT IS PRE-EXISTING -- origin/main crashes fail-open on the same input, so the write
    proceeded there too. What MF-2 changed is that it became SILENT rather than loud, which for a
    guard is worse. So the fallback must resolve AS FAR AS IT SAFELY CAN: the longest ancestor
    that resolves, plus the remainder verbatim.
    """
    mod = hb()
    with tempfile.TemporaryDirectory() as tmp:
        actual = os.path.join(tmp, "actual", "sub")
        os.makedirs(actual, exist_ok=True)
        link = os.path.join(tmp, "link")
        os.symlink("actual", link)
        root = mod.real(link)
        target = mod.real(os.path.join(link, "sub", "in\x00valid"))
        check("real() keeps ONE namespace: an unresolvable target still sits under the "
              "resolved root",
              target.startswith(root), f"root={root!r} target={target!r}")
        check("real() is still TOTAL on an unresolvable input — it must not raise, or the whole "
              "hook body fails open at exit 1",
              isinstance(target, str) and target, f"target={target!r}")
        # NEGATIVE CONTROL: a perfectly ordinary path is unaffected by the fallback.
        ok = mod.real(os.path.join(link, "sub"))
        check("real() NEGATIVE CONTROL: a resolvable path is unchanged by the fallback",
              ok == os.path.realpath(os.path.join(link, "sub")), f"got={ok!r}")



def case_run_identity_pattern():
    mod = hb()
    marker = ".harness/harness/features/BUG-1305-run-state-clobber/runs/r1/.run-identity.json"
    check("run identity pattern matches marker", mod.RE_RUN_IDENTITY.match(marker))
    check("run identity pattern is case insensitive",
          mod.RE_RUN_IDENTITY.match(marker.upper()))
    for path in (
            ".harness/harness/features/F/runs/r1/state.yaml",
            ".harness/harness/features/F/runs/r1/digest.md",
            ".harness/harness/features/F/runs/.run-identity.json",
            "tmp/runs/r1/.run-identity.json"):
        check(f"run identity pattern rejects {path}",
              not mod.RE_RUN_IDENTITY.match(path))


def case_tests_are_target_side_control_plane_only():
    mod = hb()
    for path in (
            "tests/unit/test-x.py",
            "tests/integration/test-y.py",
            "tests/manual/probe-z.py"):
        check(f"{path} is a control-plane target",
              mod.is_control_plane_target(path))
    for pattern in ("tests/**", "tests/unit/**"):
        check(f"{pattern} is not a control-plane glob",
              not mod.is_control_plane_glob(pattern))
    for path in ("src/main.py", "web/src/app.test.ts"):
        check(f"{path} remains product-side",
              not mod.is_control_plane_target(path))

def write_synthetic_run_dir_manifest(root, squad):
    """A temp team-config.yaml whose only `/runs/` grant names an invented squad."""
    harness_dir = os.path.join(root, ".harness")
    os.makedirs(harness_dir, exist_ok=True)
    path = os.path.join(harness_dir, "team-config.yaml")
    with open(path, "w") as fh:
        fh.write(
            "schema_version: 1\n"
            "leads:\n"
            f"  - name: harness-{squad}-lead\n"
            f"    squad: {squad}\n"
            "    domain:\n"
            f"      - {{ path: .harness/*/features/*/runs/*-{squad}/**, upsert: true }}\n"
            "      - { path: .harness/expertise/harness-invented-lead.md, upsert: true }\n"
        )
    return path


# ============================== run_dir_grant_globs ==============================

def case_run_dir_grant_globs_live_shape():
    mod = hb()
    globs = mod.run_dir_grant_globs(ROOT)
    check("run_dir_grant_globs_live_nonempty", bool(globs), f"got {globs!r}")
    check("run_dir_grant_globs_live_all_contain_runs_segment",
          all("/runs/" in g for g in globs), f"got {globs!r}")
    check("run_dir_grant_globs_live_sorted_deduped",
          globs == sorted(set(globs)), f"got {globs!r}")


def case_run_dir_grant_globs_synthetic():
    mod = hb()
    tmp = tempfile.mkdtemp()
    try:
        write_synthetic_run_dir_manifest(tmp, "gizmo")
        got = mod.run_dir_grant_globs(tmp)
        expected = [".harness/*/features/*/runs/*-gizmo/**"]
        check("run_dir_grant_globs_synthetic_exact", got == expected,
              f"expected {expected!r}, got {got!r}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def case_run_dir_grant_globs_uses_aggregated_accessor():
    mod = hb()
    calls = []

    class Accessors:
        @staticmethod
        def manifest_domains(path, agent=None):
            calls.append((path, agent))
            return ("all/runs/alpha", "shared/runs/beta", "outside"), (
                "shared/runs/gamma",)

    mod.artifact_accessors = Accessors
    root = "/synthetic-root"
    got = mod.run_dir_grant_globs(root)
    expected_path = os.path.join(root, ".harness", "team-config.yaml")
    check("run_dir_grant_globs_uses_aggregated_manifest_accessor",
          calls == [(expected_path, None)],
          f"calls={calls!r}")
    check("run_dir_grant_globs_combines_all_role_and_shared_run_grants",
          got == ["all/runs/alpha", "shared/runs/beta", "shared/runs/gamma"],
          f"got {got!r}")


def case_run_dir_grant_globs_absent_and_garbage():
    mod = hb()
    tmp = tempfile.mkdtemp()
    try:
        got_absent = mod.run_dir_grant_globs(tmp)
        check("run_dir_grant_globs_absent_manifest_empty", got_absent == [],
              f"got {got_absent!r}")

        harness_dir = os.path.join(tmp, ".harness")
        os.makedirs(harness_dir, exist_ok=True)
        with open(os.path.join(harness_dir, "team-config.yaml"), "wb") as fh:
            fh.write(b"\xff\xfe\x00garbage not yaml [[[")
        got_garbage = mod.run_dir_grant_globs(tmp)
        check("run_dir_grant_globs_garbage_manifest_empty", got_garbage == [],
              f"got {got_garbage!r}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ============================== run_dir_refs ==============================

def case_run_dir_refs():
    mod = hb()
    absolute = ("see /a/b/.harness/harness/features/F/runs/eng-t01/digest.md "
                "and again /a/b/.harness/harness/features/F/runs/eng-t01/digest.md now")
    got = mod.run_dir_refs(absolute)
    check("run_dir_refs_finds_tail_in_absolute_path_and_dedupes_repeat",
          got == [("harness", "F", "eng-t01")], f"got {got!r}")

    no_run_dir = "nothing here names a run directory at all"
    got_none = mod.run_dir_refs(no_run_dir)
    check("run_dir_refs_empty_for_no_run_dir", got_none == [], f"got {got_none!r}")


# ============================== run_dir_slug_ok ==============================

def case_run_dir_slug_ok():
    mod = hb()
    globs = mod.run_dir_grant_globs(ROOT)
    for slug in ("t01-eng", "plan-product", "2026-08-26-2-plan-product"):
        ref = ("harness", "F", slug)
        check(f"run_dir_slug_ok_accepts_{slug}",
              mod.run_dir_slug_ok(ref, globs), f"ref={ref!r} globs={globs!r}")
    for slug in ("eng-t01", "plan_product"):
        ref = ("harness", "F", slug)
        check(f"run_dir_slug_ok_rejects_{slug}",
              not mod.run_dir_slug_ok(ref, globs), f"ref={ref!r} globs={globs!r}")
    check("run_dir_slug_ok_empty_globs_is_false",
          not mod.run_dir_slug_ok(("harness", "F", "t01-eng"), []))


# ============================== run_dir_forms ==============================

def case_run_dir_forms():
    mod = hb()
    tmp = tempfile.mkdtemp()
    try:
        write_synthetic_run_dir_manifest(tmp, "gizmo")
        globs = mod.run_dir_grant_globs(tmp)
        got = mod.run_dir_forms(globs)
        check("run_dir_forms_synthetic_exact",
              got == ["<task-or-purpose>-gizmo"], f"got {got!r}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)



def main():
    run_case(case_marker_constant)
    run_case(case_root_from_script)
    run_case(case_resolve_root_strict)
    run_case(case_resolve_root_override_normalises_relative)
    run_case(case_root_above)
    run_case(case_worktree_for_feature)
    run_case(case_changed_state_feedback)
    run_case(case_feature_artifact_checkout_mismatch)
    run_case(case_feature_artifact_checkout_mismatch_ambiguous)
    run_case(case_load_repo_module_registration)
    run_case(case_load_repo_module_failures)
    run_case(case_bug1304_claim_set)
    run_case(case_real_keeps_one_namespace_when_unresolvable)
    run_case(case_run_identity_pattern)
    run_case(case_tests_are_target_side_control_plane_only)
    run_case(case_run_dir_grant_globs_uses_aggregated_accessor)
    run_case(case_run_dir_grant_globs_live_shape)
    run_case(case_run_dir_grant_globs_synthetic)
    run_case(case_run_dir_grant_globs_absent_and_garbage)
    run_case(case_run_dir_refs)
    run_case(case_run_dir_slug_ok)
    run_case(case_run_dir_forms)


    if failures:
        print(f"\n{len(failures)} FAILURE(S): {failures}")
        return 1
    print("\nALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
