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
the committed DESIGN.md and judges `runs/<run-id>/ui/results.json` (`harness-ui-results/1`)
against it: a results file never supplies its own list of checks. Any change under the
dashboard client package requires the package's whole table and every spec title present in
its e2e specs — no classification by route, so a shared component cannot slip past coverage.
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


# --- parsing -------------------------------------------------------------------------------

def _cells(line: str) -> list[str]:
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|") and not body.endswith("\\|"):
        body = body[:-1]
    return [c.replace("\\|", "|").strip().strip("`").strip() for c in re.split(r"(?<!\\)\|", body)]


def _table_after(lines: list[str], start: int, columns: tuple[str, ...], what: str) -> list[list[str]]:
    i = start
    while i < len(lines) and not lines[i].lstrip().startswith("|"):
        if lines[i].startswith("#"):
            raise ContractError(f"{what}: no table before the next heading")
        i += 1
    if i >= len(lines):
        raise ContractError(f"{what}: no table found")
    header = _cells(lines[i])
    if tuple(header) != columns:
        raise ContractError(f"{what}: columns are {header}; the contract requires {list(columns)}")
    rows = []
    for line in lines[i + 2:]:
        if not line.lstrip().startswith("|"):
            break
        cells = _cells(line)
        if len(cells) != len(columns):
            raise ContractError(f"{what}: row {cells[0] if cells else '?'!r} has {len(cells)} cells, not {len(columns)}")
        rows.append(cells)
    return rows


def _section(lines: list[str], heading: str) -> int | None:
    for i, line in enumerate(lines):
        if line.strip() == heading:
            return i
    return None


def _split_projects(raw: str, check_id: str) -> list[str]:
    projects = [p.strip() for p in raw.split(",") if p.strip()]
    if not projects:
        raise ContractError(f"{check_id}: no projects listed")
    for p in projects:
        if p not in PROJECTS:
            raise ContractError(f"{check_id}: unknown project {p!r}; known: {', '.join(PROJECTS)}")
    if len(set(projects)) != len(projects):
        raise ContractError(f"{check_id}: project listed twice")
    return projects


def load_manifest(design: pathlib.Path, require_predicates: bool = False,
                  require_inspection_evidence: bool = False, expect: list[str] | None = None) -> dict:
    """Parse DESIGN.md's Checks contract into the normalized manifest, or raise ContractError."""
    lines = pathlib.Path(design).read_text(encoding="utf-8").splitlines()
    start = _section(lines, "## Checks")
    if start is None:
        raise ContractError(f"{design}: no `## Checks` section")
    checks, ids, titles = [], set(), set()
    for cid, title, surface, method, raw_projects, predicate in _table_after(lines, start + 1, CHECK_COLUMNS, "Checks"):
        if not cid or not title or not surface:
            raise ContractError(f"Checks: row {cid or '?'!r} lacks an id, title or surface")
        if cid in ids:
            raise ContractError(f"Checks: duplicate check id {cid}")
        if title in titles:
            raise ContractError(f"Checks: duplicate spec title {title!r} ({cid})")
        if method not in METHODS:
            raise ContractError(f"{cid}: unknown method {method!r}; known: {', '.join(METHODS)}")
        projects = _split_projects(raw_projects, cid)
        if method == "automated-once" and len(projects) != 1:
            raise ContractError(f"{cid}: automated-once names exactly one project, got {projects}")
        if require_predicates and not predicate:
            raise ContractError(f"{cid}: no predicate or evidence description")
        ids.add(cid)
        titles.add(title)
        checks.append({"check_id": cid, "spec_title": title, "surface": surface, "method": method,
                       "projects": projects, "applicable_projects": list(projects), "predicate": predicate})
    if not checks:
        raise ContractError("Checks: the table has no rows")
    evidence = _inspection_evidence(lines, start, checks, require_inspection_evidence)
    if expect is not None:
        _match_expected(checks, expect)
    return {"schema": MANIFEST_SCHEMA, "design": str(design), "projects": list(PROJECTS), "checks": checks,
            "inspection_evidence": evidence, "listed_check_ids": [c["check_id"] for c in checks],
            "applicable": {p: [c["check_id"] for c in checks if p in c["applicable_projects"]] for p in PROJECTS}}


