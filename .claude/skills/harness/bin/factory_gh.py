"""factory_gh.py — the single seam every factory tool talks to GitHub through (D-02, D-14).

WHY: it exists so the tools are testable offline and so failure behaviour is decided once. This
module fails loudly in every case — a missing binary, a non-zero exit, a truncated read — in
deliberate contrast to gh-sync.py's SKIP-and-exit-0 behaviour, which is correct for a one-way
mirror and wrong for a control plane (D-02): a mirror that skips loses a copy, a control plane
that skips leaves the board asserting a state that is not true.

Every function takes the repository or the board owner/number as an argument. No function reads
git remotes, the current directory, or any environment variable other than FACTORY_GH. Importing
this module has no side effects. It is a library with no command-line entry of its own, so it
never calls factory_cli.run — its share of the C-3 contract is the GhError message shape below,
plus the rule that no function here mutates anything its caller did not ask for, plus the rule
that no function here writes to stdout — callers own stdout for their own payload.
"""
import json
import os
import subprocess

import factory_cli
import gh_issues

_LABEL_COLOR = "5319e7"


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
    if r.returncode != 0:
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


def default_branch_sha(repo, branch):
    return run_gh(["api", f"repos/{repo}/git/ref/heads/{branch}", "--jq", ".object.sha"]).strip()


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
