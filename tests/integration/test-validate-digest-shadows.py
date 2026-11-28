#!/usr/bin/env python3
"""Three prose rules that became validator checks (consumer audit, 2026-09-18).

Each is a predicate over data the repository owns, exercised end to end through
`validate()` on a purpose-built git checkout — never by calling the helper alone, because
the plausible bug is a helper that exists and is never reached. Every return is a digest
OBJECT `{VERDICT, DIGEST, artifact}` (FEAT-1928), exactly as an agent yields it.

  human_commits_in_scope   computed from `[harness:human]` commits in the canonical range
  dirty tree               a PASS/FAIL over tracked modifications outside .harness/ is refused
  qa kind states           `state` is one of five, cross-checked against harness.json
"""
from integration_support import BIN
import importlib.util
import json
import os
import sys
import tempfile

from check_support import Checks  # noqa: E402
from git_support import checked_git, commit_all, git_out, init_repo  # noqa: E402
from harness_config_support import write_config  # noqa: E402

VALIDATE = str(BIN / "validate-digest.py")

C = Checks()
check = C.check


def _validator():
    spec = importlib.util.spec_from_file_location("_shadow_validator", VALIDATE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Loaded once: its one cache (_qa_policy) is keyed on the feature directory and review pin,
# and every case runs in its own temporary directory.
V = _validator()


def _write(path, body):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(body)


def _commit(repo, name, content, message):
    """Write `name`, stage the whole tree (fixture files under .harness/ included) and commit;
    returns the new HEAD oid."""
    _write(os.path.join(repo, name), content)
    commit_all(repo, message, git=checked_git)
    return git_out(repo, "rev-parse", "HEAD")


# Builder overrides for every checkout's harness.json (test_kinds replaces the default roster).
HARNESS_JSON = {
    "gates": {"review": "advisory_unless_high"},
    "test_kinds": {
        "unit": {"detect": "test_*.py", "exclude": "", "cmd": "true", "status": "active"},
        "functional": {"detect": "tests/functional/**", "exclude": "", "cmd": None,
                       "status": "excluded", "excluded_because": "no service API",
                       "signed": "DEC-163"},
    },
}

FEAT = "FEAT-77-shadow"


def _checkout(td, human_messages=(), head_files=None):
    """A repo whose canonical range `A..head` carries one prose commit per entry of
    `human_messages` (each a commit subject) plus the head commit, which also lands each
    `{relpath: text}` of `head_files`. Returns `(repo, feature_dir, head_oid, [human oids])`."""
    repo = os.path.join(td, "repo")
    os.makedirs(os.path.join(repo, ".harness"))
    init_repo(repo, "main", git=checked_git)
    write_config(os.path.join(repo, ".harness", "harness.json"), HARNESS_JSON)
    _write(os.path.join(repo, ".harness", "team-config.yaml"), "agents: {}\n")
    base = _commit(repo, "readme.txt", "a\n", "A")
    git_out(repo, "update-ref", "refs/remotes/origin/main", base)
    git_out(repo, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main")
    humans = [_commit(repo, f"h{i}.md", f"{i}\n", msg) for i, msg in enumerate(human_messages)]
    for rel, text in (head_files or {}).items():
        _write(os.path.join(repo, rel), text)
    head = _commit(repo, "notes.md", "prose\n", "head")
    feature_dir = os.path.join(repo, ".harness", "harness", "features", FEAT)
    os.makedirs(os.path.join(feature_dir, "notes"))
    _write(os.path.join(feature_dir, "feature.json"),
           json.dumps({"feature_id": FEAT, "review_sha": head}))
    return repo, feature_dir, head, humans


def _review(head, verdict="PASS", human=(), findings=(), code_grade="n_a", reasons=()):
    """A reviewer object; `human=None` omits human_commits_in_scope, every other field is
    always present (FEAT-1928 ruling: `[]` spells none)."""
    digest = {
        "headline": "reviewer result", "severity_max": "low", "findings": list(findings),
        "must_fix": [], "code_grade": code_grade, "reviewed": f"origin/main..{head}",
        "files_touched": [], "open_questions": [], "expertise_update": [],
        "spec_violations": [], "grade_2_reasons": list(reasons),
    }
    if human is not None:
        digest["human_commits_in_scope"] = list(human)
    return {"VERDICT": verdict, "DIGEST": digest,
            "artifact": f".harness/harness/features/{FEAT}/notes/review.md"}


FAIL_FIRST = [{"sc": "SC-01", "evidence": "notes/fail.txt"}]


def _qa(kinds, verdict="PASS"):
    gated = verdict == "PASS"
    digest = {
        "headline": "qa result", "matrix_ok": True if gated else "n/a",
        "suite": "pass" if gated else "n/a", "failures": 0, "coverage_gaps": [],
        "fail_first": list(FAIL_FIRST), "files_touched": [], "open_questions": [],
        "expertise_update": [], "kinds": list(kinds), "sc_evidence": [],
    }
    return {"VERDICT": verdict, "DIGEST": digest,
            "artifact": f".harness/harness/features/{FEAT}/notes/qa.md"}


def _with(obj, verdict=None, **fields):
    """A copy of digest object `obj` with VERDICT and/or DIGEST fields replaced."""
    out = json.loads(json.dumps(obj))
    if verdict:
        out["VERDICT"] = verdict
    out["DIGEST"].update(fields)
    return out


def _errors(persona, obj, feature_dir, config):
    return V.validate(persona, obj, config, feature_dir, branch_override=None)


def _config(td):
    path = os.path.join(td, "harness.json")
    write_config(path, {"gates": {"review": "advisory_unless_high"}})
    return path


def case_human_commits():
    with tempfile.TemporaryDirectory() as td:
        repo, fd, head, humans = _checkout(td, ("[harness:human] hand edit", "bot edit"))
        cfg = _config(td)
        errs = _errors("harness-code-reviewer", _review(head, human=[humans[0][:10]]), fd, cfg)
        check("human: an honest list is accepted", not errs, str(errs))
        errs = _errors("harness-code-reviewer", _review(head), fd, cfg)
        check("human: an empty list over a range with a human commit is refused",
              any("human_commits_in_scope" in e and humans[0][:12] in e for e in errs), str(errs))
        errs = _errors("harness-code-reviewer", _review(head, human=None), fd, cfg)
        check("human: omitting the field is refused as a missing required field",
              any("missing 'human_commits_in_scope'" in e for e in errs), str(errs))
        errs = _errors("harness-code-reviewer",
                       _review(head, human=[humans[0][:10], humans[1][:10]]), fd, cfg)
        check("human: a bot commit claimed as human is refused and named",
              any("not in the range" in e and humans[1][:10] in e for e in errs), str(errs))
    with tempfile.TemporaryDirectory() as td:
        repo, fd, head, _ = _checkout(td)
        cfg = _config(td)
        check("human: no human commits and [] is accepted",
              not _errors("harness-code-reviewer", _review(head), fd, cfg))


def case_dirty_tree():
    with tempfile.TemporaryDirectory() as td:
        repo, fd, head, _ = _checkout(td)
        cfg = _config(td)
        with open(os.path.join(repo, "readme.txt"), "a") as fh:
            fh.write("hand edit\n")
        for verdict in ("PASS", "FAIL"):
            errs = _errors("harness-code-reviewer", _review(head, verdict), fd, cfg)
            check(f"dirty: a {verdict} over a modified tracked file is refused, naming it",
                  any("readme.txt" in e and "pinnable" in e for e in errs), str(errs))
        errs = _errors("harness-code-reviewer", _review(head, "BLOCKED"), fd, cfg)
        check("dirty: BLOCKED is the honest return and is accepted",
              not any("pinnable" in e for e in errs), str(errs))
        git_out(repo, "checkout", "--", "readme.txt")
        with open(os.path.join(repo, ".harness", "team-config.yaml"), "a") as fh:
            fh.write("\n")
        errs = _errors("harness-code-reviewer", _review(head), fd, cfg)
        check("dirty: a change under .harness/ does not count",
              not any("pinnable" in e for e in errs), str(errs))
        git_out(repo, "checkout", "--", ".harness/team-config.yaml")
        _write(os.path.join(repo, "scratch.txt"), "untracked\n")
        errs = _errors("harness-code-reviewer", _review(head), fd, cfg)
        check("dirty: an untracked file does not count",
              not any("pinnable" in e for e in errs), str(errs))


def _kind(kind, state, named_tests=1):
    """One qa `kinds` row with a runnable cmd."""
    return {"kind": kind, "state": state, "cmd": "true", "named_tests": named_tests}


UNIT_SATISFIED = _kind("unit", "satisfied", 3)
UNIT_MISSING = _kind("unit", "missing", "none")


def case_qa_kinds():
    with tempfile.TemporaryDirectory() as td:
        repo, fd, head, _ = _checkout(td)
        cfg = _config(td)
        ok = [UNIT_SATISFIED,
              {"kind": "functional", "state": "not_applicable", "cmd": "none",
               "named_tests": "none"}]
        errs = _errors("harness-qa", _qa(ok), fd, cfg)
        check("kinds: satisfied on a runnable kind and not_applicable on an excluded one pass",
              not errs, str(errs))
        errs = _errors("harness-qa", _qa([_kind("unit", "green")]), fd, cfg)
        check("kinds: an unknown state is refused",
              any("kinds[0].state" in e and "'green'" in e for e in errs), str(errs))
        errs = _errors("harness-qa", _qa([_kind("unit", "misconfigured")], "FAIL"), fd, cfg)
        check("kinds: misconfigured under a FAIL verdict is refused",
              any("misconfigured" in e and "BLOCKED" in e for e in errs), str(errs))
        errs = _errors("harness-qa", _qa([_kind("unit", "misconfigured")], "BLOCKED"), fd, cfg)
        check("kinds: misconfigured under BLOCKED is accepted",
              not any("misconfigured" in e for e in errs), str(errs))
        errs = _errors("harness-qa", _qa([_kind("unit", "not_applicable")]), fd, cfg)
        check("kinds: not_applicable on a kind with a runnable cmd is refused",
              any("not_applicable" in e and "runnable cmd" in e for e in errs), str(errs))
        errs = _errors("harness-qa", _qa([_kind("functional", "satisfied")]), fd, cfg)
        check("kinds: satisfied on a kind with no cmd is refused",
              any("no cmd" in e for e in errs), str(errs))
        errs = _errors("harness-qa", _qa([_kind("e2e", "satisfied")]), fd, cfg)
        check("kinds: a kind harness.json does not declare is refused",
              any("does not declare" in e for e in errs), str(errs))


def _dev(verdict="PASS", tv="pass", task="T-01", artifact="notes/receipt-harness-backend-dev-T-01.md"):
    return {"VERDICT": verdict,
            "DIGEST": {"headline": "dev result", "tests_added": 1, "suite": "pass",
                       "blocked_on": "none", "task": task, "task_verify": tv,
                       "files_touched": ["src/x.py"], "open_questions": [],
                       "expertise_update": []},
            "artifact": f".harness/harness/features/{FEAT}/{artifact}"}


PLAN = f"""schema: plan/1
feature: {FEAT}
approval:
  status: approved
tasks:
  - id: T-01
    title: do it
    intent: do it
    execution_mode: team
    change_type: production
    files: [src/x.py]
    verify: python3 tests/unit/test-x.py --strict
    depends_on: []
"""

GRADE_2_PY = "def moderate(a, b, c, d):\n" + "".join(
    f"    if a == {i}:\n        return {i}\n" for i in range(6)) + "    return b if c else d\n"


def case_receipt():
    with tempfile.TemporaryDirectory() as td:
        repo, fd, head, _ = _checkout(td)
        cfg = _config(td)
        _write(os.path.join(fd, "plan.yaml"), PLAN)
        errs = _errors("harness-backend-dev", _dev(), fd, cfg)
        check("receipt: task_verify pass with no receipt on disk is refused",
              any("not on disk" in e for e in errs), str(errs))
        receipt = os.path.join(fd, "notes", "receipt-harness-backend-dev-T-01.md")
        _write(receipt, "ran: python3 tests/unit/test-x.py\nok\n")
        errs = _errors("harness-backend-dev", _dev(), fd, cfg)
        check("receipt: a receipt without the verbatim verify command is refused",
              any("verbatim" in e for e in errs), str(errs))
        _write(receipt, "$ python3 tests/unit/test-x.py --strict\n3 passed\n")
        errs = _errors("harness-backend-dev", _dev(), fd, cfg)
        check("receipt: the verbatim command in the receipt is accepted", not errs, str(errs))
        errs = _errors("harness-backend-dev", _dev(verdict="BLOCKED", tv="n/a"), fd, cfg)
        check("receipt: a non-pass return is not held to the receipt",
              not any("receipt" in e for e in errs), str(errs))


def case_inspection_citations():
    with tempfile.TemporaryDirectory() as td:
        repo, fd, head, _ = _checkout(td)
        cfg = _config(td)
        _write(os.path.join(fd, "BRIEF.md"), "## Success criteria\n\n- SC-01: the doc says so\n"
               "  verify: inspection\n- SC-02: tests pass\n  verify: automated\n"
               "- SC-03: the config is shaped\n  verify: inspection\n")
        review = os.path.join(fd, "notes", "review.md")
        _write(review, "# review\nSC-01 satisfied: docs/notes.md:1\nSC-02 by the suite.\n")
        errs = _errors("harness-code-reviewer", _review(head), fd, cfg)
        check("inspection: an inspection SC with no file:line citation is refused, named",
              any("SC-03" in e and "file:line" in e and "SC-01" not in e.split("cites")[0].split("marks")[1] for e in errs), str(errs))
        _write(review, "# review\nSC-01 satisfied: docs/notes.md:1\nSC-03 holds, see .harness/harness.json:4\n")
        errs = _errors("harness-code-reviewer", _review(head), fd, cfg)
        check("inspection: every inspection SC cited is accepted", not errs, str(errs))
        os.remove(review)
        errs = _errors("harness-code-reviewer", _review(head), fd, cfg)
        check("inspection: an unreadable artifact is not this check's finding",
              not any("file:line" in e for e in errs), str(errs))


def case_findings_order():
    with tempfile.TemporaryDirectory() as td:
        repo, fd, head, _ = _checkout(td)
        cfg = _config(td)
        low = {"kind": "form", "scope": "none", "severity": "low", "reader": "code",
               "summary": "a", "why": "a drifted"}
        high = {"kind": "substance", "scope": "none", "severity": "high", "reader": "code",
                "summary": "b", "why": "b fails open"}
        errs = _errors("harness-code-reviewer", _review(head, findings=[low, high]), fd, cfg)
        check("ranking: low before high is refused", any("not ranked" in e for e in errs), str(errs))
        errs = _errors("harness-code-reviewer", _review(head, findings=[high, low]), fd, cfg)
        check("ranking: high before low is accepted", not errs, str(errs))


def case_grade_2_names():
    with tempfile.TemporaryDirectory() as td:
        repo, fd, head, _ = _checkout(td, head_files={"src/mod.py": GRADE_2_PY})
        cfg = _config(td)
        probe = _errors("harness-code-reviewer", _review(head, code_grade="grade_2",
                                                          reasons=["moderate is a dispatch table"]), fd, cfg)
        if any("disagrees with the mechanical result" in e for e in probe):
            check("grade2: fixture grades 2 (skipped: fixture graded otherwise)", True, str(probe))
            return
        check("grade2: a reason naming the function is accepted", not probe, str(probe))
        errs = _errors("harness-code-reviewer", _review(head, code_grade="grade_2",
                                                         reasons=["it is fine really"]), fd, cfg)
        check("grade2: a reason naming no graded function is refused, naming it",
              any("names none of: moderate" in e for e in errs), str(errs))


def case_qa_unearned_fail():
    with tempfile.TemporaryDirectory() as td:
        repo, fd, head, _ = _checkout(td)
        cfg = _config(td)
        green_fail = _with(_qa([], "PASS"), verdict="FAIL")
        errs = _errors("harness-qa", green_fail, fd, cfg)
        check("qa: FAIL with every gate green and fail-first evidence present is refused",
              any("no gate failed" in e for e in errs), str(errs))
        no_evidence = _with(green_fail, fail_first=[])
        errs = _errors("harness-qa", no_evidence, fd, cfg)
        check("qa: FAIL with a green suite and NO fail-first evidence is the mandated return (P59)",
              not any("no gate failed" in e for e in errs), str(errs))
        real_fail = _with(green_fail, failures=2, suite="fail")
        errs = _errors("harness-qa", real_fail, fd, cfg)
        check("qa: FAIL with a failing suite is accepted", not any("no gate failed" in e for e in errs), str(errs))


MATRIX_JSON = dict(HARNESS_JSON, test_kinds=dict(
    HARNESS_JSON["test_kinds"],
    component={"detect": "tests/component/**", "exclude": "", "cmd": None, "status": "active"},
), test_matrix={
    "logic": {"always": ["unit"]},
    "cross_module": {"always": ["unit", "functional"]},
    "docs": {"always": []},
    "bugfix": {"always": [], "when": [{"kind": "unit", "if": "touches_runtime_code"}]},
    "api": {"always": ["functional"]},
    "frontend": {"always": ["component"]},
})


def _plan_with(change_types):
    tasks = "".join(
        f"  - id: T-0{i+1}\n    title: t{i+1}\n    intent: do it\n    change_type: {ct}\n"
        f"    execution_mode: team\n    status: {status}\n    files: [src/x.py]\n"
        f"    verify: true\n    depends_on: []\n"
        for i, (ct, status) in enumerate(change_types))
    return f"schema: plan/1\nfeature: {FEAT}\napproval:\n  status: approved\ntasks:\n{tasks}"


def _pin_config(repo, feature_dir, config):
    """FEAT-2398 (D-01): QA's policy is harness.json at the review pin, so commit `config` and
    pin review_sha to that commit — a working-tree edit no longer governs QA."""
    write_config(os.path.join(repo, ".harness", "harness.json"), config)
    git_out(repo, "add", "--", ".harness/harness.json")
    git_out(repo, "commit", "-q", "-m", "policy")
    _write(os.path.join(feature_dir, "feature.json"),
           json.dumps({"feature_id": FEAT, "review_sha": git_out(repo, "rev-parse", "HEAD")}))


def case_matrix_floor():
    with tempfile.TemporaryDirectory() as td:
        repo, fd, head, _ = _checkout(td)
        _pin_config(repo, fd, MATRIX_JSON)
        cfg = _config(td)
        _write(os.path.join(fd, "plan.yaml"), _plan_with([("logic", "done")]))
        errs = _errors("harness-qa", _qa([UNIT_SATISFIED]), fd, cfg)
        check("floor: the floor kind reported satisfied is accepted", not errs, str(errs))
        errs = _errors("harness-qa", _qa([UNIT_MISSING]), fd, cfg)
        check("floor: matrix_ok true with the floor kind missing is refused, naming it",
              any("matrix floor requires unit" in e for e in errs), str(errs))
        errs = _errors("harness-qa", _qa([]), fd, cfg)
        check("floor: matrix_ok true with kinds: [] is refused as unverifiable",
              any("kinds: [] reports no kind" in e and "unit" in e for e in errs), str(errs))
        errs = _errors("harness-qa", _with(_qa([UNIT_MISSING], "FAIL"), matrix_ok=False,
                                              suite="fail"), fd, cfg)
        check("floor: a FAIL that reports the gap is not held to the floor",
              not any("matrix floor" in e for e in errs), str(errs))
        _write(os.path.join(fd, "plan.yaml"), _plan_with([("cross_module", "done")]))
        errs = _errors("harness-qa", _qa([UNIT_SATISFIED]), fd, cfg)
        check("floor: an excluded kind (functional, status: excluded) never enters the floor",
              not any("matrix floor" in e for e in errs), str(errs))
        _write(os.path.join(fd, "plan.yaml"), _plan_with([("docs", "done"), ("logic", "todo")]))
        errs = _errors("harness-qa", _qa([]), fd, cfg)
        check("floor: a docs task and an unstarted logic task impose no floor",
              not errs, str(errs))


_DECLINED = "declines to report a gate"
_NO_SUITE = _with(_qa([]), suite="n/a")


def _floor_checkout(td):
    """`(feature_dir, config)` of a checkout pinned to MATRIX_JSON, shared by one case's calls."""
    repo, fd, _head, _ = _checkout(td)
    _pin_config(repo, fd, MATRIX_JSON)
    return fd, _config(td)


def _qa_floor_errors(fd, cfg, change_types, obj=_NO_SUITE):
    """#2139: the qa errors for `obj` over a plan of `change_types`; None removes any plan an
    earlier call left, so the floor is unresolvable."""
    plan = os.path.join(fd, "plan.yaml")
    if change_types is None:
        if os.path.exists(plan):
            os.remove(plan)
    else:
        _write(plan, _plan_with(change_types))
    return _errors("harness-qa", obj, fd, cfg)


def _declined(errs, field):
    return any(_DECLINED in e and field in e for e in errs)


def case_qa_empty_floor_suite():
    """#2139: qa `suite: n/a` + PASS is honest only where the computed matrix floor is empty."""
    docs = [("docs", "done")]
    with tempfile.TemporaryDirectory() as td:
        fd, cfg = _floor_checkout(td)
        for label, plan in (("empty floor", docs), ("explicitly excluded kind", [("api", "done")])):
            errs = _qa_floor_errors(fd, cfg, plan)
            check(f"{label}: suite n/a with kinds [] and matrix_ok true is accepted", not errs, str(errs))
        errs = _qa_floor_errors(fd, cfg, docs, _with(_NO_SUITE, kinds=[UNIT_SATISFIED]))
        check("empty floor: suite n/a beside a reported kind still declines a gate",
              _declined(errs, "suite"), str(errs))
        errs = _qa_floor_errors(fd, cfg, docs, _with(_NO_SUITE, matrix_ok="n/a"))
        check("empty floor: matrix_ok n/a with PASS is still refused",
              _declined(errs, "matrix_ok"), str(errs))


_STILL_GATED = (
    ("non-empty floor", [("docs", "done"), ("logic", "done")]),
    ("conditional bugfix row", [("bugfix", "done")]),
    ("unknown change_type", [("doc", "done")]),
    ("no started task", [("docs", "todo")]),
    ("active kind with null cmd", [("frontend", "done")]),
    ("unresolvable floor", None),
)


def case_qa_floor_still_binds_suite():
    """#2139: a required, conditional or unknown row, no started work, or a floor that cannot
    be derived keeps `suite` gated."""
    with tempfile.TemporaryDirectory() as td:
        fd, cfg = _floor_checkout(td)
        for label, change_types in _STILL_GATED:
            errs = _qa_floor_errors(fd, cfg, change_types)
            check(f"{label}: suite n/a with PASS is refused", _declined(errs, "suite"), str(errs))


def main():
    case_matrix_floor()
    case_qa_empty_floor_suite()
    case_qa_floor_still_binds_suite()
    case_human_commits()
    case_dirty_tree()
    case_qa_kinds()
    case_receipt()
    case_inspection_citations()
    case_findings_order()
    case_grade_2_names()
    case_qa_unearned_fail()
    return C.report()


if __name__ == "__main__":
    sys.exit(main())
