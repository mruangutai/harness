#!/usr/bin/env python3
"""board_lifecycle.py provision must get these right — offline, against a fake gh (FEAT-33 T-04).

Modeled on test-board-station.py's shape (same `check()` convention) but board_lifecycle.py
resolves its root via `factory_config.harness_root()` (CLAUDE_PROJECT_DIR + the SPEC.md probe),
never board-station.py's own team-config.yaml walk-up, so the fixture writes that probe instead.

THE FAKE-BINARY TRAP (D-11): every case sets BOTH FACTORY_GH and GH_SYNC_GH to the SAME fake, even
though board_lifecycle.py itself only imports factory_gh — a future refactor routing some call
through gh-sync's own wrapper must not silently reach the real `gh`.

    ./test-board-lifecycle.py    -> exit 0 all pass, 1 otherwise
"""
import json
import os
import stat
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "board_lifecycle.py")
sys.path.insert(0, HERE)
import factory_config  # noqa: E402 -- only to read the SPEC.md probe path, never imported twice

FAILURES = []


def check(name, cond, detail=""):
    if cond:
        print(f"PASS  {name}")
    else:
        print(f"FAIL  {name}{(' — ' + detail) if detail else ''}")
        FAILURES.append(name)


def write_root(root, github, fleet=None):
    """A temp root carrying the SPEC.md probe factory_config.harness_root() needs, plus
    harness.json's github block. `fleet` (dict or None) writes .harness/factory/fleet.yaml only
    when given -- most cases never touch a fleet at all, mirroring test-factory-integration.py's
    own make_root, which never carries fleet.yaml unless a case needs it."""
    os.makedirs(os.path.join(root, os.path.dirname(factory_config._PROBE)), exist_ok=True)
    with open(os.path.join(root, factory_config._PROBE), "w", encoding="utf-8") as f:
        f.write("stub probe for T-04\n")
    os.makedirs(os.path.join(root, ".harness"), exist_ok=True)
    with open(os.path.join(root, ".harness", "harness.json"), "w", encoding="utf-8") as f:
        json.dump({"schema_version": 1, "github": github}, f)
    if fleet is not None:
        os.makedirs(os.path.join(root, ".harness", "factory"), exist_ok=True)
        with open(os.path.join(root, ".harness", "factory", "fleet.yaml"), "w",
                   encoding="utf-8") as f:
            f.write(
                f"schema: factory-fleet/1\n"
                f"workspace_root: {json.dumps(fleet['workspace_root'])}\n"
                f"repos:\n"
                + "".join(
                    f"  - name: {json.dumps(r['name'])}\n"
                    f"    default_branch: {json.dumps(r['default_branch'])}\n"
                    for r in fleet["repos"]
                )
            )


_BOARD = {
    "owner": "acme", "number": 9, "station_field": "Status",
    "stations": {"backlog": "Backlog", "plan": "Plan", "ready": "Ready",
                 "building": "Building", "review": "Review", "done": "Done"},
}


def default_github(board=_BOARD):
    return {"sync": True, "repo": "acme/widget", "board": board}


