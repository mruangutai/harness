"""github/issues.py — issue, label and issue-type calls, and the sub-issue and blocker edges, run
through github.transport (D-02, D-14)."""
import re

from github import issue_args, issue_types, transport


_LABEL_COLOR = "5319e7"


# The authority must be a real host: dot-separated labels, each alphanumeric at both edges with
# inner hyphens (so no empty, dot-edged or hyphen-edged label), and an optional port 1-65535
# without a leading zero. Owner is [A-Za-z0-9_-] (EMU logins carry `_shortcode`) and repo
# [A-Za-z0-9._-] other than `.`/`..`, so `?`, `#`, `%`, `@` and dot segments are refused while
# any GHE host, port included, passes.
_HOST_LABEL = r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?"
_PORT = r"(?:6553[0-5]|655[0-2][0-9]|65[0-4][0-9]{2}|6[0-4][0-9]{3}|[1-5][0-9]{4}|[1-9][0-9]{0,3})"
_ISSUE_URL = re.compile(
    rf"https?://{_HOST_LABEL}(?:\.{_HOST_LABEL})*(?::{_PORT})?"
    r"/[A-Za-z0-9_-]+/(?!\.\.?/)[A-Za-z0-9._-]+/issues/([0-9]+)/?", re.ASCII)


def issue_number_from_url(args, output):
    """The positive issue number at the end of a complete http(s) GitHub issue URL, the shape
    `gh issue create` prints. Malformed, zero, non-ASCII and oversized tails are transport.GhError with
    the argv and the original output, never a raw ValueError (#1542)."""
    match = _ISSUE_URL.fullmatch(output.strip())
    try:
        number = int(match.group(1)) if match else 0
    except ValueError:
        number = 0
    if number < 1:
        raise transport.GhError(
            args, None, output, "",
            f"{' '.join(['gh'] + list(args[:2]))} returned no issue number",
            transport.value_from_argv(args),
            "output did not contain a /issues/<n> URL",
        )
    return number


def ensure_labels(repo, labels):
    """Create every label the factory needs, idempotently. Propagates a transport.GhError rather than
    swallowing it — a control plane that cannot create its own vocabulary must stop rather than
    fail later at the issue create with a confusing message (D-02)."""
    for label in labels:
        transport.run_gh([
            "label", "create", label, "--repo", repo, "--force",
            "--color", _LABEL_COLOR,
            "--description", "created by the harness factory",
        ])


def create_issue(repo, title, body, labels):
    """Create an issue and return its number, parsed from the created URL."""
    args = ["issue", "create", "--repo", repo, "--title", title, "--body", body]
    for label in labels:
        args += ["--label", label]
    out = transport.run_gh(args)
    return issue_number_from_url(args, out)


def detect_issue_types(repo):
    """Detect whether `repo` supports native GitHub Issue Types (T-08). NEVER raises: an
    undetectable capability - the query itself failing - is compatibility mode, not a tool
    failure, so the caller falls back to the label vocabulary instead of aborting."""
    try:
        output = transport.run_gh(issue_types.capability_query_args(repo))
    except transport.GhError as e:
        return issue_types.classify_capability(e.status or 1, e.stdout or e.stderr or "")
    return issue_types.classify_capability(0, output)


def apply_issue_type(repo, number, type_id):
    """Apply `type_id` (a node id from detect_issue_types' declared mapping) to issue
    `number`. Propagates transport.GhError exactly as create_issue does - a failed type-apply must be
    visible, and the caller's receipt ordering is what makes it recoverable."""
    node_id = transport.run_gh(issue_types.node_id_args(repo, number)).strip()
    transport.run_gh(issue_types.apply_type_args(node_id, type_id))


def issue_view(repo, number, fields):
    return transport.run_gh(["issue", "view", str(number), "--repo", repo, "--json", ",".join(fields)],
                   json_out=True)


def add_label(repo, number, label):
    transport.run_gh(["issue", "edit", str(number), "--repo", repo, "--add-label", label])


def assign(repo, number, login):
    transport.run_gh(["issue", "edit", str(number), "--repo", repo, "--add-assignee", login])


# ---------------- the three edge functions (D-14) ----------------
# Each is one line: build the argv with github.issue_args' builder, run it through THIS module's transport.run_gh.

def internal_id(repo, num):
    """The internal REST integer id — never the GraphQL node id `issue view` returns. Both edge
    endpoints below take this id, never the issue number (the trap issue_args.py documents)."""
    return int(transport.run_gh(issue_args.internal_id_args(repo, num)).strip())


def attach_sub_issue(repo, parent_num, child_id):
    transport.run_gh(issue_args.attach_sub_issue_args(repo, parent_num, child_id))


def blocked_by(repo, num, blocker_id):
    transport.run_gh(issue_args.blocked_by_args(repo, num, blocker_id))
