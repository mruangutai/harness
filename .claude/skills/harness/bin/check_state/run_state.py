"""A run's checkpoint and digest agree with the record: INV-15/16/36/46. (FEAT-69)"""
import os, re, sys
import artifact_accessors
import harness_boundary
import run_identity
LEADS = {"harness-product-lead", "harness-eng-lead", "harness-validator-lead"}
CHECKPOINT_KEYS = {
    # seed (harness-team §2)
    "schema_version", "run_id", "run_uid", "feature", "squad", "host", "status", "steps",
    # loop bookkeeping
    "cycles_used",
    # The money key below is HISTORICAL-ONLY (DEC-178): nothing produces it any more,
    # but all 67 pre-FEAT-08 run state.yaml files carry it and :401 flags any key not
    # in this set — drop it and every historical run becomes a violation. Named
    # without its quoted spelling because this task's verify: counts that spelling.
    "cost",
    # pins and context markers
    "flow", "task", "team", "branch", "worktree",
    "review_sha", "pinned_sha", "base_sha", "head_sha", "tip_sha", "commits",
    # roll-up enums and the report pointer — matchable values, so checkpoint-legal
    "verdict", "severity_max", "digest",
}

# --- INV-15 (DEC-156): a complete lead-hosted run's digest.md is the durable copy a
# successor reads — it must exist and satisfy the lead digest contract. The SubagentStop
# hook checks it at source but fails open when it cannot resolve the path (worktrees,
# cwd drift); this sweep runs from repo root and cannot be fooled.
# --- INV-16 (DEC-154, mechanized): state.yaml is a checkpoint — identifiers, enums,
# counters, paths, sequence markers. Top-level keys come from this whitelist, and no key
# repeats (the FEAT-02 audit found `cost:` written twice in 12 of 15 files — the second
# key silently shadows the first in any YAML parser).
def _inv16_unknown_keys(rel, sdoc):
    bad = []
    # INV-16: shape.
    #
    # Q3, found by the re-review: the duplicate-key TEXT SCAN that used to live here was
    # DEAD CODE, and its comment told future readers to preserve it for a property it no
    # longer had. `load_file` above uses the strict loader, which RAISES DuplicateKeyError
    # before control ever reaches this point — and that path `continue`s, so INV-16's own
    # DEC-156 message never fired. Keeping a scan that cannot run, guarded by a comment
    # forbidding its removal, is worse than either fixing or deleting it: the next reader
    # trusts the comment.
    #
    # Removed, because the loader's raise is strictly better — it catches a duplicate at
    # ANY nesting depth, where the column-0 scan saw only top-level ones.
    #
    # CORRECTED (review finding 5): this comment used to claim the DEC-156 wording was
    # "preserved at the raise site", and it was NOT — DuplicateKeyError's message was
    # a bare `duplicate key 'x'`, so the guidance an author actually needs ("replace the
    # placeholder; never append a second copy") vanished from this file entirely. A
    # comment asserting a preserved message that was in fact dropped is worse than no
    # comment, in a repo whose convention is that comments are load-bearing.
    #
    # It is true NOW because the guidance was moved INTO the exception's message
    # (harness_yaml.py's DuplicateKeyError.__init__), so every caller renders it whether
    # or not it has a dedicated handler.
    # The UNKNOWN half reads the PARSED keys (F-02): a quoted key is a real key the
    # text scan misses, a `#`-commented line is not a key at all, and YAML 1.1 resolves
    # `on:`/`no:` to booleans — so str() both sides, as T-17 does in check-domain.py.
    unknown = sorted({str(k) for k in sdoc if str(k) not in CHECKPOINT_KEYS})
    if unknown:
        bad.append(f"{rel}: non-checkpoint top-level key(s) {unknown} — state.yaml carries "
                   f"only identifiers, enums, counters, paths and sequence markers "
                   f"(DEC-154). Findings and assessment prose belong in that run's "
                   f"digest.md; a one-line note: per step entry is the ceiling.")
    return bad

