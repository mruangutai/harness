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

class DuplicateKeyError(Exception):
    """Raised by the loader on a repeated mapping key, at any nesting depth
    (D-02). Carries the offending key so a caller can render it."""

    def __init__(self, key, where=None):
        self.key = key
        self.where = where
        msg = f"duplicate key {key!r}"
        if where:
            msg += f" in {where}"
        super().__init__(msg)


class YamlParseError(Exception):
    """Raised on any other malformed-YAML failure. Carries the path/label
    so a caller can render it (D-02 consequence #2 — this is a NEW blocking
    outcome where the pre-change regex silently found no keys)."""

    def __init__(self, where, original):
        self.where = where
        self.original = original
        super().__init__(f"failed to parse YAML in {where}: {original}")


# --- The loader ---------------------------------------------------------
# One SafeLoader subclass, two overrides (D-08's timestamp strip, D-02's
# duplicate-key raise). Nothing else is stripped — bool/int/float resolvers
# stay, D-08 is explicit that schema_version/cycles_used genuinely want ints.

if yaml is not None:

    class _StrictSafeLoader(yaml.SafeLoader):
        pass

    _StrictSafeLoader.yaml_implicit_resolvers = {
        first: [
            (tag, regexp)
            for tag, regexp in resolvers
            if tag != "tag:yaml.org,2002:timestamp"
        ]
        for first, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
    }

    def _construct_mapping(self, node, deep=False):
        if not isinstance(node, yaml.MappingNode):
            raise yaml.constructor.ConstructorError(
                None, None,
                "expected a mapping node, but found %s" % node.id,
                node.start_mark,
            )
        self.flatten_mapping(node)
        mapping = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if key in mapping:
                raise DuplicateKeyError(key)
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
        return mapping

    _StrictSafeLoader.construct_mapping = _construct_mapping


def load_str(text, where):
    """Parse in-memory YAML content. `where` is a label used in error
    messages. Raises DuplicateKeyError on a repeated key at any nesting
    depth, YamlParseError on any other malformed YAML."""
    try:
        return yaml.load(text, Loader=_StrictSafeLoader)
    except DuplicateKeyError:
        raise
    except yaml.YAMLError as e:
        raise YamlParseError(where, e) from e


def load_file(path):
    """Read and parse a `.yaml` file with the module's loader."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
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
