"""FEAT-69 SC-01 lock, run from a checkout root. Exit 0 (green) only when: check-state.py and the
complete expected check_state/ package exist; EVERY function on that surface grades >= 4;
_inv41_invocation, _unquoted_hash_digit, _quoted_scalar_closed and inv_49 are present. With
FEAT69_BASELINE_JSON set, every function is also classified MOVED (same qualname at baseline; grade
must not drop) or NEW (graded as new, bar 4, no exemption). Against the baseline tree it is RED:
no package, four functions below 4."""
import importlib.util, json, os, pathlib, sys

root = pathlib.Path(".")
BIN = root / ".claude/skills/harness/bin"
spec = importlib.util.spec_from_file_location("feat69_code_grade", BIN / "code_grade.py")
cg = importlib.util.module_from_spec(spec); sys.modules[spec.name] = cg; spec.loader.exec_module(cg)
EXPECTED = {"__init__.py", "ctx.py", "table.py", "runner.py", "plan.py", "feature_record.py", "run_state.py",
            "seams.py", "brief.py", "worktrees.py", "board.py", "host.py"}
REQUIRED = {"_inv41_invocation", "_unquoted_hash_digit", "_quoted_scalar_closed", "inv_49"}
pkg = BIN / "check_state"
present = {p.name for p in pkg.glob("*.py")} if pkg.is_dir() else set()
paths = [BIN / "check-state.py", *sorted(pkg.glob("*.py"))]
rows = [r for p in paths for r in cg.grade_source(p.read_text(encoding="utf-8"), str(p.relative_to(root)))]
bad = [(r.path, r.qualname, r.grade) for r in rows if r.grade < 4]
names = {r.qualname for r in rows}
problems = []
if present != EXPECTED:
    problems.append(f"package files present {sorted(present)} != expected {sorted(EXPECTED)}")
if bad:
    problems.append(f"below bar 4: {bad}")
if not REQUIRED <= names:
    problems.append(f"required functions absent: {sorted(REQUIRED - names)}")
baseline = os.environ.get("FEAT69_BASELINE_JSON")
if baseline:
    base = {g["qualname"]: g for g in json.load(open(baseline))["code_grade"]["functions"]}
    moved = [(r.qualname, base[r.qualname]["grade"], r.grade) for r in rows if r.qualname in base]
    new = [(r.qualname, r.grade) for r in rows if r.qualname not in base]
    dropped = [m for m in moved if m[2] < m[1]]
    if dropped:
        problems.append(f"moved functions whose grade DROPPED vs the baseline pre-image: {dropped}")
    print(f"moved: {len(moved)} (grade kept or raised: {len(moved) - len(dropped)}); new: {len(new)} -> {new}")
print(f"{len(rows)} function(s) over {len(paths)} file(s): " + ", ".join(
    f"{g} -> {sum(1 for r in rows if r.grade == g)}" for g in (5, 4, 3, 2, 1)))
if problems:
    print("RED:\n  " + "\n  ".join(problems)); sys.exit(1)
print("GREEN: every function on check-state.py + check_state/** at grade >= 4; required functions present")
