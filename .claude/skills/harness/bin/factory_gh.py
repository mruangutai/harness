"""factory_gh.py — the single seam every factory tool talks to GitHub through (D-02, D-14).

WHY: it exists so the tools are testable offline and so failure behaviour is decided once. This
module fails loudly in every case — a missing binary, a non-zero exit, a truncated read — in
deliberate contrast to gh-sync.py's SKIP-and-exit-0 behaviour, which is correct for a one-way
mirror and wrong for a control plane (D-02): a mirror that skips loses a copy, a control plane
that skips leaves the board asserting a state that is not true.

file_at_ref is the only function here that reads repository CONTENT rather than issue, board or
ref metadata.

Every function takes the repository or the board owner/number as an argument. No function reads
git remotes, the current directory, or any environment variable other than FACTORY_GH. Importing
this module has no side effects. It is a library with no command-line entry of its own, so it
never calls factory_cli.run — its share of the C-3 contract is the GhError message shape below,
plus the rule that no function here mutates anything its caller did not ask for, plus the rule
that no function here writes to stdout — callers own stdout for their own payload.
"""
import base64
import binascii
import datetime
import json
import os
import subprocess

import factory_cli
import gh_cost_log
import gh_issues

_LABEL_COLOR = "5319e7"

# T-04 (FEAT-29): text markers that identify a rate-limited gh failure. Detection is on the
# MESSAGE, never the exit code alone — gh exits 1 for many unrelated reasons, and treating every
# exit 1 as budget exhaustion would mislabel ordinary failures (e.g. "could not resolve to a
# Repository").
_RATE_LIMIT_MARKERS = (
    "api rate limit exceeded",
    "was submitted too quickly",
    "rate limit",
)


def _looks_like_rate_limit(stdout, stderr):
    combined = f"{stdout or ''}\n{stderr or ''}".lower()
    return any(marker in combined for marker in _RATE_LIMIT_MARKERS)


def _is_rate_limit_query(argv):
    """True for the exact call this module's own budget lookup issues — the recursion guard
    named in the plan: the budget lookup's own failure must never re-trigger the budget lookup."""
    return len(argv) >= 2 and argv[0] == "api" and argv[1] == "rate_limit"


def _iso_utc(epoch_seconds):
    return datetime.datetime.fromtimestamp(
        epoch_seconds, tz=datetime.timezone.utc
    ).isoformat().replace("+00:00", "Z")


def _rate_limit_budget_error(orig_argv, orig_stdout, orig_stderr):
    """Build (never raise directly — the caller raises it) the GhError for a gh failure whose
    text named a rate limit. Queries `gh api rate_limit` once. If that query itself fails, the
    original error is never swallowed: it survives as this GhError's `stderr`/detail."""
    rate_argv = ["api", "rate_limit"]
    try:
        rl = run_gh(rate_argv, json_out=True)
    except GhError:
        return GhError(
            orig_argv, None, orig_stdout, orig_stderr,
            "gh reported a rate limit and the budget could not be read",
            _value_from_argv(orig_argv),
            "the original gh failure is preserved as detail — re-run after checking gh auth "
            "status and network access",
        )
    resources = rl.get("resources") if isinstance(rl, dict) else None
    graphql = (resources or {}).get("graphql") or {}
    core = (resources or {}).get("core") or {}
    used = graphql.get("used")
    limit = graphql.get("limit")
    reset = graphql.get("reset")
    reset_iso = _iso_utc(reset) if isinstance(reset, (int, float)) else str(reset)
    return GhError(
        orig_argv, None, orig_stdout, orig_stderr,
        "GraphQL budget exhausted",
        f"{used} of {limit} points used, resets at {reset_iso}",
        f"this is the GraphQL budget, not the REST budget — REST currently sits at "
        f"{core.get('used')} of {core.get('limit')}",
    )


def _gh_binary():
    """FACTORY_GH, resolved at CALL time — never cached at import — so a test can set the
    environment variable after import and have the next call see it."""
    return os.environ.get("FACTORY_GH", "gh")


class GhError(Exception):
    """Carries the argv, exit status, captured stdout and captured stderr as attributes for a
    debugger. Its str() is always built with factory_cli.body(what, value, next_step) — never by
    hand — because factory_cli.run prints str(exc) verbatim behind "factory: {tool}: ". `value`
    is always the repository, issue number, field name, option name or gh subcommand; never the
    class name, never a traceback.
    """

    def __init__(self, argv, status, stdout, stderr, what, value, next_step):
        self.argv = argv
        self.status = status
        self.stdout = stdout
        self.stderr = stderr
        super().__init__(factory_cli.body(what, value, next_step))


