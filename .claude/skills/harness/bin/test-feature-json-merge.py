#!/usr/bin/env python3
"""test-feature-json-merge.py — house-shape suite for feature_json_write.py and
feature-json-merge.py (stale-anchor-write-hazard).

Mirrors test-harness-merge.py's and test-observations-merge.py's own conventions: direct
import of the library for the properties that only the library can prove (a raw transform
producing invalid or schema-invalid text; lock contention), subprocess invocation of the CLI
for the structured ops an actual caller uses.
"""
import json
import re
import os
import signal
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import feature_json_write  # noqa: E402
import harness_merge  # noqa: E402

CLI = os.environ.get("FEATURE_JSON_MERGE_BIN") or os.path.join(HERE, "feature-json-merge.py")

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, ok, detail))
    print(("PASS" if ok else "FAIL") + f" - {name}" + (f" ({detail})" if detail and not ok else ""))


# ---------------------------------------------------------------------------
# Fixture builder
# ---------------------------------------------------------------------------

def valid_doc(feature_id="FEAT-77-test", **overrides):
    doc = {
        "feature_id": feature_id,
        "branch": "none",
        "pr": None,
        "status": "Backlog",
        "review_sha": "none",
        "cycles_used": 0,
        "max_total_cycles": 5,
        "runs": [],
    }
    doc.update(overrides)
    return doc


def fixture_path(feature_id="FEAT-77-test"):
    """A tempdir shaped like .harness/features/<feature_id>/feature.json, matching
    feature_json_write.FEATURE_JSON_TAIL."""
    d = tempfile.mkdtemp(prefix="feature-json-merge-test-")
    feat_dir = os.path.join(d, ".harness", "features", feature_id)
    os.makedirs(feat_dir)
    path = os.path.join(feat_dir, "feature.json")
    return d, path


def write_bytes(path, doc_or_text):
    text = doc_or_text if isinstance(doc_or_text, str) else json.dumps(doc_or_text, indent=2) + "\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return text.encode("utf-8")


def run_cli(args):
    return subprocess.run(
        [sys.executable, CLI] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )


# ---------------------------------------------------------------------------
# Cases
# ---------------------------------------------------------------------------

def case_1_refusal_leaves_byte_identical():
    d, path = fixture_path()
    original = write_bytes(path, valid_doc())

    def transform(base):
        raise harness_merge.MergeRefusal(7, ["refused: unrelated failure"])

    raised = False
    try:
        feature_json_write.write_feature_json(path, transform)
    except harness_merge.MergeRefusal:
        raised = True
    check("case1: MergeRefusal propagated", raised)

    with open(path, "rb") as f:
        after = f.read()
    check("case1: file byte-identical to before", after == original, repr(after))


def case_2_concurrent_writer_blocks_not_clobbers():
    """Two subprocess writers append DISTINCT run entries to the same feature.json
    concurrently. If the lock only blocked without serialising correctly, one writer's
    entry could be lost (clobbered) by the other reading a stale base. Both entries must
    survive, proving the second writer waited for the lock rather than racing past it."""
    d, path = fixture_path()
    write_bytes(path, valid_doc())

    def append_entry(tag):
        def transform(base):
            doc = json.loads(base.decode("utf-8"))
            time.sleep(0.05)  # widen the overlap window
            doc["runs"] = list(doc.get("runs", [])) + [
                {"id": tag, "squad": "test", "verdict": "PASS", "agent": "test-agent"}
            ]
            return json.dumps(doc, indent=2) + "\n"
        feature_json_write.write_feature_json(path, transform)

    pid1 = os.fork()
    if pid1 == 0:
        append_entry("run-A")
        os._exit(0)
    pid2 = os.fork()
    if pid2 == 0:
        append_entry("run-B")
        os._exit(0)
    os.waitpid(pid1, 0)
    os.waitpid(pid2, 0)

    with open(path, encoding="utf-8") as f:
        final = json.load(f)
    ids = [r["id"] for r in final.get("runs", [])]
    check(
        "case2: both concurrent writers' entries survive (lock serialised, did not clobber)",
        sorted(ids) == ["run-A", "run-B"],
        f"runs={ids}",
    )


