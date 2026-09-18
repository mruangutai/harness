#!/usr/bin/env python3
"""The UI evidence contract: one parser for a DESIGN.md `## Checks` table, one gate for the
Playwright evidence bundle that discharges it (FEAT-1821 T-01; SC-05, SC-06, SC-10, SC-11).

The table, under a `## Checks` heading, has exactly these columns:

    | Check ID | Spec title | Surface | Method | Projects | Predicate or evidence |

`Method` is one of `automated-each-project`, `automated-once`, `inspection-each-project` or
`pixel-baseline` (the explicit opt-in). `Projects` is a comma list drawn from `desktop-1440`,
`desktop-1920`; an `automated-once` row names exactly one. `Spec title` is byte-matched against
the Playwright test title, so a failure is human-locatable by name.

Inspection rows carry their evidence manifest in a `### Inspection evidence` table:

    | Check ID | Evidence label | Route | Fixture state | Setup | Project | Screenshot |

`check` emits the normalized manifest (`harness-ui-manifest/1`) that the Playwright runner and
the QA gate both consume — neither parses Markdown again. `gate` recomputes that manifest from
the committed DESIGN.md — predicates and inspection evidence REQUIRED — and judges
`runs/<run-id>/ui/results.json` (`harness-ui-results/1`) against it: a results file never
supplies its own list of checks. Any change under the dashboard client package requires the
package's whole table and every spec title present in its e2e specs — no classification by
route, so a shared component cannot slip past coverage.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from dataclasses import dataclass, field

MANIFEST_SCHEMA = "harness-ui-manifest/1"
RESULTS_SCHEMA = "harness-ui-results/1"
PROJECTS = ("desktop-1440", "desktop-1920")
METHODS = ("automated-each-project", "automated-once", "inspection-each-project", "pixel-baseline")
CHECK_COLUMNS = ("Check ID", "Spec title", "Surface", "Method", "Projects", "Predicate or evidence")
EVIDENCE_COLUMNS = ("Check ID", "Evidence label", "Route", "Fixture state", "Setup", "Project", "Screenshot")
STATUS_BY_METHOD = {"automated-each-project": {"passed", "failed"}, "automated-once": {"passed", "failed"},
                    "pixel-baseline": {"passed", "failed"}, "inspection-each-project": {"evidence"}}
SPEC_GLOB = "*.e2e.spec.ts"
_TITLE = re.compile(r"""\btest(?:\.\w+)?\(\s*(?:'((?:[^'\\]|\\.)*)'|"((?:[^"\\]|\\.)*)"|`((?:[^`\\]|\\.)*)`)""")


class ContractError(ValueError):
    """The Checks table or its evidence manifest violates the contract."""


# --- markdown tables -----------------------------------------------------------------------

def _cells(line: str) -> list[str]:
    body = line.strip().removeprefix("|")
    if body.endswith("|") and not body.endswith("\\|"):
        body = body[:-1]
    return [c.replace("\\|", "|").strip().strip("`").strip() for c in re.split(r"(?<!\\)\|", body)]


def _find_table_start(lines: list[str], start: int, what: str) -> int:
    for i in range(start, len(lines)):
        if lines[i].lstrip().startswith("|"):
            return i
        if lines[i].startswith("#"):
            break
    raise ContractError(f"{what}: no table before the next heading")


def _table_after(lines: list[str], start: int, columns: tuple[str, ...], what: str) -> list[list[str]]:
    head = _find_table_start(lines, start, what)
    header = _cells(lines[head])
    if tuple(header) != columns:
        raise ContractError(f"{what}: columns are {header}; the contract requires {list(columns)}")
    rows = []
    for line in lines[head + 2:]:
        if not line.lstrip().startswith("|"):
            break
        rows.append(_row(_cells(line), columns, what))
    return rows


def _row(cells: list[str], columns: tuple[str, ...], what: str) -> list[str]:
    if len(cells) != len(columns):
        raise ContractError(f"{what}: row {cells[0] if cells else '?'!r} has {len(cells)} cells, not {len(columns)}")
    return cells


def _section(lines: list[str], heading: str, start: int = 0, stop_at_h2: bool = False) -> int | None:
    for i in range(start, len(lines)):
        if lines[i].strip() == heading:
            return i
        if stop_at_h2 and lines[i].startswith("## "):
            return None
    return None