def _value_from_argv(argv):
    """Best-effort concrete value for a GhError message: the repo, the owner, or the subcommand."""
    if "--repo" in argv:
        i = argv.index("--repo")
        if i + 1 < len(argv):
            return argv[i + 1]
    if "--owner" in argv:
        i = argv.index("--owner")
        if i + 1 < len(argv):
            return argv[i + 1]
    for a in argv:
        if a.startswith("repos/"):
            parts = a.split("/")
            if len(parts) >= 3:
                return f"{parts[1]}/{parts[2]}"
    return " ".join(argv[:2]) if argv else "gh"


def _what_from_argv(argv):
    if len(argv) >= 2:
        return f"gh {argv[0]} {argv[1]} failed"
    if len(argv) == 1:
        return f"gh {argv[0]} failed"
    return "gh failed"


def _first_line(text):
    text = (text or "").strip()
    return text.splitlines()[0] if text else ""


def run_gh(args, json_out=False):
    """Run [gh] + args. Raise GhError when the binary is absent or the exit status is non-zero.

    Never swallows a failure and never returns a default (D-02). stdin is closed so a real gh
    cannot block on an interactive prompt.
    """
    gh = _gh_binary()
    with gh_cost_log.measured(args) as _cost:
        try:
            r = subprocess.run(
                [gh] + list(args), capture_output=True, text=True, stdin=subprocess.DEVNULL,
            )
        except FileNotFoundError:
            raise GhError(
                args, None, "", "",
                "gh not found", gh,
                "install gh, or point FACTORY_GH at its path",
            )
        _cost.returncode = r.returncode
    if r.returncode != 0:
        if not _is_rate_limit_query(list(args)) and _looks_like_rate_limit(r.stdout, r.stderr):
            raise _rate_limit_budget_error(list(args), r.stdout, r.stderr)
        next_step = _first_line(r.stderr) or _first_line(r.stdout) or "no output captured"
        raise GhError(args, r.returncode, r.stdout, r.stderr,
                      _what_from_argv(args), _value_from_argv(args), next_step)
    if json_out:
        return json.loads(r.stdout)
    return r.stdout.strip()


def preflight():
    """Raise GhError telling the operator to run `gh auth login` when auth is broken."""
    try:
        run_gh(["auth", "status"])
    except GhError as e:
        raise GhError(
            e.argv, e.status, e.stdout, e.stderr,
            "gh auth status failed", "gh",
            "run `gh auth login` to authenticate",
        ) from e


def ensure_labels(repo, labels):
    """Create every label the factory needs, idempotently. Propagates a GhError rather than
    swallowing it — a control plane that cannot create its own vocabulary must stop rather than
    fail later at the issue create with a confusing message (D-02)."""
    for label in labels:
        run_gh([
            "label", "create", label, "--repo", repo, "--force",
            "--color", _LABEL_COLOR,
            "--description", "created by the harness factory",
        ])


def create_issue(repo, title, body, labels):
    """Create an issue and return its number, parsed from the created URL."""
    args = ["issue", "create", "--repo", repo, "--title", title, "--body", body]
    for label in labels:
        args += ["--label", label]
    out = run_gh(args)
    tail = out.strip().rsplit("/issues/", 1)
    if len(tail) != 2 or not tail[1].strip().isdigit():
        raise GhError(
            args, None, out, "",
            "gh issue create returned no issue number", repo,
            "output did not contain a /issues/<n> URL",
        )
    return int(tail[1].strip())


def issue_view(repo, number, fields):
    return run_gh(["issue", "view", str(number), "--repo", repo, "--json", ",".join(fields)],
                   json_out=True)


def add_label(repo, number, label):
    run_gh(["issue", "edit", str(number), "--repo", repo, "--add-label", label])


def assign(repo, number, login):
    run_gh(["issue", "edit", str(number), "--repo", repo, "--add-assignee", login])


def project_item_add(owner, number, url):
    out = run_gh(
        ["project", "item-add", str(number), "--owner", owner, "--url", url, "--format", "json"],
        json_out=True,
    )
    return out["id"]


def project_items(owner, number, query=None, limit=500):
    """Return the items list exactly as gh gives it — no reshaping.

    Raises GhError when the response's totalCount exceeds the returned item count: that means
    the read was truncated and work is hidden behind it, which must never be reported as an
    empty column. A missing totalCount raises too — defaulting it to 0 would make this guard
    permanently silent on exactly the response shape it exists to catch.
    """
    args = ["project", "item-list", str(number), "--owner", owner, "--format", "json",
            "--limit", str(limit)]
    if query:
        args += ["--query", query]
    out = run_gh(args, json_out=True)
    items = out.get("items", [])
    total = out.get("totalCount")
    if total is None:
        raise GhError(
            args, None, "", "",
            "project item-list response has no totalCount", f"{owner} project {number}",
            "cannot verify the read was not truncated",
        )
    if total > len(items):
        raise GhError(
            args, None, "", "",
            "project item-list truncated", f"{owner} project {number}: totalCount={total} items={len(items)}",
            "widen --limit or narrow with --query",
        )
    return items


