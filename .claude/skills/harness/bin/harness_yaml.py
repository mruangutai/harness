#!/usr/bin/env python3
"""Shared YAML loading + PyYAML-presence policy for the harness `bin/` tree.

D-12: this is the ONLY `try: import yaml / except ImportError:` in the whole
tree. It parses nothing itself — it exits or grants. Every other module in
this tree that needs YAML imports THIS module, never `yaml` directly.

Import-time behaviour is exactly the one `try/except` below and the loader
class definitions that follow it (pure class construction, no I/O). No
marker read, no marker write, no caching, no other module-level mutable
state (PLAN.md T-03).
"""
import json
import os
import sys

try:
    import yaml
except ImportError:
    yaml = None


# --- Errors -----------------------------------------------------------------
# Two distinct types on purpose (T-03 goal #5): check-domain.sh's converted
# block must catch a duplicate key and a general parse failure separately —
# the duplicate case renders the existing DEC-156 denial verbatim, the parse
# case renders a new parse-error denial. Merging them forces a rework there.

class YamlParseError(Exception):
    """Raised on any other malformed-YAML failure. Carries the path/label
    so a caller can render it (D-02 consequence #2 — this is a NEW blocking
    outcome where the pre-change regex silently found no keys)."""

    def __init__(self, where, original):
        self.where = where
        self.original = original
        super().__init__(f"failed to parse YAML in {where}: {original}")


class MissingDependency(YamlParseError):
    """PyYAML is not importable. Carries INSTALL_COMMAND in its message.

    A SUBCLASS OF YamlParseError (see below), so a caller that handles "this file
    cannot be read" also handles "no parser exists to read it with" — the two are
    the same outcome from the caller's seat, and a caller that distinguishes them
    can still do so by type.
    """

    def __init__(self):
        # INSTALL_COMMAND is defined further down the module. That is fine — this
        # body runs at RAISE time, long after import — but it is a forward reference,
        # so do not "tidy" this into a class attribute or a default argument, either
        # of which evaluates at class-creation time and would NameError on import.
        Exception.__init__(
            self,
            "PyYAML is not importable by this python3 interpreter, so no YAML can "
            "be read. It is REQUIRED, not optional (DEC-171 am.1):\n" + INSTALL_COMMAND)


class DuplicateKeyError(YamlParseError):
    """Raised by the loader on a repeated mapping key, at any nesting depth
    (D-02). Carries the offending key so a caller can render it.

    NOW A SUBCLASS OF YamlParseError, found by the third review pass. It was a bare
    Exception, so `except YamlParseError` did NOT catch it — and two callers wrote
    exactly that, believing they had covered "the file is unreadable". A duplicated
    key made gh-sync.py and upgrade-config.py die with a raw traceback reading
    "the tool is broken" when the truth was "your file is", defeating the very
    handler each had just added. Callers that need the DEC-156 wording still catch
    DuplicateKeyError FIRST; the ordering is what distinguishes them.
    """

    def __init__(self, key, where=None, mark=None):
        self.key = key
        self.where = where
        # `mark` is the offending key node's position. SC-14 asks findings to name
        # file, LINE and COLUMN; without it a duplicate-key finding named only the file
        # and the key, so the one defect class the corpus gate newly covers was the one
        # it diagnosed worst. Goal-check c1, Q2.
        self.mark = mark
        msg = f"duplicate key {key!r}"
        if mark is not None:
            msg += f" at line {mark.line + 1}, column {mark.column + 1}"
        if where:
            msg += f" in {where}"
        # DEC-156's guidance travels WITH the error, so every caller reports it
        # whether or not it has a dedicated handler (review finding 5).
        msg += (" — a repeated key is silently shadowed by its last occurrence. "
                "Replace the placeholder when filling it in; never append a second "
                "copy (DEC-156).")
        Exception.__init__(self, msg)



# --- The loader ---------------------------------------------------------
# One SafeLoader subclass, two overrides (D-08's timestamp strip, D-02's
# duplicate-key raise). Nothing else is stripped — bool/int/float resolvers
# stay, D-08 is explicit that schema_version/cycles_used genuinely want ints.

