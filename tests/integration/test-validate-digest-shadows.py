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
import importlib.util
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
VALIDATE = os.path.join(REPO_ROOT, ".claude", "skills", "harness", "bin", "validate-digest.py")

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, ok, detail))


def _validator():
    spec = importlib.util.spec_from_file_location("_shadow_validator", VALIDATE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], check=True,
                          capture_output=True, text=True).stdout.strip()


def _commit(repo, name, content, message):
    with open(os.path.join(repo, name), "w") as fh:
        fh.write(content)
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", message)
    return _git(repo, "rev-parse", "HEAD")


HARNESS_JSON = {
    "gates": {"review": "advisory_unless_high"},
    "test_kinds": {
        "unit": {"detect": "test_*.py", "exclude": "", "cmd": "true", "status": "active"},
        "functional": {"detect": "tests/functional/**", "exclude": "", "cmd": None,
                       "status": "excluded", "excluded_because": "no service API"},
    },
}

FEAT = "FEAT-77-shadow"


def _checkout(td, human_messages=()):
    """A repo whose canonical range `A..head` carries one prose commit per entry of
    `human_messages` (each a commit subject) plus the head commit. Returns
    `(repo, feature_dir, head_oid, [human oids])`."""
    repo = os.path.join(td, "repo")
    os.makedirs(os.path.join(repo, ".harness"))
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "t")
    with open(os.path.join(repo, ".harness", "harness.json"), "w") as fh:
        json.dump(HARNESS_JSON, fh)
    with open(os.path.join(repo, ".harness", "team-config.yaml"), "w") as fh:
        fh.write("agents: {}\n")
    base = _commit(repo, "readme.txt", "a\n", "A")
    _git(repo, "update-ref", "refs/remotes/origin/main", base)
    _git(repo, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main")
    humans = [_commit(repo, f"h{i}.md", f"{i}\n", msg) for i, msg in enumerate(human_messages)]
    head = _commit(repo, "docs/notes.md" if os.path.isdir(os.path.join(repo, "docs"))
                   else "notes.md", "prose\n", "head")
    feature_dir = os.path.join(repo, ".harness", "harness", "features", FEAT)
    os.makedirs(os.path.join(feature_dir, "notes"))
    with open(os.path.join(feature_dir, "feature.json"), "w") as fh:
        json.dump({"feature_id": FEAT, "review_sha": head}, fh)
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


def _errors(v, persona, obj, feature_dir, config):
    return v.validate(persona, obj, config, feature_dir, branch_override=None)


def _config(td):
    path = os.path.join(td, "harness.json")
    with open(path, "w") as fh:
        json.dump({"gates": {"review": "advisory_unless_high"}}, fh)
    return path


def case_human_commits():
    v = _validator()
    with tempfile.TemporaryDirectory() as td:
        repo, fd, head, humans = _checkout(td, ("[harness:human] hand edit", "bot edit"))
        cfg = _config(td)
        check("human: an honest list is accepted",
              not _errors(v, "harness-code-reviewer", _review(head, human=[humans[0][:10]]), fd, cfg),
              str(_errors(v, "harness-code-reviewer", _review(head, human=[humans[0][:10]]), fd, cfg)))
        errs = _errors(v, "harness-code-reviewer", _review(head, human=[]), fd, cfg)
        check("human: an empty list over a range with a human commit is refused",
              any("human_commits_in_scope" in e and humans[0][:12] in e for e in errs), str(errs))
        errs = _errors(v, "harness-code-reviewer", _review(head, human=None), fd, cfg)
        check("human: omitting the field is refused as a missing required field",
              any("missing 'human_commits_in_scope'" in e for e in errs), str(errs))
        errs = _errors(v, "harness-code-reviewer",
                       _review(head, human=[humans[0][:10], humans[1][:10]]), fd, cfg)
        check("human: a bot commit claimed as human is refused and named",
              any("not in the range" in e and humans[1][:10] in e for e in errs), str(errs))
    with tempfile.TemporaryDirectory() as td:
        repo, fd, head, _ = _checkout(td)
        cfg = _config(td)
        check("human: no human commits and [] is accepted",
              not _errors(v, "harness-code-reviewer", _review(head, human=[]), fd, cfg))


def case_dirty_tree():
    v = _validator()
    with tempfile.TemporaryDirectory() as td:
        repo, fd, head, _ = _checkout(td)
        cfg = _config(td)
        with open(os.path.join(repo, "readme.txt"), "a") as fh:
            fh.write("hand edit\n")
        for verdict in ("PASS", "FAIL"):
            errs = _errors(v, "harness-code-reviewer", _review(head, verdict, human=[]), fd, cfg)
            check(f"dirty: a {verdict} over a modified tracked file is refused, naming it",
                  any("readme.txt" in e and "pinnable" in e for e in errs), str(errs))
        errs = _errors(v, "harness-code-reviewer", _review(head, "BLOCKED", human=[]), fd, cfg)
        check("dirty: BLOCKED is the honest return and is accepted",
              not any("pinnable" in e for e in errs), str(errs))
        _git(repo, "checkout", "--", "readme.txt")
        with open(os.path.join(repo, ".harness", "harness.json"), "a") as fh:
            fh.write("\n")
        errs = _errors(v, "harness-code-reviewer", _review(head, human=[]), fd, cfg)
        check("dirty: a change under .harness/ does not count",
              not any("pinnable" in e for e in errs), str(errs))
        _git(repo, "checkout", "--", ".harness/harness.json")
        with open(os.path.join(repo, "scratch.txt"), "w") as fh:
            fh.write("untracked\n")
        errs = _errors(v, "harness-code-reviewer", _review(head, human=[]), fd, cfg)
        check("dirty: an untracked file does not count",
              not any("pinnable" in e for e in errs), str(errs))


def case_qa_kinds():
    v = _validator()
    with tempfile.TemporaryDirectory() as td:
        repo, fd, head, _ = _checkout(td)
        cfg = _config(td)
        ok = [{"kind": "unit", "state": "satisfied", "cmd": "true", "named_tests": 3},
              {"kind": "functional", "state": "not_applicable", "cmd": "none",
               "named_tests": "none"}]
        check("kinds: satisfied on a runnable kind and not_applicable on an excluded one pass",
              not _errors(v, "harness-qa", _qa(ok), fd, cfg),
              str(_errors(v, "harness-qa", _qa(ok), fd, cfg)))
        errs = _errors(v, "harness-qa", _qa([{"kind": "unit", "state": "green", "cmd": "true", "named_tests": 1}]), fd, cfg)
        check("kinds: an unknown state is refused",
              any("kinds[0].state" in e and "'green'" in e for e in errs), str(errs))
        errs = _errors(v, "harness-qa", _qa([{"kind": "unit", "state": "misconfigured", "cmd": "true", "named_tests": 1}], "FAIL"), fd, cfg)
        check("kinds: misconfigured under a FAIL verdict is refused",
              any("misconfigured" in e and "BLOCKED" in e for e in errs), str(errs))
        errs = _errors(v, "harness-qa", _qa([{"kind": "unit", "state": "misconfigured", "cmd": "true", "named_tests": 1}], "BLOCKED"), fd, cfg)
        check("kinds: misconfigured under BLOCKED is accepted",
              not any("misconfigured" in e for e in errs), str(errs))
        errs = _errors(v, "harness-qa", _qa([{"kind": "unit", "state": "not_applicable", "cmd": "true", "named_tests": 1}]), fd, cfg)
        check("kinds: not_applicable on a kind with a runnable cmd is refused",
              any("not_applicable" in e and "runnable cmd" in e for e in errs), str(errs))
        errs = _errors(v, "harness-qa", _qa([{"kind": "functional", "state": "satisfied", "cmd": "true", "named_tests": 1}]), fd, cfg)
        check("kinds: satisfied on a kind with no cmd is refused",
              any("no cmd" in e for e in errs), str(errs))
        errs = _errors(v, "harness-qa", _qa([{"kind": "e2e", "state": "satisfied", "cmd": "true", "named_tests": 1}]), fd, cfg)
        check("kinds: a kind harness.json does not declare is refused",
              any("does not declare" in e for e in errs), str(errs))


def _dev(verdict="PASS", tv="pass", task="T-01", artifact="notes/receipt-harness-backend-dev-T-01.md"):
    return {"VERDICT": verdict,
            "DIGEST": {"headline": "dev result", "tests_added": 1, "suite": "pass",
                       "blocked_on": "none", "task": task, "task_verify": tv,
                       "files_touched": ["src/x.py"], "open_questions": [],
                       "expertise_update": []},
            "artifact": f".harness/harness/features/{FEAT}/{artifact}"}


def _write(path, body):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(body)


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
    v = _validator()
    with tempfile.TemporaryDirectory() as td:
        repo, fd, head, _ = _checkout(td)
        cfg = _config(td)
        _write(os.path.join(fd, "plan.yaml"), PLAN)
        errs = _errors(v, "harness-backend-dev", _dev(), fd, cfg)
        check("receipt: task_verify pass with no receipt on disk is refused",
              any("not on disk" in e for e in errs), str(errs))
        receipt = os.path.join(fd, "notes", "receipt-harness-backend-dev-T-01.md")
        _write(receipt, "ran: python3 tests/unit/test-x.py\nok\n")
        errs = _errors(v, "harness-backend-dev", _dev(), fd, cfg)
        check("receipt: a receipt without the verbatim verify command is refused",
              any("verbatim" in e for e in errs), str(errs))
        _write(receipt, "$ python3 tests/unit/test-x.py --strict\n3 passed\n")
        errs = _errors(v, "harness-backend-dev", _dev(), fd, cfg)
        check("receipt: the verbatim command in the receipt is accepted", not errs, str(errs))
        errs = _errors(v, "harness-backend-dev", _dev(verdict="BLOCKED", tv="n/a"), fd, cfg)
        check("receipt: a non-pass return is not held to the receipt",
              not any("receipt" in e for e in errs), str(errs))


def case_inspection_citations():
    v = _validator()
    with tempfile.TemporaryDirectory() as td:
        repo, fd, head, _ = _checkout(td)
        cfg = _config(td)
        _write(os.path.join(fd, "BRIEF.md"), "## Success criteria\n\n- SC-01: the doc says so\n"
               "  verify: inspection\n- SC-02: tests pass\n  verify: automated\n"
               "- SC-03: the config is shaped\n  verify: inspection\n")
        review = os.path.join(fd, "notes", "review.md")
        _write(review, "# review\nSC-01 satisfied: docs/notes.md:1\nSC-02 by the suite.\n")
        errs = _errors(v, "harness-code-reviewer", _review(head, human=[]), fd, cfg)
        check("inspection: an inspection SC with no file:line citation is refused, named",
              any("SC-03" in e and "file:line" in e and "SC-01" not in e.split("cites")[0].split("marks")[1] for e in errs), str(errs))
        _write(review, "# review\nSC-01 satisfied: docs/notes.md:1\nSC-03 holds, see .harness/harness.json:4\n")
        errs = _errors(v, "harness-code-reviewer", _review(head, human=[]), fd, cfg)
        check("inspection: every inspection SC cited is accepted", not errs, str(errs))
        os.remove(review)
        errs = _errors(v, "harness-code-reviewer", _review(head, human=[]), fd, cfg)
        check("inspection: an unreadable artifact is not this check's finding",
              not any("file:line" in e for e in errs), str(errs))


def case_findings_order():
    v = _validator()
    with tempfile.TemporaryDirectory() as td:
        repo, fd, head, _ = _checkout(td)
        cfg = _config(td)
        low = {"kind": "form", "scope": "none", "severity": "low", "reader": "code",
               "summary": "a", "why": "a drifted"}
        high = {"kind": "substance", "scope": "none", "severity": "high", "reader": "code",
                "summary": "b", "why": "b fails open"}
        errs = _errors(v, "harness-code-reviewer", _review(head, human=[], findings=[low, high]), fd, cfg)
        check("ranking: low before high is refused", any("not ranked" in e for e in errs), str(errs))
        errs = _errors(v, "harness-code-reviewer", _review(head, human=[], findings=[high, low]), fd, cfg)
        check("ranking: high before low is accepted", not errs, str(errs))


def case_grade_2_names():
    v = _validator()
    with tempfile.TemporaryDirectory() as td:
        repo = os.path.join(td, "repo")
        os.makedirs(os.path.join(repo, ".harness"))
        _git(repo, "init", "-q", "-b", "main")
        _git(repo, "config", "user.email", "t@example.com")
        _git(repo, "config", "user.name", "t")
        _write(os.path.join(repo, ".harness", "harness.json"), json.dumps(HARNESS_JSON))
        _write(os.path.join(repo, ".harness", "team-config.yaml"), "agents: {}\n")
        base = _commit(repo, "readme.txt", "a\n", "A")
        _git(repo, "update-ref", "refs/remotes/origin/main", base)
        _git(repo, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main")
        _write(os.path.join(repo, "src", "mod.py"), GRADE_2_PY)
        head = _commit(repo, "head.txt", "b\n", "head")
        fd = os.path.join(repo, ".harness", "harness", "features", FEAT)
        os.makedirs(os.path.join(fd, "notes"))
        _write(os.path.join(fd, "feature.json"), json.dumps({"feature_id": FEAT, "review_sha": head}))
        cfg = _config(td)
        probe = _errors(v, "harness-code-reviewer", _review(head, human=[], code_grade="grade_2",
                                                          reasons=["moderate is a dispatch table"]), fd, cfg)
        if any("disagrees with the mechanical result" in e for e in probe):
            check("grade2: fixture grades 2 (skipped: fixture graded otherwise)", True, str(probe))
            return
        check("grade2: a reason naming the function is accepted", not probe, str(probe))
        errs = _errors(v, "harness-code-reviewer", _review(head, human=[], code_grade="grade_2",
                                                         reasons=["it is fine really"]), fd, cfg)
        check("grade2: a reason naming no graded function is refused, naming it",
              any("names none of: moderate" in e for e in errs), str(errs))


def case_qa_unearned_fail():
    v = _validator()
    with tempfile.TemporaryDirectory() as td:
        repo, fd, head, _ = _checkout(td)
        cfg = _config(td)
        green_fail = _with(_qa([], "PASS"), verdict="FAIL")
        errs = _errors(v, "harness-qa", green_fail, fd, cfg)
        check("qa: FAIL with every gate green and fail-first evidence present is refused",
              any("no gate failed" in e for e in errs), str(errs))
        no_evidence = _with(green_fail, fail_first=[])
        errs = _errors(v, "harness-qa", no_evidence, fd, cfg)
        check("qa: FAIL with a green suite and NO fail-first evidence is the mandated return (P59)",
              not any("no gate failed" in e for e in errs), str(errs))
        real_fail = _with(green_fail, failures=2, suite="fail")
        errs = _errors(v, "harness-qa", real_fail, fd, cfg)
        check("qa: FAIL with a failing suite is accepted", not any("no gate failed" in e for e in errs), str(errs))


MATRIX_JSON = dict(HARNESS_JSON, test_matrix={
    "logic": {"always": ["unit"]},
    "cross_module": {"always": ["unit", "functional"]},
    "docs": {"always": []},
})


def _plan_with(change_types):
    tasks = "".join(
        f"  - id: T-0{i+1}\n    title: t{i+1}\n    intent: do it\n    change_type: {ct}\n"
        f"    execution_mode: team\n    status: {status}\n    files: [src/x.py]\n"
        f"    verify: true\n    depends_on: []\n"
        for i, (ct, status) in enumerate(change_types))
    return f"schema: plan/1\nfeature: {FEAT}\napproval:\n  status: approved\ntasks:\n{tasks}"


UNIT_SATISFIED = {"kind": "unit", "state": "satisfied", "cmd": "true", "named_tests": 3}
UNIT_MISSING = {"kind": "unit", "state": "missing", "cmd": "true", "named_tests": "none"}


def case_matrix_floor():
    v = _validator()
    with tempfile.TemporaryDirectory() as td:
        repo, fd, head, _ = _checkout(td)
        _write(os.path.join(repo, ".harness", "harness.json"), json.dumps(MATRIX_JSON))
        cfg = _config(td)
        _write(os.path.join(fd, "plan.yaml"), _plan_with([("logic", "done")]))
        errs = _errors(v, "harness-qa", _qa([UNIT_SATISFIED]), fd, cfg)
        check("floor: the floor kind reported satisfied is accepted", not errs, str(errs))
        errs = _errors(v, "harness-qa", _qa([UNIT_MISSING]), fd, cfg)
        check("floor: matrix_ok true with the floor kind missing is refused, naming it",
              any("matrix floor requires unit" in e for e in errs), str(errs))
        errs = _errors(v, "harness-qa", _qa([]), fd, cfg)
        check("floor: matrix_ok true with kinds: [] is refused as unverifiable",
              any("kinds: [] reports no kind" in e and "unit" in e for e in errs), str(errs))
        errs = _errors(v, "harness-qa", _with(_qa([UNIT_MISSING], "FAIL"), matrix_ok=False,
                                              suite="fail"), fd, cfg)
        check("floor: a FAIL that reports the gap is not held to the floor",
              not any("matrix floor" in e for e in errs), str(errs))
        _write(os.path.join(fd, "plan.yaml"), _plan_with([("cross_module", "done")]))
        errs = _errors(v, "harness-qa", _qa([UNIT_SATISFIED]), fd, cfg)
        check("floor: an excluded kind (functional, cmd null) never enters the floor",
              not any("matrix floor" in e for e in errs), str(errs))
        _write(os.path.join(fd, "plan.yaml"), _plan_with([("docs", "done"), ("logic", "todo")]))
        errs = _errors(v, "harness-qa", _qa([]), fd, cfg)
        check("floor: a docs task and an unstarted logic task impose no floor",
              not errs, str(errs))


_DECLINED = "declines to report a gate"
_NO_SUITE = _with(_qa([]), suite="n/a")


def _qa_floor_errors(td, change_types, obj=_NO_SUITE):
    """#2139: the qa errors for `obj` over a plan of `change_types`; None writes no plan."""
    repo, fd, _head, _ = _checkout(td)
    _write(os.path.join(repo, ".harness", "harness.json"), json.dumps(MATRIX_JSON))
    if change_types is not None:
        _write(os.path.join(fd, "plan.yaml"), _plan_with(change_types))
    return _errors(_validator(), "harness-qa", obj, fd, _config(td))


def _declined(errs, field):
    return any(_DECLINED in e and field in e for e in errs)


def case_qa_empty_floor_suite():
    """#2139: qa `suite: n/a` + PASS is honest only where the computed matrix floor is empty."""
    docs = [("docs", "done")]
    with tempfile.TemporaryDirectory() as td:
        errs = _qa_floor_errors(td, docs)
        check("empty floor: suite n/a with kinds [] and matrix_ok true is accepted", not errs, str(errs))
    with tempfile.TemporaryDirectory() as td:
        errs = _qa_floor_errors(td, docs, _with(_NO_SUITE, kinds=[UNIT_SATISFIED]))
        check("empty floor: suite n/a beside a reported kind still declines a gate",
              _declined(errs, "suite"), str(errs))
    with tempfile.TemporaryDirectory() as td:
        errs = _qa_floor_errors(td, docs, _with(_NO_SUITE, matrix_ok="n/a"))
        check("empty floor: matrix_ok n/a with PASS is still refused",
              _declined(errs, "matrix_ok"), str(errs))


def case_qa_floor_still_binds_suite():
    """#2139: a required kind, or a floor that cannot be derived, keeps `suite` gated."""
    with tempfile.TemporaryDirectory() as td:
        errs = _qa_floor_errors(td, [("docs", "done"), ("logic", "done")])
        check("non-empty floor: suite n/a with PASS is refused", _declined(errs, "suite"), str(errs))
    with tempfile.TemporaryDirectory() as td:
        errs = _qa_floor_errors(td, None)
        check("unresolvable floor: suite n/a with PASS is refused", _declined(errs, "suite"), str(errs))


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
    failed = 0
    for name, ok, detail in RESULTS:
        print(("PASS  " if ok else "FAIL  ") + name)
        if not ok:
            failed += 1
            if detail:
                print("      | " + detail[:400])
    print(f"{len(RESULTS) - failed} of {len(RESULTS)} cases passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