# The single low-cost board-station query (T-01, FEAT-29). Selection is deliberately narrow —
# content's issue/PR number and repository nameWithOwner, plus the named single-select field's
# value — never the full fieldValues connection `gh project item-list` fetches for every item.
# MEASURED 2026-08-19 against board 3 (474 items, commit 6bbd706): one 100-node page cost exactly
# 1 GraphQL point. The driver is this SELECTION, not the node count — widening it is what
# reintroduces the cost `gh project item-list` carries, so do not add fields here.
_STATION_QUERY = """query($owner: String!, $number: Int!, $field: String!, $cursor: String) {
  user(login: $owner) {
    projectV2(number: $number) {
      items(first: 100, after: $cursor) {
        totalCount
        pageInfo { hasNextPage endCursor }
        nodes {
          content {
            ... on Issue { number repository { nameWithOwner } }
            ... on PullRequest { number repository { nameWithOwner } }
          }
          fieldValueByName(name: $field) {
            ... on ProjectV2ItemFieldSingleSelectValue { name }
          }
        }
      }
    }
  }
}
"""


def project_item_stations(owner, number, field_name):
    """Return one dict per board item: {"content": {...} or {}, "station": str or None}.

    ONE targeted GraphQL query, paginated (D-01 sibling): never `gh project item-list`, whose
    full fieldValues connection is what makes the whole-board scan expensive. `content` is {} for
    an item with no issue/PR (never dropped). `station` is None when the item carries no value for
    `field_name`, or when the value shape carries no "name" key (never dropped either).

    Raises GhError, never returns a default, when: any of user/projectV2/items resolves null (an
    organization-owned board resolves user() to null and must fail loudly, not report an empty
    list); totalCount is absent from the first page (never defaulted to 0 — see project_items
    above for the same reasoning); or the accumulated node count falls short of totalCount after
    pagination exhausts (truncated read hidden as an empty-looking board).
    """
    items_out = []
    total = None
    cursor = None
    argv = None
    while True:
        cursor_arg = cursor if cursor is not None else "null"
        argv = ["api", "graphql",
                "-F", "owner=" + owner,
                "-F", "number=" + str(number),
                "-F", "field=" + field_name,
                "-F", "cursor=" + cursor_arg,
                "-f", "query=" + _STATION_QUERY]
        env = run_gh(argv, json_out=True)
        data = env.get("data") if isinstance(env, dict) else None
        user = data.get("user") if isinstance(data, dict) else None
        if user is None:
            raise GhError(argv, None, "", "",
                          "project item stations unreadable",
                          f"{owner} project {number}: user is null",
                          "check the owner login — an organization-owned board resolves user() "
                          "to null")
        project = user.get("projectV2")
        if project is None:
            raise GhError(argv, None, "", "",
                          "project item stations unreadable",
                          f"{owner} project {number}: projectV2 is null",
                          "check the board number")
        items_obj = project.get("items")
        if items_obj is None:
            raise GhError(argv, None, "", "",
                          "project item stations unreadable",
                          f"{owner} project {number}: items is null",
                          "unexpected GraphQL response shape")
        if total is None:
            total = items_obj.get("totalCount")
            if total is None:
                raise GhError(argv, None, "", "",
                              "project item stations response has no totalCount",
                              f"{owner} project {number}",
                              "cannot verify the read was not truncated")
        for node in items_obj.get("nodes", []):
            content = node.get("content")
            if content:
                content_out = {
                    "number": int(content["number"]),
                    "repository": content["repository"]["nameWithOwner"],
                }
            else:
                content_out = {}
            field_value = node.get("fieldValueByName")
            station = field_value["name"] if field_value and "name" in field_value else None
            items_out.append({"content": content_out, "station": station})
        page_info = items_obj.get("pageInfo") or {}
        if page_info.get("hasNextPage"):
            cursor = page_info.get("endCursor")
        else:
            break
    if len(items_out) < total:
        raise GhError(
            argv, None, "", "",
            "project item stations truncated",
            f"{owner} project {number}: totalCount={total} items={len(items_out)}",
            "the paginated read did not reach totalCount",
        )
    return items_out


# The single named-field query, cost 1, replacing the two calls it used to take (D-01):
# `gh project field-list` (102 GraphQL points, fetches every field) and `gh project view`
# (2 points, only for the node id). The inline fragment on ProjectV2Owner is what lets one
# selection cover both a User and an Organization owner — see _project_field_resolve below for
# the branch that then tells them apart. No `first:`/`last:` connection argument anywhere: that
# is what keeps the query from fanning out, which is the entire point of replacing the old pair.
_FIELD_QUERY = """query($owner: String!, $number: Int!, $field: String!) {
  repositoryOwner(login: $owner) {
    __typename
    ... on ProjectV2Owner {
      projectV2(number: $number) {
        id
        field(name: $field) {
          ... on ProjectV2SingleSelectField {
            id
            name
            options { id name }
          }
        }
      }
    }
  }
}
"""


