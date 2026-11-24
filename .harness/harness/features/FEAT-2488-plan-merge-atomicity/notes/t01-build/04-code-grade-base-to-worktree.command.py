# code_grade's own base..head gate (_gate_file_records semantics: gated = new, or graded lower
# than its base pre-image) with base 2491336e and the head read from the WORKING TREE, because
# git writes (commit/commit-tree) are barred. Run from the worktree root.
import subprocess, sys
from pathlib import Path
sys.path.insert(0, ".claude/skills/harness/bin")
import code_grade, artifact_accessors
BASE = "2491336e"
root = Path.cwd()
test_kinds = artifact_accessors.load_harness_json(root / ".harness" / "harness.json")["test_kinds"]
base_oid = code_grade.commit_oid(root, BASE)
status = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], text=True, capture_output=True).stdout
changed = subprocess.run(["git", "diff", "--name-only", base_oid, "--", "*.py"], text=True, capture_output=True).stdout.split()
untracked = [l[3:] for l in status.splitlines() if l.startswith("??") and l.endswith(".py")]
paths = sorted(p for p in set(changed + untracked) if not p.startswith(".harness/"))
gated, informational = [], []
for path in paths:
    head_source = (root / path).read_text()
    base_source = code_grade._resolve_base_source(root, base_oid, path, None)
    before_names, before_hashes = code_grade._pre_images(base_source) if base_source else ({}, {})
    head_hashes = code_grade._body_hashes(head_source)
    for record in code_grade.grade_source(head_source, path):
        before = code_grade._resolve_pre_image(record, before_names, before_hashes, head_hashes)
        (gated if before is None or record.grade < before.grade else informational).append((record, before))
records, result = code_grade.classify([r for r, _ in gated], test_kinds)
print(f"# code_grade gate, base {BASE} .. working tree (HEAD {subprocess.run(['git','rev-parse','--short','HEAD'],text=True,capture_output=True).stdout.strip()} + T-01 edits), files: {len(paths)}")
for p in paths:
    print(f"# file: {p}")
for rec in sorted(records, key=lambda r: (r["path"], r["line"])):
    print(f"{rec['result']} {rec['path']}:{rec['line']} {rec['qualname']} grade={rec['grade']} bar={rec['bar']} "
          f"cc={rec['cyclomatic']} cog={rec['cognitive']} abc={rec['abc']} driver={rec['driver']}"
          + (f" SEVERITY={rec['severity']}" if rec['severity'] else ""))
for r, b in informational:
    print(f"INFO (not gated: grade {r.grade} >= base {b.grade}) {r.path}:{r.lineno} {r.qualname}")
high = [r for r in records if r["severity"] == "high"]
print(f"gated={len(records)} high={len(high)} reason_required={sum(r['grade'] == 2 for r in records)} result={'fail' if high else 'pass'}")
sys.exit(1 if high else 0)
