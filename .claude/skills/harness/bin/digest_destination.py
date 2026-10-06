#!/usr/bin/env python3
"""Bind lead digest appends to trusted runtime identity and a registered open run."""
import glob
import json
import os
import re
import stat
import sys
from contextlib import contextmanager

import artifact_accessors
import harness_boundary
import harness_yaml

LEAD_SQUADS = {"harness-eng-lead": "engineering", "harness-product-lead": "product",
               "harness-validator-lead": "validator"}


class AuthorizationError(ValueError):
    pass


def authorization_descriptor(path, flags):
    """Open a regular authorization source without following its final symlink or blocking."""
    descriptor = os.open(path, flags | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise OSError("authorization source is not a regular file")
    except OSError:
        os.close(descriptor)
        raise
    return descriptor



def authorization_root(root, feature):
    """Resolve an authorization checkout without report-mode topology fallbacks."""
    if not isinstance(feature, str):
        raise AuthorizationError("authorization requires an exact feature identity")
    try:
        checkout = harness_boundary.worktree_for_feature(root, feature, strict=True)
    except (harness_boundary.AmbiguousWorktree, OSError, UnicodeError) as error:
        raise AuthorizationError(f"authorization cannot resolve the feature checkout: {error}") from error
    return os.path.realpath(checkout or root)


def _registered_record_location(root, feature):
    root = os.path.realpath(root)
    # The selected feature's own record, bound to this checkout: authorization never reads
    # another checkout's copy (FEAT-1559).
    # corpus-scope: checkout-local
    records = glob.glob(os.path.join(root, ".harness", "*", "features", feature, "feature.json"))
    if len(records) != 1:
        raise AuthorizationError("authorization requires exactly one registered feature record")
    record_path = records[0]
    resolved_path = os.path.realpath(record_path)
    feature_dir = os.path.dirname(records[0])
    if os.path.dirname(resolved_path) != os.path.realpath(feature_dir):
        raise AuthorizationError("authorization feature record is not local to its feature directory")
    if os.path.commonpath((root, resolved_path)) != root:
        raise AuthorizationError("authorization feature record belongs to another checkout")
    checkout = harness_boundary.worktree_owner(resolved_path)
    if checkout is not None and (checkout[0] != root or checkout[1] is None):
        raise AuthorizationError("authorization feature record has foreign or unknown checkout ownership")
    return record_path, feature_dir


def registered_feature(root, feature):
    """Resolve the unique registered feature named by trusted runtime identity."""
    if not isinstance(feature, str) or not re.fullmatch(
            r"(?:FEAT|BUG)-[0-9]+(?:-[a-z0-9]+)+", feature):
        raise AuthorizationError("authorization requires an exact feature identity")
    record_path, feature_dir = _registered_record_location(root, feature)
    try:
        with open(record_path, "rb", opener=authorization_descriptor) as source:
            record = artifact_accessors.load_feature_json(
                text=source.read().decode("utf-8"), context=record_path)
    except (artifact_accessors.FeatureJsonError, OSError, UnicodeError) as error:
        raise AuthorizationError(str(error)) from error
    if not isinstance(record, dict) or record.get("feature_id") != feature:
        raise AuthorizationError("authorization feature record identity does not match")
    return record, feature_dir


def _registered_run(record, agent, run_id):
    identity = (agent, LEAD_SQUADS[agent], "PENDING")
    runs = [run for run in record.get("runs", []) if isinstance(run, dict)
            and (run.get("agent"), run.get("squad"), run.get("verdict")) == identity
            and not run.get("ended_at")]
    if len(runs) != 1:
        raise AuthorizationError("authorization requires exactly one matching open registered lead run")
    selected = runs[0].get("id")
    if run_id is not None and selected != run_id:
        raise AuthorizationError("authorization binding does not match the open registered lead run")
    return selected


def _registered_digest(root, feature_dir, selected, agent):
    if not isinstance(selected, str) or selected in ("", ".", "..") or "/" in selected or "\\" in selected:
        raise AuthorizationError("authorization run identity is not a single directory name")
    path = os.path.join(feature_dir, "runs", selected, "digest.md")
    try:
        grants, _shared = artifact_accessors.manifest_domains(
            os.path.join(root, ".harness", "team-config.yaml"), agent)
    except harness_yaml.YamlParseError as error:
        raise AuthorizationError(f"authorization cannot read writable grants: {error}") from error
    if not any(harness_boundary.matches(os.path.relpath(path, root), grant) for grant in grants):
        raise AuthorizationError("authorization registered run is outside this lead's writable grants")
    return path


def registered_destination(root, feature, agent, run_id=None):
    if agent not in LEAD_SQUADS:
        raise AuthorizationError("authorization requires an exact lead and feature identity")
    record, feature_dir = registered_feature(root, feature)
    selected = _registered_run(record, agent, run_id)
    return selected, _registered_digest(root, feature_dir, selected, agent)


def _runtime_identity(agent, payload):
    return {"agent": agent, "feature": payload.get("harness_feature"),
            "agent_id": payload.get("harness_agent_id"),
            "parent_agent_id": payload.get("harness_parent_agent_id")}


def _check_runtime_claim(root, expected):
    import inflight_registry

    result = inflight_registry.find_run_claim(root, expected["agent_id"])
    claim = result.get("claim", {})
    if not all(expected.values()) or not result.get("ok") or any(
            claim.get(key) != value for key, value in expected.items()):
        raise AuthorizationError("authorization requires this exact live runtime claim and parent")
    # The claim must live in this feature checkout's own registry. Its recorded `cwd` is
    # the dispatching session's directory, which is the owner checkout when the feature
    # sits on a linked worktree (#2063), so it cannot name the checkout.
    if os.path.realpath(result.get("root") or "") != root:
        raise AuthorizationError("authorization runtime claim belongs to another checkout")


def bind(root, payload):
    expected = _runtime_identity(payload.get("agent_type"), payload)
    root = authorization_root(root, expected["feature"])
    _check_runtime_claim(root, expected)
    run_id, path = registered_destination(root, expected["feature"], expected["agent"])
    return {"root": root, **expected, "run_id": run_id, "artifact": path}


def authorized_destination(root, agent, payload, artifact):
    binding = payload.get("harness_digest_binding")
    if not isinstance(binding, dict):
        raise AuthorizationError("authorization has no trusted hook-owned digest binding")
    expected = _runtime_identity(agent, payload)
    if not all(expected.values()) or any(binding.get(key) != value for key, value in expected.items()):
        raise AuthorizationError("authorization digest binding does not match the runtime identity")
    root = authorization_root(root, expected["feature"])
    if binding.get("root") != root or not binding.get("run_id"):
        raise AuthorizationError("authorization digest binding belongs to another checkout or run")
    _run_id, path = registered_destination(root, expected["feature"], agent, binding["run_id"])
    candidate = artifact if os.path.isabs(artifact) else os.path.join(root, artifact)
    if ".." in artifact.replace("\\", "/").split("/") or os.path.abspath(candidate) != path or binding.get("artifact") != path:
        raise AuthorizationError("authorization permits only this runtime's registered run digest.md")
    return root, path


@contextmanager
def _digest_directory(root, components):
    directory = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for component in components:
            next_directory = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                     dir_fd=directory)
            os.close(directory)
            directory = next_directory
        yield directory
    finally:
        os.close(directory)