def _project_field_resolve(owner, number, field):
    """Resolve a board's node id, a single-select field's id and its options in ONE GraphQL
    call (D-01). Never cached — called fresh on every invocation, same as the pair it replaces.

    D-03: one diagnosis walk, entered from both the exception path (gh exits non-zero but still
    carries a `data` envelope on stdout — GraphQL's partial-failure shape) and the success path.
    Every raise here carries a real, actionable value (D-03 step e) — never the generic argv[:2]
    fallback `_value_from_argv` would produce for a `-f owner=` argv.
    """
    argv = ["api", "graphql",
            "-f", "query=" + _FIELD_QUERY,
            "-f", "owner=" + owner,
            "-F", "number=" + str(number),
            "-f", "field=" + field]
    try:
        env = run_gh(argv, json_out=True)
    except GhError as e:
        parsed = None
        if e.stdout:
            try:
                parsed = json.loads(e.stdout)
            except ValueError:
                parsed = None
        if isinstance(parsed, dict) and "data" in parsed:
            env = parsed
        else:
            raise GhError(
                e.argv, e.status, e.stdout, e.stderr,
                "gh graphql call failed", owner + " project " + str(number),
                "re-run after checking gh auth status and network access",
            ) from e

    data = env.get("data") or {}
    repo_owner = data.get("repositoryOwner")
    if repo_owner is None:
        # D-02: a login that resolves to nothing, at exit 0, no errors key. Not the org case.
        raise GhError(argv, None, "", "",
                      "project owner not found", owner,
                      "check the owner login")
    if repo_owner.get("__typename") != "User":
        # __typename is read before projectV2: present in both the exit-0 and exit-1 envelope,
        # so the refusal never depends on the org's own board existing.
        raise GhError(argv, None, "", "",
                      "organization-owned board not supported", owner,
                      "run against a user-owned board")
    project = repo_owner.get("projectV2")
    if project is None:
        # D-02: a mistyped board number must never report the organization message.
        raise GhError(argv, None, "", "",
                      "project not found", owner + " project " + str(number),
                      "check the board number")
    field_obj = project.get("field")
    if not field_obj:
        # `not field_obj` catches BOTH None (field name absent) and {} (field exists but is not
        # single-select) — `field_obj is None` alone would miss the empty-dict shape (D-04).
        raise GhError(argv, None, "", "",
                      "project field not found", field,
                      f"field-list for {owner} project {number} does not offer it")
    return {
        "project_id": project["id"],
        "field_id": field_obj["id"],
        "options": [{"id": o["id"], "name": o["name"]} for o in field_obj.get("options", [])],
    }


def project_field_options(owner, number, field):
    resolved = _project_field_resolve(owner, number, field)
    return [o["name"] for o in resolved["options"]]


# ---------------- board lifecycle primitives (T-03, FEAT-33) ----------------
# Six read/write primitives board_lifecycle.py's provision/audit subcommands (T-04, T-05) are
# built on. Every one goes through run_gh, so the fake-binary and rate-limit handling above
# applies unchanged, and every one raises GhError rather than returning a default — the same
# discipline project_item_stations and _project_field_resolve already hold.

# Mirrors _FIELD_QUERY's own repositoryOwner/__typename shape (line 380) exactly, minus the field
# selection — project_resolve does not need a field, only the project's own id and title, but it
# needs the SAME discrimination _project_field_resolve makes: __typename read before projectV2,
# so an org-owned login is refused before a null projectV2 is ever seen, and a genuinely absent
# project (a User whose projectV2(number:) resolves null) is told apart from an unresolvable
# owner.
_PROJECT_RESOLVE_QUERY = """query($owner: String!, $number: Int!) {
  repositoryOwner(login: $owner) {
    __typename
    ... on ProjectV2Owner {
      projectV2(number: $number) { id title }
    }
  }
}
"""


