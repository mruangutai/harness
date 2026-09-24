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


class UnreadableRegistry(Exception):
    """One or more existing claim registries could not be read safely."""

    def __init__(self, paths):
        if isinstance(paths, (str, bytes, os.PathLike)):
            paths = [paths]
        self.paths = tuple(sorted({os.fspath(path) for path in paths}))
        super().__init__(
            "unreadable in-flight claim registries: " + ", ".join(self.paths)
        )


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
    """A claim is live only while its OMP supervisor is (DEC-204). Any claim that carries
    another runtime, or none, is expired: there is no other host (DEC-233)."""
    live = []
    expired = 0
    for claim in claims:
        if not isinstance(claim, dict):
            expired += 1
            continue
        if claim.get("released_at") is not None:
            expired += 1
            continue
        started = claim.get("started_at")
        if not isinstance(started, (int, float)) or isinstance(started, bool):
            expired += 1
            continue
        if claim.get("runtime") == "omp" and _omp_claim_live(claim, now):
            live.append(claim)
        else:
            expired += 1
    return live, expired

def _expire_where(claims, now, predicate):
    """Expire the claims `predicate` selects; the rest pass through untouched.
    Returns (answer_live, retained, expired): `retained` is what stays on disk."""
    answer_live = []
    retained = []
    expired = 0
    for claim in claims:
        if not predicate(claim):
            answer_live.append(claim)
            retained.append(claim)
            continue
        live, count = _expire([claim], now)
        answer_live.extend(live)
        retained.extend(live)
        expired += count
    return answer_live, retained, expired


def _matches(claim, agent=None, feature=None, claim_id=None, agent_id=None, job_id=None,
             parent_agent_id=None):
    if not isinstance(claim, dict):
        return False
    return (
        (agent is None or claim.get("agent") == agent)
        and (feature is None or claim.get("feature", LEGACY_FEATURE) == feature)
        and (claim_id is None or claim.get("claim_id") == claim_id)
        and (agent_id is None or claim.get("agent_id") == agent_id)
        and (job_id is None or claim.get("job_id") == job_id)
        and (parent_agent_id is None
             or claim.get("parent_agent_id") == parent_agent_id)
    )


def _visible(claim, feature=None):
    return feature is None or claim.get("feature", LEGACY_FEATURE) == feature


def live_claims(root, agent, now=None, agent_id=None, parent_agent_id=None):
    """Return claims that still bind ``agent`` to worktrees, without mutating state."""
    path = _registry_path(root)
    try:
        with open(path, "r", encoding="utf-8", errors="strict") as handle:
            text = handle.read()
    except FileNotFoundError:
        return []
    except (OSError, UnicodeError) as error:
        raise UnreadableRegistry(path) from error

    try:
        raw = json.loads(text)
    except (json.JSONDecodeError, ValueError) as error:
        raise UnreadableRegistry(path) from error
    if not isinstance(raw, dict):
        raise UnreadableRegistry(path)
    is_v2 = (
        raw.get("schema_version") == SCHEMA_VERSION
        and isinstance(raw.get("claims"), list)
    )
    is_v1 = (
        "schema_version" not in raw
        and all(isinstance(key, str) and isinstance(entries, list)
                for key, entries in raw.items())
    )
    if not (is_v2 or is_v1):
        raise UnreadableRegistry(path)

    live, _expired = _expire(
        [
            claim
            for claim in _parse(text, path)["claims"]
            if _matches(
                claim,
                agent=agent,
                agent_id=agent_id,
                parent_agent_id=parent_agent_id,
            )
            and _visible(claim)
        ],
        time.time() if now is None else now,
    )
    return sorted(live, key=lambda claim: claim["started_at"])


def is_single_flight(agent):
    return agent in SINGLE_FLIGHT_AGENTS

def feature_root(owner_root, feature):
    """Resolve the checkout assigned to `feature`, falling back to the supplied owner root."""
    try:
        resolved = harness_boundary.worktree_for_feature(owner_root, feature)
    except Exception:
        return owner_root
    return resolved if resolved is not None else owner_root


def live_claim(root, agent, now=None, feature=None):
    now = now if now is not None else time.time()
    path = _registry_path(root)
    if not os.path.exists(path):
        return None, 0

    def mutator(data):
        live, retained, expired = _expire_where(
            data.get("claims", []),
            now,
            lambda claim: _matches(claim, agent=agent, feature=feature),
        )
        data["claims"] = retained
        visible = [c for c in live if _matches(c, agent=agent) and _visible(c, feature)]
        oldest = min(visible, key=lambda c: c["started_at"]) if visible else None
        return data, (oldest, expired)

    return _update_registry(root, mutator)


