"""FEAT-2581 SC-02 grade bar. Usage, from any checkout of the repository (also piped to `python3 -`):
    feat2581-grade-assert.py --ref <sha>

Reads feature-record.py and every feature_record/*.py at <sha>, and the baseline's feature-record.py
and feature_schema.py, through `git show`, never from a checkout, and grades them with the current
tree's code_grade.py. The repository is found from the working directory, never this file's path.

At a ref holding feature_record/: exit 0 only when every function grades 4 or better, the twelve
baseline below-bar functions sit at their owners at 4 or better, and every other moved function
keeps its baseline qualified name and grade; new functions are listed separately.
At a ref without feature_record/: one `below_bar: <qualname> <grade>` line per function below 4, exit 1."""
import importlib.util
import subprocess
import sys

BASE = "e12381fde910eb05728004476a10d741d6918010"
BIN = ".claude/skills/harness/bin/"
ROOT = subprocess.run(["git", "rev-parse", "--show-toplevel"], check=True, capture_output=True,
                      text=True).stdout.strip()
TWELVE = {"main": "feature-record.py", "_close_refused_run.mutate": "feature_record/runs.py",
          "cmd_record_history.mutate": "feature_record/runs.py", "_run_end_digest": "feature_record/runs.py",
          "_record_run_end.mutate": "feature_record/runs.py", "spend_for": "feature_record/spend.py",
          "recovery_command_for": "feature_record/schema.py", "verify_evidence_ref": "feature_record/evidence.py",
          "run_evidence_problems": "feature_record/evidence.py",
          "mirror_provenance_problem": "feature_record/binding.py",
          "_runs_agent_problems": "feature_record/schema.py", "_problems_for_doc": "feature_record/schema.py"}


def show(ref, path):
    proc = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (ref, path)], capture_output=True)
    return proc.stdout.decode("utf-8") if proc.returncode == 0 else None


def grader():
    spec = importlib.util.spec_from_file_location("feat2581_code_grade", ROOT + "/" + BIN + "code_grade.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def grade(cg, ref, files):
    rows = {}
    for rel in files:
        text = show(ref, BIN + rel)
        if text is None:
            continue
        for row in cg.grade_source(text, rel):
            rows[row.qualname] = (row.grade, rel)
    return rows


def package_files(ref):
    proc = subprocess.run(["git", "-C", ROOT, "ls-tree", "--name-only", "%s:%sfeature_record" % (ref, BIN)],
                          capture_output=True, text=True)
    return ["feature_record/" + n for n in proc.stdout.split() if n.endswith(".py")] if proc.returncode == 0 else []


def below_bar_report(cg, ref):
    """A ref without feature_record/: list the functions below 4 and refuse."""
    below = sorted((q, g) for q, (g, _) in grade(cg, ref, ["feature-record.py", "feature_schema.py"]).items() if g < 4)
    for qualname, value in below:
        print("below_bar: %s %d" % (qualname, value))
    return 1


def placement_problems(rows):
    """Below-bar functions, then any of the twelve not at its owner."""
    problems = ["below bar: %s %d (%s)" % (q, g, p) for q, (g, p) in sorted(rows.items()) if g < 4]
    return problems + ["twelve: %s not at %s (found %s)" % (q, owner, rows.get(q, (None, "absent"))[1])
                       for q, owner in sorted(TWELVE.items()) if rows.get(q, (None, None))[1] != owner]


def drift_problems(rows, baseline, moved, ref):
    """Moved functions whose grade changed, then baseline functions that vanished."""
    problems = ["moved: %s grade %d at the baseline, %d at %s" % (q, baseline[q][0], rows[q][0], ref[:12])
                for q in moved if rows[q][0] != baseline[q][0]]
    # A nested helper of one of the twelve is rewritten with its owner, not moved.
    return problems + ["missing: %s (baseline %s)" % (q, baseline[q][1]) for q in sorted(baseline)
                       if q not in rows and q.split(".")[0] not in TWELVE]


def report(rows, baseline, moved, problems, files):
    for qualname in sorted(TWELVE):
        print("twelve: %s %s -> %s at %s" % (qualname, baseline.get(qualname, (None,))[0],
                                              rows.get(qualname, (None,))[0], TWELVE[qualname]))
    print("moved, grade kept: %d" % len(moved))
    for qualname in sorted(q for q in rows if q not in baseline):
        print("new: %s %d %s" % (qualname, rows[qualname][0], rows[qualname][1]))
    for problem in problems:
        print("RED " + problem)
    print("grade_bar %s: %d function(s) over %d file(s)" % ("RED" if problems else "GREEN", len(rows), files))
    return 1 if problems else 0


def main():
    ref = sys.argv[sys.argv.index("--ref") + 1]
    cg = grader()
    package = package_files(ref)
    if not package:
        sys.exit(below_bar_report(cg, ref))
    rows = grade(cg, ref, ["feature-record.py", *package])
    baseline = grade(cg, BASE, ["feature-record.py", "feature_schema.py"])
    moved = sorted(q for q in rows if q in baseline and q not in TWELVE)
    problems = placement_problems(rows) + drift_problems(rows, baseline, moved, ref)
    sys.exit(report(rows, baseline, moved, problems, 1 + len(package)))


main()
