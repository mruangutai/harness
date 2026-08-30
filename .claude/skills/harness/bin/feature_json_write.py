#!/usr/bin/env python3
"""feature_json_write.py — the one locked, schema-validated read-modify-write entry point for
feature.json (stale-anchor-write-hazard, 2026-08-30).

This is a LIBRARY, never a gate: it never calls sys.exit and it is never registered as a hook.
It raises harness_merge.MergeRefusal for every kind of refusal, exactly like harness_merge.py
itself, so a caller can inspect the refusal instead of losing it to a bare process exit.

WHAT THIS CLOSES, AND WHAT IT DOES NOT. The incident this exists for was a line-anchored
EDIT applied to feature.json after another tool had already rewritten it between the agent's
read and its write -- the stale anchors landed at the wrong offsets and produced invalid JSON,
and nothing refused it because a line-anchored patch is raw text splicing with no writer
entry point in between to intercept. THIS MODULE CANNOT PREVENT THAT SPECIFIC SHAPE OF
INCIDENT: an editor tool that patches file bytes directly by line offset never calls into
Python at all, so no library, however careful, sits in that path. What this module DOES close
is the adjacent hazard of every writer that DOES go through Python -- today, gh-sync.py's three
call sites -- racing each other or writing a document feature_schema.py would reject. See the
feature's receipt for the fuller argument.

This module builds no lock or rename primitive of its own (DEC-199): it is entirely a thin,
schema-checking wrapper over harness_merge.locked_update, which already gives it the fcntl
lock on the sibling `.lock` file, the same-directory tempfile, the fsync, and the os.replace.
python3 stdlib only, matching harness_merge.py's own constraint.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import feature_schema  # noqa: E402  (local import, after sys.path fix-up)
import harness_merge  # noqa: E402  (local import, after sys.path fix-up)

# A features directory either directly under a .harness segment or nested one segment deeper
# (repo-tier), a FEAT- or BUG- prefixed directory, and the literal filename feature.json.
# Matched on the RESOLVED path only (harness_merge.require_destination), never the literal
# argument -- same discipline as plan-merge.py's PLAN_TAIL and observations-merge.py's
# OBSERVATIONS_TAIL.
FEATURE_JSON_TAIL = re.compile(
    r"(?:^|/)\.harness/(?:[^/]+/)?features/(?:FEAT|BUG)-[^/]+/feature\.json$"
)

_WHAT = "a feature's feature.json under a features directory"
_HINT_LINES = [
    "  a legal path looks like .harness/features/FEAT-NN-slug/feature.json or",
    "  .harness/<repo>/features/FEAT-NN-slug/feature.json.",
    "  This tool writes feature.json only.",
]

# The refusal code THIS module raises for a validation failure (invalid JSON or schema
# violation) or a UTF-8 encoding failure -- distinct from harness_merge's own 6 (lock
# timeout) and 9 (destination refusal), so a caller can tell "somebody else holds the lock"
# and "wrong path" apart from "the write would have produced a document nothing can read".
SCHEMA_REFUSAL_CODE = 11


def parse_doc(base, display):
    """Parse `base` -- bytes as read by harness_merge.locked_update, or None when the file
    does not exist -- into a dict, or return None unchanged when `base` is None.

    "the file does not exist" and "the file holds an empty/absent-github mapping" are
    different states a caller may need to tell apart (gh-sync.py's save_recorded refuses the
    former and tolerates the latter), so this never collapses None into {}.

    Raises MergeRefusal(SCHEMA_REFUSAL_CODE) when `base` is present but is not valid JSON, or
    parses to something other than a JSON mapping.
    """
    if base is None:
        return None
    try:
        doc = feature_schema.json.loads(base.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as e:
        raise harness_merge.MergeRefusal(
            SCHEMA_REFUSAL_CODE, [f"{display}: not valid JSON: {e}"]
        )
    if not isinstance(doc, dict):
        raise harness_merge.MergeRefusal(
            SCHEMA_REFUSAL_CODE,
            [f"{display}: parsed but is not a JSON mapping (got {type(doc).__name__})"],
        )
    return doc


def write_feature_json(path, transform, timeout=None, tail_regex=None):
    """The one public read-modify-write entry point for feature.json.

    `transform(base)` receives the file's current bytes, or None when it does not exist --
    identical to harness_merge.locked_update's own contract -- and returns the candidate
    document TEXT (str or bytes) to write. That text is validated with
    feature_schema.problems_for_text before the atomic replace.

    THE POLICY IS MONOTONIC NON-REGRESSION, not "any problem refuses" -- and the difference
    is deliberate, found empirically rather than assumed: feature-schema.json's eight
    required keys (DEC-191) postdate a great many feature.json documents already on disk
    (and, concretely, every fixture test-gh-sync.py's own `write_feature_json` helper has
    built since T-01/FEAT-23, which sets only `feature_id` and `status`). A caller writing
    `status` or `pr` onto one of those pre-existing, already-schema-incomplete documents is
    not the hazard this feature exists to close -- it is today's normal operation, proven by
    a full existing green suite before this feature touched anything. Refusing it here would
    not be a stricter gate; it would be a silent, undiscussed behaviour change smuggled in
    under a different feature's ticket.

    So the comparison is against the BASE's own problem set, not against zero: a candidate
    is refused only for a problem NOT ALREADY PRESENT on the base (harness_merge.MergeRefusal,
    SCHEMA_REFUSAL_CODE), and `path` is left byte-for-byte unchanged. A base that does not
    exist, or does not parse, contributes an EMPTY baseline -- so a document written from
    nothing, or replacing unparseable bytes, must still be fully schema-clean; leniency
    exists only for problems the file already carried. This is the same shape as
    feature_schema.py's own RUNS_AGENT_EXEMPT/D-23 positional carve-out: a rule enforced
    prospectively, against a frozen baseline, rather than retroactively against everything
    already on disk.

    This still closes the incident's own shape for every document this function touches: a
    write that would corrupt a SCHEMA-CLEAN document (or produce invalid JSON at all, from
    any base) is refused, because "not valid JSON" and every schema problem on a clean base
    are, by definition, not already present in an empty baseline.

    `path` must resolve, via harness_merge.require_destination, to a path matching
    `tail_regex` (default FEATURE_JSON_TAIL, gh-sync.py's canonical `.harness/*/features/*/
    feature.json` shape); anything else is refused (code 9) before the lock is even touched.
    PATH SHAPE IS CALLER POLICY (stale-anchor-write-hazard T-c4), same as the never-create
    decision below: gh-sync.py's callers never pass this, so their canonical-layout
    requirement is exactly as strict as before this parameter existed. A caller whose
    directory is not, and never was, constrained to that layout -- factory_decompose.py's
    write_factory, pointed at a plain CLI positional argument -- passes its own, laxer
    tail_regex instead of gaining or losing strictness for every other caller.

    NEVER-CREATE IS ALSO CALLER POLICY, and unchanged by this parameter: this function has
    never refused an absent base itself -- `transform(None)` decides what an absent file
    means, and gh-sync.py's three call sites each raise before ever producing text for that
    case (see gh-sync.py's save_recorded, _record_status, _record_pr). Nothing here special-
    cases `base is None`; it is just another value `transform` may receive.

    LOCK LIFETIME: the fcntl lock on `path`'s sibling `.lock` file (harness_merge.acquire) is
    held for exactly the duration of this one read-modify-write and is released the instant
    the underlying file descriptor is closed -- on the normal path, on a MergeRefusal from
    either `transform` or the schema check, or on any other exception. Nothing here caches a
    lock, a descriptor, or a validation result across calls: every call is an independent
    acquire-then-release.

    This function is the ONLY read-modify-write entry point this module exposes (DEC-199):
    it opens no lock and performs no rename of its own, only harness_merge.locked_update's.
    """
    resolved = harness_merge.require_destination(
        path, tail_regex if tail_regex is not None else FEATURE_JSON_TAIL, _WHAT, _HINT_LINES
    )

    def _baseline_problems(base):
        if base is None:
            return set()
        try:
            base_text = base.decode("utf-8")
        except UnicodeDecodeError:
            # Bytes on disk that are not even UTF-8 establish no leniency: treat as if
            # nothing were there, so the candidate must be fully schema-clean.
            return set()
        return set(feature_schema.problems_for_text(base_text, resolved, for_path=resolved))

    def _transform(base):
        text = transform(base)
        text_bytes = text.encode("utf-8") if isinstance(text, str) else text
        try:
            decoded = text_bytes.decode("utf-8")
        except UnicodeDecodeError as e:
            raise harness_merge.MergeRefusal(
                SCHEMA_REFUSAL_CODE, [f"{resolved}: not valid UTF-8: {e}"]
            )
        candidate_problems = feature_schema.problems_for_text(decoded, resolved, for_path=resolved)
        if candidate_problems:
            baseline = _baseline_problems(base)
            new_problems = [p for p in candidate_problems if p not in baseline]
            if new_problems:
                raise harness_merge.MergeRefusal(SCHEMA_REFUSAL_CODE, new_problems)
        return text_bytes

    harness_merge.locked_update(resolved, _transform, timeout=timeout)