def case_3_invalid_json_refused_with_decode_error():
    d, path = fixture_path()
    write_bytes(path, valid_doc())

    def transform(base):
        return "{ this is not valid json"

    raised_lines = []
    try:
        feature_json_write.write_feature_json(path, transform)
    except harness_merge.MergeRefusal as e:
        raised_lines = e.lines
    check("case3: refused", bool(raised_lines), str(raised_lines))
    check(
        "case3: refusal names a JSON decode error",
        any("not valid JSON" in l for l in raised_lines),
        str(raised_lines),
    )
    with open(path, encoding="utf-8") as f:
        after = json.load(f)
    check("case3: file left as the original valid document", after == valid_doc(), after)


def case_4_schema_invalid_refused():
    d, path = fixture_path()
    original = write_bytes(path, valid_doc())

    def transform(base):
        # Valid JSON, but missing every required key except feature_id.
        return json.dumps({"feature_id": "FEAT-77-test"})

    raised_lines = []
    try:
        feature_json_write.write_feature_json(path, transform)
    except harness_merge.MergeRefusal as e:
        raised_lines = e.lines
    check("case4: refused", bool(raised_lines), str(raised_lines))
    check(
        "case4: refusal names a missing required key",
        any("missing required key" in l for l in raised_lines),
        str(raised_lines),
    )
    with open(path, "rb") as f:
        after = f.read()
    check("case4: file byte-identical to before", after == original, repr(after))


def case_5_path_outside_features_refused():
    d = tempfile.mkdtemp(prefix="feature-json-merge-test-")
    bad_path = os.path.join(d, "feature.json")  # not under .harness/*/features/*/

    def transform(base):
        return json.dumps(valid_doc())

    code = None
    try:
        feature_json_write.write_feature_json(bad_path, transform)
    except harness_merge.MergeRefusal as e:
        code = e.code
    check("case5: refused with the destination code", code == 9, f"code={code}")
    check("case5: no file created at the refused path", not os.path.exists(bad_path))


def case_6_cli_set_key_lands_and_rereads():
    d, path = fixture_path()
    write_bytes(path, valid_doc())

    r = run_cli(["set-key", path, "status", '"Building"'])
    check("case6: CLI exits 0", r.returncode == 0, r.stdout + r.stderr)

    with open(path, encoding="utf-8") as f:
        after = json.load(f)
    check("case6: status landed", after.get("status") == "Building", after)
    check(
        "case6: every other key survived unchanged",
        {k: v for k, v in after.items() if k != "status"}
        == {k: v for k, v in valid_doc().items() if k != "status"},
        after,
    )


def case_7_cli_append_run():
    d, path = fixture_path()
    write_bytes(path, valid_doc())

    entry = json.dumps({"id": "run-1", "squad": "backend", "verdict": "PASS", "agent": "test-agent"})
    r = run_cli(["append-run", path, entry])
    check("case7: CLI exits 0", r.returncode == 0, r.stdout + r.stderr)

    with open(path, encoding="utf-8") as f:
        after = json.load(f)
    check(
        "case7: run entry appended",
        after.get("runs") == [{"id": "run-1", "squad": "backend", "verdict": "PASS",
                                "agent": "test-agent"}],
        after,
    )


def case_8_cli_set_github():
    d, path = fixture_path()
    write_bytes(path, valid_doc())

    value = json.dumps({"milestone": 3, "parent": None, "attached": [], "issues": {},
                         "source_issues": []})
    r = run_cli(["set-github", path, value])
    check("case8: CLI exits 0", r.returncode == 0, r.stdout + r.stderr)

    with open(path, encoding="utf-8") as f:
        after = json.load(f)
    check(
        "case8: github block landed",
        after.get("github") == {"milestone": 3, "parent": None, "attached": [], "issues": {},
                                 "source_issues": []},
        after,
    )