# --- checks table --------------------------------------------------------------------------

def _split_projects(raw: str, check_id: str) -> list[str]:
    projects = [p.strip() for p in raw.split(",") if p.strip()]
    if not projects:
        raise ContractError(f"{check_id}: no projects listed")
    unknown = [p for p in projects if p not in PROJECTS]
    if unknown:
        raise ContractError(f"{check_id}: unknown project {unknown[0]!r}; known: {', '.join(PROJECTS)}")
    if len(set(projects)) != len(projects):
        raise ContractError(f"{check_id}: project listed twice")
    return projects


def _row_projects(cid: str, method: str, raw_projects: str) -> list[str]:
    projects = _split_projects(raw_projects, cid)
    if method == "automated-once" and len(projects) != 1:
        raise ContractError(f"{cid}: automated-once names exactly one project, got {projects}")
    return projects


def _check_from_row(cells: list[str], require_predicates: bool) -> dict:
    cid, title, surface, method, raw_projects, predicate = cells
    if not cid or not title or not surface:
        raise ContractError(f"Checks: row {cid or '?'!r} lacks an id, title or surface")
    if method not in METHODS:
        raise ContractError(f"{cid}: unknown method {method!r}; known: {', '.join(METHODS)}")
    if require_predicates and not predicate:
        raise ContractError(f"{cid}: no predicate or evidence description")
    projects = _row_projects(cid, method, raw_projects)
    return {"check_id": cid, "spec_title": title, "surface": surface, "method": method,
            "projects": projects, "applicable_projects": list(projects), "predicate": predicate}


def _refuse_duplicates(checks: list[dict]) -> None:
    ids, titles = set(), set()
    for c in checks:
        if c["check_id"] in ids:
            raise ContractError(f"Checks: duplicate check id {c['check_id']}")
        if c["spec_title"] in titles:
            raise ContractError(f"Checks: duplicate spec title {c['spec_title']!r} ({c['check_id']})")
        ids.add(c["check_id"])
        titles.add(c["spec_title"])


def load_manifest(design: pathlib.Path, require_predicates: bool = False,
                  require_inspection_evidence: bool = False, expect: list[str] | None = None) -> dict:
    """Parse DESIGN.md's Checks contract into the normalized manifest, or raise ContractError."""
    lines = pathlib.Path(design).read_text(encoding="utf-8").splitlines()
    start = _section(lines, "## Checks")
    if start is None:
        raise ContractError(f"{design}: no `## Checks` section")
    checks = [_check_from_row(row, require_predicates)
              for row in _table_after(lines, start + 1, CHECK_COLUMNS, "Checks")]
    if not checks:
        raise ContractError("Checks: the table has no rows")
    _refuse_duplicates(checks)
    evidence = _inspection_evidence(lines, start, checks)
    if require_inspection_evidence:
        _require_evidence_per_project(checks, evidence)
    if expect is not None:
        _match_expected(checks, expect)
    return _manifest(design, checks, evidence)


def _manifest(design, checks: list[dict], evidence: list[dict]) -> dict:
    return {"schema": MANIFEST_SCHEMA, "design": str(design), "projects": list(PROJECTS), "checks": checks,
            "inspection_evidence": evidence, "listed_check_ids": [c["check_id"] for c in checks],
            "applicable": {p: [c["check_id"] for c in checks if p in c["applicable_projects"]] for p in PROJECTS}}


# --- inspection evidence -------------------------------------------------------------------

def _evidence_entry(cells: list[str], by_id: dict[str, dict]) -> dict:
    cid, label, route, state, setup, project, shot = cells
    spec = by_id.get(cid)
    if spec is None:
        raise ContractError(f"Inspection evidence: {cid} is not a listed check")
    if not spec["method"].startswith("inspection"):
        raise ContractError(f"Inspection evidence: {cid} is not an inspection row")
    if project not in spec["applicable_projects"]:
        raise ContractError(f"Inspection evidence: {cid} is not applicable at {project}")
    if not all((label, route, state, setup, shot)):
        raise ContractError(f"Inspection evidence: {cid}/{label or '?'} entry is incomplete")
    return {"check_id": cid, "evidence_label": label, "route": route, "fixture_state": state,
            "setup": setup, "project": project, "screenshot": shot}


