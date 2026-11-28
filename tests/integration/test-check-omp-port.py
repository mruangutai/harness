#!/usr/bin/env python3
"""Behavior tests for check-omp-port.py."""

from __future__ import annotations

from integration_support import ROOT, BIN

import contextlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import artifact_accessors
from check_support import Checks

CHECK = BIN / "check-omp-port.py"


def run(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(CHECK), str(root)], text=True, capture_output=True)


@contextlib.contextmanager
def fixture():
    """Yield a temporary copy of the trees check-omp-port.py reads; removed on exit."""
    # `.claude/worktrees/` holds every live feature checkout — ~1 GB here, growing with
    # concurrent feature work — and check-omp-port.py never reads it: its only traversal is
    # `agent_dir.glob("harness-*.md")`. Copying it made this file 239s of the integration
    # suite's 240s wall clock (issue #1525).
    skip_worktrees = shutil.ignore_patterns("worktrees")
    with tempfile.TemporaryDirectory() as td:
        dst = Path(td)
        for rel in (".omp", ".agents", ".claude"):
            shutil.copytree(ROOT / rel, dst / rel, symlinks=True, ignore=skip_worktrees)
        shutil.copy2(ROOT / "AGENTS.md", dst / "AGENTS.md")
        yield dst


# FEAT-2397 (SC-06): native `task.perCallModel` is the sole per-call model authority, Main
# included, so the repo's config pins it explicitly to the STRING off; a project setting can
# narrow an operator's choice but never widen it. Read through the strict OMP config reader
# check-omp-port.py uses, never a second parser or a text match.
PER_CALL_MODEL_PIN = '  perCallModel: "off"\n'
PER_CALL_MODEL_MUTATIONS = (
    ("absent", ""),
    ("on", '  perCallModel: "on"\n'),
    ("eval", "  perCallModel: eval\n"),
)


def _per_call_model_off(config: Path) -> bool:
    task = artifact_accessors.load_omp_config(config).get("task") or {}
    return task.get("perCallModel") == "off"


def case_per_call_model_pinned_off():
    results = [("live .omp/config.yml pins task.perCallModel to the string off",
                _per_call_model_off(ROOT / ".omp" / "config.yml"), "")]
    # load_omp_config needs only a .yml path, not a tree around it.
    text = (ROOT / ".omp" / "config.yml").read_text()
    with tempfile.TemporaryDirectory() as td:
        for label, replacement in PER_CALL_MODEL_MUTATIONS:
            config = Path(td) / f"{label}.yml"
            config.write_text(text.replace(PER_CALL_MODEL_PIN, replacement))
            results.append((f"a task.perCallModel {label} pin fails the off assertion",
                            PER_CALL_MODEL_PIN in text and not _per_call_model_off(config), ""))
    return results


def _append_async_block(root: Path) -> None:
    config = root / ".omp" / "config.yml"
    config.write_text(config.read_text(encoding="utf-8") + "\nasync:\n  enabled: true\n",
                      encoding="utf-8")


def _duplicate_agent_name(root: Path) -> None:
    agent = root / ".omp" / "agents" / "harness-backend-dev.md"
    agent.write_text(agent.read_text(encoding="utf-8").replace(
        "name: harness-backend-dev", "name: harness-backend-dev\nname: harness-backend-dev", 1),
        encoding="utf-8")


def _duplicate_provider(root: Path) -> None:
    provider = root / ".omp" / "providers" / "openai.yml"
    text = provider.read_text(encoding="utf-8")
    provider.write_text(text + "\n" + text, encoding="utf-8")


def case_live_tree_passes():
    """The strict reader refuses a duplicate key in config, agent frontmatter and provider YAML,
    each on a fresh fixture; a refusal that does not happen aborts the file."""
    clean = run(ROOT)
    for mutate in (_append_async_block, _duplicate_agent_name, _duplicate_provider):
        with fixture() as root:
            mutate(root)
            duplicate = run(root)
        assert duplicate.returncode == 1 and "duplicate key" in duplicate.stderr, duplicate.stderr
    return [("live provider-neutral tree passes", clean.returncode == 0, clean.stderr)]


def case_missing_agents_md_fails():
    with fixture() as root:
        (root / "AGENTS.md").unlink()
        result = run(root)
        return [
            ("missing AGENTS.md fails", result.returncode == 1, ""),
            ("missing guidance is named", "AGENTS.md" in result.stderr, ""),
        ]


def case_concrete_model_in_canonical_fails():
    with fixture() as root:
        agent = root / ".omp" / "agents" / "harness-backend-dev.md"
        agent.write_text(agent.read_text().replace("model: '@standard'", "model: anthropic/claude-sonnet-5"))
        result = run(root)
        return [
            ("concrete model in canonical agent fails", result.returncode == 1, ""),
            ("provider coupling is named", "provider-neutral model alias" in result.stderr, ""),
        ]