def project_resolve(owner, number):
    """Resolve a user-owned project's node id and title, or return None when the owner resolves
    but that project number does not exist on their account.

    THIS PRIMITIVE EXISTS TO PREVENT A SPECIFIC DISASTER. _project_field_resolve (line 400) raises
    ONE GhError class for FOUR distinct conditions — owner absent, organization-owned, project
    absent, field absent/not-single-select — separated only by a message string, and its field
    case deliberately collapses two shapes (D-04). A caller that infers "there is no project" from
    a field-resolution failure will call project_create and CREATE A DUPLICATE PROJECTS V2 BOARD
    ON THE OPERATOR'S ACCOUNT. This function is the discriminator that removes the need for that
    inference: __typename is read before projectV2, exactly as _project_field_resolve does at
    :439-444, so the refusal never depends on the org's own board existing.

    Returns None — never raises — only for "this owner has no project number N", the normal
    provisioning case. Raises GhError when the owner login does not resolve at all, and raises
    GhError with the organization message when __typename is not User — both are unusable inputs,
    not absent projects.
    """
    argv = ["api", "graphql",
            "-f", "query=" + _PROJECT_RESOLVE_QUERY,
            "-f", "owner=" + owner,
            "-F", "number=" + str(number)]
    try:
        env = run_gh(argv, json_out=True)
    except GhError as e:
        parsed = None
        if e.stdout:
            try:
                parsed = json.loads(e.stdout)
            except ValueError:
                parsed = None
        if isinstance(parsed, dict) and "data" in parsed:
            env = parsed
        else:
            raise GhError(
                e.argv, e.status, e.stdout, e.stderr,
                "gh graphql call failed", owner,
                "re-run after checking gh auth status and network access",
            ) from e
    data = env.get("data") or {}
    repo_owner = data.get("repositoryOwner")
    if repo_owner is None:
        raise GhError(argv, None, "", "",
                      "project owner not found", owner,
                      "check the owner login")
    if repo_owner.get("__typename") != "User":
        raise GhError(argv, None, "", "",
                      "organization-owned board not supported", owner,
                      "run against a user-owned board")
    project = repo_owner.get("projectV2")
    if project is None:
        return None
    return {"id": project["id"], "title": project["title"]}


_OWNER_ID_QUERY = """query($login: String!) { user(login: $login) { id } }
"""

_CREATE_PROJECT_MUTATION = """mutation($ownerId: ID!, $title: String!) {
  createProjectV2(input: {ownerId: $ownerId, title: $title}) {
    projectV2 { id number }
  }
}
"""


def project_create(owner, title):
    """Create a new user-owned ProjectV2 board and return {"id": ..., "number": ...}.

    Resolves the owner's node id first, then sends createProjectV2. Raises GhError naming the
    owner and title when createProjectV2.projectV2 resolves null. Callers MUST have already
    established the project does not exist via project_resolve returning None — this function
    performs no such check itself, so calling it on a whim duplicates a board.
    """
    id_argv = ["api", "graphql", "-f", "query=" + _OWNER_ID_QUERY, "-f", "login=" + owner]
    env = run_gh(id_argv, json_out=True)
    data = env.get("data") or {}
    user = data.get("user")
    if user is None:
        raise GhError(id_argv, None, "", "",
                      "project owner not found", owner,
                      "check the owner login")
    owner_id = user["id"]
    create_argv = ["api", "graphql", "-f", "query=" + _CREATE_PROJECT_MUTATION,
                   "-f", "ownerId=" + owner_id, "-f", "title=" + title]
    env2 = run_gh(create_argv, json_out=True)
    data2 = env2.get("data") or {}
    created = data2.get("createProjectV2")
    project = created.get("projectV2") if isinstance(created, dict) else None
    if not project:
        raise GhError(create_argv, None, "", "",
                      "project not created", f"{owner}: {title}",
                      "createProjectV2 returned no projectV2")
    return {"id": project["id"], "number": project["number"]}


_REPO_ID_QUERY = """query($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) { id }
}
"""

_LINK_REPOSITORY_MUTATION = """mutation($projectId: ID!, $repositoryId: ID!) {
  linkProjectV2ToRepository(input: {projectId: $projectId, repositoryId: $repositoryId}) {
    repository { id }
  }
}
"""


def project_link_repository(project_id, repo):
    """Link `repo` ("owner/name") to a project. Returns None.

    Resolves the repository's node id first, then sends linkProjectV2ToRepository. An
    already-linked response — the mutation fails naming the link as already existing — is
    treated as SUCCESS, not an error, the same measured-conflict shape create_ref already accepts
    for a duplicate ref (line 639).
    """
    owner, _, name = repo.partition("/")
    id_argv = ["api", "graphql", "-f", "query=" + _REPO_ID_QUERY,
               "-f", "owner=" + owner, "-f", "name=" + name]
    env = run_gh(id_argv, json_out=True)
    data = env.get("data") or {}
    repository = data.get("repository")
    if repository is None:
        raise GhError(id_argv, None, "", "",
                      "repository not found", repo,
                      "check the repository name")
    repo_id = repository["id"]
    link_argv = ["api", "graphql", "-f", "query=" + _LINK_REPOSITORY_MUTATION,
                 "-f", "projectId=" + project_id, "-f", "repositoryId=" + repo_id]
    try:
        run_gh(link_argv, json_out=True)
    except GhError as e:
        combined = f"{e.stdout or ''}\n{e.stderr or ''}".lower()
        if "already" in combined and "link" in combined:
            return None
        raise
    return None


