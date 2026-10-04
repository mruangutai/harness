"""FEAT-69 SC-03 fail-first. Usage: python3 feat69-sc03-red.py <pin-sha> <baseline-sha>
Builds a scratch tree = the clean pin checkout (package, table, suites) with ONE file replaced by the
baseline's: .claude/skills/harness/bin/check-plan-routes.py (the pre-FEAT-69 lock). Runs the pin's
tests/integration/test-check-plan-routes.py there. Under the old lock the package is not walked, so
the FEAT-69 mutants (cross-module undeclared reads, a spawn two helpers deep, a row defined outside
its family, a package-file module-body violation, a package-file broad catch) go UNCAUGHT and the
case fails — the red. The same suite at the pin (the new lock) is green: the receipt records both."""
import os, shutil, subprocess, sys, tempfile

ROOT = "/Users/molchairuangutai/GitHub/harness"
pin, baseline = sys.argv[1], sys.argv[2]
WT = os.path.join(ROOT, ".claude/worktrees/harness")
pin_dir, base_dir = os.path.join(WT, f"feat69-cleanpin-{pin}"), os.path.join(WT, f"feat69-base-{baseline}")
for d in (pin_dir, base_dir):
    assert os.path.isdir(d) and not subprocess.check_output(["git", "-C", d, "status", "--porcelain"], text=True), d
scratch = os.path.join(tempfile.mkdtemp(prefix="feat69-sc03-"), "tree")
shutil.copytree(pin_dir, scratch, symlinks=True, ignore=shutil.ignore_patterns(".git", "__pycache__", "worktrees"))
old_lock = os.path.join(base_dir, ".claude/skills/harness/bin/check-plan-routes.py")
shutil.copy(old_lock, os.path.join(scratch, ".claude/skills/harness/bin/check-plan-routes.py"))
cmd = [sys.executable, "tests/integration/test-check-plan-routes.py"]
print(f"scratch tree: {scratch} = pin {pin} with baseline {baseline}'s check-plan-routes.py")
print(f"command (cwd={scratch}): {' '.join(cmd)}")
p = subprocess.run(cmd, cwd=scratch, capture_output=True, text=True, timeout=1800)
print(f"exit status: {p.returncode}")
lines = [l for l in p.stdout.splitlines() if l.startswith(("FAIL", "PASS feat69")) or "feat69" in l]
print("\n".join(lines[:40]))
print(p.stderr[-1500:])
shutil.rmtree(os.path.dirname(scratch), ignore_errors=True)
sys.exit(0 if p.returncode != 0 else 1)