def _inspection_evidence(lines: list[str], start: int, checks: list[dict]) -> list[dict]:
    sub = _section(lines, "### Inspection evidence", start + 1, stop_at_h2=True)
    if sub is None:
        return []
    by_id = {c["check_id"]: c for c in checks}
    return [_evidence_entry(row, by_id)
            for row in _table_after(lines, sub + 1, EVIDENCE_COLUMNS, "Inspection evidence")]


def _require_evidence_per_project(checks: list[dict], entries: list[dict]) -> None:
    covered = {(e["check_id"], e["project"]) for e in entries}
    for c in checks:
        if not c["method"].startswith("inspection"):
            continue
        for p in c["applicable_projects"]:
            if (c["check_id"], p) not in covered:
                raise ContractError(f"{c['check_id']}: no inspection evidence entry for {p}")


def _match_expected(checks: list[dict], expect: list[str]) -> None:
    actual = {c["check_id"]: "|".join([c["check_id"], c["spec_title"], c["surface"], c["method"], ",".join(c["projects"])])
              for c in checks}
    expected = {}
    for raw in expect:
        if raw.count("|") != 4:
            raise ContractError(f"--expect {raw!r}: needs id|title|surface|method|projects")
        expected[raw.split("|", 1)[0]] = raw
    for cid, raw in expected.items():
        if actual.get(cid) != raw:
            raise ContractError(f"expected row {raw!r} but the table has {actual.get(cid)!r}")
    extra = sorted(set(actual) - set(expected))
    if extra:
        raise ContractError(f"rows not expected by the plan: {', '.join(extra)}")


# --- gate ----------------------------------------------------------------------------------

@dataclass
class Verdict:
    status: str
    reasons: list[str] = field(default_factory=list)


@dataclass
class _Bundle:
    """One results.json being judged, with the paths the screenshot rules need."""
    doc: dict
    repo_root: pathlib.Path
    ui_dir: pathlib.Path


def _is_webp(path: pathlib.Path) -> bool:
    try:
        head = path.read_bytes()[:12]
    except OSError:
        return False
    return len(head) == 12 and head[:4] == b"RIFF" and head[8:12] == b"WEBP"


def _under(path: pathlib.Path, base: pathlib.Path) -> bool:
    try:
        path.resolve().relative_to(pathlib.Path(base).resolve())
        return True
    except ValueError:
        return False


def spec_titles(package: pathlib.Path) -> set[str]:
    titles = set()
    for spec in pathlib.Path(package).rglob(SPEC_GLOB):
        if "node_modules" in spec.parts:
            continue
        for m in _TITLE.finditer(spec.read_text(encoding="utf-8")):
            titles.add(next(g for g in m.groups() if g is not None))
    return titles


def _runner_declared(package: pathlib.Path) -> bool:
    try:
        scripts = json.loads((package / "package.json").read_text(encoding="utf-8")).get("scripts", {})
    except (OSError, ValueError):
        return False
    return "test:ui" in scripts


def _load_results(results: pathlib.Path) -> tuple[dict | None, str | None]:
    try:
        return json.loads(results.read_text(encoding="utf-8")), None
    except OSError:
        return None, f"no results.json at {results}"
    except ValueError as error:
        return None, f"results.json is not JSON: {error}"


def _identity_reasons(doc: dict, feature: str, run_id: str, commit: str) -> list[str]:
    wanted = (("schema", RESULTS_SCHEMA), ("feature", feature), ("run_id", run_id), ("served_bundle_commit", commit))
    return [f"{key}: results carry {doc.get(key)!r}, gate requires {want!r}"
            for key, want in wanted if doc.get(key) != want]


def _accounting_reasons(doc: dict, manifest: dict) -> list[str]:
    out = []
    if doc.get("listed_check_ids") != manifest["listed_check_ids"]:
        out.append(f"listed_check_ids differ from DESIGN.md: results {doc.get('listed_check_ids')}, contract {manifest['listed_check_ids']}")
    if doc.get("applicable_check_ids") != manifest["applicable"]:
        out.append("applicable_check_ids differ from the contract's applicability")
    if doc.get("missing_check_ids"):
        out.append(f"missing_check_ids is not empty: {doc['missing_check_ids']}")
    if sorted(doc.get("observed_check_ids") or []) != sorted(manifest["listed_check_ids"]):
        out.append("observed_check_ids do not account for every listed check")
    return out


