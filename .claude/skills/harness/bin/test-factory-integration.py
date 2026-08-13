#!/usr/bin/env python3
"""test-factory-integration.py — the fork-level exit-status and end-to-end test (T-12).

WHY THIS FILE, AND WHY IT IS THE ONLY ONE THAT FORKS A REAL PROCESS: every other
test-factory-*.py asserts in-process, catching SystemExit — correct for what each covers, and
blind to a tool whose `if __name__ == "__main__":` block forgets to call factory_cli.run, or
that raises at import time. Nothing else in the plan catches that class (T-12 intent, SC-10,
SC-15). It also carries SC-19, the one automated end-to-end journey: decompose -> claim ->
workspace -> land, composed for real via subprocess, each step consuming the previous step's
own JSON payload rather than a constant.

Every case here runs a tool with `subprocess.run([sys.executable, <tool path>, ...])`, a cwd
that is never this checkout, and an explicit env. Nothing here spawns real `gh` or real `git`
except the live-git smoke check at the bottom, which points FACTORY_GIT at the real git binary
against a fully local (bare-repo) fixture — no network, no github.com, no mutation of this
checkout. Every fixture lives under tempfile.TemporaryDirectory.

THE SEAM: FACTORY_GH and FACTORY_GIT are read at call time by factory_gh.py / factory_workspace.py
(never cached at import), so a stub executable at an arbitrary path is honoured. The stub `gh`
here (`_FAKE_GH_SRC`) is a small stateful Python script driven by a JSON state file (env var
GH_STATE) that every case pre-seeds; it implements exactly the gh argv surface factory_gh.py and
gh_issues.py emit — read from those two files directly, not guessed. The stub `git`
(`_FAKE_GIT_OK_SRC`) always exits 0 with empty output; T-06's own real argv forms are unit-tested
by recorder in test-factory-workspace.py, and are exercised for REAL only in the bottom section.

CLAUDE_PROJECT_DIR IS THE ROOT-REDIRECT SEAM, NOT A WORKAROUND: factory_config.harness_root()
documents (and test-factory-config.py exercises) a three-tier resolution — CLAUDE_PROJECT_DIR
wins when `<it>/docs/harness/SPEC.md` is readable. Every case sets CLAUDE_PROJECT_DIR to its own
temp root with a stub SPEC.md, so `factory_claim.py`'s import-time FEATURES_ROOT (a documented,
carried, non-blocking finding — see the receipt) resolves under the temp root instead of this
checkout's real `.harness/features`. This is also why a case's own `.harness/factory/fleet.yaml`
is never created next to the probe — every case passes `--fleet` explicitly and the DEFAULT
FLEET_PATH is left to 404, which is exactly what the "no arguments" and "missing --fleet" cases
need. Every case asserts stderr never contains "IGNORING it" — that phrase means the probe missed
and harness_root() silently fell back to this checkout's own root, which would make the case's
CLAUDE_PROJECT_DIR redirect a no-op without ever failing loudly.

TWO OF THE FIVE TOOLS NEVER CALL gh AT ALL (grep-verified: factory_config.py and
factory_workspace.py import neither factory_gh nor gh_issues), so the SC-10 "bad-auth exits 2"
case is authored only for factory_decompose.py, factory_claim.py and factory_land.py. This is
reported explicitly rather than silently narrowing "every one of the five" from the intent text.
"""
import json
import os
import re
import stat
import subprocess
import sys
import tempfile

import yaml

BIN_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS = {
    "config": os.path.join(BIN_DIR, "factory_config.py"),
    "decompose": os.path.join(BIN_DIR, "factory_decompose.py"),
    "claim": os.path.join(BIN_DIR, "factory_claim.py"),
    "workspace": os.path.join(BIN_DIR, "factory_workspace.py"),
    "land": os.path.join(BIN_DIR, "factory_land.py"),
}

FAILS = 0
RAN = 0


def check(name, cond, detail=""):
    global FAILS, RAN
    RAN += 1
    if cond:
        print(f"ok    {name}")
    else:
        FAILS += 1
        print(f"FAIL  {name}" + (f"\n        {detail}" if detail else ""))


# --------------------------------------------------------------------------
# The stub binaries. Written once per case into that case's own temp dir.
# --------------------------------------------------------------------------

