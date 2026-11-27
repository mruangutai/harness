"""Grade touched functions: working tree vs base b788e9da and HEAD 15a240bc (no git writes)."""
import subprocess, sys
sys.path.insert(0, ".claude/skills/harness/bin")
from code_grade import grade_source
FILES = {
 ".claude/skills/harness/bin/gh-sync.py": ["ensure_labels", "mirror_labels", "_label_abandoned", "cmd_abandon",
     "cmd_abandon._close_and_reseat", "_RejectWrites.label", "_open_ensure_labels", "_finish_replacement"],
 "tests/integration/test-gh-sync-abandon.py": ["_label_create_failure_run", "_closed_and_reseated",
     "_check_named_create_failure", "_check_abandon_label_gap", "abandon_label_create_failure_case",
     "_wrote_after_label", "reject_label_create_failure_case", "main"],
 "tests/integration/gh_sync_support.py": ["label_create_fails"],
}
def grades(src, path):
    return {g.qualname: g for g in grade_source(src, path)}
for path, names in FILES.items():
    work = grades(open(path).read(), path)
    revs = {}
    for rev in ("b788e9da", "15a240bc"):
        try:
            revs[rev] = grades(subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True, text=True, check=True).stdout, path)
        except subprocess.CalledProcessError:
            revs[rev] = {}
    for n in names:
        w = work.get(n)
        old = " ".join(f"{r}={revs[r][n].grade if n in revs[r] else '-'}" for r in revs)
        if w is None:
            print(f"{path} {n}: MISSING"); continue
        print(f"{path} {n}: grade={w.grade} cyc={w.cyclomatic} cog={w.cognitive} abc={w.abc} driver={w.driver} | {old}")