def live_children(root, dispatcher, now=None, feature=None):
    now = now if now is not None else time.time()
    path = _registry_path(root)
    if not os.path.exists(path):
        return []

    def mutator(data):
        live, retained, _expired = _expire_where(
            data.get("claims", []),
            now,
            lambda claim: _matches(claim, feature=feature)
            and isinstance(claim, dict)
            and claim.get("dispatcher") == dispatcher,
        )
        data["claims"] = retained
        children = [
            (c.get("agent"), c)
            for c in live
            if c.get("dispatcher") == dispatcher and _visible(c, feature)
        ]
        return data, children

    return _update_registry(root, mutator)


def claim_with_receipt(
    root,
    agent,
    dispatcher,
    cwd,
    now=None,
    feature=LEGACY_FEATURE,
    supervisor_pid=None,
    repository=None,
    dispatch_correlation=None,
):
    """Record a claim owned by `supervisor_pid` — the OMP process that holds the dispatching
    `task` call (DEC-204). Absent, the claiming process is the supervisor: that is what a
    direct caller (the CLI, a test) is. dispatch-guard.py always passes the host's pid."""
    now = now if now is not None else time.time()
    supervisor_pid = os.getpid() if supervisor_pid is None else supervisor_pid

    def mutator(data):
        live, retained, _expired = _expire_where(
            data.get("claims", []),
            now,
            lambda claim: _matches(claim, agent=agent, feature=feature),
        )
        if is_single_flight(agent) and any(
            _matches(c, agent=agent, feature=feature) for c in live
        ):
            data["claims"] = retained
            return data, None
        entry = {
            "claim_id": uuid.uuid4().hex,
            "started_at": now,
            "feature": feature,
            "agent": agent,
            "dispatcher": dispatcher,
            "cwd": cwd,
            "runtime": "omp",
            "supervisor_pid": supervisor_pid,
        }
        # Pinned at claim time so a later recycled pid can be told apart from this one.
        # Absent when the OS declines to report it; `_omp_claim_live` then falls back
        # to OMP_UNVERIFIED_TTL_SECONDS rather than trusting the bare pid.
        started_at = _process_start_time(supervisor_pid)
        if started_at is not None:
            entry["supervisor_started_at"] = started_at
        if repository is not None:
            entry["repository"] = repository
        if dispatch_correlation is not None:
            entry["dispatch_correlation"] = dict(dispatch_correlation)
        live.append(entry)
        retained.append(entry)
        data["claims"] = retained
        return data, dict(entry)

    return _update_registry(root, mutator)


def claim(root, agent, dispatcher, cwd, now=None, feature=LEGACY_FEATURE,
          supervisor_pid=None, repository=None, dispatch_correlation=None):
    return claim_with_receipt(
        root,
        agent,
        dispatcher,
        cwd,
        now=now,
        feature=feature,
        supervisor_pid=supervisor_pid,
        repository=repository,
        dispatch_correlation=dispatch_correlation,
    ) is not None


def _identity_registry_roots(root):
    """Registries that can already own an OMP runtime id visible from ``root``."""
    owner = harness_boundary.worktree_owner(root)
    owner_root = owner[1] if owner and owner[1] else root
    roots = [owner_root] + harness_boundary.linked_worktrees(owner_root)
    return sorted({os.path.realpath(item) for item in roots})


def _live_registry_claims(root, now):
    """Strict, read-only live claims for collision checks."""
    path = _registry_path(root)
    try:
        with open(path, "r", encoding="utf-8", errors="strict") as handle:
            text = handle.read()
    except FileNotFoundError:
        return []
    except (OSError, UnicodeError) as error:
        raise UnreadableRegistry(path) from error
    try:
        raw = json.loads(text)
    except (json.JSONDecodeError, ValueError) as error:
        raise UnreadableRegistry(path) from error
    if (
        not isinstance(raw, dict)
        or raw.get("schema_version") != SCHEMA_VERSION
        or not isinstance(raw.get("claims"), list)
    ):
        raise UnreadableRegistry(path)
    live, _expired = _expire(raw["claims"], now)
    return live


