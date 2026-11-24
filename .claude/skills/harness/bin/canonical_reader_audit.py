"""canonical_reader_audit.py — the canonical-reader classification audit.

Moved verbatim from check-plan-routes.py by FEAT-2489. `check-plan-routes.py
--canonical-reader-audit` is the gate that runs it. This module is a gate-imported
library under DEC-174's library clause and never imports that entry. It also holds
LEGAL_MAIN_SESSION_TOKEN, which the entry's route check imports back.
"""
import ast
import glob
import json
import os
import artifact_accessors
import feature_corpus

LEGAL_MAIN_SESSION_TOKEN = "main-session-direct"


READER_CALL_CATEGORIES = {
    "json.load": "json_file",
    "json.loads": "json_string",
    "yaml.load": "pyyaml",
    "yaml.safe_load": "pyyaml",
    "harness_yaml.load_file": "harness_yaml_file",
    "harness_yaml.load_str": "harness_yaml_string",
    "harness_yaml.load_plan": "load_plan",
    "factory_config.load_fleet": "load_fleet",
    "harness_yaml.manifest_domains": "manifest_domains",
    "feature_json_write.load_feature_json": "load_feature_json",
}
CANONICAL_ACCESSOR_NAMES = {
    "load_feature_json", "load_harness_json", "load_plan", "load_fleet",
    "manifest_domains", "load_frontmatter", "load_omp_config",
    "read_hook_payload", "parse_gh_json", "load_json_mapping",
}
# load_json_mapping is the strict JSON-mapping read for NON-config JSON (FEAT-2297). harness.json
# is configuration: its canonical remedy is the validating load_harness_json, so a canonical row
# reading it through load_json_mapping is a finding; only a ruled exemption may read it raw.
CONFIG_ARTIFACT = "harness.json"
GENERIC_JSON_REMEDY = "artifact_accessors.load_json_mapping"
LEGAL_READER_EXEMPTIONS = {
    "harness_yaml_primitive",
    "in_memory_validation",
    "canonical_writer_transform",
    "module_internal_format",
    "test_or_migration_corpus",
    "sole_state_yaml_reader",
}
READER_CLASSIFICATION_SCHEMA = "canonical-reader-classification/1"
READER_CLASSIFICATION_REL = os.path.join(
    "tests", "integration", "canonical-reader-classification.json")
