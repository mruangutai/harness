#!/usr/bin/env python3
"""Feature-scoped in-flight claim store for Harness dispatch supervision.

Every mutation crosses harness_merge.locked_update. Version 2 stores one claims list so identity
is explicit rather than encoded in object keys. Version 1 persona-keyed files are accepted on read
and rewritten as version 2 by the next mutation; version 1 is never written.
"""
import datetime
import json
import math
import os
import re
import shlex
import subprocess
import sys
import time
import uuid

import harness_boundary
import harness_merge

SINGLE_FLIGHT_AGENTS = ("harness-pm",)
CANONICAL_ARTIFACTS = ("plan.yaml", "BRIEF.md", "feature.json", "STATE.md")
_CANONICAL_ARTIFACT_RE = re.compile(
    r"^\.harness/[^/]+/features/([^/]+)/(plan\.yaml|BRIEF\.md|feature\.json|STATE\.md)$"
)
# Claude Code exposes no durable child-process owner. FEAT-37 deliberately shortened this to one
# normal PM cycle so an interrupted compatibility-host run does not strand a tier for an hour.
CLAIM_TTL_SECONDS = 1200
# An OMP claim is owned by a supervisor process, not by a clock — a verified one is live at
# ANY age, which is what lets a leaf run for hours. This backstop applies ONLY to a claim
# whose supervisor identity cannot be PROVEN (no recorded start time, or the OS would not
# report one). Without it such a claim can never age out, and a stranded one refuses its
# parent's yield through validate-digest.py's held-child gate forever. Well above the
# 7,200s longest measured leaf run, so it can never cut short a real agent.
OMP_UNVERIFIED_TTL_SECONDS = 86400
LOCK_TIMEOUT_SECONDS = 1.0
REGISTRY_REL = ".harness/.inflight-claims.json"
SCHEMA_VERSION = 2
LEGACY_FEATURE = "legacy"
RELEASE_ALL_CMD = "python3 .agents/skills/harness/bin/inflight_registry.py release-all"


def _registry_path(root):
    return os.path.join(root, REGISTRY_REL)


def _empty():
    return {"schema_version": SCHEMA_VERSION, "claims": []}


def _parse(base, path):
    if base is None:
        return _empty()
    text = base.decode("utf-8", errors="replace") if isinstance(base, bytes) else base
    if not text.strip():
        return _empty()
    try:
        raw = json.loads(text)
    except (json.JSONDecodeError, ValueError):
        print(f"inflight_registry: {path} is corrupt or unparseable, treating as empty", file=sys.stderr)
        return _empty()
    if not isinstance(raw, dict):
        print(f"inflight_registry: {path} is not a JSON object, treating as empty", file=sys.stderr)
        return _empty()
    if raw.get("schema_version") == SCHEMA_VERSION and isinstance(raw.get("claims"), list):
        return {"schema_version": SCHEMA_VERSION, "claims": list(raw["claims"])}

    # Clean cutover reader. The next locked operation writes only version 2.
    claims = []
    for agent, entries in raw.items():
        if not isinstance(agent, str) or not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                claims.append(entry)
                continue
            migrated = dict(entry)
            migrated.setdefault("claim_id", uuid.uuid4().hex)
            migrated.setdefault("agent", agent)
            migrated.setdefault("feature", LEGACY_FEATURE)
            migrated.setdefault("runtime", "claude")
            claims.append(migrated)
    return {"schema_version": SCHEMA_VERSION, "claims": claims}


def _update_registry(root, mutator):
    path = _registry_path(root)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    holder = {}

    def transform(base):
        data = _parse(base, path)
        new_data, result = mutator(data)
        holder["result"] = result
        canonical = {
            "schema_version": SCHEMA_VERSION,
            "claims": list(new_data.get("claims", [])),
        }
        return (json.dumps(canonical, indent=2, sort_keys=True) + "\n").encode("utf-8")

    harness_merge.locked_update(path, transform, timeout=LOCK_TIMEOUT_SECONDS)
    return holder["result"]


def _iso(ts):
    return datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc).isoformat()


def _pid_alive(pid):
    if not isinstance(pid, int) or isinstance(pid, bool) or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


# Cached for this process only. `_expire` runs per claim on every registry read, and the
# macOS branch forks `ps`; without this a single dispatch would fork once per claim. A
# process start time never changes, so a cache that dies with the CLI invocation is safe.
_START_TIME_CACHE = {}