def _foreign_identity_collision(
    root,
    claim_id,
    feature,
    agent_id,
    parent_agent_id,
    now,
    expected_child=None,
):
    """Whether another active dispatch already owns the requested host lineage."""
    child_claims = []
    parent_claims = []
    for registry_root in _identity_registry_roots(root):
        for claim in _live_registry_claims(registry_root, now):
            if claim.get("claim_id") == claim_id:
                continue
            if agent_id and claim.get("agent_id") == agent_id:
                child_claims.append(claim)
            if parent_agent_id and claim.get("agent_id") == parent_agent_id:
                parent_claims.append(claim)
    if child_claims:
        if expected_child is None or len(child_claims) != 1:
            return True
        expected_agent, expected_feature, expected_parent, expected_repository = expected_child
        child = child_claims[0]
        if (
            child.get("agent") != expected_agent
            or child.get("feature", LEGACY_FEATURE) != expected_feature
            or child.get("parent_agent_id") != expected_parent
            or child.get("repository") != expected_repository
        ):
            return True
    return (
        len(parent_claims) > 1
        or any(claim.get("feature", LEGACY_FEATURE) != feature for claim in parent_claims)
    )


def attach_runtime_identity_state(
    root,
    agent,
    feature,
    agent_id=None,
    job_id=None,
    claim_id=None,
    parent_agent_id=None,
    repository=None,
):
    """Attach stable OMP runtime lineage, returning a named authorization state."""
    path = _registry_path(root)
    if not os.path.exists(path) or not (agent_id or job_id or parent_agent_id):
        return "missing"
    now = time.time()
    try:
        if _foreign_identity_collision(
                root, claim_id, feature, agent_id, parent_agent_id, now):
            return "collision"
    except UnreadableRegistry:
        return "unreadable"

    # GRADE-2 REASON: selection, collision detection, and identity mutation must
    # remain inside one locked registry update; splitting them reintroduces TOCTOU.
    def mutator(data):
        live, retained, _expired = _expire_where(
            data.get("claims", []),
            now,
            lambda claim: _matches(
                claim, agent=agent, feature=feature, claim_id=claim_id
            ),
        )
        scoped = [
            claim for claim in live
            if _matches(claim, agent=agent, feature=feature, claim_id=claim_id)
        ]
        exact_repository = [
            claim for claim in scoped
            if claim.get("repository") == repository
        ]
        if any(
            (agent_id and claim.get("agent_id") not in (None, "", agent_id))
            or (job_id and claim.get("job_id") not in (None, "", job_id))
            or (
                parent_agent_id
                and claim.get("parent_agent_id") not in (None, "", parent_agent_id)
            )
            for claim in exact_repository
        ):
            data["claims"] = retained
            return data, "collision"
        candidates = [
            claim for claim in exact_repository
            if (not agent_id or claim.get("agent_id") in (None, "", agent_id))
            and (not job_id or claim.get("job_id") in (None, "", job_id))
            and (
                not parent_agent_id
                or claim.get("parent_agent_id") in (None, "", parent_agent_id)
            )
        ]
        if len(candidates) != 1:
            data["claims"] = retained
            return data, "ambiguous" if len(candidates) > 1 else "missing"
        target = candidates[0]
        if agent_id:
            target["agent_id"] = agent_id
        if job_id:
            target["job_id"] = job_id
        if parent_agent_id:
            target["parent_agent_id"] = parent_agent_id
        data["claims"] = retained
        return data, "attached"

    return _update_registry(root, mutator)


def attach_runtime_identity(root, agent, feature, agent_id=None, job_id=None, claim_id=None,
                            parent_agent_id=None, repository=None):
    return attach_runtime_identity_state(
        root,
        agent,
        feature,
        agent_id=agent_id,
        job_id=job_id,
        claim_id=claim_id,
        parent_agent_id=parent_agent_id,
        repository=repository,
    ) == "attached"


