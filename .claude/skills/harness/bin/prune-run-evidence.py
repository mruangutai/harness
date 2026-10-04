#!/usr/bin/env python3
"""prune-run-evidence.py — evidence retention at ship (#1997).

The UI lane commits `runs/<id>/ui/` (results.json + WebPs) per run so a reader's judgement is
bound to a pin (FEAT-1821). Nothing pruned them: two features reached 98 run ids. At ship the
evidence that still means something is

  * every validator-squad validate or fix run (`validate-…`, `fix-cN-…`) recorded PASS — a
    reader's judgement lives in that run's directory, so this keeps the last PASS of every reader, and
  * every run whose results.json names the shipped `review_sha` as served_bundle_commit,

plus anything named with --keep. Every other `runs/<id>/` directory under the feature is deleted
in the ship commit; the digests and notes that cite them stay (a pointer to pruned evidence is a
pointer to history, which the ship PR carries).

  prune-run-evidence.py --feature FEAT-NN-slug [--root DIR] [--keep RUN-ID ...] [--dry-run]

Exit 2 is refusal: no such feature, or no review_sha (nothing is shipped, so nothing is pruned).
"""
import argparse
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harness_boundary  # noqa: E402
import harness_yaml  # noqa: E402
import artifact_accessors  # noqa: E402


def _refuse(message):
    sys.stderr.write(f"prune-run-evidence: {message}\n")
    return 2


def _feature_dir(root, feature):
    for segment in sorted(os.listdir(os.path.join(root, ".harness"))):
        candidate = os.path.join(root, ".harness", segment, "features", feature)
        if os.path.isfile(os.path.join(candidate, "feature.json")):
            return candidate
    return None


def _served_commit(run_dir):
    path = os.path.join(run_dir, "ui", "results.json")
    if not os.path.isfile(path):
        return None
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle).get("served_bundle_commit")
    except (OSError, ValueError):
        return None


# feature-record.py's run-token shapes: `validate-…` and `fix-cN-…` are the runs whose runs/<id>/
# the readers write their evidence into. The validator-lead hosts the fix team too, so after a
# FAILed validate every reader's last PASS lives in a fix run (five recent ships had no validate-*
# PASS at all). Reconciliation and distill runs share the squad and are not evidence.
_EVIDENCE_RUN = re.compile(r"(?:^|-)(?:validate|fix)-")


def _is_validate_run(run):
    return run.get("squad") == "validator" and bool(_EVIDENCE_RUN.search(str(run.get("id", ""))))


def _passing_validate_runs(record):
    return {run.get("id") for run in record.get("runs") or [] if _is_validate_run(run) and str(run.get("verdict", "")).upper() == "PASS"}


def keep_set(feature_dir, record, explicit):
    """What stays: every validate run recorded PASS (a reader's judgement lives in its validate
    run's directory, so this is 'the last PASS of each reader' and every earlier PASS too),
    every run whose bundle names the shipped pin, and anything named with --keep. feature.json
    runs carry no sha of their own, and served_bundle_commit need not equal a later
    evidence-commit review_sha (FEAT-1821 GC-02), so neither key alone is trusted."""
    pin = record.get("review_sha")
    runs_dir = os.path.join(feature_dir, "runs")
    present = sorted(name for name in os.listdir(runs_dir)
                     if os.path.isdir(os.path.join(runs_dir, name))) if os.path.isdir(runs_dir) else []
    pin_runs = {name for name in present if _served_commit(os.path.join(runs_dir, name)) == pin}
    return present, pin_runs | _passing_validate_runs(record) | set(explicit)


def _build_parser():
    parser = argparse.ArgumentParser(prog="prune-run-evidence.py")
    parser.add_argument("--feature", required=True)
    parser.add_argument("--root")
    parser.add_argument("--keep", action="append", default=[])
    parser.add_argument("--dry-run", action="store_true")
    return parser


def _has_review_pin(record):
    pin = record.get("review_sha")
    return isinstance(pin, str) and bool(pin.strip()) and pin.strip().lower() not in harness_yaml.PLACEHOLDER_UNSET


def _load_record(args):
    """(feature_dir, record) or a refusal string."""
    root = args.root or harness_boundary.root_above(os.getcwd())
    if root is None or not os.path.isfile(os.path.join(root, ".harness", "team-config.yaml")):
        return "not inside a harness checkout (no .harness/team-config.yaml above cwd)"
    feature_dir = _feature_dir(root, args.feature)
    if feature_dir is None:
        return f"no feature {args.feature!r} under {root}"
    try:
        record = artifact_accessors.load_feature_json(os.path.join(feature_dir, "feature.json"))
    except artifact_accessors.FeatureJsonError as error:
        return f"{args.feature} has an invalid feature record: {error}"
    if not _has_review_pin(record):
        return f"{args.feature} has no review_sha — nothing is shipped, so nothing is pruned"
    return feature_dir, record


def _prune(feature_dir, present, keep, dry_run):
    verb = "would remove" if dry_run else "removed"
    for name in present:
        if name in keep:
            continue
        print(f"{verb} runs/{name}")
        if not dry_run:
            shutil.rmtree(os.path.join(feature_dir, "runs", name))
    kept = sorted(keep & set(present))
    print(f"kept {len(kept)} of {len(present)} run(s): {', '.join(kept) or '-'}")


def main(argv=None):
    args = _build_parser().parse_args(argv)
    loaded = _load_record(args)
    if isinstance(loaded, str):
        return _refuse(loaded)
    feature_dir, record = loaded
    present, keep = keep_set(feature_dir, record, args.keep)
    unmatched = sorted(set(args.keep) - set(present))
    if unmatched:
        return _refuse(f"--keep names no run directory: {', '.join(unmatched)}")
    _prune(feature_dir, present, keep, args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