def _inv16_step_id(_step, _step_index):
    return (
        str(_step.get("id") or f"index-{_step_index}")
        if isinstance(_step, dict) else f"index-{_step_index}"
    )

def _inv16_evidence_key_offends(_key, _value, _evidence_name):
    return (not isinstance(_key, str)
            or not _evidence_name.fullmatch(_key)
            or isinstance(_value, dict))

def _inv16_evidence_offenders(_step, _evidence_name):
    _offending = set()
    _evidence = _step.get("evidence")
    if isinstance(_evidence, dict):
        for _key, _value in _evidence.items():
            if _inv16_evidence_key_offends(_key, _value, _evidence_name):
                _offending.add(str(_key))
    return _offending

def _inv16_step_offenders(_step, _errors, _declared_step_keys, _evidence_name):
    """Sorted offending key names for one step, or the `<step>` placeholder."""
    _offending_step_keys = set()
    if isinstance(_step, dict):
        _offending_step_keys.update(
            set(_step) - _declared_step_keys)
        _offending_step_keys.update(_inv16_evidence_offenders(_step, _evidence_name))
    for _error in _errors:
        _path = list(_error.path)
        if _path:
            _offending_step_keys.add(str(_path[0]))
    return sorted(_offending_step_keys) or ["<step>"]

def _inv16_step_sweep(rel, sdoc, bad):
    """Appends straight to `bad` so a step judged before a later raise keeps its finding,
    exactly as it did when this loop sat inline in the caller's try."""
    import jsonschema
    # The step contract is read once per run through the shared strict reader
    # (FEAT-61 T-03); the pattern arrives as a string and is compiled here.
    _step_schema, _declared_step_keys, _evidence_pattern = (
        artifact_accessors.load_run_step_contract(sys.argv[2]))
    jsonschema.Draft202012Validator.check_schema(_step_schema)
    _step_validator = jsonschema.Draft202012Validator(_step_schema)
    _evidence_name = re.compile(_evidence_pattern)
    for _step_index, _step in enumerate(sdoc.get("steps", [])):
        _errors = list(_step_validator.iter_errors(_step))
        if not _errors:
            continue
        _step_id = _inv16_step_id(_step, _step_index)
        _names = _inv16_step_offenders(_step, _errors, _declared_step_keys, _evidence_name)
        bad.append(
            f"INV-16: {rel}: run {sdoc.get('run_id', '<unknown>')} step "
            f"{_step_id}: undeclared step key or evidence shape {_names} — "
            "declare recovery fields in "
            ".claude/skills/harness/bin/run-state-schema.json; put "
            "per-dispatch facts under evidence."
        )

def _inv16_boundary_errors():
    """What the step sweep can raise at its boundaries: jsonschema absent (ImportError), the
    step contract unreadable (ArtifactAccessError) or without its declared members (KeyError
    -- cases 61.f/g keep it natural), a contract jsonschema itself rejects (named by
    feature_schema, the module that owns that dependency). Every one is CANNOT be checked,
    none is a pass."""
    return ((ImportError, KeyError, artifact_accessors.ArtifactAccessError)
            + harness_boundary.load_repo_module("feature_schema").SCHEMA_ERRORS)

def _inv16_run(rel, sdoc):
    bad = _inv16_unknown_keys(rel, sdoc)

    # FEAT-104 census, 2026-09-09: all 356 existing run state.yaml files were
    # schema_version 1. The closed step sweep begins at version 2, so that corpus
    # remains byte-for-byte untouched and receives exactly its prior verdict.
    _schema_version = sdoc.get("schema_version")
    if (isinstance(_schema_version, int)
            and not isinstance(_schema_version, bool)
            and _schema_version >= 2):
        try:
            _inv16_step_sweep(rel, sdoc, bad)
        except _inv16_boundary_errors() as _run_schema_error:
            bad.append(
                f"INV-16: {rel}: run-state schema CANNOT be checked: "
                f"{type(_run_schema_error).__name__}: {_run_schema_error}"
            )
    return bad