def authorize_runtime_identity_state(
    root, agent, feature, agent_id, parent_agent_id, repository=None,
):
    """Authorize and, when unique, bind an OMP child to its parent claim."""
    path = _registry_path(root)
    if not os.path.exists(path) or not all((agent, feature, agent_id, parent_agent_id)):
        return "missing"
    now = time.time()
    try:
        if _foreign_identity_collision(
            root,
            None,
            feature,
            agent_id,
            parent_agent_id,
            now,
            expected_child=(agent, feature, parent_agent_id, repository),
        ):
            return "collision"
    except UnreadableRegistry:
        return "unreadable"

    # GRADE-2 REASON: exact-match selection, unique unbound fallback, collision
    # detection, and binding form one locked authorization transaction.
    def mutator(data):
        live, retained, _expired = _expire_where(
            data.get("claims", []),
            now,
            lambda claim: _matches(claim, agent=agent, feature=feature),
        )
        candidates = [
            claim for claim in live
            if _matches(
                claim,
                agent=agent,
                feature=feature,
                parent_agent_id=parent_agent_id,
            )
            and claim.get("runtime") == "omp"
            and claim.get("repository") == repository
            and claim.get("agent_id") in (None, "", agent_id)
        ]
        exact = [claim for claim in candidates if claim.get("agent_id") == agent_id]
        if len(exact) == 1:
            selected = exact[0]
        elif len(exact) > 1:
            data["claims"] = retained
            return data, "collision"
        else:
            unbound = [claim for claim in candidates if not claim.get("agent_id")]
            if len(unbound) != 1:
                data["claims"] = retained
                return data, "ambiguous" if len(unbound) > 1 else "missing"
            selected = unbound[0]
        selected["agent_id"] = agent_id
        data["claims"] = retained
        return data, "authorized"

    return _update_registry(root, mutator)


def authorize_runtime_identity(
    root, agent, feature, agent_id, parent_agent_id, repository=None,
):
    return authorize_runtime_identity_state(
        root,
        agent,
        feature,
        agent_id,
        parent_agent_id,
        repository=repository,
    ) == "authorized"

def repository_binding(
    root,
    agent,
    feature,
    repository,
    agent_id,
    parent_agent_id,
    now=None,
):
    """Return the fail-closed state of one exact factory repository binding."""
    if not all((agent, feature, repository, agent_id, parent_agent_id)):
        return "missing"
    path = _registry_path(root)
    try:
        with open(path, "r", encoding="utf-8", errors="strict") as handle:
            raw = json.load(handle)
        if (
            not isinstance(raw, dict)
            or raw.get("schema_version") != SCHEMA_VERSION
            or not isinstance(raw.get("claims"), list)
        ):
            return "unreadable"
    except FileNotFoundError:
        return "missing"
    except (OSError, UnicodeError, ValueError):
        return "unreadable"

    current = time.time() if now is None else now
    identity_claims = [
        claim for claim in raw["claims"]
        if isinstance(claim, dict) and claim.get("agent_id") == agent_id
    ]
    exact = [
        claim for claim in identity_claims
        if _matches(
            claim,
            agent=agent,
            feature=feature,
            agent_id=agent_id,
            parent_agent_id=parent_agent_id,
        )
        and claim.get("repository") == repository
    ]
    live_exact, _expired = _expire(exact, current)
    live_identity, _identity_expired = _expire(identity_claims, current)
    foreign_dispatch = [
        claim for claim in live_identity
        if claim not in live_exact
        and (
            claim.get("agent") != agent
            or claim.get("feature", LEGACY_FEATURE) != feature
        )
    ]
    if len(live_exact) > 1:
        return "ambiguous"
    if foreign_dispatch or len(live_identity) > 1:
        return "collision"
    if len(live_exact) == 1:
        return "allow"
    if any(claim.get("released_at") is not None for claim in exact):
        return "released"
    if exact:
        return "stale"
    same_dispatch = [
        claim for claim in identity_claims
        if _matches(claim, agent=agent, feature=feature, agent_id=agent_id)
    ]
    if same_dispatch:
        return "mismatched"
    return "missing"

REPOSITORY_BINDING_STATES = frozenset({
    "missing", "collision", "mismatched", "stale",
    "released", "unreadable", "ambiguous",
})


def repository_binding_refusal(agent, repository, state):
    """Return the shared, non-sensitive refusal text for a binding state."""
    rendered = state if state in REPOSITORY_BINDING_STATES else "unreadable"
    return (
        f"{agent} has a {rendered} runtime repository binding for {repository}.",
        "Product writes require one active claim matching the authenticated child, "
        "its immediate parent, feature, role, and repository. Retry from the dispatch "
        "that owns this product.",
    )




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
        live, retained, _expired = _expire_where(
            data.get("claims", []), time.time(), selector_matches
        )
        matches = [claim for claim in live if selector_matches(claim)]
        if not matches:
            data["claims"] = retained
            return data, False
        if len(matches) != 1:
            selector = claim_id or agent_id or job_id or f"{feature or '*'}:{agent or '*'}"
            print(
                f"inflight_registry: release({selector!r}) is refusing — {len(matches)} live "
                "claims match; removing none rather than guessing.",
                file=sys.stderr,
            )
            data["claims"] = retained
            return data, 0
        target = matches[0]
        if target.get("repository") is not None:
            target["released_at"] = time.time()
            data["claims"] = retained
            return data, True
        target_id = target.get("claim_id")
        data["claims"] = [
            claim for claim in retained if claim.get("claim_id") != target_id
        ]
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
        kept = []
        removed = 0
        for claim_entry in data.get("claims", []):
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
        "  a lead or orchestrator cannot yield while a child is live: the host holds the "
        "task call until every child is terminal (DEC-204, DEC-233)."
    )
    return lines


