#!/usr/bin/env python3
"""INV-45: every reference a skill makes resolves. Two things must hold:

1. The committed tree is clean — the checker's own false-positive classes (a per-project
   override slot, a runtime marker, a step range written `§ 1–2`, a path relative to the
   citing file) are recognised, so a clean tree scans to zero findings.
2. Each defect class the checker exists for is caught when planted in a copy of the tree:
   a deleted DEC (DEC-210), an unimplemented INV (INV-20), a missing path, a heading the
   cited skill lacks, a name that is neither skill nor agent, and the `.claude/skills/`
   spelling in instruction prose. Every planted defect names its file.
"""
import importlib.util
import os
import shutil
import sys
import tempfile
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
ROOT = TESTS_DIR.parents[1]
BIN_DIR = ROOT / ".claude" / "skills" / "harness" / "bin"
sys.path.insert(0, str(BIN_DIR))

spec = importlib.util.spec_from_file_location("check_skill_refs", BIN_DIR / "check-skill-refs.py")
refs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(refs)

failures = []


def check(name, cond, detail=""):
    print(f"{'ok  ' if cond else 'FAIL'} {name}" + (f": {detail}" if not cond and detail else ""))
    if not cond:
        failures.append(name)


def copy_tree(dst: Path) -> None:
    """Everything the resolver may touch, minus .git and .claude/worktrees."""
    for rel in (".claude/skills", ".omp", ".harness", "docs"):
        shutil.copytree(ROOT / rel, dst / rel, symlinks=True,
                        ignore=shutil.ignore_patterns("worktrees", "__pycache__"))
    (dst / ".agents").mkdir()
    os.symlink(os.readlink(ROOT / ".agents" / "skills"), dst / ".agents" / "skills")


def plant(dst: Path, rel: str, text: str) -> None:
    path = dst / ".claude" / "skills" / rel
    with open(path, "a", encoding="utf-8") as fh:
        fh.write("\n" + text + "\n")


def main() -> int:
    clean = refs.scan(ROOT)
    check("committed_tree_is_clean", not clean, "; ".join(clean[:5]))

    with tempfile.TemporaryDirectory() as tmp:
        dst = Path(tmp)
        copy_tree(dst)
        plant(dst, "harness-uat/SKILL.md", "History: DEC-210.")
        plant(dst, "harness-uat/SKILL.md", "Backlog it too (INV-20).")
        plant(dst, "harness-uat/SKILL.md", "Read `<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/references/no-such-file.md`.")
        plant(dst, "harness-uat/SKILL.md", "Per `harness-code-review` § Nonexistent Heading.")
        plant(dst, "harness-uat/SKILL.md", "See `harness-review`.")
        plant(dst, "harness-uat/SKILL.md", "Open `.claude/skills/harness-brief/SKILL.md`.")
        findings = refs.scan(dst)
        joined = "\n".join(findings)
        expected = {
            "deleted_dec": "cites DEC-210",
            "unimplemented_inv": "cites INV-20",
            "missing_path": "no-such-file.md",
            "missing_heading": "§ Nonexistent Heading",
            "unknown_name": "names `harness-review`",
            "claude_spelling": "spells the skills tree",
        }
        for name, needle in expected.items():
            check(f"catches_{name}", needle in joined, f"{needle!r} not in findings")
        check("every_finding_names_the_planted_file",
              all(f.startswith("harness-uat/SKILL.md:") for f in findings), joined)

    if failures:
        print(f"\n{len(failures)} failure(s): {failures}")
        return 1
    print("\nall checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