# ---------------- the ONE fake gh, parameterised by env vars the test sets ----------------
# RESOLVE_JSON answers project_resolve's own query (repositoryOwner(login:) with no field
# selection at all). PROBE_JSON answers board_lifecycle._field_probe's query (unique marker:
# ProjectV2IterationField -- a fragment no other query in this tree sends). OPTIONS_JSON answers
# factory_gh._project_field_resolve's query, the one project_field_options calls (unique marker:
# "options { id name }"). Every mutation gets one fixed, static success response -- no case here
# needs a mutation to behave differently, only to have happened or not.
FAKE_GH_SRC = r'''#!/bin/bash
# The GraphQL query argv carries REAL embedded newlines (it is a multi-line string, not a
# one-liner) -- collapsed to spaces FIRST, then to \001, so one call is always exactly one
# physical line in FAKE_LOG. Skipping the newline collapse would split one call across several
# log lines and make a positional .find()-ordering assertion compare the wrong lines.
echo "$*" | tr '\n' ' ' | tr ' ' '\001' >> "$FAKE_LOG"; echo >> "$FAKE_LOG"
case "$*" in
  *"createProjectV2Field"*)
    echo '{"data":{"createProjectV2Field":{"projectV2Field":{"id":"FIELD_STATUS_NEW"}}}}'
    exit 0 ;;
  *"updateProjectV2Field"*)
    echo '{"data":{"updateProjectV2Field":{"projectV2Field":{"id":"FIELD_STATUS"}}}}'
    exit 0 ;;
  *"linkProjectV2ToRepository"*)
    echo '{"data":{"linkProjectV2ToRepository":{"repository":{"id":"R_FAKE"}}}}'
    exit 0 ;;
  *"createProjectV2("*)
    echo '{"data":{"createProjectV2":{"projectV2":{"id":"PVT_NEW","number":42}}}}'
    exit 0 ;;
  *"ProjectV2IterationField"*)
    echo "$PROBE_JSON"
    exit 0 ;;
  *"options { id name }"*)
    echo "$OPTIONS_JSON"
    exit 0 ;;
  *"user(login: \$login) { id }"*)
    echo '{"data":{"user":{"id":"U_FAKE"}}}'
    exit 0 ;;
  *"repository(owner: \$owner, name: \$name) { id }"*)
    echo '{"data":{"repository":{"id":"R_FAKE"}}}'
    exit 0 ;;
  *"repositoryOwner(login: \$owner)"*)
    echo "$RESOLVE_JSON"
    exit 0 ;;
esac
echo "fake_gh: unmatched argv: $*" >&2
exit 1
'''

_RESOLVE_EXISTS = json.dumps(
    {"data": {"repositoryOwner": {"__typename": "User",
                                   "projectV2": {"id": "PVT_PROJ", "title": "Board"}}}})
_RESOLVE_ABSENT = json.dumps(
    {"data": {"repositoryOwner": {"__typename": "User", "projectV2": None}}})

_PROBE_ABSENT = json.dumps(
    {"data": {"repositoryOwner": {"__typename": "User",
                                   "projectV2": {"id": "PVT_PROJ", "field": None}}}})
_PROBE_SINGLE_SELECT = json.dumps(
    {"data": {"repositoryOwner": {"__typename": "User", "projectV2": {
        "id": "PVT_PROJ",
        "field": {"__typename": "ProjectV2SingleSelectField", "id": "FIELD_STATUS"}}}}})
_PROBE_TEXT_FIELD = json.dumps(
    {"data": {"repositoryOwner": {"__typename": "User", "projectV2": {
        "id": "PVT_PROJ", "field": {"__typename": "ProjectV2Field", "id": "FIELD_STATUS"}}}}})


def _options_json(names):
    return json.dumps(
        {"data": {"repositoryOwner": {"__typename": "User", "projectV2": {
            "id": "PVT_PROJ", "field": {"id": "FIELD_STATUS", "name": "Status",
                                         "options": [{"id": f"OPT_{n}", "name": n}
                                                      for n in names]}}}}})


_ALL_SIX = ["Backlog", "Plan", "Ready", "Building", "Review", "Done"]


def install_gh(tmp):
    path = os.path.join(tmp, "fake-gh")
    with open(path, "w") as f:
        f.write(FAKE_GH_SRC)
    os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)
    return path


