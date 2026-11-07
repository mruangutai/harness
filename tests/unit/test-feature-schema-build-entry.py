#!/usr/bin/env python3
"""Unit floor for feature_schema.recovery_command_for and the uniform Build-entry rule (T-11,
BUG-1309, DEC-217's Over clause; FEAT-71 removed the per-feature era exemption). Each case is
aimed at a state or observable that no
integration bed reaches (see tests/integration/test-check-state.py:4622-4699's fixture, which
always writes exactly one task with os.path.join'd paths — see this task's plan.yaml intent for
the case-by-case cross-check). Mutation-based discrimination proof for these cases lives outside
this file (throwaway scripts against a mutated copy, never the real feature_schema.py) and is
recorded in this task's receipt.

python3 stdlib only. gh-sync.py's own BIN-dir resolution convention
(tests/unit/test-handoff-done-when.py:7-10); reporting convention
(tests/unit/test-handoff-done-when.py:15-18).

    ./test-feature-schema-build-entry.py    -> exit 0 all pass, 1 otherwise
"""
import json
import os
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / ".claude" / "skills" / "harness" / "bin"
sys.path.insert(0, str(BIN))
import feature_schema  # noqa: E402

failures = []


def check(name, ok, detail=""):
    print("PASS" if ok else "FAIL", name, detail if not ok else "")
    if not ok:
        failures.append(name)


def feat_dir(tmp, name, trailing_slash=False):
    d = os.path.join(tmp, ".harness", "harness", "features", name)
    os.makedirs(d, exist_ok=True)
    return d + "/" if trailing_slash else d


