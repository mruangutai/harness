"""github/refs.py — git ref and file-content calls, run through github.transport (D-02, D-14).

file_at_ref is the only function in github/ that reads repository CONTENT rather than issue,
board or ref metadata.
"""
import base64
import binascii

from github import transport


def default_branch_sha(repo, branch):
    return transport.run_gh(["api", f"repos/{repo}/git/ref/heads/{branch}", "--jq", ".object.sha"]).strip()


def file_at_ref(repo, path, ref):
    """Read one file's content from `repo` (owner/name) at `path` (repository-relative, no
    leading slash) as it exists at `ref` (a branch name). Returns the decoded text and parses
    nothing else — JSON handling belongs to the caller. Hits the REST contents endpoint with
    `ref` as a query parameter and asks gh for the `content` field alone via --jq, never the
    whole object.

    Every failure raises transport.GhError, never a sentinel: repo not found, path not found at that ref,
    ref not found, unauthenticated gh, and a `content` field that is absent or does not
    base64-decode. A caller must never mistake "not there" for "empty file" (D-02).
    """
    argv = ["api", f"repos/{repo}/contents/{path}?ref={ref}", "--jq", ".content"]
    value = f"{repo} {path}@{ref}"
    try:
        raw = transport.run_gh(argv)
    except transport.GhError as e:
        raise transport.GhError(
            e.argv, e.status, e.stdout, e.stderr,
            "gh api contents failed", value,
            "check the repository, path and ref",
        ) from e
    if not raw or raw == "null":
        raise transport.GhError(
            argv, None, raw, "",
            "file content missing from response", value,
            "gh returned no content field",
        )
    try:
        decoded = base64.b64decode("".join(raw.split()), validate=True)
    except (binascii.Error, ValueError):
        raise transport.GhError(
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
        transport.run_gh(args)
        return True
    except transport.GhError as e:
        combined = f"{e.stdout or ''}\n{e.stderr or ''}".lower()
        if "422" in combined and "already exists" in combined:
            return False
        raise


def delete_ref(repo, ref):
    """The release path for an abandoned claim. Not called by any tool in this increment."""
    name = ref[len("refs/heads/"):] if ref.startswith("refs/heads/") else ref
    transport.run_gh(["api", "-X", "DELETE", f"repos/{repo}/git/refs/heads/{name}"])