READER_CATEGORY_REMEDIES = {
    "json_file": "artifact_accessors.load_harness_json",
    "json_string": "artifact_accessors.parse_gh_json",
    "pyyaml": "artifact_accessors.load_frontmatter",
    "harness_yaml_file": "artifact_accessors.load_plan",
    "harness_yaml_string": "artifact_accessors.load_frontmatter",
    "load_plan": "artifact_accessors.load_plan",
    "load_fleet": "artifact_accessors.load_fleet",
    "manifest_domains": "artifact_accessors.manifest_domains",
    "load_feature_json": "artifact_accessors.load_feature_json",
}
T07_TERMINAL_REMEDIES = {
    ".claude/skills/harness/bin/bash-write-guard.py::<module>::manifest_domains#1":
        "artifact_accessors.manifest_domains",
    ".claude/skills/harness/bin/check-domain.py::<module>::manifest_domains#1":
        "artifact_accessors.manifest_domains",
    ".claude/skills/harness/bin/check-domain.py::domain_check::manifest_domains#1":
        "artifact_accessors.manifest_domains",
    ".claude/skills/harness/bin/check-plan-routes.py::process_plan_yaml::load_plan#1":
        "artifact_accessors.load_plan",
    ".claude/skills/harness/bin/canonical_reader_audit.py::_task_files::load_plan#1":
        "artifact_accessors.load_plan",
    ".claude/skills/harness/bin/check-state.py::<module>::load_plan#1":
        "artifact_accessors.load_plan",
    ".claude/skills/harness/bin/factory_config.py::load_fleet::harness_yaml_file#1":
        "artifact_accessors.load_fleet",
    ".claude/skills/harness/bin/feature_json_write.py::load_feature_json::json_string#1":
        "artifact_accessors.load_feature_json",
    ".claude/skills/harness/bin/harness_yaml.py::load_plan::harness_yaml_file#1":
        "artifact_accessors.load_plan",
    ".claude/skills/harness/bin/harness_yaml.py::manifest_domains::harness_yaml_file#1":
        "artifact_accessors.manifest_domains",
}
T07_RELOCATED_IMPLEMENTATIONS = {
    ".claude/skills/harness/bin/factory_config.py::load_fleet::harness_yaml_file#1":
        (".claude/skills/harness/bin/artifact_accessors.py", "load_fleet", "harness_yaml_file", "harness_yaml.load_file"),
    ".claude/skills/harness/bin/feature_json_write.py::load_feature_json::json_string#1":
        (".claude/skills/harness/bin/artifact_accessors.py", "strict_json_loads", "json_string", "json.loads"),
    ".claude/skills/harness/bin/harness_yaml.py::load_plan::harness_yaml_file#1":
        (".claude/skills/harness/bin/artifact_accessors.py", "load_plan", "harness_yaml_file", "harness_yaml.load_file"),
    ".claude/skills/harness/bin/harness_yaml.py::manifest_domains::harness_yaml_file#1":
        (".claude/skills/harness/bin/artifact_accessors.py", "manifest_domains", "harness_yaml_file", "harness_yaml.load_file"),
    ".claude/skills/harness/bin/check-domain.py::domain_check::manifest_domains#1":
        (".claude/skills/harness/bin/check-domain.py", "_manifest_domains_or_exit", "manifest_domains", "artifact_accessors.manifest_domains"),
    ".claude/skills/harness/bin/check-plan-routes.py::process_plan_yaml::load_plan#1":
        (".claude/skills/harness/bin/check-plan-routes.py", "_load_plan_once", "load_plan", "artifact_accessors.load_plan"),
    ".claude/skills/harness/bin/check-state.py::<module>::load_plan#1":
        (".claude/skills/harness/bin/check_state/ctx.py", "Ctx._load_plan_docs", "load_plan", "artifact_accessors.load_plan"),
}


def _qualified_name(node, aliases):
    if isinstance(node, ast.Name):
        return aliases.get(node.id, node.id)
    if isinstance(node, ast.Attribute):
        parent = _qualified_name(node.value, aliases)
        if parent:
            return f"{parent}.{node.attr}"
    return None


class _ReaderAliasCollector(ast.NodeVisitor):
    def __init__(self):
        self.aliases = {}

    def visit_Import(self, node):
        for item in node.names:
            self.aliases[item.asname or item.name.split(".")[0]] = item.name

    def visit_ImportFrom(self, node):
        if not node.module:
            return
        for item in node.names:
            if item.name == "*":
                continue
            self.aliases[item.asname or item.name] = f"{node.module}.{item.name}"

    def visit_Assign(self, node):
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            resolved = _qualified_name(node.value, self.aliases)
            if resolved:
                self.aliases[node.targets[0].id] = resolved
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        if isinstance(node.target, ast.Name) and node.value is not None:
            resolved = _qualified_name(node.value, self.aliases)
            if resolved:
                self.aliases[node.target.id] = resolved
        self.generic_visit(node)


def _normalized_reader_name(qualified, file):
    if (
            file.endswith("/harness_yaml.py")
            and qualified in {"load_file", "load_str"}):
        return f"harness_yaml.{qualified}"
    return qualified


def _reader_category(qualified, file):
    qualified = _normalized_reader_name(qualified, file)
    category = READER_CALL_CATEGORIES.get(qualified)
    if category:
        return category
    if not qualified:
        return None
    name = qualified.rsplit(".", 1)[-1]
    if (
            qualified.startswith("artifact_accessors.")
            and name in CANONICAL_ACCESSOR_NAMES):
        return name
    return qualified if qualified in CANONICAL_ACCESSOR_NAMES else None


