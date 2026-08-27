#!/usr/bin/env python3
"""board_lifecycle.py provision must get these right — offline, against a fake gh (FEAT-33 T-04).

Modeled on test-board-station.py's shape (same `check()` convention) but board_lifecycle.py
resolves its root via `harness_boundary.resolve_root()` (HARNESS_PROJECT_DIR + the
team-config.yaml MARKER), never board-station.py's own team-config.yaml walk-up, so the fixture
writes that marker instead.

THE FAKE-BINARY TRAP (D-11): every case sets BOTH FACTORY_GH and GH_SYNC_GH to the SAME fake, even
though board_lifecycle.py itself only imports factory_gh — a future refactor routing some call
through gh-sync's own wrapper must not silently reach the real `gh`.

    ./test-board-lifecycle.py    -> exit 0 all pass, 1 otherwise
"""
import base64
import json
import os
import stat
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "board_lifecycle.py")
sys.path.insert(0, HERE)
import harness_boundary  # noqa: E402 -- only to read the MARKER path, never imported twice

FAILURES = []


def check(name, cond, detail=""):
    if cond:
        print(f"PASS  {name}")
    else:
        print(f"FAIL  {name}{(' — ' + detail) if detail else ''}")
        FAILURES.append(name)


def write_root(root, github, fleet=None):
    """A temp root carrying the team-config.yaml MARKER harness_boundary.resolve_root() needs,
    plus harness.json's github block. `fleet` (dict or None) writes .harness/factory/fleet.yaml
    only when given -- most cases never touch a fleet at all, mirroring
    test-factory-integration.py's own make_root, which never carries fleet.yaml unless a case
    needs it."""
    os.makedirs(os.path.join(root, os.path.dirname(harness_boundary.MARKER)), exist_ok=True)
    with open(os.path.join(root, harness_boundary.MARKER), "w", encoding="utf-8") as f:
        f.write("teams: []\n")
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
# Fix cycle c4, finding 1: MALFORMED_MATCH makes a call SUCCEED (exit 0) with a body that is not
# JSON. That is the real shape behind the defect -- `factory_gh.run_gh`'s bare
# `json.loads(r.stdout)` (factory_gh.py:170) then raises ValueError, which is NOT a GhError and
# so escaped the GhError-only catches in the post-create blocks straight to `factory_cli.run`'s
# `except BaseException`, exiting 2 ("nothing was written") on a board that had just been
# created and linked. FAIL_MATCH cannot express this: a nonzero exit produces a GhError, the
# class that was already handled.
if [ -n "$MALFORMED_MATCH" ]; then
  case "$*" in
    *"$MALFORMED_MATCH"*)
      echo 'this is not json'
      exit 0 ;;
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
  *"repositories(first:"*)
    # Fix cycle c1, MUST-FIX 1: board_lifecycle._project_linked_repos's own linkage-guard query
    # -- a unique marker ("repositories(first:") no other query in this fixture sends, matched
    # BEFORE the generic "repositoryOwner(login: \$owner)" catch-all below so it never falls
    # through to that branch's RESOLVE_JSON answer.
    echo "$LINKED_REPOS_JSON"
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
  *"/contents/"*)
    # #783's regression guard: factory_config.product_config -> factory_gh.file_at_ref, the
    # remote read of a FLEET MEMBER's own .harness/harness.json (never a directory in this
    # checkout). CONTENTS_B64 is the pre-computed --jq .content answer (real gh applies that
    # filter itself, so the fake must emit the already-extracted field, matching
    # test-factory-integration.py's own fake gh at this same endpoint).
    echo "$CONTENTS_B64"
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


def _linked_repos_json(names, has_next_page=False, end_cursor=None):
    """Fix cycle c1, MUST-FIX 1: the fixture for `_project_linked_repos`'s own query --
    `names` is the project's linked-repository connection, ordered."""
    return json.dumps({"data": {"repositoryOwner": {"__typename": "User", "projectV2": {
        "repositories": {
            "nodes": [{"nameWithOwner": n} for n in names],
            "pageInfo": {"hasNextPage": has_next_page, "endCursor": end_cursor},
        }}}}})


# The default answer every case NOT exercising the linkage guard itself relies on: the fixture's
# own default repo ("acme/widget") IS linked, so every pre-existing provision case (which never
# set this env var before this fix) keeps passing unchanged.
_LINKED_REPOS_DEFAULT = _linked_repos_json(["acme/widget"])
_LINKED_REPOS_UNLINKED = _linked_repos_json(["acme/other-widget"])

_PROBE_ABSENT = json.dumps(
    {"data": {"repositoryOwner": {"__typename": "User",
                                   "projectV2": {"id": "PVT_PROJ", "field": None}}}})
_PROBE_SINGLE_SELECT = json.dumps(
    {"data": {"repositoryOwner": {"__typename": "User", "projectV2": {
        "id": "PVT_PROJ",
        "field": {"__typename": "ProjectV2SingleSelectField", "id": "FIELD_STATUS"}}}}})