def _process_start_time(pid):
    """Epoch seconds at which `pid` started, or None when the OS will not say.

    Both branches return ABSOLUTE seconds so the value survives a reboot comparison:
    ticks-since-boot alone would let a post-reboot pid collide with its pre-reboot self.
    """
    if not isinstance(pid, int) or isinstance(pid, bool) or pid <= 0:
        return None
    if pid not in _START_TIME_CACHE:
        _START_TIME_CACHE[pid] = _read_process_start_time(pid)
    return _START_TIME_CACHE[pid]


def _read_process_start_time(pid):
    try:
        # Linux. Field 22 of /proc/<pid>/stat is start time in clock ticks since boot.
        # The comm field is parenthesised and may itself contain spaces, so split after
        # the LAST ')' rather than on the whole line.
        with open(f"/proc/{pid}/stat", "rb") as handle:
            tail = handle.read().rpartition(b")")[2].split()
        with open("/proc/stat", "rb") as handle:
            boot = next(l for l in handle if l.startswith(b"btime "))
        return int(float(boot.split()[1]) + float(tail[19]) / os.sysconf("SC_CLK_TCK"))
    except Exception:
        pass
    try:
        # macOS and anything else without /proc. One fork per distinct pid per run.
        #
        # LC_ALL=C IS LOAD-BEARING, not tidiness. `ps` renders lstart in the inherited
        # LC_TIME while Python's strptime stays in the C locale unless setlocale was
        # called, so on a non-English host the parse raises, every claim records no
        # start time, and each one silently falls to the unverified backstop — F3's fix
        # inert and DEC-204's "live for any age" quietly reduced to 24 hours. Pinning
        # the child's locale makes the two ends agree on every host.
        out = subprocess.run(["ps", "-o", "lstart=", "-p", str(pid)],
                             capture_output=True, text=True, timeout=5,
                             env={**os.environ, "LC_ALL": "C", "LC_TIME": "C"})
        line = out.stdout.strip()
        return int(time.mktime(time.strptime(line, "%a %b %d %H:%M:%S %Y"))) if line else None
    except Exception:
        return None


def _omp_claim_live(claim, now):
    """Is this OMP claim still owned by the supervisor that made it?

    IDENTITY IS (pid, start time), NEVER THE PID ALONE. The OS recycles pids, and because
    this branch has no TTL a recycled one made a dead claim look live FOREVER — not merely
    stalling single-flight for `harness-pm`, but refusing its parent's yield through
    validate-digest.py's held-child gate, which locks a lead and then the orchestrator out
    of reporting exactly as that file's own comment describes. `reconcile` could not clear
    it either, because it asks this same question and is told the claim is live.
    """
    pid = claim.get("supervisor_pid")
    if not _pid_alive(pid):
        return False
    recorded = claim.get("supervisor_started_at")
    current = _process_start_time(pid)
    if _is_number(recorded) and _is_number(current):
        return int(recorded) == int(current)
    # Identity unproven: fall back to the backstop rather than trusting the pid forever.
    started = claim.get("started_at")
    return _is_number(started) and now - started <= OMP_UNVERIFIED_TTL_SECONDS


def _is_number(value):
    # isfinite, not merely numeric: `json.loads` accepts bare NaN and Infinity, and every
    # caller here feeds this predicate straight into an `int()` that would raise on one.
    # That raise escapes into the broad `except Exception` around each registry read and
    # fails OPEN — durably, because reconcile asks the same question and its pruning write
    # never lands, so the bad entry can never clear itself.
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _expire(claims, now):
    live = []
    expired = 0
    for claim in claims:
        if not isinstance(claim, dict):
            expired += 1
            continue
        started = claim.get("started_at")
        if not isinstance(started, (int, float)) or isinstance(started, bool):
            expired += 1
            continue
        if claim.get("runtime") == "omp":
            if _omp_claim_live(claim, now):
                live.append(claim)
            else:
                expired += 1
            continue
        if now - started > CLAIM_TTL_SECONDS:
            expired += 1
        else:
            live.append(claim)
    return live, expired

def _expire_where(claims, now, predicate):
    kept = []
    expired = 0
    for claim in claims:
        if not predicate(claim):
            kept.append(claim)
            continue
        live, count = _expire([claim], now)
        kept.extend(live)
        expired += count
    return kept, expired


def _matches(claim, agent=None, feature=None, claim_id=None, agent_id=None, job_id=None):
    if not isinstance(claim, dict):
        return False
    return (
        (agent is None or claim.get("agent") == agent)
        and (feature is None or claim.get("feature", LEGACY_FEATURE) == feature)
        and (claim_id is None or claim.get("claim_id") == claim_id)
        and (agent_id is None or claim.get("agent_id") == agent_id)
        and (job_id is None or claim.get("job_id") == job_id)
    )