class _ReaderCallCollector(ast.NodeVisitor):
    def __init__(self, aliases, file):
        self.aliases = aliases
        self.file = file
        self.symbols = []
        self.calls = []

    def _visit_symbol(self, node):
        self.symbols.append(node.name)
        self.generic_visit(node)
        self.symbols.pop()

    visit_ClassDef = _visit_symbol
    visit_FunctionDef = _visit_symbol
    visit_AsyncFunctionDef = _visit_symbol

    def visit_Call(self, node):
        qualified = _qualified_name(node.func, self.aliases)
        category = _reader_category(qualified, self.file)
        if category:
            self.calls.append({
                "file": self.file,
                "symbol": ".".join(self.symbols) or "<module>",
                "callee": qualified,
                "category": category,
                "line": node.lineno,
                "column": node.col_offset,
            })
        self.generic_visit(node)


def reader_candidates_from_source(source, file):
    tree = ast.parse(source, filename=file)
    aliases = _ReaderAliasCollector()
    aliases.visit(tree)
    collector = _ReaderCallCollector(aliases.aliases, file)
    collector.visit(tree)
    ordinals = {}
    for call in sorted(collector.calls, key=lambda item: (item["line"], item["column"])):
        key = (call["symbol"], call["category"])
        ordinals[key] = ordinals.get(key, 0) + 1
        call["id"] = (
            f"{file}::{call['symbol']}::{call['category']}#{ordinals[key]}")
    return collector.calls


def _reader_source_paths(root):
    bin_root = os.path.join(root, ".claude", "skills", "harness", "bin")
    prefix = os.path.join(".claude", "skills", "harness", "bin")
    paths = []
    for current, dirs, files in os.walk(bin_root):
        dirs[:] = sorted(name for name in dirs if name != "__pycache__")
        for name in sorted(files):
            if name.endswith(".py"):
                absolute = os.path.join(current, name)
                relative = os.path.relpath(absolute, bin_root)
                paths.append((absolute, os.path.join(prefix, relative)))
    return paths


def _scan_reader_tree(root):
    candidates, scanned, findings = [], [], []
    for absolute, relative in _reader_source_paths(root):
        scanned.append(relative)
        try:
            with open(absolute, encoding="utf-8") as source:
                candidates.extend(reader_candidates_from_source(source.read(), relative))
        except (OSError, UnicodeDecodeError, SyntaxError) as error:
            findings.append(
                f"{relative}::<module> source_parse remedy=repair source: {error}. "
                "PLAN AMENDMENT REQUIRED")
    return candidates, scanned, findings


def _row_lookup(rows):
    lookup, findings = {}, []
    for row in rows:
        row_id = row.get("id") if isinstance(row, dict) else None
        if not row_id:
            findings.append("classification row has no id. PLAN AMENDMENT REQUIRED")
        elif row_id in lookup:
            findings.append(
                f"duplicate classification row {row_id}. PLAN AMENDMENT REQUIRED")
        else:
            lookup[row_id] = row
    return lookup, findings




def _exemption_finding(row):
    exemption = row.get("exemption")
    if exemption not in LEGAL_READER_EXEMPTIONS:
        return (
            f"{row.get('file')}::{row.get('symbol')} {row.get('category')} "
            f"remedy={row.get('remedy', 'unknown')}: illegal exemption "
            f"{exemption!r}. PLAN AMENDMENT REQUIRED")
    if not str(row.get("reason", "")).strip():
        return (
            f"{row.get('file')}::{row.get('symbol')} {row.get('category')} "
            "remedy=none: exemption requires a reason. PLAN AMENDMENT REQUIRED")
    return None


def _row_label(row):
    return (f"{row.get('file')}::{row.get('symbol')} {row.get('category')} "
            f"remedy={row.get('remedy')}")


def _ownership_finding(row, task_files):
    # Ownership is checked only for a row that names the plan owning its migration. The
    # inventory names no plan of its own: a row's bare `task` is provenance, so the audit never
    # depends on a feature directory that may since have been deleted (FEAT-71).
    plan, task = row.get("plan"), row.get("task")
    if not isinstance(plan, str) or not task or task == "none":
        return None
    if row.get("file") in task_files.get(plan, {}).get(task, ()):
        return None
    return f"{_row_label(row)}: {task} task files omit this source. PLAN AMENDMENT REQUIRED"