def case_thinking_level_disagrees_with_alias_fails():
    """DEC-233: the alias↔thinking-level pairing was enforced only by the deleted
    sync-agent-adapters.py. A `@review` role at `medium` must be refused here, naming both."""
    with fixture() as root:
        agent = root / ".omp" / "agents" / "harness-code-reviewer.md"
        agent.write_text(agent.read_text().replace("thinking-level: high", "thinking-level: medium"))
        result = run(root)
        return [
            ("thinking-level disagreeing with alias fails", result.returncode == 1, result.stderr),
            ("both values are named", "@review" in result.stderr and "medium" in result.stderr, result.stderr),
        ]


def case_missing_async_enablement_fails():
    with fixture() as root:
        config = root / ".omp" / "config.yml"
        config.write_text(config.read_text().replace("async:\n  enabled: true\n", ""))
        result = run(root)
        return [
            ("missing explicit async enablement fails", result.returncode == 1, ""),
            ("async liveness contract is named", "async.enabled" in result.stderr, ""),
        ]


def case_task_wall_clock_limit_fails():
    with fixture() as root:
        config = root / ".omp" / "config.yml"
        config.write_text(config.read_text().replace("maxRuntimeMs: 0", "maxRuntimeMs: 60000"))
        result = run(root)
        return [
            ("task wall clock limit fails", result.returncode == 1, ""),
            ("wall-clock contract is named", "task.maxRuntimeMs" in result.stderr, ""),
        ]


def case_task_structured_off():
    """BUG-2565: each harness agent's frontmatter carries `structured: true` and its digest
    schema, so global `task.structured` stays at OMP's default (off) and the task tool exposes
    no schema parameter. Absent or boolean false passes; true and every truthy look-alike fail."""
    variants = (
        ("absent", None, True),
        ("boolean false", "false", True),
        ("boolean true", "true", False),
        ("string 'true'", '"true"', False),
        ("integer 1", "1", False),
    )
    rows = []
    for label, value, accepted in variants:
        with fixture() as root:
            config = root / ".omp" / "config.yml"
            lines = [line for line in config.read_text().splitlines(keepends=True)
                     if not line.lstrip().startswith("structured:")]
            text = "".join(lines)
            if value is not None:
                text = text.replace("  maxRuntimeMs: 0\n", f"  maxRuntimeMs: 0\n  structured: {value}\n")
            config.write_text(text)
            result = run(root)
            if accepted:
                rows.append((f"task.structured {label} passes", result.returncode == 0, result.stderr))
            else:
                rows.append((f"task.structured {label} fails",
                             result.returncode == 1 and "task.structured" in result.stderr,
                             result.stderr))
    return rows