# Fix cycle c3, MEASURED 2026-08-23 on project 7 (owner mruangutai): a brand-new Projects v2
# project ALREADY carries a `Status` single-select. This is the probe answer the CREATE branch
# really gets from GitHub -- `_PROBE_ABSENT` is the fresh-board shape only for a declaration
# whose `station_field` is not `Status`.
_PROBE_FRESH_DEFAULT_STATUS = json.dumps(
    {"data": {"repositoryOwner": {"__typename": "User", "projectV2": {
        "id": "PVT_NEW",
        "field": {"__typename": "ProjectV2SingleSelectField",
                   "id": "FIELD_STATUS_DEFAULT"}}}}})
# The option set GitHub ships on that default field, in the order the API returns it.
_GITHUB_DEFAULT_OPTIONS = ["Todo", "In Progress", "Done"]

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


def _served_board_contents_b64(board):
    """Base64 of the SERVED repo's own remote `.harness/harness.json` `.content` field --
    board_lifecycle.py never reads a served repo's board from disk (T-04's BOARD RESOLUTION,
    factory_config.product_config), so a cross-repo case (#783) that resolves a fleet member's
    board must feed the fake gh this, not a `stations`/`options` local fixture."""
    doc = {"schema_version": 1, "github": {"board": board}}
    return base64.b64encode(json.dumps(doc).encode("utf-8")).decode("ascii")


def _stub_env(root, resolve=_RESOLVE_EXISTS, probe=_PROBE_SINGLE_SELECT,
              options=None, issues=None, stations=None, workflows=None, fail_match=None,
              item_id=None, fake_state=None, issues_after=None, stations_after=None,
              workflows_after=None, contents_b64=None, linked_repos=None, malformed_match=None):
    """The stub environment `run` forks with, built once so a SECOND entry point can reuse it.

    Extracted for T-04: `audit_findings` is a library function, so its contract -- what it
    RETURNS, and that it prints NOTHING -- cannot be asserted through a subcommand's stdout.
    `run_module` forks a `python -c` against this same environment instead. Nothing about
    `run`'s behaviour changes; it calls this and adds the argv."""
    tmp = os.path.dirname(root) if os.path.basename(root) == "root" else root
    gh_path = install_gh(tmp)
    log_path = os.path.join(tmp, "calls.log")
    env = dict(os.environ)
    env["HARNESS_PROJECT_DIR"] = root
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
    env["MALFORMED_MATCH"] = malformed_match or ""
    env["ITEM_ID"] = item_id or "ITEM_FAKE"
    env["FAKE_STATE"] = fake_state or os.path.join(tmp, "fake-state-absent-by-default")
    env["ISSUES_JSON_AFTER"] = issues_after or ""
    env["STATIONS_JSON_AFTER"] = stations_after or ""
    env["WORKFLOWS_JSON_AFTER"] = workflows_after or ""
    env["CONTENTS_B64"] = contents_b64 or ""
    env["LINKED_REPOS_JSON"] = linked_repos if linked_repos is not None else _LINKED_REPOS_DEFAULT
    env.pop("HARNESS_GH_COST_LOG", None)
    return env, tmp, log_path


def _log_lines(log_path):
    if not os.path.isfile(log_path):
        return []
    with open(log_path) as f:
        return [l for l in f.read().splitlines() if l]


def run(root, args, cwd=None, **kw):
    """Fork the real script. Returns (CompletedProcess, log_lines)."""
    env, tmp, log_path = _stub_env(root, **kw)
    r = subprocess.run(
        [sys.executable, SCRIPT] + args,
        capture_output=True, text=True, env=env, cwd=cwd or tmp,
    )
    return r, _log_lines(log_path)


def run_module(root, code, cwd=None, **kw):
    """Fork `python -c <code>` against the same stub environment, with board_lifecycle
    importable. Returns (CompletedProcess, log_lines).

    This is how the `audit_findings` contract is asserted: the function must RETURN the
    finding list and PRINT NOTHING, and neither claim is visible through `cmd_audit`'s
    stdout -- which prints. The forked process imports the module directly, so anything the
    function writes to stdout lands in `r.stdout` and fails the absence assertion."""
    env, tmp, log_path = _stub_env(root, **kw)
    env["PYTHONPATH"] = os.path.dirname(SCRIPT) + os.pathsep + env.get("PYTHONPATH", "")
    r = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, env=env, cwd=cwd or tmp,
    )
    return r, _log_lines(log_path)


def mutation_calls(log):
    """Every logged call that carries a WRITE mutation -- never a read query. Used to assert
    "zero mutations" precisely, rather than "the log is empty" (a read that never happened would
    pass that too, for the wrong reason)."""
    markers = ("createProjectV2Field", "updateProjectV2Field", "linkProjectV2ToRepository",
               "createProjectV2(", "project\x01item-edit", "label\x01create", "issue\x01edit",
               "state_reason=")
    return [l for l in log if any(m in l for m in markers)]


