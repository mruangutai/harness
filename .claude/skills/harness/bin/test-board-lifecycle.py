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


def write_feature(root, repo_slug, feat, status, parent=None, github_issues=None,
                   factory_issues=None):
    """A `feature.json` fixture at `<root>/.harness/<repo_slug>/features/<feat>/feature.json` —
    the SAME `.harness/*/features/*/feature.json` glob shape `board_lifecycle.py`'s own
    `_feature_dirs` reads, and check-state.sh's INV-24/INV-26 already read (T-15)."""
    fdir = os.path.join(root, ".harness", repo_slug, "features", feat)
    os.makedirs(fdir, exist_ok=True)
    doc = {"status": status}
    github = {}
    if parent is not None:
        github["parent"] = parent
    if github_issues is not None:
        github["issues"] = github_issues
    if github:
        doc["github"] = github
    if factory_issues is not None:
        doc["factory"] = {"issues": factory_issues}
    with open(os.path.join(fdir, "feature.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f)


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
# T-05's GhError case (exit 4): FAIL_MATCH, when set, forces any call whose argv contains it to
# fail BEFORE the normal dispatch below sees it -- so "an audit that could not run" is a real
# failure of one specific network call, not a fake gap.
if [ -n "$FAIL_MATCH" ]; then
  case "$*" in
    *"$FAIL_MATCH"*)
      echo "fake_gh: forced failure for T-05's GhError case" >&2
      exit 1 ;;
  esac
fi
# T-06 (reconcile): a marker file toggles the "before" vs "after" answer for the three reads a
# write can affect (issues, stations, workflows never changes and keeps its single env var).
# `FAKE_STATE`, when set, is touched by every successful WRITE case below; a read case that
# finds it touched AND has an "_AFTER" variant set serves that instead of the original -- the
# test author (never this fake) computes what the after-state should look like, since success
# or failure per record is already deterministic given FAIL_MATCH.
_after() {
  # $1 = the "before" value, $2 = the name of the "_AFTER" env var.
  if [ -f "$FAKE_STATE" ]; then
    after_val=$(eval "echo \"\$$2\"")
    if [ -n "$after_val" ]; then
      echo "$after_val"
      return
    fi
  fi
  echo "$1"
}
case "$*" in
  *"issue list"*)
    _after "$ISSUES_JSON" ISSUES_JSON_AFTER
    exit 0 ;;
  *"fieldValueByName"*)
    _after "$STATIONS_JSON" STATIONS_JSON_AFTER
    exit 0 ;;
  *"workflows(first:"*)
    echo "$WORKFLOWS_JSON"
    exit 0 ;;
  *"projectItems"*)
    # T-06: factory_gh.issue_board_item_id, the query gh_board.set_station sends before its
    # own item-edit mutation. project.number MUST equal the fixture's board number (9,
    # `_BOARD["number"]`) -- set_station matches client-side against it.
    item_id="${ITEM_ID:-ITEM_FAKE}"
    echo "{\"data\":{\"repository\":{\"issue\":{\"projectItems\":{\"totalCount\":1,\"nodes\":[{\"id\":\"$item_id\",\"project\":{\"number\":9}}]}}}}}"
    exit 0 ;;
  *"project item-edit"*)
    # T-06: gh_board.set_station's own mutation, sent after the field-resolve
    # ("options { id name }") and item-lookup ("projectItems") calls above.
    if [ -n "$FAKE_STATE" ]; then
      touch "$FAKE_STATE"
    fi
    exit 0 ;;
  *"label create"*)
    # T-06: board_lifecycle.py's own direct shell-out (never a helper) for the `abandoned`
    # label. Always succeeds here; the swallow-on-failure behaviour is this module's own, not
    # this fake's, to prove.
    if [ -n "$FAKE_STATE" ]; then
      touch "$FAKE_STATE"
    fi
    exit 0 ;;
  *"issue edit"*)
    # T-06: `gh issue edit <n> --add-label abandoned` (LABEL) — never confused with
    # "issue list" above, a disjoint literal.
    if [ -n "$FAKE_STATE" ]; then
      touch "$FAKE_STATE"
    fi
    exit 0 ;;
  *"state_reason="*)
    # T-06: `gh api -X PATCH repos/<repo>/issues/<n> -f state=closed -f state_reason=...`
    # (REASON).
    if [ -n "$FAKE_STATE" ]; then
      touch "$FAKE_STATE"
    fi
    exit 0 ;;
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

# T-05 additions -- the three read-only queries `audit` sends that `provision` never does.