def _visible(claim, feature=None, session=None):
    if feature is not None and claim.get("feature", LEGACY_FEATURE) != feature:
        return False
    # OMP child and parent sessions differ. Process ownership + feature identity is its liveness
    # boundary; the compatibility host retains FEAT-42's session filter.
    if session is not None and claim.get("runtime") != "omp":
        return claim.get("session") in (None, session)
    return True


def is_single_flight(agent):
    return agent in SINGLE_FLIGHT_AGENTS

def feature_root(owner_root, feature):
    """Resolve the checkout assigned to `feature`, falling back to the supplied owner root."""
    try:
        resolved = harness_boundary.worktree_for_feature(owner_root, feature)
    except Exception:
        return owner_root
    return resolved if resolved is not None else owner_root


def canonical_artifact(rel):
    match = _CANONICAL_ARTIFACT_RE.fullmatch(rel)
    return match.groups() if match else None


def quarantine_rel(rel, agent, session):
    artifact = canonical_artifact(rel)
    if artifact is None:
        return None
    feature, basename = artifact
    session_key = session[:8] if session else "nosession"
    return (
        f".harness/harness/features/{feature}/quarantine/"
        f"{agent}-{session_key}/{basename}"
    )


def orphan_write(root, agent, feature, session, now=None):
    now = now if now is not None else time.time()
    if not os.path.exists(_registry_path(root)):
        return False

    def mutator(data):
        live, _expired = _expire_where(
            data.get("claims", []),
            now,
            lambda claim: _matches(claim, feature=feature),
        )
        data["claims"] = live
        feature_claims = [claim for claim in live if _matches(claim, feature=feature)]
        has_compatibility_claim = any(
            claim.get("runtime") != "omp" for claim in feature_claims
        )
        writer_is_live = any(
            _matches(claim, agent=agent, feature=feature)
            and _visible(claim, feature, session)
            for claim in feature_claims
        )
        return data, has_compatibility_claim and not writer_is_live

    return _update_registry(root, mutator)

def live_claim(root, agent, now=None, session=None, feature=None):
    now = now if now is not None else time.time()
    path = _registry_path(root)
    if not os.path.exists(path):
        return None, 0

    def mutator(data):
        live, expired = _expire_where(
            data.get("claims", []),
            now,
            lambda claim: _matches(claim, agent=agent, feature=feature),
        )
        data["claims"] = live
        visible = [c for c in live if _matches(c, agent=agent) and _visible(c, feature, session)]
        oldest = min(visible, key=lambda c: c["started_at"]) if visible else None
        return data, (oldest, expired)

    return _update_registry(root, mutator)


def live_children(root, dispatcher, now=None, session=None, feature=None):
    now = now if now is not None else time.time()
    path = _registry_path(root)
    if not os.path.exists(path):
        return []

    def mutator(data):
        live, _expired = _expire_where(
            data.get("claims", []),
            now,
            lambda claim: _matches(claim, feature=feature)
            and isinstance(claim, dict)
            and claim.get("dispatcher") == dispatcher,
        )
        data["claims"] = live
        children = [
            (c.get("agent"), c)
            for c in live
            if c.get("dispatcher") == dispatcher and _visible(c, feature, session)
        ]
        return data, children

    return _update_registry(root, mutator)


def claim_with_receipt(
    root,
    agent,
    dispatcher,
    cwd,
    now=None,
    session=None,
    feature=LEGACY_FEATURE,
    runtime="claude",
    supervisor_pid=None,
):
    now = now if now is not None else time.time()

    def mutator(data):
        live, _expired = _expire_where(
            data.get("claims", []),
            now,
            lambda claim: _matches(claim, agent=agent, feature=feature),
        )
        if is_single_flight(agent) and any(
            _matches(c, agent=agent, feature=feature) for c in live
        ):
            data["claims"] = live
            return data, None
        entry = {
            "claim_id": uuid.uuid4().hex,
            "started_at": now,
            "feature": feature,
            "agent": agent,
            "dispatcher": dispatcher,
            "cwd": cwd,
            "runtime": runtime,
        }
        if session is not None:
            entry["session"] = session
        if runtime == "omp":
            entry["supervisor_pid"] = supervisor_pid
            # Pinned at claim time so a later recycled pid can be told apart from this one.
            # Absent when the OS declines to report it; `_omp_claim_live` then falls back
            # to OMP_UNVERIFIED_TTL_SECONDS rather than trusting the bare pid.
            started_at = _process_start_time(supervisor_pid)
            if started_at is not None:
                entry["supervisor_started_at"] = started_at
        live.append(entry)
        data["claims"] = live
        return data, dict(entry)

    return _update_registry(root, mutator)