def case_9_cli_refuses_schema_invalid_value():
    """set-key writing a key of the wrong type must be refused by the CLI, not silently
    written -- a smoke check that the CLI is actually wired to the same schema-validating
    write path, not a bypass."""
    d, path = fixture_path()
    original = write_bytes(path, valid_doc())

    r = run_cli(["set-key", path, "cycles_used", '"not-an-integer"'])
    check("case9: CLI exits non-zero", r.returncode != 0, f"rc={r.returncode}")
    check(
        "case9: stderr names the schema problem",
        len(r.stderr.strip()) > 0,
        repr(r.stderr),
    )
    with open(path, "rb") as f:
        after = f.read()
    check("case9: file byte-identical to before", after == original, repr(after))


def case_10_cli_refuses_missing_file():
    d = tempfile.mkdtemp(prefix="feature-json-merge-test-")
    feat_dir = os.path.join(d, ".harness", "features", "FEAT-88-missing")
    os.makedirs(feat_dir)
    path = os.path.join(feat_dir, "feature.json")

    r = run_cli(["set-key", path, "status", '"Building"'])
    check("case10: CLI exits non-zero for a missing file", r.returncode != 0, f"rc={r.returncode}")
    check("case10: no file created", not os.path.exists(path))

def case_11_ratchet_holds_on_dirty_base():
    """A base document already missing one required key (legacy-shaped, predates DEC-191)
    must not gain amnesty for a SECOND, different problem the transform introduces. The
    refusal must name the NEW problem and must NOT re-litigate the pre-existing one --
    that is the entire content of "monotonic non-regression" as distinct from a policy
    that either always refuses (breaks every legacy document) or grants blanket amnesty
    once a base is dirty at all (a hole big enough to launder any further corruption)."""
    d, path = fixture_path()
    dirty = valid_doc()
    del dirty["status"]  # legacy-shaped: missing one required key already
    original = write_bytes(path, dirty)

    def transform(base):
        doc = json.loads(base.decode("utf-8"))
        del doc["review_sha"]  # a SECOND, different missing key
        return json.dumps(doc)

    raised_lines = []
    try:
        feature_json_write.write_feature_json(path, transform)
    except harness_merge.MergeRefusal as e:
        raised_lines = e.lines
    check("case11: refused", bool(raised_lines), str(raised_lines))
    check(
        "case11: refusal names the NEW problem (review_sha)",
        any("review_sha" in l for l in raised_lines),
        str(raised_lines),
    )
    check(
        "case11: refusal does NOT name the pre-existing problem (status)",
        not any("'status'" in l for l in raised_lines),
        str(raised_lines),
    )
    with open(path, "rb") as f:
        after = f.read()
    check("case11: file byte-identical to before", after == original, repr(after))


def case_12_ratchet_does_not_over_refuse():
    """Same dirty base (missing `status`). The transform touches only an unrelated,
    already-legal top-level key. This must land -- refusing it would mean the policy is
    "any problem refuses" wearing a different name, exactly the regression the
    monotonic-non-regression policy was built to avoid."""
    d, path = fixture_path()
    dirty = valid_doc()
    del dirty["status"]
    write_bytes(path, dirty)

    def transform(base):
        doc = json.loads(base.decode("utf-8"))
        doc["cycles_used"] = 3
        return json.dumps(doc)

    accepted = False
    detail = ""
    try:
        feature_json_write.write_feature_json(path, transform)
        accepted = True
    except harness_merge.MergeRefusal as e:
        detail = str(e.lines)
    check("case12: accepted, not refused", accepted, detail)

    with open(path, encoding="utf-8") as f:
        after = json.load(f)
    check("case12: unrelated key landed", after.get("cycles_used") == 3, after)
    check(
        "case12: pre-existing problem (missing status) still present, unreported as a refusal",
        "status" not in after,
        after,
    )


