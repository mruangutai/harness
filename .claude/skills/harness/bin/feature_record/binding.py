"""feature_record/binding.py — a feature's repository binding and mirror provenance: which
repository a feature is bound to, which GitHub mirror its records belong to, and whether a
recorded receipt allows a merge (DEC-220).
"""
import os
import re


_REPOSITORY = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]*/(?!\.{1,2}$)[A-Za-z0-9_.-]+")


def has_repository_binding(feature_doc):
    """Invalid factory shapes are bound too: no consumer may fall back to the owner."""
    factory = feature_doc.get("factory")
    return factory is not None and (not isinstance(factory, dict) or factory.get("repo") is not None)


def resolve_binding(feature_doc, root):
    """Resolve one feature's repository, board and issue types without owner fallback."""
    import artifact_accessors
    factory = feature_doc.get("factory")
    if factory is not None and not isinstance(factory, dict):
        raise artifact_accessors.FleetError("invalid feature binding", "factory", "expected a mapping")
    bound = factory.get("repo") if factory else None
    if bound is not None:
        return _bound_mirror_binding(bound, root)
    return _owner_mirror_binding(root)


def _bound_mirror_binding(bound, root):
    import artifact_accessors
    import factory_config
    from github import issue_types
    if not isinstance(bound, str) or not _REPOSITORY.fullmatch(bound):
        raise artifact_accessors.FleetError("invalid feature binding", "factory.repo",
                                          "expected a declared owner/name")
    fleet = artifact_accessors.load_fleet(os.path.join(root, ".harness", "factory", "fleet.yaml"))
    factory_config.repo_entry(fleet, bound)
    config = factory_config.product_config(fleet, bound)
    github = config["github"]
    if github["repo"] != bound or not github["sync"]:
        raise artifact_accessors.FleetError("invalid product mirror", bound,
                                          "github.sync must be enabled and github.repo must match factory.repo")
    return bound, factory_config.board_for(fleet, bound), issue_types.overrides_from_config(config)


def _owner_mirror_binding(root):
    import artifact_accessors
    import factory_config
    from github import issue_types
    path = os.path.join(root, ".harness", "harness.json")
    try:
        config = artifact_accessors.load_harness_json(path)
    except artifact_accessors.ArtifactAccessError as error:
        raise artifact_accessors.FleetError("owner config unreadable", path, str(error)) from error
    github = config["github"]
    board = github["board"] if github["sync"] else None
    return (github["repo"], None if board is None else factory_config.validate_board(board),
            issue_types.overrides_from_config(config))


def effective_recorded_repo(doc, bound_repo):
    """The repository a mapping is proven to live in. An UNBOUND feature's pre-provenance
    mapping was created by the owner binding that still resolves it — there was never a second
    destination — so its absent `github.repo` reads as that owner repository. A bound feature's
    absence stays unproven: its old numbers may have come from an ancestor default (DEC-221)."""
    recorded = (doc.get("github") or {}).get("repo")
    if recorded is None and bound_repo and not has_repository_binding(doc):
        return bound_repo
    return recorded


def mirror_provenance_problem(doc, bound_repo):
    """A readable legacy mapping is not permission to reuse its unproven numbers."""
    github = doc.get("github") or {}
    recorded_repo = github.get("repo")
    active = any(github.get(key) for key in ("milestone", "parent", "issues", "attached", "typed"))
    if _repo_conflicts(doc, github, bound_repo, active):
        return f"recorded github.repo {recorded_repo!r} conflicts with bound repository {bound_repo!r}"
    if active and (not bound_repo or effective_recorded_repo(doc, bound_repo) != bound_repo):
        return "nonempty mirror has no matching github.repo provenance"
    return None


def _repo_conflicts(doc, github, bound_repo, active):
    """A recorded repository other than the bound one, on a mapping that claims a binding."""
    recorded_repo = github.get("repo")
    if recorded_repo is None or recorded_repo == bound_repo:
        return False
    return (bound_repo is not None or active
            or github.get("build_entry") in {"opened", "recovered-terminal"}
            or (doc.get("factory") or {}).get("repo") is not None)


def receipt_allows_merge(doc, bound_repo):
    """Shared provenance gate: only a recorded, provenanced Build-entry receipt allows."""
    if mirror_provenance_problem(doc, bound_repo):
        return False
    github = doc.get("github") or {}
    entry = github.get("build_entry")
    if entry == "not-applicable":
        return not has_repository_binding(doc)
    if entry in {"opened", "recovered-terminal"}:
        return bool(bound_repo) and effective_recorded_repo(doc, bound_repo) == bound_repo
    return False