if yaml is not None:

    # THE C LOADER WHERE THE BUILD HAS ONE (review of PR #149). PyYAML ships a libyaml
    # binding that is 7.7x faster on this repo's own corpus, and the pure-Python
    # SafeLoader was being used while `yaml.__with_libyaml__` was True — a default, not a
    # decision. Measured here over this tree's 92 YAML files: 528.2 ms on SafeLoader against
    # 69.8 ms on CSafeLoader, with ZERO differences in parsed output — confirmed again by an
    # independent reviewer at 548.0 vs 75.4 ms over 94 files, including a type-strict
    # recursive compare that a bare `==` would have let an int/float drift hide behind.
    # ONE corpus, ONE pair of numbers: the first draft quoted a different measurement here
    # than in the PR body, over a different file count, which is how two true numbers turn
    # into a reader's doubt about both.
    #
    # WHAT IS NOT FASTER: a parse ERROR under the C loader reports line and column but loses
    # the source snippet and caret the Python loader prints. Diagnosis is slightly poorer on
    # malformed input; correctness is not affected. Duplicate detection, merge keys, the timestamp strip
    # and int/bool resolution all survive, because both overrides below are applied to
    # whichever base is chosen.
    #
    # Fall back to the Python loader rather than requiring the binding: a source build of
    # PyYAML without libyaml is legal and common, and a hard requirement would turn a
    # performance choice into an install failure. `_LOADER_IS_C` is exported so a caller
    # that cares can report which one ran instead of guessing.
    _BASE_LOADER = getattr(yaml, "CSafeLoader", None) or yaml.SafeLoader
    _LOADER_IS_C = _BASE_LOADER is not yaml.SafeLoader

    class _StrictSafeLoader(_BASE_LOADER):
        pass

    _StrictSafeLoader.yaml_implicit_resolvers = {
        first: [
            (tag, regexp)
            for tag, regexp in resolvers
            if tag != "tag:yaml.org,2002:timestamp"
        ]
        # _BASE_LOADER rather than a hard-coded SafeLoader. DEFENSIVE, not corrective:
        # `yaml.SafeLoader.yaml_implicit_resolvers is yaml.CSafeLoader.yaml_implicit_resolvers`
        # is True today, so both spellings produce the same dict and nothing is fixed by
        # this. An earlier version of this comment claimed the hard-coded form would
        # "silently restore timestamp resolution"; that was a counterfactual, caught by
        # review, and is corrected rather than left for the next reader to trust. What the
        # line does buy is that the strip follows whichever base is chosen if PyYAML ever
        # stops sharing the object.
        for first, resolvers in _BASE_LOADER.yaml_implicit_resolvers.items()
    }

    def _construct_mapping(self, node, deep=False):
        if not isinstance(node, yaml.MappingNode):
            raise yaml.constructor.ConstructorError(
                None, None,
                "expected a mapping node, but found %s" % node.id,
                node.start_mark,
            )
        # THE DUPLICATE SCAN MUST SEE THIS NODE'S OWN KEYS ONLY, before flattening.
        #
        # `flatten_mapping` splices merge-key (`<<: *anchor`) entries INTO node.value,
        # so scanning afterwards counts an inherited key and an explicit override of it
        # as a duplicate — which it is not: `{<<: *base, b: 3}` is legal YAML with
        # well-defined override semantics, and stdlib safe_load returns `b: 3`. Scanning
        # after the flatten made it raise instead.
        #
        # Not reachable from this repo's own files, which use no anchors — but harness
        # is a portable framework with an onboarding path, and a downstream project that
        # DRYs its domain lists with `<<:` would have BOTH write hooks fail closed on
        # every write, blaming the user for a "duplicate key" in valid YAML. A guard
        # that is wrong about the rulebook is the failure mode this whole feature exists
        # to remove; being wrong in the strict direction is no better.
        # (key, its own node's mark) — the mark must travel WITH its key. A first
        # version passed `key_node` from the loop above, which by then held the LAST
        # node, so the reported position was right only when the duplicate happened to
        # be last. It was, in the fixture I tested. Caught by re-reading rather than by
        # the test, which asserted only that A position was present.
        own = []
        for key_node, _ in node.value:
            if key_node.tag == "tag:yaml.org,2002:merge":
                continue          # `<<` is the merge indicator, never a data key
            own.append((self.construct_object(key_node, deep=deep), key_node.start_mark))
        seen = set()
        for key, mark in own:
            try:
                if key in seen:
                    raise DuplicateKeyError(key, mark=mark)
                seen.add(key)
            except TypeError:
                # An unhashable key (a list or dict used as a key) cannot collide by
                # identity here; PyYAML rejects it downstream on its own terms.
                pass

        self.flatten_mapping(node)
        mapping = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value      # a later merge-key entry legitimately overrides
        return mapping

    _StrictSafeLoader.construct_mapping = _construct_mapping


