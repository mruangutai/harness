#!/usr/bin/env python3
"""Three prose rules that became validator checks (consumer audit, 2026-09-18).

Each is a predicate over data the repository owns, exercised end to end through
`validate()` on a purpose-built git checkout — never by calling the helper alone, because
the plausible bug is a helper that exists and is never reached.

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


def _review(head, verdict="PASS", human=None):
    human_line = "" if human is None else f"  human_commits_in_scope: {human}\n"
    return f"""VERDICT: {verdict}
DIGEST:
  headline: reviewer result
  severity_max: low
  findings: []
  must_fix: []
  code_grade: n_a
  reviewed: "origin/main..{head}"
{human_line}  files_touched: []
  open_questions: []
  expertise_update: []
artifact: .harness/harness/features/{FEAT}/notes/review.md
"""


def _qa(kinds, verdict="PASS"):
    gate = "matrix_ok: true\n  suite: pass" if verdict == "PASS" else "matrix_ok: n/a\n  suite: n/a"
    return f"""VERDICT: {verdict}
DIGEST:
  headline: qa result
  {gate}
  failures: 0
  coverage_gaps: []
  fail_first: [{{ sc: SC-01, evidence: notes/fail.txt }}]
  kinds: {kinds}
  files_touched: []
  open_questions: []
  expertise_update: []
artifact: .harness/harness/features/{FEAT}/notes/qa.md
"""


def _errors(v, persona, text, feature_dir, config):
    return v.validate(persona, text, config, feature_dir, branch_override=None)


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
              not _errors(v, "harness-code-reviewer", _review(head, human=f"[{humans[0][:10]}]"), fd, cfg),
              str(_errors(v, "harness-code-reviewer", _review(head, human=f"[{humans[0][:10]}]"), fd, cfg)))
        errs = _errors(v, "harness-code-reviewer", _review(head, human="[]"), fd, cfg)
        check("human: an empty list over a range with a human commit is refused",
              any("human_commits_in_scope" in e and humans[0][:12] in e for e in errs), str(errs))
        errs = _errors(v, "harness-code-reviewer", _review(head), fd, cfg)
        check("human: omitting the field is the same refusal",
              any("human_commits_in_scope" in e for e in errs), str(errs))
        errs = _errors(v, "harness-code-reviewer",
                       _review(head, human=f"[{humans[0][:10]}, {humans[1][:10]}]"), fd, cfg)
        check("human: a bot commit claimed as human is refused and named",
              any("not in the range" in e and humans[1][:10] in e for e in errs), str(errs))
    with tempfile.TemporaryDirectory() as td:
        repo, fd, head, _ = _checkout(td)
        cfg = _config(td)
        check("human: no human commits and [] is accepted",
              not _errors(v, "harness-code-reviewer", _review(head, human="[]"), fd, cfg))


def case_dirty_tree():
    v = _validator()
    with tempfile.TemporaryDirectory() as td:
        repo, fd, head, _ = _checkout(td)
        cfg = _config(td)
        with open(os.path.join(repo, "readme.txt"), "a") as fh:
            fh.write("hand edit\n")
        for verdict in ("PASS", "FAIL"):
            errs = _errors(v, "harness-code-reviewer", _review(head, verdict, human="[]"), fd, cfg)
            check(f"dirty: a {verdict} over a modified tracked file is refused, naming it",
                  any("readme.txt" in e and "pinnable" in e for e in errs), str(errs))
        errs = _errors(v, "harness-code-reviewer", _review(head, "BLOCKED", human="[]"), fd, cfg)
        check("dirty: BLOCKED is the honest return and is accepted",
              not any("pinnable" in e for e in errs), str(errs))
        _git(repo, "checkout", "--", "readme.txt")
        with open(os.path.join(repo, ".harness", "harness.json"), "a") as fh:
            fh.write("\n")
        errs = _errors(v, "harness-code-reviewer", _review(head, human="[]"), fd, cfg)
        check("dirty: a change under .harness/ does not count",
              not any("pinnable" in e for e in errs), str(errs))
        _git(repo, "checkout", "--", ".harness/harness.json")
        with open(os.path.join(repo, "scratch.txt"), "w") as fh:
            fh.write("untracked\n")
        errs = _errors(v, "harness-code-reviewer", _review(head, human="[]"), fd, cfg)
        check("dirty: an untracked file does not count",
              not any("pinnable" in e for e in errs), str(errs))


def case_qa_kinds():
    v = _validator()
    with tempfile.TemporaryDirectory() as td:
        repo, fd, head, _ = _checkout(td)
        cfg = _config(td)
        ok = "[{ kind: unit, state: satisfied, cmd: true, named_tests: 3 }, { kind: functional, state: not_applicable }]"
        check("kinds: satisfied on a runnable kind and not_applicable on an excluded one pass",
              not _errors(v, "harness-qa", _qa(ok), fd, cfg),
              str(_errors(v, "harness-qa", _qa(ok), fd, cfg)))
        errs = _errors(v, "harness-qa", _qa("[{ kind: unit, state: green }]"), fd, cfg)
        check("kinds: an unknown state is refused", any("state='green'" in e for e in errs), str(errs))
        errs = _errors(v, "harness-qa", _qa("[{ kind: unit, state: misconfigured }]", "FAIL"), fd, cfg)
        check("kinds: misconfigured under a FAIL verdict is refused",
              any("misconfigured" in e and "BLOCKED" in e for e in errs), str(errs))
        errs = _errors(v, "harness-qa", _qa("[{ kind: unit, state: misconfigured }]", "BLOCKED"), fd, cfg)
        check("kinds: misconfigured under BLOCKED is accepted",
              not any("misconfigured" in e for e in errs), str(errs))
        errs = _errors(v, "harness-qa", _qa("[{ kind: unit, state: not_applicable }]"), fd, cfg)
        check("kinds: not_applicable on a kind with a runnable cmd is refused",
              any("not_applicable" in e and "runnable cmd" in e for e in errs), str(errs))
        errs = _errors(v, "harness-qa", _qa("[{ kind: functional, state: satisfied }]"), fd, cfg)
        check("kinds: satisfied on a kind with no cmd is refused",
              any("no cmd" in e for e in errs), str(errs))
        errs = _errors(v, "harness-qa", _qa("[{ kind: e2e, state: satisfied }]"), fd, cfg)
        check("kinds: a kind harness.json does not declare is refused",
              any("does not declare" in e for e in errs), str(errs))


def main():
    case_human_commits()
    case_dirty_tree()
    case_qa_kinds()
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