def case_13_unparseable_base_is_strict():
    """A base that is not valid JSON at all contributes an EMPTY baseline (see
    write_feature_json's docstring): a fully schema-clean candidate must still be able to
    replace it, and a candidate that is ALSO unparseable -- but differently broken, i.e. a
    real transform attempt, not a byte-for-byte no-op -- is refused rather than waved
    through as "the base already had that problem". The comparison is by exact problem
    string, never by category ("base already had a JSON-decode problem"), so two
    different malformed texts produce two different messages and the candidate's reads as
    NEW. Pinned direction: leniency requires an EXACT prior match; anything else refuses.
    This is the safe direction because the alternative (any decode error on a broken base
    waves through any other decode error) is exactly the amnesty-by-category hole the
    monotonic policy exists to avoid."""
    d, path = fixture_path()
    write_bytes(path, "{ not json at all, missing brace")

    def clean_transform(base):
        return json.dumps(valid_doc())

    feature_json_write.write_feature_json(path, clean_transform)
    with open(path, encoding="utf-8") as f:
        after_clean = json.load(f)
    check(
        "case13: schema-clean candidate lands over an unparseable base",
        after_clean == valid_doc(),
        after_clean,
    )

    d2, path2 = fixture_path(feature_id="FEAT-77-test-b")
    original2 = write_bytes(path2, "{ not json at all, missing brace")

    def broken_transform(base):
        return '{"feature_id": "x", "status": Building}'

    raised_lines = []
    try:
        feature_json_write.write_feature_json(path2, broken_transform)
    except harness_merge.MergeRefusal as e:
        raised_lines = e.lines
    check(
        "case13: differently-broken candidate over an unparseable base is refused",
        bool(raised_lines),
        str(raised_lines),
    )
    check(
        "case13: refusal names a JSON decode error",
        any("not valid JSON" in l for l in raised_lines),
        str(raised_lines),
    )
    with open(path2, "rb") as f:
        after2 = f.read()
    check(
        "case13: file left as the original unparseable base, not overwritten",
        after2 == original2,
        repr(after2),
    )

def case_14_tail_regex_is_caller_overridable():
    """write_feature_json's default path-shape policy (FEATURE_JSON_TAIL) is unchanged, but a
    caller may supply its own `tail_regex` -- factory_decompose.py's write_factory needs this
    (stale-anchor-write-hazard T-c4): it is a general CLI tool pointed at an arbitrary
    directory, never constrained to the canonical .harness/*/features/*/ layout gh-sync.py's
    callers live under. Path shape is caller policy, not a fact this shared core owns."""
    d = tempfile.mkdtemp(prefix="feature-json-merge-test-")
    bare_path = os.path.join(d, "not-nested-under-harness", "feature.json")
    os.makedirs(os.path.dirname(bare_path))

    def transform(base):
        return json.dumps(valid_doc())

    default_code = None
    try:
        feature_json_write.write_feature_json(bare_path, transform)
    except harness_merge.MergeRefusal as e:
        default_code = e.code
    check("case14: default tail_regex still refuses a non-canonical path, code 9",
          default_code == 9, f"code={default_code}")
    check("case14: default-refused path created nothing", not os.path.exists(bare_path))

    lax_tail = re.compile(r"(?:^|/)feature\.json$")
    feature_json_write.write_feature_json(bare_path, transform, tail_regex=lax_tail)
    with open(bare_path, encoding="utf-8") as f:
        after = json.load(f)
    check("case14: a custom tail_regex accepts the same non-canonical path",
          after == valid_doc(), after)




def main():
    case_1_refusal_leaves_byte_identical()
    case_2_concurrent_writer_blocks_not_clobbers()
    case_3_invalid_json_refused_with_decode_error()
    case_4_schema_invalid_refused()
    case_5_path_outside_features_refused()
    case_6_cli_set_key_lands_and_rereads()
    case_7_cli_append_run()
    case_8_cli_set_github()
    case_9_cli_refuses_schema_invalid_value()
    case_10_cli_refuses_missing_file()
    case_11_ratchet_holds_on_dirty_base()
    case_12_ratchet_does_not_over_refuse()
    case_13_unparseable_base_is_strict()
    case_14_tail_regex_is_caller_overridable()

    failed = [r for r in RESULTS if not r[1]]
    if failed:
        print(f"FAIL - {len(failed)}/{len(RESULTS)} checks failed")
        sys.exit(1)
    print(f"PASS - {len(RESULTS)}/{len(RESULTS)} checks passed")


if __name__ == "__main__":
    main()
