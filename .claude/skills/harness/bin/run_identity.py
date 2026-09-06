#!/usr/bin/env python3
"""Write-once run identity witness primitives for Harness run directories."""
import collections.abc as _abc
import datetime as _datetime
import json as _json
import os as _os
import re as _re
import tempfile as _tempfile
import uuid as _uuid

MARKER_NAME = ".run-identity.json"

__all__ = [
    "MARKER_NAME", "MarkerUnreadable", "marker_path", "read_marker", "mint_uid",
    "inject_uid", "record_seed", "conflict", "uid_conflict",
]


class MarkerUnreadable(Exception):
    """The marker exists but cannot safely be interpreted as an object."""


def marker_path(run_dir):
    return _os.path.join(run_dir, MARKER_NAME)


def read_marker(run_dir):
    path = marker_path(run_dir)
    try:
        with open(path, encoding="utf-8") as fh:
            marker = _json.load(fh)
    except FileNotFoundError:
        return None
    except (OSError, UnicodeError, _json.JSONDecodeError) as exc:
        raise MarkerUnreadable(f"cannot read run identity marker {path}: {exc}") from exc
    if not isinstance(marker, dict):
        raise MarkerUnreadable(f"run identity marker {path} is not a JSON object")
    return marker


def mint_uid():
    return _uuid.uuid4().hex


def inject_uid(state_path, uid):
    """Append a run uid without re-emitting an author-owned YAML checkpoint."""
    temp_path = None
    try:
        with open(state_path, encoding="utf-8", newline="") as fh:
            original = fh.read()
        if _re.search(r"^run_uid:", original, _re.MULTILINE):
            return False
        # This is intentionally a text append, not a YAML round trip: the hook must
        # preserve the owning agent's comments, key order, and formatting verbatim.
        separator = "" if not original or original.endswith(("\n", "\r")) else "\n"
        updated = f"{original}{separator}run_uid: {uid}\n"
        directory = _os.path.dirname(_os.path.abspath(state_path))
        fd, temp_path = _tempfile.mkstemp(prefix=".run-uid-", dir=directory, text=True)
        with _os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
            fh.write(updated)
        _os.replace(temp_path, state_path)
        temp_path = None
        return True
    except (OSError, UnicodeError):
        return False
    finally:
        if temp_path is not None:
            try:
                _os.unlink(temp_path)
            except OSError:
                pass


def record_seed(run_dir, doc, identity, run_uid):
    """Best-effort, write-once creation of a run directory's forensic witness."""
    path = marker_path(run_dir)
    temp_path = None
    if not _os.path.isdir(run_dir) or _os.path.exists(path):
        return False
    try:
        marker = {
            key: str(doc.get(key)) if key in doc else None
            for key in ("run_id", "feature", "squad", "host")
        }
        marker.update({
            "identity": identity,
            "run_uid": run_uid,
            "created_at": _datetime.datetime.now(_datetime.timezone.utc).isoformat(),
        })
        fd, temp_path = _tempfile.mkstemp(prefix=".run-identity-", dir=run_dir, text=True)
        with _os.fdopen(fd, "w", encoding="utf-8") as fh:
            _json.dump(marker, fh, sort_keys=True)
            fh.write("\n")
        _os.replace(temp_path, path)
        temp_path = None
        return True
    except Exception:
        return False
    finally:
        if temp_path is not None:
            try:
                _os.unlink(temp_path)
            except OSError:
                pass


def conflict(marker, doc):
    """Return the first disagreement between a witness and incoming seed fields."""
    if marker is None:
        return None
    # A born-null field must not make its write-once directory permanently
    # unwritable. D-01/D-11 also make `identity` forensic evidence only: neither
    # predicate, nor any gate in this feature, may consume it as a denial input.
    for field in ("run_id", "feature", "squad", "host"):
        recorded = marker.get(field)
        incoming = doc.get(field)
        if recorded is not None and str(recorded) != str(incoming):
            return (f"run identity witness {field} is {recorded!r}, but the incoming "
                    f"checkpoint carries {incoming!r}")
    return None


def uid_conflict(prior_doc, doc):
    """Return why an incoming checkpoint is not an update of a minted run."""
    if not isinstance(prior_doc, _abc.Mapping):
        return None
    prior = prior_doc.get("run_uid")
    if prior is None or prior == "":
        return None
    incoming = doc.get("run_uid") if isinstance(doc, _abc.Mapping) else None
    if incoming is not None and incoming != "" and str(incoming) == str(prior):
        return None
    if incoming is None or incoming == "":
        return (f"the existing checkpoint belongs to run_uid {prior!r}; this write cannot "
                "be shown to update that run. A run that owns the record must carry its "
                "run_uid line forward verbatim from the checkpoint it is updating; the "
                "same value is recorded in the witness beside it")
    return (f"the incoming checkpoint belongs to run_uid {incoming!r}, a different run "
            f"than existing run_uid {prior!r}")