def claim(root, agent, dispatcher, cwd, now=None, session=None, feature=LEGACY_FEATURE,
          runtime="claude", supervisor_pid=None):
    return claim_with_receipt(
        root,
        agent,
        dispatcher,
        cwd,
        now=now,
        session=session,
        feature=feature,
        runtime=runtime,
        supervisor_pid=supervisor_pid,
    ) is not None


def attach_runtime_identity(root, agent, feature, agent_id=None, job_id=None, claim_id=None):
    path = _registry_path(root)
    if not os.path.exists(path):
        return False

    def mutator(data):
        live, _expired = _expire_where(
            data.get("claims", []),
            time.time(),
            lambda claim: _matches(
                claim, agent=agent, feature=feature, claim_id=claim_id
            ),
        )
        matches = [
            c for c in live
            if _matches(c, agent=agent, feature=feature, claim_id=claim_id)
            and not c.get("agent_id")
            and not c.get("job_id")
        ]
        if len(matches) != 1:
            data["claims"] = live
            return data, False
        if agent_id:
            matches[0]["agent_id"] = agent_id
        if job_id:
            matches[0]["job_id"] = job_id
        data["claims"] = live
        return data, True

    return _update_registry(root, mutator)


def release(root, agent=None, feature=None, claim_id=None, agent_id=None, job_id=None):
    path = _registry_path(root)
    if not os.path.exists(path):
        return False

    def mutator(data):
        selector_matches = lambda claim: _matches(
            claim,
            agent=agent,
            feature=feature,
            claim_id=claim_id,
            agent_id=agent_id,
            job_id=job_id,
        )
        live, _expired = _expire_where(
            data.get("claims", []), time.time(), selector_matches
        )
        matches = [claim for claim in live if selector_matches(claim)]
        if not matches:
            data["claims"] = live
            return data, False
        if len(matches) != 1:
            selector = claim_id or agent_id or job_id or f"{feature or '*'}:{agent or '*'}"
            print(
                f"inflight_registry: release({selector!r}) is refusing — {len(matches)} live "
                "claims match; removing none rather than guessing.",
                file=sys.stderr,
            )
            data["claims"] = live
            return data, 0
        target_id = matches[0].get("claim_id")
        data["claims"] = [c for c in live if c.get("claim_id") != target_id]
        return data, True

    return _update_registry(root, mutator)


def release_all(root):
    path = _registry_path(root)
    if not os.path.exists(path):
        return 0

    def mutator(data):
        count = len(data.get("claims", []))
        data["claims"] = []
        return data, count

    return _update_registry(root, mutator)


def reconcile(root, feature=None, now=None):
    now = now if now is not None else time.time()
    path = _registry_path(root)
    if not os.path.exists(path):
        return 0

    def mutator(data):
        claims = data.get("claims", [])
        kept = []
        removed = 0
        for claim_entry in claims:
            live, expired = _expire([claim_entry], now)
            claim_feature = (
                claim_entry.get("feature", LEGACY_FEATURE)
                if isinstance(claim_entry, dict)
                else None
            )
            if expired and (feature is None or claim_feature == feature):
                removed += expired
            else:
                kept.extend(live or [claim_entry])
        data["claims"] = kept
        return data, removed

    return _update_registry(root, mutator)


def release_cmd(root, agent, feature):
    # A featureless claim is real — LEGACY_FEATURE exists for exactly those, and `_matches`
    # reads them as `claim.get("feature", LEGACY_FEATURE)`.
    #
    # Passing that `None` through did NOT raise, which is what makes it worth guarding:
    # `shlex.quote` starts `if not s: return "''"`, so `None` rendered as an empty argument
    # and the printed remedy was `--feature ''`. That selector matches no claim at all, so
    # an operator was handed a well-formed command that ran clean and removed nothing.
    # Silent non-remedy, not a crash.
    feature = feature or LEGACY_FEATURE
    parts = [
        "python3",
        os.path.join(root, ".agents/skills/harness/bin/inflight_registry.py"),
        "release",
        "--agent",
        agent,
    ]
    parts.extend(["--feature", feature])
    parts.extend(["--root", root])
    return " ".join(shlex.quote(part) for part in parts)


