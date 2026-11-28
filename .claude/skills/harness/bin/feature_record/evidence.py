"""feature_record/evidence.py — the cycle and refusal evidence a feature.json run cites:
evidence_ref resolution and verification, historical cycle counts, and run-digest ownership.
"""
import hashlib
import os
import stat


def resolve_evidence_ref(feature_dir, operand):
    """Normalize a regular, feature-local immutable artifact to its hash-bound reference."""
    root = os.path.realpath(feature_dir)
    raw = os.fspath(operand)
    if ".." in raw.replace("\\", "/").split("/"):
        raise ValueError("evidence must not contain parent traversal")
    path = os.path.abspath(os.path.join(root, raw))
    resolved = os.path.realpath(path)
    if os.path.commonpath((root, resolved)) != root or resolved == root:
        raise ValueError("evidence must stay inside the target feature")
    if not stat.S_ISREG(os.stat(resolved).st_mode):
        raise ValueError("evidence must be a regular file")
    with open(resolved, "rb") as source:
        digest = hashlib.file_digest(source, "sha256").hexdigest()
    return {"path": os.path.relpath(resolved, root), "sha256": digest}


def verify_evidence_ref(feature_dir, ref, subject=None):
    """Verify bytes and, for operator notes, the explicitly authorized subject/effect."""
    path = _verified_artifact(feature_dir, ref)
    if subject is None:
        return path
    return _authorized_effect(path, subject)


def _verified_artifact(feature_dir, ref):
    """The on-disk path of `ref`, once its bytes still hash to the recorded reference."""
    if not isinstance(ref, dict) or set(ref) != {"path", "sha256"}:
        raise ValueError("evidence reference requires only path and sha256")
    actual = resolve_evidence_ref(feature_dir, ref["path"])
    if actual != ref:
        raise ValueError("evidence hash does not match the recorded artifact")
    return os.path.join(feature_dir, actual["path"])


def _authorized_effect(path, subject):
    """The one effect in the operator note at `path` that matches `subject` exactly."""
    from artifact_accessors import strict_json_loads
    with open(path, encoding="utf-8") as source:
        note = strict_json_loads(source.read())
    if not isinstance(note, dict) or note.get("feature_id") != subject.get("feature_id"):
        raise ValueError("authorization evidence has a different feature identity")
    effects = note.get("effects")
    matches = [effect for effect in effects if _effect_matches(effect, subject)
               ] if isinstance(effects, list) else []
    if len(matches) != 1:
        raise ValueError("authorization evidence requires one exact subject/effect")
    return matches[0]


def _effect_matches(effect, subject):
    return isinstance(effect, dict) and all(
        type(effect.get(key)) is type(value) and effect.get(key) == value
        for key, value in subject.items() if key != "feature_id")


def verify_historical_cycle_count(path, count):
    """An operator note may support missing history, but cannot contradict an explicit count."""
    import digest_record
    try:
        record = digest_record.load_record(path)
    except digest_record.DigestRecordError:
        return
    digest = record.get("DIGEST")
    reported = digest.get("cycles_used") if isinstance(digest, dict) else None
    if type(reported) is int and reported >= 0 and reported != count:
        raise ValueError("historical cycle attribution contradicts the authentic digest count")


def _run_digest_paths(run):
    evidence = run.get("cycle_evidence")
    if evidence:
        yield evidence["path"]
        for previous in evidence.get("previous", []):
            yield previous["path"]
    if run.get("refusal"):
        yield run["refusal"]["digest"]["path"]


def verify_run_digest_owner(run_id, path, runs):
    """A normalized artifact retains its run owner even after attribution correction."""
    parts = path.split(os.sep)
    owner = next((other for other in runs if other["id"] != run_id and
                  (len(parts) > 2 and parts[:2] == ["runs", other["id"]]
                   or path in _run_digest_paths(other))), None)
    if owner:
        raise ValueError(f"digest evidence belongs to run {owner['id']!r}, not {run_id!r}")