_FAKE_GH_SRC = r'''#!/usr/bin/env python3
"""A stateful fake `gh`, driven by env var GH_STATE (a JSON file) and argv matching against
the exact surface factory_gh.py / gh_issues.py emit. Never touches the network."""
import json
import os
import re
import sys


def main():
    argv = sys.argv[1:]
    # Opt-in call recording, in the exact style FACTORY_GIT_LOG already uses for the fake git:
    # unset for every case except the one that needs it, so no existing case's behaviour changes.
    # Recorded as one JSON array per line (never space-joined) because a graphql call's query=
    # argument embeds real newlines, which would otherwise split one call across several lines.
    call_log_path = os.environ.get("GH_CALL_LOG")
    if call_log_path:
        with open(call_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(argv) + "\n")
    state_path = os.environ["GH_STATE"]
    with open(state_path, encoding="utf-8") as f:
        state = json.load(f)

    def save():
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump(state, f)

    def ok(s=""):
        if s:
            print(s)
        save()
        sys.exit(0)

    def bad(s, code=1):
        print(s, file=sys.stderr)
        save()
        sys.exit(code)

    if argv[:2] == ["auth", "status"]:
        if state.get("auth_fail"):
            bad("gh: not logged in. run 'gh auth login'", 1)
        ok()

    if argv[:2] == ["label", "create"]:
        ok()

    if argv[:2] == ["issue", "create"]:
        repo = argv[argv.index("--repo") + 1]
        title = argv[argv.index("--title") + 1]
        num = state["next_issue"]
        state["next_issue"] = num + 1
        labels = [argv[i + 1] for i, a in enumerate(argv) if a == "--label"]
        state["issues"][str(num)] = {
            "title": title, "state": "OPEN", "labels": labels, "assignees": [],
        }
        ok(f"https://github.com/{repo}/issues/{num}")

    if argv[:2] == ["issue", "view"]:
        num = argv[2]
        issue = state["issues"].get(num, {})
        payload = {
            "number": int(num),
            "title": issue.get("title"),
            "state": issue.get("state", "OPEN"),
            "assignees": [{"login": a} for a in issue.get("assignees", [])],
            "labels": [{"name": l} for l in issue.get("labels", [])],
        }
        ok(json.dumps(payload))

    if argv[:2] == ["issue", "edit"]:
        num = argv[2]
        rec = state["issues"].setdefault(
            num, {"title": None, "state": "OPEN", "labels": [], "assignees": []}
        )
        if "--add-label" in argv:
            rec["labels"].append(argv[argv.index("--add-label") + 1])
        if "--add-assignee" in argv:
            rec["assignees"].append(argv[argv.index("--add-assignee") + 1])
        ok()

    if argv[:2] == ["project", "item-add"]:
        url = argv[argv.index("--url") + 1]
        parts = url.rstrip("/").split("/")
        num = parts[-1]
        repo = f"{parts[-4]}/{parts[-3]}"
        item_id = f"ITEM{state['next_item']}"
        state["next_item"] += 1
        state["items"][item_id] = {"number": int(num), "repo": repo, "station": None}
        ok(json.dumps({"id": item_id}))

    if argv[:2] == ["project", "item-list"]:
        query = argv[argv.index("--query") + 1] if "--query" in argv else ""
        m = re.search(r':"([^"]+)"', query)
        want_station = m.group(1) if m else None
        want_open = "is:open" in query
        items_out = []
        for item_id, it in state["items"].items():
            if want_open and state["issues"].get(str(it["number"]), {}).get("state") != "OPEN":
                continue
            if want_station is not None and it.get("station") != want_station:
                continue
            items_out.append(
                {"id": item_id, "content": {"number": it["number"], "repository": it["repo"]}}
            )
        ok(json.dumps({"items": items_out, "totalCount": len(items_out)}))

    if argv[:2] == ["api", "graphql"]:
        query_text = ""
        for i, a in enumerate(argv):
            if a == "-f" and i + 1 < len(argv) and argv[i + 1].startswith("query="):
                query_text = argv[i + 1][len("query="):]

        if "projectItems" in query_text:
            # FEAT-13's targeted single-issue lookup (factory_gh.issue_board_item_id), keyed on
            # the query TEXT (never argv order) since this dispatch sits ahead of the older
            # field-resolve query below and both hit ["api", "graphql"]. Read the real argv the
            # tool emits rather than guessing it.
            owner_v = name_v = number_v = None
            for i, a in enumerate(argv):
                if a == "-f" and i + 1 < len(argv) and argv[i + 1].startswith("owner="):
                    owner_v = argv[i + 1][len("owner="):]
                if a == "-f" and i + 1 < len(argv) and argv[i + 1].startswith("name="):
                    name_v = argv[i + 1][len("name="):]
                if a == "-F" and i + 1 < len(argv) and argv[i + 1].startswith("number="):
                    number_v = argv[i + 1][len("number="):]
            repo = f"{owner_v}/{name_v}"
            issue = state["issues"].get(number_v)
            if issue is None:
                ok(json.dumps({"data": {"repository": {"issue": None}}}))
            nodes = []
            for item_id, it in state["items"].items():
                if it.get("repo") == repo and str(it.get("number")) == number_v:
                    # THE SYNTHETIC NODE'S project.number MUST EQUAL THE FIXTURE'S BOARD
                    # NUMBER, 9 (fleet_dict's board.number) — issue_board_item_id matches
                    # client-side against each node's project.number, so a placeholder here
                    # makes every case return None and reddens SC-08 for a reason unrelated to
                    # the code under test.
                    nodes.append({"id": item_id, "project": {"number": 9}})
            ok(json.dumps({"data": {"repository": {"issue": {"projectItems": {
                "totalCount": len(nodes), "nodes": nodes,
            }}}}}))

        # The single GraphQL query factory_gh._project_field_resolve sends (D-01). Answered
        # unconditionally, without inspecting the query= text — that guard lives once, in
        # test-factory-gh.py. Placed BEFORE the generic ["api", ...] REST branch below: after it
        # this would still work by accident, since "graphql" matches none of the REST regexes.
        field_name = None
        for i, a in enumerate(argv):
            if a == "-f" and i + 1 < len(argv) and argv[i + 1].startswith("field="):
                field_name = argv[i + 1][len("field="):]
        ok(json.dumps({"data": {"repositoryOwner": {"__typename": "User", "projectV2": {
            "id": "PVT_kwFAKE",
            "field": {
                "id": "FIELD_STATUS", "name": field_name,
                "options": [
                    {"id": "OPT_READY", "name": "Ready"},
                    {"id": "OPT_BUILDING", "name": "Building"},
                    {"id": "OPT_REVIEW", "name": "Review"},
                ],
            },
        }}}}))

    if argv[:2] == ["project", "item-edit"]:
        item_id = argv[argv.index("--id") + 1]
        option_id = argv[argv.index("--single-select-option-id") + 1]
        project_id = argv[argv.index("--project-id") + 1]
        if project_id != "PVT_kwFAKE":
            bad(f"fake_gh: item-edit --project-id was {project_id!r}, want the node id "
                f"from the graphql field-resolve call, not the bare board number", 1)
        mapping = {"OPT_READY": "Ready", "OPT_BUILDING": "Building", "OPT_REVIEW": "Review"}
        rec = state["items"].setdefault(item_id, {"number": None, "repo": None})
        rec["station"] = mapping.get(option_id, option_id)
        ok()

    if argv and argv[0] == "api":
        rest = argv[1:]
        if "-X" in rest and rest[rest.index("-X") + 1] == "POST":
            target = rest[rest.index("-X") + 2]
            if re.match(r"^repos/.+/git/refs$", target):
                if state.get("ref_conflict"):
                    bad("422 Unprocessable Entity: reference already exists", 1)
                ok()
        if rest and re.match(r"^repos/.+/git/ref/heads/.+$", rest[0]):
            ok("deadbeefcafefeed0123456789abcdef01234567")
        m = re.match(r"^repos/.+/issues/(\d+)$", rest[0]) if rest else None
        if m and "--jq" in rest:
            ok(str(int(m.group(1)) + 100000))
        if rest and re.match(r"^repos/.+/issues/\d+/sub_issues$", rest[0]):
            ok()
        if rest and re.match(r"^repos/.+/issues/\d+/dependencies/blocked_by$", rest[0]):
            ok()

    if argv[:2] == ["pr", "create"]:
        repo = argv[argv.index("--repo") + 1]
        ok(f"https://github.com/{repo}/pull/1")

    bad(f"fake_gh: unhandled argv: {argv!r}", 1)


main()
'''

_FAKE_GIT_OK_SRC = """#!/usr/bin/env python3
# Always exits 0 with empty output — a no-op, EXCEPT: when FACTORY_GIT_LOG names an absolute
# path, this appends the argv (space-joined, one call per line) to it before exiting. Every case
# that does not set FACTORY_GIT_LOG gets the exact same no-op behaviour as before; the recording
# is opt-in per case, not a change to the stub's nature.
import os
import sys

log_path = os.environ.get("FACTORY_GIT_LOG")
if log_path:
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(" ".join(sys.argv[1:]) + "\\n")
sys.exit(0)
"""


