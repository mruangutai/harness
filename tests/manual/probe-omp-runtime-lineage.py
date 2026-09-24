#!/usr/bin/env python3
"""Manual installation probe for Harness's pinned OMP runtime.

This is intentionally not a CI gate: it launches the installed ``omp`` binary and makes a live
model call. Run it after installing or changing the pinned downstream OMP build. It fails rather
than skips when OMP is absent, Main has no runtime identity, the probe extension is not inherited
by the child, or the child's Write/Edit/Bash callbacks lack exact parent lineage.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROBE = Path(__file__).with_suffix(".ts")
RESULTS: list[tuple[str, bool, object]] = []


def check(name: str, ok: bool, detail: object = "") -> None:
    RESULTS.append((name, bool(ok), detail))
    print(f"{'PASS' if ok else 'FAIL'} - {name}" + ("" if ok else f" ({detail!r})"))


def finish() -> int:
    failed = [name for name, ok, _detail in RESULTS if not ok]
    print(f"{'FAIL' if failed else 'PASS'} - {len(RESULTS) - len(failed)}/{len(RESULTS)} checks passed")
    return 1 if failed else 0


def observations(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def probe_command(omp: str, workdir: Path, markers: list[Path], out: Path) -> list[str]:
    tasks = []
    for index, marker in enumerate(markers, start=1):
        child_task = (
            f"Use the write tool to create {marker} with the exact text alpha. "
            "Use the edit tool to replace alpha with beta. "
            f"Then use the bash tool to run rm {marker}. "
            f"Finally reply with exactly LINEAGE_CHILD_{index}_PASS."
        )
        tasks.append(
            '{"agent":"task","name":"LineageProbeChild%d","task":%s}'
            % (index, json.dumps(child_task))
        )
    prompt = (
        "Use the task tool exactly once with one batch containing these two tasks: ["
        + ",".join(tasks)
        + "]. After both finish, reply with exactly LINEAGE_PARENT_PASS."
    )
    command = [
        omp,
        "-p",
        prompt,
        "-e",
        str(PROBE),
        "--no-extensions",
        "--no-skills",
        "--no-rules",
        "--auto-approve",
        "--session-dir",
        str(workdir / "sessions"),
        "--cwd",
        str(ROOT),
        "--max-time",
        "5m",
    ]
    model = os.environ.get("OMP_LINEAGE_PROBE_MODEL", "").strip()
    if model:
        command.extend(["--model", model])
    out.write_text("", encoding="utf-8")
    return command


def run_probe(
    omp: str, workdir: Path,
) -> tuple[subprocess.CompletedProcess[str] | None, Path, list[Path]]:
    out = workdir / "lineage.jsonl"
    markers = [workdir / "child-one.txt", workdir / "child-two.txt"]
    command = probe_command(omp, workdir, markers, out)
    env = {**os.environ, "OMP_LINEAGE_PROBE_OUT": str(out)}
    try:
        proc = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=360,
            env=env,
            cwd=ROOT,
        )
    except subprocess.TimeoutExpired as exc:
        check("case2: omp completed the live lineage scenario", False, f"timeout after {exc.timeout}s")
        return None, out, markers
    return proc, out, markers


def verify_parent(rows: list[dict[str, object]]) -> None:
    parent_tasks = [row for row in rows if row.get("tool") == "task"]
    carries_main = any(
        row.get("agentId") == "Main" and not row.get("parentAgentId")
        for row in parent_tasks
    )
    check("case3: Main task callback carries the authenticated Main identity",
          carries_main, parent_tasks)


def verify_children(rows: list[dict[str, object]], markers: list[Path]) -> None:
    child_rows = [row for row in rows if row.get("parentAgentId") == "Main"]
    child_ids = {str(row.get("agentId") or "") for row in child_rows} - {""}
    tools_by_child = {
        child_id: {
            str(row.get("tool") or "").lower()
            for row in child_rows if row.get("agentId") == child_id
        }
        for child_id in child_ids
    }
    check("case4: two distinct child identities are bound to Main",
          len(child_ids) == 2, {"child_ids": sorted(child_ids), "rows": child_rows})
    check("case5: each inherited extension observes child Write, Edit, and Bash callbacks",
          all({"write", "edit", "bash"}.issubset(tools) for tools in tools_by_child.values())
          and len(tools_by_child) == 2,
          {child: sorted(tools) for child, tools in tools_by_child.items()})
    check("case6: both children removed their marker through Bash",
          all(not marker.exists() for marker in markers),
          [str(marker) for marker in markers if marker.exists()])


def verify_probe(
    proc: subprocess.CompletedProcess[str], out: Path, markers: list[Path],
) -> None:
    rows = observations(out)
    diagnostic = {
        "returncode": proc.returncode,
        "stdout": proc.stdout[-800:],
        "stderr": proc.stderr[-800:],
        "observations": rows,
    }
    check("case2: omp completed the live lineage scenario",
          proc.returncode == 0 and "LINEAGE_PARENT_PASS" in proc.stdout, diagnostic)
    verify_parent(rows)
    verify_children(rows, markers)


def main() -> int:
    omp = shutil.which("omp")
    check("case1: the omp binary is on PATH", omp is not None, omp)
    check("case1: the committed lineage probe extension exists", PROBE.is_file(), str(PROBE))
    if not omp or not PROBE.is_file():
        return finish()

    with tempfile.TemporaryDirectory(prefix="harness-omp-lineage-") as workdir_text:
        proc, out, markers = run_probe(omp, Path(workdir_text))
        if proc is not None:
            verify_probe(proc, out, markers)
    return finish()


if __name__ == "__main__":
    sys.exit(main())