def _replace_under_output(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    start = text.index("\noutput:")
    at = text.index(old, start)
    path.write_text(text[:at] + new + text[at + len(old):], encoding="utf-8")


def _schema_gains_field(root: Path) -> None:
    schema = root / ".claude/skills/harness/schemas/digest/harness-qa.json"
    data = artifact_accessors.load_json_mapping(schema)
    data["properties"]["DIGEST"]["properties"]["probe_field"] = {"type": "string"}
    schema.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def case_agent_output_drift():
    """BUG-2565: an agent's generated `output:` must stay equal to the projection of its persona
    schema, with `structured: true` beside it. Equality is typed, so 0 never stands in for false
    (in Python `{"a": False} == {"a": 0}` is True, the blind spot the last fixture guards)."""
    fixtures = (
        ("schema changed without regenerating", _schema_gains_field, ".omp/agents/harness-qa.md"),
        ("output hand-edited to additionalProperties true",
         lambda root: _replace_under_output(root / ".omp/agents/harness-pm.md",
                                            "additionalProperties: false", "additionalProperties: true"),
         ".omp/agents/harness-pm.md"),
        ("structured: true removed",
         lambda root: (root / ".omp/agents/harness-ui-reviewer.md").write_text(
             (root / ".omp/agents/harness-ui-reviewer.md").read_text(encoding="utf-8")
             .replace("structured: true\n", "", 1), encoding="utf-8"),
         ".omp/agents/harness-ui-reviewer.md"),
        ("output additionalProperties 0 instead of false",
         lambda root: _replace_under_output(root / ".omp/agents/harness-pm.md",
                                            "additionalProperties: false", "additionalProperties: 0"),
         ".omp/agents/harness-pm.md"),
    )
    rows = []
    for label, mutate, named in fixtures:
        with fixture() as root:
            mutate(root)
            result = run(root)
            rows.append((f"agent output drift: {label} fails naming {named}",
                         result.returncode == 1 and named in result.stderr, result.stderr))
    return rows


def case_tools_mapping_fails():
    """#2698 review: a `tools` mapping is read by OMP as an empty allowlist (a log warning, no
    error), and the suites read it as its keys, so this gate is the only one that refuses it."""
    with fixture() as root:
        agent = root / ".omp" / "agents" / "harness-eng-lead.md"
        text = agent.read_text(encoding="utf-8")
        match = re.search(r"(?m)^tools:\n((?:- .*\n)+)", text)
        mapping = "".join(f"  {line[2:].strip()}: true\n" for line in match.group(1).splitlines(keepends=True))
        agent.write_text(text.replace(match.group(0), "tools:\n" + mapping, 1), encoding="utf-8")
        result = run(root)
        return [
            ("a tools mapping is planted", match is not None and "read: true" in agent.read_text(), ""),
            ("a tools mapping instead of a list fails", result.returncode == 1, result.stderr),
            ("the tools shape is named", "harness-eng-lead.md tools must be a list" in result.stderr,
             result.stderr),
        ]


def case_nonblocking_nested_agent_fails():
    with fixture() as root:
        agent = root / ".omp" / "agents" / "harness-backend-dev.md"
        agent.write_text(agent.read_text().replace("blocking: true\n", ""))
        result = run(root)
        return [
            ("nonblocking nested Harness agent fails", result.returncode == 1, ""),
            ("nested supervision contract is named", "blocking: true" in result.stderr, ""),
        ]

def case_no_agent_files_fails():
    """#2696: the roster check moved to the suites that load every agent, so an empty
    .omp/agents must still fail here rather than pass every per-agent check vacuously."""
    with fixture() as root:
        for agent in (root / ".omp" / "agents").glob("harness-*.md"):
            agent.unlink()
        result = run(root)
        return [
            ("no harness agent files fails", result.returncode == 1, result.stderr),
            ("the empty agent directory is named", "no harness-*.md agent files" in result.stderr,
             result.stderr),
        ]


def case_missing_command_door_fails():
    with fixture() as root:
        (root / ".omp" / "commands" / "harness-ship.md").unlink()
        result = run(root)
        return [
            ("missing command door fails", result.returncode == 1, ""),
            ("missing door is named", "harness-ship.md" in result.stderr, ""),
        ]


def case_absent_canonical_command_root_fails():
    with fixture() as root:
        shutil.rmtree(root / ".omp" / "commands")
        result = run(root)
        missing_doors = sum(
            1 for door in ("harness", "harness-plan", "harness-ship", "harness-grilling")
            if f".omp/commands/{door}.md is missing" in result.stderr
        )
        return [
            ("absent canonical command root fails", result.returncode == 1, ""),
            ("absent canonical root names all four doors", missing_doors == 4, result.stderr),
        ]


def case_feat64_unrelated_defect_escapes():
    """FEAT-64 (SC-03): with artifact_accessors.load_omp_config replaced by a function that raises
    RuntimeError('unrelated defect'), the defect ESCAPES the tool (non-zero, traceback) instead of
    entering its quiet/best-effort path. The patch raises before any tree content is read."""
    with tempfile.TemporaryDirectory() as td:
        shim = Path(td) / "feat64-shim.py"
        shim.write_text("import sys, runpy\n"
                        f"sys.path.insert(0, {str(BIN)!r})\n"
                        "import artifact_accessors as m\n"
                        "def boom(*a, **k): raise RuntimeError('unrelated defect')\n"
                        "m.load_omp_config = boom\n"
                        f"runpy.run_path({str(CHECK)!r}, run_name='__main__')\n")
        r = subprocess.run([sys.executable, str(shim), str(ROOT)], capture_output=True, text=True)
    return [("FEAT-64: an unrelated RuntimeError in the config reader escapes check-omp-port "
             "(traceback, not 'cannot read')",
             r.returncode != 0 and "RuntimeError" in r.stderr and "cannot read .omp/config.yml" not in r.stderr,
             f"rc={r.returncode} stderr={r.stderr[-200:]!r}")]


CASES = (
    case_feat64_unrelated_defect_escapes,
    case_per_call_model_pinned_off,
    case_live_tree_passes,
    case_missing_agents_md_fails,
    case_concrete_model_in_canonical_fails,
    case_thinking_level_disagrees_with_alias_fails,
    case_missing_async_enablement_fails,
    case_task_wall_clock_limit_fails,
    case_task_structured_off,
    case_agent_output_drift,
    case_tools_mapping_fails,
    case_nonblocking_nested_agent_fails,
    case_no_agent_files_fails,
    case_missing_command_door_fails,
    case_absent_canonical_command_root_fails,
)


def main() -> int:
    C = Checks()
    for case in CASES:
        for label, ok, detail in case():
            C.check(label, ok, detail)
    return C.report()


if __name__ == "__main__":
    sys.exit(main())
