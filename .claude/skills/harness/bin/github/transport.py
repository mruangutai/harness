"""github/transport.py — the single seam every harness tool talks to GitHub through (D-02, D-14).

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
import dataclasses
import datetime
import os
import subprocess

import artifact_accessors
import factory_cli


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
            value_from_argv(orig_argv),
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


def value_from_argv(argv):
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


@dataclasses.dataclass(frozen=True)
class GhResult:
    """One gh call's outcome, never raised (FEAT-2452). status, stdout and stderr are the
    authoritative process facts — status is None only when the launch itself failed — so a
    caller classifies on them, never on error.status: the rate-limit diagnosis sets that to None
    after a completed non-zero process. value is the parsed JSON or stripped stdout of a
    success, else None; error is the GhError run_gh would raise, else None."""

    status: int | None
    stdout: str
    stderr: str
    value: object
    error: GhError | None

    @property
    def ok(self):
        return self.error is None


def launch_gh(args, *, input=None):
    """The one subprocess and FACTORY_GH boundary: run [FACTORY_GH or gh] + args and return the
    captured text CompletedProcess as it is. It neither measures, interprets a non-zero exit,
    nor parses JSON. FACTORY_GH is read at CALL time, never cached at import, so a test can set
    it after import. With no input, stdin is DEVNULL so a real gh cannot block on a prompt;
    text input is passed as the process input instead. Both launch failures are typed: an
    absent binary keeps its own message, and any other OSError reaches the caller as the same
    typed error with the OS failure chained (FEAT-64)."""
    gh = os.environ.get("FACTORY_GH", "gh")
    stream = {"stdin": subprocess.DEVNULL} if input is None else {"input": input}
    try:
        return subprocess.run([gh] + list(args), capture_output=True, text=True, **stream)
    except FileNotFoundError as error:
        raise GhError(
            args, None, "", "",
            "gh not found", gh,
            "install gh, or point FACTORY_GH at its path",
        ) from error
    except OSError as error:
        raise GhError(
            args, None, "", "",
            "gh could not be launched", gh, f"{type(error).__name__}: {error}",
        ) from error


def _decode_gh_json(args, r):
    """The JSON body of a successful gh call. A body that does not decode is a gh failure to
    the caller, not a parser's — one typed error with the argv, status and captured streams
    (FEAT-64)."""
    try:
        return artifact_accessors.parse_gh_json(r.stdout, "GitHub response")
    except artifact_accessors.ArtifactAccessError as error:
        raise GhError(args, r.returncode, r.stdout, r.stderr,
                      _what_from_argv(args), value_from_argv(args), str(error)) from error


def _exit_error(args, r):
    """The GhError for a completed non-zero gh process: the GraphQL budget diagnosis when its
    text names a rate limit (never for the budget query itself — the recursion guard), else the
    first captured line. Diagnosing never re-runs the failed operation."""
    if not _is_rate_limit_query(list(args)) and _looks_like_rate_limit(r.stdout, r.stderr):
        return _rate_limit_budget_error(list(args), r.stdout, r.stderr)
    next_step = _first_line(r.stderr) or _first_line(r.stdout) or "no output captured"
    return GhError(args, r.returncode, r.stdout, r.stderr,
                   _what_from_argv(args), value_from_argv(args), next_step)


def try_gh(args, json_out=False, *, input=None):
    """Run [gh] + args through launch_gh and return a GhResult rather
    than raising. Only GhError — a launch, non-zero exit or strict-JSON failure — becomes a
    result; any other exception is a programming error and escapes. A JSON body that does not
    decode is not ok even though the process exited zero."""
    try:
        r = launch_gh(args, input=input)
    except GhError as error:
        return GhResult(None, error.stdout, error.stderr, None, error)
    if r.returncode != 0:
        return GhResult(r.returncode, r.stdout, r.stderr, None, _exit_error(args, r))
    if not json_out:
        return GhResult(0, r.stdout, r.stderr, r.stdout.strip(), None)
    try:
        value = _decode_gh_json(args, r)
    except GhError as error:
        return GhResult(0, r.stdout, r.stderr, None, error)
    return GhResult(0, r.stdout, r.stderr, value, None)


def run_gh(args, json_out=False, *, input=None):
    """Run [gh] + args and return the parsed JSON or stripped stdout; raise the GhError
    try_gh carries on any launch, non-zero exit or strict-JSON failure.

    Never swallows a failure and never returns a default (D-02).
    """
    result = try_gh(args, json_out, input=input)
    if not result.ok:
        raise result.error
    return result.value

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