def _options_literal(option_names):
    """Render option_names as a GraphQL list-of-objects LITERAL — never as a variable, because
    gh api graphql's -f/-F flags have no syntax for an array of input objects. Each entry sends
    name, color: GRAY and description: "" ALL THREE explicitly — GitHub rejects the mutation when
    color or description is omitted. json.dumps quotes and escapes each name safely."""
    parts = [
        "{name: " + json.dumps(name) + ', color: GRAY, description: ""}'
        for name in option_names
    ]
    return "[" + ", ".join(parts) + "]"


def project_single_select_create(project_id, field_name, option_names):
    """Create a new single-select field on a project with exactly `option_names`, in order.
    Returns the new field's node id.

    Mutation createProjectV2Field with input {projectId, dataType: SINGLE_SELECT, name,
    singleSelectOptions}. Raises GhError naming field_name when createProjectV2Field returns no
    projectV2Field.
    """
    query = ("""mutation($projectId: ID!, $name: String!) {
  createProjectV2Field(input: {
    projectId: $projectId, dataType: SINGLE_SELECT, name: $name,
    singleSelectOptions: %s
  }) {
    projectV2Field { ... on ProjectV2SingleSelectField { id } }
  }
}
""" % _options_literal(option_names))
    argv = ["api", "graphql", "-f", "query=" + query,
            "-f", "projectId=" + project_id, "-f", "name=" + field_name]
    env = run_gh(argv, json_out=True)
    data = env.get("data") or {}
    created = data.get("createProjectV2Field")
    field = created.get("projectV2Field") if isinstance(created, dict) else None
    if not field:
        raise GhError(argv, None, "", "",
                      "project field not created", field_name,
                      "createProjectV2Field returned no projectV2Field")
    return field["id"]


def project_single_select_extend(project_id, field_id, option_names):
    """Send `option_names` — the FULL desired option list — as the new option set for an
    existing single-select field. Returns None.

    THE MUTATION IS A REPLACEMENT, NOT AN APPEND (D-plan T-03). updateProjectV2Field's
    singleSelectOptions input REPLACES the field's entire option set. This function does not
    compute the desired list — it sends exactly what it is given, in the order it is given.
    Callers MUST pass every existing option first, with its existing name preserved, followed by
    the additions; computing that union belongs to T-04, where the existing options have already
    been read. Getting this wrong — passing only the new options — DELETES every option the
    operator already had on the board.
    """
    query = ("""mutation($fieldId: ID!) {
  updateProjectV2Field(input: {
    fieldId: $fieldId,
    singleSelectOptions: %s
  }) {
    projectV2Field { ... on ProjectV2SingleSelectField { id } }
  }
}
""" % _options_literal(option_names))
    argv = ["api", "graphql", "-f", "query=" + query, "-f", "fieldId=" + field_id]
    env = run_gh(argv, json_out=True)
    data = env.get("data") or {}
    updated = data.get("updateProjectV2Field")
    field = updated.get("projectV2Field") if isinstance(updated, dict) else None
    if not field:
        raise GhError(argv, None, "", "",
                      "project field not updated", f"{project_id} field {field_id}",
                      "updateProjectV2Field returned no projectV2Field")
    return None


_WORKFLOWS_QUERY = """query($owner: String!, $number: Int!) {
  user(login: $owner) {
    projectV2(number: $number) {
      workflows(first: 50) { nodes { name enabled number } }
    }
  }
}
"""


def project_workflows(owner, number):
    """Return one dict per project workflow: {"name": str, "enabled": bool, "number": int}.

    Measured live 2026-08-22: this query works and returns exactly those three fields.
    ProjectV2Workflow exposes NEITHER trigger NOR action, so a caller can only match a workflow by
    NAME — there is no ProjectV2 mutation that creates or enables a workflow (all 31 mutations
    include deleteProjectV2Workflow and nothing that creates one).

    Raises GhError — never returns an empty list — when user, projectV2 or workflows resolves
    null: "no workflows" and "cannot see the project" are two different findings, and collapsing
    them would report an inaccessible project as a clean board.
    """
    argv = ["api", "graphql", "-f", "query=" + _WORKFLOWS_QUERY,
            "-f", "owner=" + owner, "-F", "number=" + str(number)]
    env = run_gh(argv, json_out=True)
    data = env.get("data") or {}
    user = data.get("user")
    if user is None:
        raise GhError(argv, None, "", "",
                      "project owner not found", owner,
                      "check the owner login")
    project = user.get("projectV2")
    if project is None:
        raise GhError(argv, None, "", "",
                      "project not found", owner + " project " + str(number),
                      "check the board number")
    workflows = project.get("workflows")
    if workflows is None:
        raise GhError(argv, None, "", "",
                      "project workflows unreadable", owner + " project " + str(number),
                      "unexpected GraphQL response shape")
    return [
        {"name": n["name"], "enabled": n["enabled"], "number": n["number"]}
        for n in workflows.get("nodes", [])
    ]