def load_str(text, where):
    """Parse in-memory YAML content. `where` is a label used in error
    messages. Raises DuplicateKeyError on a repeated key at any nesting
    depth, YamlParseError on ANY other failure to produce a document."""
    # THE MISSING-DEPENDENCY CASE MUST BE CHECKED FIRST, before any `yaml.` attribute
    # is evaluated. Without this the function could not report its own premise failing:
    # `yaml.load(...)` raised `AttributeError: 'NoneType' has no attribute 'load'`, and
    # Python then evaluated the `except yaml.YAMLError` clause — which raised a SECOND
    # AttributeError that escaped uncaught. So on a machine with no PyYAML, check-state
    # reported every file as "does not parse: 'NoneType' object has no attribute
    # 'YAMLError'" and exited 1, and the plain scripts died with a raw traceback. The
    # user never saw INSTALL_COMMAND — in the one scenario this whole feature exists
    # for. `require_or_die` was written as the gate for exactly this and has ZERO
    # production callers, so nothing intercepted it upstream either.
    if yaml is None:
        raise MissingDependency()

    try:
        return yaml.load(text, Loader=_StrictSafeLoader)
    except DuplicateKeyError:
        raise
    except yaml.YAMLError as e:
        raise YamlParseError(where, e) from e
    except Exception as e:
        # F-01, found by the review panel and reproduced live. Catching only
        # yaml.YAMLError left every other failure to propagate uncaught through
        # both write hooks, killing the subprocess with exit 1 — and exit 1 is
        # NON-BLOCKING (DEC-100), so the write proceeded UNGOVERNED. A crash is
        # the one way this fail-closed guard could fail open, and it is exactly
        # the pattern T-17's receipt documents; it was fixed once in the escape
        # path and missed here, in the module both hooks call.
        #
        # Deliberately broad: the callers already treat YamlParseError as "cannot
        # read the rulebook, block". Any unanticipated failure must land there
        # too, because the alternative is not a wrong answer, it is no guard.
        raise YamlParseError(where, e) from e


def load_file(path):
    """Read and parse a `.yaml` file with the module's loader.

    The READ is inside the try (F-01). It used to sit outside, so a manifest
    that is not valid UTF-8, or a directory where a file was expected, or an
    unreadable file, raised straight past every caller's `except YamlParseError`
    — verified live against both hook binaries with a `\\xff` byte in the
    manifest: exit 1, write allowed, enforcement silently off.
    """
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        raise YamlParseError(path, e) from e
    except UnicodeDecodeError as e:
        # NOT an OSError. Named separately so the next reader does not "simplify"
        # the pair into `except OSError` and quietly restore the fail-open.
        raise YamlParseError(path, e) from e
    return load_str(text, path)


# --- Manifest domain walk (D-03) --------------------------------------------

