#!/usr/bin/env python3
"""check_state.board.inv_37 grades a bound feature locally when gh is offline (#2190).

These tests run in-process against the public `inv_37(ctx)`. They use the real feature_record.binding receipt and provenance predicates and the real local fleet loader and `repo_entry`. The two remote boundaries are recorded: `feature_record.binding.resolve_binding` and `factory_config.product_config`. Each case asserts what INV-37 reported and which remote boundary it reached, so neither the local validation nor the receipt checks can be skipped unnoticed.

    ./test-check-state-inv37-local-binding.py    -> exit 0 all pass, 1 otherwise
"""
import os
import sys
import tempfile
from unittest import mock

from unit_support import ROOT, BIN, TESTS  # noqa: F401  (puts bin/ and tests/ on sys.path)
from check_support import Checks
from harness_config_support import build_config, write_config

import artifact_accessors
import factory_config
from feature_record import binding as record_binding
from check_state import board

C = Checks()
check = C.check
BOUND = "FEAT-9002-bound-fixture"
OWNER = "FEAT-9003-owner-fixture"
_STATIONS = ["backlog", "plan", "ready", "building", "review", "done"]


class _Ctx:
    """The slice of check_state's Ctx that INV-37 reads."""

    def __init__(self, root, docs, online, owner_sync=True):
        self.root, self.H = root, os.path.join(root, ".harness")
        self.cj = write_config(os.path.join(self.H, "harness.json"),
                               {"github": {"sync": owner_sync, "repo": "org/repo"}})
        self._docs, self._online = docs, online
        self.features = sorted(docs)
        self.plan_docs = dict.fromkeys(docs)  # INV-37 reads membership only
        self.fpath = lambda feat, name: os.path.join(".harness", "x", "features", feat, name)

    def gh_ok(self, _gh_bin):
        return self._online

    def record(self, feat):
        return self._docs[feat], None

    def feature_dir(self, feat):
        return os.path.join(self.H, "x", "features", feat)


def _bound(github, factory=None):
    return {"feature_id": BOUND, "factory": {"repo": "org/prod"} if factory is None else factory,
            "github": github}


def _run(docs, online, remote_ok=True, owner_sync=True):
    """(findings, remote log) with the remote boundaries recorded and restored."""
    def product_config(fleet, repo):
        if not remote_ok:
            raise artifact_accessors.FleetError("product config unreadable", repo, "offline")
        return build_config({"github": {"sync": True, "repo": repo, "board": {
            "owner": "org", "number": 9, "station_field": "Status", "stations": _STATIONS}}})

    with tempfile.TemporaryDirectory() as root:
        os.makedirs(os.path.join(root, ".harness", "factory"))
        with open(os.path.join(root, ".harness", "factory", "fleet.yaml"), "w") as f:
            f.write(f"schema: factory-fleet/1\nrepos:\n  - name: org/prod\n"
                    f"    default_branch: main\nworkspace_root: {root}\n")
        ctx = _Ctx(root, docs, online, owner_sync)
        factory_config.clear_product_config_memo()
        try:
            with mock.patch.object(record_binding, "resolve_binding",
                                   wraps=record_binding.resolve_binding) as resolve, \
                    mock.patch.object(factory_config, "product_config",
                                      side_effect=product_config) as product:
                bad, _warn = board.inv_37(ctx)
        finally:
            factory_config.clear_product_config_memo()
    return bad, {"resolve": resolve.call_count, "product_config": product.call_count}


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
    for label, github, detail, guidance in (
            ("missing receipt", {}, "receipt absent or incomplete", "gh-sync.py recover-terminal "),
            ("owner repo recorded", {"build_entry": "opened", "repo": "org/repo"},
             "conflicts with bound repository 'org/prod'",
             "edit the github block of"),
            ("unproven active mirror", {"build_entry": "opened", "parent": 16},
             "nonempty mirror has no matching github.repo provenance",
             "edit the github block of")):
        bad, log = _run({BOUND: _bound(github)}, online=False)
        check(f"u.2 offline {label}: the receipt finding, never a binding finding",
              _has(bad, BOUND, detail) and not _has(bad, "invalid authoritative")
              and log["product_config"] == 0, f"bad={bad} log={log}")
        check(f"u.2 offline {label}: recovery guidance is selected against factory.repo",
              _has(bad, BOUND, guidance), f"bad={bad}")


def case_offline_invalid_bindings_still_fail():
    for repo in ("not a repository", 5, "", "org/gone"):
        bad, log = _run({BOUND: _bound(OPENED, factory={"repo": repo})}, online=False)
        check(f"u.3 offline factory.repo={repo!r}: still an invalid authoritative binding",
              _has(bad, BOUND, "invalid authoritative repository binding")
              and log["product_config"] == 0, f"bad={bad} log={log}")
    for factory in ("org/prod", ["org/prod"]):
        bad, log = _run({BOUND: _bound(OPENED, factory=factory)}, online=False)
        check(f"u.3 offline factory={factory!r}: a non-mapping factory is an invalid binding "
              "with no owner fallback and no remote read",
              _has(bad, BOUND, "invalid authoritative repository binding", "expected a mapping")
              and log == {"resolve": 0, "product_config": 0}, f"bad={bad} log={log}")


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


if __name__ == "__main__":
    main()
    sys.exit(C.report())