_ALL_WORKFLOWS_ENABLED = json.dumps(
    {"data": {"user": {"projectV2": {"workflows": {"nodes": [
        {"name": "Item closed", "enabled": True, "number": 1},
        {"name": "Auto-close issue", "enabled": True, "number": 2},
        {"name": "Pull request merged", "enabled": True, "number": 3},
    ]}}}}})


def _workflows_json(workflows):
    """workflows: list of (name, enabled) pairs."""
    nodes = [{"name": n, "enabled": e, "number": i + 1} for i, (n, e) in enumerate(workflows)]
    return json.dumps({"data": {"user": {"projectV2": {"workflows": {"nodes": nodes}}}}})


def _stations_json(mapping, repo="acme/widget"):
    """mapping: {issue_number: station_name_or_None}, exactly `board_stations`'s own shape."""
    nodes = []
    for num, station in mapping.items():
        nodes.append({
            "content": {"number": num, "repository": {"nameWithOwner": repo}},
            "fieldValueByName": {"name": station} if station is not None else None,
        })
    return json.dumps({"data": {"user": {"projectV2": {"items": {
        "totalCount": len(nodes),
        "pageInfo": {"hasNextPage": False, "endCursor": None},
        "nodes": nodes,
    }}}}})


def install_gh(tmp):
    path = os.path.join(tmp, "fake-gh")
    with open(path, "w") as f:
        f.write(FAKE_GH_SRC)
    os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)
    return path


def run(root, args, resolve=_RESOLVE_EXISTS, probe=_PROBE_SINGLE_SELECT,
        options=None, issues=None, stations=None, workflows=None, fail_match=None, cwd=None,
        item_id=None, fake_state=None, issues_after=None, stations_after=None,
        workflows_after=None):
    """Fork the real script. Returns (CompletedProcess, log_lines).

    The T-06 `*_after` params (and `fake_state`) are the reconcile-only "before" vs "after"
    switch FAKE_GH_SRC's `_after` helper reads -- see its own comment for why a single marker
    file is enough: success/failure per record is already deterministic given `fail_match`, so
    the test author computes the correct after-state rather than the fake deriving it live."""
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
    env["ISSUES_JSON"] = issues if issues is not None else "[]"
    env["STATIONS_JSON"] = stations if stations is not None else _stations_json({})
    env["WORKFLOWS_JSON"] = workflows if workflows is not None else _ALL_WORKFLOWS_ENABLED
    env["FAIL_MATCH"] = fail_match or ""
    env["ITEM_ID"] = item_id or "ITEM_FAKE"
    env["FAKE_STATE"] = fake_state or os.path.join(tmp, "fake-state-absent-by-default")
    env["ISSUES_JSON_AFTER"] = issues_after or ""
    env["STATIONS_JSON_AFTER"] = stations_after or ""
    env["WORKFLOWS_JSON_AFTER"] = workflows_after or ""
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
               "createProjectV2(", "project\x01item-edit", "label\x01create", "issue\x01edit",
               "state_reason=")
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

# ============================================================================
# T-05: board_lifecycle.py audit -- the finite finding list, including workflow state.
# Every case sets BOTH FACTORY_GH and GH_SYNC_GH to the same fake (D-11), via `run()` above.
# ============================================================================

# ---------------- audit case 1: a clean board -- exit 0, zero findings -------------------