def manifest_domains(manifest_path, agent):
    """Walk the parsed manifest and return (mine, shared) glob lists for
    `agent`. Equivalent to check-domain.sh's pre-change collect() for every
    agent in this repo's manifest, at EVERY nesting level — not just
    teams[].members[] (T-02 test 5: harness-eng-lead lives under `leads:`,
    harness-orchestrator is a bare top-level key). Every returned glob is
    str()-coerced (D-08)."""
    parsed = load_file(manifest_path)

    mine = []

    def walk(node):
        if isinstance(node, dict):
            domain = node.get("domain")
            if node.get("name") == agent and isinstance(domain, list):
                for entry in domain:
                    if isinstance(entry, dict) and "path" in entry and not entry.get("read"):
                        mine.append(str(entry["path"]))
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(parsed)

    # M-02: `parsed.get("shared")` assumed a dict and sat OUTSIDE the widened try, so
    # it raised AttributeError past every caller's `except YamlParseError`. Note the
    # shape of the bug — `walk()` immediately above guards every branch with
    # isinstance, and the very next statement did not.
    #
    # WHY THE F-01 FIX DID NOT COVER IT: an empty file, a bare scalar and a bare list
    # all PARSE SUCCESSFULLY. They yield None / str / list, never an error, so the
    # widened `except` never engages. F-01 was scoped to the two shapes cycle 0 named
    # (bad UTF-8, manifest-as-directory) and this is a third route to the same
    # exit-1 fail-open — which is non-blocking (DEC-100), so both write hooks let the
    # write through. An EMPTY team-config.yaml was enough.
    #
    # Raised as YamlParseError rather than returning empty: callers already treat that
    # as "cannot read the rulebook, block", and a manifest that is not a mapping is
    # exactly that. Returning ([], []) would read as "this agent owns nothing" — a
    # silent, total loss of enforcement dressed as a legitimate answer.
    if not isinstance(parsed, dict):
        raise YamlParseError(
            manifest_path,
            f"manifest is not a YAML mapping (parsed as {type(parsed).__name__}); "
            f"an empty or malformed file cannot declare any domain")

    shared = []
    for entry in (parsed.get("shared") or []):
        if isinstance(entry, dict) and "path" in entry:
            shared.append(str(entry["path"]))

    return mine, shared


# --- PyYAML-presence policy (D-06, D-07, D-08 install command; E3 escape) ---

# D-07 + Amendment 1: the plain install is attempted first, PEP 668's escape
# hatch second. [reasoned, unverified]: the ordering assumes a pip old enough
# to reject --break-system-packages as an unknown option might still exist
# downstream; no such pip exists on this machine to prove it against
# (Homebrew 26.1.1, /usr/bin 24.1.1) so this is documented pip history, not a
# local measurement. `--user` is mandatory per Amendment 1 — Homebrew's own
# PEP 668 message warns that omitting it can break the Homebrew installation.
INSTALL_COMMAND = (
    "python3 -m pip install pyyaml\n"
    '# if that fails with "externally-managed-environment" (PEP 668, e.g. Homebrew/Debian):\n'
    "python3 -m pip install --user --break-system-packages pyyaml"
)

# The single definition of "this field is declining to answer" (DEC-121). Every
# consumer compares against THIS, lower-cased and stripped — a second copy is how
# INV-6 came to accept `review_sha: none` as a pinned SHA (issue #16).
PLACEHOLDER_UNSET = ("none", "null", "n/a")


def _marker_path(root):
    return os.path.join(root, ".harness", ".pyyaml-bootstrap")


def require_or_die():
    """For check-state.sh and the plain .py scripts. No bootstrap escape
    (D-06) — this gates the orchestrator, not a write, so a hard block here
    costs no recovery path."""
    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    marker = _marker_path(root)
    if yaml is not None:
        try:
            os.unlink(marker)
        except OSError:
            pass
        return
    sys.stderr.write("PyYAML is not importable by this python3 interpreter.\n")
    sys.stderr.write(INSTALL_COMMAND + "\n")
    sys.exit(1)


def _resolve_identity(payload):
    """session_id -> transcript_path stem -> CLAUDE_CODE_SESSION_ID ->
    CLAUDE_CODE_BRIDGE_SESSION_ID, in that order and nowhere else.

    payload=None means: this is a real hook invocation, so read the payload
    from the HOOK_PAYLOAD environment variable (never stdin — `python3 -`
    takes its PROGRAM from stdin, so a payload piped alongside a heredoc is
    lost; check-domain.sh:232-234 records why). If HOOK_PAYLOAD is unset or
    empty, fall through to the environment-variable entries below."""
    if payload is None:
        raw = os.environ.get("HOOK_PAYLOAD")
        if raw:
            try:
                payload = json.loads(raw)
            except (ValueError, TypeError):
                payload = None

    if isinstance(payload, dict):
        session_id = payload.get("session_id")
        if session_id:
            return str(session_id)
        transcript_path = payload.get("transcript_path")
        if transcript_path:
            stem = os.path.splitext(os.path.basename(str(transcript_path)))[0]
            if stem:
                return stem

    env_session_id = os.environ.get("CLAUDE_CODE_SESSION_ID")
    if env_session_id:
        return env_session_id

    bridge_session_id = os.environ.get("CLAUDE_CODE_BRIDGE_SESSION_ID")
    if bridge_session_id:
        return bridge_session_id

    return None