@contextmanager
def _digest_handle(directory, name):
    descriptor = os.open(name, os.O_RDWR | os.O_APPEND | os.O_NOFOLLOW, dir_fd=directory)
    try:
        mode = os.fstat(descriptor).st_mode
        if not stat.S_ISREG(mode):
            raise AuthorizationError("authorization durable digest is not a regular file")
        if not mode & 0o222:
            raise AuthorizationError("authorization durable digest cannot be written")
        with os.fdopen(descriptor, "a+", encoding="utf-8") as handle:
            descriptor = None
            handle.seek(0)
            yield handle
    finally:
        if descriptor is not None:
            os.close(descriptor)


@contextmanager
def authorized_digest(root, agent, payload, artifact):
    root, path = authorized_destination(root, agent, payload, artifact)
    components = os.path.relpath(path, root).split(os.sep)
    try:
        with _digest_directory(root, components[:-1]) as directory:
            with _digest_handle(directory, components[-1]) as handle:
                yield path, handle
    except OSError as error:
        raise AuthorizationError(f"authorization refused missing, unsafe or unwritable durable digest ({error})") from error


def main():
    try:
        payload = artifact_accessors.read_hook_payload(sys.stdin.read(), "digest authorization payload")
        root = harness_boundary.resolve_root(os.path.dirname(os.path.realpath(__file__)))
        binding = bind(root, payload)
        print(json.dumps({"ok": True, "binding": binding}))
        return 0
    except (AuthorizationError, OSError, ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "message": str(error)}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
