#!/usr/bin/env python3
"""Every reference a skill makes must resolve (INV-45).

Skills are read by agents that cannot ask; a citation that points at nothing is a rule the
agent cannot follow and a validator will not catch. Scanned across every `SKILL.md`, every
`*/references/*.md` and every `harness/templates/**/*.md`:

- `DEC-NNN` resolves to a `## DEC-NNN` heading in DECISIONS.md (a deleted decision is cited by
  nothing — DEC-210 was, for two months);
- `INV-NN` appears in check-state.py (INV-20 was cited in harness-brief and never implemented);
- a backticked harness-owned path exists, once `<HARNESS_*_ROOT>` is stripped, unless it carries a
  glob or a `<placeholder>`;
- `` `harness-<skill>` § <heading> `` names a heading that skill actually has;
- `` `harness-<name>` `` names a skill or an agent that exists;
- instruction prose spells the skills tree `.agents/skills/`, never `.claude/skills/`
  (DEC-233; the `.claude/` spelling is for authoring only). Files that must carry the literal
  `.claude/` value — a `git config` line, the preserved harness-code-risk-grading — are exempt
  by name below.

Exit 1 on any finding; each line is `path: what`. Usage: check-skill-refs.py [root]
"""
from __future__ import annotations

import glob
import os
import re
import sys
from pathlib import Path

SKILLS_REL = Path(".claude") / "skills"
DECISIONS_REL = ".harness/harness/docs/DECISIONS.md"
CHECK_STATE_REL = SKILLS_REL / "harness" / "bin" / "check-state.py"
AGENTS_REL = Path(".omp") / "agents"

# `.claude/skills/` is the authoring path; these files legitimately spell it.
CLAUDE_SPELLING_EXEMPT = {
    "harness-code-risk-grading/SKILL.md",          # preserved verbatim by operator decision
    "harness/references/checkout-prereqs.md",      # `git config core.hooksPath .claude/...` literal
    "harness-init/SKILL.md",                       # authoring instructions for the skills tree
}

# Paths a skill may name that need not exist in this checkout: a per-project override slot
# ("resolve X first, then the shipped Y") and a marker a hook writes at runtime.
MAY_BE_ABSENT = (
    ".harness/teams/",              # project override of .agents/skills/harness/teams/*.yaml (DEC-113)
    ".harness/.pyyaml-bootstrap",   # written by harness_yaml.require_or_die
)

DEC_RE = re.compile(r"\bDEC-\d+\b")
INV_RE = re.compile(r"\bINV-\d+\b")
PATH_RE = re.compile(
    r"`((?:<HARNESS_[A-Z_]+>/|\.claude/|\.agents/|\.omp/|\.harness/|bin/|references/|templates/|docs/|tests/)[^`\s]+?)`"
)
SECTION_RE = re.compile(r"`?(harness-[a-z-]+)`? *§ *\"?([^`\"\n(]+?)\"?\s*[`.,;)]")
NAME_RE = re.compile(r"`(harness-[a-z-]+)`")
HEADING_RE = re.compile(r"^#+ (.+)$", re.M)


def _files(root: Path) -> list[Path]:
    skills = root / SKILLS_REL
    patterns = [
        str(skills / "*" / "SKILL.md"),
        str(skills / "*" / "references" / "*.md"),
        str(skills / "harness" / "templates" / "**" / "*.md"),
    ]
    return sorted(Path(p) for pat in patterns for p in glob.glob(pat, recursive=True) if os.path.isfile(p))


def _resolves(root: Path, citing: Path, ref: str) -> bool:
    ref = re.sub(r"^<HARNESS_[A-Z_]+>/", "", ref)
    if re.search(r"<[^>]+>|\*", ref) or ref.startswith(MAY_BE_ABSENT):
        return True
    ref = ref.split("#")[0].split(" §")[0].rstrip("/")
    if "." not in os.path.basename(ref):
        return True  # a directory or a bare name, not a file claim
    skill_dir = citing.parent.parent if citing.parent.name == "references" else citing.parent
    candidates = (root / ref, root / SKILLS_REL / ref, root / SKILLS_REL / "harness" / ref,
                  citing.parent / ref, skill_dir / ref)
    return any(c.exists() for c in candidates)


def scan(root: Path) -> list[str]:
    root = Path(root)
    files = _files(root)
    if not files:
        return []  # no skills tree here (a fixture, a product repo): nothing to resolve
    decisions = (root / DECISIONS_REL).read_text(encoding="utf-8")
    dec_ids = set(re.findall(r"^## (DEC-\d+)", decisions, re.M))
    inv_ids = set(INV_RE.findall((root / CHECK_STATE_REL).read_text(encoding="utf-8")))
    skill_names = {p.parent.name for p in (root / SKILLS_REL).glob("*/SKILL.md")}
    agent_names = {p.stem for p in (root / AGENTS_REL).glob("harness-*.md")}
    headings = {f: {h.strip() for h in HEADING_RE.findall(f.read_text(encoding="utf-8"))} for f in files}

    findings: list[str] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(root / SKILLS_REL).as_posix()

        def flag(what: str) -> None:
            findings.append(f"{rel}: {what}")

        for dec in sorted(set(DEC_RE.findall(text)) - dec_ids):
            flag(f"cites {dec}, which has no heading in DECISIONS.md")
        for inv in sorted(set(INV_RE.findall(text)) - inv_ids):
            flag(f"cites {inv}, which check-state.py does not implement")
        for ref in sorted(set(PATH_RE.findall(text))):
            if not _resolves(root, path, ref):
                flag(f"path does not exist: {ref}")
        for name, heading in sorted(set(SECTION_RE.findall(text))):
            if re.fullmatch(r"[\d\s–-]+", heading.strip()):
                continue  # a step range such as § 1–2, not a heading
            target = root / SKILLS_REL / name / "SKILL.md"
            if name in skill_names and not any(
                heading.strip().lower() in h.lower() for h in headings.get(target, set())
            ):
                flag(f"section not found: {name} § {heading.strip()}")
        for name in sorted(set(NAME_RE.findall(text))):
            if name not in skill_names and name not in agent_names:
                flag(f"names `{name}`, which is neither a skill nor an agent")
        if rel not in CLAUDE_SPELLING_EXEMPT and ".claude/skills/" in text:
            flag(f"spells the skills tree `.claude/skills/` ({text.count('.claude/skills/')}x); "
                 f"instructions use `.agents/skills/`")
    return findings


def main(argv: list[str]) -> int:
    root = Path(argv[0]) if argv else Path(__file__).resolve().parents[4]
    findings = scan(root)
    for line in findings:
        print(f"INV-45 {line}")
    if findings:
        print(f"check-skill-refs: {len(findings)} unresolved reference(s)", file=sys.stderr)
        return 1
    print(f"check-skill-refs: ok ({len(_files(root))} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
