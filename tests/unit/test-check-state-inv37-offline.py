#!/usr/bin/env python3
"""check_state.board.inv_37 grades a bound feature locally when gh is offline (#2190).

These tests run in-process against the public `inv_37(ctx)`. They use the real feature_schema receipt and provenance predicates and the real local fleet loader and `repo_entry`. The two remote boundaries are recorded: `feature_schema.resolve_binding` and `factory_config.product_config`. Each case asserts what INV-37 reported and which remote boundary it reached, so neither the local validation nor the receipt checks can be skipped unnoticed.

    ./test-check-state-inv37-offline.py    -> exit 0 all pass, 1 otherwise
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
import json
import os
import tempfile

import artifact_accessors  # noqa: E402
import factory_config  # noqa: E402
import feature_schema  # noqa: E402
from check_state import board  # noqa: E402

FAILURES = []
BOUND = "FEAT-9002-bound-fixture"
OWNER = "FEAT-9003-owner-fixture"
_STATIONS = ["backlog", "plan", "ready", "building", "review", "done"]


def check(name, cond, detail=""):
    if cond:
        print(f"PASS  {name}")
    else:
        print(f"FAIL  {name}{(' — ' + detail) if detail else ''}")
        FAILURES.append(name)


class _Ctx:
    """The slice of check_state's Ctx that INV-37 reads."""

    def __init__(self, root, docs, online, owner_sync=True):
        self.root, self.H = root, os.path.join(root, ".harness")
        self.cj = {"github": {"sync": owner_sync, "repo": "org/repo", "board": None}}
        self._docs, self._online = docs, online
        self.features = sorted(docs)
        self.plan_docs = {f: {"status": "ready", "tasks": []} for f in docs}
        self.fpath = lambda feat, name: os.path.join(".harness", "x", "features", feat, name)

    def gh_ok(self, _gh_bin):
        return self._online

    def record(self, feat):
        return self._docs[feat], None

    def feature_dir(self, feat):
        return os.path.join(self.H, "x", "features", feat)


def _bound(github, repo="org/prod"):
    return {"feature_id": BOUND, "factory": {"repo": repo}, "github": github}


def _run(docs, online, remote_ok=True, owner_sync=True):
    """(findings, remote log) with the remote boundaries recorded and restored."""
    log = {"resolve": 0, "product_config": 0}
    real_resolve, real_product = feature_schema.resolve_binding, factory_config.product_config

    def resolve(doc, root):
        log["resolve"] += 1
        return real_resolve(doc, root)

    def product_config(fleet, repo):
        log["product_config"] += 1
        if not remote_ok:
            raise artifact_accessors.FleetError("product config unreadable", repo, "offline")
        return {"github": {"sync": True, "repo": repo, "board": {
            "owner": "org", "number": 9, "station_field": "Status", "stations": _STATIONS}}}

    with tempfile.TemporaryDirectory() as root:
        os.makedirs(os.path.join(root, ".harness", "factory"))
        with open(os.path.join(root, ".harness", "factory", "fleet.yaml"), "w") as f:
            f.write(f"schema: factory-fleet/1\nrepos:\n  - name: org/prod\n"
                    f"    default_branch: main\nworkspace_root: {root}\n")
        ctx = _Ctx(root, docs, online, owner_sync)
        with open(os.path.join(ctx.H, "harness.json"), "w") as f:
            json.dump(ctx.cj, f)
        feature_schema.resolve_binding, factory_config.product_config = resolve, product_config
        factory_config.clear_product_config_memo()
        try:
            bad, _warn = board.inv_37(ctx)
        finally:
            feature_schema.resolve_binding, factory_config.product_config = real_resolve, real_product
            factory_config.clear_product_config_memo()
    return bad, log


def _has(bad, *needles):
    return any(all(n in line for n in needles) for line in bad)


OPENED = {"build_entry": "opened", "repo": "org/prod"}


def case_offline_valid_bound_is_clean():
    bad, log = _run({BOUND: _bound(OPENED)}, online=False, owner_sync=False)
    check("u.1 offline: a fleet-listed bound receipt for factory.repo is clean",
          bad == [], f"bad={bad}")
    check("u.1 offline: neither remote boundary is reached",
          log == {"resolve": 0, "product_config": 0}, f"log={log}")


def case_offline_receipts_are_graded_against_factory_repo():
    for label, github, detail in (
            ("missing receipt", {}, "receipt absent or incomplete"),
            ("owner repo recorded", {"build_entry": "opened", "repo": "org/repo"},
             "conflicts with bound repository 'org/prod'"),
            ("unproven active mirror", {"build_entry": "opened", "parent": 16},
             "nonempty mirror has no matching github.repo provenance")):
        bad, log = _run({BOUND: _bound(github)}, online=False)
        check(f"u.2 offline {label}: the receipt finding, never a binding finding",
              _has(bad, BOUND, detail) and not _has(bad, "invalid authoritative")
              and log["product_config"] == 0, f"bad={bad} log={log}")


def case_offline_invalid_bindings_still_fail():
    for repo in ("not a repository", 5, "", "org/gone"):
        bad, log = _run({BOUND: _bound(OPENED, repo=repo)}, online=False)
        check(f"u.3 offline factory.repo={repo!r}: still an invalid authoritative binding",
              _has(bad, BOUND, "invalid authoritative repository binding")
              and log["product_config"] == 0, f"bad={bad} log={log}")


def case_online_keeps_full_remote_verification():
    bad, log = _run({BOUND: _bound(OPENED)}, online=True)
    check("u.4 online: the shared resolver and the remote config read both run",
          bad == [] and log["resolve"] == 1 and log["product_config"] >= 1, f"bad={bad} log={log}")
    bad, log = _run({BOUND: _bound(OPENED)}, online=True, remote_ok=False)
    check("u.4 online: an unreadable remote config is still an invalid binding",
          _has(bad, BOUND, "invalid authoritative repository binding"), f"bad={bad}")


def case_owner_path_is_unchanged():
    owner_ok = {"feature_id": OWNER, "github": {"build_entry": "opened", "repo": "org/repo"}}
    owner_bad = {"feature_id": OWNER, "github": {}}
    bad, log = _run({BOUND: _bound(OPENED), OWNER: owner_ok}, online=False)
    check("u.5 offline: an owner receipt beside a bound one is clean, via the resolver",
          bad == [] and log["resolve"] == 1, f"bad={bad} log={log}")
    bad, _log = _run({OWNER: owner_bad}, online=False)
    check("u.5 offline: a missing owner receipt is still reported",
          _has(bad, OWNER, "receipt absent or incomplete"), f"bad={bad}")


def main():
    case_offline_valid_bound_is_clean()
    case_offline_receipts_are_graded_against_factory_repo()
    case_offline_invalid_bindings_still_fail()
    case_online_keeps_full_remote_verification()
    case_owner_path_is_unchanged()
    if FAILURES:
        print(f"\n{len(FAILURES)} FAILURE(S): {FAILURES}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