def _route_finding(row, task_files):
    category = row.get("dec174_category")
    if category != "none" and row.get("execution_route") != LEGAL_MAIN_SESSION_TOKEN:
        return (
            f"{_row_label(row)}: DEC-174 category {category!r} requires "
            "main-session-direct. PLAN AMENDMENT REQUIRED")
    return _ownership_finding(row, task_files)


def _classification_shape_findings(document, scanned_files):
    findings = []
    if document.get("schema") != READER_CLASSIFICATION_SCHEMA:
        findings.append(
            f"classification schema must be {READER_CLASSIFICATION_SCHEMA}. "
            "PLAN AMENDMENT REQUIRED")
    if document.get("scanned_files") != scanned_files:
        findings.append(
            "scanned-file manifest differs from the live Python tree. "
            "PLAN AMENDMENT REQUIRED")
    rows = document.get("rows")
    if not isinstance(rows, list):
        findings.append(
            "classification rows must be a list. PLAN AMENDMENT REQUIRED")
        return findings, None
    return findings, rows




def _state_reader_findings(rows):
    state_readers = [
        row for row in rows
        if isinstance(row, dict)
        and row.get("artifact") == "state.yaml"
        and row.get("exemption") == "sole_state_yaml_reader"
    ]
    if len(state_readers) <= 1:
        return []
    return [
        "second state.yaml reader found; add a canonical accessor. "
        "PLAN AMENDMENT REQUIRED"
    ]


def reader_classification_findings(candidates, scanned_files, document, task_files):
    findings, rows = _classification_shape_findings(document, scanned_files)
    if rows is None:
        return findings
    _lookup, duplicate_findings = _row_lookup(rows)
    findings.extend(duplicate_findings)
    live = {candidate["id"]: candidate for candidate in candidates}
    findings.extend(_unaccounted_candidate_findings(candidates, rows))
    findings.extend(_classified_rows_findings(rows, task_files, live, candidates))
    findings.extend(_state_reader_findings(rows))
    return findings


def _classification_document(path):
    try:
        with open(path, encoding="utf-8") as source:
            document = json.load(source)
    except (OSError, UnicodeDecodeError, ValueError) as error:
        return None, [f"{path}: classification cannot be read: {error}"]
    if not isinstance(document, dict):
        return None, [f"{path}: classification must be a JSON object"]
    return document, []


def _expanded_task_paths(root, path):
    if not glob.has_magic(path):
        return [path]
    return [
        os.path.relpath(match, root)
        for match in sorted(glob.glob(os.path.join(root, path)))
    ]


def _task_files(root, plan_relative):
    # A classification row names the plan of the feature that owns a migration — usually another
    # feature, which a sparse worktree reads at the owner root (FEAT-1559).
    plan = artifact_accessors.load_plan(feature_corpus.corpus_path(root, plan_relative))
    task_files = {}
    for task in plan["tasks"]:
        paths = []
        for entry in task.get("files", []):
            path = str(entry.get("path") if isinstance(entry, dict) else entry).split("#", 1)[0]
            paths.extend(_expanded_task_paths(root, path))
        task_files[str(task["id"])] = paths
    return task_files


_CLASSIFICATION_REMEDY_OVERRIDES = {
    # Signed T-02/T-03 amendments made the concrete public accessors explicit after T-01
    # captured broader route labels. These overrides remain part of the permanent audit.
    ".claude/skills/harness/bin/factory_config.py::product_config::json_string#1":
        "artifact_accessors.load_harness_json",
}


def _row_remedy(row):
    return _CLASSIFICATION_REMEDY_OVERRIDES.get(
        row.get("id"), row.get("remedy"))


def _candidate_matches_canonical_row(candidate, row, remedy):
    return (
        candidate.get("file") == row.get("file")
        and candidate.get("symbol") == row.get("symbol")
        and candidate.get("callee") == remedy
    )


def _candidate_matches_relocated(candidate, relocated):
    file, symbol, category, callee = relocated
    return (
        candidate.get("file") == file
        and candidate.get("symbol") == symbol
        and candidate.get("category") == category
        and candidate.get("callee") == callee
    )