def _inspection_evidence(lines, start, checks, required) -> list[dict]:
    by_id = {c["check_id"]: c for c in checks}
    sub = None
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("## "):
            break
        if lines[i].strip() == "### Inspection evidence":
            sub = i
            break
    entries = []
    if sub is not None:
        for cid, label, route, state, setup, project, shot in _table_after(lines, sub + 1, EVIDENCE_COLUMNS, "Inspection evidence"):
            if cid not in by_id:
                raise ContractError(f"Inspection evidence: {cid} is not a listed check")
            if not by_id[cid]["method"].startswith("inspection"):
                raise ContractError(f"Inspection evidence: {cid} is not an inspection row")
            if project not in by_id[cid]["applicable_projects"]:
                raise ContractError(f"Inspection evidence: {cid} is not applicable at {project}")
            if not all((label, route, state, setup, project, shot)):
                raise ContractError(f"Inspection evidence: {cid}/{label or '?'} entry is incomplete")
            entries.append({"check_id": cid, "evidence_label": label, "route": route, "fixture_state": state,
                            "setup": setup, "project": project, "screenshot": shot})
    if required:
        for c in checks:
            if not c["method"].startswith("inspection"):
                continue
            for p in c["applicable_projects"]:
                if not any(e["check_id"] == c["check_id"] and e["project"] == p for e in entries):
                    raise ContractError(f"{c['check_id']}: no inspection evidence entry for {p}")
    return entries


def _match_expected(checks, expect):
    actual = {c["check_id"]: "|".join([c["check_id"], c["spec_title"], c["surface"], c["method"], ",".join(c["projects"])])
              for c in checks}
    expected = {}
    for raw in expect:
        parts = raw.split("|")
        if len(parts) != 5:
            raise ContractError(f"--expect {raw!r}: needs id|title|surface|method|projects")
        expected[parts[0]] = raw
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


def _is_webp(path: pathlib.Path) -> bool:
    try:
        head = path.read_bytes()[:12]
    except OSError:
        return False
    return len(head) == 12 and head[:4] == b"RIFF" and head[8:12] == b"WEBP"


def spec_titles(package: pathlib.Path) -> set[str]:
    titles = set()
    for spec in pathlib.Path(package).rglob(SPEC_GLOB):
        if "node_modules" in spec.parts:
            continue
        for m in _TITLE.finditer(spec.read_text(encoding="utf-8")):
            titles.add(next(g for g in m.groups() if g is not None))
    return titles


