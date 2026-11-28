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
from unit_support import ROOT, load_script

import os
import shutil
import sys
import tempfile
from pathlib import Path

import feature_corpus  # noqa: E402
from check_support import Checks

refs = load_script("check-skill-refs.py")

C = Checks()
check = C.check

UAT = "harness-uat/SKILL.md"

# Each defect class: the line planted in UAT, and the text its finding must carry.
CASES = {
    "deleted_dec": ("History: DEC-210.", "cites DEC-210"),
    "unimplemented_inv": ("Backlog it too (INV-20).", "cites INV-20"),
    "missing_path": ("Read `<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/references/no-such-file.md`.",
                     "no-such-file.md"),
    "missing_heading": ("Per `harness-code-review` § Nonexistent Heading.", "§ Nonexistent Heading"),
    "unknown_name": ("See `harness-review`.", "names `harness-review`"),
    "claude_spelling": ("Open `.claude/skills/harness-brief/SKILL.md`.", "spells the skills tree"),
}


def copy_tree(dst: Path) -> None:
    """Everything the resolver may touch, minus .git and .claude/worktrees. The copy is not a git
    checkout, so it must hold the whole corpus itself: a sparse worktree's other features come
    from the main corpus (FEAT-1559), exactly where the live scan reads them."""
    for rel in (".claude/skills", ".omp", ".harness", "docs"):
        shutil.copytree(ROOT / rel, dst / rel, symlinks=True,
                        ignore=shutil.ignore_patterns("worktrees", "__pycache__"))
    owner = Path(feature_corpus.owner_root(str(ROOT)))
    for segment, fid, path in feature_corpus.landed_dirs(str(owner)):
        target = dst / ".harness" / segment / "features" / fid
        if not target.exists():
            shutil.copytree(path, target, symlinks=True)
    (dst / ".agents").mkdir()
    os.symlink(os.readlink(ROOT / ".agents" / "skills"), dst / ".agents" / "skills")


def plant(dst: Path, rel: str, text: str) -> None:
    path = dst / ".claude" / "skills" / rel
    with open(path, "a", encoding="utf-8") as fh:
        fh.write("\n" + text + "\n")


def restore(dst: Path, rel: str) -> None:
    """Put one planted file back to the committed copy, so the next scenario starts clean."""
    shutil.copy2(ROOT / ".claude" / "skills" / rel, dst / ".claude" / "skills" / rel)


def check_defect_classes(dst: Path) -> None:
    for line, _ in CASES.values():
        plant(dst, UAT, line)
    findings = refs.scan(dst)
    joined = "\n".join(findings)
    for name, (_, needle) in CASES.items():
        check(f"catches_{name}", needle in joined, f"{needle!r} not in findings")
    check("every_finding_names_the_planted_file",
          all(f.startswith(UAT + ":") for f in findings), joined)


def check_package_numbers(dst: Path) -> None:
    """FEAT-69: the invariants live in check_state/*.py beside the entry. A number only a family
    module spells is implemented; an unspelled one is still not; spelling a number twice in a
    skill is one finding, not two."""
    plant(dst, "harness/bin/check_state/host.py", "# INV-777: spelled in a family module only")
    plant(dst, UAT, "Graded by INV-777; INV-20 twice (INV-20).")
    findings = refs.scan(dst)
    joined = "\n".join(findings)
    check("package_only_number_is_implemented", not any("INV-777" in f for f in findings), joined)
    check("unspelled_number_is_still_a_finding", sum("cites INV-20" in f for f in findings) == 1, joined)


def main() -> int:
    clean = refs.scan(ROOT)
    check("committed_tree_is_clean", not clean, "; ".join(clean[:5]))

    # One copy serves both scenarios: the first plants only UAT, which is restored before the
    # second plants, so each scan sees exactly its own plants.
    with tempfile.TemporaryDirectory() as tmp:
        dst = Path(tmp)
        copy_tree(dst)
        check_defect_classes(dst)
        restore(dst, UAT)
        check_package_numbers(dst)

    return C.report()


if __name__ == "__main__":
    sys.exit(main())