def _record_reasons(record: dict, spec: dict, key: tuple[str, str]) -> list[str]:
    """Judge one (check, project) record against its Checks row."""
    out = []
    if record.get("spec_title") != spec["spec_title"]:
        out.append(f"{key[0]}: spec_title {record.get('spec_title')!r} != {spec['spec_title']!r}")
    out += [f"{key[0]}: {f} {record.get(f)!r} != {spec[f]!r}" for f in ("method", "surface") if record.get(f) != spec[f]]
    status_reason = _status_reason(record, spec["method"], key)
    return out + ([status_reason] if status_reason else [])


def _status_reason(record: dict, method: str, key: tuple[str, str]) -> str | None:
    status, errors = record.get("status"), record.get("errors") or []
    if status not in STATUS_BY_METHOD[method]:
        return f"{key[0]}@{key[1]}: status {status!r} is not allowed for {method} (inspection rows only carry evidence)"
    if status == "failed":
        return f"{key[0]}@{key[1]} failed: {'; '.join(errors or ['no error recorded'])}"
    if status == "evidence" and errors:
        return f"{key[0]}@{key[1]}: inspection setup failed, so its screenshots are not evidence: {'; '.join(errors)}"
    return None


def _screenshot_reason(shot: dict, key: tuple[str, str], bundle: _Bundle) -> str | None:
    rel = shot.get("path") or ""
    path = bundle.repo_root / rel
    if not _under(path, bundle.ui_dir):
        return f"{key[0]}@{key[1]}: screenshot {rel!r} is outside {bundle.ui_dir.relative_to(bundle.repo_root)}"
    if not path.is_file() or path.stat().st_size == 0:
        return f"{key[0]}@{key[1]}: screenshot {rel!r} is absent or empty"
    if not _is_webp(path):
        return f"{key[0]}@{key[1]}: screenshot {rel!r} is not WebP"
    return None


def _screenshot_reasons(record: dict, key: tuple[str, str], bundle: _Bundle) -> list[str]:
    shots = record.get("screenshots") or []
    if not shots:
        return [f"{key[0]}@{key[1]}: no screenshot evidence"]
    reasons = (_screenshot_reason(shot, key, bundle) for shot in shots)
    return [r for r in reasons if r]


def _records_reasons(bundle: _Bundle, manifest: dict) -> tuple[list[str], dict[tuple[str, str], dict]]:
    by_id = {c["check_id"]: c for c in manifest["checks"]}
    seen: dict[tuple[str, str], dict] = {}
    out: list[str] = []
    for record in bundle.doc.get("checks") or []:
        key = (record.get("check_id"), record.get("project"))
        spec = by_id.get(key[0])
        if key in seen:
            out.append(f"duplicate record for {key[0]} at {key[1]}")
        elif spec is None:
            out.append(f"{key[0]} is not a listed check")
        elif key[1] not in spec["applicable_projects"]:
            out.append(f"{key[0]} is not applicable at {key[1]}")
        else:
            seen[key] = record
            out += _record_reasons(record, spec, key) + _screenshot_reasons(record, key, bundle)
    return out, seen


def _coverage_reasons(manifest: dict, seen: dict[tuple[str, str], dict]) -> list[str]:
    missing = [f"no record for {spec['check_id']} at {p}"
               for spec in manifest["checks"] for p in spec["applicable_projects"] if (spec["check_id"], p) not in seen]
    return missing + [r for entry in manifest["inspection_evidence"] if (r := _label_reason(entry, seen))]


def _label_reason(entry: dict, seen: dict[tuple[str, str], dict]) -> str | None:
    record = seen.get((entry["check_id"], entry["project"])) or {}
    labels = {s.get("evidence_label") for s in record.get("screenshots") or []}
    if entry["evidence_label"] in labels:
        return None
    return f"{entry['check_id']}@{entry['project']}: no screenshot labelled {entry['evidence_label']!r}"


