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
resolves that root from CLAUDE_PROJECT_DIR when set, otherwise from an explicit --root argument,
so two worktrees never contend over the same file.

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

import harness_merge

# Module-level literals. Each is mutated BY NAME in a copy of the tree by the test's red proof.
SINGLE_FLIGHT_AGENTS = ("harness-pm",)
CLAIM_TTL_SECONDS = 3600
REGISTRY_REL = ".harness/.inflight-claims.json"

CLI_REL_PATH = ".claude/skills/harness/bin/inflight_registry.py"
RELEASE_ALL_CMD = f"python3 {CLI_REL_PATH} release-all"


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
        if now - c.get("started_at", 0) > CLAIM_TTL_SECONDS:
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

    harness_merge.locked_update(path, transform)
    return result_holder["result"]


def _iso(ts):
    return datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def is_single_flight(agent):
    return agent in SINGLE_FLIGHT_AGENTS


def live_claim(root, agent, now=None):
    """Returns (oldest_live_claim_or_None, expired_count) for agent. Any claim older than
    CLAIM_TTL_SECONDS is deleted as a side effect."""
    now = now if now is not None else time.time()
    path = _registry_path(root)
    if not os.path.exists(path):
        return None, 0

    def mutator(data):
        claims = data.get(agent, [])
        live, expired = _expire(claims, now)
        _set_or_pop(data, agent, live)
        oldest = min(live, key=lambda c: c["started_at"]) if live else None
        return data, (oldest, expired)

    return _update_registry(root, mutator)


def live_children(root, dispatcher, now=None):
    """Returns the list of (persona, claim) pairs whose claim's dispatcher equals `dispatcher`,
    expiring stale claims across the WHOLE registry as it scans."""
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
            for c in live:
                if c.get("dispatcher") == dispatcher:
                    result.append((persona, c))
        return data, result

    return _update_registry(root, mutator)


def claim(root, agent, dispatcher, cwd, now=None):
    """Appends a claim and returns True, unless is_single_flight(agent) and a live claim for
    agent already exists — in which case nothing is recorded and this returns False. Never
    raises for contention."""
    now = now if now is not None else time.time()

    def mutator(data):
        claims_list = data.get(agent, [])
        live, _expired = _expire(claims_list, now)
        if is_single_flight(agent) and live:
            _set_or_pop(data, agent, live)
            return data, False
        live.append({"started_at": now, "dispatcher": dispatcher, "cwd": cwd})
        data[agent] = live
        return data, True

    return _update_registry(root, mutator)


def release(root, agent):
    """Removes the OLDEST live claim for agent if present. Returns whether it removed one. Never
    creates the registry file when there is nothing to release."""
    path = _registry_path(root)
    if not os.path.exists(path):
        return False

    def mutator(data):
        claims_list = data.get(agent, [])
        if not claims_list:
            return data, False
        oldest_idx = min(range(len(claims_list)), key=lambda i: claims_list[i]["started_at"])
        claims_list = list(claims_list)
        claims_list.pop(oldest_idx)
        _set_or_pop(data, agent, claims_list)
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


def refusal_lines(agent, existing, release_cmd):
    """The exact stderr block a single-flight caller prints (issue #551)."""
    started_iso = _iso(existing.get("started_at"))
    dispatcher = existing.get("dispatcher")
    return [
        f"dispatch-guard: BLOCKED - single-flight ({agent})",
        f"  existing claim started {started_iso}, dispatched by {dispatcher}",
        "  this is issue #551: the second writer would otherwise overwrite the first's plan.yaml.",
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
        "  this refusal fires ONCE; a second identical return will ship, so the correction has "
        "to be made now."
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
    root = os.environ.get("CLAUDE_PROJECT_DIR")
    if "--root" in rest:
        i = rest.index("--root")
        root = rest[i + 1]
        rest = rest[:i] + rest[i + 2 :]
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
        print("inflight_registry: no root - set CLAUDE_PROJECT_DIR or pass --root", file=sys.stderr)
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
