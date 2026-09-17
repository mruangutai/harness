"""Live code-grade distribution KPI."""
import json
from pathlib import Path
import subprocess


_CODE_GRADE = Path(__file__).resolve().parents[1] / "code-grade.py"


def distribution(project_root: Path) -> dict:
    """Return the live grade distribution for the supplied project."""
    root = Path(project_root).resolve()
    paths = _tracked_files(root)
    payload = _grader_payload(root, paths)
    records = payload["records"]
    return {
        "graded_functions": len(records),
        "at_or_above_bar": payload["passing"],
        "at_or_above_bar_share": _share(payload["passing"], len(records)),
        "bins": _bins(records),
        "outliers": _outliers(records),
        "languages_covered": ["python"],
        "file_mix": _file_mix(paths, records, payload["ungraded"]),
        "sourcing_rule": "code-grade.py whole-repo mode supplies each record's bar.",
    }


def _tracked_files(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "git ls-files failed")
    return result.stdout.splitlines()


def _grader_payload(root: Path, paths: list[str]) -> dict:
    python_paths = [str(root / path) for path in paths if path.endswith(".py")]
    command = ["python3", str(_CODE_GRADE), "--json", *python_paths]
    if not python_paths:
        revision = _revision(root)
        command.extend(["--base", revision, "--head", revision])
    result = subprocess.run(
        command,
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError(result.stderr.strip() or "code-grade.py returned invalid JSON") from error


def _revision(root: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "git rev-parse HEAD failed")
    return result.stdout.strip()


def _bins(records: list[dict]) -> dict[int, int]:
    bins = {grade: 0 for grade in range(1, 6)}
    for record in records:
        bins[record["grade"]] += 1
    return bins


def _outliers(records: list[dict]) -> list[dict]:
    outliers = [
        {key: record[key] for key in ("qualname", "path", "line", "grade", "driver", "bar")}
        for record in records if record["grade"] <= 2
    ]
    return sorted(outliers, key=lambda record: (record["grade"], record["path"], record["line"]))


def _file_mix(paths: list[str], records: list[dict], ungraded: list[str]) -> dict:
    by_extension = {}
    for path in paths:
        extension = Path(path).suffix
        by_extension[extension] = by_extension.get(extension, 0) + 1
    tracked_files = len(paths)
    return {
        "tracked_files": tracked_files,
        "graded_files": len({record["path"] for record in records}),
        "ungraded_files": len(ungraded),
        "ungraded_share": _share(len(ungraded), tracked_files),
        "by_extension": by_extension,
    }


def _share(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0