def number_arg(line):
    """The `-F number=<N>` value the fake gh was REALLY called with on one logged call.

    Fix cycle c4, finding 2. FAKE_GH_SRC's first line has always logged the full argv, so the
    number argument was recorded all along -- what was missing was any assertion that READ it.
    The fake DISPATCHES on query text alone, so which project number a read is sent for changes
    no fixture answer: swapping `created["number"]` for the declared `number` in
    `_fresh_board_station_field` left the whole suite green while breaking every live fresh
    provision at exit 4, because the declared number is precisely the one that did not resolve.
    `number=` is unambiguous in the log -- the GraphQL bodies spell it `number: $number`, and
    only the `-F` flag uses `=`. Returns None unless exactly one such token is present, so an
    ambiguous line fails the assertion rather than silently picking one."""
    hits = [t.split("=", 1)[1] for t in line.split("\x01") if t.startswith("number=")]
    return hits[0] if len(hits) == 1 else None


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

# ---------------- case 5: no project, field ABSENT -- creates, links, creates it, exits 3 -
# Fix cycle c3: this case now pins `probe=_PROBE_ABSENT` explicitly. An absent field on a
# just-created project is reachable only for a declaration whose `station_field` is NOT `Status`
# (a real fresh board ships a default `Status` -- see case 5d), so the create branch is the
# absent-field branch and the fixture must say so rather than inherit the default.
# Fix cycle c2 (SC-01): the Status field is created in the SAME run as the project. It used to
# take a SECOND run (the operator had to write the new number into harness.json first), and the
# assertion below used to read "never calls createProjectV2Field or updateProjectV2Field" --
# asserting the defect. createProjectV2Field is now REQUIRED here; updateProjectV2Field is still
# forbidden (extend can never run on a board whose field was just created with all six).

def _expected_options_literal(names):
    """The EXACT `singleSelectOptions` GraphQL literal factory_gh._options_literal renders,
    re-authored here on purpose (never imported) so the assertion is a byte-for-byte
    specification of what goes over the wire (SC-01), not a tautology against the renderer.
    chr(1) is FAKE_LOG's own space substitution -- see FAKE_GH_SRC's header comment."""
    parts = ['{name: "%s", color: GRAY, description: ""}' % n for n in names]
    return ("[" + ", ".join(parts) + "]").replace(" ", "\x01")