def write_plan(d, status, tasks):
    """Write a schema-valid plan so each case isolates recovery state."""
    lines = [
        "schema: plan/1",
        f"feature: {os.path.basename(d)}",
        f"status: {status}",
    ]
    if tasks:
        lines.append("tasks:")
        required = {
            "title": "fixture task",
            "change_type": "bugfix",
            "execution_mode": "main-session-direct",
            "files": ["fixture.py"],
            "verify": "true",
            "intent": "exercise recovery state",
        }
        for task in tasks:
            lines.append(f"  - {json.dumps({**required, **task})}")
    else:
        lines.extend(("station_only: true", "tasks: []"))
    with open(os.path.join(d, "plan.yaml"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


# FEAT-71: NO FEATURE ID IS EXEMPT. The Build-entry rule once consulted a frozen set of feature
# directory names; the rule is now uniform, so the module must hold no per-feature id table at
# all, and every id behaves exactly as a fresh synthetic one. The ids probed are the synthetic
# ones below PLUS every feature-id-shaped string the module itself holds as data — read from the
# module, never written here, so this file names no real feature and still goes red against any
# build that reintroduces a per-feature table.
_FEATURE_ID = re.compile(r"^(FEAT|BUG|PR)-[0-9]+")


def module_feature_id_tables(module):
    """{global name: sorted feature-id-shaped members} for each module-level collection."""
    tables = {}
    for name, value in vars(module).items():
        if isinstance(value, dict):
            members = value.keys()
        elif isinstance(value, (set, frozenset, list, tuple)):
            members = value
        else:
            continue
        ids = sorted(m for m in members if isinstance(m, str) and _FEATURE_ID.match(m))
        if ids:
            tables[name] = ids
    return tables


TABLES = module_feature_id_tables(feature_schema)
check("FEAT-71 feature_schema holds no per-feature id table", TABLES == {},
      repr({name: f"{len(ids)} ids, e.g. {ids[:3]}" for name, ids in TABLES.items()}))
PROBE_IDS = ["FEAT-90-fixture", "BUG-9-x", "PR-9-fixture"] + sorted(
    {i for ids in TABLES.values() for i in ids})

# BE-02: a would-be-open plan is `open` for EVERY feature id, with or without a trailing slash
# on feat_dir — no id short-circuits to recover-terminal.
with tempfile.TemporaryDirectory() as tmp:
    shortcut = []
    for name in PROBE_IDS:
        for slash in (False, True):
            d = feat_dir(tmp, name, trailing_slash=slash)
            write_plan(d, "building", [{"id": "T-01"}])
            got = feature_schema.recovery_command_for(d)
            if got != "open":
                shortcut.append((name, slash, got))
    check("BE-02 a building plan with no task done is open for every feature id",
          shortcut == [], f"{len(shortcut)} short-circuited, e.g. {shortcut[:3]}")

# BE-10: a feature with no Build-entry receipt (absent, or recovery-required) never allows a
# merge, whatever its id.
allowed = [(name, entry) for name in PROBE_IDS for entry in (None, "recovery-required")
           if feature_schema.receipt_allows_merge(
               {"feature_id": name, "github": {} if entry is None else {"build_entry": entry}},
               "org/product")]
check("BE-10 no receipt allows no merge for any feature id", allowed == [],
      f"{len(allowed)} allowed, e.g. {allowed[:3]}")

# BE-03: a feature with no plan.yaml returns recover-terminal.
with tempfile.TemporaryDirectory() as tmp:
    d = feat_dir(tmp, "FEAT-9002-fixture-no-plan")
    got = feature_schema.recovery_command_for(d)
    check("BE-03 a feature with no plan.yaml returns recover-terminal",
          got == "recover-terminal", repr(got))

# BE-04: a feature whose plan.yaml does not parse returns recover-terminal.
with tempfile.TemporaryDirectory() as tmp:
    d = feat_dir(tmp, "FEAT-9003-fixture-bad-yaml")
    with open(os.path.join(d, "plan.yaml"), "w", encoding="utf-8") as f:
        f.write("status: building\ntasks: [\n  - unterminated flow sequence\n")
    got = feature_schema.recovery_command_for(d)
    check("BE-04 a feature whose plan.yaml does not parse returns recover-terminal",
          got == "recover-terminal", repr(got))

# BE-06: plan status done returns recover-terminal, isolated from the any()-task-done trigger
# by giving the one task a non-done status.
with tempfile.TemporaryDirectory() as tmp:
    d = feat_dir(tmp, "FEAT-9004-fixture-plan-done")
    write_plan(d, "done", [{"id": "T-01", "status": "building"}])
    got = feature_schema.recovery_command_for(d)
    check("BE-06 plan status done returns recover-terminal", got == "recover-terminal", repr(got))

# BE-08: a plan at status building with THREE tasks, none carrying a status of done, returns
# open; and the SAME three-task plan with only the LAST task carrying status done returns
# recover-terminal, so the any() scans every task rather than the first.
with tempfile.TemporaryDirectory() as tmp:
    d1 = feat_dir(tmp, "FEAT-9005-fixture-three-open")
    write_plan(d1, "building", [{"id": "T-01"}, {"id": "T-02"}, {"id": "T-03"}])
    leg1 = feature_schema.recovery_command_for(d1)
    d2 = feat_dir(tmp, "FEAT-9006-fixture-last-done")
    write_plan(d2, "building",
               [{"id": "T-01"}, {"id": "T-02"}, {"id": "T-03", "status": "done"}])
    leg2 = feature_schema.recovery_command_for(d2)
    check("BE-08 building with three tasks none done is open, and only-last-done is "
          "recover-terminal",
          leg1 == "open" and leg2 == "recover-terminal",
          f"leg1={leg1!r} leg2={leg2!r}")

# BE-09: plan status building with an empty tasks list returns open.
with tempfile.TemporaryDirectory() as tmp:
    d = feat_dir(tmp, "FEAT-9007-fixture-empty-tasks")
    write_plan(d, "building", [])
    got = feature_schema.recovery_command_for(d)
    check("BE-09 plan status building with an empty tasks list returns open",
          got == "open", repr(got))

# A plan-flow SIMPLIFY run an engineering lead hosts before signature grades a specification
# (code_grade n_a): replacement stays full. An engineering run that reviewed code is started work.
with tempfile.TemporaryDirectory() as tmp:
    d = feat_dir(tmp, "FEAT-9011-fixture-plan-simplify")
    write_plan(d, "ready", [{"id": "T-01", "status": "ready"}])
    plan_flow = {"id": "r1", "squad": "engineering", "verdict": "PASS", "code_grade": "n_a"}
    built = {"id": "r2", "squad": "engineering", "verdict": "PASS"}
    legs = [feature_schema.recovery_command_for(d, {"runs": runs}, replacement=True)
            for runs in ([plan_flow], [plan_flow, built])]
    check("a plan-flow engineering simplify run is not started work; a code-graded one is",
          legs == ["open", "recover-terminal"], repr(legs))

# The runs[] agent rule is uniform too: an entry without `agent` is refused at index 0 under
# every feature directory name.
exempted = []
for name in PROBE_IDS:
    doc = {"feature_id": name, "branch": "none", "pr": None, "review_sha": "none",
           "cycles_used": 0, "max_total_cycles": 10,
           "runs": [{"id": "r1", "squad": "eng", "verdict": "PASS"}]}
    probs = feature_schema.problems_for_text(
        json.dumps(doc), f"/tmp/x/.harness/harness/features/{name}/feature.json")
    if not any("runs[0]" in p and "'agent'" in p for p in probs):
        exempted.append(name)
check("FEAT-71 a runs entry without agent is refused at index 0 for every feature id",
      exempted == [], f"{len(exempted)} exempt, e.g. {exempted[:3]}")


# FEAT-64 (SC-03): the plan read is a TYPED boundary. A plan that does not parse is
# recover-terminal (harness_yaml.YamlParseError, the loader's own class); an unrelated
# programming defect in the loader must escape, never be read as "the plan is unusable".
import artifact_accessors  # noqa: E402
with tempfile.TemporaryDirectory() as tmp:
    d = feat_dir(tmp, "FEAT-9010-fixture-bad-yaml")
    Path(d, "plan.yaml").write_text("schema: plan/1\ntasks: [\n", encoding="utf-8")
    got = feature_schema.recovery_command_for(d)
    check("FEAT-64 BE-11 a plan.yaml that does not parse is recover-terminal",
          got == "recover-terminal", repr(got))
    _real = artifact_accessors.load_plan
    def _boom(path):
        raise RuntimeError("unrelated defect")
    artifact_accessors.load_plan = _boom
    try:
        try:
            feature_schema.recovery_command_for(d)
            escaped = False
        except RuntimeError:
            escaped = True
    finally:
        artifact_accessors.load_plan = _real
    check("FEAT-64 BE-12 an unrelated RuntimeError in the plan loader escapes recovery_command_for",
          escaped)

allows = getattr(feature_schema, "receipt_allows_merge", None)
bound = {"repo": "org/product"}
check("a bound feature's opened mapping without github.repo is not repository provenance",
      callable(allows) and not allows(
          {"factory": bound, "github": {"parent": 7, "build_entry": "opened"}}, "org/product"))
if callable(allows):
    for name, doc, expected in (
        ("matching opened generation",
         {"github": {"repo": "org/product", "parent": 7, "build_entry": "opened"}}, True),
        ("wrong repository",
         {"github": {"repo": "org/owner", "parent": 7, "build_entry": "opened"}}, False),
        ("bound wrong repository",
         {"factory": bound, "github": {"repo": "org/owner", "parent": 7, "build_entry": "opened"}},
         False),
        ("legacy unbound opened, created by the owner binding that still resolves it",
         {"github": {"parent": 7, "build_entry": "opened"}}, True),
        ("legacy unbound recovered-terminal",
         {"github": {"milestone": 3, "parent": 7, "build_entry": "recovered-terminal"}}, True),
        ("unresolved owner repository", {"github": {"parent": 7, "build_entry": "opened"}}, None),
        ("replacement in progress", {"github": {"repo": "org/product", "build_entry": "opened",
                                                "recovery": {"state": "in-progress"}}}, False),
        ("uncertain create", {"github": {
            "repo": "org/product", "build_entry": "recovered-terminal",
            "recovery": {"state": "complete", "pending_create": {"role": "parent"}}}}, False),
        ("legacy unbound sync-off", {"github": {"build_entry": "not-applicable"}}, True),
    ):
        repo = None if expected is None else "org/product"
        check(f"repository-aware merge receipt: {name}",
              allows(doc, repo) is bool(expected))

resolve = getattr(feature_schema, "resolve_binding", None)
check("the shared binding resolver exists", callable(resolve))
if callable(resolve):
    with tempfile.TemporaryDirectory() as tmp:
        directory = Path(tmp, ".harness")
        directory.mkdir()
        Path(directory, "harness.json").write_text(
            json.dumps({"github": {"sync": False, "repo": None, "board": None}}), encoding="utf-8")
        check("unbound sync-off retains legal null board", resolve({}, tmp) == (None, None, {}))
        for malformed in ("", "owner", "../owner/product", 12, False):
            try:
                resolve({"factory": {"repo": malformed}}, tmp)
            except artifact_accessors.FleetError:
                refused = True
            else:
                refused = False
            check(f"invalid authoritative binding refuses before owner fallback: {malformed!r}", refused)

sys.exit(1 if failures else 0)
