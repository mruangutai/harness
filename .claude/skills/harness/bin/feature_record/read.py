"""feature_record/read.py — reading feature.json: the canonical loader (load_feature_json and
its recorded-issue checks), the byte-level parse the locked writer and the CLI share
(parse_doc, opt_int), and the CLI's read-only document helpers.
"""
import os
import sys

import harness_merge
from artifact_accessors import strict_json_loads


class FeatureJsonError(Exception):
    """A feature.json read failed with an actionable next step."""

    def __init__(self, what, value, next_step):
        import factory_cli
        self.next_step = next_step
        super().__init__(factory_cli.body(what, value, next_step))


def _feature_json_source(path, text, context):
    label = context or ("feature.json" if path is None else str(path))
    if (path is None) == (text is None):
        raise FeatureJsonError(
            "feature.json invalid", label, "supply exactly one source")
    source_context = context or (
        "in-memory feature.json" if text is not None else str(path))
    if text is not None:
        return text, source_context
    if not os.path.exists(path):
        return None, source_context
    return _read_feature_json_text(path, source_context), source_context


def load_feature_json(path=None, *, text=None, context=None):
    """Load a feature mapping from exactly one path or in-memory JSON text source."""
    source_text, source_context = _feature_json_source(path, text, context)
    if source_text is None:
        return None
    doc = _parse_feature_json_text(source_text, source_context)
    _validate_recorded_blocks(doc, source_context)
    return doc


def _read_feature_json_text(path, context):
    try:
        with open(path, "rb") as source:
            return source.read().decode("utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise FeatureJsonError(
            "feature.json unreadable", context, f"could not be read: {error}"
        ) from error


def _parse_feature_json_text(text, context):
    try:
        doc = strict_json_loads(text)
    except (TypeError, ValueError, RecursionError) as error:
        raise FeatureJsonError(
            "feature.json invalid", context, f"does not parse: {error}"
        ) from error
    if not isinstance(doc, dict):
        raise FeatureJsonError(
            "feature.json invalid", context,
            f"parsed but is not a JSON mapping (got {type(doc).__name__})",
        )
    return doc


def _positive_issue_number(value):
    try:
        number = opt_int(value)
    except ValueError:  # an `isdigit` string int() cannot parse, e.g. "²" (FEAT-2206)
        return None
    return number if number is not None and number >= 1 else None


def _validate_recorded_parent(block, path, block_name):
    if "parent" not in block or block["parent"] is None:
        return
    if _positive_issue_number(block["parent"]) is not None:
        return
    raise FeatureJsonError(
        "feature.json invalid", path,
        f"has a {block_name}.parent that is not a recorded issue number",
    )


def _validate_recorded_issues(block, path, block_name):
    if "issues" not in block:
        return
    issues = block["issues"]
    if not isinstance(issues, dict):
        raise FeatureJsonError(
            "feature.json invalid", path,
            f"has a {block_name}.issues key that is not a JSON object",
        )
    for key, value in issues.items():
        if _positive_issue_number(value) is None:
            raise FeatureJsonError(
                "feature.json invalid", path,
                f"has a {block_name}.issues[{key!r}] value that is not a recorded issue number",
            )


def _validate_recorded_block(doc, path, block_name):
    """Refuse malformed recorded issue fields in a present GitHub-style block."""
    block = doc.get(block_name)
    if not isinstance(block, dict):
        return
    _validate_recorded_parent(block, path, block_name)
    _validate_recorded_issues(block, path, block_name)


def _validate_recorded_blocks(doc, path):
    """Validate recorded GitHub and factory issue fields at the shared read boundary."""
    for block_name in ("github", "factory"):
        _validate_recorded_block(doc, path, block_name)


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

    Decodes through artifact_accessors.strict_json_loads (FEAT-61 T-01): the duplicate-key
    and non-finite rejection that used to be two private hooks copied here is the accessor's
    one primitive, so feature.json is read to the same strictness whether it is loaded for a
    write here or for a read anywhere else. Only the translation into this module's refusal
    code and line shape lives here.
    """
    if base is None:
        return None
    try:
        doc = strict_json_loads(base.decode("utf-8"))
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


def opt_int(value):
    """A recorded issue/milestone number as int, or None for `none`/absent/junk -- moved
    here from gh-sync.py's private `_opt_int` (BUG-285 property 7) so the one coercion
    gh-sync.py's `load_recorded` needs at three call sites (milestone, parent, each `issues`
    member) lives beside the reader it belongs to, instead of duplicated wherever it is
    needed.

    Tolerates the quoted form the old `(\\d+)` regex silently read as ABSENT -- and "absent"
    here meant gh-sync believed nothing was recorded and would create a duplicate parent or
    milestone. `bool` is excluded explicitly: it is an `int` subclass in Python, so
    `parent: true` would otherwise become `1`."""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    s = str(value).strip()
    return int(s) if s.isdigit() else None


def _read_doc(path):
    """The parsed feature.json, or a refusal — shared by the read-only verbs."""
    try:
        with open(path, "rb") as handle:
            return parse_doc(handle.read(), path)
    except FileNotFoundError:
        print(f"REFUSED: {path} does not exist.", file=sys.stderr)
        sys.exit(SCHEMA_REFUSAL_CODE)
    except harness_merge.MergeRefusal as refusal:
        for line in refusal.lines:
            print(line, file=sys.stderr)
        sys.exit(refusal.code)


def _runs(doc):
    runs = doc.get("runs")
    return list(runs) if isinstance(runs, list) else []