def refusal_lines(agent, existing, release_command):
    return [
        f"dispatch-guard: BLOCKED - single-flight ({agent})",
        f"  existing claim for {existing.get('feature', LEGACY_FEATURE)} started "
        f"{_iso(existing.get('started_at'))}, dispatched by {existing.get('dispatcher')}",
        "  this is issue #628: a second writer for the same feature could overwrite plan.yaml.",
        "  (the original single-flight report is #551.)",
        f"  {release_command}",
    ]


def children_refusal_lines(agent, children):
    lines = [f"check-digest: BLOCKED - returned with children in flight ({agent})"]
    for persona, claim_entry in children:
        lines.append(
            f"  - {persona} [{claim_entry.get('feature', LEGACY_FEATURE)}] "
            f"started {_iso(claim_entry.get('started_at'))}"
        )
    lines.append(
        "  this is issue #551: a verdict about a member still running is a verdict about "
        "something the reporter cannot see."
    )
    lines.append(
        "  the legal turn-end for a lead or orchestrator whose child is live is VERDICT "
        "SUSPENDED with an awaiting list naming every live child."
    )
    return lines


def _all_live(root, now=None):
    now = now if now is not None else time.time()
    path = _registry_path(root)
    if not os.path.exists(path):
        return []

    def mutator(data):
        live, _expired = _expire(data.get("claims", []), now)
        data["claims"] = live
        return data, live

    return _update_registry(root, mutator)


def _cli_list(root):
    claims = _all_live(root)
    if not claims:
        print("NO CLAIMS")
        return
    for claim_entry in claims:
        print(
            f"{claim_entry.get('feature')}:{claim_entry.get('agent')} "
            f"started={_iso(claim_entry.get('started_at'))} "
            f"dispatcher={claim_entry.get('dispatcher')} runtime={claim_entry.get('runtime')} "
            f"agent_id={claim_entry.get('agent_id')} job_id={claim_entry.get('job_id')}"
        )


def _resolve_root(rest):
    root = None
    if "--root" in rest:
        index = rest.index("--root")
        root = rest[index + 1]
        rest = rest[:index] + rest[index + 2 :]
    if not root:
        try:
            root = harness_boundary.resolve_root(os.path.dirname(os.path.abspath(__file__)))
        except ValueError:
            root = None
    return root, rest


def _option(rest, name):
    if name not in rest:
        return None
    index = rest.index(name)
    return rest[index + 1]


def main(argv=None):
    argv = list(argv) if argv is not None else sys.argv[1:]
    if not argv:
        print(
            "usage: inflight_registry.py {list|attach|release|release-all|reconcile|feature-root} [options]",
            file=sys.stderr,
        )
        return 1
    command = argv[0]
    root, rest = _resolve_root(argv[1:])
    if not root:
        print("inflight_registry: no checkout root and no --root was given", file=sys.stderr)
        return 1

    if command == "feature-root":
        feature = _option(rest, "--feature")
        if not feature:
            print("inflight_registry: feature-root requires --feature", file=sys.stderr)
            return 1
        print(feature_root(root, feature))
        return 0
    if command == "list":
        _cli_list(root)
        return 0
    if command == "attach":
        agent = _option(rest, "--agent")
        feature = _option(rest, "--feature")
        if not agent or not feature:
            print("inflight_registry: attach requires --agent and --feature", file=sys.stderr)
            return 1
        ok = attach_runtime_identity(
            root,
            agent,
            feature,
            agent_id=_option(rest, "--agent-id"),
            job_id=_option(rest, "--job-id"),
            claim_id=_option(rest, "--claim-id"),
        )
        return 0 if ok else 1
    if command == "release":
        selector = any(
            _option(rest, name)
            for name in ("--agent", "--claim-id", "--agent-id", "--job-id")
        )
        if not selector:
            print("inflight_registry: release requires a claim selector", file=sys.stderr)
            return 1
        removed = release(
            root,
            agent=_option(rest, "--agent"),
            feature=_option(rest, "--feature"),
            claim_id=_option(rest, "--claim-id"),
            agent_id=_option(rest, "--agent-id"),
            job_id=_option(rest, "--job-id"),
        )
        return 0 if removed is not False else 1
    if command == "release-all":
        release_all(root)
        return 0
    if command == "reconcile":
        feature = _option(rest, "--feature")
        target_root = feature_root(root, feature) if feature else root
        removed = reconcile(target_root, feature=feature)
        print(f"RECONCILED {removed}")
        return 0
    print(f"inflight_registry: unknown command {command!r}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
