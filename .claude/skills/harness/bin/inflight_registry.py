#!/usr/bin/env python3
"""inflight_registry.py — the single-flight claim store (FEAT-32 T-06, D-06, D-09).

A small interface (seven public functions plus a three-verb CLI) over a locked JSON store. The
ONE seam is harness_merge.locked_update — every read-modify-write of the registry file crosses
it, and this module never opens its own locking or atomic-rename primitive (case 10 of
test-inflight-registry.py asserts both halves of that).

The registry is a JSON object mapping a persona name to a LIST of claim objects, each holding
started_at (unix float), dispatcher (the dispatching persona name, or None) and cwd (the
checkout it was claimed in). A list, not one object per persona, because two harness-backend-dev
members in flight at once is legal and one object could not hold both (D-06).

Root resolution: every public function takes an explicit `root` — the checkout root. The CLI
resolves that root through harness_boundary.resolve_root (the one project-dir override, the
derived-from-script-location fallback), overridable by an explicit --root argument — the
operator's manual escape hatch — so two worktrees never contend over the same file.

A missing, empty or unparseable registry file is treated as an EMPTY registry and reported on
stderr — never an exception out of a hook. Failing OPEN on a leaked claim, not closed, is the
house precedent for a guard's own bug (see validate-digest.py's hook_mode pass-through, whose
stderr line ends "this is our bug, not theirs").
"""
import datetime
import json
import os
import sys
import time

import harness_boundary
import harness_merge

# Module-level literals. Each is mutated BY NAME in a copy of the tree by the test's red proof.
SINGLE_FLIGHT_AGENTS = ("harness-pm",)

# 1200s = one pm cycle (10-20 minutes), not the four cycles 3600 used to allow. The cost is
# real, not hidden: a legitimate run longer than 20 minutes loses its single-flight protection.
# That is preferred to the alternative measured on 2026-08-26 — a strand that locks a tier
# chain out of reporting until an hour-long timer expires.
CLAIM_TTL_SECONDS = 1200

# The registry is written by HOOKS, on every spawn. harness_merge's 10s default is right for a
# file merge and wrong here: a registry read-modify-write is milliseconds, so a lock still held
# after a second means the holder is STUCK, not busy, and hanging the dispatch to discover that
# buys nothing. Giving up fast and failing OPEN loudly is D-07's posture. Named so a measurement
# can move it; the four file-merge callers keep the 10s default untouched.
LOCK_TIMEOUT_SECONDS = 1.0
REGISTRY_REL = ".harness/.inflight-claims.json"

# RETIRED as a printed remedy at T-06 (FEAT-42): release_cmd(root, agent) below is what a
# refusal prints now — absolute and single-agent, where this was relative and release-all.
# Kept as a plain literal, not built from a deleted constant, ONLY because dispatch-guard.sh:115
# still reads this name inside its refusal branch; an AttributeError there is swallowed by that
# script's broad except and turns into a fail-open dispatch (measured, not assumed — see T-06's
# receipt). T-18 removes this constant together with the dispatch-guard.sh callsite that reads it.
RELEASE_ALL_CMD = "python3 .agents/skills/harness/bin/inflight_registry.py release-all"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _registry_path(root):
    return os.path.join(root, REGISTRY_REL)


def _parse(base, path):
    """base is the raw bytes read by locked_update, or None if the file did not exist. Any
    failure to produce a JSON object is reported on stderr and treated as an empty registry —
    never raised out of this module."""
    if base is None:
        return {}
    text = base.decode("utf-8", errors="replace") if isinstance(base, bytes) else base
    if not text.strip():
        return {}
    try:
        data = json.loads(text)
    except (json.JSONDecodeError, ValueError):
        print(f"inflight_registry: {path} is corrupt or unparseable, treating as empty", file=sys.stderr)
        return {}
    if not isinstance(data, dict):
        print(f"inflight_registry: {path} is not a JSON object, treating as empty", file=sys.stderr)
        return {}
    return data


def _set_or_pop(data, agent, live):
    if live:
        data[agent] = live
    else:
        data.pop(agent, None)


