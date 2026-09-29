"""FEAT-70 SC-01 lock. Usage, from any checkout of the repository:
    python3 feat70-grade-assert.py <pin-sha> <baseline-sha> [--tree <sha-to-grade>]

Both trees are read from git objects (`git archive`), never from a working tree, so the receipt cannot
be about uncommitted bytes. The graded tree is the pin unless `--tree` names another commit (the
red-first run grades the baseline). GREEN (exit 0) only when, in the graded tree:
  - plan-merge.py exists and plan_merge/ holds exactly the eleven expected files;
  - EVERY function on that surface grades >= 4;
  - the twelve baseline below-bar identities are present at their package owners;
  - `signed_task_hash` is importable from the entry;
  - against the baseline monolith as the pre-image table: every moved function (same qualified
    identity) whose body is UNCHANGED keeps its exact grade; the twelve named functions reach >= 4;
    every changed-body or new function grades >= 4 and is listed.
Against the baseline tree it is RED: no package, twelve functions below 4."""
import ast, importlib.util, os, pathlib, subprocess, sys, tarfile, tempfile

pin, baseline = sys.argv[1], sys.argv[2]
graded = sys.argv[sys.argv.index("--tree") + 1] if "--tree" in sys.argv else pin
REPO = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
BIN = ".claude/skills/harness/bin"
EXPECTED = {"__init__.py", "text.py", "guards.py", "union.py", "approval.py", "stations.py", "panel.py",
            "amend.py", "amendments.py", "delete.py", "check.py"}
TWELVE = {"_task_status_line": "stations.py", "_verify_spliced": "union.py", "cmd_amend": "amend.py",
          "cmd_amend.transform": "amend.py", "_item_range": "text.py", "_index_list_items": "text.py",
          "_find_field_line": "text.py", "_parsed_value": "text.py", "_index_top_keys": "text.py",
          "_print_apply_receipt": "union.py", "_panel_own_end": "panel.py", "_replace_fields": "union.py"}


def export(sha):
    d = pathlib.Path(tempfile.mkdtemp(prefix=f"feat70-tree-{sha[:8]}-"))
    tar = subprocess.run(["git", "-C", REPO, "archive", sha, BIN], check=True, capture_output=True).stdout
    with tarfile.open(fileobj=__import__("io").BytesIO(tar)) as tf:
        tf.extractall(d, filter="data")
    return d


def grader(tree):
    spec = importlib.util.spec_from_file_location(f"feat70_code_grade_{tree.name}", tree / BIN / "code_grade.py")
    cg = importlib.util.module_from_spec(spec); sys.modules[spec.name] = cg; spec.loader.exec_module(cg)
    return cg


def _nested_defs(node):
    """The FunctionDefs inside a top-level def/class, keyed `outer.inner` (one level, as code_grade)."""
    return {f"{node.name}.{sub.name}": sub for sub in ast.walk(node)
            if isinstance(sub, ast.FunctionDef) and sub is not node}


def bodies(path):
    """{qualname: ast dump of the def, line numbers stripped} for top-level and one-deep nested defs."""
    out = {}
    tops = [n for n in ast.parse(path.read_text(encoding="utf-8")).body if isinstance(n, (ast.FunctionDef, ast.ClassDef))]
    for node in tops:
        out[node.name] = ast.dump(node, include_attributes=False)
        out.update({q: ast.dump(sub, include_attributes=False) for q, sub in _nested_defs(node).items()})
    return out


def surface(tree):
    entry = tree / BIN / "plan-merge.py"
    pkg = tree / BIN / "plan_merge"
    paths = [entry, *sorted(pkg.glob("*.py"))] if pkg.is_dir() else [entry]
    return entry, pkg, paths


g_tree, b_tree = export(graded), export(baseline)
cg = grader(g_tree)
entry, pkg, paths = surface(g_tree)
present = {p.name for p in pkg.glob("*.py")} if pkg.is_dir() else set()
rows = [r for p in paths for r in cg.grade_source(p.read_text(encoding="utf-8"), str(p.relative_to(g_tree)))]
grade = {r.qualname: (r.grade, r.path) for r in rows}
bad = [(r.path, r.qualname, r.grade) for r in rows if r.grade < 4]
problems = []
if present != EXPECTED:
    problems.append(f"package files present {sorted(present)} != expected {sorted(EXPECTED)}")
if bad:
    problems.append(f"below bar 4: {bad}")
misplaced = [(q, owner, grade.get(q, (None, "absent"))[1]) for q, owner in TWELVE.items()
             if q not in grade or not grade[q][1].endswith("plan_merge/" + owner)]
if misplaced:
    problems.append(f"twelve named functions not at their owners (qualname, expected owner, found): {misplaced}")
try:
    # Sibling imports derive the harness root at import time; the exported tree has no .harness,
    # so the import is pointed at this repository's root. The import surface is what is tested.
    os.environ.setdefault("HARNESS_PROJECT_DIR", REPO)
    sys.path.insert(0, str(g_tree / BIN))
    spec = importlib.util.spec_from_file_location("feat70_entry", entry)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    if not callable(getattr(mod, "signed_task_hash", None)):
        problems.append("signed_task_hash is not importable from the entry")
except Exception as exc:  # the entry failing to import IS the finding
    problems.append(f"entry does not import: {exc!r}")

# Pre-image table: the baseline monolith graded by ITS OWN grader.
bcg = grader(b_tree)
b_entry = b_tree / BIN / "plan-merge.py"
b_rows = {r.qualname: r.grade for r in bcg.grade_source(b_entry.read_text(encoding="utf-8"), "plan-merge.py")}
b_bodies = bodies(b_entry)
g_bodies = {}
for p in paths:
    g_bodies.update(bodies(p))
moved_same, moved_changed, new = [], [], []
for q, (g, path) in sorted(grade.items()):
    if q not in b_rows:
        new.append((q, g, path))
    elif b_bodies.get(q) == g_bodies.get(q):
        moved_same.append((q, b_rows[q], g))
    else:
        moved_changed.append((q, b_rows[q], g))
identity_broken = [m for m in moved_same if m[1] != m[2]]
if identity_broken:
    problems.append(f"moved functions with UNCHANGED bodies whose grade changed: {identity_broken}")
not_improved = [(q, b_rows.get(q), grade.get(q, (None,))[0]) for q in TWELVE
                if q in grade and grade[q][0] < 4]
if not_improved:
    problems.append(f"named functions still below 4: {not_improved}")
print(f"graded tree {graded}: {len(rows)} function(s) over {len(paths)} file(s): " + ", ".join(
    f"{g} -> {sum(1 for r in rows if r.grade == g)}" for g in (5, 4, 3, 2, 1)))
print(f"pre-image {baseline}: {len(b_rows)} function(s) in the monolith")
print(f"moved, body unchanged (grade identity required): {len(moved_same)}")
print(f"moved, body changed (>= 4 required): {len(moved_changed)} -> {[(q, b, g) for q, b, g in moved_changed]}")
print(f"new (>= 4 required): {len(new)} -> {[(q, g) for q, g, _ in new]}")
print("twelve named: " + ", ".join(f"{q} {b_rows.get(q)}->{grade.get(q, (None,))[0]}" for q in TWELVE))
if problems:
    print("RED:\n  " + "\n  ".join(problems)); sys.exit(1)
print("GREEN: every function on plan-merge.py + plan_merge/** at grade >= 4; owners, identity, import all hold")