def run(root, args, resolve=_RESOLVE_EXISTS, probe=_PROBE_SINGLE_SELECT,
        options=None, cwd=None):
    """Fork the real script. Returns (CompletedProcess, log_lines)."""
    tmp = os.path.dirname(root) if os.path.basename(root) == "root" else root
    gh_path = install_gh(tmp)
    log_path = os.path.join(tmp, "calls.log")
    env = dict(os.environ)
    env["CLAUDE_PROJECT_DIR"] = root
    env["FACTORY_GH"] = gh_path
    env["GH_SYNC_GH"] = gh_path
    env["FAKE_LOG"] = log_path
    env["RESOLVE_JSON"] = resolve
    env["PROBE_JSON"] = probe
    env["OPTIONS_JSON"] = options if options is not None else _options_json(_ALL_SIX)
    env.pop("HARNESS_GH_COST_LOG", None)
    r = subprocess.run(
        [sys.executable, SCRIPT] + args,
        capture_output=True, text=True, env=env, cwd=cwd or tmp,
    )
    lines = []
    if os.path.isfile(log_path):
        with open(log_path) as f:
            lines = [l for l in f.read().splitlines() if l]
    return r, lines


def mutation_calls(log):
    """Every logged call that carries a WRITE mutation -- never a read query. Used to assert
    "zero mutations" precisely, rather than "the log is empty" (a read that never happened would
    pass that too, for the wrong reason)."""
    markers = ("createProjectV2Field", "updateProjectV2Field", "linkProjectV2ToRepository",
               "createProjectV2(")
    return [l for l in log if any(m in l for m in markers)]


# ---------------- case 1: complete board -- zero mutations, exit 0 ----------------