def _expire(claims, now):
    """Split claims into (live, expired_count). A claim older than CLAIM_TTL_SECONDS is treated
    as ABSENT."""
    live = []
    expired = 0
    for c in claims:
        # PER-CLAIM TOLERANCE, and it is not defensive padding. This runs UPSTREAM of the
        # single-flight test in dispatch-guard.sh, so a single malformed entry raising here
        # took the whole #628 refusal down SILENTLY -- the guard caught the exception and
        # failed open, which is right for the dispatch and wrong as a way to lose the check.
        # A claim we cannot read is treated as expired: it cannot be released by name either,
        # so keeping it would refuse a legitimate dispatch until its TTL, and the TTL cannot
        # be computed for an entry whose started_at is unreadable.
        if not isinstance(c, dict):
            expired += 1
            continue
        started = c.get("started_at")
        if not isinstance(started, (int, float)):
            expired += 1
            continue
        if now - started > CLAIM_TTL_SECONDS:
            expired += 1
        else:
            live.append(c)
    return live, expired


def _update_registry(root, mutator):
    """mutator(data: dict) -> (new_data, result). Runs entirely inside a single
    harness_merge.locked_update transform, so the read, the mutation and the write are one
    atomic step under the shared lock. Returns the mutator's result to the caller — locked_update
    itself returns nothing, so the result travels out via a closure cell."""
    path = _registry_path(root)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    result_holder = {}

    def transform(base):
        data = _parse(base, path)
        new_data, result = mutator(data)
        result_holder["result"] = result
        return (json.dumps(new_data, indent=2, sort_keys=True) + "\n").encode("utf-8")

    harness_merge.locked_update(path, transform, timeout=LOCK_TIMEOUT_SECONDS)
    return result_holder["result"]


def _iso(ts):
    return datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def is_single_flight(agent):
    return agent in SINGLE_FLIGHT_AGENTS


def _filter_session(claims, session):
    """The SESSION filter (T-06 item 3), applied ON TOP OF _expire's TTL filter, never in place
    of it. When the caller supplies a session and an entry carries a DIFFERENT one, that entry
    is not live for this query, whatever its age — this is what kills a cross-session strand
    outright instead of waiting out CLAIM_TTL_SECONDS. It is NOT removed from disk: it is not
    actually expired, only foreign to this caller, and its own session must still find it.
    An entry with no recorded session always matches, so nothing already on disk changes
    meaning. session=None (the default) disables the filter entirely — today's behaviour."""
    if session is None:
        return list(claims)
    return [c for c in claims if c.get("session") in (None, session)]


def live_claim(root, agent, now=None, session=None):
    """Returns (oldest_live_claim_or_None, expired_count) for agent. Any claim older than
    CLAIM_TTL_SECONDS is deleted as a side effect. `expired_count` counts only TTL expiry —
    a claim filtered out by `session` is neither expired nor deleted, see _filter_session."""
    now = now if now is not None else time.time()
    path = _registry_path(root)
    if not os.path.exists(path):
        return None, 0

    def mutator(data):
        claims = data.get(agent, [])
        live, expired = _expire(claims, now)
        _set_or_pop(data, agent, live)
        visible = _filter_session(live, session)
        oldest = min(visible, key=lambda c: c["started_at"]) if visible else None
        return data, (oldest, expired)

    return _update_registry(root, mutator)


def live_children(root, dispatcher, now=None, session=None):
    """Returns the list of (persona, claim) pairs whose claim's dispatcher equals `dispatcher`,
    expiring stale claims across the WHOLE registry as it scans. `session`, when supplied,
    filters out entries carrying a different session — see _filter_session."""
    now = now if now is not None else time.time()
    path = _registry_path(root)
    if not os.path.exists(path):
        return []

    def mutator(data):
        result = []
        for persona in list(data.keys()):
            claims = data.get(persona, [])
            live, _expired = _expire(claims, now)
            _set_or_pop(data, persona, live)
            for c in _filter_session(live, session):
                if c.get("dispatcher") == dispatcher:
                    result.append((persona, c))
        return data, result

    return _update_registry(root, mutator)