def gate(design, results, feature: str, run_id: str, served_bundle_commit: str, repo_root,
         changed: list[str], client_package) -> Verdict:
    """Judge one evidence bundle against the committed contract. FAIL carries every reason."""
    repo_root = pathlib.Path(repo_root).resolve()
    reasons: list[str] = []
    try:
        manifest = load_manifest(design)
    except ContractError as error:
        return Verdict("FAIL", [f"contract: {error}"])
    package = pathlib.Path(client_package)
    try:
        scripts = json.loads((package / "package.json").read_text(encoding="utf-8")).get("scripts", {})
    except (OSError, ValueError):
        scripts = {}
    if "test:ui" not in scripts:
        return Verdict("FAIL", [f"runner: {package / 'package.json'} declares no test:ui script"])
    results = pathlib.Path(results).resolve()
    try:
        doc = json.loads(results.read_text(encoding="utf-8"))
    except OSError:
        return Verdict("FAIL", [f"no results.json at {results}"])
    except ValueError as error:
        return Verdict("FAIL", [f"results.json is not JSON: {error}"])

    for key, want in (("schema", RESULTS_SCHEMA), ("feature", feature), ("run_id", run_id),
                      ("served_bundle_commit", served_bundle_commit)):
        if doc.get(key) != want:
            reasons.append(f"{key}: results carry {doc.get(key)!r}, gate requires {want!r}")
    if doc.get("listed_check_ids") != manifest["listed_check_ids"]:
        reasons.append(f"listed_check_ids differ from DESIGN.md: results {doc.get('listed_check_ids')}, contract {manifest['listed_check_ids']}")
    if doc.get("applicable_check_ids") != manifest["applicable"]:
        reasons.append("applicable_check_ids differ from the contract's applicability")
    if doc.get("missing_check_ids"):
        reasons.append(f"missing_check_ids is not empty: {doc['missing_check_ids']}")
    if sorted(doc.get("observed_check_ids") or []) != sorted(manifest["listed_check_ids"]):
        reasons.append("observed_check_ids do not account for every listed check")

    by_id = {c["check_id"]: c for c in manifest["checks"]}
    seen: dict[tuple[str, str], dict] = {}
    for record in doc.get("checks") or []:
        key = (record.get("check_id"), record.get("project"))
        if key in seen:
            reasons.append(f"duplicate record for {key[0]} at {key[1]}")
            continue
        seen[key] = record
        spec = by_id.get(key[0])
        if spec is None:
            reasons.append(f"{key[0]} is not a listed check")
            continue
        if key[1] not in spec["applicable_projects"]:
            reasons.append(f"{key[0]} is not applicable at {key[1]}")
            continue
        if record.get("spec_title") != spec["spec_title"]:
            reasons.append(f"{key[0]}: spec_title {record.get('spec_title')!r} != {spec['spec_title']!r}")
        for f in ("method", "surface"):
            if record.get(f) != spec[f]:
                reasons.append(f"{key[0]}: {f} {record.get(f)!r} != {spec[f]!r}")
        allowed = STATUS_BY_METHOD[spec["method"]]
        if record.get("status") not in allowed:
            reasons.append(f"{key[0]}@{key[1]}: status {record.get('status')!r} is not allowed for {spec['method']} (inspection rows only carry evidence)")
        elif record["status"] == "failed":
            reasons.append(f"{key[0]}@{key[1]} failed: {'; '.join(record.get('errors') or ['no error recorded'])}")
        reasons.extend(_screenshot_reasons(record, key, repo_root, results.parent))
    for spec in manifest["checks"]:
        for p in spec["applicable_projects"]:
            if (spec["check_id"], p) not in seen:
                reasons.append(f"no record for {spec['check_id']} at {p}")
    for entry in manifest["inspection_evidence"]:
        record = seen.get((entry["check_id"], entry["project"]))
        labels = {s.get("evidence_label") for s in (record or {}).get("screenshots") or []}
        if entry["evidence_label"] not in labels:
            reasons.append(f"{entry['check_id']}@{entry['project']}: no screenshot labelled {entry['evidence_label']!r}")

    summary = (doc.get("summary") or {}).get("status")
    failed = any(r.get("status") == "failed" for r in doc.get("checks") or [])
    if summary not in ("passed", "failed") or (summary == "passed" and failed) or (summary == "failed" and not failed and not reasons):
        reasons.append(f"summary.status {summary!r} disagrees with the records")

    if any(_under(repo_root / c, package) for c in changed):
        missing = [c["spec_title"] for c in manifest["checks"] if c["spec_title"] not in spec_titles(package)]
        for title in missing:
            reasons.append(f"client package changed and no spec carries the title {title!r}")
    return Verdict("FAIL" if reasons else "PASS", reasons)


def _under(path: pathlib.Path, base: pathlib.Path) -> bool:
    try:
        path.resolve().relative_to(pathlib.Path(base).resolve())
        return True
    except ValueError:
        return False


def _screenshot_reasons(record, key, repo_root, ui_dir) -> list[str]:
    shots = record.get("screenshots") or []
    if not shots:
        return [f"{key[0]}@{key[1]}: no screenshot evidence"]
    out = []
    for shot in shots:
        rel = shot.get("path") or ""
        path = repo_root / rel
        if not _under(path, ui_dir):
            out.append(f"{key[0]}@{key[1]}: screenshot {rel!r} is outside {ui_dir.relative_to(repo_root)}")
        elif not path.is_file() or path.stat().st_size == 0:
            out.append(f"{key[0]}@{key[1]}: screenshot {rel!r} is absent or empty")
        elif not _is_webp(path):
            out.append(f"{key[0]}@{key[1]}: screenshot {rel!r} is not WebP")
    return out


# --- cli -----------------------------------------------------------------------------------

def main(argv=None) -> int:
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
    args = parser.parse_args(argv)
    if args.cmd == "check":
        try:
            manifest = load_manifest(args.design, args.require_predicates, args.require_inspection_evidence, args.expect)
        except ContractError as error:
            print(f"REFUSED: {error}", file=sys.stderr)
            return 1
        json.dump(manifest, sys.stdout, indent=1)
        print()
        return 0
    verdict = gate(args.design, args.results, args.feature, args.run_id, args.served_bundle_commit,
                   args.repo_root, args.changed, args.client_package)
    print(f"UI GATE: {verdict.status}")
    for reason in verdict.reasons:
        print(f"  - {reason}")
    return 0 if verdict.status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