def _all_live(root, now=None):
    now = now if now is not None else time.time()
    path = _registry_path(root)
    if not os.path.exists(path):
        return []

    def mutator(data):
        live, retained, _expired = _expire_where(
            data.get("claims", []), now, lambda _claim: True
        )
        data["claims"] = retained
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


def _feature_root_command(root, rest):
    feature = _option(rest, "--feature")
    if not feature:
        print("inflight_registry: feature-root requires --feature", file=sys.stderr)
        return 1
    try:
        resolved = harness_boundary.worktree_for_feature(root, feature)
    except harness_boundary.AmbiguousWorktree as exc:
        print("inflight_registry: feature-root is ambiguous for %s (%s)" % (feature, exc),
              file=sys.stderr)
        return 1
    print(resolved if resolved is not None else root)
    return 0

def _list_command(root, _rest):
    _cli_list(root)
    return 0


def _attach_command(root, rest):
    agent = _option(rest, "--agent")
    feature = _option(rest, "--feature")
    if not agent or not feature:
        print("inflight_registry: attach requires --agent and --feature", file=sys.stderr)
        return 1
    state = attach_runtime_identity_state(
        root,
        agent,
        feature,
        agent_id=_option(rest, "--agent-id"),
        job_id=_option(rest, "--job-id"),
        claim_id=_option(rest, "--claim-id"),
        parent_agent_id=_option(rest, "--parent-agent-id"),
        repository=_option(rest, "--repository"),
    )
    if state == "attached":
        return 0
    print(
        "inflight_registry: %s - runtime lineage attach %s"
        % ("BLOCKED" if state in ("collision", "ambiguous", "unreadable") else "refused", state),
        file=sys.stderr,
    )
    return 2 if state in ("collision", "ambiguous", "unreadable") else 1


def _authorize_command(root, rest):
    agent = _option(rest, "--agent")
    feature = _option(rest, "--feature")
    agent_id = _option(rest, "--agent-id")
    parent_agent_id = _option(rest, "--parent-agent-id")
    if not all((agent, feature, agent_id, parent_agent_id)):
        print(
            "inflight_registry: authorize requires --agent, --feature, "
            "--agent-id, and --parent-agent-id",
            file=sys.stderr,
        )
        return 1
    target_root = feature_root(root, feature)
    state = authorize_runtime_identity_state(
        target_root,
        agent,
        feature,
        agent_id,
        parent_agent_id,
        repository=_option(rest, "--repository"),
    )
    if state == "authorized":
        return 0
    print(
        "inflight_registry: BLOCKED - runtime child lineage %s"
        % ("identity collision" if state == "collision" else state),
        file=sys.stderr,
    )
    return 2


def _release_command(root, rest):
    selector_names = ("--agent", "--claim-id", "--agent-id", "--job-id")
    if not any(_option(rest, name) for name in selector_names):
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


def _release_all_command(root, _rest):
    release_all(root)
    return 0


def _reconcile_command(root, rest):
    feature = _option(rest, "--feature")
    target_root = feature_root(root, feature) if feature else root
    removed = reconcile(target_root, feature=feature)
    print(f"RECONCILED {removed}")
    return 0


COMMANDS = {
    "feature-root": _feature_root_command,
    "list": _list_command,
    "attach": _attach_command,
    "authorize": _authorize_command,
    "release": _release_command,
    "release-all": _release_all_command,
    "reconcile": _reconcile_command,
}




def main(argv=None):
    argv = list(argv) if argv is not None else sys.argv[1:]
    if not argv:
        print(
            "usage: inflight_registry.py {list|attach|authorize|release|release-all|reconcile|feature-root} [options]",
            file=sys.stderr,
        )
        return 1
    command = argv[0]
    root, rest = _resolve_root(argv[1:])
    if not root:
        print("inflight_registry: no checkout root and no --root was given", file=sys.stderr)
        return 1

    handler = COMMANDS.get(command)
    if handler is None:
        print(f"inflight_registry: unknown command {command!r}", file=sys.stderr)
        return 1
    return handler(root, rest)


if __name__ == "__main__":
    raise SystemExit(main())