with tempfile.TemporaryDirectory() as base:
    root = os.path.join(base, "root")
    write_root(root, default_github())
    r, log = run(root, ["audit"])
    check("audit clean board: exits 0",
          r.returncode == 0, f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")
    check("audit clean board: reports zero findings",
          "0 finding(s)" in r.stdout, repr(r.stdout))
    check("audit clean board: no finding-class marker on stdout",
          not any(m in r.stdout for m in
                  ("DECLARATION:", "STATION:", "REASON:", "LABEL:", "WORKFLOW:", "STATUS:")),
          repr(r.stdout))

# ---------------- audit case 2: DECLARATION -- a declared value the board lacks ----------

with tempfile.TemporaryDirectory() as base:
    root = os.path.join(base, "root")
    write_root(root, default_github())
    r, log = run(root, ["audit"], options=_options_json(["Backlog", "Ready", "Building",
                                                          "Review", "Done"]))
    check("audit DECLARATION: exits 1", r.returncode == 1, f"rc={r.returncode}")
    check("audit DECLARATION: names the missing key and value on stdout",
          "DECLARATION" in r.stdout and "'plan'" in r.stdout and "'Plan'" in r.stdout,
          repr(r.stdout))

# ---------------- audit case 3: STATION -- a closed board issue off the done station -----

with tempfile.TemporaryDirectory() as base:
    root = os.path.join(base, "root")
    write_root(root, default_github())
    issues = json.dumps([{"number": 10, "stateReason": "COMPLETED", "labels": []}])
    r, log = run(root, ["audit"], issues=issues, stations=_stations_json({10: "Building"}))
    check("audit STATION: exits 1", r.returncode == 1, f"rc={r.returncode}")
    check("audit STATION: names the issue, its actual and expected station",
          "STATION" in r.stdout and "#10" in r.stdout
          and "'Building'" in r.stdout and "'Done'" in r.stdout,
          repr(r.stdout))

# ---------------- audit case 4: REASON -- a closed issue with a null close reason --------

with tempfile.TemporaryDirectory() as base:
    root = os.path.join(base, "root")
    write_root(root, default_github())
    issues = json.dumps([{"number": 20, "stateReason": None, "labels": []}])
    r, log = run(root, ["audit"], issues=issues)
    check("audit REASON: exits 1", r.returncode == 1, f"rc={r.returncode}")
    check("audit REASON: names the issue",
          "REASON" in r.stdout and "#20" in r.stdout, repr(r.stdout))

# ---------------- audit case 5: LABEL -- not_planned with no abandoned label -------------

with tempfile.TemporaryDirectory() as base:
    root = os.path.join(base, "root")
    write_root(root, default_github())
    issues = json.dumps([{"number": 30, "stateReason": "NOT_PLANNED", "labels": []}])
    r, log = run(root, ["audit"], issues=issues)
    check("audit LABEL: exits 1", r.returncode == 1, f"rc={r.returncode}")
    check("audit LABEL: names the issue",
          "LABEL" in r.stdout and "#30" in r.stdout, repr(r.stdout))

    # a sibling not_planned issue that DOES carry the label produces no LABEL finding.
    issues_ok = json.dumps([{"number": 31, "stateReason": "NOT_PLANNED",
                              "labels": [{"name": "abandoned"}]}])
    r2, log2 = run(root, ["audit"], issues=issues_ok)
    check("audit LABEL: a not_planned issue carrying the abandoned label is NOT a finding",
          r2.returncode == 0 and "LABEL" not in r2.stdout, repr(r2.stdout))

# ---------------- audit case 6: WORKFLOW -- renamed/absent reports MISSING ---------------

with tempfile.TemporaryDirectory() as base:
    root = os.path.join(base, "root")
    write_root(root, default_github())
    workflows = _workflows_json([("Item closed", True), ("Auto-close issue", True)])
    r, log = run(root, ["audit"], workflows=workflows)
    check("audit WORKFLOW (renamed/absent): exits 1", r.returncode == 1, f"rc={r.returncode}")
    check("audit WORKFLOW (renamed/absent): reports 'Pull request merged' MISSING",
          "WORKFLOW" in r.stdout and "'Pull request merged'" in r.stdout
          and "MISSING" in r.stdout, repr(r.stdout))
    check("audit WORKFLOW: the header names detection-by-name, once, on every run",
          r.stdout.count("workflow detection matches by NAME only") == 1, repr(r.stdout))

# ---------------- audit case 7: WORKFLOW -- present but disabled -------------------------

with tempfile.TemporaryDirectory() as base:
    root = os.path.join(base, "root")
    write_root(root, default_github())
    workflows = _workflows_json([("Item closed", True), ("Auto-close issue", False),
                                  ("Pull request merged", True)])
    r, log = run(root, ["audit"], workflows=workflows)
    check("audit WORKFLOW (disabled): exits 1", r.returncode == 1, f"rc={r.returncode}")
    check("audit WORKFLOW (disabled): reports 'Auto-close issue' disabled",
          "WORKFLOW" in r.stdout and "'Auto-close issue'" in r.stdout
          and "disabled" in r.stdout, repr(r.stdout))
    check("audit WORKFLOW (disabled): says no API can enable it, only the web UI can",
          "no API can enable it" in r.stdout and "web UI" in r.stdout, repr(r.stdout))

# ---------------- audit case 8: STATUS -- a recorded status disagreeing with its parent card
# (T-15, FEAT-33). feature.json IS THE AUTHORITY (T-13's outbound posture, DEC-138) -- the
# message names the feature directory, the recorded status, the column that status means, and
# the column the board actually reads. No extra network call: reuses STATIONS_JSON, the same
# station read STATION (class 2) already fetched.

with tempfile.TemporaryDirectory() as base:
    # FEAT-32 shape, recorded at f5f5185 as a written FIXTURE (T-15 intent) -- NOT a live board
    # state; FEAT-32 has since shipped and this shape is no longer on the real board.
    root = os.path.join(base, "root")
    write_root(root, default_github())
    write_feature(root, "widget", "FEAT-32-fixture", "Review", parent=700,
                  github_issues={"T-01": 701})
    r, log = run(root, ["audit"], stations=_stations_json({700: "Building"}))
    check("audit STATUS (FEAT-32 shape): exits 1", r.returncode == 1, f"rc={r.returncode}")
    check("audit STATUS (FEAT-32 shape): names the feature dir, recorded status, expected "
          "column and actual column",
          "STATUS" in r.stdout and "FEAT-32-fixture" in r.stdout
          and "'Review'" in r.stdout and "'Building'" in r.stdout, repr(r.stdout))

with tempfile.TemporaryDirectory() as base:
    # FEAT-08 shape, re-derived at 46ee87c: status Done, parent #85 still OPEN, board reads
    # Backlog. THERE IS NO Done EXEMPTION (D-22) -- this is a finding regardless of the parent
    # issue's open/closed state.
    root = os.path.join(base, "root")
    write_root(root, default_github())
    write_feature(root, "widget", "FEAT-08", "Done", parent=85, github_issues={"T-01": 86})
    r, log = run(root, ["audit"], stations=_stations_json({85: "Backlog"}))
    check("audit STATUS (FEAT-08 shape): exits 1", r.returncode == 1, f"rc={r.returncode}")
    check("audit STATUS (FEAT-08 shape): names the feature dir, status Done, expected Done, "
          "actual Backlog -- no Done exemption",
          "STATUS" in r.stdout and "FEAT-08" in r.stdout
          and "'Done'" in r.stdout and "'Backlog'" in r.stdout, repr(r.stdout))

with tempfile.TemporaryDirectory() as base:
    # FEAT-09 shape, its own assertion (T-15 intent: "each its own assertion").
    root = os.path.join(base, "root")
    write_root(root, default_github())
    write_feature(root, "widget", "FEAT-09", "Done", parent=98, github_issues={"T-01": 99})
    r, log = run(root, ["audit"], stations=_stations_json({98: "Backlog"}))
    check("audit STATUS (FEAT-09 shape): exits 1", r.returncode == 1, f"rc={r.returncode}")
    check("audit STATUS (FEAT-09 shape): names the feature dir, status Done, expected Done, "
          "actual Backlog",
          "STATUS" in r.stdout and "FEAT-09" in r.stdout
          and "'Done'" in r.stdout and "'Backlog'" in r.stdout, repr(r.stdout))

with tempfile.TemporaryDirectory() as base:
    # A matching status and card -- no finding.
    root = os.path.join(base, "root")
    write_root(root, default_github())
    write_feature(root, "widget", "FEAT-CLEAN", "Building", parent=500,
                  github_issues={"T-01": 501})
    r, log = run(root, ["audit"], stations=_stations_json({500: "Building"}))
    check("audit STATUS: a matching status and card is NOT a finding",
          r.returncode == 0 and "STATUS" not in r.stdout, repr(r.stdout))

with tempfile.TemporaryDirectory() as base:
    # Exemption 1 -- status Abandoned has no board column (DEC-192) to compare against, even
    # though the parent card reads something that would otherwise mismatch every mapped status.
    root = os.path.join(base, "root")
    write_root(root, default_github())
    write_feature(root, "widget", "FEAT-ABANDONED", "Abandoned", parent=600,
                  github_issues={"T-01": 601})
    r, log = run(root, ["audit"], stations=_stations_json({600: "Backlog"}))
    check("audit STATUS: exemption 1 -- Abandoned is exempt, no STATUS finding",
          r.returncode == 0 and "STATUS" not in r.stdout, repr(r.stdout))

with tempfile.TemporaryDirectory() as base:
    # Exemption 2 -- no recorded parent (INV-21's finding, not this one).
    root = os.path.join(base, "root")
    write_root(root, default_github())
    write_feature(root, "widget", "FEAT-NO-PARENT", "Building", parent=None)
    r, log = run(root, ["audit"])
    check("audit STATUS: exemption 2 -- no recorded parent is exempt, no STATUS finding",
          r.returncode == 0 and "STATUS" not in r.stdout, repr(r.stdout))

with tempfile.TemporaryDirectory() as base:
    # Exemption 3 -- issues recorded under factory.issues, not github.issues: this feature's
    # cards live on the PRODUCT's board, not this one. The station fixture deliberately
    # mismatches what a non-exempt comparison would expect, so a leaky exemption would redden.
    root = os.path.join(base, "root")
    write_root(root, default_github())
    write_feature(root, "widget", "FEAT-PRODUCT", "Building", parent=400,
                  factory_issues={"T-01": 401})
    r, log = run(root, ["audit"], stations=_stations_json({400: "Backlog"}))
    check("audit STATUS: exemption 3 -- factory.issues (product board) is exempt, no STATUS "
          "finding", r.returncode == 0 and "STATUS" not in r.stdout, repr(r.stdout))

# ---------------- audit case 9: a GhError propagates as exit 4, no findings printed ------
# DEC-186's inverse-of-the-mirror posture (T-05 intent): an audit that could not run must
# never be mistaken for exit 0 (clean) or exit 1 (findings). Forces the FIRST of the audit's
# four network calls (project_field_options) to fail, so nothing after it ever runs.

with tempfile.TemporaryDirectory() as base:
    root = os.path.join(base, "root")
    write_root(root, default_github())
    r, log = run(root, ["audit"], fail_match="options { id name }")
    check("audit GhError: exits 4, never 0 or 1",
          r.returncode == 4, f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")
    check("audit GhError: prints nothing that looks like a finding or a clean report",
          not any(m in r.stdout for m in
                  ("DECLARATION:", "STATION:", "REASON:", "LABEL:", "WORKFLOW:", "STATUS:",
                   "finding(s)")),
          repr(r.stdout))
    check("audit GhError: the failure is on stderr, one line",
          bool(r.stderr.strip()) and len(r.stderr.strip().splitlines()) == 1, repr(r.stderr))

# ============================================================================
# T-06: board_lifecycle.py reconcile -- the write side of audit. Every case sets BOTH
# FACTORY_GH and GH_SYNC_GH to the same fake (D-11), via run()'s own defaults.
# ============================================================================

# ---------------- reconcile case 1: a GhError propagates as exit 4 -----------------------

with tempfile.TemporaryDirectory() as base:
    root = os.path.join(base, "root")
    write_root(root, default_github())
    r, log = run(root, ["reconcile", "--apply"], fail_match="options { id name }")
    check("reconcile GhError: exits 4, never 0 or 1",
          r.returncode == 4, f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")

# ---------------- reconcile case 2: --dry-run (the default) performs ZERO mutations ------
# Fixture carries a fixable finding of every kind (STATION, REASON, LABEL, STATUS) so the
# "zero mutations" assertion is not vacuous.

_RECON_ISSUES = json.dumps([
    {"number": 10, "stateReason": "COMPLETED", "labels": []},
    {"number": 20, "stateReason": None, "labels": []},
    {"number": 30, "stateReason": "NOT_PLANNED", "labels": []},
])
_RECON_STATIONS_BEFORE = _stations_json({10: "Building", 40: "Ready"})
_RECON_STATIONS_AFTER = _stations_json({10: "Done", 40: "Building"})
_RECON_ISSUES_AFTER = json.dumps([
    {"number": 10, "stateReason": "COMPLETED", "labels": []},
    {"number": 20, "stateReason": "COMPLETED", "labels": []},
    {"number": 30, "stateReason": "NOT_PLANNED", "labels": [{"name": "abandoned"}]},
])


def _write_recon_fixture(base):
    root = os.path.join(base, "root")
    write_root(root, default_github())
    write_feature(root, "widget", "FEAT-RECON", "Building", parent=40,
                  github_issues={"T-01": 41})
    return root


with tempfile.TemporaryDirectory() as base:
    root = _write_recon_fixture(base)
    with open(os.path.join(root, ".harness", "widget", "features", "FEAT-RECON",
                            "feature.json"), encoding="utf-8") as f:
        feature_json_before = f.read()
    r, log = run(root, ["reconcile"], issues=_RECON_ISSUES, stations=_RECON_STATIONS_BEFORE)
    check("reconcile --dry-run: exits 0 even with fixable findings present",
          r.returncode == 0, f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")
    check("reconcile --dry-run: performs ZERO mutations (not merely exit 0)",
          not mutation_calls(log), repr(log))
    check("reconcile --dry-run: previews every fixable finding as a would-fix line",
          all(f"DRY-RUN would fix -- {kind}" in r.stdout
              for kind in ("STATION", "REASON:", "LABEL:", "STATUS")),
          repr(r.stdout))
    with open(os.path.join(root, ".harness", "widget", "features", "FEAT-RECON",
                            "feature.json"), encoding="utf-8") as f:
        check("reconcile --dry-run: never writes feature.json",
              f.read() == feature_json_before, "feature.json changed")

# ---------------- reconcile case 3: --apply fixes one of each fixable class --------------

with tempfile.TemporaryDirectory() as base:
    root = _write_recon_fixture(base)
    with open(os.path.join(root, ".harness", "widget", "features", "FEAT-RECON",
                            "feature.json"), encoding="utf-8") as f:
        feature_json_before = f.read()
    fake_state = os.path.join(base, "fixed-marker")
    r, log = run(
        root, ["reconcile", "--apply"], issues=_RECON_ISSUES, stations=_RECON_STATIONS_BEFORE,
        fake_state=fake_state, issues_after=_RECON_ISSUES_AFTER,
        stations_after=_RECON_STATIONS_AFTER,
    )
    check("reconcile --apply (one of each): exits 0 once every fixable finding is resolved",
          r.returncode == 0, f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")
    check("reconcile --apply (one of each): STATION -- set_station moves issue #10 to Done",
          any("number=10" in l for l in log) and any("OPT_Done" in l for l in log),
          repr(log))
    check("reconcile --apply (one of each): STATUS -- set_station moves the PARENT #40 to "
          "Building, never the issue's own number",
          any("number=40" in l for l in log) and any("OPT_Building" in l for l in log),
          repr(log))
    check("reconcile --apply (one of each): REASON -- PATCHes issue #20 to state_reason="
          "completed (it carries no abandoned label)",
          any("issues/20" in l and "state_reason=completed" in l for l in log), repr(log))
    check("reconcile --apply (one of each): LABEL -- creates the abandoned label with "
          "b60205 directly, then adds it to issue #30",
          any("label" in l and "create" in l and "abandoned" in l and "b60205" in l
              for l in log)
          and any("issue" in l and "edit" in l and "30" in l and "abandoned" in l
                  for l in log),
          repr(log))
    check("reconcile --apply (one of each): STATUS never rewrites feature.json -- the card "
          "moves, the recorded status does not",
          open(os.path.join(root, ".harness", "widget", "features", "FEAT-RECON",
                             "feature.json"), encoding="utf-8").read() == feature_json_before,
          "feature.json changed")
    check("reconcile --apply (one of each): the residual report says zero fixable findings "
          "remain",
          "0 fixable finding(s) remain" in r.stdout, repr(r.stdout))

# ---------------- reconcile case 4: a failed write mid-bulk-fix is a residual, not a stop -

with tempfile.TemporaryDirectory() as base:
    root = os.path.join(base, "root")
    write_root(root, default_github())
    issues = json.dumps([
        {"number": 50, "stateReason": "COMPLETED", "labels": []},
        {"number": 51, "stateReason": "COMPLETED", "labels": []},
    ])
    stations_before = _stations_json({50: "Building", 51: "Building"})
    stations_after = _stations_json({50: "Building", 51: "Done"})
    fake_state = os.path.join(base, "fixed-marker")
    r, log = run(
        root, ["reconcile", "--apply"], issues=issues, stations=stations_before,
        fail_match="number=50", fake_state=fake_state, stations_after=stations_after,
    )
    check("reconcile (partial failure): the run continues past issue #50's failed write to "
          "issue #51 -- #51's item lookup was actually sent",
          any("number=51" in l for l in log), repr(log))
    check("reconcile (partial failure): issue #50's failure is reported on stderr",
          "50" in r.stderr, repr(r.stderr))
    check("reconcile (partial failure): #50 survives as a residual STATION finding, #51 does "
          "not",
          "STATION: issue #50" in r.stdout and "STATION: issue #51" not in r.stdout,
          repr(r.stdout))
    check("reconcile (partial failure): exits 1 -- a bulk fix that stops at the first error "
          "must never report a zero exit with the board half migrated",
          r.returncode == 1, f"rc={r.returncode}")

# ---------------- reconcile case 5: DECLARATION and WORKFLOW residuals never gate exit 0 --

with tempfile.TemporaryDirectory() as base:
    root = os.path.join(base, "root")
    write_root(root, default_github())
    workflows = _workflows_json([("Item closed", True), ("Auto-close issue", True)])
    r, log = run(
        root, ["reconcile", "--apply"],
        options=_options_json(["Backlog", "Ready", "Building", "Review", "Done"]),
        workflows=workflows,
    )
    check("reconcile (unfixable residuals): DECLARATION and WORKFLOW both survive on stdout",
          "DECLARATION" in r.stdout and "WORKFLOW" in r.stdout, repr(r.stdout))
    check("reconcile (unfixable residuals): exits 0 anyway -- neither class is ever attempted "
          "or counted", r.returncode == 0, f"rc={r.returncode} stdout={r.stdout!r}")
    check("reconcile (unfixable residuals): performs zero mutations -- neither class is a "
          "write this tool can make",
          not mutation_calls(log), repr(log))

# ---------------- reconcile case 6: a Done-status STATUS finding is never auto-fixed -----
# T-15's own exemption (Done and Abandoned have no automated write here) applied to the WRITE
# side: a Done-status mismatch is a genuine finding (D-22, no Done exemption in DETECTION) but
# reconcile does not move a card to the done station on its own say -- it is left for a human
# exactly like DECLARATION and WORKFLOW.

with tempfile.TemporaryDirectory() as base:
    root = os.path.join(base, "root")
    write_root(root, default_github())
    write_feature(root, "widget", "FEAT-DONE-MISMATCH", "Done", parent=85,
                  github_issues={"T-01": 86})
    r, log = run(root, ["reconcile", "--apply"], stations=_stations_json({85: "Backlog"}))
    check("reconcile (Done exemption): the STATUS finding survives --apply untouched",
          "STATUS" in r.stdout and "FEAT-DONE-MISMATCH" in r.stdout, repr(r.stdout))
    check("reconcile (Done exemption): exits 0 anyway -- Done is excluded from the exit-code "
          "count the SAME way DECLARATION and WORKFLOW are (never attempted, never counted); "
          "counting it would permanently gate exit 0 on a class this tool never fixes by "
          "design, the identical reasoning the module docstring gives for excluding WORKFLOW",
          r.returncode == 0, f"rc={r.returncode}")
    check("reconcile (Done exemption): never calls set_station for issue #85",
          not any("number=85" in l for l in log), repr(log))

# ---------------- reconcile case 7: a fully reconciled fixture -- exit 0, zero writes -----

with tempfile.TemporaryDirectory() as base:
    root = os.path.join(base, "root")
    write_root(root, default_github())
    r, log = run(root, ["reconcile", "--apply"])
    check("reconcile (clean board): exits 0", r.returncode == 0, f"rc={r.returncode}")
    check("reconcile (clean board): performs ZERO mutations",
          not mutation_calls(log), repr(log))
    check("reconcile (clean board): re-running it again also exits 0 with zero mutations",
          True, "")
    r2, log2 = run(root, ["reconcile", "--apply"])
    check("reconcile (clean board, second run): idempotent -- exits 0, zero mutations",
          r2.returncode == 0 and not mutation_calls(log2), f"rc={r2.returncode} log={log2}")

# ============================================================================
# T-17: board_lifecycle.py retitle -- the task-ticket title backfill.
# Every case sets BOTH FACTORY_GH and GH_SYNC_GH to the same fake (D-11), via `run()` above.
# retitle never touches a project or a card, only issue titles, so most of these cases never
# even set a board -- `default_github()`'s board is present only because `_resolve_board` is
# reused for the repo-name half and discards it.
# ============================================================================


def rename_calls(log):
    """Every logged call that is retitle's own write -- `gh issue edit <n> --title <new>` --
    distinct from `mutation_calls`'s LABEL-edit marker (`issue\\x01edit` also matches an
    `--add-label` call from T-06, which retitle never sends): a rename call additionally
    carries `--title` in the same logged line."""
    return [l for l in log if "issue\x01edit" in l and "--title" in l]


# ---------------- retitle case 1: a ticket with a milestone -- renamed to the exact string -

with tempfile.TemporaryDirectory() as base:
    root = os.path.join(base, "root")
    write_root(root, default_github())
    old_title = "T-9 — Add the retitle command"
    new_title = "FEAT-9-widget — T-9 — Add the retitle command"  # byte-identical to what
    # gh-sync.py's cmd_open would write today for this same task (f"{feat} — {tid} — {title}",
    # gh-sync.py:764) -- verified against the live source line, not merely asserted here.
    issues = json.dumps([{"number": 101, "title": old_title,
                           "milestone": {"title": "FEAT-9-widget"}}])
    r, log = run(root, ["retitle", "--apply"], issues=issues)
    check("retitle (has milestone): exits 0",
          r.returncode == 0, f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")
    check("retitle (has milestone): the summary line reports it renamed",
          f"renamed #101: {old_title!r} -> {new_title!r}" in r.stdout, repr(r.stdout))
    rc = rename_calls(log)
    check("retitle (has milestone): exactly one rename call reaches the fake, for issue 101, "
          "carrying the new title verbatim in its argv",
          len(rc) == 1 and "101" in rc[0] and new_title.replace(" ", "\x01") in rc[0],
          repr(log))

# ---------------- retitle case 2: a ticket with NO milestone -- refused, no rename call -----

with tempfile.TemporaryDirectory() as base:
    root = os.path.join(base, "root")
    write_root(root, default_github())
    issues = json.dumps([{"number": 202, "title": "T-3 — Something else", "milestone": None}])
    r, log = run(root, ["retitle", "--apply"], issues=issues)
    check("retitle (no milestone): exits 0 -- a per-ticket refusal never fails the whole run",
          r.returncode == 0, f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")
    check("retitle (no milestone): the refusal names issue #202 (SC-18)",
          "REFUSED" in r.stdout and "202" in r.stdout, repr(r.stdout))
    check("retitle (no milestone): NO rename call is issued for it",
          not rename_calls(log), repr(log))

# ---------------- retitle case 3: a ticket already carrying its feature id -- skipped ------
# A title already starting with its own milestone title followed by " — " is idempotent-skip
# (D-20's own mechanism, no state file). Constructed so the milestone title ITSELF is "T-9" --
# an unusual milestone title, but it is what makes one fixture satisfy both the selection
# regex (which needs `^T-\d+ — `) and the already-correct prefix check in the same title,
# exactly as the plan's step 4 describes -- a real feature id (`FEAT-NN-slug`) never begins
# with `T-\d+`, so this shape does not occur on the live backfill and is not claimed to.

with tempfile.TemporaryDirectory() as base:
    root = os.path.join(base, "root")
    write_root(root, default_github())
    issues = json.dumps([{"number": 303, "title": "T-9 — already renamed rest",
                           "milestone": {"title": "T-9"}}])
    r, log = run(root, ["retitle", "--apply"], issues=issues)
    check("retitle (already correct): exits 0",
          r.returncode == 0, f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")
    check("retitle (already correct): NOT reported as refused or renamed",
          "REFUSED" not in r.stdout and "renamed #303" not in r.stdout, repr(r.stdout))
    check("retitle (already correct): the summary counts it already correct",
          "already correct: 1" in r.stdout, repr(r.stdout))
    check("retitle (already correct): NO rename call is issued for it",
          not rename_calls(log), repr(log))

# ---------------- retitle case 4: a truncated enumeration -- refused with exit 2 -----------

with tempfile.TemporaryDirectory() as base:
    root = os.path.join(base, "root")
    write_root(root, default_github())
    issues = json.dumps([{"number": i, "title": "unrelated", "milestone": None}
                          for i in range(1000)])
    r, log = run(root, ["retitle", "--apply"], issues=issues)
    check("retitle (truncated enumeration): exits 2",
          r.returncode == 2, f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")
    check("retitle (truncated enumeration): names the returned count and the limit",
          "1000" in r.stderr, repr(r.stderr))
    check("retitle (truncated enumeration): NO rename call is issued -- the refusal is before "
          "any write is attempted",
          not rename_calls(log), repr(log))

# ---------------- retitle case 5: --dry-run -- zero write calls ----------------------------

with tempfile.TemporaryDirectory() as base:
    root = os.path.join(base, "root")
    write_root(root, default_github())
    old_title = "T-9 — Add the retitle command"
    issues = json.dumps([{"number": 101, "title": old_title,
                           "milestone": {"title": "FEAT-9-widget"}}])
    r, log = run(root, ["retitle"], issues=issues)  # --dry-run is the default (matches reconcile)
    check("retitle (--dry-run default): exits 0",
          r.returncode == 0, f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")
    check("retitle (--dry-run default): previews the pending rename on stdout",
          "DRY-RUN would rename #101" in r.stdout, repr(r.stdout))
    check("retitle (--dry-run default): performs ZERO write calls -- not merely exit 0",
          not rename_calls(log) and not mutation_calls(log), repr(log))

# ---------------- retitle case 6: an unknown --repo -- exits 2, no gh call at all -----------

with tempfile.TemporaryDirectory() as base:
    root = os.path.join(base, "root")
    write_root(root, default_github(),
               fleet={"workspace_root": os.path.join(base, "ws"),
                      "repos": [{"name": "acme/other", "default_branch": "main"}]})
    r, log = run(root, ["retitle", "--repo", "acme/unknown-repo"])
    check("retitle unknown --repo: exits 2, naming the repo, with no gh call at all",
          r.returncode == 2 and not log and "acme/unknown-repo" in r.stderr,
          f"rc={r.returncode} stderr={r.stderr!r} log={log}")

print(f"\n{len(FAILURES)} failing." if FAILURES else "\nall checks passed.")
sys.exit(1 if FAILURES else 0)