def require_or_bootstrap(root, payload=None):
    """For the two write-gating hooks. True = allow, False = block.

    yaml importable: unlink the marker if present, return True.

    yaml missing: resolve session identity (see _resolve_identity). No
    identity resolves -> fail CLOSED, print INSTALL_COMMAND, return False —
    an unbounded grant here is a permanent silent bypass (D-06). Otherwise,
    exactly the four marker-state cases in PLAN.md T-03:
      absent                       -> write marker, print INSTALL_COMMAND, allow
      present, identity matches    -> allow silently
      present, identity mismatches -> block
      marker write fails           -> block
    """
    marker = _marker_path(root)

    if yaml is not None:
        try:
            os.unlink(marker)
        except OSError:
            pass
        return True

    identity = _resolve_identity(payload)
    if not identity:
        sys.stderr.write(
            "PyYAML is not importable and no session identity could be resolved "
            "— failing closed.\n"
        )
        sys.stderr.write(INSTALL_COMMAND + "\n")
        return False

    # D-14a: EVERY block says why. Found by the SC-09 hand-run — these three branches
    # returned False silently, and both callers assume the callee already printed (they
    # say so in comments). That assumption held only for the no-identity path above, so
    # a user whose grant had expired got every Write AND every Bash command refused with
    # zero bytes of explanation: the agent saw only "PreToolUse:Write hook error: No
    # stderr output". Recoverable only by reading this source. A guard that blocks
    # without a reason is DEC-100b's "actionable rejection" inverted.
    if os.path.exists(marker):
        try:
            with open(marker, encoding="utf-8") as f:
                recorded = f.read().strip()
        except OSError as e:
            sys.stderr.write(
                f"PyYAML is not importable and the bootstrap marker at {marker} could "
                f"not be read ({e}) — failing closed.\n"
            )
            sys.stderr.write(INSTALL_COMMAND + "\n")
            return False
        if recorded == identity:
            return True
        sys.stderr.write(
            "PyYAML is not importable, and this session's one-time bootstrap grant was "
            "already used by an EARLIER session — failing closed. Install PyYAML to "
            "restore normal operation:\n"
        )
        sys.stderr.write(INSTALL_COMMAND + "\n")
        return False

    try:
        with open(marker, "w", encoding="utf-8") as f:
            f.write(identity)
    except OSError as e:
        sys.stderr.write(
            f"PyYAML is not importable and the bootstrap marker at {marker} could not "
            f"be written ({e}), so a one-time grant cannot be recorded — failing "
            f"closed rather than granting one that never expires.\n"
        )
        sys.stderr.write(INSTALL_COMMAND + "\n")
        return False

    sys.stderr.write(
        "PyYAML is not importable by this python3 interpreter; allowing this "
        "session once.\n"
    )
    sys.stderr.write(INSTALL_COMMAND + "\n")

    # D-14b: stderr ALONE does not satisfy SC-08. BRIEF:106 requires the install
    # command on "a channel the user sees", and the 2026-08-03 hand-run measured that
    # Claude Code surfaces hook stderr only on a BLOCK — on this allow path (exit 0) the
    # tester saw nothing, and grepping all three session transcripts for the command
    # returned 0. The grant is the one moment the user CAN still fix the machine, so a
    # message they never see is the same as no message.
    #
    # `systemMessage` on stdout is the PreToolUse contract's user-visible channel, and
    # it is proven live in this repo rather than assumed: branch-create-gate.sh:82,111
    # already emits exactly this shape on its own allow path, and it is registered in
    # .claude/settings.json. Emitted LAST so that a failure here cannot lose the stderr
    # copy, which is what reaches the agent.
    try:
        sys.stdout.write(json.dumps({"systemMessage":
            "[harness] PyYAML is missing, so the write guards cannot read the domain "
            "manifest. This session is granted ONE bootstrap pass and later sessions "
            "will be blocked. Install it now:\n" + INSTALL_COMMAND}) + "\n")
    except Exception:
        # Never let the courtesy channel break the grant it is announcing.
        pass
    return True