def claim(root, agent, dispatcher, cwd, now=None, session=None):
    """Appends a claim and returns True, unless is_single_flight(agent) and a live claim for
    agent already exists — in which case nothing is recorded and this returns False.

    `session`, when supplied, is recorded in the entry alongside started_at, dispatcher and
    cwd — it is what live_claim/live_children later use to tell a foreign session's stale-
    looking claim from this session's live one (T-06 item 3). The single-flight check above
    is unaffected: it stays TTL-only, matching today's behaviour for every existing caller
    that never passes a session.

    IT DOES RAISE. The single-flight refusal returns False rather than raising, and an earlier
    version of this docstring generalised that into "never raises for contention", which is
    false: LOCK contention raises harness_merge.MergeRefusal once the deadline passes.
    Measured, not reasoned — with the lock held it raised after exactly the deadline.
    EVERY HOOK CALLER MUST WRAP THIS. An uncaught exception in a PreToolUse hook exits
    non-zero and the dispatch is affected, which inverts D-07's fail-open posture — the exact
    outcome the refusal path was written to avoid.
    """
    now = now if now is not None else time.time()

    def mutator(data):
        claims_list = data.get(agent, [])
        live, _expired = _expire(claims_list, now)
        if is_single_flight(agent) and live:
            _set_or_pop(data, agent, live)
            return data, False
        entry = {"started_at": now, "dispatcher": dispatcher, "cwd": cwd}
        if session is not None:
            entry["session"] = session
        live.append(entry)
        data[agent] = live
        return data, True

    return _update_registry(root, mutator)


def release(root, agent):
    """Removes agent's SOLE live claim. Returns True if one was removed, False if none existed,
    or the int 0 if MORE THAN ONE live claim exists and nothing was removed. Expired entries
    are swept from the registry in every case. Never creates the registry file when there is
    nothing to release.

    THIS USED TO POP OLDEST(started_at) UNCONDITIONALLY — the defect measured live on
    2026-08-26 (issue #628): the stop hook released an abandoned run's claim and left the
    returning lead's own claim stranded. There is no identity on either payload — the dispatch
    payload has tool_use_id, the stop payload has agent_id, and the sidecar join between them is
    unbuilt and rests on an undocumented format — so with two or more live claims for the same
    agent, NOTHING here can tell which one belongs to the caller. Guessing (oldest, newest, or
    otherwise) is a silent chance of releasing the wrong holder's claim; refusing is the only
    answer without a name."""
    path = _registry_path(root)
    if not os.path.exists(path):
        return False

    def mutator(data):
        claims_list = data.get(agent, [])
        live, _expired = _expire(claims_list, time.time())
        _set_or_pop(data, agent, live)
        if not live:
            return data, False
        if len(live) > 1:
            print(
                f"inflight_registry: release({agent!r}) is refusing — {len(live)} live claims "
                "exist and nothing on either payload can match one to its holder (issue #628). "
                "Removing none rather than guessing which one to release.",
                file=sys.stderr,
            )
            return data, 0
        _set_or_pop(data, agent, [])
        return data, True

    return _update_registry(root, mutator)


def release_all(root):
    """Removes every claim. Returns how many were removed."""
    path = _registry_path(root)
    if not os.path.exists(path):
        return 0

    def mutator(data):
        count = sum(len(v) for v in data.values())
        return {}, count

    return _update_registry(root, mutator)


def release_cmd(root, agent):
    """The absolute, single-agent remedy a refusal prints (T-06 item 5, issue #628). Never
    release_all: that command wipes every claim of every agent, and the relative path the old
    remedy was built from only resolved when cwd happened to be `root`, which a refused caller
    cannot be relied on to be standing in."""
    return (
        f"python3 {root}/.agents/skills/harness/bin/inflight_registry.py "
        f"release --agent {agent} --root {root}"
    )