with tempfile.TemporaryDirectory() as base:
    root = os.path.join(base, "root")
    write_root(root, default_github())
    r, log = run(root, ["provision"])
    check("complete board: exits 0",
          r.returncode == 0, f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")
    check("complete board: performs ZERO mutations (not merely exit 0)",
          not mutation_calls(log), repr(log))
    check("complete board: reports nothing to do",
          "nothing to do" in r.stdout, repr(r.stdout))

    # a second consecutive run performs zero mutations too.
    r2, log2 = run(root, ["provision"])
    check("complete board: a second consecutive run also performs zero mutations",
          r2.returncode == 0 and not mutation_calls(log2), f"rc={r2.returncode} log={log2}")

# ---------------- case 2: missing options -- extend with existing-then-additions ----------

with tempfile.TemporaryDirectory() as base:
    root = os.path.join(base, "root")
    write_root(root, default_github())
    existing = ["Backlog", "Plan", "Ready", "Building"]
    r, log = run(root, ["provision"], options=_options_json(existing))
    extend_calls = [l for l in log if "updateProjectV2Field" in l]
    check("missing options: exits 0 and calls updateProjectV2Field exactly once",
          r.returncode == 0 and len(extend_calls) == 1,
          f"rc={r.returncode} stdout={r.stdout!r} log={log}")
    check("missing options: sends existing options first, in existing order, then the "
          "additions, and never touches createProjectV2Field",
          extend_calls
          and extend_calls[0].find("Backlog") < extend_calls[0].find("Plan")
          < extend_calls[0].find("Ready") < extend_calls[0].find("Building")
          < extend_calls[0].find("Review") < extend_calls[0].find("Done")
          and "createProjectV2Field" not in extend_calls[0],
          repr(extend_calls))

# ---------------- SC-08: no argv ever carries the literal string "Abandoned" -------------
# Deliberately run against the SAME missing-options fixture as case 2 -- a real mutation
# happens here, so the assertion is not vacuous. This is NOT T-02's seven-key rejection case,
# which passes identically for a seventh key of any name; this is the literal-string guard
# SC-08 names as board_lifecycle's own discriminating assertion.

with tempfile.TemporaryDirectory() as base:
    root = os.path.join(base, "root")
    write_root(root, default_github())
    r, log = run(root, ["provision"], options=_options_json(["Backlog", "Plan"]))
    check("SC-08: no argv the fake receives contains the string 'Abandoned'",
          r.returncode == 0 and log and not any("Abandoned" in l for l in log),
          repr(log))

# ---------------- case 3: field absent -- created with all six, in declared order --------

with tempfile.TemporaryDirectory() as base:
    root = os.path.join(base, "root")
    write_root(root, default_github())
    r, log = run(root, ["provision"], probe=_PROBE_ABSENT)
    create_calls = [l for l in log if "createProjectV2Field" in l]
    check("field absent: exits 0 and calls createProjectV2Field exactly once",
          r.returncode == 0 and len(create_calls) == 1,
          f"rc={r.returncode} stdout={r.stdout!r} log={log}")
    check("field absent: sends all six declared options in declared order",
          create_calls
          and create_calls[0].find("Backlog") < create_calls[0].find("Plan")
          < create_calls[0].find("Ready") < create_calls[0].find("Building")
          < create_calls[0].find("Review") < create_calls[0].find("Done"),
          repr(create_calls))
    # THE DISASTER GUARD (i): the project EXISTS (RESOLVE_JSON default is _RESOLVE_EXISTS in
    # this case) and the field is absent -- assert project_create (createProjectV2( with no
    # trailing "Field") was NEVER called. "createProjectV2Field" legitimately appears in this
    # very log, so the substring checked here must exclude it, matching the established
    # in-tree convention (test-factory-integration.py:1239).
    check("field absent (disaster guard i): factory_gh.project_create was NOT called",
          not any("createProjectV2(" in l and "createProjectV2Field" not in l for l in log),
          repr(log))

# ---------------- case 4: field exists but is NOT single-select -- exit 2, zero mutations -

with tempfile.TemporaryDirectory() as base:
    root = os.path.join(base, "root")
    write_root(root, default_github())
    r, log = run(root, ["provision"], probe=_PROBE_TEXT_FIELD)
    check("field wrong type (disaster guard ii): exits 2",
          r.returncode == 2, f"rc={r.returncode} stderr={r.stderr!r}")
    check("field wrong type (disaster guard ii): names the field and its actual data type",
          "Status" in r.stderr and "ProjectV2Field" in r.stderr, repr(r.stderr))
    check("field wrong type (disaster guard ii): ZERO mutations of any kind reached the fake",
          not mutation_calls(log), repr(log))

# ---------------- case 5: no project -- creates, links, exits 3 --------------------------

with tempfile.TemporaryDirectory() as base:
    root = os.path.join(base, "root")
    write_root(root, default_github())
    r, log = run(root, ["provision"], resolve=_RESOLVE_ABSENT)
    check("no project: exits 3",
          r.returncode == 3, f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")
    check("no project: creates the project and links the repository",
          any("createProjectV2(" in l and "createProjectV2Field" not in l for l in log)
          and any("linkProjectV2ToRepository" in l for l in log),
          repr(log))
    check("no project: reports the new project number",
          "42" in r.stdout, repr(r.stdout))
    check("no project: never calls createProjectV2Field or updateProjectV2Field",
          not any("createProjectV2Field" in l or "updateProjectV2Field" in l for l in log),
          repr(log))

# ---------------- case 6: an explicit null board -- exits 0, writes nothing --------------

with tempfile.TemporaryDirectory() as base:
    root = os.path.join(base, "root")
    write_root(root, {"sync": True, "repo": "acme/widget", "board": None})
    r, log = run(root, ["provision"])
    check("null board: exits 0 silently, no gh call at all",
          r.returncode == 0 and not log and "no board declared" in r.stdout,
          f"rc={r.returncode} stdout={r.stdout!r} log={log}")

# ---------------- case 7: an unknown --repo -- exits 2 -----------------------------------

with tempfile.TemporaryDirectory() as base:
    root = os.path.join(base, "root")
    write_root(root, default_github(),
               fleet={"workspace_root": os.path.join(base, "ws"),
                      "repos": [{"name": "acme/other", "default_branch": "main"}]})
    r, log = run(root, ["provision", "--repo", "acme/unknown-repo"])
    check("unknown --repo: exits 2, naming the repo, with no gh call at all",
          r.returncode == 2 and not log and "acme/unknown-repo" in r.stderr,
          f"rc={r.returncode} stderr={r.stderr!r} log={log}")

print(f"\n{len(FAILURES)} failing." if FAILURES else "\nall checks passed.")
sys.exit(1 if FAILURES else 0)