def _summary_reasons(doc: dict, reasons_so_far: list[str]) -> list[str]:
    summary = (doc.get("summary") or {}).get("status")
    failed = any(r.get("status") == "failed" for r in doc.get("checks") or [])
    consistent = summary in ("passed", "failed") and (summary == "failed") == (failed or bool(reasons_so_far))
    return [] if consistent else [f"summary.status {summary!r} disagrees with the records"]


def _client_change_reasons(manifest: dict, repo_root: pathlib.Path, changed: list[str], package: pathlib.Path) -> list[str]:
    if not any(_under(repo_root / c, package) for c in changed):
        return []
    present = spec_titles(package)
    return [f"client package changed and no spec carries the title {c['spec_title']!r}"
            for c in manifest["checks"] if c["spec_title"] not in present]


def gate(design, results, feature: str, run_id: str, served_bundle_commit: str, repo_root,
         changed: list[str], client_package) -> Verdict:
    """Judge one evidence bundle against the committed contract. FAIL carries every reason."""
    repo_root = pathlib.Path(repo_root).resolve()
    package = pathlib.Path(client_package)
    results = pathlib.Path(results).resolve()
    manifest, bundle, blocker = _preflight(design, package, results, repo_root)
    if blocker:
        return Verdict("FAIL", [blocker])
    reasons = _identity_reasons(bundle.doc, feature, run_id, served_bundle_commit) + _accounting_reasons(bundle.doc, manifest)
    record_reasons, seen = _records_reasons(bundle, manifest)
    reasons += record_reasons + _coverage_reasons(manifest, seen)
    reasons += _summary_reasons(bundle.doc, reasons)
    reasons += _client_change_reasons(manifest, repo_root, changed, package)
    return Verdict("FAIL" if reasons else "PASS", reasons)


def _preflight(design, package: pathlib.Path, results: pathlib.Path, repo_root: pathlib.Path):
    """Contract, runner and results must all load before any record is judged; the first
    blocker is the whole verdict because nothing downstream is meaningful without it."""
    try:
        manifest = load_manifest(design, require_predicates=True, require_inspection_evidence=True)
    except ContractError as error:
        return None, None, f"contract: {error}"
    if not _runner_declared(package):
        return None, None, f"runner: {package / 'package.json'} declares no test:ui script"
    doc, load_error = _load_results(results)
    if doc is None:
        return None, None, load_error
    return manifest, _Bundle(doc, repo_root, results.parent), None


# --- cli -----------------------------------------------------------------------------------

def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="parse a DESIGN.md Checks table; print the normalized manifest")
    c.add_argument("--design", required=True, type=pathlib.Path)
    c.add_argument("--require-predicates", action="store_true")
    c.add_argument("--require-inspection-evidence", action="store_true")
    c.add_argument("--expect", action="append", help="id|title|surface|method|projects, one per row the plan pins")
    g = sub.add_parser("gate", help="judge runs/<id>/ui/results.json against the committed contract")
    g.add_argument("--design", required=True, type=pathlib.Path)
    g.add_argument("--results", required=True, type=pathlib.Path)
    g.add_argument("--feature", required=True)
    g.add_argument("--run-id", required=True)
    g.add_argument("--served-bundle-commit", required=True, help="the pinned review_sha")
    g.add_argument("--repo-root", default=".", type=pathlib.Path)
    g.add_argument("--client-package", required=True, type=pathlib.Path)
    g.add_argument("--changed", action="append", default=[], help="a changed path (repeat); from git diff --name-only")
    return parser


def _run_check(args) -> int:
    try:
        manifest = load_manifest(args.design, args.require_predicates, args.require_inspection_evidence, args.expect)
    except ContractError as error:
        print(f"REFUSED: {error}", file=sys.stderr)
        return 1
    json.dump(manifest, sys.stdout, indent=1)
    print()
    return 0


def _run_gate(args) -> int:
    verdict = gate(args.design, args.results, args.feature, args.run_id, args.served_bundle_commit,
                   args.repo_root, args.changed, args.client_package)
    print(f"UI GATE: {verdict.status}")
    for reason in verdict.reasons:
        print(f"  - {reason}")
    return 0 if verdict.status == "PASS" else 1


def main(argv=None) -> int:
    args = _parser().parse_args(argv)
    return _run_check(args) if args.cmd == "check" else _run_gate(args)


if __name__ == "__main__":
    sys.exit(main())