def inv_16(ctx, feat):
    bad, warn = [], []
    H, root, fpath = ctx.H, ctx.root, ctx.fpath

    for sy, rel, rundir, sdoc, _error in ctx.run_states(feat):
        if _error:
            bad.append(_error)
            continue
        bad.extend(_inv16_run(rel, sdoc))
    return bad, warn

def _inv36_uid_conflict(_run_rel, _marker, sdoc):
    """The finding for a witness uid that disagrees with the checkpoint uid, as a list."""
    bad = []
    _wuid = _marker.get("run_uid") if isinstance(_marker, dict) else None
    _suid = sdoc.get("run_uid")
    if (_wuid is not None and str(_wuid).strip()
            and _suid is not None and str(_suid).strip()
            and str(_wuid) != str(_suid)):
        _uid_reason = run_identity.uid_conflict(
            {"run_uid": _wuid}, {"run_uid": _suid})
        bad.append(
            f"INV-36: {_run_rel}: the checkpoint occupying this run directory "
            "records an identity that disagrees with the identity recorded when "
            f"the directory was first written: {_uid_reason}. The checkpoint "
            "the witness describes is the record that was lost; the occupying "
            "file belongs to a different run.")
    return bad

def _inv36_conflict(_run_rel, _marker, sdoc):
    """The finding for a readable witness whose identity disagrees with the checkpoint."""
    bad = []
    _reason = run_identity.conflict(_marker, sdoc)
    if _reason:
        bad.append(
            f"INV-36: {_run_rel}: the checkpoint occupying this run directory "
            "records an identity that disagrees with the identity recorded when "
            f"the directory was first written: {_reason}. The checkpoint the "
            "witness describes is the record that was lost; the occupying file "
            "belongs to a different run.")
    else:
        bad.extend(_inv36_uid_conflict(_run_rel, _marker, sdoc))
    return bad

def _inv36_run(H, rundir, sdoc):
    """INV-36 findings for one run directory."""
    bad = []
    # INV-36 (BUG-1305): D-13 makes this self-limiting. Only a run directory
    # carrying the write-once witness is judged; witness-absent directories are
    # permanently legacy and remain silent. A witness uid with no checkpoint uid
    # is also silent: that can be a legitimate landing where POST did not run, and
    # a hook-registration defect must not be mislabeled as a clobber.
    _marker_path = run_identity.marker_path(rundir)
    if os.path.lexists(_marker_path):
        _run_rel = os.path.relpath(rundir, H)
        try:
            _marker = run_identity.read_marker(rundir)
        except run_identity.MarkerUnreadable:
            bad.append(
                f"INV-36: {_run_rel}: its recorded run identity cannot be read, so "
                "whether the checkpoint occupying this directory belongs to it cannot "
                "be determined.")
        else:
            bad.extend(_inv36_conflict(_run_rel, _marker, sdoc))
    return bad

def inv_36(ctx, feat):
    bad, warn = [], []
    H, root, fpath = ctx.H, ctx.root, ctx.fpath

    for sy, rel, rundir, sdoc, _error in ctx.run_states(feat):
        if sdoc is None:
            continue
        bad.extend(_inv36_run(H, rundir, sdoc))
    return bad, warn

def _inv15_digest_verdict(_dtext):
    """The digest's VERDICT match, tail-anchored, or None."""
    # Keep validate-digest.py:1155-1160's tail-anchor semantics byte-for-byte.
    _anchors = list(re.finditer(r"^\s*VERDICT:", _dtext, re.M))
    _tail = _dtext[_anchors[-1].start():] if _anchors else _dtext
    return re.search(r"^\s*VERDICT:\s*(\S+)", _tail, re.M)