with tempfile.TemporaryDirectory() as base:
    root = os.path.join(base, "root")
    write_root(root, default_github())
    r, log = run(root, ["provision"], resolve=_RESOLVE_ABSENT, probe=_PROBE_ABSENT)
    field_calls = [l for l in log if "createProjectV2Field" in l]
    check("no project: exits 3",
          r.returncode == 3, f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")
    check("no project: creates the project and links the repository",
          any("createProjectV2(" in l and "createProjectV2Field" not in l for l in log)
          and any("linkProjectV2ToRepository" in l for l in log),
          repr(log))
    check("no project: reports the new project number",
          "42" in r.stdout, repr(r.stdout))
    check("SC-01: no project: createProjectV2Field is called exactly ONCE in the SAME run -- "
          "the field never waits for a second run",
          len(field_calls) == 1, f"rc={r.returncode} log={log}")
    check("SC-01: no project: the field is created ON THE NEWLY CREATED project "
          "(projectId=PVT_NEW, the id createProjectV2 returned) and is named Status",
          field_calls
          and "projectId=PVT_NEW" in field_calls[0]
          and "name=Status" in field_calls[0],
          repr(field_calls))
    check("SC-01: no project: all six declared station names go over the wire BYTE FOR BYTE, "
          "in declared order, in the singleSelectOptions literal",
          field_calls and _expected_options_literal(_ALL_SIX) in field_calls[0],
          f"expected={_expected_options_literal(_ALL_SIX)!r} calls={field_calls!r}")
    check("no project: still exits 3 AFTER the field creation -- the operator must record the "
          "new number, and 3 is that signal (its meaning is unchanged)",
          r.returncode == 3 and len(field_calls) == 1,
          f"rc={r.returncode} log={log}")
    check("no project: updateProjectV2Field is STILL never called -- extend must never run on a "
          "board whose field was just created with all six options",
          not any("updateProjectV2Field" in l for l in log),
          repr(log))
    check("no project: reports the field it created on stdout",
          "created field 'Status'" in r.stdout, repr(r.stdout))
    # Fix cycle c4, finding 2, on the field-ABSENT create branch as well.
    probe_calls = [l for l in log if "ProjectV2IterationField" in l]
    check("c4: the probe on the field-absent create branch is sent for the CREATED number (42), "
          "never the DECLARED 9",
          len(probe_calls) == 1 and number_arg(probe_calls[0]) == "42",
          f"probe_calls={probe_calls!r}")

# ---------------- case 5c (fix cycle c2, SC-01): create + link succeed, the FIELD creation
# fails -- exit 4, and stderr names the created number so a retry cannot duplicate the board ---
# Same reasoning as case 5b: a write landed (the project exists and is linked), so the code must
# be 4, never 2 ("nothing mutated") and never 3 ("clean success"). FAIL_MATCH is scoped to
# createProjectV2Field, which no other call in this branch carries.

with tempfile.TemporaryDirectory() as base:
    root = os.path.join(base, "root")
    write_root(root, default_github())
    r, log = run(root, ["provision"], resolve=_RESOLVE_ABSENT, probe=_PROBE_ABSENT,
                 fail_match="createProjectV2Field")
    check("SC-01: field-create failure after a successful create+link exits 4, never 2 or 3",
          r.returncode == 4, f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")
    check("SC-01: the field-create failure names the CREATED project's number on stderr -- a "
          "retry that cannot see it would create a second board",
          "42" in r.stderr, repr(r.stderr))
    check("SC-01: the field-create failure names the field it failed to create",
          "Status" in r.stderr, repr(r.stderr))
    check("SC-01: create and link really did happen before the field failure",
          any("createProjectV2(" in l and "createProjectV2Field" not in l for l in log)
          and any("linkProjectV2ToRepository" in l for l in log),
          repr(log))
    check("SC-01: the field-create was actually attempted (the failure is a real call's, not a "
          "gap in the branch)",
          any("createProjectV2Field" in l for l in log), repr(log))

# ---------------- case 5d (fix cycle c3): a REAL fresh board -- the default Status field is
# already there, and provision sets it to EXACTLY the declared six -------------------------
# The finding c3 fixes: c2 assumed a just-created project cannot already carry `Status`, and a
# live run (2026-08-23, project 7 on mruangutai) proved otherwise -- createProjectV2Field failed
# with "Name has already been taken" and provision exited 4 on a board it had just created. The
# operator's ruling: on a project THIS SAME RUN created, replace the option set with exactly the
# declared stations, deleting GitHub's Todo and In Progress. Safe there and only there -- a
# brand-new board holds no items, so no card can lose its column.

with tempfile.TemporaryDirectory() as base:
    root = os.path.join(base, "root")
    write_root(root, default_github())
    r, log = run(root, ["provision"], resolve=_RESOLVE_ABSENT,
                 probe=_PROBE_FRESH_DEFAULT_STATUS,
                 options=_options_json(_GITHUB_DEFAULT_OPTIONS))
    extend_calls = [l for l in log if "updateProjectV2Field" in l]
    check("c3: fresh board whose Status field ALREADY EXISTS as single-select: still exits 3 -- "
          "the operator must record the new number, and 3 is that signal",
          r.returncode == 3, f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")
    check("c3: fresh board with a pre-existing Status: updateProjectV2Field is called EXACTLY "
          "once",
          len(extend_calls) == 1, f"rc={r.returncode} log={log}")
    check("c3: fresh board with a pre-existing Status: createProjectV2Field is NEVER called -- "
          "that is the call the real API rejected with 'Name has already been taken'",
          not any("createProjectV2Field" in l for l in log), repr(log))
    check("c3: the option list sent over the wire is EXACTLY the six declared, in declared "
          "order, BYTE FOR BYTE -- nothing appended, nothing preserved from GitHub's default",
          extend_calls and _expected_options_literal(_ALL_SIX) in extend_calls[0],
          f"expected={_expected_options_literal(_ALL_SIX)!r} calls={extend_calls!r}")
    check("c3: the exact replace targets the DEFAULT field's id, the one _field_probe read off "
          "the just-created project",
          extend_calls and "fieldId=FIELD_STATUS_DEFAULT" in extend_calls[0],
          repr(extend_calls))
    check("c3: GitHub's undeclared defaults are GONE from the payload -- Todo and In Progress "
          "appear in NO argv the fake received",
          not any("Todo" in l or "In\x01Progress" in l for l in log), repr(log))
    check("c3: stdout names the options it REMOVED, so the operator sees Todo and In Progress "
          "went",
          "Todo" in r.stdout and "In Progress" in r.stdout and "REMOVED" in r.stdout,
          repr(r.stdout))
    # Fix cycle c4, finding 2: WHICH project number the two reads were sent for. The declaration
    # says 9 (`_BOARD["number"]`) and it did not resolve -- that is why this branch is running --
    # so every read here must carry the CREATED 42. Nothing asserted this before, and the fake
    # answers by query text alone, so `created["number"]` -> `number` was a silent mutant.
    probe_calls = [l for l in log if "ProjectV2IterationField" in l]
    options_calls = [l for l in log if "options\x01{\x01id\x01name\x01}" in l]
    check("c4: the fresh-board probe is sent for the CREATED project number (42), never the "
          "DECLARED 9 -- the declared number is the one that did not resolve",
          len(probe_calls) == 1 and number_arg(probe_calls[0]) == "42",
          f"probe_calls={probe_calls!r}")
    check("c4: the fresh-board options read is sent for the CREATED number (42) too -- reading "
          "the declared board's options would compute the removal set off the WRONG project",
          len(options_calls) == 1 and number_arg(options_calls[0]) == "42",
          f"options_calls={options_calls!r}")

# ---------------- case 5e (fix cycle c3): the exact replace FAILS on a fresh board -- exit 4,
# stderr names the created number ----------------------------------------------------------
# Same reasoning as 5b and 5c: a write landed (the project exists and is linked), so the code is
# 4, never 2 ("nothing mutated") and never 3 ("clean success").

with tempfile.TemporaryDirectory() as base:
    root = os.path.join(base, "root")
    write_root(root, default_github())
    r, log = run(root, ["provision"], resolve=_RESOLVE_ABSENT,
                 probe=_PROBE_FRESH_DEFAULT_STATUS,
                 options=_options_json(_GITHUB_DEFAULT_OPTIONS),
                 fail_match="updateProjectV2Field")
    check("c3: an extend failure on a just-created board exits 4, never 2 or 3",
          r.returncode == 4, f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")
    check("c3: the extend failure names the CREATED project's number on stderr -- a retry that "
          "cannot see it would create a second board",
          "42" in r.stderr, repr(r.stderr))
    check("c3: the extend failure names the field it could not set",
          "Status" in r.stderr, repr(r.stderr))
    check("c3: the extend really was attempted (the failure is a real call's, not a gap)",
          any("updateProjectV2Field" in l for l in log), repr(log))

# ---------------- case 5f (fix cycle c3): a fresh board whose field is NOT single-select ---
# Unreachable against today's API -- GitHub's default `Status` IS a single-select -- but the API
# is not promised to stay still, and c2's own falsified comment is why this branch exists rather
# than an assumption. A project was created, so it is exit 4, not the resolved path's exit 2.

with tempfile.TemporaryDirectory() as base:
    root = os.path.join(base, "root")
    write_root(root, default_github())
    r, log = run(root, ["provision"], resolve=_RESOLVE_ABSENT, probe=_PROBE_TEXT_FIELD)
    check("c3: a fresh board whose field is not single-select exits 4 (a project WAS created), "
          "never 2",
          r.returncode == 4, f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")
    check("c3: that refusal names the created number and the type it found",
          "42" in r.stderr and "ProjectV2Field" in r.stderr, repr(r.stderr))
    check("c3: it converts nothing -- no field mutation of any kind reached the fake",
          not any("createProjectV2Field" in l or "updateProjectV2Field" in l for l in log),
          repr(log))

# ---------------- cases 5h/5i (fix cycle c4, finding 1): a NON-GhError failure after a
# successful create+link is exit 4, never exit 2 ---------------------------------------------
# The defect: both post-create blocks caught `factory_gh.GhError` only. `run_gh`'s bare
# `json.loads(r.stdout)` raises ValueError on a body gh returned with exit 0, and
# `_project_field_resolve`'s unguarded subscripts raise KeyError/TypeError -- none of them a
# GhError, so each reached `factory_cli.run`'s `except BaseException` and exited EXIT_REFUSED = 2.
# 2 is documented as "nothing was written". A project has been created and linked by then, so an
# operator or script that reads 2 as "nothing happened" retries, re-enters the create branch and
# gets a SECOND board -- the exact disaster the exit-code contract exists to prevent. These two
# cases pin the FIELD work and the LINK call, the two blocks that were broadened.

with tempfile.TemporaryDirectory() as base:
    root = os.path.join(base, "root")
    write_root(root, default_github())
    r, log = run(root, ["provision"], resolve=_RESOLVE_ABSENT,
                 probe=_PROBE_FRESH_DEFAULT_STATUS,
                 options=_options_json(_GITHUB_DEFAULT_OPTIONS),
                 malformed_match="ProjectV2IterationField")
    check("c4: a NON-GhError (ValueError from run_gh's json.loads) in the field work after a "
          "successful create+link exits 4, NEVER 2 -- 2 would claim nothing was written",
          r.returncode == 4, f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")
    check("c4: that unexpected failure still names the CREATED project's number on stderr -- a "
          "retry that cannot see 42 re-enters the create branch and duplicates the board",
          "42" in r.stderr, repr(r.stderr))
    check("c4: it says plainly that the failure was UNEXPECTED and names the exception class, "
          "rather than dressing a ValueError up as a gh error",
          "UNEXPECTED" in r.stderr and "JSONDecodeError" in r.stderr, repr(r.stderr))
    check("c4: it still tells the operator to record the number now",
          "record 42" in r.stderr, repr(r.stderr))
    check("c4: create and link really did land before the unexpected failure",
          any("createProjectV2(" in l and "createProjectV2Field" not in l for l in log)
          and any("linkProjectV2ToRepository" in l for l in log), repr(log))

with tempfile.TemporaryDirectory() as base:
    root = os.path.join(base, "root")
    write_root(root, default_github())
    r, log = run(root, ["provision"], resolve=_RESOLVE_ABSENT, probe=_PROBE_ABSENT,
                 malformed_match="linkProjectV2ToRepository")
    check("c4: a NON-GhError in the LINK call after a successful create exits 4, never 2 -- the "
          "same hole lived in that block too",
          r.returncode == 4, f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")
    check("c4: the link's unexpected failure names the created number and the exception class",
          "42" in r.stderr and "unexpected" in r.stderr and "JSONDecodeError" in r.stderr,
          repr(r.stderr))
    check("c4: no field work was attempted after the link failed",
          not any("createProjectV2Field" in l or "updateProjectV2Field" in l for l in log),
          repr(log))

# ---------------- case 5g (fix cycle c3) REGRESSION GUARD: the EXISTING-board path still sends
# existing + missing, and can never send a bare `declared` -----------------------------------
# The disaster the exact replace above must never reach: an established board carries columns the
# declaration does not name (here `Icebox`), and updateProjectV2Field REPLACES the option set, so
# a bare `declared` there DELETES the operator's column. Case 2's fixture cannot catch that --
# every option it holds is also declared, so union and bare-declared render identically.

with tempfile.TemporaryDirectory() as base:
    root = os.path.join(base, "root")
    write_root(root, default_github())
    existing = ["Backlog", "Icebox", "Plan", "Ready"]
    r, log = run(root, ["provision"], options=_options_json(existing))
    extend_calls = [l for l in log if "updateProjectV2Field" in l]
    check("c3 regression: an EXISTING board with an undeclared column still exits 0 and extends "
          "exactly once",
          r.returncode == 0 and len(extend_calls) == 1,
          f"rc={r.returncode} stdout={r.stdout!r} log={log}")
    check("c3 regression: the payload is BYTE FOR BYTE existing + missing -- the undeclared "
          "Icebox survives, in its existing position",
          extend_calls
          and _expected_options_literal(existing + ["Building", "Review", "Done"])
          in extend_calls[0],
          f"expected={_expected_options_literal(existing + ['Building', 'Review', 'Done'])!r} "
          f"calls={extend_calls!r}")
    check("c3 regression: the payload is NEVER the bare declared six -- that is the "
          "column-deletion disaster, and no existing-board path may reach it",
          extend_calls and _expected_options_literal(_ALL_SIX) not in extend_calls[0],
          repr(extend_calls))
    check("c3 regression: Icebox is still in the argv the fake received -- the operator's "
          "column was not deleted",
          any("Icebox" in l for l in log), repr(log))

# ---------------- case 5b (fix cycle c1, MUST-FIX 2): create succeeds, link fails -- honest
# partial-success reporting, no duplicate-board risk on retry -------------------------------
# `resolved is None` (no project) forces the create-then-link branch; forcing
# `linkProjectV2ToRepository` itself to fail proves the project's number reaches stdout BEFORE
# the failure, and that the exit code is neither 2 (this module's OWN "nothing mutated" code)
# nor 3 (the clean-success race code) -- both would misreport a run that DID create a project.

with tempfile.TemporaryDirectory() as base:
    root = os.path.join(base, "root")
    write_root(root, default_github())
    r, log = run(root, ["provision"], resolve=_RESOLVE_ABSENT,
                 fail_match="linkProjectV2ToRepository")
    check("MUST-FIX 2: create-then-link failure exits 4, never 2 (this module's own "
          "'nothing mutated' code) or 3 (the clean-success race code) -- this run DID create "
          "a real project",
          r.returncode == 4, f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")
    check("MUST-FIX 2: the created project's number reaches stdout BEFORE the link failure -- "
          "a retry must be able to see it and record it rather than create a duplicate",
          "created project 42" in r.stdout, repr(r.stdout))
    check("MUST-FIX 2: createProjectV2( was actually called -- the project really was created, "
          "so 'nothing mutated' would be false",
          any("createProjectV2(" in l and "createProjectV2Field" not in l for l in log),
          repr(log))
    check("MUST-FIX 2: the stderr failure names the created project's number and the repo it "
          "failed to link",
          "42" in r.stderr and "acme/widget" in r.stderr, repr(r.stderr))

# ---------------- case 8 (fix cycle c1, MUST-FIX 1): the linkage guard -- a resolved project
# NOT linked to the served repo refuses, zero mutations, before either field-schema branch ----
# Reuses case 2's missing-options fixture (which otherwise reaches the mutating "extend" branch)
# so "zero mutations" is not a vacuous assertion of a run that would have done nothing anyway.

with tempfile.TemporaryDirectory() as base:
    root = os.path.join(base, "root")
    write_root(root, default_github())
    existing = ["Backlog", "Plan", "Ready", "Building"]
    r, log = run(root, ["provision"], options=_options_json(existing),
                 linked_repos=_LINKED_REPOS_UNLINKED)
    check("linkage guard (MUST-FIX 1): refuses exit 2 when the resolved project is not linked "
          "to the served repo",
          r.returncode == 2, f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")
    check("linkage guard: performs ZERO mutations -- the confused-deputy write never reaches "
          "the fake",
          not mutation_calls(log), repr(log))
    check("linkage guard: the refusal names the project (owner and number), the repo, and why",
          "9" in r.stderr and "acme" in r.stderr and "acme/widget" in r.stderr
          and "not linked" in r.stderr, repr(r.stderr))

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

# ---------------- audit case 8b: #783 regression guard -- STATUS must not compare THIS
# checkout's own on-disk features against a DIFFERENT repo's board. `--repo` names a fleet
# member (never this checkout's own repo); its board is resolved REMOTELY
# (factory_config.product_config), so this checkout's own `.harness/widget/features/*` are
# NEVER that repo's features. Before the fix this fixture produced a false STATUS finding
# (own-repo feature.json, status Done, compared against the SERVED repo's #950 reading
# Backlog) -- reddened against the pre-fix code (see the receipt's RED proof). After the fix,
# STATUS self-skips for any --repo but this checkout's own, so this is exit 0, zero STATUS.

_SERVED_BOARD = {
    "owner": "acme", "number": 42, "station_field": "Status",
    "stations": _BOARD["stations"],
}

with tempfile.TemporaryDirectory() as base:
    root = os.path.join(base, "root")
    write_root(root, default_github(),
               fleet={"workspace_root": os.path.join(base, "ws"),
                      "repos": [{"name": "acme/gadget", "default_branch": "main"}]})
    # This checkout's OWN feature, on disk, status Done -- would mismatch the served repo's
    # #950 reading Backlog if STATUS wrongly compared across repos.
    write_feature(root, "widget", "FEAT-CROSSREPO-783", "Done", parent=950,
                  github_issues={"T-01": 951})
    r, log = run(
        root, ["audit", "--repo", "acme/gadget"],
        stations=_stations_json({950: "Backlog"}, repo="acme/gadget"),
        contents_b64=_served_board_contents_b64(_SERVED_BOARD),
    )
    check("audit #783: cross-repo audit exits 0 -- STATUS never fires for a repo that is not "
          "this checkout's own", r.returncode == 0, f"rc={r.returncode} stdout={r.stdout!r}")
    check("audit #783: no STATUS finding at all -- only the skip line, never a "
          "'records status' finding",
          "records status" not in r.stdout, repr(r.stdout))
    check("audit #783: STATUS reports itself skipped, naming both repos, rather than silently "
          "omitting the class",
          "STATUS" in r.stdout and "skipped" in r.stdout
          and "acme/gadget" in r.stdout and "acme/widget" in r.stdout, repr(r.stdout))

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

# ---------------- reconcile case 6b: #783 regression guard -- reconcile shares audit's
# STATUS scoping, since both run `_audit_findings`. A "Building" (non-Done, otherwise
# FIXABLE) status mismatch would, before the fix, be previewed as a real fix reconcile could
# --apply against the SERVED repo's card -- computed from THIS checkout's own, unrelated
# feature.json. Dry-run only (no --apply): the preview text alone is the discriminator, so
# this stays a read even against the pre-fix code.

with tempfile.TemporaryDirectory() as base:
    root = os.path.join(base, "root")
    write_root(root, default_github(),
               fleet={"workspace_root": os.path.join(base, "ws"),
                      "repos": [{"name": "acme/gadget", "default_branch": "main"}]})
    write_feature(root, "widget", "FEAT-CROSSREPO-RECON-783", "Building", parent=960,
                  github_issues={"T-01": 961})
    r, log = run(
        root, ["reconcile", "--repo", "acme/gadget"],
        stations=_stations_json({960: "Ready"}, repo="acme/gadget"),
        contents_b64=_served_board_contents_b64(_SERVED_BOARD),
    )
    check("reconcile #783: cross-repo dry-run exits 0 with zero fixable findings previewed "
          "-- STATUS never fires for a repo that is not this checkout's own",
          r.returncode == 0 and "0 fixable finding(s) previewed" in r.stdout,
          f"rc={r.returncode} stdout={r.stdout!r}")
    check("reconcile #783: never previews a write against issue #960",
          "#960" not in r.stdout, repr(r.stdout))
    check("reconcile #783: performs zero mutations -- dry-run never writes regardless",
          not mutation_calls(log), repr(log))

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

# ---------------- retitle case 2b (fix cycle c1, MUST-FIX 3): a per-ticket GhError does not
# stop the bulk backfill -- the module docstring's own claim ("caught explicitly here exactly
# as audit and reconcile catch it") is what this proves true, not merely asserts.

with tempfile.TemporaryDirectory() as base:
    root = os.path.join(base, "root")
    write_root(root, default_github())
    issues = json.dumps([
        {"number": 401, "title": "T-1 — first ticket", "milestone": {"title": "FEAT-A"}},
        {"number": 402, "title": "T-2 — second ticket", "milestone": {"title": "FEAT-B"}},
    ])
    r, log = run(root, ["retitle", "--apply"], issues=issues, fail_match="401")
    rc = rename_calls(log)
    check("MUST-FIX 3: ticket #401's rename was attempted and failed, but the run continues "
          "-- ticket #402 is still renamed rather than the run stopping at #401",
          any("402" in l for l in rc), repr(log))
    check("MUST-FIX 3: ticket #401's failure is reported on stderr, per-ticket",
          "401" in r.stderr, repr(r.stderr))
    check("MUST-FIX 3: exits 1 -- a partial failure must be signalled honestly, never exit 2's "
          "caller/declaration meaning and never a silent exit 0",
          r.returncode == 1, f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")
    check("MUST-FIX 3: the summary reports both the renamed and the failed count",
          "renamed: 1" in r.stdout and "failed: 1" in r.stdout, repr(r.stdout))

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

# ---------------- T-04: audit_findings -- the LIBRARY entry point ship calls ---------------
# `gh-sync.py ship` runs the audit once per feature as REQ-06's compensating control, so the
# audit has to be callable as a function. The contract is three clauses, and each is a clause
# `cmd_audit` breaks today: it PRINTS (the workflow header, the STATUS skip line, the no-board
# line), and it EXITS (factory_cli.refuse, and sys.exit(4) on a GhError). A caller inside ship
# can tolerate none of that -- ship must never exit on the audit, and ship prefixes every audit
# line with its own literal, so a line printed from inside board_lifecycle would appear
# unprefixed and unfindable.

_AF_RETURNS = (
    "import json, board_lifecycle as bl;"
    "fs = bl.audit_findings(%r);"
    "print('RESULT=' + json.dumps([f.message for f in fs]))"
)

# --- clause 1: it returns the findings cmd_audit prints, and prints NOTHING itself ---------

with tempfile.TemporaryDirectory() as base:
    root = os.path.join(base, "root")
    write_root(root, default_github())
    issues = json.dumps([{"number": 10, "stateReason": "COMPLETED", "labels": []}])
    stations = _stations_json({10: "Building"})

    r_cmd, _ = run(root, ["audit"], issues=issues, stations=stations)
    r_fn, _ = run_module(root, _AF_RETURNS % None, issues=issues, stations=stations)

    got = ""
    for line in r_fn.stdout.splitlines():
        if line.startswith("RESULT="):
            got = line[len("RESULT="):]
    messages = json.loads(got) if got else None

    check("audit_findings: returns the same STATION finding cmd_audit prints",
          messages is not None and any("STATION: issue #10" in m for m in messages),
          f"stdout={r_fn.stdout!r} stderr={r_fn.stderr!r}")
    check("audit_findings: returns a LIST, not an exit code -- the caller decides what to do",
          isinstance(messages, list), repr(messages))
    check("audit_findings: prints NOTHING -- no workflow header",
          "workflow detection matches by NAME only" not in r_fn.stdout,
          f"stdout={r_fn.stdout!r}")
    check("audit_findings: prints NOTHING -- no finding line of its own, and no count line",
          "STATION: issue #10" not in r_fn.stdout.replace(got, "")
          and "finding(s)" not in r_fn.stdout,
          f"stdout={r_fn.stdout!r}")
    check("audit_findings: writes nothing to stderr either",
          r_fn.stderr.strip() == "", repr(r_fn.stderr))
    check("audit_findings: cmd_audit's own output is UNCHANGED by the move -- it still prints "
          "the workflow header before its findings",
          "workflow detection matches by NAME only" in r_cmd.stdout
          and r_cmd.stdout.index("workflow detection") < r_cmd.stdout.index("STATION: issue #10"),
          repr(r_cmd.stdout))

# --- clause 2: a failed read RAISES, it never exits ---------------------------------------
# cmd_audit turns this into exit 4. audit_findings must let it propagate, because ship catches
# GhError and continues: an audit that could not run must not stop a ship that already wrote
# every card.

with tempfile.TemporaryDirectory() as base:
    root = os.path.join(base, "root")
    write_root(root, default_github())
    code = (
        "import board_lifecycle as bl, factory_gh;"
        "\ntry:"
        "\n    bl.audit_findings(None)"
        "\n    print('RESULT=no-exception')"
        "\nexcept factory_gh.GhError as e:"
        "\n    print('RESULT=GhError')"
        "\nexcept SystemExit as e:"
        "\n    print('RESULT=SystemExit-' + str(e.code))"
    )
    r_fn, _ = run_module(root, code, fail_match="options { id name }")
    check("audit_findings: a failed read raises GhError -- it never calls sys.exit",
          "RESULT=GhError" in r_fn.stdout,
          f"stdout={r_fn.stdout!r} stderr={r_fn.stderr!r}")

# --- clause 3: no board declared returns [], matching cmd_audit's own branch ---------------

with tempfile.TemporaryDirectory() as base:
    root = os.path.join(base, "root")
    write_root(root, {"sync": True, "repo": "acme/widget", "board": None})
    r_fn, _ = run_module(root, _AF_RETURNS % None)
    check("audit_findings: no board declared returns an EMPTY LIST, not an error",
          "RESULT=[]" in r_fn.stdout, f"stdout={r_fn.stdout!r} stderr={r_fn.stderr!r}")
    check("audit_findings: no board declared prints nothing -- cmd_audit keeps that line",
          "nothing to audit" not in r_fn.stdout, repr(r_fn.stdout))
    r_cmd, _ = run(root, ["audit"])
    check("audit_findings: cmd_audit STILL prints its own no-board line",
          "no board declared" in r_cmd.stdout and r_cmd.returncode == 0,
          f"rc={r_cmd.returncode} stdout={r_cmd.stdout!r}")

# --- clause 4: cmd_audit keeps its refuse when github.repo is not declared -----------------

with tempfile.TemporaryDirectory() as base:
    root = os.path.join(base, "root")
    write_root(root, {"sync": True, "repo": "", "board": _BOARD})
    r_cmd, _ = run(root, ["audit"])
    check("audit_findings: cmd_audit STILL refuses when github.repo is not declared -- the "
          "exit stays inside the subcommand",
          r_cmd.returncode != 0 and "github.repo" in (r_cmd.stderr + r_cmd.stdout),
          f"rc={r_cmd.returncode} stderr={r_cmd.stderr!r} stdout={r_cmd.stdout!r}")

print(f"\n{len(FAILURES)} failing." if FAILURES else "\nall checks passed.")
sys.exit(1 if FAILURES else 0)