def refusal_lines(agent, existing, release_cmd):
    """The exact stderr block a single-flight caller prints (issue #628).

    `release_cmd` is a parameter, not the module-level function of the same name above — the
    CALLER chooses the command to print (today, dispatch-guard.sh still passes the retired
    RELEASE_ALL_CMD; see T-06's receipt for why deleting that constant was refused). The
    module-level `release_cmd` is shadowed inside this function's body and unused by it; that is
    legal and deliberate — minimal diff until T-18 rewires the caller.
    """
    started_iso = _iso(existing.get("started_at"))
    dispatcher = existing.get("dispatcher")
    return [
        f"dispatch-guard: BLOCKED - single-flight ({agent})",
        f"  existing claim started {started_iso}, dispatched by {dispatcher}",
        "  this is issue #628: the second writer would otherwise overwrite the first's plan.yaml.",
        "  (the original single-flight report is #551.)",
        f"  {release_cmd}",
    ]


def children_refusal_lines(agent, children):
    """The exact stderr block validate-digest.py prints under D-09, for `agent` returning while
    `children` (a list of (persona, claim) pairs) are still in flight."""
    lines = [f"check-digest: BLOCKED - returned with children in flight ({agent})"]
    for persona, c in children:
        lines.append(f"  - {persona} started {_iso(c.get('started_at'))}")
    lines.append(
        "  this is issue #551: a verdict about a member still running is a verdict about "
        "something the reporter cannot see."
    )
    lines.append(
        "  this refusal fires at most once per consecutive stop sequence; an immediate second "
        "identical return ships, and it re-fires on a later wake while a child is still live — "
        "correct any claim about a child you cannot see and end the turn again."
    )
    return lines


# ---------------------------------------------------------------------------
# CLI — the operator's escape hatch
# ---------------------------------------------------------------------------


def _all_live(root, now=None):
    now = now if now is not None else time.time()
    path = _registry_path(root)
    if not os.path.exists(path):
        return []

    def mutator(data):
        result = []
        for persona in list(data.keys()):
            claims_list = data.get(persona, [])
            live, _expired = _expire(claims_list, now)
            _set_or_pop(data, persona, live)
            for c in live:
                result.append((persona, c))
        return data, result

    return _update_registry(root, mutator)


def _cli_list(root):
    claims_list = _all_live(root)
    if not claims_list:
        print("NO CLAIMS")
        return
    for persona, c in claims_list:
        print(
            f"{persona} started={_iso(c.get('started_at'))} "
            f"dispatcher={c.get('dispatcher')} cwd={c.get('cwd')}"
        )


def _resolve_root(rest):
    """The ONE root implementation (T-06 item 1): harness_boundary.resolve_root, never a
    second, locally-invented environment chain. --root stays ahead of it — the operator's
    manual escape hatch — because a chain neither of us derives is the one an operator must be
    able to override outright."""
    root = None
    if "--root" in rest:
        i = rest.index("--root")
        root = rest[i + 1]
        rest = rest[:i] + rest[i + 2 :]
    if not root:
        bin_dir = os.path.dirname(os.path.abspath(__file__))
        try:
            root = harness_boundary.resolve_root(bin_dir)
        except ValueError:
            root = None
    return root, rest


def main(argv=None):
    argv = list(argv) if argv is not None else sys.argv[1:]
    if not argv:
        print("usage: inflight_registry.py {list|release|release-all} [--root PATH]", file=sys.stderr)
        return 1

    cmd = argv[0]
    rest = argv[1:]
    root, rest = _resolve_root(rest)
    if not root:
        print(
            "inflight_registry: no checkout root — neither the project-dir override nor this "
            "script's own location carries a checkout marker, and no --root was given",
            file=sys.stderr,
        )
        return 1

    if cmd == "list":
        _cli_list(root)
        return 0
    if cmd == "release":
        agent = None
        if "--agent" in rest:
            i = rest.index("--agent")
            agent = rest[i + 1]
        if not agent:
            print("inflight_registry: release requires --agent NAME", file=sys.stderr)
            return 1
        release(root, agent)
        return 0
    if cmd == "release-all":
        release_all(root)
        return 0

    print(f"inflight_registry: unknown command {cmd!r}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