# The single targeted-lookup query, cost 1, replacing a whole-board `project item-list` scan
# (D-01). Scoped to one repository and one issue number with NO state filter — a closed issue
# still resolves, which is the property decompose's recovery path depends on (REQ-02).
_ISSUE_ITEM_QUERY = """query($owner: String!, $name: String!, $number: Int!) {
  repository(owner: $owner, name: $name) {
    issue(number: $number) {
      projectItems(first: 100) {
        totalCount
        nodes { id project { number } }
      }
    }
  }
}
"""


def issue_board_item_id(repo, number, board_number):
    """The board item id for issue `number` of `repo` ("owner/name") on project `board_number`,
    or None when the issue carries no item on that board. One targeted, repository-scoped
    GraphQL call replaces a whole-board `project item-list` read (D-01).

    THE DISCRIMINATION IS THE POINT (D-03): absence is CORRECT and returns None — an issue
    number that does not exist, or a recognised, non-truncated item list with no node on
    `board_number`. Only an unrecognised or truncated response shape raises GhError. A caller
    that collapses "issue explicitly null" and "issue key absent" into the same None reads an
    unrecognised shape as go-add-it and re-adds a board item that already exists — the exact
    defect this function exists to prevent — so those two are told apart by explicit
    key-presence tests, never by reading `.get("issue")` and treating None as "not there".

    Never scoped by issue state: no `is:open`, no `query=` filter of any kind. Never cached.
    """
    parts = repo.split("/")
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise GhError(
            [], None, "", "",
            "malformed repository", repo,
            "expected owner/name",
        )
    owner, name = parts
    argv = ["api", "graphql",
            "-f", "query=" + _ISSUE_ITEM_QUERY,
            "-f", "owner=" + owner,
            "-f", "name=" + name,
            "-F", "number=" + str(number)]
    try:
        env = run_gh(argv, json_out=True)
    except GhError as e:
        parsed = None
        if e.stdout:
            try:
                parsed = json.loads(e.stdout)
            except ValueError:
                parsed = None
        if isinstance(parsed, dict) and "data" in parsed:
            env = parsed
        else:
            raise GhError(
                e.argv, e.status, e.stdout, e.stderr,
                "gh graphql call failed", repo + " issue " + str(number),
                "re-run after checking gh auth status and network access",
            ) from e

    def _generic():
        return GhError(
            argv, None, "", "",
            "gh graphql call failed", repo + " issue " + str(number),
            "re-run after checking gh auth status and network access",
        )

    if not isinstance(env, dict) or "data" not in env or not isinstance(env["data"], dict):
        raise _generic()
    data = env["data"]
    if "repository" not in data:
        raise _generic()
    repository = data["repository"]
    if repository is not None and not isinstance(repository, dict):
        raise _generic()
    if repository is None:
        raise GhError(argv, None, "", "",
                      "repository not found", repo,
                      "check the repository name")
    if "issue" not in repository:
        # Absence of the key is an unrecognised shape. An explicit null (below) is a real
        # answer — the issue does not exist — and is DISTINCT from this case.
        raise _generic()
    issue = repository["issue"]
    if issue is None:
        return None
    if not isinstance(issue, dict) or "projectItems" not in issue \
            or not isinstance(issue["projectItems"], dict):
        raise _generic()
    project_items_obj = issue["projectItems"]
    if "nodes" not in project_items_obj or not isinstance(project_items_obj["nodes"], list):
        raise _generic()
    nodes = project_items_obj["nodes"]
    if "totalCount" not in project_items_obj:
        # Do NOT default to 0 — that would make this guard permanently silent on exactly the
        # response shape it exists to catch.
        raise GhError(argv, None, "", "",
                      "issue projectItems missing totalCount", repo + " issue " + str(number),
                      "cannot verify the read was not truncated")
    total = project_items_obj["totalCount"]
    if not isinstance(total, int):
        raise GhError(argv, None, "", "",
                      "issue projectItems totalCount is not an integer",
                      repo + " issue " + str(number) + ": totalCount=" + repr(total),
                      "unexpected GraphQL response shape")
    if total > len(nodes):
        raise GhError(
            argv, None, "", "",
            "issue projectItems truncated",
            f"{repo} issue {number}: totalCount={total} nodes={len(nodes)}",
            "the issue is on more projects than this query returned — widen the query",
        )
    for node in nodes:
        if not isinstance(node, dict) or "id" not in node \
                or not isinstance(node.get("project"), dict) or "number" not in node["project"]:
            raise GhError(argv, None, "", "",
                          "issue projectItems node has unrecognised shape",
                          repo + " issue " + str(number),
                          "unexpected GraphQL response shape")
    for node in nodes:
        if node["project"]["number"] == board_number:
            return node["id"]
    return None