def _row_is_canonical(row, candidates):
    relocated = T07_RELOCATED_IMPLEMENTATIONS.get(row.get("id"))
    if relocated is not None:
        return any(
            _candidate_matches_relocated(candidate, relocated)
            for candidate in candidates
        )
    remedy = _row_remedy(row)
    return any(
        _candidate_matches_canonical_row(candidate, row, remedy)
        for candidate in candidates
    )


def _migration_row_state(row, live, candidates):
    if _row_is_canonical(row, candidates):
        return "canonical"
    if row.get("id") in live:
        return "raw"
    return "missing"



def _candidate_matches_remedy(candidate, row):
    return (
        candidate.get("file") == row.get("file")
        and candidate.get("symbol") == row.get("symbol")
        and candidate.get("callee") == _row_remedy(row)
    )


def _candidate_matches_relocated_row(candidate, row):
    relocated = T07_RELOCATED_IMPLEMENTATIONS.get(row.get("id"))
    return (
        relocated is not None
        and _candidate_matches_relocated(candidate, relocated)
    )


def _candidate_is_accounted(candidate, rows):
    identities = {row.get("id") for row in rows if isinstance(row, dict)}
    return (
        candidate.get("id") in identities
        or any(
            _candidate_matches_remedy(candidate, row)
            or _candidate_matches_relocated_row(candidate, row)
            for row in rows if isinstance(row, dict)
        )
    )


def _scanned_manifest_findings(scanned, document):
    expected = set(document.get("scanned_files", []))
    if set(scanned) == expected:
        return []
    return [
        "scanned-file manifest differs from the live Python tree. "
        "PLAN AMENDMENT REQUIRED"
    ]


def _unaccounted_candidate_findings(candidates, rows):
    return [
        f"{candidate['file']}::{candidate['symbol']} "
        f"{candidate['category']} "
        f"remedy={READER_CATEGORY_REMEDIES.get(candidate['category'], 'artifact_accessors')}: "
        "live AST row absent from migration inventory. PLAN AMENDMENT REQUIRED"
        for candidate in candidates
        if not _candidate_is_accounted(candidate, rows)
    ]


def _migration_row_findings(row, live, candidates):
    if _migration_row_state(row, live, candidates) != "missing":
        return []
    return [
        f"{row.get('file')}::{row.get('symbol')} "
        f"{row.get('category')} remedy={_row_remedy(row)}: "
        "artifact row absent from AST and its canonical remedy does not exist. "
        "PLAN AMENDMENT REQUIRED"
    ]


def _unmigrated_row_findings(row, live, candidates):
    same_site = [
        candidate for candidate in candidates
        if candidate.get("file") == row.get("file")
        and candidate.get("symbol") == row.get("symbol")
        and candidate.get("category") == row.get("category")
    ]
    if row.get("id") in live or len(same_site) == 1:
        return []
    return [
        f"{row.get('file')}::{row.get('symbol')} "
        f"{row.get('category')}: artifact row absent from AST. "
        "PLAN AMENDMENT REQUIRED"
    ]


def _exempt_row_findings(row, live, candidates):
    findings = _unmigrated_row_findings(row, live, candidates)
    exemption = _exemption_finding(row)
    if exemption:
        findings.append(exemption)
    return findings


def _canonical_row_findings(row, live, candidates):
    state = _migration_row_state(row, live, candidates)
    if state != "canonical":
        return [
            f"{row.get('id')}: observed state={state}; expected disposition=canonical "
            f"remedy={_row_remedy(row)}. PLAN AMENDMENT REQUIRED"
        ]
    if row.get("artifact") == CONFIG_ARTIFACT and _row_remedy(row) == GENERIC_JSON_REMEDY:
        return [
            f"{row.get('id')}: harness.json read through {GENERIC_JSON_REMEDY}; configuration "
            f"reads use {READER_CATEGORY_REMEDIES['json_file']}. PLAN AMENDMENT REQUIRED"
        ]
    return _migration_row_findings(row, live, candidates)


def _classified_disposition_findings(row, live, candidates):
    disposition = row.get("disposition")
    if disposition == "exempt":
        return _exempt_row_findings(row, live, candidates)
    if disposition == "canonical":
        return _canonical_row_findings(row, live, candidates)
    if disposition == "migrate":
        return _migration_row_findings(row, live, candidates)
    return [
        f"{row.get('file')}::{row.get('symbol')} {row.get('category')} "
        f"remedy={row.get('remedy', 'unknown')}: illegal disposition "
        f"{disposition!r}. PLAN AMENDMENT REQUIRED"
    ]