def _inv46_verdict_cross_check(ctx, feat, rundir, dg, _dtext):
    """INV-46: the digest verdict against every verdict feature.json records for the run
    (BUG-440; printed under INV-37's number until the 2026-09-21 ruling gave it a row)."""
    bad = []
    H = ctx.H
    _feat_dir = os.path.dirname(os.path.dirname(rundir))
    _rid = os.path.basename(rundir)
    _recorded = ctx.run_verdicts(feat)
    if _rid not in _recorded:
        return bad
    _dm = _inv15_digest_verdict(_dtext)
    if not _dm:
        return bad
    for _rv in dict.fromkeys(_recorded[_rid]):
        if _dm.group(1) != _rv:
            bad.append(
                f"INV-46: {os.path.basename(_feat_dir)} run {_rid}: "
                f"digest verdict {_dm.group(1)!r} in "
                f"{os.path.relpath(dg, H)} differs from feature.json verdict "
                f"{_rv!r} in {os.path.relpath(os.path.join(_feat_dir, 'feature.json'), H)}; "
                "the gate does not decide which record is wrong.")
    return bad

def _inv15_validate(ctx, feat, rundir, dg, _vd_mod):
    bad = []
    H = ctx.H
    _dtext, _errs = ctx.lead_digest(dg)
    if _errs:
        bad.append(f"{os.path.relpath(dg, H)}: does not satisfy the lead digest "
                   f"contract — a successor reads this file, not the transcript "
                   f"(DEC-156). Run bin/validate-digest.py lead on it for reasons.")
    return bad

def _inv15_validator_unavailable(ctx, vd, _vd_import_err):
    root = ctx.root
    return (f"INV-15 could not run: {os.path.relpath(vd, root)} "
            f"{'is missing' if not os.path.isfile(vd) else 'will not import (' + str(_vd_import_err) + ')'}. "
            f"Digest files are UNCHECKED — likely a partial deploy.")

def _inv15_run(ctx, feat, rundir, sdoc, _vd):
    bad = []
    H = ctx.H
    vd, _vd_mod, _vd_import_err = _vd
    complete = str(sdoc.get("status", "")).strip() == "complete"
    # INV-15: the durable digest.
    _host = str(sdoc.get("host", "")).strip()
    if not (complete and _host in LEADS):
        return bad
    dg = os.path.join(rundir, "digest.md")
    if not os.path.isfile(dg):
        bad.append(f"{os.path.relpath(rundir, H)}: run is complete but digest.md is "
                   f"missing — the lead's report artifact never landed (DEC-156).")
    elif _vd_mod is None:
        bad.append(_inv15_validator_unavailable(ctx, vd, _vd_import_err))
    else:
        bad.extend(_inv15_validate(ctx, feat, rundir, dg, _vd_mod))
    return bad

def inv_15(ctx, feat):
    bad, warn = [], []
    H, root, fpath = ctx.H, ctx.root, ctx.fpath
    _vd = ctx.validate_digest()
    for sy, rel, rundir, sdoc, _error in ctx.run_states(feat):
        if sdoc is None:
            continue
        bad.extend(_inv15_run(ctx, feat, rundir, sdoc, _vd))
    return bad, warn

def _inv46_digest(ctx, sdoc, rundir):
    """The contract-clean digest of a complete lead-hosted run, or None: INV-15 owns every
    other outcome (missing digest, unavailable validator, contract failure)."""
    complete = str(sdoc.get("status", "")).strip() == "complete"
    _host = str(sdoc.get("host", "")).strip()
    if not (complete and _host in LEADS):
        return None
    dg = os.path.join(rundir, "digest.md")
    if not os.path.isfile(dg):
        return None
    _dtext, _errs = ctx.lead_digest(dg)
    return (dg, _dtext) if _dtext is not None and not _errs else None

def inv_46(ctx, feat):
    bad, warn = [], []
    for sy, rel, rundir, sdoc, _error in ctx.run_states(feat):
        if sdoc is None:
            continue
        found = _inv46_digest(ctx, sdoc, rundir)
        if found is not None:
            bad.extend(_inv46_verdict_cross_check(ctx, feat, rundir, found[0], found[1]))
    return bad, warn