def write_exec(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def write_yaml(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False)


def write_state(path, **overrides):
    state = {
        "auth_fail": False, "ref_conflict": False,
        "next_issue": 500, "next_item": 1,
        "issues": {}, "items": {},
    }
    state.update(overrides)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f)
    return path


def read_state(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def make_root(base):
    """A temp root with the docs/harness/SPEC.md probe CLAUDE_PROJECT_DIR redirection needs.
    Never carries .harness/factory/fleet.yaml — every case passes --fleet explicitly."""
    root = os.path.join(base, "root")
    os.makedirs(os.path.join(root, "docs", "harness"), exist_ok=True)
    with open(os.path.join(root, "docs", "harness", "SPEC.md"), "w", encoding="utf-8") as f:
        f.write("stub probe for T-12\n")
    return root


REPO = "acme/widget"
DEFAULT_BRANCH = "main"


def fleet_dict(workspace_root, repo=REPO, default_branch=DEFAULT_BRANCH):
    return {
        "schema": "factory-fleet/1",
        "repos": [{
            "name": repo, "default_branch": default_branch,
            "board": {
                "owner": "acme", "number": 9, "station_field": "Status",
                "stations": {"ready": "Ready", "building": "Building", "review": "Review"},
            },
        }],
        "workspace_root": workspace_root,
    }


def base_env(root, gh_bin=None, git_bin=None, gh_state=None):
    env = dict(os.environ)
    env["CLAUDE_PROJECT_DIR"] = root
    if gh_bin:
        env["FACTORY_GH"] = gh_bin
    else:
        env.pop("FACTORY_GH", None)
    if git_bin:
        env["FACTORY_GIT"] = git_bin
    else:
        env.pop("FACTORY_GIT", None)
    if gh_state:
        env["GH_STATE"] = gh_state
    else:
        env.pop("GH_STATE", None)
    return env


def run_tool(tool_key, args, env, cwd):
    return subprocess.run(
        [sys.executable, TOOLS[tool_key]] + args,
        cwd=cwd, env=env, capture_output=True, text=True,
        stdin=subprocess.DEVNULL, timeout=20,
    )


def not_ignored(label, r):
    check(f"{label}: harness_root probe was not silently discarded (no 'IGNORING it')",
          "IGNORING it" not in r.stderr, r.stderr)


# ============================================================================
# Case (A) — every one of the five tools, run with NO arguments, exits 2, never 1.
# ============================================================================
for tool in ("config", "decompose", "claim", "workspace", "land"):
    with tempfile.TemporaryDirectory() as td:
        root = make_root(td)
        gh = os.path.join(td, "fake_gh.py")
        write_exec(gh, _FAKE_GH_SRC)
        gitb = os.path.join(td, "fake_git.py")
        write_exec(gitb, _FAKE_GIT_OK_SRC)
        cwd = os.path.join(td, "cwd")
        os.makedirs(cwd, exist_ok=True)
        env = base_env(root, gh_bin=gh, git_bin=gitb)
        r = run_tool(tool, [], env, cwd)
        check(f"(A) {tool}: no arguments exits 2", r.returncode == 2, f"code={r.returncode} stderr={r.stderr!r}")
        check(f"(A) {tool}: no arguments never exits 1", r.returncode != 1, f"code={r.returncode}")
        check(f"(A) {tool}: no arguments writes nothing to stdout", r.stdout == "", repr(r.stdout))
        not_ignored(f"(A) {tool}", r)

# ============================================================================
# Case (B) — a --fleet path that does not exist exits 2 naming that path on stderr.
# ============================================================================
with tempfile.TemporaryDirectory() as td:
    root = make_root(td)
    missing = os.path.join(td, "does", "not", "exist", "fleet.yaml")
    cwd = os.path.join(td, "cwd")
    os.makedirs(cwd, exist_ok=True)
    env = base_env(root)
    r = run_tool("claim", ["--as", "agent-a", "--fleet", missing], env, cwd)
    check("(B) missing --fleet path: exits 2", r.returncode == 2, f"code={r.returncode}")
    check("(B) missing --fleet path: nothing on stdout", r.stdout == "", repr(r.stdout))
    check("(B) missing --fleet path: stderr names the path", missing in r.stderr, r.stderr)
    not_ignored("(B)", r)

# ============================================================================
# Case (C) — SC-10: a stub gh that fails `auth status` exits 2, never 1, empty stdout,
# non-empty stderr. Only decompose/claim/land ever call gh (grep-verified in the module
# docstring above) — config and workspace are structurally exempt and are not asserted here.
# ============================================================================
with tempfile.TemporaryDirectory() as td:
    root = make_root(td)
    gh = os.path.join(td, "fake_gh.py")
    write_exec(gh, _FAKE_GH_SRC)
    gitb = os.path.join(td, "fake_git.py")
    write_exec(gitb, _FAKE_GIT_OK_SRC)
    workspace_root = os.path.join(td, "workspaces")
    fleet_path = os.path.join(td, "fleet", "fleet.yaml")
    write_yaml(fleet_path, fleet_dict(workspace_root))
    cwd = os.path.join(td, "cwd")
    os.makedirs(cwd, exist_ok=True)
    gh_state = write_state(os.path.join(td, "gh_state.json"), auth_fail=True)
    env = base_env(root, gh_bin=gh, git_bin=gitb, gh_state=gh_state)

    # decompose: needs a valid signed plan to reach preflight.
    feat_dir = os.path.join(td, "feature")
    os.makedirs(feat_dir, exist_ok=True)
    write_yaml(os.path.join(feat_dir, "plan.yaml"), {
        "schema": "plan/1", "feature": "FEAT-AUTHFAIL", "approval": {"status": "approved"},
        "tasks": [{
            "id": "T-1", "title": "do a thing", "change_type": "feature",
            "execution_mode": "team", "files": ["a.py"], "verify": "true",
            "intent": "intent text, verbatim.", "traces": ["REQ-01"],
        }],
    })
    r = run_tool("decompose", [feat_dir, "--repo", REPO, "--fleet", fleet_path], env, cwd)
    check("(C) decompose: auth failure exits 2", r.returncode == 2, f"code={r.returncode}")
    check("(C) decompose: auth failure never exits 1", r.returncode != 1)
    check("(C) decompose: auth failure writes nothing to stdout", r.stdout == "", repr(r.stdout))
    check("(C) decompose: auth failure writes to stderr", r.stderr != "")

    # claim: preflight is step 1, before any board read.
    r = run_tool("claim", ["--as", "agent-a", "--fleet", fleet_path], env, cwd)
    check("(C) claim: auth failure exits 2", r.returncode == 2, f"code={r.returncode}")
    check("(C) claim: auth failure never exits 1", r.returncode != 1)
    check("(C) claim: auth failure writes nothing to stdout", r.stdout == "", repr(r.stdout))
    check("(C) claim: auth failure writes to stderr", r.stderr != "")

    # land: the git push (step 3) precedes preflight (step 4), so pre-create the checkout so
    # the stub git push succeeds trivially and preflight is what is actually being measured.
    os.makedirs(os.path.join(workspace_root, "widget"), exist_ok=True)
    r = run_tool("land", ["--repo", REPO, "--issue", "9001", "--fleet", fleet_path], env, cwd)
    check("(C) land: auth failure exits 2", r.returncode == 2, f"code={r.returncode}")
    check("(C) land: auth failure never exits 1", r.returncode != 1)
    check("(C) land: auth failure writes nothing to stdout", r.stdout == "", repr(r.stdout))
    check("(C) land: auth failure writes to stderr", r.stderr != "")

# ============================================================================
# Case (D) — a run whose stubs script a success exits 0 and its whole stdout parses in one
# json.loads, for every one of the five tools.
# ============================================================================

# (D-config)
with tempfile.TemporaryDirectory() as td:
    root = make_root(td)
    fleet_path = os.path.join(td, "fleet", "fleet.yaml")
    write_yaml(fleet_path, fleet_dict(os.path.join(td, "workspaces")))
    cwd = os.path.join(td, "cwd")
    os.makedirs(cwd, exist_ok=True)
    env = base_env(root)
    r = run_tool("config", ["--fleet", fleet_path, "--show"], env, cwd)
    check("(D-config) success: exits 0", r.returncode == 0, f"code={r.returncode} stderr={r.stderr!r}")
    try:
        payload = json.loads(r.stdout)
        check("(D-config) success: stdout is one JSON object", True)
        check("(D-config) success: payload carries repos, each with its own board, and no "
              "fleet-level board",
              "repos" in payload and "board" not in payload
              and payload["repos"][0]["board"]["number"] == 9, payload)
    except Exception as e:
        check("(D-config) success: stdout is one JSON object", False, str(e))
    not_ignored("(D-config)", r)

# (D-decompose)
with tempfile.TemporaryDirectory() as td:
    root = make_root(td)
    gh = os.path.join(td, "fake_gh.py")
    write_exec(gh, _FAKE_GH_SRC)
    fleet_path = os.path.join(td, "fleet", "fleet.yaml")
    write_yaml(fleet_path, fleet_dict(os.path.join(td, "workspaces")))
    cwd = os.path.join(td, "cwd")
    os.makedirs(cwd, exist_ok=True)
    gh_state = write_state(os.path.join(td, "gh_state.json"))
    env = base_env(root, gh_bin=gh, gh_state=gh_state)
    feat_dir = os.path.join(td, "feature")
    os.makedirs(feat_dir, exist_ok=True)
    write_yaml(os.path.join(feat_dir, "plan.yaml"), {
        "schema": "plan/1", "feature": "FEAT-DSUCCESS", "approval": {"status": "approved"},
        "tasks": [{
            "id": "T-1", "title": "do a thing", "change_type": "feature",
            "execution_mode": "team", "files": ["a.py"], "verify": "true",
            "intent": "intent text, verbatim.", "traces": ["REQ-01"],
        }],
    })
    r = run_tool("decompose", [feat_dir, "--repo", REPO, "--fleet", fleet_path], env, cwd)
    check("(D-decompose) success: exits 0", r.returncode == 0, f"code={r.returncode} stderr={r.stderr!r}")
    try:
        payload = json.loads(r.stdout)
        check("(D-decompose) success: stdout is one JSON object", True)
        check("(D-decompose) success: one issue recorded for T-1", payload.get("issues", {}).get("T-1") is not None, payload)
    except Exception as e:
        check("(D-decompose) success: stdout is one JSON object", False, str(e))
    not_ignored("(D-decompose)", r)

# (D-claim)
with tempfile.TemporaryDirectory() as td:
    root = make_root(td)
    gh = os.path.join(td, "fake_gh.py")
    write_exec(gh, _FAKE_GH_SRC)
    fleet_path = os.path.join(td, "fleet", "fleet.yaml")
    write_yaml(fleet_path, fleet_dict(os.path.join(td, "workspaces")))
    cwd = os.path.join(td, "cwd")
    os.makedirs(cwd, exist_ok=True)
    gh_state = write_state(
        os.path.join(td, "gh_state.json"),
        next_issue=700,
        issues={"600": {"title": "pick me", "state": "OPEN", "labels": [], "assignees": []}},
        items={"ITEMX": {"number": 600, "repo": REPO, "station": "Ready"}},
    )
    env = base_env(root, gh_bin=gh, gh_state=gh_state)
    r = run_tool("claim", ["--as", "agent-a", "--repo", REPO, "--fleet", fleet_path], env, cwd)
    check("(D-claim) success: exits 0", r.returncode == 0, f"code={r.returncode} stderr={r.stderr!r}")
    try:
        payload = json.loads(r.stdout)
        check("(D-claim) success: stdout is one JSON object", True)
        check("(D-claim) success: payload branch is factory/issue-600",
              payload.get("branch") == "factory/issue-600", payload)
    except Exception as e:
        check("(D-claim) success: stdout is one JSON object", False, str(e))
    st = read_state(gh_state)
    check("(D-claim) success: board item actually moved to Building",
          st["items"]["ITEMX"]["station"] == "Building", st["items"])
    not_ignored("(D-claim)", r)

# (D-workspace)
with tempfile.TemporaryDirectory() as td:
    root = make_root(td)
    gitb = os.path.join(td, "fake_git.py")
    write_exec(gitb, _FAKE_GIT_OK_SRC)
    workspace_root = os.path.join(td, "workspaces")
    fleet_path = os.path.join(td, "fleet", "fleet.yaml")
    write_yaml(fleet_path, fleet_dict(workspace_root))
    os.makedirs(os.path.join(workspace_root, "widget", ".git"), exist_ok=True)
    cwd = os.path.join(td, "cwd")
    os.makedirs(cwd, exist_ok=True)
    env = base_env(root, git_bin=gitb)
    r = run_tool("workspace", ["--repo", REPO, "--issue", "800", "--fleet", fleet_path], env, cwd)
    check("(D-workspace) success: exits 0", r.returncode == 0, f"code={r.returncode} stderr={r.stderr!r}")
    try:
        payload = json.loads(r.stdout)
        check("(D-workspace) success: stdout is one JSON object", True)
        check("(D-workspace) success: payload path is under workspace_root",
              payload.get("path", "").startswith(os.path.abspath(workspace_root)), payload)
        check("(D-workspace) success: payload branch is factory/issue-800",
              payload.get("branch") == "factory/issue-800", payload)
    except Exception as e:
        check("(D-workspace) success: stdout is one JSON object", False, str(e))
    not_ignored("(D-workspace)", r)

# (D-land)
with tempfile.TemporaryDirectory() as td:
    root = make_root(td)
    gh = os.path.join(td, "fake_gh.py")
    write_exec(gh, _FAKE_GH_SRC)
    gitb = os.path.join(td, "fake_git.py")
    write_exec(gitb, _FAKE_GIT_OK_SRC)
    workspace_root = os.path.join(td, "workspaces")
    fleet_path = os.path.join(td, "fleet", "fleet.yaml")
    write_yaml(fleet_path, fleet_dict(workspace_root))
    os.makedirs(os.path.join(workspace_root, "widget"), exist_ok=True)
    cwd = os.path.join(td, "cwd")
    os.makedirs(cwd, exist_ok=True)
    gh_state = write_state(
        os.path.join(td, "gh_state.json"),
        issues={"700": {"title": "land me", "state": "OPEN", "labels": [], "assignees": []}},
        items={"ITEMY": {"number": 700, "repo": REPO, "station": "Building"}},
    )
    env = base_env(root, gh_bin=gh, git_bin=gitb, gh_state=gh_state)
    r = run_tool("land", ["--repo", REPO, "--issue", "700", "--fleet", fleet_path], env, cwd)
    check("(D-land) success: exits 0", r.returncode == 0, f"code={r.returncode} stderr={r.stderr!r}")
    try:
        payload = json.loads(r.stdout)
        check("(D-land) success: stdout is one JSON object", True)
        check("(D-land) success: payload carries a pull request url",
              str(payload.get("url", "")).startswith("https://"), payload)
    except Exception as e:
        check("(D-land) success: stdout is one JSON object", False, str(e))
    st = read_state(gh_state)
    check("(D-land) success: board item actually moved to Review",
          st["items"]["ITEMY"]["station"] == "Review", st["items"])
    not_ignored("(D-land)", r)

# ============================================================================
# Case (E) — factory_claim.py with every candidate's ref create refused: the losing agent,
# observed as a process. Exits 1 (nothing_to_do — no --issue means every skip falls through
# to the exhausted-queue path, never lost_race's exit 3), writes nothing to stdout.
# ============================================================================
with tempfile.TemporaryDirectory() as td:
    root = make_root(td)
    gh = os.path.join(td, "fake_gh.py")
    write_exec(gh, _FAKE_GH_SRC)
    fleet_path = os.path.join(td, "fleet", "fleet.yaml")
    write_yaml(fleet_path, fleet_dict(os.path.join(td, "workspaces")))
    cwd = os.path.join(td, "cwd")
    os.makedirs(cwd, exist_ok=True)
    gh_state = write_state(
        os.path.join(td, "gh_state.json"),
        ref_conflict=True,
        issues={"600": {"title": "contested", "state": "OPEN", "labels": [], "assignees": []}},
        items={"ITEMX": {"number": 600, "repo": REPO, "station": "Ready"}},
    )
    env = base_env(root, gh_bin=gh, gh_state=gh_state)
    r = run_tool("claim", ["--as", "agent-a", "--repo", REPO, "--fleet", fleet_path], env, cwd)
    check("(E) ref refused for every candidate: exits 1", r.returncode == 1, f"code={r.returncode}")
    check("(E) ref refused for every candidate: writes nothing to stdout", r.stdout == "", repr(r.stdout))
    not_ignored("(E)", r)

# ============================================================================
# Case (F) — SC-19: the happy path, end to end. decompose -> claim -> workspace -> land,
# composed for real, each step consuming the previous step's own payload.
# ============================================================================
with tempfile.TemporaryDirectory() as td:
    root = make_root(td)
    gh = os.path.join(td, "fake_gh.py")
    write_exec(gh, _FAKE_GH_SRC)
    gitb = os.path.join(td, "fake_git.py")
    write_exec(gitb, _FAKE_GIT_OK_SRC)
    workspace_root = os.path.join(td, "workspaces")
    fleet_path = os.path.join(td, "fleet", "fleet.yaml")
    fleet_data = fleet_dict(workspace_root)
    write_yaml(fleet_path, fleet_data)
    ready_option = fleet_data["repos"][0]["board"]["stations"]["ready"]
    cwd = os.path.join(td, "cwd")
    os.makedirs(cwd, exist_ok=True)
    gh_state = write_state(os.path.join(td, "gh_state.json"), next_issue=500)
    env = base_env(root, gh_bin=gh, git_bin=gitb, gh_state=gh_state)
    # GAP 3 (ii)/(iii): an env-gated absolute log path for this case only — FACTORY_GIT_LOG is
    # never set for any other case, so their stub-git behaviour is unaffected.
    git_log = os.path.join(td, "git_log.txt")
    env["FACTORY_GIT_LOG"] = git_log

    # The fixture plan lives exactly where factory_claim's (import-time) FEATURES_ROOT will
    # look for it under this case's CLAUDE_PROJECT_DIR: <root>/.harness/features/<feature>.
    feat = "FEAT-INTEG-HAPPY"
    feat_dir = os.path.join(root, ".harness", "features", feat)
    os.makedirs(feat_dir, exist_ok=True)
    write_yaml(os.path.join(feat_dir, "plan.yaml"), {
        "schema": "plan/1", "feature": feat, "approval": {"status": "approved"},
        "tasks": [
            {
                "id": "T-1", "title": "the first task, no dependencies", "change_type": "feature",
                "execution_mode": "team", "files": ["a.py"], "verify": "true",
                "intent": "intent text for T-1, verbatim.", "traces": ["REQ-01"],
            },
            {
                "id": "T-2", "title": "the second task, depends on T-1", "change_type": "feature",
                "execution_mode": "team", "files": ["b.py"], "verify": "true",
                "intent": "intent text for T-2, verbatim.", "traces": ["REQ-01"],
                "depends_on": ["T-1"],
            },
        ],
    })

    # Step 1: decompose.
    r1 = run_tool("decompose", [feat_dir, "--repo", REPO, "--fleet", fleet_path], env, cwd)
    check("(F) decompose exits 0", r1.returncode == 0, f"code={r1.returncode} stderr={r1.stderr!r}")
    try:
        p1 = json.loads(r1.stdout)
        check("(F) decompose: stdout is one JSON object", True)
        check("(F) decompose: one issue per task", set(p1.get("issues", {})) == {"T-1", "T-2"}, p1)
    except Exception as e:
        p1 = {}
        check("(F) decompose: stdout is one JSON object", False, str(e))
    not_ignored("(F) decompose", r1)

    # GAP 3 (i): decompose boards both items at the fleet's declared `ready` station — read
    # BEFORE claim runs, since claim is what moves the winner to Building.
    st_after_decompose = read_state(gh_state)
    check(
        "(F) decompose: both board items boarded at the fleet's declared ready station",
        len(st_after_decompose["items"]) == 2
        and all(v["station"] == ready_option for v in st_after_decompose["items"].values()),
        st_after_decompose["items"],
    )

    # Step 2: claim (no --issue: polls the ready queue; T-1's issue number is the lowest).
    r2 = run_tool("claim", ["--as", "agent-a", "--repo", REPO, "--fleet", fleet_path], env, cwd)
    check("(F) claim exits 0", r2.returncode == 0, f"code={r2.returncode} stderr={r2.stderr!r}")
    try:
        p2 = json.loads(r2.stdout)
        check("(F) claim: stdout is one JSON object", True)
        expected_issue = p1.get("issues", {}).get("T-1")
        check("(F) claim: claimed the T-1 issue (unblocked candidate)",
              p2.get("issue") == expected_issue, (p2, expected_issue))
        check("(F) claim: payload branch is factory/issue-<n>",
              p2.get("branch") == f"factory/issue-{p2.get('issue')}", p2)
    except Exception as e:
        p2 = {}
        check("(F) claim: stdout is one JSON object", False, str(e))
    st = read_state(gh_state)
    claimed_item = next(
        (v for v in st["items"].values() if v["number"] == p2.get("issue")), None
    )
    check("(F) claim: board item actually moved to Building",
          claimed_item is not None and claimed_item["station"] == "Building", st["items"])
    not_ignored("(F) claim", r2)

    # Step 3: workspace, for the issue claim just handed back. Pre-create the checkout's .git
    # so the tool takes the fetch/checkout/reset branch, never the clone (network) branch — the
    # stub git cannot actually clone anything.
    os.makedirs(os.path.join(workspace_root, "widget", ".git"), exist_ok=True)
    r3 = run_tool(
        "workspace", ["--repo", REPO, "--issue", str(p2.get("issue")), "--fleet", fleet_path],
        env, cwd,
    )
    check("(F) workspace exits 0", r3.returncode == 0, f"code={r3.returncode} stderr={r3.stderr!r}")
    try:
        p3 = json.loads(r3.stdout)
        check("(F) workspace: stdout is one JSON object", True)
        check("(F) workspace: payload path is under workspace_root",
              p3.get("path", "").startswith(os.path.abspath(workspace_root)), p3)
        check("(F) workspace: payload branch matches claim's branch",
              p3.get("branch") == p2.get("branch"), (p3, p2))
        # GAP 3 (iii), split: the cheap half — a real directory on the filesystem, not merely a
        # payload string.
        check("(F) workspace: the payload path is an actual directory on disk",
              os.path.isdir(p3.get("path", "")), p3.get("path"))
    except Exception as e:
        check("(F) workspace: stdout is one JSON object", False, str(e))
    not_ignored("(F) workspace", r3)

    # GAP 3 (iii), the other half — the recorded git commands include a checkout of the claimed
    # branch. Read via the recorder wired into _FAKE_GIT_OK_SRC (FACTORY_GIT_LOG).
    log_after_workspace = []
    if os.path.exists(git_log):
        with open(git_log, encoding="utf-8") as f:
            log_after_workspace = [l.strip() for l in f if l.strip()]
    branch = p2.get("branch")
    check(
        "(F) workspace: recorded git commands include a checkout of factory/issue-<n>",
        any(l.startswith("checkout") and branch in l for l in log_after_workspace),
        log_after_workspace,
    )

    # Step 4: land, for the same issue.
    r4 = run_tool(
        "land", ["--repo", REPO, "--issue", str(p2.get("issue")), "--fleet", fleet_path],
        env, cwd,
    )
    check("(F) land exits 0", r4.returncode == 0, f"code={r4.returncode} stderr={r4.stderr!r}")
    try:
        p4 = json.loads(r4.stdout)
        check("(F) land: stdout is one JSON object", True)
        check("(F) land: opened exactly one pull request",
              str(p4.get("url", "")).startswith("https://"), p4)
    except Exception as e:
        check("(F) land: stdout is one JSON object", False, str(e))
    st = read_state(gh_state)
    landed_item = next(
        (v for v in st["items"].values() if v["number"] == p2.get("issue")), None
    )
    check("(F) land: board item actually moved to Review",
          landed_item is not None and landed_item["station"] == "Review", st["items"])
    not_ignored("(F) land", r4)

    # GAP 3 (ii): land pushes the claimed branch — asserted against the recorded git commands,
    # not merely inferred from a successful exit.
    log_after_land = []
    if os.path.exists(git_log):
        with open(git_log, encoding="utf-8") as f:
            log_after_land = [l.strip() for l in f if l.strip()]
    check(
        "(F) land: recorded git commands include a push of factory/issue-<n> to origin",
        any(
            l.startswith("push") and "--set-upstream" in l and "origin" in l and branch in l
            for l in log_after_land
        ),
        log_after_land,
    )


# ============================================================================
# Case (G) — the T-06 live-git smoke check (T-12 addition). FACTORY_GIT points at REAL git
# against a fully local fixture (bare "origin" + one clone): both untested argv forms from
# factory_workspace.py:97 (-B ... --track) and :101 (-b ... --track) are reached by running the
# real module, never a hand-typed argv. Hermetic git config (GIT_CONFIG_GLOBAL/SYSTEM=os.devnull,
# a private HOME) rules out branch.autoSetupMerge silently turning the -B case into a bare
# `checkout <branch>` (case F would then be exercising nothing).
# ============================================================================
real_git = None
for candidate in ("/usr/bin/git", "/usr/local/bin/git", "/opt/homebrew/bin/git"):
    if os.path.exists(candidate):
        real_git = candidate
        break
if real_git is None:
    import shutil
    real_git = shutil.which("git")

if real_git is None:
    check("(G) live-git smoke check: BLOCKED — no git binary found on this machine", False)
else:
    git_version = subprocess.run([real_git, "--version"], capture_output=True, text=True).stdout.strip()

    def hermetic_git_env(home):
        env = dict(os.environ)
        env["GIT_CONFIG_GLOBAL"] = os.devnull
        env["GIT_CONFIG_SYSTEM"] = os.devnull
        env["HOME"] = home
        env["GIT_AUTHOR_NAME"] = "t12"
        env["GIT_AUTHOR_EMAIL"] = "t12@example.com"
        env["GIT_COMMITTER_NAME"] = "t12"
        env["GIT_COMMITTER_EMAIL"] = "t12@example.com"
        return env

    def git(args, cwd, genv):
        r = subprocess.run(
            [real_git] + args, cwd=cwd, env=genv, capture_output=True, text=True,
            stdin=subprocess.DEVNULL,
        )
        if r.returncode != 0:
            raise RuntimeError(f"fixture git {args} failed: {r.stdout!r} {r.stderr!r}")
        return r.stdout

    def rev_parse(cwd, genv, ref="HEAD"):
        return git(["rev-parse", ref], cwd, genv).strip()

    def upstream_of(cwd, genv, branch):
        r = subprocess.run(
            [real_git, "for-each-ref", "--format=%(upstream:short)", f"refs/heads/{branch}"],
            cwd=cwd, env=genv, capture_output=True, text=True,
        )
        return r.stdout.strip()

    # --- (G1) the -b ... --track form (factory_workspace.py:101): fresh clone, origin already
    # carries factory/issue-<n>, no local branch of that name exists yet. ---------------------
    with tempfile.TemporaryDirectory() as td:
        root = make_root(td)
        genv = hermetic_git_env(os.path.join(td, "home"))
        os.makedirs(genv["HOME"], exist_ok=True)

        origin = os.path.join(td, "origin.git")
        git(["init", "--bare", "-b", DEFAULT_BRANCH, origin], td, genv)

        seed = os.path.join(td, "seed")
        git(["clone", origin, seed], td, genv)
        with open(os.path.join(seed, "README.md"), "w", encoding="utf-8") as f:
            f.write("seed\n")
        git(["add", "README.md"], seed, genv)
        git(["commit", "-m", "seed"], seed, genv)
        git(["push", "origin", DEFAULT_BRANCH], seed, genv)

        git(["checkout", "-b", "factory/issue-1"], seed, genv)
        with open(os.path.join(seed, "extra.txt"), "w", encoding="utf-8") as f:
            f.write("extra\n")
        git(["add", "extra.txt"], seed, genv)
        git(["commit", "-m", "issue work"], seed, genv)
        git(["push", "origin", "factory/issue-1"], seed, genv)
        origin_issue_sha = rev_parse(seed, genv, "factory/issue-1")

        workspace_root = os.path.join(td, "workspaces")
        os.makedirs(workspace_root, exist_ok=True)
        checkout = os.path.join(workspace_root, "widget")
        git(["clone", origin, checkout], td, genv)  # .git exists -> the else (fetch) branch.

        fleet_path = os.path.join(td, "fleet", "fleet.yaml")
        write_yaml(fleet_path, fleet_dict(workspace_root))
        cwd = os.path.join(td, "cwd")
        os.makedirs(cwd, exist_ok=True)
        env = base_env(root, git_bin=real_git)
        r = run_tool("workspace", ["--repo", REPO, "--issue", "1", "--fleet", fleet_path], env, cwd)
        check("(G1) -b --track form: workspace exits 0 against real git",
              r.returncode == 0, f"code={r.returncode} stderr={r.stderr!r}")
        if r.returncode == 0:
            check("(G1) -b --track form: HEAD equals origin's factory/issue-1",
                  rev_parse(checkout, genv) == origin_issue_sha,
                  (rev_parse(checkout, genv), origin_issue_sha))
            check("(G1) -b --track form: local branch tracks origin/factory/issue-1",
                  upstream_of(checkout, genv, "factory/issue-1") == "origin/factory/issue-1",
                  upstream_of(checkout, genv, "factory/issue-1"))
        not_ignored("(G1)", r)

    # --- (G2) the -B ... --track form (factory_workspace.py:97): a local factory/issue-<n>
    # already exists (cut from default_branch, no upstream), and origin's ref has since moved
    # ahead — the local branch must be FORCE-ALIGNED onto origin's tip, not kept as is. --------
    with tempfile.TemporaryDirectory() as td:
        root = make_root(td)
        genv = hermetic_git_env(os.path.join(td, "home"))
        os.makedirs(genv["HOME"], exist_ok=True)

        origin = os.path.join(td, "origin.git")
        git(["init", "--bare", "-b", DEFAULT_BRANCH, origin], td, genv)

        seed = os.path.join(td, "seed")
        git(["clone", origin, seed], td, genv)
        with open(os.path.join(seed, "README.md"), "w", encoding="utf-8") as f:
            f.write("seed\n")
        git(["add", "README.md"], seed, genv)
        git(["commit", "-m", "seed"], seed, genv)
        git(["push", "origin", DEFAULT_BRANCH], seed, genv)

        git(["checkout", "-b", "factory/issue-2"], seed, genv)
        with open(os.path.join(seed, "extra.txt"), "w", encoding="utf-8") as f:
            f.write("extra\n")
        git(["add", "extra.txt"], seed, genv)
        git(["commit", "-m", "issue work"], seed, genv)
        git(["push", "origin", "factory/issue-2"], seed, genv)
        origin_issue_sha = rev_parse(seed, genv, "factory/issue-2")

        workspace_root = os.path.join(td, "workspaces")
        os.makedirs(workspace_root, exist_ok=True)
        checkout = os.path.join(workspace_root, "widget")
        git(["clone", origin, checkout], td, genv)
        # A LOCAL branch cut from local default_branch, with no upstream — starting point is a
        # LOCAL ref, so git's own autoSetupMerge default (which only fires off a remote-tracking
        # start point) cannot silently give it one; the hermetic config rules out any surprise.
        git(["branch", "factory/issue-2", DEFAULT_BRANCH], checkout, genv)
        pre_local_sha = rev_parse(checkout, genv, "factory/issue-2")
        check("(G2) fixture sanity: local factory/issue-2 differs from origin's before the run",
              pre_local_sha != origin_issue_sha, (pre_local_sha, origin_issue_sha))
        check("(G2) fixture sanity: local factory/issue-2 has no upstream before the run",
              upstream_of(checkout, genv, "factory/issue-2") == "", "has an upstream already")

        fleet_path = os.path.join(td, "fleet", "fleet.yaml")
        write_yaml(fleet_path, fleet_dict(workspace_root))
        cwd = os.path.join(td, "cwd")
        os.makedirs(cwd, exist_ok=True)
        env = base_env(root, git_bin=real_git)
        r = run_tool("workspace", ["--repo", REPO, "--issue", "2", "--fleet", fleet_path], env, cwd)
        check("(G2) -B --track form: workspace exits 0 against real git",
              r.returncode == 0, f"code={r.returncode} stderr={r.stderr!r}")
        if r.returncode == 0:
            check("(G2) -B --track form: HEAD force-aligned onto origin's factory/issue-2",
                  rev_parse(checkout, genv) == origin_issue_sha,
                  (rev_parse(checkout, genv), origin_issue_sha))
            check("(G2) -B --track form: local branch now tracks origin/factory/issue-2",
                  upstream_of(checkout, genv, "factory/issue-2") == "origin/factory/issue-2",
                  upstream_of(checkout, genv, "factory/issue-2"))
        not_ignored("(G2)", r)

    check(f"(G) live-git smoke check ran against a real git binary ({real_git}, {git_version})", True)


# ============================================================================
# Case (H) — a fleet declaring TWO repositories on TWO DIFFERENT board numbers, driven through
# decompose -> claim -> land against ONE of them (T-05 addition, real processes composing). Every
# recorded gh call that carries a board number carries the served repository's board number, and
# never the other repository's — this file is the only place these tools run as real processes
# and compose, so it is the only place that can prove this end to end.
# ============================================================================
def _board_numbers_in_gh_call(argv):
    """Board-number-bearing positions only: the `project` subcommand's numeric positional
    (item-add / item-list) and the field-resolve graphql call's `-F number=` argument. The
    issue-item graphql call also carries a `-F number=`, but that one is an ISSUE number, not a
    board number — excluded here by keying off the query text, exactly as the fake gh's own
    dispatch (above) tells the two graphql calls apart."""
    found = set()
    if argv[:2] in (["project", "item-add"], ["project", "item-list"]):
        found.add(argv[2])
    if argv[:2] == ["api", "graphql"]:
        query_text = ""
        for i, a in enumerate(argv):
            if a == "-f" and i + 1 < len(argv) and argv[i + 1].startswith("query="):
                query_text = argv[i + 1]
        if "projectV2(number:" in query_text:
            for i, a in enumerate(argv):
                if a == "-F" and i + 1 < len(argv) and argv[i + 1].startswith("number="):
                    found.add(argv[i + 1][len("number="):])
    return found


with tempfile.TemporaryDirectory() as td:
    root = make_root(td)
    gh = os.path.join(td, "fake_gh.py")
    write_exec(gh, _FAKE_GH_SRC)
    gitb = os.path.join(td, "fake_git.py")
    write_exec(gitb, _FAKE_GIT_OK_SRC)
    workspace_root = os.path.join(td, "workspaces")
    other_repo = "acme/gadget"
    other_number = 42
    served_number = 9
    fleet_two = {
        "schema": "factory-fleet/1",
        "repos": [
            {
                "name": REPO, "default_branch": DEFAULT_BRANCH,
                "board": {
                    "owner": "acme", "number": served_number, "station_field": "Status",
                    "stations": {"ready": "Ready", "building": "Building", "review": "Review"},
                },
            },
            {
                "name": other_repo, "default_branch": "main",
                "board": {
                    "owner": "acme", "number": other_number, "station_field": "Status",
                    "stations": {"ready": "Ready", "building": "Building", "review": "Review"},
                },
            },
        ],
        "workspace_root": workspace_root,
    }
    fleet_path = os.path.join(td, "fleet", "fleet.yaml")
    write_yaml(fleet_path, fleet_two)
    cwd = os.path.join(td, "cwd")
    os.makedirs(cwd, exist_ok=True)
    gh_state = write_state(os.path.join(td, "gh_state.json"), next_issue=500)
    call_log = os.path.join(td, "gh_call_log.jsonl")
    env = base_env(root, gh_bin=gh, git_bin=gitb, gh_state=gh_state)
    env["GH_CALL_LOG"] = call_log

    feat = "FEAT-INTEG-TWOBOARD"
    feat_dir = os.path.join(root, ".harness", "features", feat)
    os.makedirs(feat_dir, exist_ok=True)
    write_yaml(os.path.join(feat_dir, "plan.yaml"), {
        "schema": "plan/1", "feature": feat, "approval": {"status": "approved"},
        "tasks": [{
            "id": "T-1", "title": "the only task", "change_type": "feature",
            "execution_mode": "team", "files": ["a.py"], "verify": "true",
            "intent": "intent text, verbatim.", "traces": ["REQ-01"],
        }],
    })

    r1 = run_tool("decompose", [feat_dir, "--repo", REPO, "--fleet", fleet_path], env, cwd)
    check("(H) decompose against the two-board fleet exits 0",
          r1.returncode == 0, f"code={r1.returncode} stderr={r1.stderr!r}")
    p1 = json.loads(r1.stdout) if r1.returncode == 0 else {}
    not_ignored("(H) decompose", r1)

    r2 = run_tool("claim", ["--as", "agent-a", "--repo", REPO, "--fleet", fleet_path], env, cwd)
    check("(H) claim against the two-board fleet exits 0",
          r2.returncode == 0, f"code={r2.returncode} stderr={r2.stderr!r}")
    p2 = json.loads(r2.stdout) if r2.returncode == 0 else {}
    not_ignored("(H) claim", r2)

    os.makedirs(os.path.join(workspace_root, "widget"), exist_ok=True)
    r4 = run_tool(
        "land", ["--repo", REPO, "--issue", str(p2.get("issue")), "--fleet", fleet_path],
        env, cwd,
    )
    check("(H) land against the two-board fleet exits 0",
          r4.returncode == 0, f"code={r4.returncode} stderr={r4.stderr!r}")
    not_ignored("(H) land", r4)

    calls = []
    if os.path.exists(call_log):
        with open(call_log, encoding="utf-8") as f:
            calls = [json.loads(l) for l in f if l.strip()]
    check("(H) at least one gh call was recorded (anti-vacuum)", len(calls) > 0, calls)

    board_numbers_seen = set()
    for c in calls:
        board_numbers_seen |= _board_numbers_in_gh_call(c)
    check(
        "(H) no recorded gh call names the other repository's board number",
        str(other_number) not in board_numbers_seen, sorted(board_numbers_seen),
    )
    check(
        "(H) at least one recorded gh call names the served repository's own board number "
        "(proves the check above has power)",
        str(served_number) in board_numbers_seen, sorted(board_numbers_seen),
    )


print(f"\n{RAN - FAILS}/{RAN} checks passed." if FAILS == 0 else f"\n{FAILS} of {RAN} FAILING.")
sys.exit(1 if FAILS else 0)