def _classified_row_finding(row, task_files, live, candidates):
    if not isinstance(row, dict):
        return []
    route = _route_finding(row, task_files)
    route_findings = [route] if route else []
    return route_findings + _classified_disposition_findings(
        row, live, candidates)


def _t07_terminal_observation(row_id, rows, live, candidates):
    matches = [
        row for row in rows
        if isinstance(row, dict) and row.get("id") == row_id
    ]
    if not matches:
        return "missing", None
    if len(matches) != 1:
        return f"duplicate({len(matches)})", matches[0]
    row = matches[0]
    return _migration_row_state(row, live, candidates), row


def _t07_terminal_message(row_id, state, row, expected_remedy):
    observed_task = row.get("task") if row else "<missing>"
    observed_disposition = row.get("disposition") if row else "<missing>"
    observed_remedy = row.get("remedy") if row else "<missing>"
    return (
        f"{row_id}: observed state={state} task={observed_task} "
        f"disposition={observed_disposition} remedy={observed_remedy}; "
        f"expected task=T-07 disposition=canonical remedy={expected_remedy}. "
        "PLAN AMENDMENT REQUIRED"
    )


def _t07_row_matches_contract(state, row, expected_remedy):
    return (
        state == "canonical"
        and row is not None
        and row.get("task") == "T-07"
        and row.get("disposition") == "canonical"
        and row.get("remedy") == expected_remedy
    )


def _t07_expected_finding(row_id, expected_remedy, rows, live, candidates):
    state, row = _t07_terminal_observation(
        row_id, rows, live, candidates)
    if _t07_row_matches_contract(state, row, expected_remedy):
        return None
    return _t07_terminal_message(row_id, state, row, expected_remedy)


def _t07_extra_findings(rows, live, candidates):
    findings = []
    for row in rows:
        if not isinstance(row, dict) or row.get("task") != "T-07":
            continue
        if row.get("id") in T07_TERMINAL_REMEDIES:
            continue
        state = _migration_row_state(row, live, candidates)
        findings.append(_t07_terminal_message(
            row.get("id", "<missing id>"), state, row,
            "<no additional T-07 row>"))
    return findings


def _t07_terminal_findings(rows, candidates):
    live = {candidate["id"]: candidate for candidate in candidates}
    expected = [
        _t07_expected_finding(
            row_id, expected_remedy, rows, live, candidates)
        for row_id, expected_remedy in T07_TERMINAL_REMEDIES.items()
    ]
    return (
        [finding for finding in expected if finding]
        + _t07_extra_findings(rows, live, candidates)
    )


def _selected_migration_rows(rows, task_id):
    return [
        row for row in rows
        if isinstance(row, dict) and row.get("task") == task_id
        and "plan" not in row
        and row.get("disposition") in {"migrate", "canonical"}
    ]


def _task_migration_findings(rows, task_id, live, candidates):
    selected = _selected_migration_rows(rows, task_id)
    if not selected:
        return [f"{task_id}: classification has no assigned rows"]
    states = {
        _migration_row_state(row, live, candidates) for row in selected
    }
    if (
        states == {"canonical"}
        and all(row.get("disposition") == "canonical" for row in selected)
    ):
        return []
    return [
        f"{task_id}: migration unit is not terminally canonical "
        f"({', '.join(sorted(states))}). PLAN AMENDMENT REQUIRED"
    ]


def _classified_rows_findings(rows, task_files, live, candidates):
    findings = []
    for row in rows:
        findings.extend(
            _classified_row_finding(row, task_files, live, candidates))
    return findings


def _classification_structure(root, document, scanned, rows):
    task_files, task_findings = _classification_task_files(root, document)
    _lookup, duplicate_findings = _row_lookup(rows)
    findings = (
        _scanned_manifest_findings(scanned, document)
        + task_findings
        + duplicate_findings
    )
    return task_files, findings


