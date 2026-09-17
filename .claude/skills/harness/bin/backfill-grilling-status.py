#!/usr/bin/env python3
"""One-shot backfill of grilling-note front-matter from a reviewed manifest (FEAT-53 T-25).

    backfill-grilling-status.py propose --root <checkout> --out <manifest.yaml>
    backfill-grilling-status.py apply   --root <checkout> --manifest <manifest.yaml>
    backfill-grilling-status.py --check --root <checkout> [--manifest <manifest.yaml>]

`propose` scans .harness/notes/grilling-*.md that carry no front-matter and writes a manifest:
one entry per note with the proposed status, the became value, the citation evidence and
`reviewed: false`. A note cited by exactly one feature's BRIEF.md or plan.yaml proposes
`handed-off` to that feature; no citation proposes `abandoned`; several features citing it is
`conflict`, which stays unresolved until a human edits the entry. `apply` refuses a manifest
with any entry not `reviewed: true` or still `conflict`, then writes each note's front-matter
through grilling_status.mark. `--check` exits 0 when every note parses under the lifecycle
rule and the manifest (if given) has no unresolved entry; it writes nothing and is idempotent.
"""
import argparse
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grilling_status  # noqa: E402
import harness_yaml  # noqa: E402


def notes(root):
    return sorted(glob.glob(os.path.join(root, ".harness", "notes", "grilling-*.md")))


def citations(root, note_path):
    """Feature directory names whose BRIEF.md or plan.yaml cite this note's path or filename."""
    rel = os.path.relpath(note_path, root)
    name = os.path.basename(note_path)
    hits = set()
    for feat_dir in glob.glob(os.path.join(root, ".harness", "*", "features", "*")):
        for artifact in ("BRIEF.md", "plan.yaml"):
            try:
                text = open(os.path.join(feat_dir, artifact), encoding="utf-8").read()
            except OSError:
                continue
            if rel in text or name in text:
                hits.add(os.path.basename(feat_dir))
    return sorted(hits)


def propose(root, observed):
    entries = []
    for path in notes(root):
        text = open(path, encoding="utf-8").read()
        try:
            grilling_status.parse(text)
            continue  # already carries front-matter
        except grilling_status.GrillingStatusError:
            pass
        cited = citations(root, path)
        if len(cited) == 1:
            status, became = "handed-off", cited[0]
        elif not cited:
            status, became = "abandoned", None
        else:
            status, became = "conflict", None
        entries.append({"path": os.path.relpath(path, root), "status": status, "became": became,
                        "evidence": cited, "reviewed": False})
    return {"schema": "grilling-status-backfill/1", "observed": observed, "notes": entries}


def apply(root, manifest):
    unresolved = [e["path"] for e in manifest["notes"]
                  if e.get("status") == "conflict" or e.get("reviewed") is not True]
    if unresolved:
        sys.exit("REFUSED: unresolved manifest entries (conflict or reviewed != true): " + ", ".join(unresolved))
    changed = 0
    for entry in manifest["notes"]:
        path = os.path.join(root, entry["path"])
        text = open(path, encoding="utf-8").read()
        new = grilling_status.mark(text, entry["status"], entry.get("became"))
        if new != text:
            open(path, "w", encoding="utf-8").write(new)
            changed += 1
    print(f"applied: {changed} note(s) written, {len(manifest['notes']) - changed} already current")


def check(root, manifest):
    faults = []
    for path in notes(root):
        try:
            status, became = grilling_status.parse(open(path, encoding="utf-8").read())
        except grilling_status.GrillingStatusError as exc:
            faults.append(f"{os.path.relpath(path, root)}: {exc}")
            continue
        if status == "handed-off" and not grilling_status.check_exists(became, root):
            faults.append(f"{os.path.relpath(path, root)}: handed-off to {became}, which is not a feature directory")
    if manifest is not None:
        faults += [f"manifest: {e['path']} unresolved" for e in manifest["notes"]
                   if e.get("status") == "conflict" or e.get("reviewed") is not True]
    for fault in faults:
        print("FAIL " + fault)
    print(f"checked {len(notes(root))} note(s); {len(faults)} fault(s)")
    return 1 if faults else 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?", choices=("propose", "apply"))
    parser.add_argument("--root", required=True)
    parser.add_argument("--out")
    parser.add_argument("--manifest")
    parser.add_argument("--observed", default=None, help="observation date recorded in a proposed manifest")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = os.path.abspath(args.root)
    manifest = harness_yaml.load_file(args.manifest) if args.manifest else None
    if args.check:
        sys.exit(check(root, manifest))
    if args.command == "propose":
        if not args.out:
            parser.error("propose requires --out")
        import datetime
        observed = args.observed or datetime.date.today().isoformat()
        doc = propose(root, observed)
        with open(args.out, "w", encoding="utf-8") as fh:
            import yaml
            yaml.safe_dump(doc, fh, sort_keys=False, allow_unicode=True)
        print(f"proposed {len(doc['notes'])} note(s) -> {args.out}")
    elif args.command == "apply":
        if manifest is None:
            parser.error("apply requires --manifest")
        apply(root, manifest)
    else:
        parser.error("choose propose, apply, or --check")


if __name__ == "__main__":
    main()