def default_branch_sha(repo, branch):
    return run_gh(["api", f"repos/{repo}/git/ref/heads/{branch}", "--jq", ".object.sha"]).strip()


def file_at_ref(repo, path, ref):
    """Read one file's content from `repo` (owner/name) at `path` (repository-relative, no
    leading slash) as it exists at `ref` (a branch name). Returns the decoded text and parses
    nothing else — JSON handling belongs to the caller. Hits the REST contents endpoint with
    `ref` as a query parameter and asks gh for the `content` field alone via --jq, never the
    whole object.

    Every failure raises GhError, never a sentinel: repo not found, path not found at that ref,
    ref not found, unauthenticated gh, and a `content` field that is absent or does not
    base64-decode. A caller must never mistake "not there" for "empty file" (D-02).
    """
    argv = ["api", f"repos/{repo}/contents/{path}?ref={ref}", "--jq", ".content"]
    value = f"{repo} {path}@{ref}"
    try:
        raw = run_gh(argv)
    except GhError as e:
        raise GhError(
            e.argv, e.status, e.stdout, e.stderr,
            "gh api contents failed", value,
            "check the repository, path and ref",
        ) from e
    if not raw or raw == "null":
        raise GhError(
            argv, None, raw, "",
            "file content missing from response", value,
            "gh returned no content field",
        )
    try:
        decoded = base64.b64decode("".join(raw.split()), validate=True)
    except (binascii.Error, ValueError):
        raise GhError(
            argv, None, raw, "",
            "file content could not be decoded", value,
            "gh returned invalid base64",
        )
    return decoded.decode("utf-8")


def create_ref(repo, ref, sha):
    """THE ATOMIC PRIMITIVE. Return True on success. Return False — never raise — only for the
    measured conflict: exit non-zero, "422" AND "already exists" both present (case-insensitive)
    across the captured stdout+stderr. Any other non-zero exit raises, because a False there
    would report a lost race that did not happen and the caller would skip live work forever.
    """
    args = ["api", "-X", "POST", f"repos/{repo}/git/refs", "-f", f"ref={ref}", "-f", f"sha={sha}"]
    try:
        run_gh(args)
        return True
    except GhError as e:
        combined = f"{e.stdout or ''}\n{e.stderr or ''}".lower()
        if "422" in combined and "already exists" in combined:
            return False
        raise


def delete_ref(repo, ref):
    """The release path for an abandoned claim. Not called by any tool in this increment."""
    name = ref[len("refs/heads/"):] if ref.startswith("refs/heads/") else ref
    run_gh(["api", "-X", "DELETE", f"repos/{repo}/git/refs/heads/{name}"])


def project_field_set(owner, number, item_id, field, option):
    resolved = _project_field_resolve(owner, number, field)
    option_id = None
    for o in resolved["options"]:
        if o["name"] == option:
            option_id = o["id"]
            break
    if option_id is None:
        raise GhError(
            [], None, "", "",
            "project field option not found", option,
            f"field {field} on {owner} project {number} does not offer it",
        )
    # `item-edit --project-id` takes the GraphQL node id (PVT_kwHO...), never the board NUMBER
    # that every other `gh project` subcommand accepts — measured live: --project-id 4 raises
    # "Could not resolve to a node with the global id of '4'". The id comes from the same single
    # query, above, that resolved the field and option ids — there is no second read.
    run_gh([
        "project", "item-edit",
        "--id", item_id,
        "--project-id", resolved["project_id"],
        "--field-id", resolved["field_id"],
        "--single-select-option-id", option_id,
    ])


# ---------------- the three edge functions (D-14) ----------------
# Each is one line: build the argv with gh_issues' builder, run it through THIS module's run_gh.
# Never through gh_issues.gh_bin() — that reads GH_SYNC_GH, not FACTORY_GH, and a call routed
# through it would silently escape the injected test binary.

def internal_id(repo, num):
    """The internal REST integer id — never the GraphQL node id `issue view` returns. Both edge
    endpoints below take this id, never the issue number (the trap gh_issues.py documents)."""
    return int(run_gh(gh_issues.internal_id_args(repo, num)).strip())


def attach_sub_issue(repo, parent_num, child_id):
    run_gh(gh_issues.attach_sub_issue_args(repo, parent_num, child_id))


def blocked_by(repo, num, blocker_id):
    run_gh(gh_issues.blocked_by_args(repo, num, blocker_id))