def _valid_classification_findings(
        root, document, candidates, scanned, rows, task_id):
    task_files, findings = _classification_structure(
        root, document, scanned, rows)
    live = {candidate["id"]: candidate for candidate in candidates}
    findings.extend(_unaccounted_candidate_findings(candidates, rows))
    findings.extend(_classified_rows_findings(rows, task_files, live, candidates))
    if task_id == "T-07":
        historical_rows = [row for row in rows
                           if isinstance(row, dict) and "plan" not in row]
        findings.extend(_t07_terminal_findings(historical_rows, candidates))
    else:
        findings.extend(
            _task_migration_findings(rows, task_id, live, candidates))
    return findings


def classification_task_findings(root, classification_path, task_id):
    """Validate one signed migration unit without mistaking expected cutovers for drift. A unit
    is the inventory's own task label: rows naming another feature's plan are not in it."""
    candidates, scanned, scan_findings = _scan_reader_tree(root)
    document, document_findings = _classification_document(classification_path)
    findings = scan_findings + document_findings
    if document is None:
        return findings
    rows = document.get("rows")
    if not isinstance(rows, list):
        return findings + ["classification rows must be a list"]
    return findings + _valid_classification_findings(
        root, document, candidates, scanned, rows, task_id)


def _audit_result(scanned, candidates, findings, violations):
    exit_code = 2 if findings else (1 if violations else 0)
    return {
        "exit_code": exit_code,
        "unresolved": len(violations),
        "scanned_files": scanned,
        "candidates": candidates,
        "classification_findings": findings,
        "violations": violations,
    }


def _named_plans(document):
    """Distinct `plan` values the classification rows name, in first-seen order."""
    plans = []
    for row in document.get("rows", []):
        if isinstance(row, dict) and "plan" in row and row["plan"] not in plans:
            plans.append(row["plan"])
    return plans


def _ownership_task_files(root, plan):
    if not isinstance(plan, str) or not plan:
        raise ValueError("ownership plan must be a nonempty path")
    return _task_files(root, plan)


def _classification_task_files(root, document):
    """`(task_files, findings)` for the plans classification rows name — `{plan: {task: files}}`.
    Only a row whose migration a feature owns names one; there is no document-level default."""
    import harness_yaml
    task_files, findings = {}, []
    for plan in _named_plans(document):
        try:
            task_files[plan] = _ownership_task_files(root, plan)
        except (harness_yaml.YamlParseError, OSError, ValueError, KeyError, TypeError,
                feature_corpus.CorpusError) as error:
            findings.append(f"{plan}: plan cannot be read: {error}")
    return task_files, findings


def _migration_violations(rows):
    return [
        f"{row['file']}::{row['symbol']} {row['category']} "
        f"artifact={row['artifact']} remedy={row['remedy']} task={row['task']} "
        f"route={row['execution_route']}"
        for row in rows
        if isinstance(row, dict) and row.get("disposition") == "migrate"
    ]


def audit_canonical_readers(root, classification_path=None):
    classification_path = classification_path or os.path.join(
        root, READER_CLASSIFICATION_REL)
    candidates, scanned, scan_findings = _scan_reader_tree(root)
    document, document_findings = _classification_document(classification_path)
    if document is None:
        return _audit_result(
            scanned, candidates, scan_findings + document_findings, [])
    task_files, task_findings = _classification_task_files(root, document)
    findings = scan_findings + document_findings + task_findings
    findings.extend(
        reader_classification_findings(candidates, scanned, document, task_files))
    return _audit_result(
        scanned, candidates, findings,
        _migration_violations(document.get("rows", [])))


def _run_canonical_reader_audit(root):
    result = audit_canonical_readers(root)
    for finding in result["classification_findings"]:
        print(f"CLASSIFICATION {finding}")
    for violation in result["violations"]:
        print(f"VIOLATION {violation}")
    # COUPLED: the `Canonical-reader audit` step in .github/workflows/tests.yml parses this
    # summary line for its scanned-file count. Change both together.
    print(
        f"{result['unresolved']} unresolved reader site(s) across "
        f"{len(result['scanned_files'])} Python file(s)")
    return result["exit_code"]
