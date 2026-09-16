#!/usr/bin/env python3
"""Measure what every harness agent preloads, and note when it is over budget.

Each `.omp/agents/<agent>.md` declares `autoloadSkills:`; every entry resolves to
`.claude/skills/<skill>/SKILL.md` and its whole text is paid on every spawn of that
agent. This module counts that weight, per agent and for the UNIVERSAL set (the skills
every agent preloads), and compares both against `budgets.preload_warn_words` in
harness.json. The numerals live there and nowhere else (FEAT-60 SC-08).

Exceeding a budget is a NOTE, never a failure: weight is a cost, not a defect. What IS
a failure is an autoloadSkills entry that resolves to nothing — the agent would spawn
without a rule it was declared to carry — and a file under `references/` named as a
preload, which defeats the reason references exist (FEAT-60 SC-11, DEC-150).

Usage: check-skill-weight.py [ROOT] [--json]
"""

from __future__ import annotations

import artifact_accessors
import sys
from dataclasses import dataclass, field
from pathlib import Path


AGENTS_REL = Path(".omp") / "agents"
SKILLS_REL = Path(".claude") / "skills"
CONFIG_REL = ".harness/harness.json"   # config path, not a root probe (test-check-plan-routes case_20)
BUDGET_KEY = "preload_warn_words"
BUDGET_FIELDS = ("universal", "agent")


@dataclass
class Report:
    skills: dict[str, int]                       # skill name -> words
    agents: dict[str, list[str]]                 # agent -> autoloadSkills, in order
    universal: list[str]                         # skills every agent preloads
    budget: dict[str, int] | None                # {"universal": N, "agent": N} or None
    errors: list[str] = field(default_factory=list)

    def agent_words(self, agent: str) -> int:
        return sum(self.skills.get(s, 0) for s in self.agents[agent])

    @property
    def universal_words(self) -> int:
        return sum(self.skills[s] for s in self.universal)

    @property
    def total_words(self) -> int:
        return sum(self.agent_words(a) for a in self.agents)

    def notes(self) -> list[str]:
        """Over-budget findings, phrased for check-state's note channel."""
        if self.budget is None:
            return [f"preload weight is UNBUDGETED — budgets.{BUDGET_KEY} is absent or malformed "
                    f"in {CONFIG_REL}; {self.total_words} words preload across "
                    f"{len(self.agents)} agents and nothing is watching them"]
        out = []
        uni = self.universal_words
        if uni > self.budget["universal"]:
            out.append(f"universal preload is {uni} words (budget {self.budget['universal']}): "
                       + ", ".join(f"{s} {self.skills[s]}" for s in self.universal))
        for agent in sorted(self.agents, key=self.agent_words, reverse=True):
            words = self.agent_words(agent)
            if words > self.budget["agent"]:
                out.append(f"{agent} preloads {words} words (budget {self.budget['agent']}): "
                           + ", ".join(f"{s} {self.skills.get(s, 0)}" for s in self.agents[agent]))
        return out


def _frontmatter(path: Path) -> dict:
    metadata, _body = artifact_accessors.load_frontmatter(
        path.read_text(encoding="utf-8"), str(path))
    return metadata


def _budget(root: Path) -> dict[str, int] | None:
    path = root / CONFIG_REL
    if not path.is_file():
        return None
    raw = artifact_accessors.load_harness_json(path)
    block = (raw.get("budgets") or {}).get(BUDGET_KEY)
    if not isinstance(block, dict):
        return None
    out = {}
    for key in BUDGET_FIELDS:
        value = block.get(key)
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            return None
        out[key] = value
    return out


def scan(root: Path) -> Report:
    root = Path(root)
    try:
        budget = _budget(root)
    except artifact_accessors.ArtifactAccessError as error:
        budget = None
        budget_error = f"harness.json is unreadable ({error})"
    else:
        budget_error = None
    report = Report(skills={}, agents={}, universal=[], budget=budget)
    if budget_error:
        report.errors.append(budget_error)
    agents_dir = root / AGENTS_REL
    for agent_path in sorted(agents_dir.glob("*.md")):
        agent = agent_path.stem
        try:
            declared = _frontmatter(agent_path).get("autoloadSkills") or []
        except Exception as exc:
            report.errors.append(f"{agent}: unreadable frontmatter ({exc})")
            continue
        if not isinstance(declared, list) or not all(isinstance(s, str) for s in declared):
            report.errors.append(f"{agent}: autoloadSkills is not a list of names")
            continue
        report.agents[agent] = declared
        for skill in declared:
            if "/" in skill or "references" in Path(skill).parts:
                report.errors.append(f"{agent}: autoloadSkills names `{skill}` — only a skill "
                                     f"name resolves, and references/ is read at its seam, "
                                     f"never preloaded")
                continue
            if skill in report.skills:
                continue
            skill_md = root / SKILLS_REL / skill / "SKILL.md"
            if not skill_md.is_file():
                report.errors.append(f"{agent}: autoloadSkills names `{skill}` but "
                                     f"{SKILLS_REL / skill / 'SKILL.md'} does not exist")
                continue
            report.skills[skill] = len(skill_md.read_text(encoding="utf-8").split())
    if report.agents:
        common = set.intersection(*(set(s) for s in report.agents.values()))
        # Keep the first agent's declaration order so the note reads the same every run.
        first = next(iter(report.agents.values()))
        report.universal = [s for s in first if s in common and s in report.skills]
    return report


def main(argv: list[str]) -> int:
    as_json = "--json" in argv
    args = [a for a in argv if a != "--json"]
    root = Path(args[0]).resolve() if args else Path(__file__).resolve().parents[4]
    report = scan(root)
    if as_json:
        print(json.dumps({
            "skills": report.skills,
            "agents": {a: report.agent_words(a) for a in report.agents},
            "universal": report.universal,
            "universal_words": report.universal_words,
            "total_words": report.total_words,
            "budget": report.budget,
            "notes": report.notes(),
            "errors": report.errors,
        }, indent=2))
    else:
        for agent in sorted(report.agents, key=report.agent_words, reverse=True):
            print(f"{report.agent_words(agent):6}  {agent}")
        print(f"{report.universal_words:6}  universal: {', '.join(report.universal)}")
        print(f"{report.total_words:6}  total across {len(report.agents)} agents")
        for note in report.notes():
            print(f"  note       {note}")
        for err in report.errors:
            print(f"  VIOLATION  {err}")
    return 1 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
