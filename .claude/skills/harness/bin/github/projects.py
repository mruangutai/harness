"""github/projects.py — Projects v2 board calls: items, stations, fields, workflows and project
setup, run through github.transport (D-02, D-14)."""
import json

import artifact_accessors
from github import transport


def project_item_add(owner, number, url):
    out = transport.run_gh(
        ["project", "item-add", str(number), "--owner", owner, "--url", url, "--format", "json"],
        json_out=True,
    )
    return out["id"]


def project_items(owner, number, query=None, limit=500):
    """Return the items list exactly as gh gives it — no reshaping.

    Raises transport.GhError when the response's totalCount exceeds the returned item count: that means
    the read was truncated and work is hidden behind it, which must never be reported as an
    empty column. A missing totalCount raises too — defaulting it to 0 would make this guard
    permanently silent on exactly the response shape it exists to catch.
    """
    args = ["project", "item-list", str(number), "--owner", owner, "--format", "json",
            "--limit", str(limit)]
    if query:
        args += ["--query", query]
    out = transport.run_gh(args, json_out=True)
    items = out.get("items", [])
    total = out.get("totalCount")
    if total is None:
        raise transport.GhError(
            args, None, "", "",
            "project item-list response has no totalCount", f"{owner} project {number}",
            "cannot verify the read was not truncated",
        )
    if total > len(items):
        raise transport.GhError(
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

    Raises transport.GhError, never returns a default, when: any of user/projectV2/items resolves null (an
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
        env = transport.run_gh(argv, json_out=True)
        data = env.get("data") if isinstance(env, dict) else None
        user = data.get("user") if isinstance(data, dict) else None
        if user is None:
            raise transport.GhError(argv, None, "", "",
                          "project item stations unreadable",
                          f"{owner} project {number}: user is null",
                          "check the owner login — an organization-owned board resolves user() "
                          "to null")
        project = user.get("projectV2")
        if project is None:
            raise transport.GhError(argv, None, "", "",
                          "project item stations unreadable",
                          f"{owner} project {number}: projectV2 is null",
                          "check the board number")
        items_obj = project.get("items")
        if items_obj is None:
            raise transport.GhError(argv, None, "", "",
                          "project item stations unreadable",
                          f"{owner} project {number}: items is null",
                          "unexpected GraphQL response shape")
        if total is None:
            total = items_obj.get("totalCount")
            if total is None:
                raise transport.GhError(argv, None, "", "",
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
        raise transport.GhError(
            argv, None, "", "",
            "project item stations truncated",
            f"{owner} project {number}: totalCount={total} items={len(items_out)}",
            "the paginated read did not reach totalCount",
        )
    return items_out


# The BY-ISSUE station read (issue #1541). `project_item_stations` above reads the WHOLE board,
# and every caller but one already knows the issue numbers it cares about, so the whole-board
# read made cost scale with lifetime board history instead of with work in flight.
#
# MEASURED 2026-09-09, board 3: 918 items, `items(first: 100)` is at GitHub's ceiling, so the
# read took 10 SEQUENTIAL `gh` processes at ~0.8-1.1s each — 11.25s of check-state.py's 14.3s,
# paid on every pre-commit run, against 14 non-terminal features carrying zero mirrored issues.
# The board had 474 items three weeks earlier: this is a cost that grows with history, because a
# card stays on the board after its issue closes.
#
# The old comment at _STATION_QUERY says "the driver is this SELECTION, not the node count".
# That is true of the GraphQL POINT budget and false of wall clock, where the driver is page
# count times process spawn. Both costs are real; this function is the one that fixes latency.
#
# `projectItems(first: 20)`: an issue sits on few boards, and `hasNextPage` REFUSES rather than
# silently missing the board we were asked about — the same posture as the truncation guard above.
_ISSUE_STATION_ALIAS = """  i%(num)d: issue(number: %(num)d) {
    number
    projectItems(first: 20) {
      pageInfo { hasNextPage }
      nodes {
        project { number }
        fieldValueByName(name: $field) {
          ... on ProjectV2ItemFieldSingleSelectValue { name }
        }
      }
    }
  }"""

# One request per this many issues. GitHub caps a GraphQL document's complexity, not its alias
# count, and 50 aliases at 20 project items each stays far inside it. The batch exists so the
# call count grows with in-flight work and does so 50x more slowly than the issue count.
ISSUE_STATION_BATCH = 50


def issue_stations(repo, project_number, field_name, numbers):
    """Return {issue number: station or None} for those `numbers` that are ON `project_number`.

    The by-issue counterpart of `project_item_stations`, and deliberately the same output
    vocabulary as `github.board.board_stations` consumes:

    - a number ABSENT from the result is not on that board;
    - a number present with None is on the board with no value for `field_name`.

    Those are two different findings and neither is a default (D-02). An issue that does not
    exist, or that GraphQL resolves to null, is absent — not an error: a feature can record an
    issue number whose card was never added, and the caller reports that as its own finding.

    NO NETWORK CALL IS MADE FOR AN EMPTY `numbers`. That is not an optimisation detail, it is
    the invariant issue #1541 turns on: a checkout with nothing in flight pays nothing.

    Raises transport.GhError, never returns a partial, when `repository` resolves null (a bad repo name
    must fail loudly rather than report every card missing) or when an issue is on more project
    boards than one page holds.
    """
    if "/" not in repo:
        raise transport.GhError(["api", "graphql"], None, "", "",
                      "issue stations unreadable", repo,
                      "repo must be owner/name")
    owner, name = repo.split("/", 1)
    wanted = sorted({int(n) for n in numbers})
    out = {}
    for start in range(0, len(wanted), ISSUE_STATION_BATCH):
        chunk = wanted[start:start + ISSUE_STATION_BATCH]
        aliases = "\n".join(_ISSUE_STATION_ALIAS % {"num": n} for n in chunk)
        query = ("query($owner: String!, $name: String!, $field: String!) {\n"
                 "  repository(owner: $owner, name: $name) {\n"
                 + aliases + "\n  }\n}\n")
        argv = ["api", "graphql",
                "-F", "owner=" + owner,
                "-F", "name=" + name,
                "-F", "field=" + field_name,
                "-f", "query=" + query]
        env = transport.run_gh(argv, json_out=True)
        data = env.get("data") if isinstance(env, dict) else None
        repository = data.get("repository") if isinstance(data, dict) else None
        if repository is None:
            raise transport.GhError(argv, None, "", "",
                          "issue stations unreadable",
                          f"{repo}: repository is null",
                          "check the repository name — a null here would otherwise read as "
                          "every card being off the board")
        for num in chunk:
            node = repository.get("i%d" % num)
            if node is None:
                continue
            items = node.get("projectItems") or {}
            if (items.get("pageInfo") or {}).get("hasNextPage"):
                raise transport.GhError(argv, None, "", "",
                              "issue project items truncated",
                              f"{repo}#{num}",
                              "the issue is on more boards than one page holds, so the "
                              "board under check may not have been read")
            for item in items.get("nodes") or []:
                if (item.get("project") or {}).get("number") != project_number:
                    continue
                field_value = item.get("fieldValueByName")
                out[num] = (field_value["name"]
                            if field_value and "name" in field_value else None)
                break
    return out


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
    fallback `transport._value_from_argv` would produce for a `-f owner=` argv.
    """
    argv = ["api", "graphql",
            "-f", "query=" + _FIELD_QUERY,
            "-f", "owner=" + owner,
            "-F", "number=" + str(number),
            "-f", "field=" + field]
    try:
        env = transport.run_gh(argv, json_out=True)
    except transport.GhError as e:
        parsed = None
        if e.stdout:
            try:
                parsed = artifact_accessors.parse_gh_json(
                    e.stdout, "GitHub project field response")
            except artifact_accessors.ArtifactAccessError:
                parsed = None
        if isinstance(parsed, dict) and "data" in parsed:
            env = parsed
        else:
            raise transport.GhError(
                e.argv, e.status, e.stdout, e.stderr,
                "gh graphql call failed", owner + " project " + str(number),
                "re-run after checking gh auth status and network access",
            ) from e

    data = env.get("data") or {}
    repo_owner = data.get("repositoryOwner")
    if repo_owner is None:
        # D-02: a login that resolves to nothing, at exit 0, no errors key. Not the org case.
        raise transport.GhError(argv, None, "", "",
                      "project owner not found", owner,
                      "check the owner login")
    if repo_owner.get("__typename") != "User":
        # __typename is read before projectV2: present in both the exit-0 and exit-1 envelope,
        # so the refusal never depends on the org's own board existing.
        raise transport.GhError(argv, None, "", "",
                      "organization-owned board not supported", owner,
                      "run against a user-owned board")
    project = repo_owner.get("projectV2")
    if project is None:
        # D-02: a mistyped board number must never report the organization message.
        raise transport.GhError(argv, None, "", "",
                      "project not found", owner + " project " + str(number),
                      "check the board number")
    field_obj = project.get("field")
    if not field_obj:
        # `not field_obj` catches BOTH None (field name absent) and {} (field exists but is not
        # single-select) — `field_obj is None` alone would miss the empty-dict shape (D-04).
        raise transport.GhError(argv, None, "", "",
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
# built on. Every one goes through transport.run_gh, so the fake-binary and rate-limit handling above
# applies unchanged, and every one raises transport.GhError rather than returning a default — the same
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
    ONE transport.GhError class for FOUR distinct conditions — owner absent, organization-owned, project
    absent, field absent/not-single-select — separated only by a message string, and its field
    case deliberately collapses two shapes (D-04). A caller that infers "there is no project" from
    a field-resolution failure will call project_create and CREATE A DUPLICATE PROJECTS V2 BOARD
    ON THE OPERATOR'S ACCOUNT. This function is the discriminator that removes the need for that
    inference: __typename is read before projectV2, exactly as _project_field_resolve does at
    :439-444, so the refusal never depends on the org's own board existing.

    Returns None — never raises — only for "this owner has no project number N", the normal
    provisioning case. Raises transport.GhError when the owner login does not resolve at all, and raises
    transport.GhError with the organization message when __typename is not User — both are unusable inputs,
    not absent projects.
    """
    argv = ["api", "graphql",
            "-f", "query=" + _PROJECT_RESOLVE_QUERY,
            "-f", "owner=" + owner,
            "-F", "number=" + str(number)]
    try:
        env = transport.run_gh(argv, json_out=True)
    except transport.GhError as e:
        parsed = None
        if e.stdout:
            try:
                parsed = artifact_accessors.parse_gh_json(
                    e.stdout, "GitHub project response")
            except artifact_accessors.ArtifactAccessError:
                parsed = None
        if isinstance(parsed, dict) and "data" in parsed:
            env = parsed
        else:
            raise transport.GhError(
                e.argv, e.status, e.stdout, e.stderr,
                "gh graphql call failed", owner,
                "re-run after checking gh auth status and network access",
            ) from e
    data = env.get("data") or {}
    repo_owner = data.get("repositoryOwner")
    if repo_owner is None:
        raise transport.GhError(argv, None, "", "",
                      "project owner not found", owner,
                      "check the owner login")
    if repo_owner.get("__typename") != "User":
        raise transport.GhError(argv, None, "", "",
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

    Resolves the owner's node id first, then sends createProjectV2. Raises transport.GhError naming the
    owner and title when createProjectV2.projectV2 resolves null. Callers MUST have already
    established the project does not exist via project_resolve returning None — this function
    performs no such check itself, so calling it on a whim duplicates a board.
    """
    id_argv = ["api", "graphql", "-f", "query=" + _OWNER_ID_QUERY, "-f", "login=" + owner]
    env = transport.run_gh(id_argv, json_out=True)
    data = env.get("data") or {}
    user = data.get("user")
    if user is None:
        raise transport.GhError(id_argv, None, "", "",
                      "project owner not found", owner,
                      "check the owner login")
    owner_id = user["id"]
    create_argv = ["api", "graphql", "-f", "query=" + _CREATE_PROJECT_MUTATION,
                   "-f", "ownerId=" + owner_id, "-f", "title=" + title]
    env2 = transport.run_gh(create_argv, json_out=True)
    data2 = env2.get("data") or {}
    created = data2.get("createProjectV2")
    project = created.get("projectV2") if isinstance(created, dict) else None
    if not project:
        raise transport.GhError(create_argv, None, "", "",
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
    env = transport.run_gh(id_argv, json_out=True)
    data = env.get("data") or {}
    repository = data.get("repository")
    if repository is None:
        raise transport.GhError(id_argv, None, "", "",
                      "repository not found", repo,
                      "check the repository name")
    repo_id = repository["id"]
    link_argv = ["api", "graphql", "-f", "query=" + _LINK_REPOSITORY_MUTATION,
                 "-f", "projectId=" + project_id, "-f", "repositoryId=" + repo_id]
    try:
        transport.run_gh(link_argv, json_out=True)
    except transport.GhError as e:
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
    singleSelectOptions}. Raises transport.GhError naming field_name when createProjectV2Field returns no
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
    env = transport.run_gh(argv, json_out=True)
    data = env.get("data") or {}
    created = data.get("createProjectV2Field")
    field = created.get("projectV2Field") if isinstance(created, dict) else None
    if not field:
        raise transport.GhError(argv, None, "", "",
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
    env = transport.run_gh(argv, json_out=True)
    data = env.get("data") or {}
    updated = data.get("updateProjectV2Field")
    field = updated.get("projectV2Field") if isinstance(updated, dict) else None
    if not field:
        raise transport.GhError(argv, None, "", "",
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

    Raises transport.GhError — never returns an empty list — when user, projectV2 or workflows resolves
    null: "no workflows" and "cannot see the project" are two different findings, and collapsing
    them would report an inaccessible project as a clean board.
    """
    argv = ["api", "graphql", "-f", "query=" + _WORKFLOWS_QUERY,
            "-f", "owner=" + owner, "-F", "number=" + str(number)]
    env = transport.run_gh(argv, json_out=True)
    data = env.get("data") or {}
    user = data.get("user")
    if user is None:
        raise transport.GhError(argv, None, "", "",
                      "project owner not found", owner,
                      "check the owner login")
    project = user.get("projectV2")
    if project is None:
        raise transport.GhError(argv, None, "", "",
                      "project not found", owner + " project " + str(number),
                      "check the board number")
    workflows = project.get("workflows")
    if workflows is None:
        raise transport.GhError(argv, None, "", "",
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
    `board_number`. Only an unrecognised or truncated response shape raises transport.GhError. A caller
    that collapses "issue explicitly null" and "issue key absent" into the same None reads an
    unrecognised shape as go-add-it and re-adds a board item that already exists — the exact
    defect this function exists to prevent — so those two are told apart by explicit
    key-presence tests, never by reading `.get("issue")` and treating None as "not there".

    Never scoped by issue state: no `is:open`, no `query=` filter of any kind. Never cached.
    """
    parts = repo.split("/")
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise transport.GhError(
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
        env = transport.run_gh(argv, json_out=True)
    except transport.GhError as e:
        parsed = None
        if e.stdout:
            try:
                parsed = artifact_accessors.parse_gh_json(
                    e.stdout, "GitHub issue board response")
            except artifact_accessors.ArtifactAccessError:
                parsed = None
        if isinstance(parsed, dict) and "data" in parsed:
            env = parsed
        else:
            raise transport.GhError(
                e.argv, e.status, e.stdout, e.stderr,
                "gh graphql call failed", repo + " issue " + str(number),
                "re-run after checking gh auth status and network access",
            ) from e

    def _generic():
        return transport.GhError(
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
        raise transport.GhError(argv, None, "", "",
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
        raise transport.GhError(argv, None, "", "",
                      "issue projectItems missing totalCount", repo + " issue " + str(number),
                      "cannot verify the read was not truncated")
    total = project_items_obj["totalCount"]
    if not isinstance(total, int):
        raise transport.GhError(argv, None, "", "",
                      "issue projectItems totalCount is not an integer",
                      repo + " issue " + str(number) + ": totalCount=" + repr(total),
                      "unexpected GraphQL response shape")
    if total > len(nodes):
        raise transport.GhError(
            argv, None, "", "",
            "issue projectItems truncated",
            f"{repo} issue {number}: totalCount={total} nodes={len(nodes)}",
            "the issue is on more projects than this query returned — widen the query",
        )
    for node in nodes:
        if not isinstance(node, dict) or "id" not in node \
                or not isinstance(node.get("project"), dict) or "number" not in node["project"]:
            raise transport.GhError(argv, None, "", "",
                          "issue projectItems node has unrecognised shape",
                          repo + " issue " + str(number),
                          "unexpected GraphQL response shape")
    for node in nodes:
        if node["project"]["number"] == board_number:
            return node["id"]
    return None


def project_field_set(owner, number, item_id, field, option):
    resolved = _project_field_resolve(owner, number, field)
    option_id = None
    for o in resolved["options"]:
        if o["name"] == option:
            option_id = o["id"]
            break
    if option_id is None:
        raise transport.GhError(
            [], None, "", "",
            "project field option not found", option,
            f"field {field} on {owner} project {number} does not offer it",
        )
    # `item-edit --project-id` takes the GraphQL node id (PVT_kwHO...), never the board NUMBER
    # that every other `gh project` subcommand accepts — measured live: --project-id 4 raises
    # "Could not resolve to a node with the global id of '4'". The id comes from the same single
    # query, above, that resolved the field and option ids — there is no second read.
    transport.run_gh([
        "project", "item-edit",
        "--id", item_id,
        "--project-id", resolved["project_id"],
        "--field-id", resolved["field_id"],
        "--single-select-option-id", option_id,
    ])
